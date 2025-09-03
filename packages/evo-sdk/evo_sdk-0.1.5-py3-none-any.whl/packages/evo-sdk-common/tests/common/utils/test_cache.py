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

import shutil
from pathlib import Path
from uuid import uuid5

from evo.common.exceptions import StorageFileExistsError, StorageFileNotFoundError
from evo.common.test_tools import TestWithStorage
from evo.common.utils import Cache


class TestCache(TestWithStorage):
    def test_init_with_path(self) -> None:
        """Test setting the cache location with a Path object."""
        new_location = self.CACHE_DIR / "some subdir"
        shutil.rmtree(new_location, ignore_errors=True)
        self.assertFalse(new_location.exists(), "The cache directory should not exist.")

        manager = Cache(new_location, mkdir=True)
        self.assertTrue(new_location.is_dir(), "The cache directory should exist.")
        self.assertEqual(
            new_location,
            manager.get_location(self.environment, "some scope").parent,
            "The cache location should be set correctly.",
        )

    def test_init_with_str(self) -> None:
        """Test setting the cache location with a string."""
        new_location = self.CACHE_DIR / "some other subdir"
        shutil.rmtree(new_location, ignore_errors=True)
        self.assertFalse(new_location.exists(), "The cache directory should not exist.")

        manager = Cache(str(new_location), mkdir=True)
        self.assertTrue(new_location.is_dir(), "The cache directory should exist.")
        self.assertEqual(
            new_location,
            manager.get_location(self.environment, "some other scope").parent,
            "The cache location should be set correctly.",
        )

    def test_init_with_other_types_raise_typeerror(self) -> None:
        """Test setting the cache location with a string."""
        for invalid in (1, 1.0, b"some bytes", False, object(), dict(), list(), tuple(), set()):
            with self.subTest(invalid=invalid):
                with self.assertRaises(TypeError):
                    Cache(invalid)  # type: ignore

    def test_init_with_nonexistent(self) -> None:
        """Test setting the cache location to a non-existent directory when mkdir=False should raise an error."""
        new_location = self.CACHE_DIR / "nonexistent"
        shutil.rmtree(new_location, ignore_errors=True)
        self.assertFalse(new_location.exists(), "The cache directory should not exist.")

        with self.assertRaises(StorageFileNotFoundError):
            Cache(new_location)

    def test_init_with_file_exists(self) -> None:
        """Test setting the cache location to an existing file should raise an error."""
        new_location = self.CACHE_DIR / "some file"
        new_location.touch()
        self.assertTrue(new_location.is_file(), "The cache directory should be a file.")

        with self.assertRaises(StorageFileExistsError):
            Cache(new_location)

    def test_root(self) -> None:
        """Test getting the cache root."""
        self.assertEqual(self.CACHE_DIR, self.cache.root)

    def test_get_cache(self) -> None:
        """Test getting the cache directory for a given scope."""
        scope = "some random scope"
        expected_cache_name = str(uuid5(self.environment.workspace_id, scope))
        cache_dir = self.cache.get_location(self.environment, scope)
        self.assertIsInstance(cache_dir, Path, "The cache directory should be a Path object.")
        self.assertTrue(cache_dir.is_dir(), "The cache directory should exist.")
        self.assertEqual(expected_cache_name, cache_dir.name, "The cache directory should be named correctly.")
        self.assertEqual(self.CACHE_DIR, cache_dir.parent, "The cache directory should be in the correct location.")

    def test_clear_scoped_cache(self) -> None:
        """Test clearing the cache for a given scope."""
        scope = "some other scope"
        scope_2 = "another some other scope"
        cache_dir = self.cache.get_location(self.environment, scope)
        cache_dir_2 = self.cache.get_location(self.environment, scope_2)
        self.assertTrue(cache_dir.is_dir(), "The cache directory should exist.")
        self.assertTrue(cache_dir_2.is_dir(), "The cache directory should exist.")

        some_file = cache_dir / "some_file.txt"
        some_file.touch()
        self.assertTrue(some_file.exists(), "The file should exist.")

        self.cache.clear_cache(self.environment, scope)

        self.assertFalse(cache_dir.exists(), "The cache directory should be removed.")
        self.assertFalse(some_file.exists(), "The file should be removed.")
        self.assertTrue(self.CACHE_DIR.is_dir(), "The root cache should still exist.")
        self.assertTrue(cache_dir_2.is_dir(), "The other cache directory should still exist.")

    def test_clear_root_cache(self) -> None:
        """Test clearing the entire cache."""
        scope = "some other scope"
        cache_dir = self.cache.get_location(self.environment, scope)
        self.assertTrue(cache_dir.is_dir(), "The cache directory should exist.")

        some_file = cache_dir / "some_file.txt"
        some_file.touch()
        self.assertTrue(some_file.exists(), "The file should exist.")

        self.cache.clear_cache()

        self.assertFalse(cache_dir.exists(), "The cache directory should be removed.")
        self.assertFalse(some_file.exists(), "The file should be removed.")
        self.assertTrue(self.CACHE_DIR.is_dir(), "The root cache should still exist.")
        self.assertEqual(0, len(list(self.CACHE_DIR.iterdir())), "The cache should be empty.")

    def test_clear_cache_no_scope_raises_valueerror(self) -> None:
        """Test clearing the cache without specifying a scope should raise an error."""
        with self.assertRaises(ValueError):
            self.cache.clear_cache(environment=self.environment)

    def test_clear_cache_no_environment_raises_valueerror(self) -> None:
        """Test clearing the cache without specifying an environment should raise an error."""
        with self.assertRaises(ValueError):
            self.cache.clear_cache(scope="some scope")

    def test_temporary_cache(self) -> None:
        """Test creating a temporary cache."""
        with self.cache.temporary_location() as temp_cache:
            self.assertTrue(temp_cache.is_dir(), "The temporary cache directory should exist.")
            self.assertEqual(self.cache.root, temp_cache.parent, "The temporary cache should be in the root.")

        self.assertFalse(
            temp_cache.exists(), "The temporary cache directory should be removed after exiting the context."
        )
        self.assertTrue(self.CACHE_DIR.is_dir(), "The root cache should still exist.")
