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

__all__ = [
    "FileMetadata",
    "FileVersion",
]

from dataclasses import dataclass
from datetime import datetime

from evo.common import ResourceMetadata, ServiceUser


@dataclass(frozen=True, kw_only=True)
class FileMetadata(ResourceMetadata):
    """Metadata about a file in the File API."""

    parent: str
    """The parent path of the file."""

    version_id: str
    """An arbitrary identifier for the file version."""

    size: int
    """The size of the file in bytes."""

    modified_at: datetime
    """The resource's last modified timestamp."""

    modified_by: ServiceUser | None = None
    """The user who last modified the resource."""

    @property
    def path(self) -> str:
        """The full path of the file, formed by joining the parent and name, separated by a slash ('/')."""
        return f"{self.parent.removesuffix('/')}/{self.name.removeprefix('/')}"

    @property
    def url(self) -> str:
        """The URL of the file in the File API."""
        return (
            "{hub_url}/file/v2/orgs/{org_id}/workspaces/{workspace_id}/files/{file_id}?version_id={version_id}".format(
                hub_url=self.environment.hub_url.rstrip("/"),
                org_id=self.environment.org_id,
                workspace_id=self.environment.workspace_id,
                file_id=self.id,
                version_id=self.version_id,
            )
        )


@dataclass(frozen=True, kw_only=True)
class FileVersion:
    """Represents a version of a file."""

    version_id: str
    """An arbitrary identifier for the file version."""

    created_at: datetime
    """The date and time when the file version was created."""

    created_by: ServiceUser | None
    """The user who uploaded the file version."""
