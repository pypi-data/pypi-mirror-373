import os
from collections import namedtuple
from datetime import datetime
from pathlib import Path
from struct import Struct
from typing import Callable, Dict, Iterable, List, Optional, Union, cast

from biolib import api
from biolib._internal import types
from biolib._internal.data_record import get_data_record_state_from_uri
from biolib._internal.data_record.data_record import validate_sqlite_v1
from biolib._internal.data_record.push_data import (
    push_data_path,
    validate_data_path_and_get_files_and_size_of_directory,
)
from biolib._internal.data_record.remote_storage_endpoint import DataRecordRemoteStorageEndpoint
from biolib._internal.http_client import HttpClient
from biolib._internal.types.file_node import ZipFileNodeDict
from biolib.api import client as api_client
from biolib.biolib_api_client import BiolibApiClient
from biolib.biolib_api_client.lfs_types import DataRecordInfo, DataRecordVersion, DataRecordVersionInfo
from biolib.biolib_binary_format import LazyLoadedFile
from biolib.biolib_binary_format.utils import RemoteIndexableBuffer
from biolib.biolib_logging import logger
from biolib.utils.app_uri import parse_app_uri

PathFilter = Union[str, List[str], Callable[[str], bool]]


class DataRecord:
    def __init__(self, _internal_state: DataRecordVersionInfo):
        self._state = _internal_state

    def __repr__(self):
        return f'DataRecord: {self._state["resource_uri"]}'

    @property
    def uri(self) -> str:
        return self._state['resource_uri']

    @property
    def uuid(self) -> str:
        return self._state['resource_uuid']

    @property
    def name(self) -> str:
        uri_parsed = parse_app_uri(self._state['resource_uri'], use_account_as_name_default=False)
        if not uri_parsed['app_name']:
            raise ValueError('Expected parameter "resource_uri" to contain resource name')

        return uri_parsed['app_name']

    def list_files(
        self,
        path_filter: Optional[PathFilter] = None,
        max_count: Optional[int] = 100_000,
    ) -> List[LazyLoadedFile]:
        files = list(
            self._fetch_files(
                path_filter=path_filter,
                max_count=max_count + 1 if max_count is not None else None,
            )
        )

        if max_count is not None and len(files) > max_count:
            raise Exception(
                f'list_files returned more than {max_count} files. '
                f'Please set the keyword argument "max_count" to a higher number.'
            )

        return files

    def download_zip(self, output_path: str):
        remote_storage_endpoint = DataRecordRemoteStorageEndpoint(
            resource_version_uuid=self._state['resource_version_uuid'],
        )
        HttpClient.request(url=remote_storage_endpoint.get_remote_url(), response_path=output_path)

    def download_files(self, output_dir: str, path_filter: Optional[PathFilter] = None) -> None:
        filtered_files = self.list_files(path_filter=path_filter)

        if len(filtered_files) == 0:
            logger.debug('No files to save')
            return

        for file in filtered_files:
            file_path = os.path.join(output_dir, file.path)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, mode='wb') as file_handle:
                for chunk in file.get_data_iterator():
                    file_handle.write(chunk)

    def save_files(self, output_dir: str, path_filter: Optional[PathFilter] = None) -> None:
        self.download_files(output_dir=output_dir, path_filter=path_filter)

    def update(self, data_path: str, chunk_size_in_mb: Optional[int] = None) -> None:
        BiolibApiClient.assert_is_signed_in(authenticated_action_description='push data to a Data Record')
        files_to_zip, data_size_in_bytes = validate_data_path_and_get_files_and_size_of_directory(data_path)

        # validate data record
        detailed_dict: types.DataRecordDetailedDict = self._get_detailed_dict()
        if detailed_dict['type']:
            # only validate if data record has a type
            data_record_type: types.DataRecordTypeDict = detailed_dict['type']
            logger.info(f"Validating data record of type {data_record_type['name']}")
            for rule in data_record_type['validation_rules']:
                logger.info(f"Validating rule {rule['type']} for {rule['path']}...")
                if rule['type'] == 'sqlite-v1':
                    try:
                        validate_sqlite_v1(schema=rule['rule'], sqlite_file=Path(rule['path']))
                    except Exception as error:
                        raise Exception('Data Record Validation failed') from error
                else:
                    raise Exception(f"Error processing data record validation: unknown rule type {rule['type']}")

        response = api.client.post(path='/lfs/versions/', data={'resource_uuid': self._state['resource_uuid']})
        data_record_version: DataRecordVersion = response.json()
        resource_version_uuid = data_record_version['uuid']

        push_data_path(
            data_path=data_path,
            data_size_in_bytes=data_size_in_bytes,
            files_to_zip=files_to_zip,
            resource_version_uuid=resource_version_uuid,
            chunk_size_in_mb=chunk_size_in_mb,
        )

        api.client.patch(
            path=f'/resources/versions/{resource_version_uuid}/',
            data={'state': 'published', 'set_as_active': True},
        )

        logger.info(f"Successfully pushed a new Data Record version '{data_record_version['uri']}'")
        self._state = get_data_record_state_from_uri(data_record_version['uri'])

    @staticmethod
    def get_by_uri(uri: str) -> 'DataRecord':
        return DataRecord(_internal_state=get_data_record_state_from_uri(uri))

    @staticmethod
    def create(destination: str, data_path: Optional[str] = None, record_type: Optional[str] = None) -> 'DataRecord':
        BiolibApiClient.assert_is_signed_in(authenticated_action_description='create a Data Record')
        if data_path is not None:
            assert os.path.isdir(data_path), f'The path "{data_path}" is not a directory.'
        uri_parsed = parse_app_uri(destination, use_account_as_name_default=False)
        if uri_parsed['app_name_normalized']:
            data_record_uri = destination
        else:
            record_name = 'data-record-' + datetime.now().isoformat().split('.')[0].replace(':', '-')
            data_record_uri = f'{destination}/{record_name}'

        response = api.client.post(
            path='/resources/data-records/',
            data={
                'uri': data_record_uri,
                'type': record_type,
            },
        )
        data_record_info: DataRecordInfo = response.json()
        logger.info(f"Successfully created new Data Record '{data_record_info['uri']}'")

        data_record = DataRecord.get_by_uri(uri=data_record_info['uri'])
        if data_path is not None:
            data_record.update(data_path=data_path)

        return data_record

    @staticmethod
    def fetch(uri: Optional[str] = None, count: Optional[int] = None) -> List['DataRecord']:
        max_page_size = 1_000
        params: Dict[str, Union[str, int]] = {
            'page_size': str(count or max_page_size),
            'resource_type': 'data-record',
        }
        if uri:
            uri_parsed = parse_app_uri(uri, use_account_as_name_default=False)
            params['account_handle'] = uri_parsed['account_handle_normalized']
            if uri_parsed['app_name_normalized']:
                params['app_name'] = uri_parsed['app_name_normalized']

        results = api_client.get(path='/apps/', params=params).json()['results']
        if count is None and len(results) == max_page_size:
            logger.warning(
                f'Fetch results exceeded maximum count of {max_page_size}. Some data records might not be fetched.'
            )

        return [
            DataRecord(
                _internal_state={
                    'resource_uri': result['resource_uri'],
                    'resource_uuid': result['public_id'],
                    'resource_version_uuid': result['active_version'],
                }
            )
            for result in results
        ]

    def _fetch_files(
        self,
        max_count: Optional[int],
        path_filter: Optional[PathFilter] = None,
    ) -> Iterable[LazyLoadedFile]:
        if path_filter and not (isinstance(path_filter, (str, list)) or callable(path_filter)):
            raise Exception('Expected path_filter to be a string, a list of strings or a function')

        path_filters = (
            [path_filter] if isinstance(path_filter, str) else path_filter if isinstance(path_filter, list) else []
        )

        resource_version_uuid = self._state['resource_version_uuid']
        remote_storage_endpoint = DataRecordRemoteStorageEndpoint(resource_version_uuid)

        page: Optional[int] = 1
        yielded_files: int = 0
        while page:
            response = api.client.post(
                path=f'/proxy/files/data-record-versions/{resource_version_uuid}/query/',
                data=dict(page=page, page_size=1_000, path_filters=path_filters),
            ).json()

            for file_node_dict in cast(List[ZipFileNodeDict], response['results']):
                if file_node_dict['is_dir']:
                    continue

                if callable(path_filter) and not path_filter(file_node_dict['dir_path'] + file_node_dict['name']):
                    continue

                yield self._get_file(remote_storage_endpoint, file_node_dict)
                yielded_files += 1

                if max_count is not None and yielded_files >= max_count:
                    page = None
                    break

            page = page + 1 if page is not None and response['page_count'] > page else None

    @staticmethod
    def _get_file(
        remote_storage_endpoint: DataRecordRemoteStorageEndpoint,
        file_node_dict: ZipFileNodeDict,
    ) -> LazyLoadedFile:
        local_file_header_signature_bytes = b'\x50\x4b\x03\x04'
        local_file_header_struct = Struct('<H2sHHHIIIHH')
        LocalFileHeader = namedtuple(
            'LocalFileHeader',
            (
                'version',
                'flags',
                'compression_raw',
                'mod_time',
                'mod_date',
                'crc_32_expected',
                'compressed_size_raw',
                'uncompressed_size_raw',
                'file_name_len',
                'extra_field_len',
            ),
        )

        local_file_header_start = file_node_dict['zip_meta']['header_start'] + len(local_file_header_signature_bytes)
        local_file_header_end = local_file_header_start + local_file_header_struct.size

        def file_start_func() -> int:
            local_file_header_response = HttpClient.request(
                url=remote_storage_endpoint.get_remote_url(),
                headers={'range': f'bytes={local_file_header_start}-{local_file_header_end - 1}'},
                timeout_in_seconds=300,
            )
            local_file_header = LocalFileHeader._make(
                local_file_header_struct.unpack(local_file_header_response.content)
            )
            file_start: int = (
                local_file_header_end + local_file_header.file_name_len + local_file_header.extra_field_len
            )
            return file_start

        return LazyLoadedFile(
            buffer=RemoteIndexableBuffer(endpoint=remote_storage_endpoint),
            length=file_node_dict['zip_meta']['size_on_disk'],
            path=file_node_dict['dir_path'] + file_node_dict['name'],
            start=None,
            start_func=file_start_func,
        )

    def _get_detailed_dict(self) -> types.DataRecordDetailedDict:
        return cast(types.DataRecordDetailedDict, api_client.get(f'/resources/data-records/{self.uuid}/').json())

    def delete(self) -> None:
        """Delete the data record.

        Example::
            >>> record = DataRecord.get_by_uri("account/data-record")
            >>> record.delete()
        """
        try:
            api_client.delete(path=f'/apps/{self.uuid}/')
            logger.info(f'Data record {self.uri} deleted')
        except Exception as error:
            raise Exception(f'Failed to delete data record {self.uri} due to: {error}') from error
