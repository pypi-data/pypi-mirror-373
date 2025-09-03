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

from datetime import datetime, timedelta, timezone
from enum import Flag, auto
from typing import Literal, Optional

from pydantic import BaseModel, Field

__all__ = [
    "AccessToken",
    "OAuthScopes",
]

_ALLOWABLE_CLOCK_DRIFT = timedelta(minutes=5)


def _utcnow() -> datetime:
    """Get the current UTC time.

    :return: The current UTC time.
    """
    return datetime.now(timezone.utc)


class OAuthScopes(Flag):
    """Public OAuth scopes for authenticating against Evo APIs.

    https://developer.seequent.com/docs/guides/getting-started/apps-and-tokens#about-evo-access-tokens
    """

    offline_access = auto()

    # Evo Scopes
    evo_discovery = auto()
    """Required for access to the Evo Discovery API, both discovery and token endpoints."""

    evo_workspace = auto()
    """Required for access to the Workspaces API."""

    evo_audit = auto()
    """Required for access to the Audit API."""

    evo_blocksync = auto()
    """Required for access to the BlockSync API."""

    evo_object = auto()
    """Required for access to the Geoscience Object API."""

    evo_file = auto()
    """Required for access to the File API."""

    # Useful combinations
    """Default scopes for Evo applications.

    Extra scopes to be added as needed include `evo_blocksync`, `evo_object`, or `evo_file`, etc.
    """
    default = evo_discovery | evo_workspace

    """All scopes for Evo applications."""
    all_evo = default | evo_blocksync | evo_object | evo_file

    def __str__(self) -> str:
        """Format a space-separated list of scopes for the OAuth request."""
        scopes = sorted([scope for scope in self.__class__ if scope in self and len(scope) == 1], key=lambda s: s.value)
        return " ".join([scopes_map[scope] for scope in scopes])

    def __len__(self) -> int:
        """Count the number of unique scopes that are set."""
        return len([scope for scope in self.__class__ if scope in self and (scope.value & (scope.value - 1)) == 0])


scopes_map = {
    OAuthScopes.offline_access: "offline_access",
    OAuthScopes.evo_discovery: "evo.discovery",
    OAuthScopes.evo_workspace: "evo.workspace",
    OAuthScopes.evo_blocksync: "evo.blocksync",
    OAuthScopes.evo_object: "evo.object",
    OAuthScopes.evo_file: "evo.file",
    OAuthScopes.evo_audit: "evo.audit",
}


class AccessToken(BaseModel):
    """An access token model, returned by the OAuth server.
    https://www.rfc-editor.org/rfc/rfc6749#section-5.1
    """

    token_type: Literal["Bearer"]

    access_token: str
    """The access token issued by the authorization server."""

    refresh_token: Optional[str] = None
    """The refresh token, which can be used to obtain new access tokens using the same authorization grant. Refresh tokens are only returned if you request the "offline access" scope."""

    expires_in: Optional[int] = None
    """The lifetime in seconds of the access token."""

    issued_at: datetime = Field(default_factory=_utcnow)
    """The time at which the token response was received."""

    @property
    def expires_at(self) -> datetime | None:
        """The time at which the token expires, or None if the token lifetime is unknown.

        A small margin of error may occur due to the time taken to process the token response.
        """
        if self.expires_in is None:
            return None
        return self.issued_at + timedelta(seconds=self.expires_in)

    @property
    def ttl(self) -> int | None:
        """The time-to-live (TTL) of this access token in seconds, or None if the token lifetime is unknown.

        If the token is expired, the TTL will be 0.
        """
        if self.expires_at is None:
            return None
        ttl = self.expires_at - _utcnow()
        return max(round(ttl.total_seconds()), 0)

    @property
    def is_expired(self) -> bool:
        """Whether this access token has expired.

        True if the access token has expired, False otherwise.
        If the token lifetime is unknown, this method will always return False.
        """
        if (expiry := self.expires_at) is not None:
            return _utcnow() > expiry
        else:
            return False
