r"""executor.py

Responsible for:
----------------

- Calling execution of unittests
- Supports the executors:
  - unittest
  - pytest
  - maya (Autodesk Maya via mayapy,exe)

"""

import uuid
import os
import tempfile
import shutil
import subprocess
import traceback
import argparse
import unittest
from utwrite import collector
from utwrite import utilities


def run_unittest(*tests, **kwargs) -> int:
    r"""Run given tests with `unittest` executor.

    Args:
        - *tests `str`: Tests to run
        - **kwargs:
            - verbosity `bool`: Default 1. Verbosity value flag
            - test_suite `TestSuite`: Default None.

    Returns:
        `int`: 0 if successful, 1 otherwise

    Examples::

        from utwrite import executor
        from utwrite import utilities

        # Test using collector
        import os
        collector_test = os.path.join(os.path.dirname(__file__), 'test_collector_auto.py')
        if os.path.isfile(collector_test):
            r =executor.run_unittest(collector_test)
            r == 0
            # Result: True #

    """
    verbosity = kwargs.get('verbosity', 1)
    test_suite = kwargs.get('test_suite', None)
    suite = collector.get_tests(*tests, test_suite=test_suite)
    runner = unittest.TextTestRunner(verbosity=verbosity)
    r = runner.run(suite)
    return int(not bool(r.wasSuccessful()))


def run_pytest(*tests, **kwargs) -> int:
    r"""Run given tests with `pytest` executor.

    Args:
        - *tests `str`: Tests to run
        - **kwargs: Passed to `pytest.main()`


    Returns:
        `int`: 0 if successful, 1 otherwise

    Examples::

        from utwrite import executor
        from utwrite import utilities
        try:
            import pytest

            # Test using collector
            import os
            collector_test = os.path.join(os.path.dirname(__file__), 'test_collector_auto.py')
            if os.path.isfile(collector_test):
                r =executor.run_pytest(collector_test)
                r == r.OK
                # Result: True #
        except:
            pass
    """
    try:
        import pytest
    except:
        raise RuntimeError(
            'Pytest not installed. Install it first (i.e. `pip install pytest`)'
        )
    return pytest.main(list(tests))


def run_maya(*tests, **kwargs) -> int:
    r"""Run given *tests with mayapy.

    Args:
        - *tests `str`: Tests to run
        - **kwargs:
            - verbosity `bool`: Default 1. Verbosity value flag
            - test_suite `TestSuite`: Default None.
            - cli `bool`: Default False. When True run in a separated shell.
            - interactive `bool`: Default False. When True and `cli` keep the
              mayapy shell active
            - maya_version `int`, `str`: Default 'latest', get latest installed.
              Maya version to use.
            - app_dir `str`: Default '', create an empty directory in temp dir.
              MAYA_APP_DIR to use.

    Returns:
        `int`: 0 if successful, 1 otherwise

    :Tags:
        notest, software-required

    Examples::

        from utwrite import utilities
        from utwrite import executor
        if utilities.maya_installation_dir():
            import os
            collector_test = os.path.join(os.path.dirname(__file__), 'test_collector_auto.py')
            if os.path.isfile(collector_test):
                r = executor.run_maya(collector_test, cli=True)
                r
                # Result: 0 #

    """
    cli = kwargs.get('cli', False)
    interactive = kwargs.get('interactive', False)

    # add utwrite root to PATH
    utilities.add_to_env('PATH', os.path.dirname(os.path.dirname(__file__)))

    if cli:
        # Create dummy clean MAYA_APP_DIR
        tempDir = tempfile.gettempdir()
        app_dir = kwargs.get('app_dir', '')
        app_dir = os.path.join(tempDir, 'maya_app_dir%s' % (str(uuid.uuid4())))
        if not os.path.isdir(app_dir):
            os.makedirs(app_dir)
        os.environ['MAYA_APP_DIR'] = app_dir
        # create command
        maya_version = kwargs.get('maya_version', 'latest')
        cmd = [utilities.mayapy(version=maya_version)]
        if interactive:
            cmd.append('-i')
        cmd.append('-c')
        cmdStr = 'from maya import cmds, standalone; standalone.initialize();'
        cmdStr += (
            f'from utwrite import executor; executor.run_unittest(*{tests}, **{kwargs})'
        )
        cmd.append(cmdStr)
        # print(f'cmd={cmd}')
        try:
            print('\n> Launching Maya (%s)....' % cmd[0])
            return subprocess.check_call(cmd)
        finally:
            if os.path.isdir(app_dir):
                shutil.rmtree(app_dir)

    else:
        r = run_unittest(*tests, **kwargs)
        exit(r)


