r"""unittest_cases.py

Library for handy unittest custom / inherited types, and decorators.
"""

import unittest
from functools import wraps


class BaseTestCase(unittest.TestCase):
    r"""
    :Tags:
        notest, already-tested
    """

    def assertListAlmostEqual(
        self, first, second, places=5, msg=None, delta=None
    ) -> None:
        """Asserts that a list of floating point values is almost equal.

        unittest has assertAlmostEqual and assertListEqual but no assertListAlmostEqual.

        Args:
            - first (`types`): First list to check.
            - second (`types`): Second list to check against.
            - places (`uint`): Default 5. Precision to compare `first` with `second`.
            - msg (`str`): Default None. Message to pass into
              `TestCase.assertEqual` method.
            - delta (`float`): Default None. Acceptable delta differente, passed
              to `TestCase.assertAlmostEqual`

        Returns:
            `None`

        :Tags:
            notest
        """
        self.assertEqual(len(first), len(second), msg)
        for a, b in zip(first, second):
            self.assertAlmostEqual(a, b, places, msg, delta)


def MISSINGTEST(func) -> callable:
    r"""Decorator for functions without a test case.

    Args:
        - func (`func`): Function to be decorated

    Returns:
        `func`: Decorated function.

    :Tags:
        notest, decorator.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        r"""

        :Tags:
            notest, wrapper
        """
        raise RuntimeError('MISSING EXAMPLE TEST!')

    return wrapper


class MayaTestCase(BaseTestCase):
    r"""Base test case for Maya

    :Tags:
        notest

    """

    MAYA_INITIALIZED = False
    try:
        from maya import cmds

        if hasattr(cmds, 'optionVar'):
            MAYA_INITIALIZED = True
    except:
        pass

    if MAYA_INITIALIZED:
        cmds.optionVar(sv=('colorManagementPolicyFileName', ''))
