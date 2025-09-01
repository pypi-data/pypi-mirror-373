"""
EOAP CWLWrap (c) 2025

EOAP CWLWrap is licensed under
Creative Commons Attribution-ShareAlike 4.0 International.

You should have received a copy of the license along with this work.
If not, see <https://creativecommons.org/licenses/by-sa/4.0/>.
"""

import os
from tests.helpers import TestCWL

class TestPattern12(TestCWL):

    def setUp(self):
        super().setUp()
        self.entrypoint = "pattern-12"

    def tearDown(self):
        super().tearDown()

    def test_pattern_wrapped_cwl(self):
        self._wrapped_cwl_validation()
