import math
import random
import pymsb.language.modules
from pymsb.language.modules.pymsbmodule import PyMsbModule


def math_wrapper(func):
    return lambda self, *args: str(func(*(map(pymsb.language.modules.utilities.numericize, args))))

# TODO: find the differences in precision with original MSB?


# noinspection PyPep8Naming
class Math(PyMsbModule):
    """
    The implementation of the MSB Math module.
    """

    @property
    def Pi(self):
        return str(math.pi)  # TODO: restrict precision level?

    ArcCos = math_wrapper(math.acos)
    ArcSin = math_wrapper(math.asin)
    ArcTan = math_wrapper(math.atan)
    Ceiling = math_wrapper(math.ceil)
    Cos = math_wrapper(math.cos)
    Floor = math_wrapper(math.floor)
    GetDegrees = math_wrapper(math.degrees)
    GetRadians = math_wrapper(math.radians)
    GetRandomNumber = math_wrapper(lambda max_number: random.randint(1, max_number))  # inclusive on both ends
    Log = math_wrapper(math.log10)
    Max = math_wrapper(max)
    Min = math_wrapper(min)
    NaturalLog = math_wrapper(math.log)
    Power = math_wrapper(math.pow)
    Remainder = math_wrapper(lambda dividend, divisor: dividend % divisor)
    Round = math_wrapper(round)
    Sin = math_wrapper(math.sin)
    SquareRoot = math_wrapper(math.sqrt)
    Tan = math_wrapper(math.tan)
