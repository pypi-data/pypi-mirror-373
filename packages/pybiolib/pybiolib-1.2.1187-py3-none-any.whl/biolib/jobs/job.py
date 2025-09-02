import base64
import sys
import time
from collections import OrderedDict
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse

import biolib.api.client
from biolib import utils
from biolib._internal.http_client import HttpClient
from biolib._internal.tree_utils import build_tree_from_files, build_tree_str
from biolib._internal.utils import open_browser_window_from_notebook
from biolib.api.client import ApiClient
from biolib.biolib_api_client import BiolibApiClient, CreatedJobDict
from biolib.biolib_api_client.biolib_app_api import BiolibAppApi
from biolib.biolib_api_client.biolib_job_api import BiolibJobApi
from biolib.biolib_binary_format import LazyLoadedFile, ModuleInput, ModuleInputDict, ModuleOutputV2
from biolib.biolib_binary_format.remote_endpoints import RemoteJobStorageEndpoint
from biolib.biolib_binary_format.stdout_and_stderr import StdoutAndStderr
from biolib.biolib_errors import BioLibError, CloudJobFinishedError
from biolib.biolib_logging import logger, logger_no_user_data
from biolib.compute_node.job_worker.job_storage import JobStorage
from biolib.compute_node.utils import SystemExceptionCodeMap, SystemExceptionCodes
from biolib.jobs.job_result import JobResult, PathFilter
from biolib.jobs.types import CloudJobDict, CloudJobStartedDict, JobDict
from biolib.tables import BioLibTable
from biolib.typing_utils import Dict, List, Optional, Union, cast
from biolib.utils import IS_RUNNING_IN_NOTEBOOK
from biolib.utils.app_uri import parse_app_uri


