import os
import shutil
import tempfile


def file_method(func):
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
class FileModule:
    def __init__(self):
        self.__last_error = ""

    @property
    def LastError(self):
        return self.__last_error

    @LastError.setter
    def LastError(self, error):
        if error is None:
            self.__last_error = ""
        else:
            self.__last_error = str(error)  # TODO: translate into proper error message

    @file_method
    def AppendContents(self, file_path, contents):
        with open(file_path, mode="a") as f:
            f.write(contents + "\n")

    @file_method
    def CopyFile(self, source_path, destination_path):
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
        # TODO: make into MSB array

    @file_method
    def GetFiles(self, path):
        dirpath, dirnames, filenames = os.walk(path)
        files = (os.path.join(dirpath, name) for name in filenames)
        # TODO: make into MSB array

    @file_method
    def GetSettingsFilePath(self):
        # TODO: implement File.GetSettingsFilePath
        raise NotImplementedError("Settings file path needs Program module implementation")

    @file_method
    def GetTemporaryFilePath(self):
        ntf = tempfile.NamedTemporaryFile(suffix=".tmp", prefix="tmp", delete=False)
        return ntf.name

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
            return  # Microsoft has strange behaviour; this case intentionally returns "SUCCESS"

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
