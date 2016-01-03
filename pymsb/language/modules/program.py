import tempfile
import time


# noinspection PyPep8Naming,PyMethodMayBeStatic
class Program:
    """
    The implementation of the MSB Program module.
    :param interpreter: The interpreter used to execute this instance of PyMSB.
    """

    def __init__(self, interpreter):
        self.interpreter = interpreter

    @property
    def ArgumentCount(self):
        """
        Returns the number of arguments passed to this MSB program as a string.  (This does not include arguments passed
        to the Python interpreter or arguments absorbed by the call to PyMSB).

        :return: The number of arguments passed to this MSB program, as a string.
        """
        return str(len(self.interpreter.prog_args))

    @property
    def Directory(self):
        """
        Returns the directory of the MSB program being executed.  If the interpreter is executing code directly from a
        string, then this returns a directory in the system's temporary storage location.

        :return: The executing program's directory.
        """
        if self.interpreter.program_path:
            return self.interpreter.program_path
        return tempfile.gettempdir()  # same every time this is evaluated

    def Delay(self, milliseconds):
        time.sleep(milliseconds / 1000)

    def End(self):
        # noinspection PyProtectedMember
        self.interpreter._exit()

    def GetArgument(self, index):
        try:
            index = int(index) - 1
        except:
            return ""
        if 0 <= index < len(self.interpreter.prog_args):
            return self.interpreter.prog_args[index]
        return ""
