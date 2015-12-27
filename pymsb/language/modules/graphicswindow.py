import random
import tkinter as tk
import tkinter.font
from tkinter import messagebox
from pymsb.language.modules.interface import PyMsbWindow
from pymsb.language.modules import utilities


# noinspection PyPep8Naming,PyMethodMayBeStatic
class GraphicsWindow(PyMsbWindow):
    def __init__(self, interpreter, root):
        super().__init__(interpreter, root)
        self.window.title("Microsoft Small Basic Graphics Window")

        self.window.rowconfigure(0, weight=1)
        self.window.columnconfigure(0, weight=1)
        self.canvas = tk.Canvas(self.window)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.config(background="white")

        # Bind mouse, key events
        self.__last_key = "None"
        self.window.bind("<Key>", self.on_key_down)

        # Initialize MSB fields
        self.BrushColor = "#6A5ACD"
        self.PenColor = "#000000"
        self.PenWidth = 2
        self.FontName = None  # TODO: package a font that looks like Tahoma?
        self.FontSize = 12
        self.FontItalic = False
        self.FontBold = False

    #############################################################################
    # MSB Fields

    @property
    def BackgroundColor(self):
        return self.canvas["background"]

    @BackgroundColor.setter
    def BackgroundColor(self, col):
        alpha, bkg = utilities.translate_color(col, "#000000")
        if alpha == 255:
            self.canvas["background"] = bkg
        else:
            self.canvas["background"] = "#000000"

    @property
    def BrushColor(self):
        return self.__brush_color

    # noinspection PyAttributeOutsideInit
    @BrushColor.setter
    def BrushColor(self, b):
        self.__brush_alpha, self.__brush_color = utilities.translate_color(b, "#000000")

    @property
    def CanResize(self):
        return str(self.window.resizable() == (1, 1))

    @CanResize.setter
    def CanResize(self, b):
        if b.lower() == "true":
            self.window.resizable(True, True)
        else:
            self.window.resizable(False, False)

    # TODO: FontBold, FontItalic, FontName
    @property
    def FontBold(self):
        return self.__font_bold

    # noinspection PyAttributeOutsideInit
    @FontBold.setter
    @utilities.bool_setter
    def FontBold(self, fb):
        self.__font_bold = fb

    @property
    def FontItalic(self):
        return self.__font_italic

    # noinspection PyAttributeOutsideInit
    @FontItalic.setter
    @utilities.bool_setter
    def FontItalic(self, fi):
        self.__font_italic = fi

    @property
    def FontName(self):
        return self.__font_name

    # noinspection PyAttributeOutsideInit
    @FontName.setter
    def FontName(self, fn):
        self.__font_name = fn

    @property
    def FontSize(self):
        return self.__font_size

    # noinspection PyAttributeOutsideInit
    @FontSize.setter
    @utilities.numerical_args
    def FontSize(self, fs):
        self.__font_size = max(fs, 0)

    @property
    def LastKey(self):
        return self.__last_key

    # TODO: LastText

    # Note: MouseX and MouseY will track the cursor independently as long as one coordinate is in bounds.
    @property
    def MouseX(self):
        pos = self.window.winfo_pointerx() - self.window.winfo_rootx()
        if pos < 0 or pos > int(self.Width):  # if not visible, self.Width is 1
            return"0"
        return str(pos)

    @property
    def MouseY(self):
        pos = self.window.winfo_pointery() - self.window.winfo_rooty()
        if pos < 0 or pos > int(self.Height): # if not visible, self.Height is 1
            return "0"
        return str(pos)

    @property
    def PenColor(self):
        return self.__pen_color

    # noinspection PyAttributeOutsideInit
    @PenColor.setter
    def PenColor(self, col):
        self.__pen_alpha, self.__pen_color = utilities.translate_color(col, "#000000")

    @property
    def PenWidth(self):
        return self.__pen_width

    # noinspection PyAttributeOutsideInit
    @PenWidth.setter
    def PenWidth(self, p):
        self.__pen_width = utilities.numericize(p, True)

    #############################################################################
    # MSB Methods
    # TODO: optimize the stipple offsets to minimize cancelling stipple patterns
    # TODO: implement true alpha blending instead of using stipple

    def Clear(self):
        self.canvas.delete("all")

    def DrawBoundText(self, x, y, width, text):
        self.DrawText(x, y, text, width)

    def DrawImage(self, imageName, x, y):
        raise NotImplementedError()

    @utilities.numerical_args
    def DrawEllipse(self, x, y, width, height):
        self.draw_shape(self.canvas.create_oval, x, y, x + width, y + height, stipple_offset=tk.CENTER)

    @utilities.numerical_args
    def DrawLine(self, x1, y1, x2, y2):
        self.fill_shape(self.canvas.create_line, x1, y1, x2, y2, width=self.PenWidth,
                        fill=self.PenColor, alpha=self.__pen_alpha)

    @utilities.numerical_args
    def DrawRectangle(self, x, y, width, height):
        self.draw_shape(self.canvas.create_rectangle, x, y, x + width, y + height)

    def DrawResizedImage(self, imageName, x, y, width, height):
        raise NotImplementedError()

    def DrawText(self, x, y, text, width=None):
        x = utilities.numericize(x)
        y = utilities.numericize(y)
        weight = "bold" if self.FontBold else "normal"
        slant = "italic" if self.FontItalic else "roman"
        font = tk.font.Font(root=self.root, family=self.FontName, size=self.FontSize, weight=weight,slant=slant)
        if self.__pen_alpha > 0:
            self.canvas.create_text(x, y, text=text, justify=tk.LEFT, anchor=tk.NW, width=width,
                                    font=font, fill=self.PenColor, stipple=self.get_stipple(self.__pen_alpha))

    @utilities.numerical_args
    def DrawTriangle(self, x1, y1, x2, y2, x3, y3):
        self.draw_shape(self.canvas.create_polygon, x1, y1, x2, y2, x3, y3)

    @utilities.numerical_args
    def FillEllipse(self, x, y, width, height):
        self.fill_shape(self.canvas.create_oval, x, y, x + width, y + height, stipple_offset=tk.CENTER)

    @utilities.numerical_args
    def FillRectangle(self, x, y, width, height):
        self.fill_shape(self.canvas.create_rectangle, x, y, x + width, y + height)

    @utilities.numerical_args
    def FillTriangle(self, x1, y1, x2, y2, x3, y3):
        self.fill_shape(self.canvas.create_polygon, x1, y1, x2, y2, x3, y3)

    def GetColorFromRGB(self, r, g, b):
        def f(n):  # Force value to be 0-255
            return ((abs(int(n)) % 256) + 256) % 256
        return u"#{0:02x}{1:02x}{2:02x}".format(*map(f, (r, g, b))).upper()

    @utilities.numerical_args
    def GetPixel(self, x, y):
        raise NotImplementedError()

    def GetRandomColor(self):
        return self.GetColorFromRGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def SetPixel(self, x, y, color):
        raise NotImplementedError()

    def Show(self):
        super().Show()
        if self.Width == 0:
            self.Width = 624
        if self.Height == 0:
            self.Height = 442

    def ShowMessage(self, message, title):
        self.Show()
        # TODO: replace with custom icon-less modal dialog
        messagebox.showinfo(title, message)

    #############################################################################
    # Helper methods

    def draw_shape(self, draw_func, *coords, stipple_offset=tk.NW):
        self.Show()
        if self.__pen_alpha > 0:
            draw_func(*coords, outline=self.PenColor, width=self.PenWidth, fill="",
                      outlinestipple=self.get_stipple(self.__pen_alpha),
                      outlineoffset=stipple_offset)

    def fill_shape(self, fill_func, *coords, stipple_offset=tk.NW, width=0, fill=None, alpha=None):
        self.Show()
        if not fill:
            fill = self.BrushColor
        if not alpha:
            alpha = self.__brush_alpha
        if alpha > 0:
            fill_func(*coords, width=width, fill=fill,
                      stipple=self.get_stipple(alpha),
                      offset=stipple_offset)

    def get_stipple(self, alpha):
        # return ''
        if alpha >= 255:
            return ''
        if alpha >= 191:
            return "gray75"
        if alpha >= 127:
            return "gray50"
        if alpha >= 63:
            return "gray25"
        if alpha > 0:
            return "gray12"
        return ''  # TODO: figure out a blank stipple in case this is still called when alpha is 0
        # TODO: dynamically determine stipple based on colors involved

    def on_key_down(self, event):
        # TODO: implement the same text representation as MSB
        self.__last_key = event.keysym
        # print(event.char, "|", event.keysym, "|", event.__dict__, sep="")
