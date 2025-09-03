"""Provide utility functions for dealing with lists."""

from typing import Any, Tuple


def add_and_return_unique(*lists: Tuple[Any]) -> list:  # noqa: DOC103
    """Add lists together and return a list of unique elements

    :param Tuple[Any] *lists: lists to add together
    :return: a list of unique elements
    :rtype: list
    """
    unique_elements = set()
    for lst in lists:
        unique_elements.update(lst)
    return list(unique_elements)
