import os
import shutil
import tempfile
from pymsb.language.modules.pymsbmodule import PyMsbModule


def file_method(func):
    """
    A wrapper for the functions in FileModule.

    :param func: A FileModule member function.
    :return: A function that will return "SUCCESS"/"FAILED" unless otherwise specified in the given function, and that
             will automatically update File.LastError.
    """
    def f(self, *args):
        try:
            result = func(self, *args)
            self.LastError = None
            if result is None:
                return "SUCCESS"
            return result
        except BaseException as e:
            self.LastError = e
            print(e)
        return "FAILED"
    return f

# TODO: test if all of these work the same way as MSB, across Windows XP, Mac OS X and Linux (Ubuntu).
# TODO: Optimize these operations by condensing number of individual disk read/writes


# noinspection PyPep8Naming,PyMethodMayBeStatic
class FileModule(PyMsbModule):
    def __init__(self, interpreter):
        super().__init__(interpreter)
        self.array_parser = interpreter.array_parser
        self.__last_error = ""

    @property
    def LastError(self):
        """
        :return: Returns the representation of the most recent file I/O error, or the empty string if the most recent
                 operation was successful.
        """
        return self.__last_error

    @LastError.setter
    def LastError(self, error):
        """
        Updates the File.LastError property with a description of the given error, or the empty string if error is None.
        :param error: The error raised during execution of a File member function, or None.
        """
        if error is None:
            self.__last_error = ""
        else:
            self.__last_error = str(error)  # TODO: translate into proper error description

    @file_method
    def AppendContents(self, file_path, contents):
        """
        Appends the given string to the end of the file specified by a file_path, and appends an additional newline
        character.  If the file does not exist, then the file is created.
        :param file_path: The path to the file to be appended to.
        :param contents: The contents to be appended to the file.
        """
        with open(file_path, mode="a") as f:
            f.write(contents + "\n")

    @file_method
    def CopyFile(self, source_path, destination_path):
        """
        Copies the file from source_path to destination_path.  If destination_path refers to a non-existent location, then
        it will be created.  If the destination path refers to an existing file, it will not overwrite the file.
        :param source_path: A path to a source file.
        :param destination_path: A path to a directory or new file.
        """
        # FIXME: the behaviour of this function does not match the description.
        shutil.copyfile(source_path, destination_path)

    @file_method
    def CreateDirectory(self, path):
        os.mkdir(path)

    @file_method
    def DeleteDirectory(self, path):
        shutil.rmtree(path)

    @file_method
    def DeleteFile(self, path):
        os.remove(path)

    @file_method
    def GetDirectories(self, path):
        dirpath, dirnames, filenames = os.walk(path)
        dirs = (os.path.join(dirpath, name) for name in dirnames)
        return self.array_parser.list_to_array(dirs)

    @file_method
    def GetFiles(self, path):
        dirpath, dirnames, filenames = os.walk(path)
        files = (os.path.join(dirpath, name) for name in filenames)
        return self.array_parser.list_to_array(files)

    @file_method
    def GetSettingsFilePath(self):
        """
        Gets the full path to the settings file for the current program.  If the current program is being run from a
        file, then the returned path points to a file with a name beginning with the executable file name and ending in
        ".settings".  If the program has no source file (i.e. the interpreter is only executing code in a string) then a
        path to a temporary file of the form "tmp(...).tmp.settings" in the system's temporary folder is returned.

        :return: A full path to the file designated for saving settings for the current program.
        """
        p = self.interpreter.program_path
        if p:
            return p + ".settings"
        return tempfile.NamedTemporaryFile(prefix="tmp", suffix=".tmp.settings", delete=False).name

    @file_method
    def GetTemporaryFilePath(self):
        """
        Gets the full path to a new file (not previously existing) for temporary storage, in the system's temporary
        storage directory.  Multiple calls to this function will return distinct file paths.
        :return: A full path to a new file for temporary storage.
        """
        return tempfile.NamedTemporaryFile(prefix="tmp", suffix=".tmp", delete=False).name

    @file_method
    def InsertLine(self, path, line_number, contents):
        try:
            line_number = int(line_number)
        except:
            return  # Microsoft has strange behaviour; this case intentionally returns "SUCCESS"

        if line_number <= 0:
            return

        with open(path, mode="r+") as f:
            lines = f.readlines()
            lines.insert(line_number - 1, contents)  # appends to end when line_number > length of lines
            f.seek(0)
            f.writelines(lines)

    @file_method
    def ReadContents(self, path):
        try:
            with open(path) as f:
                return f.read()
        except BaseException as e:
            return ""

    @file_method
    def ReadLine(self, path, line_number):
        try:
            with open(path) as f:
                return f.readlines()[int(line_number)]
        except:  # Microsoft implementation silently fails and never sets LastError flag either.
            return ""

    @file_method
    def WriteLine(self, path, line_number, contents):
        try:
            line_number = int(line_number)
        except:
            return  # Microsoft has strange behaviour; this case returns "SUCCESS"

        with open(path, mode="r+") as f:
            lines = f.readlines()
            if 1 <= line_number <= len(lines):
                lines[line_number - 1] = contents
            elif line_number > len(lines):
                lines.append(contents)
            else:
                return
            f.seek(0)
            f.writelines(lines)
