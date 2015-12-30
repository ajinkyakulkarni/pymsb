# noinspection PyPep8Naming
class Desktop:
    def __init__(self, interpreter, root):
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