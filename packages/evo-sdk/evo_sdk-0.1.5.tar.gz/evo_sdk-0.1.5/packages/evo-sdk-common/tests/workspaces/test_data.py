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
from datetime import datetime, timezone
from uuid import UUID

from parameterized import parameterized

from evo.common import Environment
from evo.workspaces import ServiceUser, UserPermission, Workspace, WorkspaceRole
from evo.workspaces.endpoints.models import RoleEnum, UserModel
from evo.workspaces.exceptions import UserPermissionTypeError


class TestWorkspaceRoles(unittest.TestCase):
    """Test cases for the workspace roles and permissions enums."""

    @parameterized.expand(
        [
            (UserPermission.read, UserPermission.write),
            (UserPermission.read, UserPermission.manage),
            (UserPermission.write, UserPermission.manage),
        ]
    )
    def test_user_permissions_unique(self, left: UserPermission, right: UserPermission) -> None:
        """Test that user permissions enums are unique."""
        self.assertNotEqual(left.value, right.value)
        masked = left & right
        self.assertEqual(masked, UserPermission(0))

    @parameterized.expand(
        [
            ("Viewer can read", WorkspaceRole.viewer, UserPermission.read),
            ("Editor can read", WorkspaceRole.editor, UserPermission.read),
            ("Editor can write", WorkspaceRole.editor, UserPermission.write),
            ("Editor is viewer", WorkspaceRole.editor, WorkspaceRole.viewer),
            ("Owner can read", WorkspaceRole.owner, UserPermission.read),
            ("Owner can write", WorkspaceRole.owner, UserPermission.write),
            ("Owner can manage", WorkspaceRole.owner, UserPermission.manage),
            ("Owner is viewer", WorkspaceRole.owner, WorkspaceRole.viewer),
            ("Owner is editor", WorkspaceRole.owner, WorkspaceRole.editor),
        ]
    )
    def test_workspace_role_permissions_include(
        self, _label: str, role: WorkspaceRole, permission: UserPermission | WorkspaceRole
    ) -> None:
        """Test that workspace roles contain the correct permissions."""
        self.assertIn(permission, role)

    @parameterized.expand(
        [
            ("Viewer cannot write", WorkspaceRole.viewer, UserPermission.write),
            ("Viewer cannot manage", WorkspaceRole.viewer, UserPermission.manage),
            ("Viewer is not an editor", WorkspaceRole.viewer, WorkspaceRole.editor),
            ("Viewer is not an owner", WorkspaceRole.viewer, WorkspaceRole.owner),
            ("Editor cannot manage", WorkspaceRole.editor, UserPermission.manage),
            ("Editor is not an owner", WorkspaceRole.editor, WorkspaceRole.owner),
        ]
    )
    def test_workspace_role_permissions_exclude(
        self, _label: str, role: WorkspaceRole, permission: UserPermission | WorkspaceRole
    ) -> None:
        """Test that workspace roles do not contain the incorrect permissions."""
        self.assertNotIn(permission, role)

    def test_user_permission_type_error(self) -> None:
        """Test that a user permission type error is raised when an invalid permission is used."""
        with self.assertRaises(UserPermissionTypeError):
            assert RoleEnum.viewer in WorkspaceRole.viewer

    @parameterized.expand(
        [
            ("Viewer is a viewer", RoleEnum.viewer, WorkspaceRole.viewer),
            ("Editor is an editor", RoleEnum.editor, WorkspaceRole.editor),
            ("Owner is an owner", RoleEnum.owner, WorkspaceRole.owner),
        ]
    )
    def test_endpoint_role_conversion(
        self, _label: str, endpoint_role: RoleEnum, workspace_role: WorkspaceRole
    ) -> None:
        """Test that the endpoint role enum can be converted to the workspace role enum."""
        interpreted_role = WorkspaceRole[str(endpoint_role.value)]
        self.assertEqual(workspace_role, interpreted_role)


