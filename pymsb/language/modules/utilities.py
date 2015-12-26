import xml.etree.ElementTree as ET
import itertools
import pkg_resources
from configparser import ConfigParser, ExtendedInterpolation

# Load list of built-in methods, fields, events
# TODO: worry about what variables are being exported
# TODO: decide if this is too ugly/hacky
msb_builtins_path = pkg_resources.resource_string(__name__, "msb_builtins.xml")
root = ET.fromstring(msb_builtins_path)

obj_infos = {}
for child in root:
    obj_info = {"methods": dict(), "fields": dict(), "events": set()}
    m = child.find("methods")
    if m is not None:
        for method in m:
            name = method.get("name")
            num_args = int(method.get("num_args", 0))
            obj_info["methods"][name] = num_args
    f = child.find("fields")
    if f is not None:
        for field in f:
            name = field.get("name")
            readonly = bool(field.get("readonly", False))  # if readonly is any non-empty string, then is read-only
            obj_info["fields"][name] = readonly
    e = child.find("events")
    if e is not None:
        for event in e:
            obj_info["events"].add(event.get("name"))
    obj_infos[child.get("name")] = obj_info

# Load named colours
color_parser = ConfigParser(interpolation=ExtendedInterpolation(), comment_prefixes=(";",))
color_parser.read(pkg_resources.resource_filename(__name__, "colors.ini"))
text_colors = color_parser["TextWindow"]
graphic_colors = color_parser["GraphicWindow"]


# Helper functions
def get_msb_method_args(obj_name, method_name):
    for o_name, info in obj_infos.items():
        if o_name.lower() == obj_name.lower():
            for m_name, num_args in info["methods"].items():
                if m_name.lower() == method_name.lower():
                    return num_args
    return None


def get_msb_field_readonly(obj_name, field_name):
    """
    :param obj_name: The name of an MSB object.
    :param field_name: The name of an MSB field.
    :return: True if the given field is read-only, False if the given field is not read-only
    """
    for o_name, info in obj_infos.items():
        if o_name.lower() == obj_name.lower():
            for f_name, readonly in info["fields"].items():
                if f_name.lower() == field_name.lower():
                    return readonly
    return None  # TODO: add the check and corresponding errors for when the object or member don't exist


def msb_event_exists(obj_name, event_name):
    for o_name, info in obj_infos.items():
        if o_name.lower() == obj_name.lower():
            for e_name in info["events"]:
                if e_name.lower() == event_name.lower():
                    return True
    return False


def capitalize(msb_name):
    for o_name, info in obj_infos.items():
        if o_name.lower() == msb_name.lower():
            return o_name
        for name in itertools.chain(info["methods"].keys(),
                                    info["fields"].keys(),
                                    info["events"]):
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
        return list(color_parser["TextWindow"].values())[int(float(col))]
    except IndexError:
        return default_color
    except ValueError:
        try:
            return color_parser["TextWindow"][col.lower()].lower()
        except KeyError:
            return default_color
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
    col = code[1:]
    try:
        return 255, color_parser["GraphicWindow"][code.lower()]
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
