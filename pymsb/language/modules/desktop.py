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
        pass  # TODO: implement Desktop.SetWallpaper, across all supported platforms