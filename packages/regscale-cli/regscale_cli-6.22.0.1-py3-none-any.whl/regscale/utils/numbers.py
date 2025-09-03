"""Define functions relating to numbers"""

from typing import Any


def is_number(value: Any) -> bool:
    """Determine if a value is a number
    :param Any value: value to check
    :return: whether the value is a number
    :rtype: bool
    """
    return isinstance(value, (int, float, complex))
