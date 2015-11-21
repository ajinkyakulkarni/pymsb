import re
import tkinter as tk
import time

__author__ = 'Simon Tang'


class PyMsbWindow:
    def __init__(self, interpreter, root):
        self.interpreter = interpreter
        self.root = root
        self.window = tk.Toplevel(root)
        self.hide()
        self.window.protocol("WM_DELETE_WINDOW", self.exit_interpreter)

    def exit_interpreter(self):
        self.interpreter.exit()
        self.root.destroy()

    @property
    def Title(self):
        return self.window.title()

    @Title.setter
    def Title(self, title):
        self.window.title(title)

    @property
    def Left(self):
        return str(self.get_geometry()[2])

    @Left.setter
    def Left(self, left):
        self.set_geometry(left=left)

    @property
    def Top(self):
        return str(self.get_geometry()[3])  # TODO: implement setter

    @Top.setter
    def Top(self, top):
        self.set_geometry(top=top)

    @property
    def Width(self):  # although Width and Height are not available in TextWindow they are in GraphicsWindow
        return str(self.get_geometry()[0])

    @Width.setter
    def Width(self, width):
        self.set_geometry(width=width)

    @property
    def Height(self):
        return str(self.get_geometry()[1])

    @Height.setter
    def Height(self, height):
        self.set_geometry(height=height)

    def get_geometry(self):
        g = self.window.geometry()
        m = re.match("(\d+)x(\d+)[+]?([-+]\d+)[+]?([-+]\d+)", g)
        if not m:
            raise ValueError("failed to parse geometry string " + g)
        return tuple(map(int, m.groups()))

    def set_geometry(self, **kwargs):
        self.window.geometry(u"{0:d}x{1:d}+{2:d}+{3:d}".format(
            int(kwargs.get("width", self.Width)),
            int(kwargs.get("height", self.Height)),
            int(kwargs.get("left", self.Left)),
            int(kwargs.get("top", self.Top))
        ))

    def show(self):
        if not self.window.winfo_viewable():
            self.window.deiconify()
            # noinspection PyAttributeOutsideInit
            self.__is_visible = True

    def hide(self):
        self.window.withdraw()
        # noinspection PyAttributeOutsideInit
        self.__is_visible = False

    def is_visible(self):
        return self.__is_visible