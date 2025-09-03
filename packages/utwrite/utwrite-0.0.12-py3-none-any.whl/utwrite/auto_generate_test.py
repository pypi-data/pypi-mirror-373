r"""auto_generate_test.py

Functions to parse a python file, extract test cases and create unittest file.

"""

import subprocess
import traceback
import argparse
import os
import ast
import re
from . import headers
from . import utilities

RES_KEYS = {'result': {'name': 'Result', 'raises': ''}}

ASSERT_TOKEN = '@'
IGNORE_TAG = 'notest'
TEST_TAG = 'test'
# NOTE: Functions with "hidden" tag will not generate test

# - Add general Python errors
PY_ERR = [k for k in __builtins__.keys() if 'error' in k.lower()]
RES_KEYS.update({e.lower(): {'name': e, 'raises': e} for e in PY_ERR})


def make_test_res_data(module_path) -> dict:
    r"""Parse contents from module_path into test/assert blocks

    Args:
        - module_path `str`: Path to module .py file. For debugging you can also
          pass the contents of a function.

    Returns:
        `dict`: Dictionary of functions and test/assert tuples
            {<func_name>: [
                (<test_section>, (<result_key>, <result_value>)),
                ...
                ]}

    Examples::

        from utwrite import auto_generate_test as agt

        d = agt.make_test_res_data(agt.TST_FUNC)
        d ['my_func']
        # Result: [('\nmy_func(2)', ('Result', '3 ')), ('\nmy_func(0)',
        # ('Result', '1 ')), ('\nmy_func(4)', ('Result', '5 \@self.assertAlmostEqual '))] #

    """
    if os.path.isfile(module_path):
        with open(module_path, 'r') as f:
            code = ast.parse(f.read())
    else:
        code = ast.parse(module_path)

    # - Get `Examples::` section from docstring
    func_doc_data = {}
    tag_re = r'\s*:Tags:\n\s*(.*)'
    tag_re = re.compile(tag_re)
    for node in ast.walk(code):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            doc = ast.get_docstring(node)
            tag_result = tag_re.search(doc) if doc else None
            func_name = node.name

            # hidden dunder functions are ignored by default
            if func_name.startswith('__'):
                if tag_result and TEST_TAG in tag_result.groups()[0]:
                    # run the code to create unittest
                    pass
                else:
                    # skip the function
                    continue

            if not doc:
                # give empty string to the function to be later decorated as
                # `unittest.skip`
                func_doc_data[func_name] = ''
                continue

            # - Check if docstring has example section
            if tag_result and IGNORE_TAG in tag_result.groups()[0].lower():
                continue

            if 'Examples::' not in doc:
                func_doc_data[func_name] = ''
                continue

            # - Get example section
            ex = doc.split('Examples::')[-1]
            # capture result comment line
            # if not any('#%s:'%r in ex.lower().replace(' ','') for r in RES_KEYS):
            if not _check_in_res_keys(ex):
                func_doc_data[func_name] = ''
                continue

            # add full example test block as value to the dictionary
            if func_name in func_doc_data:
                func_name = utilities.number_increase(func_name)

            func_doc_data[func_name] = ex

    # - Break docstring examples in tests and results.
    return _break_docstrings_in_tests_and_results(func_doc_data)


def _check_in_res_keys(st) -> bool:
    r"""Check if any result key in given string.

    For a valid check it's required the line to start with "#" and have ":"
    after the result key word.

    Args:
        - st `str`: String to check for result key (`RES_KEYS`)

    Returns:
        `bool`: True if result key in `st`, False otherwise

    Examples::

        from utwrite import auto_generate_test as agt

        agt._check_in_res_keys('# Result:')
        # Result: True #

        agt._check_in_res_keys('#RESULT:')
        # Result: True #
        agt._check_in_res_keys('#result:')
        # Result: True #
        agt._check_in_res_keys('#   result   :')
        # Result: True #

        agt._check_in_res_keys('result')
        # Result: False #

        agt._check_in_res_keys('Result')
        # Result: False #
        agt._check_in_res_keys('#Result')
        # Result: False #
        agt._check_in_res_keys('# Result')
        # Result: False #
    """
    resRe = r'^\s*#\s*(\w+)\s*:'
    resRe = re.compile(resRe)
    st = st.split('\n')
    for s in st:
        g = resRe.match(s)
        if g:
            k = g.groups()[0]
            if k.lower().replace(' ', '') in RES_KEYS:
                return True
    return False


