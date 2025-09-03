#  Copyright © 2025 Bentley Systems, Incorporated
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#      http://www.apache.org/licenses/LICENSE-2.0
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from threading import Lock
from typing import BinaryIO

from evo import logging

from .interfaces import IDestination, ISource

logger = logging.getLogger("io.bytes")

__all__ = [
    "BytesDestination",
    "BytesSource",
]


class BytesDestination(IDestination):
    """A wrapper for a writable binary buffer, usually an open file."""

    def __init__(self, backend: BinaryIO):
        self._backend = backend
        self._write_lock = Lock()

    async def write_chunk(self, offset: int, data: bytes) -> None:
        """Write raw data to the destination at the provided offset.

        BytesDestination does not handle any errors from the underlying buffer. Any errors that occur must be handled
        by the calling code.
        """
        logger.debug(f"Writing {len(data)} bytes at offset {offset}")
        with self._write_lock:
            self._backend.seek(offset)
            self._backend.write(data)


class BytesSource(ISource):
    """A wrapper for a readable binary buffer, usually an open file."""

    def __init__(self, backend: BinaryIO, size: int | None = None) -> None:
        """
        :param backend: A readable binary buffer.
        :param size: The size of the source data, or None. If None, the size will be determined by seeking to the end
            of the buffer the first time `get_size()` is called.
        """
        self._backend = backend
        self._size = size
        self._read_lock = Lock()

    async def get_size(self) -> int:
        """Get the size of the source data.

        :returns: The size of the source data.
        """
        if self._size is None:
            with self._read_lock:
                # No need to seek back to the original position, because `read_chunk` will always seek to the correct
                # position before reading.
                self._size = self._backend.seek(0, 2)
        return self._size

    async def read_chunk(self, offset: int, length: int) -> bytes:
        """Read <length> bytes of raw data from the source, starting at the given offset.

        BytesSource does not handle any errors from the underlying buffer. Any errors that occur must be handled
        by the calling code.

        :param offset: The offset in the source data to start reading from.
        :param length: The number of bytes to read.

        :returns: The raw data read from the source.
        """
        logger.debug(f"Reading {length} bytes at offset {offset}")
        with self._read_lock:
            self._backend.seek(offset)
            return self._backend.read(length)
