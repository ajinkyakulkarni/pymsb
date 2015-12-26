from queue import Queue
import tkinter as tk
import time
from pymsb.language.modules import utilities as py_msb_utils
from pymsb.language.modules.interface import PyMsbWindow
from idlelib.WidgetRedirector import WidgetRedirector

# TODO: implement text input inside the output console instead of in a separate tk.Entry
# TODO: make the window follow the insertion cursor.
# TODO: rework textwindow so input is inserted directly into window instead of textbox below, and allow cursor in any position in range


# noinspection PyAttributeOutsideInit,PyPep8Naming
class TextWindow(PyMsbWindow):
    BLANK = ""
    ALL = "ALL"
    NUMERICAL = "NUMERICAL"
    INPUT_DISABLED = "INPUT_DISABLED"

    def __init__(self, interpreter, root):
        super().__init__(interpreter, root)

        self.interpreter = interpreter

        # Set up GUI
        frame = tk.Frame(self.window, bd=2, relief=tk.SUNKEN)  # TODO: research these kwargs
        frame.grid_rowconfigure(0, weight=1)  # output section
        frame.grid_rowconfigure(1, weight=0)  # input section

        frame.grid_columnconfigure(0, weight=0)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(2, weight=0)

        scroll_y = tk.Scrollbar(frame, orient=tk.VERTICAL)
        scroll_y.grid(column=2, rowspan=2, sticky=(tk.N + tk.S + tk.E))

        self.text_box = TextWithInsertChangeCallback(
            self.on_insert_change,
            frame, background="black", bd=0, height=25, width=80,
            yscrollcommand=scroll_y.set, state=tk.DISABLED)

        self.text_box.grid(row=0, column=0, columnspan=2, sticky=(tk.N + tk.S + tk.E + tk.W))

        self.input_label = tk.Label(frame, text="Input: ")
        self.input_label.grid(row=1, sticky=tk.W)

        self.input_box = tk.Entry(frame,
                                  # background="black", foreground="gray",
                                  bd=0)
        self.input_box.grid(row=1, column=1, sticky=(tk.N + tk.E + tk.S + tk.W))
        self.input_box.bind("<Return>", self.on_input_box_return)
        self.input_box.bind("<Key>", self.on_input_box_key)
        self.input_box.focus()

        scroll_y.config(command=self.text_box.yview)

        frame.pack(fill=tk.BOTH, expand=tk.YES)

        # Customize with default values
        self.BackgroundColor = "black"
        self.ForegroundColor = "gray"
        self.window.title("Microsoft Small Basic Text Window")

        self.prepare_color_tags()

        self.cached_user_input = Queue()

        self.current_input_mode = TextWindow.INPUT_DISABLED

    def on_insert_change(self, result, *args):
        print("result: ", result)
        print("args: ", args)

    def on_input_box_return(self, event):
        user_input = self.input_box.get().splitlines()
        if user_input:
            for line in user_input:
                self.cached_user_input.put(line)
        else:
            self.cached_user_input.put("")
        self.input_box.delete(0, tk.END)

    def on_input_box_key(self, event):
        pass

    def has_user_input(self):
        return not self.cached_user_input.empty()

    def prepare_color_tags(self):
        # Prepare all the color tags for text
        for name, val in py_msb_utils.color_parser["TextWindow"].items():
            name = py_msb_utils.capitalize_text_color(name)
            self.text_box.tag_configure("foreground_" + name, foreground=val)
            self.text_box.tag_configure("background_" + name, background=val)
            self.text_box.tag_configure("output")

    @property
    def current_input_mode(self):
        return self.__current_input_mode

    @current_input_mode.setter
    def current_input_mode(self, mode):
        # TODO: add restrictions on the input that can be accepted as it is typed
        # TODO: update this when we no longer use external box
        self.__current_input_mode = mode
        if mode == TextWindow.INPUT_DISABLED:
            self.input_box.configure(state=tk.DISABLED)
            return

        self.input_box.configure(state=tk.NORMAL)
        if mode == TextWindow.BLANK:
            pass
        elif mode == TextWindow.NUMERICAL:
            pass
        elif mode == TextWindow.ALL:
            pass


    @property
    def BackgroundColor(self):
        code = self.__background_color
        for key, val in py_msb_utils.color_parser["TextWindow"].items():
            if code == val:
                return py_msb_utils.capitalize_text_color(key)

    @BackgroundColor.setter
    def BackgroundColor(self, background_color):
        try:
            default = self.__background_color
        except AttributeError:
            default = "#000000"
        self.__background_color = py_msb_utils.translate_textwindow_color(background_color, default).upper()

    @property
    def ForegroundColor(self):
        code = self.text_box["insertbackground"].upper()
        for key, val in py_msb_utils.color_parser["TextWindow"].items():
            if code == val:
                return py_msb_utils.capitalize_text_color(key)

    @ForegroundColor.setter
    def ForegroundColor(self, foreground_color):
        current = self.text_box["insertbackground"].upper()
        self.text_box["insertbackground"] = py_msb_utils.translate_textwindow_color(foreground_color, current).upper()

    @property
    def CursorLeft(self):
        return str(self.text_box.index(tk.INSERT).split(".")[1])

    @CursorLeft.setter
    def CursorLeft(self, cl):
        self.text_box.mark_set(tk.INSERT, u"{0:d}.{1:d}".format(int(self.CursorTop) + 1, int(cl)))

    @property
    def CursorTop(self):
        return str(int(self.text_box.index(tk.INSERT).split(".")[0]) - 1)

    @CursorTop.setter
    def CursorTop(self, ct):
        self.text_box.mark_set(tk.INSERT, u"{0:d}.{1:d}".format(int(ct) + 1, int(self.CursorLeft)))

    def Clear(self):
        self.text_box.delete("1.0", tk.END)

    def Pause(self, message="Press any key to continue..."):
        self.Show()
        self.current_input_mode = TextWindow.BLANK

        if message is not None:
            self.WriteLine(message)

        # TODO: decide if cached user input should skip Pause (right now, it does)
        self.Read()

    def PauseIfVisible(self):
        if self.is_visible():
            self.Pause()

    def PauseWithoutMessage(self):
        # noinspection PyTypeChecker
        self.Pause(message=None)

    def Read(self):
        self.Show()

        self.current_input_mode = TextWindow.ALL

        # Wait for user input
        while not self.has_user_input():
            time.sleep(0.1)
        self.current_input_mode = None

        user_input = self.cached_user_input.get(0)
        self.cached_user_input.task_done()

        tmp = self.ForegroundColor
        self.ForegroundColor = "green"
        self.WriteLine(user_input)
        self.ForegroundColor = tmp
        return user_input

    def ReadKey(self):
        # Note - ReadKey exists in MSB but MSB 1.2 IDE doesn't display it in the autocomplete for some reason
        # (another reason why Microsoft's own implementation of MSB is unreliable)
        # TODO: make ReadKey only take exactly one character out of the input instead of removing a line
        # TODO: figure out the behaviour of ReadKey() when enter, tab, etc. are involved
        # TODO: implement ReadKey after revamping the console
        return self.Read()[0]

    def ReadNumber(self):
        self.Show()
        # TODO: make the text box reject invalid input as it is entered instead of rejecting entire lines of input
        while True:
            self.current_input_mode = TextWindow.NUMERICAL
            user_input = self.Read()
            converted = py_msb_utils.numericize(user_input, False)
            if isinstance(converted, str):  # wasn't a numeric input
                continue
            return str(converted)

    def Write(self, contents):
        """Outputs the contents of the contents string to the TextWindow."""
        self.Show()

        self.text_box.configure(state=tk.NORMAL)
        self.text_box.insert(tk.INSERT,
                             contents,
                             ("foreground_" + self.ForegroundColor, "background_" + self.BackgroundColor))
        self.text_box.see(tk.INSERT)
        self.text_box.configure(state=tk.DISABLED)

    def WriteLine(self, contents):
        """Outputs the contents of the contents string to the TextWindow, with a trailing newline character."""
        self.Write(contents + "\n")


