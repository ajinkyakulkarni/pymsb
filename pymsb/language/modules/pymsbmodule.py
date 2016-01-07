from pymsb.language.modules import utilities


class PyMsbModule:
    """
    This is the base class for all of the MSB modules (e.g. TextWindow, Clock).
    :param interpreter:
    """

    def __init__(self, interpreter):
        self.interpreter = interpreter

        self.__events = {}

    def get_event_sub(self, event_name):
        """
        Returns the name of the subroutine (defined in MSB code) assigned to the given event, or None if none is
        assigned.
        :param event_name: The name of an event in this MSB module (e.g. "Tick" in the Timer class).
        :return: The name of the assigned MSB subroutine, or None if none is assigned.
        """
        return self.__events.get(utilities.capitalize(event_name), None)

    def set_event_sub(self, event_name, subroutine_name):
        """
        Assigns an MSB subroutine to the specified event, by name.  (e.g. assigning "say_hello" to "Tick" in the Timer
        MSB module, when say_hello is the name of a subroutine defined in the MSB code).
        :param event_name: The name of the specified event.
        :param subroutine_name:
        """
        self.__events[utilities.capitalize(event_name)] = subroutine_name

    def _trigger_event(self, event_name):
        """
        Tells the interpreter to execute the subroutine assigned to an MSB event in this MSB module.
        :param event_name: The name of the event (e.g. "Tick" in the Timer class)
        """
        # noinspection PyNoneFunctionAssignment
        sub_name = self.get_event_sub(event_name)
        if sub_name:
            # noinspection PyProtectedMember
            self.interpreter._call_subroutine_in_new_thread(sub_name)
