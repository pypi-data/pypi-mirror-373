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

import sys


class NoImport:
    """Simple context manager to prevent one or more named modules from being imported."""

    def __init__(self, *names: str) -> None:
        """
        :param names: The names of the modules to prevent from being imported.
        """
        self._names = names

    def __enter__(self) -> None:
        for name in self._names:
            # Set the module to None to prevent it from being imported.
            sys.modules[name] = None

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        for name in self._names:
            # Remove the module from sys.modules to clean up.
            del sys.modules[name]
