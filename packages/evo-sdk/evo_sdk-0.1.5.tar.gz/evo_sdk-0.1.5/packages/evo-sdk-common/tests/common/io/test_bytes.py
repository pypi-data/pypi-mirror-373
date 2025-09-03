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

import unittest
from io import BytesIO
from unittest import mock

from parameterized import parameterized

from evo.common.io import BytesDestination, BytesSource

from .common import TestISource


class TestBytesDestination(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.buffer = BytesIO()
        self.destination = BytesDestination(self.buffer)

    @parameterized.expand(
        [
            ("next byte", 0, b"\xaa", b"\xaa"),
            ("skip bytes", 3, b"\xaa", b"\x00\x00\x00\xaa"),
        ]
    )
    async def test_write_chunk(self, _name: str, offset: int, data: bytes, expected_result: bytes) -> None:
        await self.destination.write_chunk(offset, data)
        self.buffer.seek(0)
        actual_result = self.buffer.read()
        self.assertEqual(expected_result, actual_result)


class TestBytesSource(TestISource):
    def setup_source(self, test_data: bytes) -> None:
        self.buffer = BytesIO(test_data)
        self.source = BytesSource(self.buffer, len(test_data))

    @parameterized.expand(
        [
            ("with buffer at start", 0),
            ("with buffer at end", 5),
            ("with buffer in middle", 2),
        ]
    )
    async def get_size_uninitialized(self, _label: str, offset_start: int) -> None:
        expected_size = self.buffer.seek(0, 2)
        self.buffer.seek(offset_start)

        # Mock the buffer to ensure that it is not being used prematurely.
        mock_buffer = mock.Mock(wraps=self.buffer)
        source = BytesSource(mock_buffer)

        # Ensure that the size is not calculated during initialization.
        mock_buffer.seek.assert_not_called()
        mock_buffer.tell.assert_not_called()

        # Ensure that the size is correctly calculated when `get_size` is called.
        actual = await source.get_size()
        self.assertEqual(expected_size, actual)
        mock_buffer.seek.assert_called_once_with(0, 2)

        # Ensure that the size is cached
        mock_buffer.seek.reset_mock()
        actual = await source.get_size()
        self.assertEqual(expected_size, actual)
        mock_buffer.seek.assert_not_called()


# Delete base test classes to prevent discovery by unittest.
del TestISource