def _parse_args() -> dict:
    r"""Capture command line arguments

    Flags:
        -t --tests: Tests to run (files and/or directories)
        -app: Unittest application runner (unittest*, pytest, maya)
        -i --interactive: If `-app` is "maya" and this flag given, keep the
         initialized session open.
        -vb --verboity: Verbosity level for unittest (default 1)
        --maya-version: Maya version to use (default 'latest')

    Returns:
        `dict`: Flags values, i.e.:
            {
                'tests': pargs.tests,
                'app': pargs.app,
                'interactive': pargs.interactive,
                'verbosity': pargs.verbosity,
                'maya_version': pargs.maya_version
            }

    :Tags:
        notest, cli

    Examples::

        # - Running from a shell calling python, to capture args
        $ python -c 'from utwrite import executor; print(executor._parse_args())'
        # {'tests': '', 'app': 'unittest', 'interactive': False, 'verbosity': 1, 'maya_version': 'latest'}

        # - And giving params
        $ python -c 'from utwrite import executor; print(executor._parse_args())' -app pytest -v 3
        # {'tests': '', 'app': 'pytest', 'interactive': False, 'verbosity': 3, 'maya_version': 'latest'}
    """

    parser = argparse.ArgumentParser(prog='utw run', description='Run unittests')
    parser.add_argument('cmd', nargs='?')  # since called from command line as utw [run]
    parser.add_argument('tests', nargs='*')

    parser.add_argument(
        '-app',
        help='Unittest application runner (unittest*, pytest, maya)',
        default='unittest',
    )

    parser.add_argument(
        '-i',
        '--interactive',
        help='Keep headless Maya interactive (default False).',
        action=argparse.BooleanOptionalAction,
        type=bool,
        default=False,
    )

    parser.add_argument(
        '-vb',
        '--verbosity',
        help='Unittest verbosity level (default 1).',
        type=int,
        default=1,
    )

    parser.add_argument(
        '--maya-version', help='Maya version to use.', type=str, default='latest'
    )

    try:
        pargs = parser.parse_args()
        return {
            'tests': pargs.tests,
            'app': pargs.app,
            'interactive': pargs.interactive,
            'verbosity': pargs.verbosity,
            'maya_version': pargs.maya_version,
        }

    except:
        # called main directly (no CLI)
        return {
            'tests': [],
            'app': 'unittest',
            'interactive': False,
            'verbosity': 1,
            'maya_version': 'latest',
        }


def main(*tests, **kwargs) -> int:
    r"""Capture command line arguments and call appropriate runner.

    Returns:
        `int`: Error code. 0 if successful, 1 otherwise.

    Examples::

        # From a Python interpreter
        from utwrite import executor
        # Test using collector
        import os
        collector_test = os.path.join(os.path.dirname(__file__), 'test_collector_auto.py')
        if os.path.isfile(collector_test):
            r = executor.main(collector_test)
            r
            # Result: 0 #

    """
    # - Capture args and tests
    args = _parse_args()
    tests = list(tests) + list(args.pop('tests'))
    if not tests:
        return 1

    cmd = ['python', '-c']
    # - Capture application to run unittests
    app = args.pop('app')
    apps = ['maya', 'unittest', 'pytest']
    args.update(kwargs)
    if app not in apps:
        raise RuntimeError(
            '"%s": Given app not supported. Acceptable: %s' % (app, apps)
        )

    if app == 'maya':
        cmd += [
            'from utwrite import executor; executor.run_%s(*%s, cli=True, **%s)'
            % (app, tests, args)
        ]
    else:
        cmd += [
            'from utwrite import executor; executor.run_%s(*%s, **%s)'
            % (app, tests, args)
        ]

    if args['verbosity'] > 2:
        print(f'cmd = {cmd}')

    # call command
    return subprocess.check_call(cmd)


if __name__ == '__main__':
    r"""
    Run as
    `python utwrite/executor.py -t tests/utwrite/`
    """
    try:
        main()

    except Exception as e:
        print('Failed running tests: %s\n%s', e, traceback.format_exc())
        exit(1)
