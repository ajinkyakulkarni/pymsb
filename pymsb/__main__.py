import os
import sys

from pymsb.language.interpreter import Interpreter


def main():
    """Entry point for PyMSB interpreter"""

    args = sys.argv[1:]
    # TODO: don't run /home/simon/PycharmProjecgts/pymsb/test_code.sb when no args given
    if not args:
        print('''Usage: pymsb [FILEPATH] [ARGUMENT]...
Executes the Microsoft Small Basic code in the given file path, with the given arguments.''')
        source_arg = "/home/simon/PycharmProjects/pymsb/test_code.sb"
        prog_args = args[:]
    else:
        source_arg = args[0]
        prog_args = args[1:]

    print("pymsb.__main__.main executed.  Args:", args)

    path = os.path.abspath(source_arg)
    interpreter = Interpreter()
    interpreter.execute_file(path, prog_args)


if __name__ == "__main__":
    main()
