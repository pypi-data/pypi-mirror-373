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

from evo.files.io import _INVALID_NAMES, _make_name_safe


class TestMakeNameSafe(unittest.TestCase):
    def test_invalid_characters(self):
        self.assertEqual(_make_name_safe("test<name>"), "test%3Cname%3E")
        self.assertEqual(_make_name_safe("test:name"), "test%3Aname")
        self.assertEqual(_make_name_safe("test/name"), "test%2Fname")
        self.assertEqual(_make_name_safe("test\\name"), "test%5Cname")
        self.assertEqual(_make_name_safe("test|name"), "test%7Cname")
        self.assertEqual(_make_name_safe("test?name"), "test%3Fname")
        self.assertEqual(_make_name_safe("test*name"), "test%2Aname")

    def test_invalid_trailing_characters(self):
        self.assertEqual(_make_name_safe("test "), "test%20")
        self.assertEqual(_make_name_safe("test."), "test%2E")

    def test_reserved_names(self):
        for name in _INVALID_NAMES:
            self.assertEqual(_make_name_safe(name), name + "_")
            self.assertEqual(_make_name_safe(name + ".txt"), name + "_.txt")

    def test_valid_names(self):
        self.assertEqual(_make_name_safe("test"), "test")
        self.assertEqual(_make_name_safe("test123"), "test123")
        self.assertEqual(_make_name_safe("test_name"), "test_name")

    def test_leading_trailing_special_characters(self):
        self.assertEqual(_make_name_safe("<test>"), "%3Ctest%3E")

    def test_leading_trailing_reserved_names(self):
        self.assertEqual(_make_name_safe("CONtestCON"), "CONtestCON")

    def test_mixed_valid_invalid_characters(self):
        self.assertEqual(_make_name_safe("te<st>na:me"), "te%3Cst%3Ena%3Ame")

    def test_empty_string(self):
        self.assertEqual(_make_name_safe(""), "")

    def test_only_special_characters(self):
        self.assertEqual(_make_name_safe('<>:"/\\|?*'), "%3C%3E%3A%22%2F%5C%7C%3F%2A")
