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

from evo.common.io import Upload
from evo.common.test_tools import TestWithUploadHandler, UrlGenerator

from .common import TEST_DATA


class MyUpload(Upload):
    def __init__(self, url_generator: UrlGenerator) -> None:
        self._generator = url_generator

    @property
    def label(self) -> str:
        return "test_upload"

    async def get_upload_url(self) -> str:
        return await self._generator.get_new_url()


class TestUpload(TestWithUploadHandler):
    def setUp(self) -> None:
        super().setUp()
        self.upload = MyUpload(self.url_generator)

    async def test_from_path(self) -> None:
        test_data_file = self.CACHE_DIR / "test_data_upload.csv"
        test_data_file.write_bytes(TEST_DATA)
        await self.upload.upload_from_path(test_data_file, self.transport)
        uploaded_data = await self.handler.get_committed()
        self.assertEqual(test_data_file.read_bytes(), uploaded_data)