# http://stackoverflow.com/questions/13835207/binding-to-cursor-movement-doesnt-change-insert-mark
# TODO: revisit this some day
class TextWithInsertChangeCallback(tk.Text):
    def __init__(self, on_insert_change, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)

        self.redirector = WidgetRedirector(self)
        self.insert = self.redirector.register("insert", lambda *args, **kw: "break")
        self.delete = self.redirector.register("delete", lambda *args, **kw: "break")

        self.callback = on_insert_change

        private_callback = self.register(self._callback)
        self.tk.eval('''
            proc widget_proxy {actual_widget callback args} {

                # this prevents recursion if the widget is called
                # during the callback
                set flag ::dont_recurse(actual_widget)

                # call the real tk widget with the real args
                set result [uplevel [linsert $args 0 $actual_widget]]

                # call the callback and ignore errors, but only
                # do so on inserts, deletes, and changes in the
                # mark. Otherwise we'll call the callback way too
                # often.
                if {! [info exists $flag]} {
                    if {([lindex $args 0] in {insert replace delete}) ||
                        ([lrange $args 0 2] == {mark set insert})} {
                        # the flag makes sure that whatever happens in the
                        # callback doesn't cause the callbacks to be called again.
                        set $flag 1
                        catch {$callback $result {*}$args } callback_result
                        unset -nocomplain $flag
                    }
                }

                # return the result from the real widget command
                return $result
            }
            ''')
        self.tk.eval('''
            rename {widget} _{widget}
            interp alias {{}} ::{widget} {{}} widget_proxy _{widget} {callback}
        '''.format(widget=str(self), callback=private_callback))

    def _callback(self, result, *args):
        self.callback(result, *args)
