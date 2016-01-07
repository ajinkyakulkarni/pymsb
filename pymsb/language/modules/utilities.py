from collections import namedtuple
import xml.etree.ElementTree as ET
import pkg_resources
from configparser import ConfigParser, ExtendedInterpolation


# Load list of built-in methods, fields, events
def __load_msb_builtins_information():
    global __obj_infos, __msb_capitalizations
    msb_builtins_path = pkg_resources.resource_string(__name__, "msb_builtins.xml")
    root = ET.fromstring(msb_builtins_path)

    # Map properly-capitalized MSB object names to a dict that maps properly-capitalized member names to NamedTuples.
    __obj_infos = dict()
    # Store the proper capitalization for every built-in object, function, event and field name
    __msb_capitalizations = dict()

    MsbFunction = namedtuple('MsbFunction', ['name', 'type', 'num_args', 'returns_value'])
    MsbField = namedtuple('MsbField', ['name', 'type', 'read_only'])
    MsbEvent = namedtuple('MsbEvent', ['name', 'type'])

    for object_element in root:
        object_name = object_element.get("name")
        obj_info = dict()
        m = object_element.find("methods")
        if m is not None:
            for method_element in m:
                name = method_element.get("name")
                num_args = int(method_element.get("num_args", 0))
                returns_value = method_element.get("returns_value", "").lower() in ("1", "true")
                obj_info[name] = MsbFunction(name, "function", num_args, returns_value)
                __msb_capitalizations[name.lower()] = name

        f = object_element.find("fields")
        if f is not None:
            for field_element in f:
                name = field_element.get("name")
                read_only = field_element.get("read_only", "").lower() in ("1", "true")
                obj_info[name] = MsbField(name, "field", read_only)
                __msb_capitalizations[name.lower()] = name

        e = object_element.find("events")
        if e is not None:
            for event_element in e:
                name = event_element.get("name")
                obj_info[name] = MsbEvent(name, "event")
                __msb_capitalizations[name.lower()] = name
        __obj_infos[object_name] = obj_info

__load_msb_builtins_information()


# Load list of named colors
def __load_named_colors():
    global __text_colors, __graphic_colors
    __color_parser = ConfigParser(interpolation=ExtendedInterpolation(), comment_prefixes=(";",))
    __color_parser.read(pkg_resources.resource_filename(__name__, "colors.ini"))
    __text_colors = __color_parser["TextWindow"]
    __graphic_colors = __color_parser["GraphicWindow"]

__load_named_colors()


# Helper function definitions

def get_textwindow_colors():
    """Get a dict mapping color names to color codes that are supported by TextWindow."""
    return __text_colors


def get_graphicwindow_colors():
    """Get a dict mapping color names to color codes that are supported by GraphicWindow."""
    return __graphic_colors


def msb_builtin_object_exists(obj_name):
    return capitalize(obj_name) in __obj_infos


def get_msb_builtin_info(obj_name, member_name):
    """
    Returns a NamedTuple containing information about the specified MSB built-in, or None if the object does not exist.

    If the specified built-in is a function, then the NamedTuple contains fields name, type, num_args and returns_value.
    If the specified built-in is a field, then the NamedTuple contains fields name, type and read_only.
    If the specified built-in is a event, then the NamedTuple contains the field name.

    The "type" field is one of "function", "field" or "event".

    :param obj_name: A case-insensitive string to specify an MSB object.
    :param member_name: A case-insensitive string to specify an MSB object's member (field, event or function)
    :return: A NamedTuple containing information about the specified MSB built-in, or None if the object does not exist.
    """

    obj_name, member_name = capitalize(obj_name), capitalize(member_name)
    return __obj_infos.get(obj_name, {}).get(member_name, None)


def capitalize(msb_name):
    """Returns the properly-capitalized version of the given name for a MSB object, function, field or event."""
    for o_name, info in __obj_infos.items():
        if o_name.lower() == msb_name.lower():
            return o_name
        for name in info:
            if name.lower() == msb_name.lower():
                return name
    return None


# FIXME: replace the current test with an adequately restrictive one
def numericize(number_str, force_numeric=True):
    """
    :param number_str: A string that may or may not contain a numeric value
    :param force_numeric: Whether to return 0 or the given string itself in the case of failed conversion
    :return: The conversion of the given string to a float, or if not convertible, then either 0.0 or the string itself
             depending on the value of force_numeric.
    """
    try:
        f = float(number_str)
        i = int(f)
        if i == f:
            return i
        else:
            return f
    except (ValueError, OverflowError):
        if force_numeric:
            return 0
        else:
            return number_str


def capitalize_text_color(n):
    if n.startswith("dark"):
        return "Dark" + n[4:].capitalize()
    return n.capitalize()


def translate_textwindow_color(col, default_color):
    """
    :param col: The name of a named color (e.g. "white" or "black"), or a string containing an index of a textwindow
                named color (e.g. "0").
    :return: The name of a named color corresponding to the given index or name, or default_color if invalid.
    """
    try:
        return list(get_textwindow_colors().values())[int(float(col))]
    except IndexError:
        return default_color
    except ValueError:
        try:
            return get_textwindow_colors()[col.lower()].lower()
        except KeyError:
            return default_color


def translate_color(code, default_color):
    """
    :param code: The name of a named color (e.g. "white" or "Crimson"), or a hex color code.
    :param default_color: The hex color code that should be returned if code is invalid.
    :return: A pair (alpha, code), where alpha is 0-255 based on the given code (defaults to 255), and
             code is a hex color code (e.g. "#FF00FF") corresponding to the name/code if valid, or default_color
             otherwise.
    """
    code = str(code).upper()
    if code == "TRANSPARENT":
        return 0, "#000000"
    col = code[1:]
    try:
        return 255, get_graphicwindow_colors()[code.lower()]
    except KeyError:
        for digit in col:
            if digit not in "0123456789abcdefABCDEF":
                return 255, default_color
        if not code or code[0] != "#":
            return 255, default_color
        alpha = 255
        color = default_color
        if len(col) == 3:
            color = "#" + "".join(i * 2 for i in col)
        elif len(col) == 4:
            alpha = int(col[0] * 2, 16)
            color = "#" + "".join(i * 2 for i in col[1:])
        elif len(col) == 6:
            alpha = 255
            color = code
        elif len(col) == 8:
            alpha = int(col[0:2], 16)
            color = "#" + col[2:]
        return alpha, color


# TODO: use numerical_args throughout the MSB modules
def numerical_args(method):
    """
    :param method: A method of a class that needs its arguments to be converted into numerical values
    :return: A method that converts its arguments into numerical values automatically.
    """
    def f(self, *args):
        args = map(numericize, args)
        return method(self, *args)
    return f


def bool_setter(method):
    """
    :param method: A method of a class that needs its arguments to be converted from strings into boolean values
    :return: A method that converts its arguments into boolean values automatically.
    """
    def f(self, *args):
        args = ((str(arg).lower() == "true") for arg in args)
        return method(self, *args)
    return f
