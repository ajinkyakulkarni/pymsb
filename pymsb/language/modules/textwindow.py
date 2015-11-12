import tkinter as tk
from pymsb.language.modules import utilities as py_msb_utils
from pymsb.language.modules.interface import PyMsbWindow
from idlelib.WidgetRedirector import WidgetRedirector

# TODO: implement text input inside the output console instead of in a separate tk.Entry
# TODO: make the window follow the insertion cursor.

from pymsb.language.process import ProcessBlock, Process, WaitingProcess


# noinspection PyAttributeOutsideInit,PyPep8Naming
class TextWindow(PyMsbWindow):
    BLANK = ""
    ALL = "ALL"
    NUMERICAL = "NUMERICAL"

    def __init__(self, interpreter, root):
        super().__init__(root)

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
        self.input_box.configure(state=tk.DISABLED)

        scroll_y.config(command=self.text_box.yview)

        frame.pack(fill=tk.BOTH, expand=tk.YES)

        # Customize with default values
        self.BackgroundColor = "black"
        self.ForegroundColor = "gray"
        self.Title = "Small Basic Text Window"

        self.prepare_color_tags()

        self.cached_user_input = []
        self.pause_processes = []

        self.current_input_mode = None

    def on_insert_change(self, result, *args):
        print("result: ", result)
        print("args: ", args)

    def on_input_box_return(self, event):
        if self.pause_processes:
            self.pause_processes[-1].resolve()

        else:
            user_input = self.input_box.get().splitlines()
            if user_input:
                self.cached_user_input.extend(user_input)
            else:
                self.cached_user_input.append("")
            self.input_box.delete(0, tk.END)
            self.input_box.configure(state=tk.DISABLED)

    def on_input_box_key(self, event):
        pass

    def has_user_input(self):
        return len(self.cached_user_input) > 0

    def prepare_color_tags(self):
        # Prepare all the color tags for text
        for name, val in py_msb_utils.COLOR_TRANSLATION.items():
            self.text_box.tag_configure("foreground_" + name, foreground=val)
            self.text_box.tag_configure("background_" + name, background=val)
            self.text_box.tag_configure("output")

    @property
    def BackgroundColor(self):
        return self.__background_color

    @BackgroundColor.setter
    def BackgroundColor(self, background_color):
        if background_color in py_msb_utils.COLOR_TRANSLATION:
            self.__background_color = background_color

    @property
    def ForegroundColor(self):
        return self.__foreground_color

    @ForegroundColor.setter
    def ForegroundColor(self, foreground_color):
        if foreground_color in py_msb_utils.COLOR_TRANSLATION:
            self.__foreground_color = foreground_color
            self.text_box.config(insertbackground=py_msb_utils.COLOR_TRANSLATION[foreground_color])

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

    # noinspection PyMethodMayBeStatic
    def Hide(self):
        super().hide()

    def Pause(self, message="Press any key to continue..."):
        self.Show()
        self.current_input_mode = TextWindow.BLANK

        # Check if we've "unpaused" the most recent call to pause  TODO: decide if it should be LIFO or FIFO
        if self.pause_processes and self.pause_processes[-1].state == Process.FINISHED:
            self.pause_processes.pop()
            return

        if message is not None:
            self.WriteLine(message)

        # Otherwise, pause the current process
        p = TextWindowPauseProcess()
        self.pause_processes.append(p)
        raise ProcessBlock(p)

    def PauseIfVisible(self):
        if self.is_visible():
            self.Pause()

    def PauseWithoutMessage(self):
        self.Pause(message=None)

    def Read(self):
        self.Show()

        # If there is user input cached up, then return a line of that.
        if self.has_user_input():
            user_input = self.cached_user_input.pop(0)
            tmp = self.ForegroundColor
            self.ForegroundColor = "green"
            self.WriteLine(user_input)
            self.ForegroundColor = tmp
            return user_input

        # Otherwise, block the process until we get user input.
        self.input_box.configure(state=tk.NORMAL)
        p = ReadUserInputProcess(self.has_user_input)
        raise ProcessBlock(p)

    def ReadKey(self):
        self.Show()  # todo: implement

    def ReadNumber(self):
        self.Show()
        return self.Read()  # todo: implement

    # noinspection PyMethodMayBeStatic
    def Show(self):
        """Make the TextWindow visible on the screen; if already visible, does nothing."""
        super().show()

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


class ReadUserInputProcess(WaitingProcess):
    pass


class TextWindowPauseProcess(WaitingProcess):
    pass
