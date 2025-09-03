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

from ._types import DataFrame, Table
from .data import ObjectDataClient

__all__ = [
    "DataFrame",
    "ObjectDataClient",
    "Table",
]

try:
    import pyarrow  # noqa: F401
except ImportError:
    pass  # Omit the following imports if pyarrow is not installed.
else:
    from .table_formats import all_known_formats, get_known_format
    from .tables import ArrowTableFormat, BaseTableFormat, KnownTableFormat

    __all__ += [
        "ArrowTableFormat",
        "BaseTableFormat",
        "KnownTableFormat",
        "all_known_formats",
        "get_known_format",
    ]
