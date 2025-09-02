import typing
from typing import Union

from lxml import objectify

from prosuite.utils.checks import str_is_none_or_empty


def try_get_from_oe(prop: str, object: objectify.ObjectifiedElement) -> Union[str, None]:
    try:
        return object[prop]
    except:
        return None


def try_get_from_str_dict(key: str, dictionary: dict, default_value: Union[int, float, str, None] = "") -> \
        Union[int, float, str, None]:
    """
    returns the value of the lookup element if it is available in the dict.
    if the lookup element is not in the dict, the default value is returned.
    """
    if key in dictionary.keys():
        return dictionary[key]
    return default_value


def to_bool(value: Union[str, bool, int, None] = None, default_value: bool = False) -> bool:
    """"
    treats "true" or "True" or 'yes' or 'Yes' or 1 or '1' as True (bool). Anything else returns False (bool)
    """
    if type(value) == bool:
        return value
    if type(value) == str:
        if str_is_none_or_empty(value):
            return default_value
        if value.upper() == 'TRUE' or value.upper() == 'YES' or value == '1':
            return True
        else:
            return False
    if type(value) == int:
        if value == 1:
            return True
        else:
            return False
    else:
        return default_value


def to_float(value: Union[str, int, float, None], default_value: float = 0) -> Union[float, None]:
    """
    :param value: value that gets converted to float type
    :param default_value: value that is returned in case the float conversion fails
    :return:
    """
    try:
        return float(value)
    except:
        return default_value


def to_int(value: Union[str, int, None], default_value: int = 0) -> Union[int, None]:
    """
    Tries to convert the input value to int. If conversion is not possible, returns the default value.

    :param value: value that gets converted to int type
    :param default_value: value that is returned in case the int conversion fails
    :return: int representation of the input value or 0
   """
    try:
        return int(value)
    except:
        return default_value


def get_value_or_default(value: typing.Any, default: typing.Any) -> typing.Any:
    """
    Returns the value if it is not None. Else returns the default value.
    """
    if value:
        return value
    return default
