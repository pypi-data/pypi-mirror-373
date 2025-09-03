r"""collector.py

Responsible for:
----------------

- Gathering unittests
"""

import sys
import os
import unittest
from . import utilities


def get_tests(*tests, test_suite=None) -> unittest.TestSuite:
    r"""Get available tests

    Args:
        - *tests `str`: Path to test files or directories
        - test_suite `unittest.TestSuite`: Default None. Suite to add tests to.

    Returns:
        `unittest.TestSuite`: Suite with added tests

    Examples::

        from utwrite import collector
        from utwrite import utilities
        import os

        tst_dir = utilities.get_test_dir(__file__)
        if os.path.isdir(tst_dir):
            suite = collector.get_tests(tst_dir)
            suite.countTestCases() > 1
            # Result: True #

    """
    if not (test_suite or tests):
        raise RuntimeError(
            'Failed to find tests.' + ' Pass a <TestSuite> sute, directories or tests'
        )

    if test_suite is None:
        test_suite = unittest.TestSuite()

    # added_paths = {}
    test_mods = []
    test_paths = []
    for t in tests:
        if os.path.isdir(t):
            test_paths.append(t)
        else:
            test_mods.append(t)

    loader = unittest.TestLoader()
    # suite = unittest.TestSuite()
    # - Add directories
    for p in test_paths:
        top_dir = os.path.dirname(p)
        try:
            d = loader.discover(p)
        except:
            d = loader.discover(
                p, top_level_dir=top_dir
            )  # this auto adds top_dir to PATH env
        if d.countTestCases():
            test_suite.addTests(d)

    # - Add files
    for f in test_mods:
        tst_file = utilities.clean_file_path(f)
        tst_dir = os.path.dirname(tst_file)
        tst = os.path.splitext(os.path.basename(tst_file))[0]
        sys.path.insert(0, tst_dir)
        # utilities.set_env('PATH', tst_dir)
        d = loader.loadTestsFromName(tst)
        if d.countTestCases():
            test_suite.addTest(d)

    return test_suite
