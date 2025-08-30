#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Model for Inheritance in the application"""

from typing import Optional, Union

from pydantic import ConfigDict, Field, field_validator

from regscale.core.app.api import Api
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models.regscale_model import RegScaleModel


class Inheritance(RegScaleModel):
    """
    Inherited Control model
    """

    _module_slug = "inheritance"

    id: int = 0
    recordId: int = 0
    recordModule: str
    policyId: Optional[int] = None
    planId: Optional[int] = None
    dateInherited: Optional[str] = Field(default_factory=get_current_datetime)

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

    ## Note: There are no endpoints in this module for
    # get (get_object)
    # post (save/update)
