#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Model for Control Parameter in the application"""
import warnings
from typing import Optional, List
from urllib.parse import urljoin

from pydantic import Field, ConfigDict

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.utils.api_handler import APIInsertionError
from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models.regscale_model import RegScaleModel


class ControlParameter(RegScaleModel):
    """
    ControlParameter class
    """

    _module_slug = "controlParameters"
    _module_string = "controlparameter"
    _unique_fields = [
        ["parameterId", "securityControlId"],
    ]

    id: Optional[int] = 0
    uuid: Optional[str] = None
    text: str = ""
    parameterId: Optional[str] = None
    otherId: Optional[str] = None
    securityControlId: Optional[int] = None
    archived: bool = False
    createdById: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    dateCreated: Optional[str] = Field(default_factory=get_current_datetime)
    lastUpdatedById: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    dateLastUpdated: Optional[str] = Field(default_factory=get_current_datetime)
    tenantsId: Optional[int] = 1
    dataType: Optional[str] = None
    isPublic: bool = True
    default: Optional[str] = None
    displayName: str = ""

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the ControlParameter

        :return: Additional endpoints for the ControlParameter
        :rtype: ConfigDict
        """
        return ConfigDict(  # type: ignore
            get_all_by_parent="/api/{model_slug}/getByControl/{intParentID}",
            get_by_control="/api/{model_slug}/getByControl/{id}",
            create="/api/{model_slug}",
            batch_create="/api/{model_slug}/batchCreate",
        )

    @classmethod
    def get_by_control(cls, control_id: int) -> Optional[List["ControlParameter"]]:
        """
        Get a list of control parameters by control ID
        :param int control_id:
        :return: Optional[List["ControlParameter"]]
        :rtype: Optional[List["ControlParameter"]]
        """
        endpoint = cls.get_endpoint("get_by_control").format(id=control_id)
        response = cls._get_api_handler().get(endpoint=endpoint)
        if response and response.ok:
            return [cls(**item) for item in response.json()]
        return None

    def insert_parameter(self, app: Application) -> dict:
        """
        DEPRECATED: Insert a new control parameter

        :param Application app: Application object
        :raises APIInsertionError: If the API request fails
        :return: JSON response as a dictionary
        :rtype: dict
        """
        warnings.warn(
            "The 'insert_parameter' method is deprecated, use 'create' method instead",
            DeprecationWarning,
        )

        # Convert the model to a dictionary
        api = Api()
        data = self.dict()
        api_url = urljoin(app.config["domain"], "/api/controlparameters")
        # Make the API call
        response = api.post(api_url, json=data)

        # Check the response
        if not response.ok:
            print(response.text)
            raise APIInsertionError(f"API request failed with status {response.status_code}")

        return response.json()
