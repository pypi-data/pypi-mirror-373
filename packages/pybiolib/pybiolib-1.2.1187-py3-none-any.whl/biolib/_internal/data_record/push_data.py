import os

from biolib import utils
from biolib._internal.file_utils import get_files_and_size_of_directory, get_iterable_zip_stream
from biolib._internal.types.typing import List, Optional, Tuple
from biolib.biolib_errors import BioLibError
from biolib.biolib_logging import logger


def validate_data_path_and_get_files_and_size_of_directory(data_path: str) -> Tuple[List[str], int]:
    assert os.path.isdir(data_path), f'The path "{data_path}" is not a directory.'

    if os.path.realpath(data_path) == '/':
        raise BioLibError('Pushing your root directory is not possible')

    original_working_dir = os.getcwd()
    os.chdir(data_path)
    files_to_zip, data_size_in_bytes = get_files_and_size_of_directory(directory=os.getcwd())
    os.chdir(original_working_dir)

    if data_size_in_bytes > 4_500_000_000_000:
        raise BioLibError('Attempted to push directory with a size larger than the limit of 4.5 TB')

    return files_to_zip, data_size_in_bytes


def push_data_path(
    data_path: str,
    data_size_in_bytes: int,
    files_to_zip: List[str],
    resource_version_uuid: str,
    chunk_size_in_mb: Optional[int] = None,
) -> None:
    original_working_dir = os.getcwd()
    os.chdir(data_path)

    min_chunk_size_bytes = 10_000_000
    chunk_size_in_bytes: int
    if chunk_size_in_mb:
        chunk_size_in_bytes = chunk_size_in_mb * 1_000_000  # Convert megabytes to bytes
        if chunk_size_in_bytes < min_chunk_size_bytes:
            logger.warning('Specified chunk size is too small, using minimum of 10 MB instead.')
            chunk_size_in_bytes = min_chunk_size_bytes
    else:
        # Calculate chunk size based on max chunk count of 10_000, using 9_000 to be on the safe side
        chunk_size_in_bytes = max(min_chunk_size_bytes, int(data_size_in_bytes / 9_000))

    data_size_in_mb = round(data_size_in_bytes / 10**6)
    logger.info(f'Zipping {len(files_to_zip)} files, in total ~{data_size_in_mb}mb of data')

    iterable_zip_stream = get_iterable_zip_stream(files=files_to_zip, chunk_size=chunk_size_in_bytes)
    multipart_uploader = utils.MultiPartUploader(
        use_process_pool=True,
        get_presigned_upload_url_request=dict(
            headers=None,
            requires_biolib_auth=True,
            path=f'/lfs/versions/{resource_version_uuid}/presigned_upload_url/',
        ),
        complete_upload_request=dict(
            headers=None,
            requires_biolib_auth=True,
            path=f'/lfs/versions/{resource_version_uuid}/complete_upload/',
        ),
    )

    multipart_uploader.upload(payload_iterator=iterable_zip_stream, payload_size_in_bytes=data_size_in_bytes)
    os.chdir(original_working_dir)
