import hashlib
import io
import os
import zipfile as zf
from pathlib import Path

from biolib.typing_utils import Iterator, List, Tuple


def get_files_and_size_of_directory(directory: str) -> Tuple[List[str], int]:
    data_size = 0
    file_list: List[str] = []

    for path, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(path, file)
            if os.path.islink(file_path):
                continue  # skip symlinks

            relative_file_path = file_path[len(directory) + 1 :]  # +1 to remove starting slash
            file_list.append(relative_file_path)
            data_size += os.path.getsize(file_path)

    return file_list, data_size


def get_iterable_zip_stream(files: List[str], chunk_size: int) -> Iterator[bytes]:
    class ChunkedIOBuffer(io.RawIOBase):
        def __init__(self, chunk_size: int):
            super().__init__()
            self.chunk_size = chunk_size
            self.tmp_data = bytearray()

        def get_buffer_size(self):
            return len(self.tmp_data)

        def read_chunk(self):
            chunk = bytes(self.tmp_data[: self.chunk_size])
            self.tmp_data = self.tmp_data[self.chunk_size :]
            return chunk

        def write(self, data):
            data_length = len(data)
            self.tmp_data += data
            return data_length

    # create chunked buffer to hold data temporarily
    io_buffer = ChunkedIOBuffer(chunk_size)

    # create zip writer that will write to the io buffer
    zip_writer = zf.ZipFile(io_buffer, mode='w')  # type: ignore

    for file_path in files:
        # generate zip info and prepare zip pointer for writing
        z_info = zf.ZipInfo.from_file(file_path)
        zip_pointer = zip_writer.open(z_info, mode='w')
        if Path(file_path).is_file():
            # read file chunk by chunk
            with open(file_path, 'br') as file_pointer:
                while True:
                    chunk = file_pointer.read(chunk_size)
                    if len(chunk) == 0:
                        break
                    # write the chunk to the zip
                    zip_pointer.write(chunk)
                    # if writing the chunk caused us to go over chunk_size, flush it
                    if io_buffer.get_buffer_size() > chunk_size:
                        yield io_buffer.read_chunk()

        zip_pointer.close()

    # flush any remaining data in the stream (e.g. zip file meta data)
    zip_writer.close()
    while True:
        chunk = io_buffer.read_chunk()
        if len(chunk) == 0:
            break
        yield chunk


def path_to_renamed_path(path_str: str, prefix_with_slash: bool = True) -> str:
    """
    Normalize file paths consistently:
    - If path contains '..' (relative path going up), convert to absolute path
    - If relative path not containing '..', keep as is, but prepend / if prefix_with_slash=True
    - If absolute path that is subpath of current directory, convert to relative path
    - If absolute path not subpath of current directory, hash the folder path and keep filename
    """
    path = Path(path_str)
    current_dir = Path.cwd()

    if '..' in path.parts:
        resolved_path = path.resolve()
        try:
            relative_path = resolved_path.relative_to(current_dir)
            result = str(relative_path)
        except ValueError:
            folder_path = str(resolved_path.parent)
            filename = resolved_path.name
            folder_hash = hashlib.md5(folder_path.encode()).hexdigest()[:6]
            result = f'/{folder_hash}/{filename}'
    elif path.is_absolute():
        try:
            resolved_path = path.resolve()
            relative_path = resolved_path.relative_to(current_dir)
            result = str(relative_path)
        except ValueError:
            folder_path = str(path.parent)
            filename = path.name
            folder_hash = hashlib.md5(folder_path.encode()).hexdigest()[:6]
            result = f'/{folder_hash}/{filename}'
    else:
        result = path_str

    if prefix_with_slash:
        if not result.startswith('/'):
            return '/' + result
        return result
    else:
        if result.startswith('/'):
            return result[1:]
        return result
