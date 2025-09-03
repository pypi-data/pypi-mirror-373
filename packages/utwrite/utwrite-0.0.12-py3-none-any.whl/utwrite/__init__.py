r"""

Info
----
This module is responsible for command line execution to create unittest from
docstrings.

Usage
-----
First pip install, then run
```sh
utw gen <python_file_to_generate_unittest_from_docstrings>
```

And call a runner with
```sh
utw run <python_file_to_generate_unittest_from_docstrings>
```

"""

__author__ = 'pb'


def main() -> None:
    import sys

    sys.tracebacklimit = 0

    sub_commands = ['gen', 'run']
    sub_command = ''

    if len(sys.argv) > 1:
        if sys.argv[1] in sub_commands:
            sub_command = sys.argv[1]

    if not sub_command:
        raise RuntimeError(
            'Sub command required, please use one of `utw %s`' % sub_commands
        )

    if sub_command == 'gen':
        from . import auto_generate_test

        auto_generate_test.main()
    if sub_command == 'run':
        from . import executor

        executor.main()
