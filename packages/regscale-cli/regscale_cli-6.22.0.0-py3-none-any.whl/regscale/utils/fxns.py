"""Provide utilities for dealing with functions."""

import inspect
from typing import Any, List


def get_callback_param(command: Any) -> List[str]:
    """
    Return a list of parameter names in the callback function of a command

    :param Any command: a function to get the parameters for
    :return: a list of parameter names
    :rtype: List[str]
    """
    callback = command.callback
    sig = inspect.signature(callback)
    return list(sig.parameters.keys())


def get_callback_defaults(command: Any) -> dict:
    """
    Return a dictionary of callback defaults.

    :param Any command: a function to get the defaults for
    :return: a dictionary of parameter names and their defaults
    :rtype: dict
    """
    callback = command.callback
    sig = inspect.signature(callback)
    return {name: param.default if param.default != param.empty else None for name, param in sig.parameters.items()}
