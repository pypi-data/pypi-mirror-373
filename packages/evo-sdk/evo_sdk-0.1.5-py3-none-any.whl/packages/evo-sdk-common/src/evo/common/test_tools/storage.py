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

import inspect
import shutil
import unittest
from pathlib import Path

from ..data import Environment
from ..utils import Cache
from .consts import BASE_URL, ORG, WORKSPACE_ID


class TestWithStorage(unittest.TestCase):
    CACHE_DIR: Path

    @classmethod
    def setUpClass(cls) -> None:
        cache_dir = Path(inspect.getfile(cls)).parent.resolve() / f".{cls.__name__.lower()}_cache"

        def _cleanup_cache() -> None:
            """Fail-safe cleanup of the cache directory."""
            shutil.rmtree(cache_dir, ignore_errors=True)

        cls.addClassCleanup(_cleanup_cache)
        cache_dir.mkdir(parents=True, exist_ok=True)

        # Write gitignore file in case cleanup fails.
        gitignore_file = cache_dir / ".gitignore"
        gitignore_file.write_text("*\n", encoding="utf-8")

        cls.CACHE_DIR = cache_dir

    def setUp(self) -> None:
        self.cache = Cache(self.CACHE_DIR)
        self.environment = Environment(hub_url=BASE_URL, org_id=ORG.id, workspace_id=WORKSPACE_ID)
