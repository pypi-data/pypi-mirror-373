from biolib.biolib_binary_format.utils import IndexableBuffer
from biolib.typing_utils import Iterable


class StreamSeeker:
    def __init__(
            self,
            upstream_buffer: IndexableBuffer,
            files_data_start: int,
            files_data_end: int,
            download_chunk_size_in_bytes: int,
    ):
        self._upstream_buffer = upstream_buffer
        self._files_data_end = files_data_end
        self._download_chunk_size_in_bytes = download_chunk_size_in_bytes

        self._buffer_start = files_data_start
        self._buffer = bytearray()

    def seek_and_read(self, file_start: int, file_length: int) -> Iterable[bytes]:
        assert file_start >= self._buffer_start
        self._buffer = self._buffer[file_start - self._buffer_start:]  # Returns empty array if "out of bounds"
        self._buffer_start = file_start

        while True:
            file_byte_count_remaining = file_length - (self._buffer_start - file_start)
            if file_byte_count_remaining == 0:
                return

            start_of_fetch = self._buffer_start + len(self._buffer)
            byte_count_left_in_stream = self._files_data_end - start_of_fetch

            if byte_count_left_in_stream != 0:
                # Only fetch if there is still data left upstream
                if self._download_chunk_size_in_bytes > len(self._buffer):
                    # Only fetch if size of buffer is below chunk size
                    self._buffer.extend(self._upstream_buffer.get_data(
                        start=start_of_fetch,
                        length=min(byte_count_left_in_stream, self._download_chunk_size_in_bytes),
                    ))

            bytes_to_yield = self._buffer[:file_byte_count_remaining]  # Returns empty array if "out of bounds"
            yield bytes_to_yield
            self._buffer = self._buffer[file_byte_count_remaining:]  # Returns empty array if "out of bounds"
            self._buffer_start += len(bytes_to_yield)
