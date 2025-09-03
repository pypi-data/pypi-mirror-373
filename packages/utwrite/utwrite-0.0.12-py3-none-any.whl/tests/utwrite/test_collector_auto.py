
import sys
import os
import unittest
from utwrite.unittest_cases import *


class Test_collector_AUTO(BaseTestCase):

    def test_get_tests(self):

        from utwrite import collector
        from utwrite import utilities
        import os
        tst_dir = utilities.get_test_dir(__file__)
        if os.path.isdir(tst_dir):
            suite = collector.get_tests(tst_dir)
            self.assertEqual(    suite.countTestCases() > 1,    True )
