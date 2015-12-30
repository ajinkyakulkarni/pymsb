# TODO: Eventually, popping from an empty stack needs to terminate the program gracefully.

# noinspection PyPep8Naming
class Stack:
    def __init__(self):
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
