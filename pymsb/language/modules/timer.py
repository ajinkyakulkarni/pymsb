import threading
from pymsb.language.modules.pymsbmodule import PyMsbModule


# noinspection PyPep8Naming
class Timer(PyMsbModule):
    def __init__(self, interpreter):
        super().__init__(interpreter)
        self.__interval = 100000000
        self.__timer = None

    @property
    def Interval(self):
        return str(self.__interval)

    @Interval.setter
    def Interval(self, interval):
        try:
            self.__interval = max(10, min(100000000, int(interval)))
        except:
            self.__interval = 10
        print("interval:", self.__interval)

    def Pause(self):
        if self.__timer:
            self.__timer.cancel()
            self.__timer = None

    def Resume(self):
        """Begins the timer again, with the time elapsed since the last tick reset to 0."""
        self.Pause()
        self.__timer = threading.Timer(self.__interval/1000, self.__on_tick)
        self.__timer.daemon = True
        self.__timer.start()

    def __on_tick(self):
        self._trigger_event("Tick")
        self.Resume()
