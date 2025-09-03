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

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Iterator, Sequence
from pathlib import Path
from uuid import UUID

from evo import logging
from evo.common import APIConnector, Environment, ICache, IFeedback, ITransport
from evo.common.io import Download, Upload
from evo.common.io.exceptions import DataExistsError, DataNotFoundError, RenewalError
from evo.common.utils import NoFeedback, Retry

from .data import ObjectMetadata
from .endpoints import DataApi, ObjectsApi
from .endpoints.models import DataUploadRequestBody, DataUploadResponseBody

__all__ = [
    "ObjectDataDownload",
    "ObjectDataUpload",
]

logger = logging.getLogger("object.data")

_CACHE_SCOPE = "geoscience-object"
_MAX_UPLOAD_URLS = 32


class ObjectDataUpload(Upload):
    """Context for uploading data to the Geoscience Object Service."""

    def __init__(
        self, connector: APIConnector, environment: Environment, name: str, initial_url: str | None = None
    ) -> None:
        """
        :param connector: The API connector to use.
        :param environment: The environment to upload the data to.
        :param name: The name of the data to be uploaded.
        :param initial_url: An initial URL to use for the upload.
        """
        self._api = DataApi(connector)
        self._environment = environment
        self._name = name
        self._mutex = asyncio.Lock()
        self._initial_url = initial_url

    @property
    def name(self) -> str:
        """The name of the data to be uploaded."""
        return self._name

    @property
    def label(self) -> str:
        return self._name

    @property
    def environment(self) -> Environment:
        """The environment that the data will be uploaded to."""
        return self._environment

    async def get_upload_url(self) -> str:
        # Use the initial URL.
        async with self._mutex:
            if (url := self._initial_url) is not None:
                # Clear the initial URL so it can't be reused.
                self._initial_url = None
                return url

        # Get a new upload URL.
        logger.debug(f"Requesting upload URL for {self.label}")
        match await self._api.put_data_in_workspace(
            org_id=str(self.environment.org_id),
            workspace_id=str(self.environment.workspace_id),
            data_upload_request_body=[DataUploadRequestBody(name=self._name)],
        ):
            case [DataUploadResponseBody(upload_url=url)] if isinstance(url, str):
                return url
            case [DataUploadResponseBody(exists=exists)] if exists is True:
                raise DataExistsError(
                    "Named data already exists in the workspace:\n"
                    f"data_name: {self._name}\n"
                    f"workspace_id: {self.environment.workspace_id}"
                )
            case _:
                raise RenewalError("Failed to get an upload url")

    async def upload_from_cache(
        self,
        cache: ICache,
        transport: ITransport,
        max_workers: int | None = None,
        retry: Retry | None = None,
        fb: IFeedback = NoFeedback,
    ) -> None:
        target = cache.get_location(environment=self.environment, scope=_CACHE_SCOPE) / self.name
        await self.upload_from_path(filename=target, transport=transport, max_workers=max_workers, retry=retry, fb=fb)

    @staticmethod
    async def _create_multiple(
        connector: APIConnector, environment: Environment, names: Sequence[str | UUID]
    ) -> AsyncIterator[ObjectDataUpload]:
        """Internal method to create multiple data upload contexts.

        Object data that already exists in the workspace will be skipped.

        :param connector: The API connector to use.
        :param environment: The environment to upload the data to.
        :param names: The names of the data to be uploaded.

        :return: An asynchronous iterator of data upload contexts.
        """
        api = DataApi(connector)
        # Up to _MAX_UPLOAD_URLS upload URLs can be generated in a single API request. We can accommodate any number of
        # data names by batching them in groups of _MAX_UPLOAD_URLS.
        for start in range(0, len(names), _MAX_UPLOAD_URLS):
            end = min(start + _MAX_UPLOAD_URLS, len(names))
            logger.debug(f"Requesting {end - start} upload URL{'' if end - start == 1 else 's'}")
            response = await api.put_data_in_workspace(
                org_id=str(environment.org_id),
                workspace_id=str(environment.workspace_id),
                data_upload_request_body=[DataUploadRequestBody(name=str(name)) for name in names[start:end]],
            )
            for ref in response:
                if ref.exists:
                    logger.debug(f"Skipping upload of existing data: {ref.name}")
                    continue
                yield ObjectDataUpload(
                    connector=connector,
                    environment=environment,
                    name=ref.name,
                    initial_url=ref.upload_url,
                )


class ObjectDataDownload(Download[ObjectMetadata]):
    """Context for downloading data from the Geoscience Object Service."""

    def __init__(
        self, connector: APIConnector, metadata: ObjectMetadata, name: str, initial_url: str | None = None
    ) -> None:
        self._api = ObjectsApi(connector)
        self._metadata = metadata
        self._name = name
        self._mutex = asyncio.Lock()
        self._initial_url = initial_url

    @property
    def name(self) -> str:
        """The name of the data to be uploaded."""
        return self._name

    @property
    def label(self) -> str:
        return f"{self.metadata.path} (ref={self.name})"

    @property
    def metadata(self) -> ObjectMetadata:
        return self._metadata

    def _get_cache_location(self, cache: ICache) -> Path:
        return cache.get_location(environment=self.metadata.environment, scope=_CACHE_SCOPE) / self._name

    async def get_download_url(self) -> str:
        # Use the initial URL.
        async with self._mutex:
            if (url := self._initial_url) is not None:
                # Clear the initial URL so it can't be reused.
                self._initial_url = None
                return url

        # Get a new download URL.
        logger.debug(f"Requesting download URL for {self.label}")
        response = await self._api.get_object_by_id(
            org_id=str(self.metadata.environment.org_id),
            workspace_id=str(self.metadata.environment.workspace_id),
            object_id=str(self.metadata.id),
            version=self.metadata.version_id,
        )
        for data_ref in response.links.data:
            data_key = getattr(data_ref, "name", data_ref.id)
            if data_key != self._name:
                continue
            elif isinstance(url := data_ref.download_url, str):
                return url
            else:
                raise RenewalError(f"Failed to get a data download url for {self.label}")
        raise DataNotFoundError(f"Unable to find the requested data: {self.label}")

    @staticmethod
    def _create_multiple(
        connector: APIConnector, metadata: ObjectMetadata, urls_by_name: dict[str, str]
    ) -> Iterator[ObjectDataDownload]:
        """Internal method to create multiple data download contexts.

        :param connector: The API connector to use.
        :param metadata: The metadata of the object to download data from.
        :param urls_by_name: A mapping of data names to download URLs.

        :return: An asynchronous iterator of data download contexts.
        """
        for name, url in urls_by_name.items():
            yield ObjectDataDownload(
                connector=connector,
                metadata=metadata,
                name=name,
                initial_url=url,
            )
