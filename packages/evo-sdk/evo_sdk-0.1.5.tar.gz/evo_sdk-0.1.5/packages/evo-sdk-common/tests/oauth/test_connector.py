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
from typing import Literal

from parameterized import parameterized

from evo.aio import AioTransport
from evo.oauth import OAuthConnector


class TestOAuthConnector(unittest.TestCase):
    @parameterized.expand(
        [
            ("authorize", "/connect/authorize"),
            ("token", "/connect/token"),
        ],
    )
    def test_endpoint(self, endpoint_type: Literal["authorize", "token"], expected: str) -> None:
        transport = AioTransport(user_agent="test")
        connector = OAuthConnector(transport, client_id="test")
        assert connector.endpoint(endpoint_type) == expected
