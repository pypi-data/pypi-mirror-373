# utwrite

# Info

Auto[magically] write Python unittest files from docstrings.

# Demo
[Demo](./demo.cast)


# Why not `doctest` ?
[doctest](https://docs.python.org/3/library/doctest.html) is great, built-in, if
it works for you use it. The main differences are:

- Write out `.py` test file
- Create `tests` directory structure from the project root (contains `.git`
  folder), and mirror directory hierarchy of the source file.
- Support custom header for your unittest file.
- Support custom assertion (i.e. `numpy.testing`) via the assertion token `@`.
- Support custom `TestCase` super class, that can host relevant methods, i.e.
  `BaseTestCase.assertListAlmostEqual`.
- No `eval` call.
  
`utwrite` is not an unittest executor. It creates the `.py` unittest files to be
called with one (i.e. `python -m unittest`, `pytest` ). Though it can call an
executor on its behalf (`untitest`, `pytest`, `maya`).


# Installation
## From pypi
Run `pip install utwrite` on your Python environment of choice.

## From source

Clone the repo, and run
```sh
make install
```

This will `pip` install the package and make it available both for CLI and Python
interpreter.


# Usage

Call the `utw` on the file(s) and/or directory(ies) you want to auto generate
unittest from the docstrings.

## `utw` provides 2 sub commands
### utw gen
Generate unittest via `utw gen`.

```sh
utw gen <my_python_file>
```

I.E.

``` sh
utw gen utwrite/examples/example_mod.py
```

### utw run
Execute tests with `utw run` (but also with `python -m unittest` or `pytest`)

- `utw run`
  ```sh
  utw run <tests>
  ```
  
  By default `utw run` uses Python's *unittest* module, you can choose the
  executor via the `-app` flag 
  
  ```sh
  utw run <tests> -app pytest
  ```
  
  It's also possible to run your unittests inside Autodesk Maya headless with
  `-app maya` (if you have it installed).
  

- Python default:
You can also run the generated tests with `unittest` module

``` sh
python -m unittest discover .
```


Or with `pytest` if you have it installed

``` sh
pytest
```

### Executing the `example_mod.py`
By default example_mod.py has one test section expected to fail, and the
execution result is expected as:

> $ python -m unittest tests/utwrite/examples/test_example_mod_auto.py
> .....E..
> ======================================================================
> ERROR: test_missing_test_crash_func (tests.utwrite.examples.test_example_mod_auto.Test_example_mod_AUTO)
> ----------------------------------------------------------------------
> Traceback (most recent call last):
>   File "D:\home\dev\personal\utwrite\utwrite\unittest_cases.py", line 58, in wrapper
>     raise RuntimeError('MISSING EXAMPLE TEST!')
> RuntimeError: MISSING EXAMPLE TEST!
> 
> ----------------------------------------------------------------------
> Ran 8 tests in 0.148s
> 
> FAILED (errors=1)

# Auto-Generation

To make meaningful unittests automatically this module expects docstrings
formatted with some particularities. Also it works well with Sphinx Python
auto-documentation generator (through ReST and google styled docstrings).


## How Does it Work ?

For unittest to be auto-generated it needs 2 lines. The first line defines the
execution that will return the value to be tested. The second line will assert
the line above with the result given.


## Examples Section

Auto generated unittests are only concerned with the **Examples** section of your
docstring. That section is ReST formatted, in order to generate proper
documentation (through auto generators like Sphinx), and extrapolated to make
test cases. By definition the section must be exactly as:

``` python
r"""
Examples::

    <code_section>
    <more_code>
    ...
"""

```

Such that:

- `Examples::` Must be used to start the example code block.
- Followed by an empty line.
- Code inside must have 1 indentation from the `Examples::` point.


## Result Keys

Tests are made through **Result Keys** (`RES_KEYS`). At this moment the result
keys are:

- All Python's errors (`ValueError`, `RuntimeError`, ...);
- `Result`

> Whenever wanted to create a test section (assertion) it is necessary to have a
> **Result Key** present. No **Result Key** no test.


## Result Section

A **Result Section** is defined by a section of text that starts with
"# <result_key>: "; and ends with "#". I.E.

``` python
r"""
1+1
# Result: 2 #
"""
```

## Tags

Functions can be tagged to explicitly be ignored or be found through the **Tags**
section. The available **Tags** are:

- `test` Use this function to generate unittests.
- `notest` Ignore this function from auto unittest generation.

The **Tags** section by definition must be as follows:

``` python
r"""
:Tags:
    test
"""
```

Such that:

- `:Tags:` Must be used to start the **Tags** block.
- Tag values must be indented from `:Tags:` position.
- Tag values should be separated with &ldquo;, &rdquo; (ie &ldquo;specific, notest&rdquo;)


## Assertion Tokens

By default tests will use either `self.assertEqual` or `with self.assertRaises`
to generate unittest assert test case. Such that:

- `self.assertAlmostEqual` Used for default values;
- `with self.assertRaises` Used for any **Error** (`RES_KEYS` with `'raises'`
    value).

For any other case you might want to pass your assertion function explicitly.
That is done by using the `ASSERT_TOKEN` &ldquo;@&rdquo; inside a result block, as follows:

``` python
r"""
<execution_line_to_produce_value(s)_to_assert>
# Result: <expected_result_from_line_above> @<asserting_function> #
"""
```


I.E.

``` python
r"""
Examples::

    ...
    import numpy as np
    np.arange(5)
    # Result: np.array([0, 1, 2, 3, 4, 5]) @np.testing.assert_almost_equal#
"""

```


> ***Important***:
> If you have the assertion token in your result section, but is not part
> of the assert function i.e.

``` python
def func(): return '@'

```
The test case requires it to be escaped "\@"
i.e.

``` python
r"""
func()
# Result: '\@' #
"""

```

## Dunders

Functions/Classes that start with double underscore will by default not generate
any unittest.


# Full Example

View [example_mod.py](./utwrite/examples/example_mod.py)

The result test should be created inside
[test_example_mod_auto.py](./tests/utwrite/examples/test_example_mod_auto.py) with
the contents:

```python

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
```
