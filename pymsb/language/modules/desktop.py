import os
import platform
import pathlib
import tempfile
import requests
from pymsb.language.modules.pymsbmodule import PyMsbModule


# noinspection PyPep8Naming
class Desktop(PyMsbModule):
    def __init__(self, interpreter, root):
        super().__init__(interpreter)
        self.interpreter = interpreter
        self.root = root

    @property
    def Width(self):
        return str(self.root.winfo_screenwidth())

    @property
    def Height(self):
        return str(self.root.winfo_screenheight())

    def SetWallpaper(self, path_or_url):
        '''
        Sets the system desktop wallpaper to a local or internet image.  If it fails, nothing should change.
        However this is only implemented in Linux and the wallpaper will reset to default if this function fails.
        then no change is made.
        :param path_or_url: A path to a local image file or a URL to an image from the internet.
        :return: None
        '''

        plat = platform.system()
        if plat == "Windows":
            # TODO: implement SetWallpaper for Windows; I couldn't get the ctypes code samples to work on my VM.
            # old_path = ?
            # file_path = self.__get_file_path(path_or_url)
            # if file_path:
            #     setwallpaper with file_path
            pass

        elif plat == "Darwin":  # This is actually Mac OS X.
            # TODO: implement SetWallpaper for Mac OS X.
            # old_path = ?
            # file_path = self.__get_file_path(path_or_url)
            # if file_path:
            #     setwallpaper with file_path
            pass

        elif plat == "Linux":
            # FIXME: detect when gsettings fails in Desktop.SetWallpaper.
            # This should work on Ubuntu (Unity) and Linux Mint (Cinnamon) at the least.
            old_path = os.popen('gsettings get org.cinnamon.desktop.background picture-uri').read()

            file_path = self.__get_file_path(path_or_url)
            if file_path:
                os.system('gsettings set org.cinnamon.desktop.background picture-uri  "{}"'.format(file_path))

    def __get_file_path(self, path_or_url):
        # Return the given path if valid, otherwise tries to download the file to the temporary directory, otherwise
        # returns None.

        # Check if file exists locally.
        path = pathlib.Path(path_or_url)
        if path.is_file():
            return path_or_url

        # If file does not exist locally, try to download to temp folder.
        else:
            response = self.__get_response(path_or_url)
            if response:
                ntf = tempfile.NamedTemporaryFile(suffix=".tmp", prefix="tmp", delete=False)
                ntf.write(response.content)
                ntf.close()
                return ntf.name
            else:
                return

    def __get_response(self, url):
        try:
            return requests.get(url)
        except BaseException as e:
            return None
