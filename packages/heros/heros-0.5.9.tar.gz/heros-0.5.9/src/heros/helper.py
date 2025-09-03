import re
import logging


log = logging.Logger("heros")


def object_name_from_keyexpr(key_expr, ns_objects, realm, endpoint=".*"):
    return re.search(f"{ns_objects}/{realm}/(.*?)/{endpoint}", key_expr).groups()[0]


def full_classname(o):
    """
    Return the fully qualified class name of an object.

    Args:
        o: object

    Returns:
        fully qualified module and class name
    """
    cl = o.__class__
    mod = cl.__module__
    if mod == "__builtin__":
        return cl.__name__  # avoid outputs like '__builtin__.str'
    return ".".join([mod, cl.__name__])
