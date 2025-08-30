#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RegScale Implementation Option Model"""
import warnings
from typing import Optional, List
from urllib.parse import urljoin

import requests
from pydantic import Field, ConfigDict, model_validator, BaseModel

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models.implementation_objective import ImplementationStatus
from regscale.models.regscale_models.objective import Objective
from regscale.models.regscale_models.regscale_model import RegScaleModel
from regscale.models.regscale_models.search import Search


class ImplementationOption(RegScaleModel):
    """RegScale Implementation Option Model"""

    _module_slug = "implementationOptions"
    _unique_fields = [
        ["securityControlId", "name"],
    ]
    _parent_id_field = "securityControlId"

    id: int = Field(default=0)
    uuid: str = Field(default="")
    name: str = Field(..., description="Name of the implementation option")
    description: str = Field(..., description="Description of the implementation option")
    acceptability: str = Field(
        ImplementationStatus.NOT_IMPLEMENTED, description="Acceptability status of the implementation option"
    )
    otherId: Optional[str] = Field(default=None, description="An optional other identifier")
    securityControlId: Optional[int] = Field(default=None, description="Foreign Key SecurityControls.id")
    objectiveId: Optional[int] = Field(default=None, description="Foreign Key ControlObjective.id")
    archived: bool = Field(default=False, description="Archival status of the implementation option")
    createdById: Optional[str] = Field(default=None, description="Foreign Key AspNetUsers.id")
    dateCreated: str = Field(
        default_factory=get_current_datetime, description="Creation date of the implementation option"
    )
    lastUpdatedById: Optional[str] = Field(default=None, description="Foreign Key AspNetUsers.id")
    dateLastUpdated: str = Field(
        default_factory=get_current_datetime, description="Last update date of the implementation option"
    )
    tenantsId: Optional[int] = Field(default=None, description="Foreign Key Tenants.id")
    isPublic: bool = Field(default=False, description="Public visibility of the implementation option")
    restricted: bool = Field(default=False, description="Restriction status of the implementation option")
    restrictedSecurityPlanId: Optional[int] = Field(
        default=None, description="Associated restricted security plan ID if any"
    )
    responsibility: Optional[str] = Field(default=None, description="Who is responsible for the implementation option")

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the ImplementationOption model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(  # type: ignore
            get_all_by_parent="/api/{model_slug}/getByControl/{intParentID}/{securityPlanId}",
            get_by_control="/api/{model_slug}/getByControl/{intControl}/{securityPlanId}",
            batch_create="/api/{model_slug}/batchCreate",
        )

    @classmethod
    def get_all_by_parent(
        cls,
        parent_id: int,
        parent_module: Optional[str] = None,
        search: Optional[Search] = None,
        plan_id: Optional[int] = None,
    ) -> List["ImplementationOption"]:
        """
        Get a list of objects by parent.

        :param int parent_id: The ID of the parent
        :param Optional[str] parent_module: The parent module
        :param Optional[Search] search: The search object
        :param Optional[int] plan_id: The ID of the security plan
        :return: A list of objects
        :rtype: List["ImplementationOption"]
        """
        return cls._handle_list_response(
            cls._get_api_handler().get(
                endpoint=cls.get_endpoint("get_all_by_parent").format(
                    intParentID=parent_id,
                    securityPlanId=plan_id,
                )
            )
        )

    @classmethod
    def get_by_control(cls, security_control_id: int, security_plan_id: int) -> list["ImplementationOption"]:
        """
        Get a list of implementation options by control id and security plan id

        :param int security_control_id: Security Control ID
        :param int security_plan_id: Security Plan ID
        :return: A list of Implementation Options as a dictionary from RegScale via API
        :rtype: list[ImplementationOption]
        """
        return cls._handle_list_response(
            cls._get_api_handler().get(
                endpoint=cls.get_endpoint("get_by_control").format(
                    intControl=security_control_id, securityPlanId=security_plan_id
                ),
            )
        )


