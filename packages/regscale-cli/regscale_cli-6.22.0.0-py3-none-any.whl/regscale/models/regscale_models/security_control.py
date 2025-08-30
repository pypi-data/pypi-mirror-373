#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dataclass for Security Control in the application"""

from typing import Any, List, Optional

from pydantic import Field, ConfigDict

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models.regscale_model import RegScaleModel


class SecurityControl(RegScaleModel):
    """Security Control

    :return: A RegScale Security Control instance
    """

    _module_slug = "SecurityControls"
    _module_str = "securitycontrol"
    _unique_fields = [
        ["controlId", "catalogueId"],
    ]
    _parent_id_field = "catalogueId"
    _exclude_graphql_fields = ["objectives", "tests", "parameters"]

    id: int = 0
    otherId: Optional[str] = None
    isPublic: bool = True
    uuid: Optional[str] = None
    controlId: Optional[str] = None
    sortId: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    controlType: Optional[str] = None
    references: Optional[str] = None
    relatedControls: Optional[str] = None
    subControls: Optional[str] = None
    enhancements: Optional[str] = None
    family: Optional[str] = None
    mappings: Optional[str] = None
    assessmentPlan: Optional[str] = None
    weight: float
    catalogueId: int = Field(..., alias="catalogueID")
    practiceLevel: Optional[str] = None
    objectives: Optional[List[object]] = None
    tests: Optional[List[object]] = None
    parameters: Optional[List[object]] = None
    archived: bool = False
    createdById: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    dateCreated: Optional[str] = Field(default_factory=get_current_datetime)
    lastUpdatedById: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    dateLastUpdated: Optional[str] = Field(default_factory=get_current_datetime)
    criticality: Optional[str] = None

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the SecurityControl

        :return: Additional endpoints for the SecurityControl
        :rtype: ConfigDict
        """
        return ConfigDict(
            get_all_by_parent="/api/{model_slug}/getAllByCatalog/{intParentID}",
            get_list="/api/{model_slug}/getList/{catalogId}",
        )

    def __hash__(self) -> hash:
        """
        Enable object to be hashable

        :return: Hashed SecurityControl
        :rtype: hash
        """
        return hash((self.controlId, self.catalogueId))

    def __eq__(self, other: "SecurityControl") -> bool:
        """
        Update items in SecurityControl class

        :param SecurityControl other: SecurityControl Object to compare to
        :return: Whether the two objects are equal
        :rtype: bool
        """
        return self.controlId == other.controlId and self.catalogueId == other.catalogueID

    @classmethod
    def get_list_by_catalog(cls, catalog_id: int) -> List["Catalog"]:
        """
        Get list of Security Controls for the provided Catalog ID

        :param int catalog_id: Catalog ID
        :return: list of catalogs
        :rtype: List["Catalog"]
        """
        return cls._handle_list_response(
            cls._get_api_handler().get(cls.get_endpoint("get_list").format(catalogId=catalog_id))
        )

    @staticmethod
    def lookup_control(
        app: Application,
        control_id: int,
    ) -> "SecurityControl":
        """
        Return a Security Control in RegScale via API

        :param Application app: Application Instance
        :param int control_id: ID of the Security Control to look up
        :return: A Security Control from RegScale
        :rtype: SecurityControl
        """
        api = Api()
        control = api.get(url=app.config["domain"] + f"/api/securitycontrols/{control_id}").json()
        return SecurityControl(**control)

    @staticmethod
    def lookup_control_by_name(app: Application, control_name: str, catalog_id: int) -> Optional["SecurityControl"]:
        """
        Lookup a Security Control by name and catalog ID

        :param Application app: Application instance
        :param str control_name: Name of the security control
        :param int catalog_id: Catalog ID for the security control
        :return: A Security Control from RegScale, if found
        :rtype: Optional[SecurityControl]
        """
        api = Api()
        config = api.config
        res = api.get(config["domain"] + f"/api/securitycontrols/findByUniqueId/{control_name}/{catalog_id}")
        return SecurityControl(**res.json()) if res.status_code == 200 else None

    @classmethod
    def get_controls_by_parent_id_and_module(
        cls, parent_id: int, parent_module: str, return_dicts: bool = False
    ) -> List["SecurityControl"]:
        """
        Get a list of Security Controls by parent ID and module using GraphQL

        :param int parent_id: The ID of the parent
        :param str parent_module: The module of the parent
        :param bool return_dicts: Whether to return the controls as a list of dicts, defaults to False
        :return: A list of Security Controls
        :rtype: List["SecurityControl"]
        """
        query = f"""
            query {{
            controlImplementations(skip: 0, take: 50, where:  {{
                parentId:  {{
                    eq: {parent_id}
                }},
                parentModule:  {{
                    eq: "{parent_module}"
                }}
                control:  {{
                    id:  {{
                    gt: 0
                    }}
                }}
            }}) {{
                items {{
                    control {{
                        {cls.build_graphql_fields(use_aliases=True)}
                    }}
                }}
                totalCount
                pageInfo {{
                    hasNextPage
                }}
            }}
        }}"""
        data = cls._get_api_handler().graph(query=query)
        controls = data.get("controlImplementations", {}).get("items", [])
        if return_dicts:
            return [control["control"] for control in controls if control.get("control")]
        return [cls(**control["control"]) for control in controls if control.get("control")]
