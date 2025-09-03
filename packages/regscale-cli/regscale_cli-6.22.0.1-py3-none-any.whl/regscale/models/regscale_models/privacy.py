#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regscale Model for Privacy in the application"""

from enum import Enum
from typing import Optional, List

from pydantic import ConfigDict
from pydantic import Field

from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models.regscale_model import RegScaleModel


class PrivacyDataTypes(Enum):
    STRING = "string"
    INTEGER = "integer"
    DATE = "date"
    BOOLEAN = "boolean"
    ARRAY = "array"


class Privacy(RegScaleModel):
    """
    RegScale Privacy record
    Represents a row in the Policy table in the database.

    Relationships:
    - securityPlanId -> Security Plan (1:1)
    - CreatedById, LastUpdatedById -> AspNetUsers (1:1) [FKs]
    - TenantsId -> Tenants (1:1) [inherited]
    """

    _module_slug = "privacy"

    id: Optional[int] = 0
    isPublic: Optional[bool] = True
    uuid: Optional[str] = None
    uniqueIdentifier: Optional[str] = None
    piiCollection: str = Field(default="No", alias="piiCollection")
    piiPublicCollection: str = Field(default="No", alias="piiPublicCollection")
    piaConducted: str = Field(default="No", alias="piaConducted")
    sornExists: str = Field(default="No", alias="sornExists")
    sornId: Optional[str] = None
    ombControlId: Optional[str] = None
    infoCollected: Optional[str] = None
    justification: Optional[str] = None
    businessUse: Optional[str] = None
    pointOfContactId: Optional[str] = None
    privacyOfficerId: Optional[str] = None
    informationSharing: Optional[str] = None
    consent: Optional[str] = None
    security: Optional[str] = None
    privacyActSystem: Optional[str] = None
    recordsSchedule: Optional[str] = None
    securityPlanId: Optional[int] = 0
    status: Optional[str] = None
    dateApproved: Optional[str] = None
    notes: Optional[str] = None

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the Policy model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(  # type: ignore
            get_all_by_parent="/api/{model_slug}/getAllByParent/{intSPID}",
            create="/api/{model_slug}",
            update="/api/{model_slug}/{ID}",
            delete="/api/{model_slug}/{ID}",
            get="/api/{model_slug}/{intID}",
        )

    @classmethod
    def get_all_by_parent(cls, security_plan_id: int) -> List["Privacy"]:
        """
        Get all privacy records by security plan ID.

        :param int security_plan_id: The ID of the security plan
        :return: A list of Privacy records
        :rtype: List["Privacy"]
        """
        res = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("get_all_by_parent").format(intSPID=security_plan_id)
        )
        return cls._handle_list_response(res)
