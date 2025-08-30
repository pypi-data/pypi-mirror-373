#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Model for Profile Link in the application"""

from typing import Optional, List

from pydantic import ConfigDict, Field

from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models.regscale_model import RegScaleModel


class ProfileLink(RegScaleModel):
    """
    Profile Mapping Model
    """

    _module_slug = "profileLinks"

    id: int
    profileId: int
    linkDate: Optional[str] = Field(default_factory=get_current_datetime)
    parentId: int
    parentModule: Optional[str] = None
    tenantsId: Optional[int] = None
    createdById: Optional[str] = None
    dateCreated: Optional[str] = Field(default_factory=get_current_datetime)
    dateLastUpdated: Optional[str] = Field(default_factory=get_current_datetime)
    isPublic: bool = False
    lastUpdatedById: Optional[str] = None

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the ProfileMapping model, using {model_slug} as a placeholder for the model slug.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """

        return ConfigDict(  # type: ignore
            get_all_by_parent="/api/{model_slug}/getProfiles/{strModule}/{intParentID}",
        )

    @classmethod
    def get_all_by_parent(cls, parent_id: int, parent_module: str) -> List["ProfileLink"]:
        """
        Get a list of objects by parent.
        # TODO: Update API to return needed data

        :param int parent_id: The ID of the parent
        :param str parent_module: The module of the parent
        :return: A list of profile links
        :rtype: List["ProfileLink]
        """
        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("get_all_by_parent").format(
                intParentID=parent_id,
                strModule=parent_module,
            )
        )
        records = []
        for obj in response.json():
            obj["parentModule"] = parent_module
            obj["parentId"] = parent_id
            obj["profileId"] = obj["profile"]["id"]
            records.append(cls(**obj))
        return records
