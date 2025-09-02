import time
from fnmatch import fnmatch
from pathlib import Path

from biolib.biolib_binary_format import ModuleOutputV2
from biolib.biolib_binary_format.remote_endpoints import RemoteJobStorageEndpoint
from biolib.biolib_binary_format.remote_stream_seeker import StreamSeeker
from biolib.biolib_binary_format.utils import LazyLoadedFile, RemoteIndexableBuffer
from biolib.biolib_errors import BioLibError
from biolib.biolib_logging import logger
from biolib.typing_utils import Callable, List, Optional, Union, cast

PathFilter = Union[str, Callable[[str], bool]]


class JobResult:
    def __init__(
        self,
        job_uuid: str,
        job_auth_token: str,
        module_output: Optional[ModuleOutputV2] = None,
    ):
        self._job_uuid: str = job_uuid
        self._job_auth_token: str = job_auth_token

        self._module_output: Optional[ModuleOutputV2] = module_output

    def get_stdout(self) -> bytes:
        return self._get_module_output().get_stdout()

    def get_stderr(self) -> bytes:
        return self._get_module_output().get_stderr()

    def get_exit_code(self) -> int:
        return self._get_module_output().get_exit_code()

    def save_files(
        self,
        output_dir: str,
        path_filter: Optional[PathFilter] = None,
        skip_file_if_exists: Optional[bool] = None,
        overwrite: bool = False,
    ) -> None:
        module_output = self._get_module_output()
        output_files = module_output.get_files()
        filtered_output_files = self._get_filtered_files(output_files, path_filter) if path_filter else output_files

        if len(filtered_output_files) == 0:
            logger.debug('No output files to save')
            return

        total_files_data_to_download_in_bytes = sum(file.length for file in filtered_output_files)

        # Assume files are in order
        first_file = filtered_output_files[0]
        last_file = filtered_output_files[len(filtered_output_files) - 1]
        stream_seeker = StreamSeeker(
            files_data_start=first_file.start,
            files_data_end=last_file.start + last_file.length,
            download_chunk_size_in_bytes=min(total_files_data_to_download_in_bytes, 10_000_000),
            upstream_buffer=module_output.buffer,
        )

        logger.info(f'Saving {len(filtered_output_files)} files to {output_dir}...')
        for file in filtered_output_files:
            # Remove leading slash of file_path
            destination_file_path = Path(output_dir) / Path(file.path.lstrip('/'))
            if destination_file_path.exists():
                if skip_file_if_exists:
                    print(f'Skipping {destination_file_path} as a file with that name already exists locally.')
                    continue
                elif not overwrite:
                    raise BioLibError(f'File {destination_file_path} already exists. Set overwrite=True to overwrite.')
                else:
                    destination_file_path.rename(
                        f'{destination_file_path}.biolib-renamed.{time.strftime("%Y%m%d%H%M%S")}'
                    )

            dir_path = destination_file_path.parent
            if dir_path:
                dir_path.mkdir(parents=True, exist_ok=True)

            # write content to temporary (partial) file
            partial_path = destination_file_path.with_suffix(
                destination_file_path.suffix + f'.{self._job_uuid}.partial_biolib_download'
            )
            file_start = file.start
            data_to_download = file.length
            if partial_path.exists():
                data_already_downloaded = partial_path.stat().st_size
                file_start += data_already_downloaded
                data_to_download -= data_already_downloaded

            with open(partial_path, mode='ab') as partial_file:
                for chunk in stream_seeker.seek_and_read(file_start=file_start, file_length=data_to_download):
                    partial_file.write(chunk)

            # rename partial file to actual file name
            partial_path.rename(destination_file_path)

    def get_output_file(self, filename) -> LazyLoadedFile:
        files = self._get_module_output().get_files()
        filtered_files = self._get_filtered_files(files, path_filter=filename)
        if not filtered_files:
            raise BioLibError(f'File {filename} not found in results.')

        if len(filtered_files) != 1:
            raise BioLibError(f'Found multiple results for filename {filename}.')

        return filtered_files[0]

    def list_output_files(self, path_filter: Optional[PathFilter] = None) -> List[LazyLoadedFile]:
        files = self._get_module_output().get_files()
        if not path_filter:
            return files

        return self._get_filtered_files(files, path_filter)

    @staticmethod
    def _get_filtered_files(files: List[LazyLoadedFile], path_filter: PathFilter) -> List[LazyLoadedFile]:
        if not (isinstance(path_filter, str) or callable(path_filter)):
            raise Exception('Expected path_filter to be a string or a function')

        if callable(path_filter):
            return list(filter(lambda x: path_filter(x.path), files))  # type: ignore

        glob_filter = cast(str, path_filter)

        # since all file paths start with /, make sure filter does too
        if not glob_filter.startswith('/'):
            glob_filter = '/' + glob_filter

        def _filter_function(file: LazyLoadedFile) -> bool:
            return fnmatch(file.path, glob_filter)

        return list(filter(_filter_function, files))

    def _get_module_output(self) -> ModuleOutputV2:
        if self._module_output is None:
            remote_job_storage_endpoint = RemoteJobStorageEndpoint(
                job_auth_token=self._job_auth_token,
                job_uuid=self._job_uuid,
                storage_type='output',
            )
            buffer = RemoteIndexableBuffer(endpoint=remote_job_storage_endpoint)
            self._module_output = ModuleOutputV2(buffer)

        return self._module_output