class Result:
    # Columns to print in table when showing Result
    table_columns_to_row_map = OrderedDict(
        {
            'ID': {'key': 'uuid', 'params': {'width': 36}},
            'Name': {'key': 'main_result.name', 'params': {}},
            'Application': {'key': 'app_uri', 'params': {}},
            'Status': {'key': 'state', 'params': {}},
            'Started At': {'key': 'started_at', 'params': {}},
        }
    )

    def __init__(self, job_dict: JobDict, _api_client: Optional[ApiClient] = None):
        self._api_client: Optional[ApiClient] = _api_client

        self._uuid: str = job_dict['uuid']
        self._auth_token: str = job_dict['auth_token']

        self._job_dict: JobDict = job_dict
        self._job_dict_last_fetched_at: datetime = datetime.utcnow()
        self._result: Optional[JobResult] = None
        self._cached_input_arguments: Optional[List[str]] = None

    def __str__(self):
        return f"Result of {self._job_dict['app_uri']} created at {self._job_dict['created_at']} ({self._uuid})"

    def __repr__(self):
        # Get job status and shareable link
        status = self.get_status()
        shareable_link = self.get_shareable_link()

        # ANSI color codes for terminal output
        blue = '\033[34m'
        white = '\033[90m'
        reset = '\033[0m'

        # Start with the header section
        output_lines = [
            '--- BioLib Result ---',
            f'ID: {self._uuid}',
            f'Status: {status}',
            f'Link: {shareable_link}',
        ]

        # Only show output files if the job is not pending
        if not self.is_pending():
            output_lines.append('Output Files:')

            try:
                # Get files from the job
                files = self.list_output_files()

                # If no files, indicate that
                if not files:
                    output_lines.append('No output files')
                    return '\n'.join(output_lines)

                # If more than 25 files, show simplified message
                if len(files) > 25:
                    output_lines.append(f'{len(files)} output files in result.')
                    return '\n'.join(output_lines)

                # Build the tree representation
                tree_data = build_tree_from_files(files)
                output_lines.extend(build_tree_str(tree_data, blue=blue, white=white, reset=reset))
            except Exception:
                output_lines.append('Error accessing output files')

        return '\n'.join(output_lines)

    @property
    def id(self) -> str:  # pylint: disable=invalid-name
        return self._uuid

    @property
    def result(self) -> JobResult:
        if not self._result:
            self._result = JobResult(job_uuid=self._uuid, job_auth_token=self._auth_token)

        return self._result

    @property
    def stdout(self) -> bytes:
        logger.warning('The property .stdout is deprecated, please use .get_stdout()')
        return self.result.get_stdout()

    @property
    def stderr(self) -> bytes:
        logger.warning('The property .stderr is deprecated, please use .get_stderr()')
        return self.result.get_stderr()

    @property
    def exitcode(self) -> int:
        logger.warning('The property .exitcode is deprecated, please use .get_exit_code()')
        return self.result.get_exit_code()

    def is_finished(self) -> bool:
        if self._job_dict['ended_at']:
            return True

        self._refetch_job_dict()
        return bool(self._job_dict['ended_at'])

    def is_pending(self) -> bool:
        """Returns whether the result is in a pending state.

        A result is considered pending if it's not finished yet.
        The result state is re-fetched when this method is called.

        Returns:
            bool: True if the result is in a pending state, False otherwise.

        Example::
            >>> result = biolib.get_result("result_id")
            >>> if result.is_pending():
            >>>     print("Result is still running")
            >>> else:
            >>>     print("Result has finished")
        """
        return not self.is_finished()

    def get_name(self) -> str:
        self._refetch_job_dict()
        return self._job_dict['main_result']['name']

    def to_dict(self) -> Dict:
        # Construct user facing dict with friendly named keys
        return dict(
            app_uri=self._job_dict['app_uri'],
            created_at=self._job_dict['created_at'],
            finished_at=self._job_dict['ended_at'],
            job_id=self._job_dict['uuid'],
            started_at=self._job_dict['started_at'],
            state=self._job_dict['state'],
        )

    def list_output_files(
        self,
        path_filter: Optional[PathFilter] = None,
    ) -> List[LazyLoadedFile]:
        """List output files from the result.

        Args:
            path_filter (PathFilter, optional): Filter to apply to the output files.
                Can be a string glob pattern or a callable that takes a path string and returns a boolean.

        Returns:
            List[LazyLoadedFile]: List of output files.

        Example::
            >>> result = biolib.get_result("result_id")
            >>> output_files = result.list_output_files()
            >>> # Filter files with a glob pattern
            >>> output_files = result.list_output_files("*.pdb")
        """
        return self.result.list_output_files(path_filter=path_filter)

    def get_output_file(self, filename: str) -> LazyLoadedFile:
        return self.result.get_output_file(filename=filename)

    def load_file_as_numpy(self, *args, **kwargs):
        try:
            import numpy  # type: ignore # pylint: disable=import-outside-toplevel,import-error
        except ImportError:  # pylint: disable=raise-missing-from
            raise Exception('Failed to import numpy, please make sure it is installed.') from None
        file_handle = self.result.get_output_file(*args, **kwargs).get_file_handle()
        return numpy.load(file_handle, allow_pickle=False)  # type: ignore

    def get_stdout(self) -> bytes:
        return self.result.get_stdout()

    def get_stderr(self) -> bytes:
        return self.result.get_stderr()

    def get_exit_code(self) -> int:
        return self.result.get_exit_code()

    def _get_module_input(self) -> ModuleInputDict:
        self._refetch_job_dict()
        presigned_download_url = BiolibJobApi.get_job_storage_download_url(
            job_uuid=self._job_dict['uuid'],
            job_auth_token=self._job_dict['auth_token'],
            storage_type='input',
        )
        response = HttpClient.request(url=presigned_download_url)
        module_input_serialized: bytes = response.content
        return ModuleInput(module_input_serialized).deserialize()

    def get_input_arguments(self) -> List[str]:
        if self._cached_input_arguments is None:
            logger.debug('Fetching input arguments...')
            module_input = self._get_module_input()
            self._cached_input_arguments = module_input['arguments']

        return self._cached_input_arguments

    def save_input_files(self, output_dir: str, overwrite: bool = False) -> None:
        logger.info('Downloading input files...')
        module_input = self._get_module_input()

        files = module_input['files'].items()
        logger.info(f'Saving input {len(files)} files to "{output_dir}"...')
        for path, data in files:
            # Remove leading slash of file_path
            destination_file_path = Path(output_dir) / Path(path.lstrip('/'))
            if destination_file_path.exists():
                if not overwrite:
                    raise BioLibError(f'File {destination_file_path} already exists. Set overwrite=True to overwrite.')
                else:
                    destination_file_path.rename(
                        f'{destination_file_path}.biolib-renamed.{time.strftime("%Y%m%d%H%M%S")}'
                    )

            dir_path = destination_file_path.parent
            if dir_path:
                dir_path.mkdir(parents=True, exist_ok=True)

            with open(destination_file_path, mode='wb') as file_handler:
                file_handler.write(data)

            logger.info(f'  - {destination_file_path}')

    def save_files(
        self,
        output_dir: str,
        path_filter: Optional[PathFilter] = None,
        skip_file_if_exists: Optional[bool] = None,
        overwrite: bool = False,
    ) -> None:
        self.result.save_files(
            output_dir=output_dir,
            path_filter=path_filter,
            skip_file_if_exists=skip_file_if_exists,
            overwrite=overwrite,
        )

    def get_status(self) -> str:
        self._refetch_job_dict()
        return self._job_dict['state']

    def wait(self):
        logger.info(f'Waiting for job {self.id} to finish...')
        while not self.is_finished():
            time.sleep(2)
        logger.info(f'Result {self.id} has finished.')

    def get_shareable_link(self, embed_view: Optional[bool] = None) -> str:
        api_client = BiolibApiClient.get()
        prefix = '/embed' if embed_view else ''
        shareable_link = f'{api_client.base_url}{prefix}/results/{self.id}/?token={self._auth_token}'
        return shareable_link

    def open_browser(self) -> None:
        results_url_to_open = self.get_shareable_link()
        if IS_RUNNING_IN_NOTEBOOK:
            print(f'Opening results page at: {results_url_to_open}')
            print('If your browser does not open automatically, click on the link above.')
            open_browser_window_from_notebook(results_url_to_open)
        else:
            print('Please copy and paste the following link into your browser:')
            print(results_url_to_open)

    def cancel(self) -> None:
        try:
            biolib.api.client.patch(
                path=f'/jobs/{self._uuid}/',
                headers={'Job-Auth-Token': self._auth_token} if self._auth_token else None,
                data={'state': 'cancelled'},
            )
            logger.info(f'Result {self._uuid} canceled')
        except Exception as error:
            logger.error(f'Failed to cancel result {self._uuid} due to: {error}')

    def delete(self) -> None:
        """Delete the result.

        Example::
            >>> result = biolib.get_result("result_id")
            >>> result.delete()
        """
        try:
            biolib.api.client.delete(path=f'/jobs/{self._uuid}/')
            logger.info(f'Result {self._uuid} deleted')
        except Exception as error:
            raise BioLibError(f'Failed to delete job {self._uuid} due to: {error}') from error

    def rename(self, name: str) -> None:
        try:
            biolib.api.client.patch(
                path=f'/jobs/{self._uuid}/main_result/',
                headers={'Job-Auth-Token': self._auth_token} if self._auth_token else None,
                data={'result_name_prefix': name},
            )
            self._refetch_job_dict(force_refetch=True)
            updated_name = self.get_name()
            logger.info(f'Result {self._uuid} renamed to "{updated_name}"')
        except Exception as error:
            raise BioLibError(f'Failed to rename job {self._uuid} due to: {error}') from error

    def recompute(
        self,
        app_uri: Optional[str] = None,
        machine: Optional[str] = None,
        blocking: bool = True,
        arguments: Optional[List[str]] = None,
    ) -> 'Result':
        """Recompute the result with the same input files but potentially different arguments.

        Args:
            app_uri (Optional[str], optional): The URI of the app to use for recomputation.
                If None, uses the original app URI. Defaults to None.
            machine (Optional[str], optional): The machine to run the result on.
                If None, uses the original requested machine. Defaults to None.
            blocking (bool, optional): Whether to block until the result completes.
                If True, streams logs until completion. Defaults to True.
            arguments (Optional[List[str]], optional): New arguments to use for the result.
                If None, uses the original arguments. Defaults to None.

        Returns:
            Result: A new Result instance for the recomputed result.

        Example::
            >>> result = biolib.get_result("result_id")
            >>> # Recompute with the same arguments
            >>> new_result = result.recompute()
            >>> # Recompute with different arguments
            >>> new_result = result.recompute(arguments=["--new-arg", "value"])
        """
        app_response = BiolibAppApi.get_by_uri(uri=app_uri or self._job_dict['app_uri'])

        job_storage_input = RemoteJobStorageEndpoint(
            job_auth_token=self._auth_token,
            job_uuid=self._uuid,
            storage_type='input',
        )
        http_response = HttpClient.request(url=job_storage_input.get_remote_url())
        module_input_serialized = http_response.content

        # If arguments are provided, deserialize the module input, update the arguments, and serialize it again
        if arguments is not None:
            module_input = ModuleInput(module_input_serialized)
            module_input_dict = module_input.deserialize()

            # Create a new ModuleInput with updated arguments
            module_input_serialized = ModuleInput().serialize(
                stdin=module_input_dict['stdin'], arguments=arguments, files=module_input_dict['files']
            )

        original_requested_machine = (
            self._job_dict['requested_machine'] if self._job_dict['requested_machine'] else None
        )
        job = self._start_job_in_cloud(
            app_uri=app_response['app_uri'],
            app_version_uuid=app_response['app_version']['public_id'],
            module_input_serialized=module_input_serialized,
            machine=machine if machine else original_requested_machine,
        )
        if blocking:
            job.stream_logs()

        return job

    def _get_cloud_job(self) -> CloudJobDict:
        self._refetch_job_dict(force_refetch=True)
        if self._job_dict['cloud_job'] is None:
            raise BioLibError(f'Result {self._uuid} did not register correctly. Try creating a new result.')

        return self._job_dict['cloud_job']

    def _set_result_module_output(self, module_output: ModuleOutputV2) -> None:
        self._result = JobResult(job_uuid=self._uuid, job_auth_token=self._auth_token, module_output=module_output)

    @staticmethod
    def fetch_jobs(count: int, status: Optional[str] = None) -> List['Result']:
        job_dicts = Result._get_job_dicts(count, status)
        return [Result(job_dict) for job_dict in job_dicts]

    @staticmethod
    def show_jobs(count: int = 25) -> None:
        job_dicts = Result._get_job_dicts(count)
        BioLibTable(columns_to_row_map=Job.table_columns_to_row_map, rows=job_dicts, title='Jobs').print_table()

    @staticmethod
    def _get_job_dicts(count: int, status: Optional[str] = None) -> List['JobDict']:
        job_states = ['in_progress', 'completed', 'failed', 'cancelled']
        if status is not None and status not in job_states:
            raise Exception('Invalid status filter')

        page_size = min(count, 1_000)
        params: Dict[str, Union[str, int]] = dict(page_size=page_size)
        if status:
            params['state'] = status

        api_path = '/jobs/'
        response = biolib.api.client.get(api_path, params=params).json()
        jobs = [job_dict for job_dict in response['results']]

        for page_number in range(2, response['page_count'] + 1):
            if len(jobs) >= count:
                break
            page_response = biolib.api.client.get(path=api_path, params=dict(**params, page=page_number)).json()
            jobs.extend([job_dict for job_dict in page_response['results']])

        return jobs[:count]

    @staticmethod
    def _get_job_dict(uuid: str, auth_token: Optional[str] = None, api_client: Optional[ApiClient] = None) -> JobDict:
        api = api_client or biolib.api.client
        job_dict: JobDict = api.get(
            path=f'/jobs/{uuid}/',
            headers={'Job-Auth-Token': auth_token} if auth_token else None,
        ).json()

        return job_dict

    @staticmethod
    def create_from_uuid(uuid: str, auth_token: Optional[str] = None) -> 'Result':
        job_dict = Result._get_job_dict(uuid=uuid, auth_token=auth_token)
        return Result(job_dict)

    @staticmethod
    def print_logs_packages(stdout_and_stderr_packages_b64):
        for stdout_and_stderr_package_b64 in stdout_and_stderr_packages_b64:
            stdout_and_stderr_package = base64.b64decode(stdout_and_stderr_package_b64)
            stdout_and_stderr = StdoutAndStderr(stdout_and_stderr_package).deserialize()

            sys.stdout.write(stdout_and_stderr.decode())
            if not IS_RUNNING_IN_NOTEBOOK:  # for some reason flushing in jupyter notebooks breaks \r handling
                sys.stdout.flush()
        # flush after having processed all packages
        sys.stdout.flush()

    def show(self) -> None:
        self._refetch_job_dict()
        BioLibTable(
            columns_to_row_map=Result.table_columns_to_row_map,
            rows=[self._job_dict],
            title=f'Result: {self._uuid}',
        ).print_table()

    def stream_logs(self) -> None:
        self._stream_logs()

    def _stream_logs(self, enable_print: bool = True) -> None:
        try:
            cloud_job = self._get_cloud_job_awaiting_started()
        except CloudJobFinishedError:
            logger.info(f'--- The result {self.id} has already completed (no streaming will take place) ---')
            logger.info('--- The stdout log is printed below: ---')
            sys.stdout.flush()
            print(self.get_stdout().decode(), file=sys.stdout)
            sys.stdout.flush()
            logger.info('--- The stderr log is printed below: ---')
            print(self.get_stderr().decode(), file=sys.stderr)
            sys.stderr.flush()
            logger.info(f'--- The job {self.id} has already completed. Its output was printed above. ---')
            return

        compute_node_url = cloud_job['compute_node_url']
        logger_no_user_data.debug(f'Using compute node URL "{compute_node_url}"')

        if utils.BIOLIB_CLOUD_BASE_URL:
            compute_node_url = utils.BIOLIB_CLOUD_BASE_URL + str(urlparse(compute_node_url).path)
            logger_no_user_data.debug(f'Using cloud proxy URL from env var BIOLIB_CLOUD_BASE_URL: {compute_node_url}')

        if enable_print:
            self._print_full_logs(node_url=compute_node_url)

        final_status_messages: List[str] = []
        while True:
            time.sleep(2)
            status_json = self._get_job_status_from_compute_node(compute_node_url)
            if not status_json:
                # this can happen if the job is finished but already removed from the compute node
                logger.warning('WARN: We were unable to retrieve the full log of the job, please try again')
                break
            job_is_completed = status_json['is_completed']
            for status_update in status_json['status_updates']:
                # If the job is completed, print the log messages after all stdout and stderr has been written
                if job_is_completed:
                    final_status_messages.append(status_update['log_message'])
                else:
                    # Print the status before writing stdout and stderr
                    logger.info(f'Cloud: {status_update["log_message"]}')

            if 'stdout_and_stderr_packages_b64' and enable_print:
                self.print_logs_packages(status_json['stdout_and_stderr_packages_b64'])

            if 'error_code' in status_json:
                error_code = status_json['error_code']
                error_message = SystemExceptionCodeMap.get(error_code, f'Unknown error code {error_code}')

                raise BioLibError(f'Cloud: {error_message}')

            if job_is_completed:
                break

        # Print the final log messages after stdout and stderr has been written
        for message in final_status_messages:
            logger.info(f'Cloud: {message}')

        self.wait()  # Wait for compute node to tell the backend that the job is finished

    def _print_full_logs(self, node_url: str) -> None:
        try:
            response_json = HttpClient.request(url=f'{node_url}/v1/job/{self._uuid}/status/?logs=full').json()
        except Exception as error:
            logger.error(f'Could not get full streamed logs due to: {error}')
            raise BioLibError('Could not get full streamed logs') from error

        for status_update in response_json.get('previous_status_updates', []):
            logger.info(f'Cloud: {status_update["log_message"]}')

        self.print_logs_packages(response_json['streamed_logs_packages_b64'])

    def _get_cloud_job_awaiting_started(self) -> CloudJobStartedDict:
        retry_count = 0
        while True:
            retry_count += 1
            time.sleep(min(10, retry_count))
            cloud_job = self._get_cloud_job()

            if cloud_job['finished_at']:
                raise CloudJobFinishedError()

            if cloud_job and cloud_job['started_at']:
                if not cloud_job['compute_node_url']:
                    raise BioLibError(f'Failed to get URL to compute node for job {self._uuid}')

                return cast(CloudJobStartedDict, cloud_job)

            logger.info('Cloud: The job has been queued. Please wait...')

    def _get_job_status_from_compute_node(self, compute_node_url):
        for _ in range(15):
            try:
                return HttpClient.request(url=f'{compute_node_url}/v1/job/{self._uuid}/status/').json()
            except Exception:  # pylint: disable=broad-except
                cloud_job = self._get_cloud_job()
                logger.debug('Failed to get status from compute node, retrying...')
                if cloud_job['finished_at']:
                    logger.debug('Result no longer exists on compute node, checking for error...')
                    if cloud_job['error_code'] != SystemExceptionCodes.COMPLETED_SUCCESSFULLY.value:
                        error_message = SystemExceptionCodeMap.get(
                            cloud_job['error_code'], f'Unknown error code {cloud_job["error_code"]}'
                        )
                        raise BioLibError(f'Cloud: {error_message}') from None
                    else:
                        logger.info(f'The job {self._uuid} is finished. Get its output by calling `.result()`')
                        return

                time.sleep(2)

        raise BioLibError(
            'Failed to stream logs, did you lose internet connection?\n'
            'Call `.stream_logs()` on your job to resume streaming logs.'
        )

    def _refetch_job_dict(self, force_refetch: Optional[bool] = False) -> None:
        if not force_refetch and self._job_dict_last_fetched_at > datetime.utcnow() - timedelta(seconds=2):
            return

        self._job_dict = self._get_job_dict(self._uuid, self._auth_token)
        self._job_dict_last_fetched_at = datetime.utcnow()

    @staticmethod
    def _start_job_in_cloud(
        app_uri: str,
        app_version_uuid: str,
        module_input_serialized: bytes,
        override_command: bool = False,
        machine: Optional[str] = None,
        experiment_id: Optional[str] = None,
        result_prefix: Optional[str] = None,
        timeout: Optional[int] = None,
        notify: bool = False,
        requested_machine_count: Optional[int] = None,
        temporary_client_secrets: Optional[Dict[str, str]] = None,
        api_client: Optional[ApiClient] = None,
    ) -> 'Result':
        if len(module_input_serialized) < 500_000 and temporary_client_secrets is None:
            _job_dict = BiolibJobApi.create_job_with_data(
                app_resource_name_prefix=parse_app_uri(app_uri)['resource_name_prefix'],
                app_version_uuid=app_version_uuid,
                arguments_override_command=override_command,
                experiment_uuid=experiment_id,
                module_input_serialized=module_input_serialized,
                notify=notify,
                requested_machine=machine,
                requested_timeout_seconds=timeout,
                result_name_prefix=result_prefix,
                requested_machine_count=requested_machine_count,
                api_client=api_client,
            )
            return Result(cast(JobDict, _job_dict))

        job_dict: CreatedJobDict = BiolibJobApi.create(
            app_resource_name_prefix=parse_app_uri(app_uri)['resource_name_prefix'],
            app_version_id=app_version_uuid,
            experiment_uuid=experiment_id,
            machine=machine,
            notify=notify,
            override_command=override_command,
            timeout=timeout,
            requested_machine_count=requested_machine_count,
            temporary_client_secrets=temporary_client_secrets,
            api_client=api_client,
        )
        JobStorage.upload_module_input(job=job_dict, module_input_serialized=module_input_serialized)
        cloud_job = BiolibJobApi.create_cloud_job(job_id=job_dict['public_id'], result_name_prefix=result_prefix)
        logger.debug(f"Cloud: Job created with id {cloud_job['public_id']}")
        return Result(cast(JobDict, job_dict), _api_client=api_client)


class Job(Result):
    """
    Deprecated class. `Job` extends the `Result` class and is retained for backward compatibility.
    Please use the `Result` class instead.
    """
