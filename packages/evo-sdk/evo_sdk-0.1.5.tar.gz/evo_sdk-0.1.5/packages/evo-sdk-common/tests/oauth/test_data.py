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

from parameterized import parameterized

from evo.oauth import OAuthScopes

EXPECTED_SCOPE_NAMES = {
    OAuthScopes.offline_access: "offline_access",
    OAuthScopes.evo_discovery: "evo.discovery",
    OAuthScopes.evo_workspace: "evo.workspace",
    OAuthScopes.evo_blocksync: "evo.blocksync",
    OAuthScopes.evo_object: "evo.object",
    OAuthScopes.evo_file: "evo.file",
    OAuthScopes.evo_audit: "evo.audit",
}


class TestOAuthScopes(unittest.TestCase):
    @parameterized.expand(
        [
            (OAuthScopes.offline_access,),
            (OAuthScopes.evo_discovery,),
            (OAuthScopes.evo_workspace,),
            (OAuthScopes.evo_blocksync,),
            (OAuthScopes.evo_object,),
            (OAuthScopes.evo_file,),
            (OAuthScopes.evo_audit,),
        ],
        name_func=lambda func,
        index,
        params: f"{func.__name__}_{index}_{parameterized.to_safe_name(str(params[0][0]))}",
    )
    def test_single_scope_string(self, scope: OAuthScopes) -> None:
        self.assertIn(scope, EXPECTED_SCOPE_NAMES)
        expected_string = EXPECTED_SCOPE_NAMES[scope]
        self.assertEqual(expected_string, str(scope))
        self.assertEqual(1, len(scope), "Expected a single scope")

    @classmethod
    def expand_scopes(cls, scopes: tuple[OAuthScopes, ...]) -> list[OAuthScopes]:
        """Expand a tuple of scopes into a list of individual scopes."""
        all_scopes = set()
        for scope in scopes:
            if len(scope) == 1:
                all_scopes.add(scope)
            else:
                for member in OAuthScopes:
                    if member in scope and len(member) == 1:
                        all_scopes.add(member)

        return sorted(all_scopes, key=lambda s: s.value)

    @parameterized.expand(
        [
            (
                OAuthScopes.default,
                (
                    OAuthScopes.evo_discovery,
                    OAuthScopes.evo_workspace,
                ),
            ),
            (
                OAuthScopes.all_evo,
                (
                    OAuthScopes.default,
                    OAuthScopes.evo_blocksync,
                    OAuthScopes.evo_object,
                    OAuthScopes.evo_file,
                ),
            ),
        ],
        name_func=lambda f, n, p: f"{f.__name__}_{n}_{parameterized.to_safe_name(p[0][0].name)}",
    )
    def test_multiple_scope_string(self, scopes: OAuthScopes, expected_scopes: tuple[OAuthScopes, ...]) -> None:
        expected_string = " ".join([EXPECTED_SCOPE_NAMES[scope] for scope in self.expand_scopes(expected_scopes)])
        self.assertEqual(expected_string, str(scopes))

        for scope in expected_scopes:
            self.assertIn(scope, scopes)

        self.assertEqual(len(self.expand_scopes(expected_scopes)), len(scopes))
