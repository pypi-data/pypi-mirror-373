
import sys
import os
import unittest
from utwrite.unittest_cases import *


class Test_executor_AUTO(BaseTestCase):

    def test_run_unittest(self):

        from utwrite import executor
        from utwrite import utilities
        import os
        collector_test = os.path.join(os.path.dirname(__file__), 'test_collector_auto.py')
        if os.path.isfile(collector_test):
            r =executor.run_unittest(collector_test)
            self.assertEqual(    r == 0,    True )

    def test_run_pytest(self):

        from utwrite import executor
        from utwrite import utilities
        try:
            import pytest
            import os
            collector_test = os.path.join(os.path.dirname(__file__), 'test_collector_auto.py')
            if os.path.isfile(collector_test):
                r =executor.run_pytest(collector_test)
                self.assertEqual(        r == r.OK,        True )

        except:
            pass

    def test_main(self):

        from utwrite import executor
        import os
        collector_test = os.path.join(os.path.dirname(__file__), 'test_collector_auto.py')
        if os.path.isfile(collector_test):
            r = executor.main(collector_test)
            self.assertEqual(    r,    0 )