class TestUser(unittest.TestCase):
    """Test cases for the service user dataclass."""

    def test_from_model(self) -> None:
        """Test that a service user can be created from a user model."""
        model = UserModel(id=UUID(int=0), name="Test User", email="test.user@unit.test")
        user = ServiceUser.from_model(model)
        self.assertEqual(model.id, user.id)
        self.assertEqual(model.name, user.name)
        self.assertEqual(model.email, user.email)

    def test_from_model_no_name(self) -> None:
        """Test that a service user can be created from a user model with no name."""
        model = UserModel(id=UUID(int=0), name=None, email="test.user@unit.test")
        user = ServiceUser.from_model(model)
        self.assertEqual(model.id, user.id)
        self.assertIsNone(user.name)
        self.assertEqual(model.email, user.email)

    def test_from_model_no_email(self) -> None:
        """Test that a service user can be created from a user model with no email."""
        model = UserModel(id=UUID(int=0), name="Test User", email=None)
        user = ServiceUser.from_model(model)
        self.assertEqual(model.id, user.id)
        self.assertEqual(model.name, user.name)
        self.assertIsNone(user.email)

    def test_from_model_no_name_or_email(self) -> None:
        """Test that a service user can be created from a user model with no name or email."""
        model = UserModel(id=UUID(int=0), name=None, email=None)
        user = ServiceUser.from_model(model)
        self.assertEqual(model.id, user.id)
        self.assertIsNone(user.name)
        self.assertIsNone(user.email)


class TestWorkspace(unittest.TestCase):
    """Test cases for the workspace dataclass."""

    def setUp(self) -> None:
        self.org_id = UUID(int=0)
        self.workspace_id = UUID(int=1)
        self.user_id = UUID(int=2)
        self.user = ServiceUser(id=self.user_id, name="Test User", email="test.user@unit.test")

    def get_workspace(self, role: WorkspaceRole = WorkspaceRole.owner) -> Workspace:
        return Workspace(
            id=self.workspace_id,
            display_name="Test Workspace",
            description="A test workspace",
            user_role=role,
            org_id=self.org_id,
            hub_url="https://unit.test/",
            created_at=datetime.fromtimestamp(0, tz=timezone.utc),
            created_by=self.user,
            updated_at=datetime.fromtimestamp(0, tz=timezone.utc),
            updated_by=self.user,
        )

    @parameterized.expand(
        [
            ("Viewer can read", WorkspaceRole.viewer, UserPermission.read),
            ("Editor can read", WorkspaceRole.editor, UserPermission.read),
            ("Editor can write", WorkspaceRole.editor, UserPermission.write),
            ("Editor is viewer", WorkspaceRole.editor, WorkspaceRole.viewer),
            ("Owner can read", WorkspaceRole.owner, UserPermission.read),
            ("Owner can write", WorkspaceRole.owner, UserPermission.write),
            ("Owner can manage", WorkspaceRole.owner, UserPermission.manage),
            ("Owner is viewer", WorkspaceRole.owner, WorkspaceRole.viewer),
            ("Owner is editor", WorkspaceRole.owner, WorkspaceRole.editor),
        ]
    )
    def test_user_has_permission(
        self, _label: str, role: WorkspaceRole, permission: UserPermission | WorkspaceRole
    ) -> None:
        """Test that the user has the correct permissions in the workspace."""
        workspace = self.get_workspace(role)
        self.assertTrue(workspace.user_has_permission(permission))

    def test_get_environment(self) -> None:
        """Test that the workspace can generate an environment object."""
        workspace = self.get_workspace()
        environment = workspace.get_environment()
        self.assertIsInstance(environment, Environment)
        self.assertEqual(self.org_id, environment.org_id)

    def test_hash(self) -> None:
        """Test that the workspace can be hashed."""
        workspace = self.get_workspace()
        self.assertEqual(hash(workspace.id), hash(workspace))
