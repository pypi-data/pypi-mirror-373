
from .internal import (
    _str2bool,
)


def str2bool(s):
    """
    Determines the "truthy" nature of whether the given string is "truthy"
    and, if so, whether it is "falsey" or "truey".

    Returns
    -------
        - `None` - string is not classified as "truthy";
        - `False` - string is classified as "truthy" and is deemed "falsey";
        - `True` - string is classified as "truthy" and is deemed "truey";
    """

    return _str2bool(s)


def string_is_falsey(s):
    """
    Indicates that the given string, when trimmed, is classified as "truthy"
    and is deemed as "falsey".

    Note
    ----
        `string_is_falsey(x) == !string_is_truey(x)` is NOT guaranteed.
    """

    return _str2bool(s) == False


def string_is_truey(s):
    """
    Indicates that the given string, when trimmed, is classified as "truthy"
    and is deemed as "truey".

    Note
    ----
        `string_is_falsey(x) == !string_is_truey(x)` is NOT guaranteed.
    """

    return _str2bool(s) == True


def string_is_truthy(s):
    """
    Indicates that the given string, when trimmed, is classified as "truthy"
    (and is deemed as either "falsey" or "truey").

    Returns
    -------
        - `False` - string is not classified as "truthy";
        - `True` - string is deemed "truey";
    """

    return _str2bool(s) is not None
