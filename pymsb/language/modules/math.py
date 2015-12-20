import math
import random

# TODO: find the differences in precision with original MSB?


class Math:
    pass


def conv(val):
    # TODO: implement the less permissive float conversion
    # noinspection PyBroadException
    try:
        return float(val)
    except:
        return 0


def math_wrapper(func):
    return lambda self, *args: str(func(*(map(conv, args))))


Math.ArcCos = math_wrapper(math.acos)
Math.ArcSin = math_wrapper(math.asin)
Math.ArcTan = math_wrapper(math.atan)
Math.Ceiling = math_wrapper(math.ceil)
Math.Cos = math_wrapper(math.cos)
Math.Floor = math_wrapper(math.floor)
Math.GetDegrees = math_wrapper(math.degrees)
Math.GetRadians = math_wrapper(math.radians)
Math.GetRandomNumber = math_wrapper(lambda max_number: random.randint(1, max_number))  # inclusive on both ends
Math.Log = math_wrapper(math.log10)
Math.Max = math_wrapper(max)
Math.Min = math_wrapper(min)
Math.NaturalLog = math_wrapper(math.log)
Math.Pi = math.pi  # TODO: decide if using this or Microsoft's string constant
Math.Power = math_wrapper(math.pow)
Math.Remainder = math_wrapper(lambda dividend, divisor: dividend % divisor)
Math.Round = math_wrapper(round)
Math.Sin = math_wrapper(math.sin)
Math.SquareRoot = math_wrapper(math.sqrt)
Math.Tan = math_wrapper(math.tan)
