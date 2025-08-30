#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Model for a RegScale Component"""
import logging
from enum import Enum
from typing import Optional, Any, Union, List, cast, Dict

from pydantic import ConfigDict, Field
from requests import Response

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models.mixins.parent_cache import PlanCacheMixin
from regscale.models.regscale_models.regscale_model import RegScaleModel, T

logger = logging.getLogger(__name__)


class ComponentType(str, Enum):
    """Component Type Enum"""

    Hardware = "hardware"
    Software = "software"
    Service = "service"
    Policy = "policy"
    Process = "process"
    Procedure = "procedure"
    ComplianceArtifact = "compliance artifact"


class ComponentStatus(str, Enum):
    """Component Status Enum"""

    DraftPending = "Draft/Pending"
    Active = "Active"
    InactiveRetired = "Inactive/Retired"
    Cancelled = "Cancelled"
    UndergoingMajorModification = "Undergoing Major Modification"
    Other = "Other"


class ComponentList(RegScaleModel):
    id: Optional[int]
    title: Optional[str]
    status: Optional[str]
    exclude: Optional[bool]
    componentType: Optional[str]


class Component(RegScaleModel):
    """Component Model"""

    _module_slug = "components"
    _unique_fields = [
        ["title", "securityPlansId"],
    ]
    _parent_id_field = "securityPlansId"

    title: str
    description: str
    componentType: Union[ComponentType, str]
    status: Union[ComponentStatus, str] = ComponentStatus.Active
    id: int = 0
    securityPlansId: Optional[int] = None
    defaultAssessmentDays: int = 0
    purpose: Optional[str] = None
    cmmcAssetType: Optional[str] = None
    createdById: str = Field(default_factory=RegScaleModel.get_user_id)
    dateCreated: str = Field(default_factory=get_current_datetime)
    lastUpdatedById: str = Field(default_factory=RegScaleModel.get_user_id)
    dateLastUpdated: str = Field(default_factory=get_current_datetime)
    uuid: Optional[str] = None
    componentOwnerId: str = Field(default_factory=RegScaleModel.get_user_id)
    cmmcExclusion: bool = False
    externalId: Optional[str] = None
    isPublic: bool = True
    riskCategorization: Optional[str] = None

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the Components model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(  # type: ignore
            get_list="/api/{model_slug}/getList",
            get_all_by_parent="/api/{model_slug}/getAllByParent/{intParentID}",
            get_count="/api/{model_slug}/getCount",
            graph="/api/{model_slug}/graph",
            graph_by_date="/api/{model_slug}/graphByDate/{strGroupBy}",
            report="/api/{model_slug}/report/{strReport}",
            filter_components="/api/{model_slug}/filterComponents",
            filter_component_dashboard="/api/{model_slug}/filterComponentDashboard",
            query_by_custom_field="/api/{model_slug}/queryByCustomField/{strFieldName}/{strValue}",
            get="/api/{model_slug}/find/{id}",
            evidence="/api/{model_slug}/evidence/{intID}",
            find_by_guid="/api/{model_slug}/findByGUID/{strGUID}",
            find_by_external_id="/api/{model_slug}/findByExternalId/{strID}",
            get_titles="/api/{model_slug}/getTitles",
            main_dashboard="/api/{model_slug}/mainDashboard/{intYear}",
            component_dashboard="/api/{model_slug}/componentDashboard/{intYear}",
            oscal="/api/{model_slug}/oscal/{intID}",
            statusboard="/api/{model_slug}/statusboard/{intID}/{strSearch}/{intPage}/{pageSize}",
            emass_export="/api/{model_slug}/emassExport/{intID}",
            mega_api="/api/{model_slug}/megaAPI/{intId}",
        )

    def __eq__(self, other: "Component") -> bool:
        """
        Check if two Component objects are equal

        :param Component other: Component object to compare
        :return: True if equal, False if not
        :rtype: bool
        """
        return (
            self.title == other.title
            and self.description == other.description
            and self.componentType == other.componentType
        )

    def __hash__(self) -> int:
        """
        Hash a Component object

        :return: Hashed Component object
        :rtype: int
        """
        return hash((self.title, self.description, self.componentType))

    def __getitem__(self, key: Any) -> Any:
        """
        Get attribute from Pipeline

        :param Any key: Key to get value for
        :return: value of provided key
        :rtype: Any
        """
        if getattr(self, key) == "None":
            return None
        return getattr(self, key)

    def __setitem__(self, key: Any, value: Any) -> None:
        """
        Set attribute in Pipeline with provided key

        :param Any key: Key to change to provided value
        :param Any value: New value for provided Key
        :rtype: None
        """
        return setattr(self, key, value)

    @staticmethod
    def get_components_from_ssp(app: Application, ssp_id: int) -> list[dict]:
        """
        Get all components for a given SSP

        :param Application app: Application instance
        :param int ssp_id: RegScale SSP
        :return: List of component dictionaries
        :rtype: list[dict]
        """
        api = Api()
        existing_res = api.get(app.config["domain"] + f"/api/components/getAllByParent/{ssp_id}")
        existing_res.raise_for_status()
        return existing_res.json()

    @classmethod
    def get_map(cls, plan_id: int, key_field: str = "title") -> dict[str, "Component"]:
        """
        Get the component map for the component and cache it in Redis

        :param int plan_id: Security Plan ID
        :param str key_field: Key field to use, defaults to "componentId"
        :return: Component Map
        :rtype: dict[str, "Component"]
        """
        search_data = f"""query {{
            componentMappings(skip: 0, take: 50, where: {{component: {{securityPlansId: {{eq: {plan_id}}} }} }}) {{
                items {{
                id
                component {{
                    {cls.build_graphql_fields()}
                }}
                }}
                totalCount
                pageInfo {{
                hasNextPage
                }}
            }}
        }}"""
        response = cls._get_api_handler().graph(query=search_data)
        components = cast(List["Component"], cls._handle_graph_response(response, child="component"))
        return_components = {}
        for component in components:
            identifier = getattr(component, key_field, None)
            if identifier:
                return_components[identifier] = component

        return return_components

    @classmethod
    def get_list(cls) -> List[ComponentList]:  # type: ignore
        """
        Retrieves a list of items for the model.

        :return: A list of items or None
        :rtype: List[ComponentList]
        """
        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("get_list").format(model_slug=cls.get_module_slug())
        )
        if not response or response.status_code in [204, 404]:
            return []
        if response and response.ok:
            return [ComponentList(**item) for item in response.json()]
        return []

    @classmethod
    def filter_components(cls, params: Dict) -> List["Component"]:
        """
        Retrieves a list of items for the model.

        :param Dict params: The parameters to filter the components
        :return: A list of Components or None
        :rtype: List[Component]
        """
        response = cls._get_api_handler().post(
            endpoint=cls.get_endpoint("filter_components").format(
                model_slug=cls.get_module_slug(),
            ),
            data=params,
        )
        if not response or response.status_code in [204, 404]:
            return []
        if response and response.ok:
            items = response.json().get("items")
            return list(filter(None, [cls.get_object(object_id=item.get("id")) for item in items]))
        return []

    @classmethod
    def get_sort_position_dict(cls) -> dict:
        """
        Overrides the base method.

        :return: dict The sort position in the list of properties
        :rtype: dict
        """
        return {
            "id": 1,
            "title": 2,
            "description": 3,
            "purpose": 4,
            "componentType": 5,
            "status": 6,
            "defaultAssessmentDays": 7,
            "cmmcAssetType": 9,
            "cmmcExclusion": 10,
            "componentOwnerId": 11,
            "isPublic": 12,
            "tenantsId": 13,
            "securityPlansId": 14,
        }

    @classmethod
    def get_enum_values(cls, field_name: str) -> list:
        """
        Overrides the base method.

        :param str field_name: The property name to provide enum values for
        :return: list of strings
        :rtype: list
        """
        if field_name == "componentType":
            return [component_type.value for component_type in ComponentType]
        if field_name == "status":
            return [status.value for status in ComponentStatus]
        return cls.get_bool_enums(field_name)

    @classmethod
    def get_lookup_field(cls, field_name: str) -> str:
        """
        Overrides the base method.

        :param str field_name: The property name to provide enum values for
        :return: str the field name to look up
        :rtype: str
        """
        return "user" if field_name == "componentOwnerId" else ""

    @classmethod
    def is_date_field(cls, field_name: str) -> bool:
        """
        Overrides the base method.

        :param str field_name: The property name to provide enum values for
        :return: bool if the field should be formatted as a date
        :rtype: bool
        """
        return False

    @classmethod
    def create_new_connecting_model(cls, instance: Any) -> Any:
        """
        Overrides the base method.

        :param Any instance: The instance to create a new connecting model for when loading new records.
        :return Any:
        :rtype Any:
        """
        connecting_model = ComponentMapping(
            securityPlanId=instance.securityPlansId, componentId=instance.id, isPublic=instance.isPublic
        )
        return connecting_model.create()


