#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dataclass for Objective in the application"""

from dataclasses import dataclass


@dataclass
class Objective:
    """RegScale Base Objective"""

    securityControlId: int
    id: int
    uuid: str
