import tkinter as tk
from pymsb.language.modules.interface import PyMsbWindow


class GraphicsWindow(PyMsbWindow):
    def __init__(self, interpreter, root):
        super().__init__(interpreter, root)

        self.interpreter = interpreter

        self.Title = "Microsoft Small Basic Graphics Window"
