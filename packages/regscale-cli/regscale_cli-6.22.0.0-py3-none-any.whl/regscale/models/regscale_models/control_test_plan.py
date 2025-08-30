#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Model for Control Test Plan in the application"""
import warnings
from typing import Optional
from urllib.parse import urljoin

from pydantic import ConfigDict

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.utils.api_handler import APIInsertionError
from regscale.models.regscale_models.regscale_model import RegScaleModel


class ControlTestPlan(RegScaleModel):
    """
    ControlTestPlan class
    """

    _module_slug = "controlTestPlans"
    _module_string = "controltestplan"

    id: int = 0
    uuid: Optional[str] = None
    test: Optional[str] = None
    testId: Optional[str] = None
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
        Get additional endpoints for the ControlTestPlan

        :return: Additional endpoints for the ControlTestPlan
        :rtype: ConfigDict
        """
        return ConfigDict(  # type: ignore
            get_all_by_parent="/api/{model_slug}/getByControl/{intParentID}",
        )

    def insert_controltestplan(self, app: Application) -> dict:
        """
        Insert a ControlTestPlan into the database

        :param Application app: Application object
        :raises APIInsertionError: API request failed
        :return: JSON response
        :rtype: dict
        """
        warnings.warn(
            "The 'insert_controltestplan' method is deprecated, use 'create' method instead",
            DeprecationWarning,
        )

        # Convert the model to a dictionary
        api = Api()
        data = self.dict()
        api_url = urljoin(app.config["domain"], "/api/controltestplans")
        # Make the API call
        response = api.post(api_url, json=data)

        # Check the response
        if not response.ok:
            print(response.text)
            raise APIInsertionError(f"API request failed with status {response.status_code}")

        return response.json()
