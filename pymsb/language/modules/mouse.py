import threading
import pymouse
from pymsb.language.modules import utilities
from pymsb.language.modules.pymsbmodule import PyMsbModule


# noinspection PyPep8Naming
class Mouse(PyMsbModule):
    def __init__(self, interpreter):
        super().__init__(interpreter)

        self.__pymouse = pymouse.PyMouse()
        self.__mouse_click_event = MouseClickEvent(self)

        self._left_down = False
        self._right_down = False

        # noinspection PyProtectedMember
        threading._start_new_thread(self.__mouse_click_event.run, tuple())

    @property
    def MouseX(self):
        return str(self.__pymouse.position()[0])

    @MouseX.setter
    def MouseX(self, x):
        self.__pymouse.move(utilities.numericize(x, force_numeric=True), self.__pymouse.position()[1])

    @property
    def MouseY(self):
        return str(self.__pymouse.position()[1])

    @MouseY.setter
    def MouseY(self, y):
        self.__pymouse.move(self.__pymouse.position()[0], utilities.numericize(y, force_numeric=True))

    @property
    def IsLeftButtonDown(self):
        return str(self._left_down)

    @property
    def IsRightButtonDown(self):
        return str(self._right_down)

    def on_mouse_click(self, button, press):
        if button == 1:
            self._left_down = press
        if button == 2:
            self._right_down = press


class MouseClickEvent(pymouse.PyMouseEvent):
    def __init__(self, mouse_module):
        super().__init__()
        self.__mouse_module = mouse_module

    def click(self, x, y, button, press):
        self.__mouse_module.on_mouse_click(button, press)