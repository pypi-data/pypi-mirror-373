"""
This module contains utility functions for working with dictionaries.
"""

from typing import Dict, List, Tuple, Any, Optional


def get_value(data: dict, key: str) -> Any:
    """
    Get a value from a dictionary even if nested dict using dot notation.
    If the value is within a list, return a list of values. (e.g. "key1.key2" -> {key1: {key2: value2}}) -> value2
    also fetches values from nested lists. (e.g. "key1.key2" -> {key1: [{key2: value2}, {key2: value3}]} -> [value2, value3])
    :param dict data: The dictionary to get the value from.
    :param str key: The key to get the value for.
    :return: The value from the dictionary or None if the key is not found.
    :rtype: Any
    """
    keys = key.split(".")
    value = data
    for k in keys:
        if isinstance(value, list):
            value = [item.get(k, None) if isinstance(item, dict) else None for item in value]
        elif isinstance(value, dict):
            value = value.get(k, None)
        else:
            return None
        if value and any(isinstance(i, list) for i in value):
            value = [item for sublist in value for item in sublist if item is not None]
    return value


def flatten_dict(
    d: Dict[str, Any], prefix: str = "", result: Optional[List[Tuple[str, Any]]] = None
) -> List[Tuple[str, Any]]:
    """
    Recursively flattens a nested dictionary or list of dictionaries into a list of tuples,
    preserving the hierarchy in the keys.

    :param Dict[str, Any] d: The dictionary or list of dictionaries to flatten.
    :param str prefix: The current prefix representing the hierarchy of keys, defaults to an empty string.
    :param Optional[List[Tuple[str, Any]]] result: The accumulated list of tuples, This is used internally and should
        not be set by the caller. defaults to None.
    :return: A list of tuples where each tuple is a key-value pair, with the key representing the hierarchical path.
    :rtype: List[Tuple[str, Any]]
    """
    if result is None:
        result = []
    if isinstance(d, dict):
        for key, value in d.items():
            new_key = f"{prefix}{key}" if prefix else key
            if isinstance(value, (dict, list)):
                flatten_dict(value, f"{new_key}.", result)
            else:
                result.append((new_key, value))
    elif isinstance(d, list):
        for index, item in enumerate(d):
            flatten_dict(item, f"{prefix}{index}.", result)

    return result
