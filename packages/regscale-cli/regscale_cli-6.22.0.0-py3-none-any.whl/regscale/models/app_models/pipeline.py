#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dataclass for a user's pipeline"""

# standard python imports
from dataclasses import dataclass
from typing import Any


@dataclass
class Pipeline:
    """Pipeline Model"""

    email: str  # Required
    fullName: str = None
    pipelines: Any = None
    totalTasks: int = None
    analyzed: bool = False
    emailed: bool = False

    def __getitem__(self, key: Any) -> Any:
        """
        Get attribute from Pipeline
        :param Any key:
        :return: value of provided key
        :rtype: Any
        """
        return getattr(self, key)

    def __setitem__(self, key: Any, value: Any) -> None:
        """
        Set attribute in Pipeline with provided key
        :param Any key: Key to change to provided value
        :param Any value: New value for provided Key
        :rtype: None
        """
        return setattr(self, key, value)