def _break_docstrings_in_tests_and_results(func_doc_data) -> dict:
    r"""Split docstring section in function + test + assert.

    Args:
        - func_doc_data `dict`: Function documentation as {<func_name>:<example_section>}

    Returns:
        `dict`: Dictionary with tests and asserts broken in tuples, i.e.
            {<func_name>:[(<test_code>, (<assertion_type>, <assertion_value>))]}

    Examples::

        from utwrite import auto_generate_test as agt

        func_doc_data = {'my_func': '\n\n    my_func(2)\n    # Result: 3 #\n\n    my_func(0)\n    # Result: 1 #\n\n'}
        agt._break_docstrings_in_tests_and_results(func_doc_data)

        # Result: {'my_func': [('\nmy_func(2)', ('Result', '3 ')), ('\nmy_func(0)', ('Result', '1 '))]} #
    """

    mod_test_data = {}
    res_key_re = r'#\s*(.*):'
    regex = re.compile(res_key_re)
    for func, doc in func_doc_data.items():
        if not doc:
            mod_test_data[func] = []
            continue

        tst, result, test_result_tuples = [], [], []
        result_found = False

        for s in doc.split('\n'):
            # check if current line is a result line.
            if _check_in_res_keys(s):
                if not regex.search(s).groups()[0].startswith('#'):
                    result_found = True

            if result_found:
                result.append(s)
                # - Result block ends when the line ends with "#"
                if s.endswith('#'):
                    # section ended, reset vars
                    test_result_tuples.append((tst, result))
                    tst, result = [], []
                    result_found = False

            else:
                # code test line
                if s:
                    # check for comment line
                    if not re.match(r'\s*#', s):
                        tst.append(s)

            # - Capture trailing lines
            # those are not tests, but could hold sections to cleanup the
            # tests before it.
            if s == doc.split('\n')[-1]:
                if ''.join(tst).replace('\n', '') == '':
                    continue  # just blank lines, we are done
                test_result_tuples.append((tst, result))
                continue

        # - Parse test and result tuples
        flat_result = utilities.flatten_list(test_result_tuples)
        # get docstring indentation size
        tab_size = min([utilities.leading_whitespace(s) for s in flat_result if s])

        # variable to hold tests and results
        # formatted as [(<str>test, (<str>result_key, <str>result_value)), ...]
        tst_res = []
        for tst, res in test_result_tuples:
            # - Get test lines
            tst = [x[tab_size:] for x in tst]
            tst = '\n' + '\n'.join(tst)

            # no result
            if not res:
                tst_res.append((tst, ('', '')))
                continue

            # - Get result section
            # capture result key
            res_key = [
                k for k in RES_KEYS if k in ''.join(res).lower().replace(' ', '')
            ]
            res_key = RES_KEYS[res_key[0]]['name']
            # remove leading indentation from result
            res = [x[tab_size:] for x in res]
            # remove key info (only the first to avoid namespace hit)
            res = [re.sub(r'\w+:s*', '', x, count=1) if x == res[0] else x for x in res]
            # remove comments (leading and trailing)
            res = [re.sub(r'#\s*', '', x) for x in res]
            res = [re.sub(r'\s*#', '', x) for x in res]

            res = ''.join(res)
            tst_res.append((tst, (res_key, res)))

        # - Update the dictionary
        mod_test_data[func] = tst_res

    return mod_test_data


