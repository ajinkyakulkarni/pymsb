class Process:
    NORMAL = "NORMAL"
    FINISHED = "FINISHED"
    WAITING = "WAITING"

    def __init__(self, line_number, statements):
        self.line_number = line_number
        self.statements = statements  # the statements for this process to be following
        self.sub_return_locations = []  # when a subroutine is called, stores the originating line numbers in LIFO order
        self.__state = Process.NORMAL
        self.blocking_process = None

    def set_blocking_process(self, proc):
        self.__state = Process.WAITING
        self.blocking_process = proc

    def check_blocking(self):
        if self.blocking_process and self.blocking_process.state == Process.FINISHED:
            self.__state = Process.NORMAL
            self.blocking_process = None

    @property
    def state(self):
        if self.line_number == len(self.statements):
            return Process.FINISHED
        return self.__state


class WaitingProcess(Process):
    def __init__(self, condition=None, on_finish=None):
        super().__init__(-1, None)
        self.condition = condition
        self.on_finish = on_finish
        self.resolved = False

    @property
    def state(self):
        if self.resolved:
            return Process.FINISHED
        if self.condition is None:
            return Process.WAITING
        return Process.FINISHED if self.condition() else Process.WAITING

    def resolve(self):
        self.resolved = True


class ProcessBlock(Exception):
    def __init__(self, new_process):
        super().__init__()
        self.new_process = new_process
