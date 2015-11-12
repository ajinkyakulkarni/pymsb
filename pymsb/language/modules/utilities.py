import xml.etree.ElementTree as ET
import itertools
import pkg_resources

# Colors  TODO: add the actual colors, and find out what's going on with the MSB documentation on colors
COLOR_TRANSLATION = {
    "black": "#000000",
    "blue": "#0000FF",
    "cyan": "#00FFFF",
    "gray": "#888888",
    "green": "#00FF00",
    "magenta": "#FF00FF",
    "red": "#FF0000",
    "white": "#FFFFFF",
    "yellow": "#FFFF00"
}

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
            readonly = bool(field.get("readonly", False))  # if readonly is any non-empty string, then considered read-only
            obj_info["fields"][name] = readonly
    e = child.find("events")
    if e is not None:
        for event in e:
            obj_info["events"].add(event.get("name"))
    obj_infos[child.get("name")] = obj_info


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