def make_test_body_from_test_result_data(mod_test_data) -> str:
    r"""Create test function(s) from test:result dictionary

    Args:
        - mod_test_data `dict`: Dictionary data with split test code and
          assertions (as returned by `_break_docstrings_in_tests_and_results`)

    Returns:
        `str`: Test body

    Examples::

        import utwrite.auto_generate_test as agt

        func_doc_data = {'my_func': '\n\n    my_func(2)\n    # Result: 3 #\n\n    my_func(0)\n    # Result: 1 #\n\n'}
        mod_test_data = agt._break_docstrings_in_tests_and_results(func_doc_data)
        body = agt.make_test_body_from_test_result_data(mod_test_data)
        body
        # Result: '\n    def test_my_func(self):\n\n        self.assertEqual(my_func(2),3 )\n\n        self.assertEqual(my_func(0),1 )\n' #

    """

    # - Build string with contents of unittest
    tst_str = ''
    for key, test_tuples in mod_test_data.items():
        tab_count = 1
        tab_size = 4
        spc = ' ' * tab_size
        func = '\n%sdef test_%s(self):\n' % (spc * tab_count, key)
        if not test_tuples:
            # Function does not have unittest. Tag as missing
            tst_str += '\n%s@MISSINGTEST' % (
                spc * tab_count
            )  # from unittest_cases imported as * from header
            tst_str += func
            tst_str += '\n%spass\n' % (spc * (tab_count + 1))
            continue

        tst_str += func
        for tst, res in test_tuples:
            try:
                last_tst = tst.rpartition('\n')[-1]
                tst = tst.replace('print ', '')  # remove prints
                last_tst = last_tst.replace('print ', '')
                parts = tst.rpartition(last_tst)
            except Exception as e:
                # - Failed to extract pieces
                msg = 'Failed to caputre test results\n'
                msg += f'key = {key}\n'
                msg += f'res = {res}\n'
                msg += f'test = {tst}\n'
                msg += str(e)
                raise RuntimeError(msg)

            res_type = res[0].lower()
            res_assert = ''
            if '\\%s' % ASSERT_TOKEN in res[1]:
                res_val = res[1].replace('\\%s' % ASSERT_TOKEN, ASSERT_TOKEN)
            else:
                res_val, _, res_assert = res[1].partition(ASSERT_TOKEN)
            res_indent = ' ' * utilities.leading_whitespace(res_val)
            res_part = parts[0] + res_indent
            lst = res_part + 'self.assertEqual(%s,%s)' % (last_tst, res_val)
            if not res_type:
                lst = parts[0] + last_tst

            # use assert method if givein in the docstring
            if res_assert:
                if '(' in res_assert:  # assert given as a full function call
                    try:
                        lst = res_part + res_assert % (last_tst, res_val)
                    except TypeError:
                        lst = res_part + res_assert.format(last_tst, res_val)
                else:
                    # result assert just as a method name
                    lst = res_part + '%s(%s,%s)' % (res_assert, last_tst, res_val)
            else:  # use default asserts
                try:
                    if isinstance(ast.literal_eval(res[1]), float):
                        lst = res_part + 'self.assertAlmostEqual(%s,%s)' % (
                            last_tst,
                            res[1],
                        )
                except:
                    pass
                # use defined in RES_KEYS
                if res_type in RES_KEYS:
                    raise_key = RES_KEYS[res_type]['raises']

                    # assertion raise using "with" method on last line
                    if raise_key:
                        lst = res_part + 'with self.assertRaises(%s): %s' % (
                            raise_key,
                            last_tst,
                        )

            # add indentations
            lst = lst.replace('\n', '\n' + spc * (tab_count + 1))
            # add end line
            if not lst.endswith('\n'):
                lst += '\n'

            # add test line to test string
            tst_str += lst

    return r'%s' % tst_str


def build_test_file(
    module_path,
    write=True,
    output='',
    header='default',
    test_case='BaseTestCase',
    verbose=True,
) -> str:
    r"""Auto generate test file.

    Args:
        - module_path `str`: Path of a python file wanted to create unittests
          from. For debugging you can also provide a string representation of
          the python module contents and check the output.
        - write `bool`: Default True. When False, or `module_path` given is not
          a real python file (i.e. String with function contents, see
          `TST_FUNC`), no file is written.
        - output `str`: Default ''. Finds the `tests` directory based on the
          `module_path`
        - header `str`: Default 'default', uses headers.HEADER['default']. The
          default header for the test file, either a rogue complete string
          header of a key in headers.HEADER dictionary. Expects to have
          everything required imported.
        - test_case `str`: Default 'BaseTestCase'. Test case function wanted to
          super class your tests with.
        - verbose `bool`: Default True, prints file writting messages.

    Returns:
        `str`: Module file test contents.

    Examples::

        from utwrite import utilities
        from utwrite import headers
        import utwrite.auto_generate_test as agt
        import os, tempfile, shutil

        temp_dir = os.path.join(tempfile.gettempdir(), 'utwrite_agt_unittest_DELETE')
        if os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir)

        git_dir = os.path.join(temp_dir, '.git')
        os.makedirs(git_dir)
        f = os.path.join(temp_dir, 'd1', 'd2', 'ut_file.py')

        utilities.ensure_path_to_file(f)

        with open(f, 'w') as m:
            m.write(agt.TST_FUNC)

        test_contents = agt.build_test_file(f, verbose=False)
        tst_file = os.path.join(temp_dir, 'tests', 'd1','d2','test_ut_file_auto.py')
        with open(tst_file ,'r') as t:
            file_contents = t.read()
        str(file_contents) == str(test_contents)
        # Result: True #

        test_body = agt.make_test_body_from_test_result_data(agt.make_test_res_data(f))
        expected_contents = headers.HEADER['default'] + test_body
        expected_contents = expected_contents % ('', 'ut_file', 'BaseTestCase')

        file_contents == expected_contents
        # Result: True #

        # Delete temp dir
        if os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir)
        os.path.isdir(temp_dir)
        # Result: False #
    """
    if header in headers.HEADER.keys():
        header = headers.HEADER[header]

    # - Get module name
    if not os.path.isfile(module_path):
        module_name = 'UNNAMED'
        from_file = False
    else:
        module_name = os.path.basename(module_path).replace('.py', '')
        from_file = True

    if isinstance(test_case, type):
        test_case = test_case.__name__

    # - Generate test functions
    tst_res_data = make_test_res_data(module_path)
    tst_func_body = make_test_body_from_test_result_data(tst_res_data)
    if not tst_func_body:
        print('"%s": Empty test body, nothing to do.' % module_path)
        return ''

    # - Compose test file
    ut_deco = ''
    if from_file:
        ut_deco = get_module_unittest_deco(module_path)
    tst = header % (ut_deco, module_name, test_case) + tst_func_body

    if write and from_file:
        if not output:
            output = utilities.get_test_dir(module_path)
            output = os.path.join(output, 'test_%s_auto.py' % module_name)

        utilities.write_to_file(tst, output, verbose=verbose)
        return tst
    return tst


