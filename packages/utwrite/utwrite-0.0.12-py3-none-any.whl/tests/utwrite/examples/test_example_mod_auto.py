
import sys
import os
import unittest
from utwrite.unittest_cases import *


@unittest.skipUnless(sys.version_info.major == 3, "Lets say it requires Python3 only")
class Test_example_mod_AUTO(BaseTestCase):

    def test_default_func(self):

        import utwrite.examples.example_mod as ex
        self.assertEqual(ex.default_func(),1 )

    def test_list_func(self):

        import utwrite.examples.example_mod as ex
        self.assertEqual(ex.list_func(),[1,2,3] )

    def test_almost_equal_func(self):

        import utwrite.examples.example_mod as ex
        self.assertListAlmostEqual(ex.almost_equal_func(),[0.5] )

    def test___dunder_test_tag_func(self):

        import utwrite.examples.example_mod as ex
        self.assertEqual(getattr(ex, '__dunder_test_tag_func')(),None )

    @MISSINGTEST
    def test_missing_test_crash_func(self):

        pass

    def test_np_explicit_assert_func(self):

        HAS_NUMPY = False
        try:
            import numpy as np
            HAS_NUMPY = True
        except:
            pass
        import utwrite.examples.example_mod as ex
        if HAS_NUMPY:
            np.testing.assert_array_equal(    ex.np_explicit_assert_func(3),    np.array([0, 1, 2]) )

        else:
            self.assertEqual(    ex.np_explicit_assert_func(3),    True )

    def test_escaped_assertion_token_func(self):

        import utwrite.examples.example_mod as ex
        self.assertEqual(ex.escaped_assertion_token_func(),'@' )

    def test_raise_error(self):

        from utwrite.examples import example_mod
        with self.assertRaises(ZeroDivisionError): example_mod.raise_error()
