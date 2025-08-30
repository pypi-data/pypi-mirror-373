#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Model for Security Plan in the application"""

from typing import Optional, Union

from pydantic import ConfigDict, Field, field_validator

from regscale.core.app.api import Api
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models.regscale_model import RegScaleModel


class InheritedControl(RegScaleModel):
    """
    Inherited Control model
    """

    _module_slug = "inheritedControls"

    id: int = 0
    createdBy: Optional[str] = None
    createdById: Optional[str] = None
    dateCreated: Optional[str] = Field(default_factory=get_current_datetime)
    lastUpdatedById: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    dateLastUpdated: Optional[str] = Field(default_factory=get_current_datetime)
    isPublic: bool = True
    parentId: int = 0
    parentModule: str = ""
    baseControlId: int = 0
    inheritedControlId: int = 0

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the Inherited Controls model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(  # type: ignore
            get_all_by_parent="/api/{model_slug}/getAllByParent/{intParentID}/{strModule}",
            get_all_by_control="/api/{model_slug}/getAllByBaseControl/{control_id}",
        )

    @classmethod
    def get_all_by_control(cls, control_id: int) -> dict:
        """
        Fetch the Mega API data for the given SSP ID

        :param int ssp_id: RegScale SSP ID
        :return: Mega API data
        :rtype: dict
        """
        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("get_all_by_control").format(module_slug=cls._module_slug, control_id=control_id)
        )
        if not response.raise_for_status():
            return response.json()
        return {}
