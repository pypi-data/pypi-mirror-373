#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Model for Control Parameter in the application"""
from typing import Optional

from pydantic import ConfigDict

from regscale.models.regscale_models.regscale_model import RegScaleModel


class CCI(RegScaleModel):
    """
    CCI class
    """

    _module_slug = "cci"
    _unique_fields = [
        ["parameterId", "securityControlId"],
    ]

    id: Optional[int] = 0
    uuid: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    controlType: Optional[str] = None
    publishDate: Optional[str] = None
    securityControlId: Optional[int] = None
    archived: bool = False
    createdById: Optional[str] = None
    dateCreated: Optional[str] = None
    lastUpdatedById: Optional[str] = None
    dateLastUpdated: Optional[str] = None
    tenantsId: Optional[int] = None
    isPublic: bool = True

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the ControlParameter

        :return: Additional endpoints for the ControlParameter
        :rtype: ConfigDict
        """
        return ConfigDict(  # type: ignore
            get_all_by_parent="/api/{model_slug}/getByControl/{intParentID}",
        )
