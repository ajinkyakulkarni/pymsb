from datetime import datetime as dt
import time


# noinspection PyPep8Naming
class Clock:
    @property
    def Date(self):
        return dt.now().strftime("%m/%d/%Y")

    @property
    def Day(self):
        return str(dt.now().day)

    @property
    def ElapsedMilliseconds(self):
        # TODO: figure out a more precise implementation
        return str((2208988800 + time.time()) * 1000)

    @property
    def Hour(self):
        return str(dt.now().hour)

    @property
    def Millisecond(self):
        return str(dt.now().microsecond//1000)

    @property
    def Minute(self):
        return str(dt.now().minute)

    @property
    def Month(self):
        return str(dt.now().month)

    @property
    def Second(self):
        return str(dt.now().second)

    @property
    def Time(self):
        return dt.now().strftime("%I:%M:%S %p")

    @property
    def WeekDay(self):
        return dt.now().strftime("%A")

    @property
    def Year(self):
        return str(dt.now().year)