class ComponentMapping(RegScaleModel, PlanCacheMixin["ComponentMapping"]):
    """Component Mapping Model"""

    _module_slug = "componentmapping"
    _unique_fields = [
        ["componentId", "securityPlanId"],
    ]

    componentId: int
    securityPlanId: int
    id: int = 0
    uuid: Optional[str] = None
    dateCreated: Optional[str] = None
    lastUpdatedById: Optional[str] = None
    dateLastUpdated: Optional[str] = None
    TenantId: Optional[int] = 1
    isPublic: bool = True

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the ComponentMappings model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(  # type: ignore
            find_mapping="/api/{model_slug}/findMappings/{intID}",
            get_mappings_as_components="/api/{model_slug}/getMappingsAsComponents/{intID}",
            get_mappings_as_security_plans="/api/{model_slug}/getMappingsAsSecurityPlans/{intID}",
        )

    def find_by_unique(self, **kwargs: dict) -> Optional["ComponentMapping"]:  # type: ignore
        """
        Find a ComponentMapping by its unique fields

        :param dict **kwargs: Additional Keyword Arguments
        :raises ValueError: If componentId or securityPlanId are not populated
        :return: ComponentMapping object, if found
        :rtype: Optional[ComponentMapping]
        """

        if not self.componentId or not self.securityPlanId:
            raise ValueError("Component ID and Security Plan ID are required")
        mappings: list[ComponentMapping] = self.find_mappings(self.securityPlanId)
        for mapping in mappings:
            # Check if all unique fields match
            all_fields_match = all(getattr(mapping, key) == getattr(self, key) for key in self._unique_fields)
            if all_fields_match:
                return mapping
        return None

    @classmethod
    def find_mappings(cls, security_plan_id: int) -> List[T]:
        """
        Find mappings for a given component

        :param int security_plan_id: Security Plan ID
        :return: List of mappings
        :rtype: List[T]
        """
        return cls._handle_list_response(
            cls._get_api_handler().get(
                cls.get_endpoint("get_mappings_as_components").format(
                    intID=security_plan_id,
                )
            ),
            security_plan_id=security_plan_id,
        )

    @classmethod
    def _handle_list_response(cls, response: Response, security_plan_id: int) -> List[T]:  # type: ignore
        """
        Handle list response

        :param Response response: Response from API
        :param int security_plan_id: Security Plan ID
        :return: List of ComponentMappings as RegScale model objects
        :rtype: List[T]
        """
        if not response or response.status_code in [204, 404]:
            return []
        if response.ok:
            json_response = response.json()
            if isinstance(json_response, dict):
                json_response = json_response.get("items", [])
            return cast(
                List[T],
                [cls(securityPlanId=security_plan_id, **o) for o in json_response],
            )
        else:
            logger.error(f"Failed to get {cls.get_module_slug()} for {cls.__name__}")
            return []
