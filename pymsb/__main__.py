import os
import sys

from pymsb.language.interpreter import Interpreter


def main():
    """Entry point for PyMSB interpreter"""

    args = sys.argv[1:]

    if not args:
        print('''Usage: pymsb [FILEPATH] [ARGUMENT]...
Executes the Microsoft Small Basic code in the given file path, with the given arguments.''')
        source_arg = "/home/simon/PycharmProjects/pymsb/test_code.sb"
    else:
        source_arg = args[0]

    print("pymsb.__main__.main executed.  Args:", args)

    path = os.path.abspath(source_arg)
    interpreter = Interpreter()
    interpreter.execute_file(path)


if __name__ == "__main__":
    main()
