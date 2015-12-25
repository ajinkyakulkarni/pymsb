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
color_parser = ConfigParser(interpolation=ExtendedInterpolation(), comment_prefixes=("//",))
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
    for o_name, info in obj_infos.items():
        if o_name.lower() == obj_name.lower():
            for f_name, readonly in info["fields"].items():
                if f_name.lower() == field_name.lower():
                    return readonly
    return None


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


# TODO: replace the current etest with an adequately restrictive one
def numericize(number_str, force_numeric=True):
    '''
    :param number_str: A string that may or may not contain a numeric value
    :param force_numeric: Whether to return 0.0 or the given string itself in the case of failed conversion
    :return: The conversion of the given string to a float, or if not convertible, then either 0.0 or the string itself
             depending on the value of force_numeric.
    '''
    try:
        int(float(number_str))
        return float(number_str)
    except:
        if force_numeric:
            return 0.0
        else:
            return number_str


def capitalize_text_color(n):
    if n.startswith("dark"):
        return "Dark" + n[4:].capitalize()
    return n.capitalize()


def translate_textwindow_color(col, default_color):
    '''
    :param col: The name of a named color (e.g. "white" or "black"), or a string containing an index of a textwindow
                named color (e.g. "0" or 1)
    :return: The name of a named color corresponding to the given index or name, or default_color if invalid.
    '''
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


def translate_color(col):
    '''
    :param col: The name of a named color (e.g. "white" or "Crimson"), or a hex color code
    :return: A hex color code (e.g. "#FF00FF") corresponding to the name/code if valid, or "#000000" otherwise.
    '''
    raise NotImplementedError()

