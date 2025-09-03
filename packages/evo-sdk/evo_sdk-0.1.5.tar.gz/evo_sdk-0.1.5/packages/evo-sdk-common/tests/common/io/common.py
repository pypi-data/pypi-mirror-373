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

import asyncio
import unittest
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from parameterized import parameterized

from evo.common.io.interfaces import IDestination, ISource

__all__ = [
    "TEST_DATA",
    "AsyncIterator",
    "TestIDestination",
    "TestISource",
    "asynccontextmanager",
]

TEST_DATA = """
x,y,z
10689.54607,100813.2874,442.172449
10690.87819,100812.6204,437.399555
10692.21062,100811.9502,432.627182
10693.54337,100811.277,427.85533
10694.87638,100810.6009,423.083966
10696.06353,100809.9976,418.831067
10725.47983,100777.2912,448.471682
10727.51038,100775.9784,444.022761
10729.54666,100774.6657,439.576449
10731.58199,100773.3566,435.128615
""".lstrip().encode("utf-8")


class TestISource(unittest.IsolatedAsyncioTestCase):
    """Base class for testing ISource implementations."""

    source: ISource
    """The source to test."""

    def setUp(self) -> None:
        self.setup_source(TEST_DATA)
        self.assertIsInstance(self.source, ISource)

    def setup_source(self, test_data: bytes) -> None:
        """Hook for subclasses to set up the source with the given test data."""
        raise unittest.SkipTest("Subclasses must implement this method.")

    @asynccontextmanager
    async def ctx_test_get_size(self) -> AsyncIterator[None]:
        """Async context manager for testing conditions immediately before and after calling ISource.get_size()"""
        yield

    async def test_get_size(self) -> None:
        """Test that the size is correctly reported."""
        expected_size = len(TEST_DATA)
        async with self.ctx_test_get_size():
            actual_size = await self.source.get_size()
            self.assertEqual(expected_size, actual_size)

    @asynccontextmanager
    async def ctx_test_read_chunk(self, offset: int, length: int) -> AsyncIterator[None]:
        """Async context manager for testing conditions immediately before and after calling ISource.read_chunk().

        offset and length are the arguments that will be passed to read_chunk().

        :param offset: The offset argument that will be passed to read_chunk().
        :param length: The length argument that will be passed to read_chunk().
        """
        yield

    @parameterized.expand(
        [
            ("read first byte", 0, 1),
            ("read last byte", len(TEST_DATA) - 1, 1),
            ("read whole chunk", 0, 256),
            ("read part chunk", 256, 256),
        ]
    )
    async def test_read_chunk(self, _label: str, offset: int, length: int) -> None:
        """Test that the correct data is read from the source."""
        expected_result = TEST_DATA[offset : min(offset + length, len(TEST_DATA))]
        async with self.ctx_test_read_chunk(offset, length):
            actual_result = await self.source.read_chunk(offset, length)
            self.assertEqual(expected_result, actual_result)


class TestIDestination(unittest.IsolatedAsyncioTestCase):
    """Base class for testing IDestination implementations."""

    destination: IDestination
    """The destination to test."""

    def setUp(self) -> None:
        self.setup_destination()
        self.assertIsInstance(self.destination, IDestination)

    def setup_destination(self) -> None:
        """Hook for subclasses to set up the destination."""
        raise unittest.SkipTest("Subclasses must implement this method.")

    @asynccontextmanager
    async def ctx_test_write_chunk(self, offset: int, data: bytes) -> AsyncIterator[None]:
        """Async context manager for testing conditions immediately before and after calling ISource.read_chunk().

        offset and length are the arguments that will be passed to read_chunk().

        :param offset: The offset argument that will be passed to read_chunk().
        :param data: The data argument that will be passed to read_chunk().
        """
        yield

    @parameterized.expand(
        [
            ("write first byte", 0, 1),
            ("write last byte", len(TEST_DATA) - 1, 1),
            ("write whole chunk", 0, 256),
            ("write part chunk", 256, 256),
        ]
    )
    async def test_write_chunk(self, _label: str, offset: int, length: int) -> None:
        """Test that the correct data is written to the destination."""
        data = TEST_DATA[offset : min(offset + length, len(TEST_DATA))]
        async with self.ctx_test_write_chunk(offset, data):
            await self.destination.write_chunk(offset, data)

    async def write_whole_file(self) -> list[tuple[int, bytes]]:
        """Test writing the entire test data contents to the destination.

        :return: A list of tuples of the form (offset, data) where data is the data written at the given byte offset.
        """
        total_bytes = len(TEST_DATA)
        chunks_with_offset = [
            (offset, TEST_DATA[offset : min(offset + 32, total_bytes)])
            for offset in range(0, total_bytes, 32)  # Use really small chunks for the sake of this test.
        ]
        tasks = [self.destination.write_chunk(offset, chunk) for offset, chunk in chunks_with_offset]
        await asyncio.gather(*tasks)
        return chunks_with_offset