def build(*modules, **kwargs) -> None:
    r"""Build unittest for given params.

    Args:
        - modules `str`: Modules to generate unittests from. If param is a
          directory, get all python files in there (excluding `__init__.py`)
        - kwargs `dict`: Params accepted by `build_test_file`:

            - write `bool`: Default True. When False, or `module_path` given is
             not a real python file (i.e. String with function contents, see `TST_FUNC`), no file is written.
            - output `str`: Default ''. Finds the `tests` directory based on the `module_path`
            - header `str`: Default headers.HEADER['default']. The default
              header for the test file. Expects to have everything required
            imported.
            - test_case `str`: Default 'BaseTestCase'. Test case function wanted to
              super class your tests with.
            - verbose `bool`: Default True, prints file writting messages.

    Returns:
        `None`

    Examples::

        from utwrite import utilities
        import utwrite.auto_generate_test as agt
        import os, tempfile, shutil

        temp_dir = os.path.join(tempfile.gettempdir(), 'utwrite_agt_unittest_DELETE')
        if os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir)

        git_dir = os.path.join(temp_dir, '.git')
        os.makedirs(git_dir)
        f = os.path.join(temp_dir, 'd1', 'd2', 'ut_file.py')

        utilities.ensure_path_to_file(f)

        with open(f, 'w') as m:
            m.write(agt.TST_FUNC)

        agt.build(f, verbose=False)
        tst_file = os.path.join(temp_dir, 'tests', 'd1','d2','test_ut_file_auto.py')
        with open(tst_file ,'r') as t:
            file_contents = t.read()

        test_data = agt.make_test_res_data(f)
        test_body = agt.make_test_body_from_test_result_data(test_data)

        test_body in file_contents
        # Result: True #

        # Delete temp dir
        if os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir)
        os.path.isdir(temp_dir)
        # Result: False #
    """
    pmodules = []
    for m in modules:
        if os.path.isfile(m):
            pmodules.append(m)
        elif os.path.isdir(m):
            pmodules.extend(
                utilities.get_files_from_dir(m, ext=['.py'], ignore=['__init__.py'])
            )
        else:
            print('"%s": Could not find file, skipping...' % m)
    for module in pmodules:
        build_test_file(module, **kwargs)


def get_module_unittest_deco(module_path, token=':Unittest decorator:') -> str:
    r"""Get module level unittest decorator.

    Args:
        - module_path `str`: Python module file to get unittest decorator from.
        - token `str`: Default ":Unittest decorator:". Token used after which
          expects to find module level unittest decorator

    Returns:
        `str`: Contents of module level decorators.

    Examples::

        import utwrite.auto_generate_test as agt

        mod_docs = '\"\"\"'
        mod_docs += '\nSome module\n\n'
        mod_docs += ':Unittest decorator:\n'
        mod_docs += "@unittest.skipunless(1==2, 'Some reason')\n"
        mod_docs += '\"\"\"'

        agt.get_module_unittest_deco(mod_docs)
        # Result: "\n\@unittest.skipunless(1==2, 'Some reason')" #

    """
    if os.path.isfile(module_path):
        with open(module_path, 'r') as f:
            code = ast.parse(f.read())
    else:
        code = ast.parse(module_path)
    mod_deco = ''
    for node in ast.walk(code):
        if isinstance(node, ast.Module):
            doc = ast.get_docstring(node)
            if not doc:
                continue
            _, _, t = doc.partition(token)
            for d in t.split('\n'):
                if d.startswith('@'):
                    mod_deco += '\n%s' % d

            return mod_deco
    return ''