class ImplementationOptionDeprecated(BaseModel, Objective):
    """RegScale Implementation Option"""

    _module_slug = "implementationoptions"

    id: int = 0
    uuid: str = ""
    name: str  # Required
    description: str  # Required
    status: Optional[str] = None
    acceptability: Optional[str] = (
        None  # Required for create but not returned on get by control ??? api is inconsistent
    )
    otherId: Optional[str] = None
    securityControlId: Optional[int] = None
    objectiveId: Optional[int] = None
    restricted: bool = False
    restrictedSecurityPlanId: Optional[int] = None
    createdById: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    lastUpdatedById: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    dateCreated: str = Field(default_factory=get_current_datetime)
    dateLastUpdated: str = Field(default_factory=get_current_datetime)
    archived: bool = False
    isPublic: bool = True

    def __getitem__(
        self, other: "ImplementationOptionDeprecated"
    ) -> str:  # this allows getting an element (overrided method)
        return self.name and self.description and self.objectiveId and self.securityControlId

    @model_validator(mode="after")
    def correct_control_id(self):
        """
        Correct the acceptability value for the implementation option as it is not returned
        by the API on get by control but is return in field status which is not a valid field for the model
        """
        if self.acceptability is None and self.status is not None:
            self.acceptability = self.status

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the ImplementationOptions model, using {model_slug} as a placeholder for the model slug.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(  # type: ignore
            get_by_control="/api/{model_slug}/getByControl/{intControl}/{securityPlanId}",
            batch_create="/api/{model_slug}/batchCreate",
        )

    def __eq__(self, other: "ImplementationOptionDeprecated") -> bool:
        """
        Check if two ImplementationOption objects are equal

        :param ImplementationOptionDeprecated other: ImplementationOption object to compare
        :return: True if equal, False if not
        :rtype: bool
        """
        return (
            self.name == other.name
            and self.description == other.description
            and self.objectiveId == other.objectiveId
            and self.securityControlId == other.securityControlId
        )

    def __hash__(self) -> hash:
        """
        Hash a ImplementationOption object

        :return: Hashed ImplementationOption object
        :rtype: hash
        """
        return hash((self.name, self.description, self.objectiveId, self.securityControlId))

    @classmethod
    def get_by_control(cls, security_control_id: int, security_plan_id: int) -> list["ImplementationOption"]:
        """
        Get a list of implementation options by control id and security plan id

        :param int security_control_id: Security Control ID
        :param int security_plan_id: Security Plan ID
        :return: A list of Implementation Options as a dictionary from RegScale via API
        :rtype: list[ImplementationOption]
        """
        return cls._handle_list_response(
            cls._get_api_handler().get(
                endpoint=cls.get_endpoint("get_by_control").format(
                    intControl=security_control_id, securityPlanId=security_plan_id
                ),
            )
        )

    @staticmethod
    def fetch_implementation_options(app: Application, control_id: int) -> list["ImplementationOptionDeprecated"]:
        """
        Fetch list of implementation objectives by control id

        :param Application app: Application Instance
        :param int control_id: Security Control ID
        :return: A list of Implementation Objectives as a dictionary from RegScale via API
        :rtype: list[ImplementationOptionDeprecated]
        """
        warnings.warn(
            "The 'fetch_implemetation_options method is deprecated, use 'get_by_control' method instead",
            DeprecationWarning,
        )
        results = []
        logger = create_logger()
        api = Api()
        res = api.get(url=app.config["domain"] + f"/api/implementationoptions/getByControl/{control_id}")
        if res.ok:
            try:
                results = [ImplementationOptionDeprecated(**opt) for opt in res.json()]
            except requests.RequestException.JSONDecodeError:
                logger.warning("Unable to find control implementation objectives.")
        return results

    def insert(self, api: Api) -> requests.Response:
        """
        Insert implementation option into RegScale

        :param Api api: The API instance
        :return: API Response
        :rtype: requests.Response
        """
        warnings.warn(
            "The 'insert_parameter' method is deprecated, use 'create' method instead",
            DeprecationWarning,
        )
        response = api.post(
            url=urljoin(api.config["domain"], "/api/implementationOptions"),
            json=self.dict(),
        )
        api.logger.debug(
            "ImplementationOption insertion Response: %s=%s",
            response.status_code,
            response.text,
        )
        if response.status_code == 400 and "Duplicate" in response.text:
            #  rev 5 contains multiple parts for each control with implemention options
            #  there will be duplicates (which is ok)
            #  do not log a message.
            return response
        if response.status_code == 422 and "Duplicate" in response.text:
            #  rev 5 contains multiple parts for each control with implemention options
            #  there will be duplicates (which is ok)
            #  do not log a message.
            return response

        if not response.ok or response.status_code != 200:
            api.logger.error(
                "Unable to insert Implementation Option into RegScale.\n%s:%s %s",
                response.status_code,
                response.reason,
                response.text,
            )
        return response
