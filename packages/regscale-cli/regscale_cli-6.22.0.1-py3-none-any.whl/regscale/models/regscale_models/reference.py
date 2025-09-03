#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Provide References models."""
import warnings
from typing import List, Union, Optional

from pydantic import Field

from regscale.core.app.api import Api
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models.regscale_model import RegScaleModel


class Reference(RegScaleModel):
    """References model"""

    _module_slug = "references"

    id: int = 0
    createdById: str = ""  # this should be userID
    dateCreated: str = Field(default_factory=get_current_datetime)
    lastUpdatedById: str = ""  # this should be userID
    isPublic: bool = True
    identificationNumber: str = ""
    title: str = ""
    version: str = ""
    datePublished: str = Field(default_factory=get_current_datetime)
    referenceType: str = ""
    link: str = ""
    parentId: int = 0
    parentModule: str = ""
    dateLastUpdated: str = Field(default_factory=get_current_datetime)

    @staticmethod
    def create_references_from_list(
        parent_id: Union[str, int],
        references_list: List[dict],
        parent_module: Optional[str] = "securityplans",
    ) -> List[Union["Reference", bool]]:
        """
        Create a list of References objects from a list of dicts

        :param Union[str, int] parent_id: ID of the SSP to create the References objects for
        :param List[dict] references_list: List of dicts to create objects from
        :param Optional[str] parent_module: Parent module of the References objects, defaults to "securityplans"
        :return: List of References objects or False if unsuccessful
        :rtype: List[Union[Reference, bool]]
        """
        references = [
            Reference(parentId=int(parent_id), parentModule=parent_module, **references)
            for references in references_list
        ]
        response = []
        for reference in references:
            response.append(reference.create_new_references(return_object=True))
        return response

    def create_new_references(self, return_object: Optional[bool] = False) -> Union[bool, "Reference"]:
        """
        Create a new References object in RegScale

        :param Optional[bool] return_object: Return the References object if successful, defaults to False
        :return: True if successful, False otherwise
        :rtype: Union[bool, "Reference"]
        """
        warnings.warn(
            "The 'create_new_references' method is deprecated, use 'create' method instead",
            DeprecationWarning,
        )
        api = Api()
        data = self.dict()
        data["createdById"] = api.config["userId"]
        data["lastUpdatedById"] = api.config["userId"]
        references_response = api.post(
            f'{api.config["domain"]}/api/references/',
            json=data,
        )
        logger = create_logger()
        if references_response.ok:
            logger.info(f'Created References: {references_response.json()["id"]}')
            if return_object:
                return Reference(**references_response.json())
            return True
        logger.error(f"Error creating References: {references_response.text}")
        return False
