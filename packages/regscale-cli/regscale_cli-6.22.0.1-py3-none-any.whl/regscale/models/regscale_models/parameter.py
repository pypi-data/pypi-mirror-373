#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regscale Model for Implementation Parameter in the application"""

from enum import Enum
from typing import List, Optional

from pydantic import ConfigDict, Field

from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models.regscale_model import RegScaleModel


class ParameterDataTypes(Enum):
    STRING = "string"
    INTEGER = "integer"
    DATE = "date"
    BOOLEAN = "boolean"
    ARRAY = "array"


class Parameter(RegScaleModel):
    """
    RegScale Implementation Parameter
    Represents a row in the Parameter table in the database.

    Relationships:
    - ControlImplementationId -> ControlImplementation (1:1)
    - CreatedById, LastUpdatedById -> AspNetUsers (1:1) [FKs]
    - ParentParameterId -> ControlParameter (0..1:1) [optional]
    - TenantsId -> Tenants (1:1) [inherited]
    """

    _module_slug = "parameters"

    id: Optional[int] = None
    uuid: Optional[str] = None
    name: str
    value: str
    controlImplementationId: int = Field(alias="controlImplementation")  # Required, FK to ControlImplementation
    createdById: str = Field(default_factory=RegScaleModel.get_user_id)  # FK to AspNetUsers
    dateCreated: str = Field(default_factory=get_current_datetime)  # Required
    lastUpdatedById: str = Field(default_factory=RegScaleModel.get_user_id)  # FK to AspNetUsers
    dateLastUpdated: str = Field(default_factory=get_current_datetime)  # Required
    tenantsId: Optional[int] = None  # Optional, FK to Tenants
    dataType: Optional[str] = None  # Optional
    externalPropertyName: Optional[str] = None  # Optional
    parentParameterId: Optional[int] = None  # Optional, FK to ControlParameter
    isPublic: bool = False  # Required, default to False

    oscalNamespaceMapping: Optional[List[str]] = None

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the Parameter model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(  # type: ignore
            get_all_by_parent="/api/{model_slug}/getAllByParent/{intParentID}",
            get_count="/api/{model_slug}/getCount",
            create="/api/{model_slug}",
            update="/api/{model_slug}/{id}",
            delete="/api/{model_slug}/{id}",
            get="/api/{model_slug}/find/{id}",
            find_by_guid="/api/{model_slug}/findByGUID/{strGUID}",
            merge="/api/{model_slug}/merge/{implementationID}/{securityControlID}",
        )

    @classmethod
    def get_by_parent_id(cls, parent_id: int) -> List["Parameter"]:
        """
        Get all Parameters by Parent ID.

        :param int parent_id: The Parent ID
        :return: A list of Parameters
        :rtype: List[Parameter]
        """
        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("get_all_by_parent").format(intParentID=parent_id)
        )
        if response and response.ok:
            return [Parameter(**param) for param in response.json()]
        return []

    @classmethod
    def merge_parameters(cls, implementation_id: int, security_control_id: int) -> List["Parameter"]:
        """
        Get a list of parameters by implementation ID and security control ID.

        :param int implementation_id: The ID of the controlImplementation
        :param int security_control_id: The ID of the security control
        :return: A list of parameters
        :rtype: List["Parameter"]
        """
        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("merge").format(
                implementationID=implementation_id,
                securityControlID=security_control_id,
            )
        )
        if response and response.ok:
            return [cls(**ci) for ci in response.json()]
        return []
