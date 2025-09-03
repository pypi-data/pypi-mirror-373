#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dataclass for Implementation Objective in the application"""
import logging
import uuid
from dataclasses import asdict
from enum import Enum
from logging import Logger
from typing import Any, Optional, Union, Dict

import requests
from pydantic import Field, ConfigDict
from requests import Response

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models.regscale_model import RegScaleModel


logger = logging.getLogger("regscale")


class ImplementationStatus(str, Enum):
    """
    Implementation Status
    :param Enum: Enum
    """

    FULLY_IMPLEMENTED = "Fully Implemented"
    PARTIALLY_IMPLEMENTED = "Partially Implemented"
    NOT_IMPLEMENTED = "Not Implemented"


class ImplementationObjectiveResponsibility(str, Enum):
    """
    Responsibility Enum
    :param Enum: Enum
    """

    PROVIDER = "Provider"
    PROVIDER_SYSTEM_SPECIFIC = "Provider (System Specific)"
    HYBRID = "Hybrid"
    CUSTOMER = "Customer"
    CUSTOMER_CONFIGURED = "Customer Configured"
    SHARED = "Shared"
    INHERITED = "Inherited"
    NOT_APPLICABLE = "Not Applicable"


class ImplementationObjective(RegScaleModel):
    """
    RegScale Implementation Objective
    Represents a row in the ImplementationObjectives table in the database.

    Relationships:
    - ImplementationId -> ControlImplementation (1:1)
    - ObjectiveId -> ControlObjective (0..1:1) [optional]
    - OptionId -> ImplementationOption (1:1)
    - SecurityControlId -> SecurityControls (0..1:1) [optional]
    - CreatedBy, LastUpdatedBy -> AspNetUsers (1:1) [FKs]
    - TenantsId -> Tenants (1:1) [inherited]
    - AuthorizationId -> LeveragedAuthorizations (0..1:1) [optional]
    """

    _module_slug = "implementationObjectives"
    _get_objects_for_list = True  # TODO: Fix API to return securityControlId
    _unique_fields = [
        ["implementationId", "objectiveId"],
    ]
    _parent_id_field = "implementationId"

    id: int = 0
    securityControlId: int
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))  # Required
    notes: Optional[str] = None
    implementationId: int  # Required, FK to ControlImplementation
    optionId: Optional[int] = None  # no longer Required, FK to ImplementationOption
    inherited: Optional[bool] = False
    status: Optional[Union[str, ImplementationStatus]] = ImplementationStatus.NOT_IMPLEMENTED  # Not Required
    objectiveId: Optional[int] = None  # Optional, FK to ControlObjective
    createdById: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    lastUpdatedById: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    # statement Should be required, represents the implementation statement
    statement: Optional[str] = None
    dateLastAssessed: str = Field(default_factory=get_current_datetime)  # Required
    dateCreated: str = Field(default_factory=get_current_datetime)  # Required
    dateLastUpdated: str = Field(default_factory=get_current_datetime)  # Required
    isPublic: bool = True  # Required
    parentObjectiveId: Optional[int] = None
    authorizationId: Optional[int] = None
    responsibility: Optional[str] = None
    cloudResponsibility: Optional[str] = None
    customerResponsibility: Optional[str] = None

    def __init__(self, **data: Any):
        # returned by bad api values for securityControlId corrected with validator
        # Map 'controlId' to 'securityControlId' internally
        if "controlId" in data:
            data["securityControlId"] = data.pop("controlId")
        super().__init__(**data)

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the ImplementationObjectives model, using {model_slug} as a placeholder for the model slug.

        :return: Additional endpoints for the ImplementationObjective
        :rtype: ConfigDict
        """
        return ConfigDict(  # type: ignore
            get_all_by_parent="/api/{model_slug}/getByControl/{intParentID}",
            get_by_control="/api/{model_slug}/getByControl/{intControl}",
            get_assessment="/api/{model_slug}/getAssessment/{intControl}/{intObjective}",
            batch_create="/api/{model_slug}/batchCreate",
            merge="/api/{model_slug}/merge/{implementationID}/{securityControlID}",
        )

    @classmethod
    def merge_objectives(cls, implementationId: int, securityControlId: int) -> Dict:
        """
        Merge objectives for a given implementation and security control

        :param int implementationId: Implementation ID
        :param int securityControlId: Security Control ID
        :return: Merged objectives
        :rtype: Dict
        """

        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("merge").format(
                implementationID=implementationId, securityControlID=securityControlId
            )
        )
        if response and response.ok:
            return response.json()

    # pydantic provides __eq__ method
    def __eq__(self, other: "ImplementationObjective") -> bool:
        """
        Check if two ImplementationObjective objects are equal

        :param ImplementationObjective other: ImplementationObjective object to compare to
        :return: True if equal, False if not equal
        :rtype: bool
        """
        if isinstance(other, ImplementationObjective):
            return (
                getattr(self, "notes", None) == getattr(other, "notes", None)
                and getattr(self, "implementationId", None) == getattr(other, "implementationId", None)
                and getattr(self, "objectiveId", None) == getattr(other, "objectiveId", None)
                and getattr(self, "optionId", None) == getattr(other, "optionId", None)
                and getattr(self, "statement", None) == getattr(other, "statement", None)
            )
        return False

    def __hash__(self) -> hash:
        """
        Hash a ImplementationObjective object

        :return: Hash of ImplementationObjective object
        :rtype: hash
        """
        return hash((self.implementationId, self.objectiveId))

    @classmethod
    def get_by_control(
        cls,
        implementation_id: int,
    ) -> list["ImplementationObjective"]:
        """
        Get a list of implementation options by control id and security plan id

        :param int implementation_id: Implementation Control ID
        :return: A list of implementation options
        :rtype: list[ImplementationObjective]
        """
        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("get_by_control").format(intControl=implementation_id),
        )
        if response and response.ok:
            return [cls(**obj) for obj in response.json()]
        return []

    @property
    def logger(self) -> Logger:
        """
        Logger implementation for a dataclass

        :return: logger object
        :rtype: Logger
        """
        logger = create_logger()
        return logger

    @staticmethod
    def fetch_by_security_control(
        app: Application,
        security_control_id: int,
    ) -> list["ImplementationObjective"]:
        """
        Fetch list of all implementation objectives in RegScale via API

        :param Application app: Application Instance
        :param int security_control_id: Security Control ID # in RegScale
        :return: List of security controls from RegScale
        :rtype: list[ImplementationObjective]
        """
        api = Api()
        logger = create_logger()
        query = """
                    query {
            implementationObjectives  (
                take: 50,
                skip: 0,
                where: { securityControlId:  {eq: placeholder }, })
                {
                items {
                    id,
                    uuid,
                    notes,
                    optionId,
                    implementationId,
                    securityControlId,
                    objectiveId,
                    status
                    }
                totalCount
                pageInfo {
                    hasNextPage
                }
            }
                }
            """.replace(
            "placeholder", str(security_control_id)
        )
        results = []
        data = api.graph(query=query)
        if "implementationObjectives" in data.keys():
            try:
                results.extend(data["implementationObjectives"]["items"])
            except requests.exceptions.JSONDecodeError:
                logger.warning(
                    "Unable to find control implementation objectives for control %i.",
                    security_control_id,
                )
        return [ImplementationObjective(**obj) for obj in results]

    @staticmethod
    def update_objective(
        app: Application,
        obj: Any,
    ) -> Response:
        """
        Update a single implementation objective

        :param Application app: Application Instance
        :param Any obj: Implementation Objective
        :return: Response from RegScale API
        :rtype: Response
        """
        if isinstance(obj, ImplementationObjective):
            obj = asdict(obj)
        api = Api(retry=10)
        return api.put(
            url=app.config["domain"] + f"/api/implementationObjectives/{obj['id']}",
            json=obj,
        )

    @staticmethod
    def insert_objective(
        app: Application,
        obj: Any,
    ) -> Response:
        """
        Update a single implementation objective

        :param Application app: Application Instance
        :param Any obj: Implementation Objective
        :return: Response from RegScale API
        :rtype: Response
        """
        if isinstance(obj, ImplementationObjective):
            obj = asdict(obj)
        api = Api(retry=10)
        res = api.post(url=app.config["domain"] + "/api/implementationObjectives", json=obj)
        return res

    @classmethod
    def fetch_implementation_objectives(
        cls, app: Application, control_id: int, query_type: Optional[str] = "implementation"
    ) -> list[dict]:
        """
        Fetch list of implementation objectives by control id

        :param Application app: Application Instance
        :param int control_id: Implementation Control ID
        :param Optional[str] query_type: Query Type for GraphQL query
        :return: A list of Implementation Objectives as a dictionary
        :rtype: list[dict]
        """
        graph_query = """
                        query {
                        implementationObjectives (skip: 0, take: 50,  where: {securityControlId: {eq: placeholder}}) {
                            items {
                                    id
                                    notes
                                    optionId
                                    objectiveId
                                    implementationId
                                    securityControlId
                                    status
                            }
                            totalCount
                                pageInfo {
                                    hasNextPage
                                }
                        }
                    }
                        """.replace(
            "placeholder", str(control_id)
        )
        results: list[Any] = []
        api = Api()
        if query_type != "implementation":
            results = cls._get_api_handler().graph(graph_query)
        else:
            res = api.get(url=app.config["domain"] + f"/api/implementationObjectives/getByControl/{control_id}")
            if res.ok:
                try:
                    results = res.json()
                except requests.exceptions.JSONDecodeError:
                    logger.warning("Unable to find control implementation objectives.")
        return results
