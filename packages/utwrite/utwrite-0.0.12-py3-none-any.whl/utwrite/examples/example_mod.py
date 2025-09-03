r"""

Example module to auto generate unittests from docstring

:Unittest decorator:
@unittest.skipUnless(sys.version_info.major == 3, "Lets say it requires Python3 only")
"""


def default_func():
    r"""

    Examples::

        import utwrite.examples.example_mod as ex
        ex.default_func()
        # Result: 1 #
    """
    return 1


def list_func():
    r"""

    Examples::

        import utwrite.examples.example_mod as ex
        ex.list_func()
        # Result: [1,2,3] #
    """
    return [1, 2, 3]


def almost_equal_func():
    r"""

    Examples::

        import utwrite.examples.example_mod as ex

        # python 3 ...
        ex.almost_equal_func()
        # Result: [0.5] @self.assertListAlmostEqual#
    """
    return [1 / 2]


def __dunder_func():
    r"""This should not generate unittest.

    Examples::

        import utwrite.examples.example_mod as ex
        ex.__dunder_func()
        # Result: None #
    """
    return


def __dunder_test_tag_func():
    r"""This should generate unittest.

    :Tags:
        test

    Examples::

        import utwrite.examples.example_mod as ex
        getattr(ex, '__dunder_test_tag_func')()
        # Result: None #
    """
    return


def notest_tag_func():
    r"""This should not generate unittest.

    :Tags:
        notest

    Examples::

        import utwrite.examples.example_mod as ex
        ex.notest_tag_func()
        # Result: None #
    """
    return


def missing_test_crash_func():
    r"""Funcion with no examples section (bad).

    By default functions without an example section are tagged with
    @MISSINGTEST, which means it will raise an error.

    This is so the developer dont't forget to create unittest, or tag as
    `notest`.
    """


def np_explicit_assert_func(n):
    r"""External assertion

    Examples::

        HAS_NUMPY = False
        try:
            import numpy as np
            HAS_NUMPY = True
        except:
            pass
        import utwrite.examples.example_mod as ex

        if HAS_NUMPY:
            ex.np_explicit_assert_func(3)
            # Result: np.array([0, 1, 2]) @np.testing.assert_array_equal#
        else:
            ex.np_explicit_assert_func(3)
            # Result: True #
    """
    try:
        import numpy as np

        return np.arange(n)
    except:
        # no numpy
        return True


def escaped_assertion_token_func():
    r"""Escaped assertion token

    Examples::

        import utwrite.examples.example_mod as ex
        ex.escaped_assertion_token_func()
        # Result: '\@' #
    """
    return '@'


def raise_error():
    r"""Example on how to use exception RES_KEY.

    Examples::

        from utwrite.examples import example_mod
        example_mod.raise_error()
        # ZeroDivisionError: division by zero #
    """
    return 2 / 0