def _parse_args() -> dict:
    r"""Capture command line arguments

    Flags:
        -h --header: Unittest header template (default 'default')

    Returns:
        `dict`: Flags values, i.e.:
            {
                'header': pargs.header,
            }

    :Tags:
        notest, cli

    Examples::

        # - Running from a shell calling python, to capture args
        $ python -c 'from utwrite import auto_generate_test as agt; print(agt._parse_args())'
        # {'modules': [], 'header': 'default'}

        # - And giving params
        $ python -c 'from utwrite import auto_generate_test as agt; print(agt._parse_args())' --header 'maya'
        # {'modules': [], 'header': 'maya'}
    """

    parser = argparse.ArgumentParser(prog='utw gen', description='Generate unittests')
    parser.add_argument('cmd', nargs='?')  # since called from command line as utw [run]
    parser.add_argument('modules', nargs='*')

    parser.add_argument(
        '--header',
        help='Unittest header template (default False).',
        type=str,
        default='default',
    )

    try:
        pargs = parser.parse_args()
        return {
            'modules': pargs.modules,
            'header': pargs.header,
        }

    except:
        # called main directly (no CLI)
        return {
            'modules': [],
            'header': 'default',
        }


def main(*modules, **kwargs) -> int:
    r"""Capture command line arguments and call generator.

    Args:
        - *modules `list(str)`: Module files to write.
        - **kwargs `dict`: Unpacked into `build()`
            - write `bool`: Default True. When False, or `module_path` given is
             not a real python file (i.e. String with function contents, see
             `TST_FUNC`), no file is written.
            - output `str`: Default ''. Finds the `tests` directory based on the
              `module_path`
            - header `str`: Default headers.HEADER['default']. The default
              header for the test file. Expects to have everything required
              imported.
            - test_case `str`: Default 'BaseTestCase'. Test case function wanted
              to super class your tests with.
            - verbose `bool`: Default True, prints file writting messages.

    Returns:
        `int`: Error code. 0 if successful, 1 otherwise.

    Examples::

        from utwrite import utilities
        import utwrite.auto_generate_test as agt
        import os, tempfile, shutil

        temp_dir = os.path.join(tempfile.gettempdir(), 'utwrite_agt_unittest_DELETE')
        if os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir)

        git_dir = os.path.join(temp_dir, '.git')
        os.makedirs(git_dir)
        f = os.path.join(temp_dir, 'd1', 'd2', 'ut_file.py')

        utilities.ensure_path_to_file(f)

        with open(f, 'w') as m:
            m.write(agt.TST_FUNC)

        agt.main(f, verbose=False)
        tst_file = os.path.join(temp_dir, 'tests', 'd1','d2','test_ut_file_auto.py')
        with open(tst_file ,'r') as t:
            file_contents = t.read()

        test_data = agt.make_test_res_data(f)
        test_body = agt.make_test_body_from_test_result_data(test_data)

        test_body in file_contents
        # Result: True #

        # Delete temp dir
        if os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir)
        os.path.isdir(temp_dir)
        # Result: False #

    """
    # - Capture args and tests
    args = _parse_args()
    args.update(kwargs)
    modules = list(modules) + list(args.pop('modules'))

    cmd = [
        'python',
        '-c',
        'from utwrite import auto_generate_test; auto_generate_test.build(*%s, **%s)'
        % (modules, args),
    ]

    # call command
    return subprocess.check_call(cmd)


if __name__ == '__main__':
    r"""
    Run as
    `python utwrite/auto_generate_test.py utwrite/examples/examples_mod.py`
    """
    try:
        main()

    except Exception as e:
        print('Failed generate tests: %s\n%s', e, traceback.format_exc())
        exit(1)

TST_FUNC = r'''
def my_func(v):
    r"""

    Examples::

        my_func(2)
        # Result: 3 #

        my_func(0)
        # Result: 1 #

        my_func(4)
        # Result: 5 @self.assertAlmostEqual #
    """
    return v+1

def another_func(n):
    r"""

    Examples::

        import numpy as np

        another_func(3)
        # Result:  array([0, 1, 2]) @np.testing.assert_array_equal#
    """

    return np.arange(n)
'''
