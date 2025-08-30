#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Qualys Integration Variables"""

from regscale.integrations.variables import RsVariablesMeta, RsVariableType


class QualysVariables(metaclass=RsVariablesMeta):
    """
    Qualys Variables class to define class-level attributes with type annotations and examples
    """

    # API Connection Settings
    qualysUserName: RsVariableType(str, "qualys_username")  # type: ignore
    qualysPassword: RsVariableType(str, "qualys_password", sensitive=True)  # type: ignore
    qualysUrl: RsVariableType(str, "https://qualysapi.qualys.com", default="https://qualysapi.qualys.com")  # type: ignore

    # Total Cloud Specific Settings
    totalCloudTagFilter: RsVariableType(str, "tag_name", required=False)  # type: ignore
    totalCloudIncludeTags: RsVariableType(str, "tag1,tag2,tag3", required=False)  # type: ignore
    totalCloudExcludeTags: RsVariableType(str, "tag1,tag2,tag3", required=False)  # type: ignore
