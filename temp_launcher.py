import pkg_resources
from pymsb.language.interpreter import Interpreter

__author__ = 'Simon Tang'

if __name__ == "__main__":
    test_code = pkg_resources.resource_string(__name__, "test_code.sb").decode()
    interpreter = Interpreter()
    interpreter.run(test_code)
