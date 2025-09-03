"""
    Provide common tools for string handling
"""
import re
import random
import string
from unidecode import unidecode


def force_ascii(value):
    """
    Return enforced ascii string
    éko=>ko
    """
    if isinstance(value, bytes):
        value = force_string(value)
    elif not isinstance(value, str):
        # Supports numbers, for instance
        value = str(value)
    value = unidecode(value)
    return value


def force_string(value):
    """
    return an utf-8 str

    :param bytes value: The original value to convert
    :rtype: str
    """
    if isinstance(value, bytes):
        value = value.decode("utf-8")
    return value


force_unicode = force_string


def camel_case_to_name(name):
    """
    Used to convert a classname to a lowercase name
    """

    def convert_func(m):
        return "_" + m.group(0).lower()

    return name[0].lower() + re.sub(r"([A-Z])", convert_func, name[1:])


def gen_random_string(size=15):
    """
    Generate random string

        size

            size of the resulting string
    """
    return "".join(random.choice(string.ascii_lowercase) for _ in range(size))


def to_utf8(datas):
    """
    Force utf8 string entries in the given datas
    """
    res = datas
    if isinstance(datas, dict):
        res = {}
        for key, value in datas.items():
            key = to_utf8(key)
            value = to_utf8(value)
            res[key] = value

    elif isinstance(datas, (list, tuple)):
        res = []
        for data in datas:
            res.append(to_utf8(data))

    elif isinstance(datas, str):
        res = datas.encode("utf-8")

    return res


def force_filename(val):
    """
    Transform a string to a valid filename
    """
    result = force_ascii(val)
    result = result.replace(" ", "_")

    valid_chars = "-_.%s%s" % (string.ascii_letters, string.digits)
    result = "".join((char for char in result if char in valid_chars))

    return result
