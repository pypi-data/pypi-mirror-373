"""
App decorators
"""

import warnings
import functools


def deprecated(reason="This method is deprecated and may be removed in a future version."):
    """
    Decorator to mark functions as deprecated.

    :param reason: The reason for deprecation.
    """

    def decorator(func):
        """
        Decorator to mark functions as deprecated.
        :param func:
        :return:
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """
            Wrapper function to mark functions as deprecated.
            :param args:
            :param kwargs:
            :return:
            """
            warnings.warn(f"{func.__name__} is deprecated: {reason}", category=DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)

        return wrapper

    return decorator


class classproperty:  # pylint: disable=invalid-name # noqa: N801
    """
    A class property decorator.
    """

    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        return self.func(owner)
