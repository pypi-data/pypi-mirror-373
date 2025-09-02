import json
import logging
import os
from typing import Dict, List

import click

from biolib._data_record.data_record import DataRecord
from biolib.biolib_api_client import BiolibApiClient
from biolib.biolib_logging import logger, logger_no_user_data
from biolib.typing_utils import Optional


@click.group(help='Data Records')
def data_record() -> None:
    logger.configure(default_log_level=logging.INFO)
    logger_no_user_data.configure(default_log_level=logging.INFO)


@data_record.command(help='Create a Data Record')
@click.argument('uri', required=True)
@click.option('--data-path', required=True, type=click.Path(exists=True))
@click.option('--record-type', required=False, type=str, default=None)
def create(uri: str, data_path: str, record_type: Optional[str]) -> None:
    DataRecord.create(destination=uri, data_path=data_path, record_type=record_type)


@data_record.command(help='Update a Data Record')
@click.argument('uri', required=True)
@click.option('--data-path', required=True, type=click.Path(exists=True))
@click.option('--chunk-size', default=None, required=False, type=click.INT, help='The size of each chunk (In MB)')
def update(uri: str, data_path: str, chunk_size: Optional[int]) -> None:
    DataRecord.get_by_uri(uri=uri).update(data_path=data_path, chunk_size_in_mb=chunk_size)


@data_record.command(help='Download files from a Data Record')
@click.argument('uri', required=True)
@click.option('--file', required=False, type=str)
@click.option('--path-filter', required=False, type=str, hide_input=True)
def download(uri: str, file: Optional[str], path_filter: Optional[str]) -> None:
    record = DataRecord.get_by_uri(uri=uri)
    if file is not None:
        try:
            file_obj = [file_obj for file_obj in record.list_files() if file_obj.path == file][0]
        except IndexError:
            raise Exception('File not found in data record') from None

        assert not os.path.exists(file_obj.name), 'File already exists in current directory'
        with open(file_obj.name, 'wb') as file_handle:
            file_handle.write(file_obj.get_data())

    else:
        assert not os.path.exists(record.name), f'Directory with name {record.name} already exists in current directory'
        record.save_files(output_dir=record.name, path_filter=path_filter)


@data_record.command(help='Describe a Data Record')
@click.argument('uri', required=True)
@click.option('--json', 'output_as_json', is_flag=True, default=False, required=False, help='Format output as JSON')
def describe(uri: str, output_as_json: bool) -> None:
    BiolibApiClient.assert_is_signed_in(authenticated_action_description='get Data Record description')
    record = DataRecord.get_by_uri(uri)
    files_info: List[Dict] = []
    total_size_in_bytes = 0
    for file in record.list_files():
        files_info.append({'path': file.path, 'size_bytes': file.length})
        total_size_in_bytes += file.length

    if output_as_json:
        print(
            json.dumps(
                obj={'uri': record.uri, 'size_bytes': total_size_in_bytes, 'files': files_info},
                indent=4,
            )
        )
    else:
        print(f'Data Record {record.uri}\ntotal {total_size_in_bytes} bytes\n')
        print('size bytes    path')
        for file_info in files_info:
            size_string = str(file_info['size_bytes'])
            leading_space_string = ' ' * (10 - len(size_string))
            print(f"{leading_space_string}{size_string}    {file_info['path']}")


@data_record.command(help='Delete a Data Record')
@click.argument('uri', required=True)
def delete(uri: str) -> None:
    record = DataRecord.get_by_uri(uri=uri)

    print(f'You are about to delete the data record: {record.uri}')
    print('This action cannot be undone.')

    confirmation = input(f'To confirm deletion, please type the data record name "{record.name}": ')
    if confirmation != record.name:
        print('Data record name does not match. Deletion cancelled.')
        return

    record.delete()
    print(f'Data record {record.uri} has been deleted.')
