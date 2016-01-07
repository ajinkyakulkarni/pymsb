from pymsb.language.modules.pymsbmodule import PyMsbModule

# TODO: Eventually, popping from an empty stack needs to terminate the program gracefully.


# noinspection PyPep8Naming
class Stack(PyMsbModule):
    def __init__(self, interpreter):
        super().__init__(interpreter)
        self.stacks = {}

    def GetCount(self, stack_name):
        return len(self.stacks.setdefault(stack_name, []))

    def PopValue(self, stack_name):
        lst = self.stacks.setdefault(stack_name, [])
        if lst:
            return lst.pop()
        return ""

    def PushValue(self, stack_name, value):
        self.stacks.setdefault(stack_name, []).append(value)
