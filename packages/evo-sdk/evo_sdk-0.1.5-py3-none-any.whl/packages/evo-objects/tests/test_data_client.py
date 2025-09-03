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

import json
from unittest import mock
from uuid import UUID

from data import load_test_data
from evo.common import IFeedback, RequestMethod
from evo.common.io.exceptions import DataExistsError
from evo.common.test_tools import TestWithConnector, TestWithStorage
from evo.common.utils import NoFeedback, PartialFeedback
from evo.objects.utils import KnownTableFormat, ObjectDataClient


class TestObjectDataClient(TestWithConnector, TestWithStorage):
    def setUp(self) -> None:
        TestWithConnector.setUp(self)
        TestWithStorage.setUp(self)
        self.data_client = ObjectDataClient(environment=self.environment, connector=self.connector, cache=self.cache)

    @property
    def base_path(self) -> str:
        return f"geoscience-object/orgs/{self.environment.org_id}/workspaces/{self.environment.workspace_id}"

    def test_save_table(self) -> None:
        """Test saving tabular data using pyarrow."""
        with (
            mock.patch("evo.objects.utils.table_formats.get_known_format") as mock_get_known_format,
            mock.patch("evo.common.io.upload.StorageDestination") as mock_destination,
        ):
            mock_table = mock.Mock()
            mock_get_known_format.return_value = mock_known_format = mock.Mock(spec=KnownTableFormat)
            mock_known_format.save_table.return_value = mock_table_info = {}

            actual_table_info = self.data_client.save_table(mock_table)

        mock_get_known_format.assert_called_once_with(mock_table)
        mock_known_format.save_table.assert_called_once_with(
            table=mock_table, destination=self.data_client.cache_location
        )
        mock_destination.upload_file.assert_not_called()
        self.transport.assert_no_requests()
        self.assertIs(mock_table_info, actual_table_info)

    def test_save_dataframe(self) -> None:
        """Test saving tabular data using pandas."""
        with (
            mock.patch("evo.objects.utils.table_formats.get_known_format") as mock_get_known_format,
            mock.patch("evo.common.io.upload.StorageDestination") as mock_destination,
            mock.patch("pyarrow.Table") as mock_pyarrow_table,
        ):
            mock_pyarrow_table.from_pandas.return_value = mock_table = mock.Mock()
            mock_get_known_format.return_value = mock_known_format = mock.Mock(spec=KnownTableFormat)
            mock_known_format.save_table.return_value = mock_table_info = {}

            mock_dataframe = mock.Mock()
            actual_table_info = self.data_client.save_dataframe(mock_dataframe)

        mock_get_known_format.assert_called_once_with(mock_table)
        mock_known_format.save_table.assert_called_once_with(
            table=mock_table, destination=self.data_client.cache_location
        )
        mock_destination.upload_file.assert_not_called()
        self.transport.assert_no_requests()
        self.assertIs(mock_table_info, actual_table_info)

    async def test_upload_referenced_data(self) -> None:
        put_data_response = load_test_data("put_data_batch.json")[:5]
        test_pointset = {
            "name": "Test Pointset",
            "uuid": None,
            "bounding_box": {"min_x": 0.0, "max_x": 0.0, "min_y": 0.0, "max_y": 0.0, "min_z": 0.0, "max_z": 0.0},
            "coordinate_reference_system": "unspecified",
            "locations": {
                "attributes": [
                    {
                        "name": f"Test Attribute {n}",
                        "nan_description": {"values": []},
                        "values": {
                            "data": data["name"],
                            "length": 0,
                            "width": 1,
                            "data_type": "float64",
                        },
                        "attribute_type": "scalar",
                    }
                    for n, data in enumerate(put_data_response[1:])
                ],
                "coordinates": {
                    "data": put_data_response[0]["name"],
                    "length": 0,
                    "width": 3,
                    "data_type": "float64",
                },
            },
            "schema": "/objects/pointset/1.1.0/pointset.schema.json",
        }

        data_by_name = {}
        for data in put_data_response:
            data_by_name[data["name"]] = data
            if data["exists"] is False:
                # Create an empty file to simulate the data being present in the cache.
                (self.data_client.cache_location / data["name"]).touch()

        with (
            self.transport.set_http_response(status_code=200, content=json.dumps(put_data_response)),
            mock.patch("evo.common.io.upload.StorageDestination", autospec=True) as mock_destination,
        ):

            async def _mock_upload_file_side_effect(*args, **kwargs):
                filename = kwargs["filename"]
                data = data_by_name.pop(filename.name)
                actual_upload_url = await kwargs["url_generator"]()
                self.assertEqual(data["upload_url"], actual_upload_url)
                self.assertIs(self.transport, kwargs["transport"])
                self.assertIsInstance(kwargs["fb"], PartialFeedback)

            mock_destination.upload_file.side_effect = _mock_upload_file_side_effect
            await self.data_client.upload_referenced_data(test_pointset, mock.Mock(spec=IFeedback))

        self.assert_request_made(
            method=RequestMethod.PUT,
            path=f"{self.base_path}/data",
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            body=[{"name": data["name"]} for data in put_data_response[1:]] + [{"name": put_data_response[0]["name"]}],
        )

    async def test_upload_table(self) -> None:
        """Test uploading tabular data using pyarrow or pandas."""
        put_data_response = load_test_data("put_data.json")
        with (
            self.transport.set_http_response(status_code=200, content=json.dumps(put_data_response)),
            mock.patch("evo.objects.utils.table_formats.get_known_format") as mock_get_known_format,
            mock.patch("evo.common.io.upload.StorageDestination", autospec=True) as mock_destination,
        ):
            mock_table = mock.Mock()
            mock_get_known_format.return_value = mock_known_format = mock.Mock(spec=KnownTableFormat)
            mock_known_format.save_table.return_value = mock_table_info = {}
            mock_table_info["data"] = mock_data_id = put_data_response[0]["name"]

            async def _mock_upload_file_side_effect(*args, **kwargs):
                expected_filename = self.data_client.cache_location / mock_data_id
                expected_upload_url = put_data_response[0].get("upload_url")
                actual_upload_url = await kwargs["url_generator"]()
                self.assertEqual(expected_filename, kwargs["filename"])
                self.assertEqual(expected_upload_url, actual_upload_url)
                self.assertIs(self.transport, kwargs["transport"])
                self.assertIs(NoFeedback, kwargs["fb"])

            mock_destination.upload_file.side_effect = _mock_upload_file_side_effect
            actual_table_info = await self.data_client.upload_table(mock_table)

        mock_get_known_format.assert_called_once_with(mock_table)
        mock_known_format.save_table.assert_called_once_with(
            table=mock_table, destination=self.data_client.cache_location
        )
        mock_destination.upload_file.assert_called_once()
        self.assert_request_made(
            method=RequestMethod.PUT,
            path=f"{self.base_path}/data",
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            body=[{"name": mock_data_id}],
        )
        self.assertIs(mock_table_info, actual_table_info)

    async def test_upload_dataframe(self) -> None:
        """Test uploading tabular data using pyarrow or pandas."""
        put_data_response = load_test_data("put_data.json")
        with (
            self.transport.set_http_response(status_code=200, content=json.dumps(put_data_response)),
            mock.patch("evo.objects.utils.table_formats.get_known_format") as mock_get_known_format,
            mock.patch("evo.common.io.upload.StorageDestination", autospec=True) as mock_destination,
            mock.patch("pyarrow.Table") as mock_pyarrow_table,
        ):
            mock_pyarrow_table.from_pandas.return_value = mock_table = mock.Mock()
            mock_get_known_format.return_value = mock_known_format = mock.Mock(spec=KnownTableFormat)
            mock_known_format.save_table.return_value = mock_table_info = {}
            mock_table_info["data"] = mock_data_id = put_data_response[0]["name"]

            async def _mock_upload_file_side_effect(*args, **kwargs):
                expected_filename = self.data_client.cache_location / mock_data_id
                expected_upload_url = put_data_response[0].get("upload_url")
                actual_upload_url = await kwargs["url_generator"]()
                self.assertEqual(expected_filename, kwargs["filename"])
                self.assertEqual(expected_upload_url, actual_upload_url)
                self.assertIs(self.transport, kwargs["transport"])
                self.assertIs(NoFeedback, kwargs["fb"])

            mock_destination.upload_file.side_effect = _mock_upload_file_side_effect

            mock_dataframe = mock.Mock()
            actual_table_info = await self.data_client.upload_dataframe(mock_dataframe)

        mock_get_known_format.assert_called_once_with(mock_table)
        mock_known_format.save_table.assert_called_once_with(
            table=mock_table, destination=self.data_client.cache_location
        )
        mock_destination.upload_file.assert_called_once()
        self.assert_request_made(
            method=RequestMethod.PUT,
            path=f"{self.base_path}/data",
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            body=[{"name": mock_data_id}],
        )
        self.assertIs(mock_table_info, actual_table_info)

    async def test_upload_table_exists(self) -> None:
        """Test uploading tabular data using pyarrow when the table exists."""
        put_data_response = load_test_data("put_data_exists.json")
        with (
            self.transport.set_http_response(status_code=200, content=json.dumps(put_data_response)),
            mock.patch("evo.objects.utils.table_formats.get_known_format") as mock_get_known_format,
            mock.patch("evo.common.io.upload.StorageDestination", autospec=True) as mock_destination,
        ):
            mock_table = mock.Mock()
            mock_get_known_format.return_value = mock_known_format = mock.Mock(spec=KnownTableFormat)
            mock_known_format.save_table.return_value = mock_table_info = {}
            mock_table_info["data"] = mock_data_id = put_data_response[0]["name"]

            async def _mock_upload_file_side_effect(*args, **kwargs):
                expected_filename = self.data_client.cache_location / mock_data_id
                self.assertEqual(expected_filename, kwargs["filename"])
                self.assertIs(self.transport, kwargs["transport"])
                self.assertIs(NoFeedback, kwargs["fb"])

                with self.assertRaises(DataExistsError) as cm:
                    await kwargs["url_generator"]()
                raise cm.exception  # upload_table() should catch this exception.

            mock_destination.upload_file.side_effect = _mock_upload_file_side_effect
            actual_table_info = await self.data_client.upload_table(mock_table)

        mock_get_known_format.assert_called_once_with(mock_table)
        mock_known_format.save_table.assert_called_once_with(
            table=mock_table, destination=self.data_client.cache_location
        )
        mock_destination.upload_file.assert_called_once()
        self.assert_request_made(
            method=RequestMethod.PUT,
            path=f"{self.base_path}/data",
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            body=[{"name": mock_data_id}],
        )
        self.assertIs(mock_table_info, actual_table_info)

    async def test_upload_dataframe_exists(self) -> None:
        """Test uploading tabular data using pandas when the table exists."""
        put_data_response = load_test_data("put_data_exists.json")
        with (
            self.transport.set_http_response(status_code=200, content=json.dumps(put_data_response)),
            mock.patch("evo.objects.utils.table_formats.get_known_format") as mock_get_known_format,
            mock.patch("evo.common.io.upload.StorageDestination", autospec=True) as mock_destination,
            mock.patch("pyarrow.Table") as mock_pyarrow_table,
        ):
            mock_pyarrow_table.from_pandas.return_value = mock_table = mock.Mock()
            mock_get_known_format.return_value = mock_known_format = mock.Mock(spec=KnownTableFormat)
            mock_known_format.save_table.return_value = mock_table_info = {}
            mock_table_info["data"] = mock_data_id = put_data_response[0]["name"]

            async def _mock_upload_file_side_effect(*args, **kwargs):
                expected_filename = self.data_client.cache_location / mock_data_id
                self.assertEqual(expected_filename, kwargs["filename"])
                self.assertIs(self.transport, kwargs["transport"])
                self.assertIs(NoFeedback, kwargs["fb"])

                with self.assertRaises(DataExistsError) as cm:
                    await kwargs["url_generator"]()
                raise cm.exception  # upload_table() should catch this exception.

            mock_destination.upload_file.side_effect = _mock_upload_file_side_effect

            mock_dataframe = mock.Mock()
            actual_table_info = await self.data_client.upload_dataframe(mock_dataframe)
            print(actual_table_info)

        mock_get_known_format.assert_called_once_with(mock_table)
        mock_known_format.save_table.assert_called_once_with(
            table=mock_table, destination=self.data_client.cache_location
        )
        mock_destination.upload_file.assert_called_once()
        self.assert_request_made(
            method=RequestMethod.PUT,
            path=f"{self.base_path}/data",
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            body=[{"name": mock_data_id}],
        )
        self.assertIs(mock_table_info, actual_table_info)

    async def test_download_table(self) -> None:
        """Test downloading tabular data using pyarrow."""
        get_object_response = load_test_data("get_object.json")
        object_id = UUID(int=2)
        with (
            self.transport.set_http_response(status_code=200, content=json.dumps(get_object_response)),
            mock.patch("evo.objects.utils.tables.KnownTableFormat") as mock_known_table_format,
            mock.patch("evo.common.io.download.HTTPSource", autospec=True) as mock_source,
        ):
            mock_table_info = {}
            mock_table_info["data"] = mock_data_id = "0000000000000000000000000000000000000000000000000000000000000001"
            mock_known_table_format.load_table = mock_load_table = mock.Mock()

            async def _mock_download_file_side_effect(*args, **kwargs):
                expected_filename = self.data_client.cache_location / mock_data_id
                expected_download_url = get_object_response["links"]["data"][1]["download_url"]
                actual_download_url = await kwargs["url_generator"]()
                self.assertEqual(expected_filename, kwargs["filename"])
                self.assertEqual(expected_download_url, actual_download_url)
                self.assertIs(self.transport, kwargs["transport"])
                self.assertIs(NoFeedback, kwargs["fb"])

            mock_source.download_file.side_effect = _mock_download_file_side_effect
            actual_table = await self.data_client.download_table(object_id, None, mock_table_info)

        mock_source.download_file.assert_called_once()
        self.assert_request_made(
            method=RequestMethod.GET,
            path=f"{self.base_path}/objects/{object_id}",
            headers={"Accept": "application/json", "Accept-Encoding": "gzip"},
        )
        mock_load_table.assert_called_once_with(mock_table_info, self.data_client.cache_location)
        self.assertIs(mock_load_table.return_value, actual_table)

    async def test_download_dataframe(self) -> None:
        """Test downloading tabular data using pandas."""
        get_object_response = load_test_data("get_object.json")
        object_id = UUID(int=2)
        with (
            self.transport.set_http_response(status_code=200, content=json.dumps(get_object_response)),
            mock.patch("evo.objects.utils.tables.KnownTableFormat") as mock_known_table_format,
            mock.patch("evo.common.io.download.HTTPSource", autospec=True) as mock_source,
        ):
            mock_table_info = {}
            mock_table_info["data"] = mock_data_id = "0000000000000000000000000000000000000000000000000000000000000001"
            mock_known_table_format.load_table = mock_load_table = mock.Mock()

            async def _mock_download_file_side_effect(*args, **kwargs):
                expected_filename = self.data_client.cache_location / mock_data_id
                expected_download_url = get_object_response["links"]["data"][1]["download_url"]
                actual_download_url = await kwargs["url_generator"]()
                self.assertEqual(expected_filename, kwargs["filename"])
                self.assertEqual(expected_download_url, actual_download_url)
                self.assertIs(self.transport, kwargs["transport"])
                self.assertIs(NoFeedback, kwargs["fb"])

            mock_source.download_file.side_effect = _mock_download_file_side_effect

            _actual_dataframe = await self.data_client.download_dataframe(object_id, None, mock_table_info)

        mock_source.download_file.assert_called_once()
        self.assert_request_made(
            method=RequestMethod.GET,
            path=f"{self.base_path}/objects/{object_id}",
            headers={"Accept": "application/json", "Accept-Encoding": "gzip"},
        )
        mock_load_table.assert_called_once_with(mock_table_info, self.data_client.cache_location)

    async def test_download_dataframe_error(self) -> None:
        """Test error when trying to download dataframe without pandas installed."""
        get_object_response = load_test_data("get_object.json")
        object_id = UUID(int=2)
        with (
            self.transport.set_http_response(status_code=200, content=json.dumps(get_object_response)),
            mock.patch("evo.objects.utils.tables.KnownTableFormat") as mock_known_table_format,
            mock.patch("evo.common.io.download.HTTPSource", autospec=True),
        ):
            mock_table_info = {}
            mock_table_info["data"] = "0000000000000000000000000000000000000000000000000000000000000001"

            mock_known_table_format.load_table.return_value = mock_table = mock.Mock()
            # This is the error that a non-mocked `pyarrow.Table.to_pandas()` would raise.
            mock_table.to_pandas.side_effect = ModuleNotFoundError("No module named 'pandas'")

            with self.assertRaisesRegex(
                RuntimeError, "Unable to download dataframe because the `pandas` package is not installed"
            ):
                _ = await self.data_client.download_dataframe(object_id, None, mock_table_info)

    async def test_download_table_confusable(self) -> None:
        """Test downloading tabular data using pyarrow that includes confusable types."""
        get_object_response = load_test_data("get_object_validator_check.json")
        object_id = UUID(int=2)
        with (
            self.transport.set_http_response(status_code=200, content=json.dumps(get_object_response)),
            mock.patch("evo.objects.utils.tables.KnownTableFormat") as mock_known_table_format,
            mock.patch("evo.common.io.download.HTTPSource", autospec=True) as mock_source,
        ):
            mock_table_info = {}
            mock_table_info["data"] = mock_data_name = (
                "995f2e6cab5ad17147d9c5fddf371189bef4b623f657dde91f175a0734ed17dc"
            )
            mock_known_table_format.load_table = mock_load_table = mock.Mock()

            async def _mock_download_file_side_effect(*args, **kwargs):
                expected_filename = self.data_client.cache_location / str(mock_data_name)
                expected_download_url = get_object_response["links"]["data"][0]["download_url"]
                actual_download_url = await kwargs["url_generator"]()
                self.assertEqual(expected_filename, kwargs["filename"])
                self.assertEqual(expected_download_url, actual_download_url)
                self.assertIs(self.transport, kwargs["transport"])
                self.assertIs(NoFeedback, kwargs["fb"])

            mock_source.download_file.side_effect = _mock_download_file_side_effect
            actual_table = await self.data_client.download_table(object_id, None, mock_table_info)

        mock_source.download_file.assert_called_once()
        self.assert_request_made(
            method=RequestMethod.GET,
            path=f"{self.base_path}/objects/{object_id}",
            headers={"Accept": "application/json", "Accept-Encoding": "gzip"},
        )
        mock_load_table.assert_called_once_with(mock_table_info, self.data_client.cache_location)
        self.assertIs(mock_load_table.return_value, actual_table)

    async def test_download_dataframe_confusable(self) -> None:
        """Test downloading tabular data using pandas that includes confusable types."""
        get_object_response = load_test_data("get_object_validator_check.json")
        object_id = UUID(int=2)
        with (
            self.transport.set_http_response(status_code=200, content=json.dumps(get_object_response)),
            mock.patch("evo.objects.utils.tables.KnownTableFormat") as mock_known_table_format,
            mock.patch("evo.common.io.download.HTTPSource", autospec=True) as mock_source,
        ):
            mock_table_info = {}
            mock_table_info["data"] = mock_data_name = (
                "995f2e6cab5ad17147d9c5fddf371189bef4b623f657dde91f175a0734ed17dc"
            )
            mock_known_table_format.load_table = mock_load_table = mock.Mock()

            async def _mock_download_file_side_effect(*args, **kwargs):
                expected_filename = self.data_client.cache_location / str(mock_data_name)
                expected_download_url = get_object_response["links"]["data"][0]["download_url"]
                actual_download_url = await kwargs["url_generator"]()
                self.assertEqual(expected_filename, kwargs["filename"])
                self.assertEqual(expected_download_url, actual_download_url)
                self.assertIs(self.transport, kwargs["transport"])
                self.assertIs(NoFeedback, kwargs["fb"])

            mock_source.download_file.side_effect = _mock_download_file_side_effect
            _actual_dataframe = await self.data_client.download_dataframe(object_id, None, mock_table_info)

        mock_source.download_file.assert_called_once()
        self.assert_request_made(
            method=RequestMethod.GET,
            path=f"{self.base_path}/objects/{object_id}",
            headers={"Accept": "application/json", "Accept-Encoding": "gzip"},
        )
        mock_load_table.assert_called_once_with(mock_table_info, self.data_client.cache_location)

    async def test_download_table_already_downloaded(self) -> None:
        """Test downloading tabular data using pyarrow or pandas when the table is already downloaded."""
        get_object_response = load_test_data("get_object.json")
        object_id = UUID(int=2)
        with (
            self.transport.set_http_response(status_code=200, content=json.dumps(get_object_response)),
            mock.patch("evo.objects.utils.tables.KnownTableFormat") as mock_known_table_format,
            mock.patch("evo.common.io.download.HTTPSource", autospec=True) as mock_source,
        ):
            mock_table_info = {}
            mock_table_info["data"] = mock_data_id = "0000000000000000000000000000000000000000000000000000000000000001"
            mock_known_table_format.load_table = mock_load_table = mock.Mock()
            expected_file = self.data_client.cache_location / mock_data_id

            async def _mock_download_file_side_effect(*args, **kwargs):
                expected_filename = self.data_client.cache_location / mock_data_id
                expected_download_url = get_object_response["links"]["data"][1]["download_url"]
                actual_download_url = await kwargs["url_generator"]()
                self.assertEqual(expected_filename, kwargs["filename"])
                self.assertEqual(expected_download_url, actual_download_url)
                self.assertIs(self.transport, kwargs["transport"])
                self.assertIs(NoFeedback, kwargs["fb"])

            mock_source.download_file.side_effect = _mock_download_file_side_effect

            expected_file.touch()
            actual_table = await self.data_client.download_table(object_id, None, mock_table_info)

        mock_source.download_file.assert_not_called()
        self.transport.assert_no_requests()
        mock_load_table.assert_called_once_with(mock_table_info, self.data_client.cache_location)
        self.assertIs(mock_load_table.return_value, actual_table)

        # Otherwise this will interfere with the other "already_download" test, since cache cleanup in TestWithStorage
        # is in class setup, not individual test setup.
        expected_file.unlink()

    async def test_download_dataframe_already_downloaded(self) -> None:
        """Test downloading tabular data using pandas when the table is already downloaded."""
        get_object_response = load_test_data("get_object.json")
        object_id = UUID(int=2)
        with (
            self.transport.set_http_response(status_code=200, content=json.dumps(get_object_response)),
            mock.patch("evo.objects.utils.tables.KnownTableFormat") as mock_known_table_format,
            mock.patch("evo.common.io.download.HTTPSource", autospec=True) as mock_source,
        ):
            mock_table_info = {}
            mock_table_info["data"] = mock_data_id = "0000000000000000000000000000000000000000000000000000000000000001"
            mock_known_table_format.load_table = mock_load_table = mock.Mock()
            expected_file = self.data_client.cache_location / mock_data_id

            async def _mock_download_file_side_effect(*args, **kwargs):
                expected_filename = self.data_client.cache_location / mock_data_id
                expected_download_url = get_object_response["links"]["data"][1]["download_url"]
                actual_download_url = await kwargs["url_generator"]()
                self.assertEqual(expected_filename, kwargs["filename"])
                self.assertEqual(expected_download_url, actual_download_url)
                self.assertIs(self.transport, kwargs["transport"])
                self.assertIs(NoFeedback, kwargs["fb"])

            mock_source.download_file.side_effect = _mock_download_file_side_effect

            expected_file.touch()
            _actual_dataframe = await self.data_client.download_dataframe(object_id, None, mock_table_info)

        mock_source.download_file.assert_not_called()
        self.transport.assert_no_requests()
        mock_load_table.assert_called_once_with(mock_table_info, self.data_client.cache_location)

        # Otherwise this will interfere with the other "already_download" test, since cache cleanup in TestWithStorage
        # is in class setup, not individual test setup.
        expected_file.unlink()
