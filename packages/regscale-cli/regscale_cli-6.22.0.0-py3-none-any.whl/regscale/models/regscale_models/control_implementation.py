#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Model for a RegScale Security Control Implementation"""
# standard python imports
import logging
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union, TypeVar
from urllib.parse import urljoin

import requests
from lxml.etree import Element
from pydantic import ConfigDict, Field

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.core.app.utils.catalog_utils.common import parentheses_to_dot
from regscale.models.regscale_models.implementation_role import ImplementationRole
from regscale.models.regscale_models.regscale_model import RegScaleModel
from regscale.models.regscale_models.security_control import SecurityControl


logger = logging.getLogger("regscale")
PATCH_CONTENT_TYPE = "application/json-patch+json"


class ControlImplementationStatus(str, Enum):
    """Control Implementation Status"""

    FullyImplemented = "Fully Implemented"
    Implemented = "Implemented"
    NotImplemented = "Not Implemented"
    PartiallyImplemented = "Partially Implemented"
    InRemediation = "In Remediation"
    Inherited = "Inherited"
    NA = "Not Applicable"
    Planned = "Planned"
    Archived = "Archived"
    RiskAccepted = "Risk Accepted"
    Alternative = "Alternate Implementation"


class ImplementationControlOrigin(str, Enum):
    SERVICE_PROVIDER_CORPORATE = "Service Provider Corporate"
    SERVICE_PROVIDER_SYSTEM = "Service Provider System Specific"
    SERVICE_PROVIDER_HYBRID = "Service Provider Hybrid (Corporate and System Specific)"
    CONFIGURED_BY_CUSTOMER = "Configured by Customer (Customer System Specific)"
    PROVIDED_BY_CUSTOMER = "Provided by Customer (Customer Specific)"
    SHARED = "Shared (Service Provider and Customer Responsibility)"
    INHERITED_FROM_PRE_EXISTING_FEDRAMP_AUTHORIZATION = (
        "Inherited from pre-existing FedRAMP Authorization"  # noqa: E501
    )

    def __str__(self):
        return self.value


class ControlImplementationOrigin(str, Enum):
    """Control Origination"""

    Provider = "Provider"
    ProviderSS = "Provider (System Specific)"
    CustomerConfigured = "Customer Configured"
    CustomerProvided = "Customer"
    Inherited = "Inherited"


class ControlImplementation(RegScaleModel):
    """Control Implementation"""

    _module_slug = "controlImplementation"
    _module_string = "controls"
    _unique_fields = [["controlID", "parentId", "parentModule"]]
    _get_objects_for_list = True

    controlOwnerId: str = Field(default_factory=RegScaleModel.get_user_id)
    status: str  # Required
    controlID: int  # Required foreign key to Security Control
    status_lst: List[ControlImplementationStatus] = []
    id: int = 0
    parentId: Optional[int] = None
    parentModule: Optional[str] = None
    control: Union[SecurityControl, dict, None] = None  # Security Control object
    createdById: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    uuid: Optional[str] = None
    policy: Optional[str] = None
    implementation: Optional[str] = None
    dateLastAssessed: Optional[str] = None
    lastAssessmentResult: Optional[str] = None
    practiceLevel: Optional[str] = None
    processLevel: Optional[str] = None
    cyberFunction: Optional[str] = None
    implementationType: Optional[str] = None
    implementationMethod: Optional[str] = None
    qdWellDesigned: Optional[str] = None
    qdProcedures: Optional[str] = None
    qdSegregation: Optional[str] = None
    qdFlowdown: Optional[str] = None
    qdAutomated: Optional[str] = None
    qdOverall: Optional[str] = None
    qiResources: Optional[str] = None
    qiMaturity: Optional[str] = None
    qiReporting: Optional[str] = None
    qiVendorCompliance: Optional[str] = None
    qiIssues: Optional[str] = None
    qiOverall: Optional[str] = None
    responsibility: Optional[str] = None
    inheritedControlId: Optional[int] = None
    inheritedRequirementId: Optional[int] = None
    inheritedSecurityPlanId: Optional[int] = None
    inheritedPolicyId: Optional[int] = None
    dateCreated: Optional[str] = Field(default_factory=get_current_datetime)
    lastUpdatedById: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    dateLastUpdated: Optional[str] = Field(default_factory=get_current_datetime)
    weight: Optional[int] = None
    isPublic: Optional[bool] = True
    inheritable: Optional[bool] = False
    systemRoleId: Optional[int] = None
    plannedImplementationDate: Optional[str] = None
    stepsToImplement: Optional[str] = None
    exclusionJustification: Optional[str] = None
    bBaseline: Optional[bool] = False
    bInherited: Optional[bool] = False
    bOverlay: Optional[bool] = False
    bTailored: Optional[bool] = False
    bStatusImplemented: Optional[bool] = False
    bStatusPartiallyImplemented: Optional[bool] = False
    bStatusPlanned: Optional[bool] = False
    bStatusAlternative: Optional[bool] = False
    bStatusNotApplicable: Optional[bool] = False
    bServiceProviderCorporate: Optional[bool] = False
    bServiceProviderSystemSpecific: Optional[bool] = False
    bServiceProviderHybrid: Optional[bool] = False
    bConfiguredByCustomer: Optional[bool] = False
    bProvidedByCustomer: Optional[bool] = False
    bShared: Optional[bool] = False
    bInheritedFedrampAuthorization: Optional[bool] = False
    cloudImplementation: Optional[str] = None
    customerImplementation: Optional[str] = None
    controlSource: Optional[str] = "Baseline"
    maturityLevel: Optional[str] = None
    assessmentFrequency: int = 0

    def __str__(self):
        return f"Control Implementation {self.id}: {self.controlID}"

    def model_post_init(self, __context: Any) -> None:
        """
        Model post init method

        :param Any __context: The context
        :return: None
        """
        self.status_lst = self._get_status_enum()

    def __setattr__(self, name: str, value: Any) -> None:
        """
        Override __setattr__ to update status_lst when status changes.

        :param str name: The attribute name
        :param Any value: The attribute value
        :return: None
        """
        super().__setattr__(name, value)
        if name == "status":
            self.status_lst = self._get_status_enum()

    @classmethod
    def _get_additional_endpoints(cls) -> ConfigDict:
        """
        Get additional endpoints for the API.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(  # type: ignore
            get_all_count="/api/{model_slug}/getAllCount",
            get_filtered_list="/api/{model_slug}/getFilteredList/{str_find}",
            get_all_by_parent="/api/{model_slug}/getAllByParent/{intParentID}/{strModule}",
            get_all_by_plan="/api/{model_slug}/getAllByPlan/{int_security_plan}",
            get_all_by_plan_with_controls="/api/{model_slug}/getAllByPlanWithControls/{int_security_plan}",
            get_compliance_history_by_plan="/api/{model_slug}/GetComplianceHistoryByPlan/{int_parent}/{str_module}",
            save_compliance_history_by_plan="/api/{model_slug}/SaveComplianceHistoryByPlan",
            get_all_by_plan_with_objectives="/api/{model_slug}/getAllByPlanWithObjectives/{int_security_plan}",
            get_all_by_component_list="/api/{model_slug}/getAllByComponentList",
            get_mappings_by_security_plan="/api/{model_slug}/getMappingsBySecurityPlan/{int_security_plan}",
            get_list_by_plan="/api/{model_slug}/getListByPlan/{int_security_plan}",
            get_list_by_parent="/api/{model_slug}/getListByParent/{int_id}/{str_module}",
            get_master_assessment_list="/api/{model_slug}/getMasterAssessmentList/{int_parent}/{str_module}",
            get_list_by_parent_control="/api/{model_slug}/getListByParentControl/{parent_control_id}",
            get_sc_list_by_plan="/api/{model_slug}/getSCListByPlan/{int_security_plan}",
            get_inheritance_list_by_plan="/api/{model_slug}/getInheritanceListByPlan/{int_security_plan}",
            get_sc_list_by_component="/api/{model_slug}/getSCListByComponent/{int_component}",
            graph_main_dashboard="/api/{model_slug}/graphMainDashboard/{str_group_by}/{str_mod}",
            export="/api/{model_slug}/export/{int_id}",
            wizard="/api/{model_slug}/wizard/{int_id}/{str_module}",
            get_date_last_assessed_by_parent="/api/{model_slug}/getDateLastAssessedByParent/{int_record}",
            get_date_last_assessed_by_parent_and_module="/api/{model_slug}/getDateLastAssessedByParentAndModule/{str_module}/{int_record}",  # noqa: E501
            get_date_last_assessed_for_all_assets="/api/{model_slug}/getDateLastAssessedForAllAssets/{int_record}",
            graph_controls_by_date="/api/{model_slug}/graphControlsByDate/{year}",
            get_date_last_assessed_by_control="/api/{model_slug}/getDateLastAssessedByControl/{int_control}",
            get_by_status_and_parent="/api/{model_slug}/getByStatusAndParent/{int_id}",
            get_by_status_and_parent_control="/api/{model_slug}/getByStatusAndParentControl/{int_id}",
            get_by_owner_and_parent="/api/{model_slug}/getByOwnerAndParent/{int_id}",
            get_by_owner_and_parent_control="/api/{model_slug}/getByOwnerAndParentControl/{int_id}",
            get_by_result_and_parent="/api/{model_slug}/getByResultAndParent/{int_id}",
            get_by_result_and_parent_control="/api/{model_slug}/getByResultAndParentControl/{int_id}",
            get_by_process_and_parent="/api/{model_slug}/getByProcessAndParent/{int_id}",
            get_by_practice_and_parent="/api/{model_slug}/getByPracticeAndParent/{int_id}",
            get_by_practice_and_control="/api/{model_slug}/getByPracticeAndControl/{int_id}",
            get_by_process_and_control="/api/{model_slug}/getByProcessAndControl/{int_id}",
            graph="/api/{model_slug}/graph",
            filter_control_implementations="/api/{model_slug}/filterControlImplementations",
            filter_scorecard="/api/{model_slug}/filterScorecard",
            scorecard_count="/api/{model_slug}/ScorecardCount",
            query_by_custom_field="/api/{model_slug}/queryByCustomField/{str_field_name}/{str_value}",
            insert="/api/controlImplementation",
            batch_create="/api/{model_slug}/batchCreate",
            batch_update="/api/{model_slug}/batchUpdate",
            quick_update="/api/{model_slug}/quickUpdate/{id}/{str_status}/{int_weight}/{str_user}",
            dashboard_by_parent="/api/{model_slug}/dashboardByParent/{str_group_by}/{int_id}/{str_module}",
            security_control_dashboard="/api/{model_slug}/securityControlDashboard/{str_group_by}/{int_id}",
            dashboard_by_parent_and_catalogue="/api/{model_slug}/dashboardByParentAndCatalogue/{str_group_by}/{int_id}/{int_cat_id}",  # noqa: E501
            group_by_family="/api/{model_slug}/groupByFamily/{int_security_plan}",
            dashboard_by_sp="/api/{model_slug}/dashboardBySP/{str_group_by}/{int_security_plan}",
            report="/api/{model_slug}/report/{str_report}",
            get_by_parent="/api/{model_slug}/getByParent/{int_id}/{str_module}",
            get_count_by_parent="/api/{model_slug}/getCountByParent/{int_id}/{str_module}",
            get_all_asset_controls_by_component="/api/{model_slug}/getAllAssetControlsByComponent/{int_id}",
            drilldown_asset_controls_by_component="/api/{model_slug}/drilldownAssetControlsByComponent/{component_id}/{str_field}/{str_value}",  # noqa: E501
            get_control_context="/api/{model_slug}/getControlContext/{int_control_id}/{int_parent_id}/{str_module}",
            get_control_with_all_child_details="/api/{model_slug}/getControlWithAllChildDetails/{intId}",
        )

    @classmethod
    def get_with_child_details(cls, implementation_id: int) -> Optional[list[dict]]:
        """
        Get control implementation with all child details.

        Retrieve a control implementation with all supporting data in a single call.

        :param int implementation_id: The ID of the control implementation
        :return: A list of control implementation details or None
        :rtype: Optional[list[dict]]
        """
        endpoint = cls.get_endpoint("get_control_with_all_child_details").format(intId=implementation_id)
        response = cls._get_api_handler().get(endpoint)
        if response and response.ok:
            return response.json()
        return None

    # Removed for now, will need to be added back once platform changes are made
    # def find_by_unique(self, **kwargs: dict) -> Optional["ControlImplementation"]:
    #     """
    #     Find an object by unique query.
    #
    #     :param dict **kwargs: The unique query parameters
    #     :return: The object or None if not found
    #     :rtype: Optional[ControlImplementation]
    #     """
    #
    #     for instance in self.get_by_security_control_id(security_control_id=self.controlID):
    #         return instance
    #     return None

    def _get_status_enum(self) -> List["ControlImplementationStatus"]:
        """
        A method to pull the RegScale multiselect status as a list of ControlImplementationStatus.

        :return: A list of control implementation status
        :rtype: List["ControlImplementationStatus"]
        """
        if not self.status:
            return []
        try:
            return [ControlImplementationStatus(status.strip()) for status in self.status.split(",")]
        except ValueError:
            return []

    @classmethod
    def get_by_security_control_id(cls, security_control_id: int) -> List["ControlImplementation"]:
        """
        Get a list of control implementations by security control ID.

        :param int security_control_id: The ID of the security control
        :return: A list of control implementations
        :rtype: List[ControlImplementation]
        """
        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("get_by_security_control_id").format(int_security_plan=security_control_id)
        )
        security_controls = []
        if response and response.ok:
            for ci in response.json():
                if ci := cls.get_object(object_id=ci["id"]):
                    security_controls.append(ci)
        return security_controls

    @classmethod
    def get_list_by_plan(cls, plan_id: int) -> List["ControlImplementation"]:
        """
        Get a list of control implementations by plan ID.

        :param int plan_id: The ID of the plan
        :return: A list of control implementations
        :rtype: List[ControlImplementation]
        """
        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("get_list_by_plan").format(int_security_plan=plan_id)
        )
        security_controls = []
        if response and response.ok:
            for ci in response.json():
                if ci := cls.get_object(object_id=ci["id"]):
                    security_controls.append(ci)
        return security_controls

    @classmethod
    def get_control_label_map_by_parent(cls, parent_id: int, parent_module: str) -> Dict[str, int]:
        """
        Get a map of control names to implementation IDs by parent

        :param int parent_id: The ID of the parent
        :param str parent_module: The module of the parent
        :return: A dictionary mapping control IDs to implementation IDs
        :rtype: Dict[str, int]
        """
        logger.info("Getting control label map by parent...")
        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("get_all_by_parent").format(intParentID=parent_id, strModule=parent_module)
        )

        if response and response.ok:
            logger.info("Fetched control label map by parent successfully.")
            return {parentheses_to_dot(ci["controlName"]): ci["id"] for ci in response.json()}
        logger.info("Unable to get control label map by parent.")
        return {}

    @classmethod
    def get_control_id_map_by_parent(cls, parent_id: int, parent_module: str) -> Dict[int, int]:
        """
        Get a map of control IDs to implementation IDs by parent

        :param int plan_id: The ID of the plan
        :return: A dictionary mapping control IDs to implementation IDs
        :rtype: Dict[int, int]
        """
        logger.info("Getting control id map by parent...")
        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("get_all_by_parent").format(intParentID=parent_id, strModule=parent_module)
        )
        if response and response.ok:
            logger.info("Fetched control id map by parent successfully.")
            return {ci["controlID"]: ci["id"] for ci in response.json()}
        logger.info("Unable to get control id map by parent.")
        return {}

    @classmethod
    def get_control_label_map_by_plan(cls, plan_id: int) -> Dict[str, int]:
        """
        Get a map of control labels to control implementations by plan ID.

        :param int plan_id: The ID of the plan
        :return: A dictionary mapping control IDs to implementation IDs
        :rtype: Dict[str, int]
        """
        logger.debug("Getting control label map by plan...")
        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("get_all_by_plan_with_controls").format(int_security_plan=plan_id)
        )
        if response and response.ok:
            logger.debug("Fetched control label map by plan successfully.")
            return {parentheses_to_dot(ci["control"]["controlId"]): ci["id"] for ci in response.json()}
        logger.warning("Unable to get control label map by plan.")
        return {}

    @classmethod
    def fetch_implementation_ids_by_cci(cls, parent_id: int, cci_name: str, skip: int = 0, take: int = 50) -> list[int]:
        """
        Fetch control implementation ids by CCI.

        :param int parent_id: The ID of the parent
        :param str cci_name: The name of the CCI
        :param int skip: The number of items to skip
        :param int take: The number of items to take
        :return: A list of control implementation IDs
        :rtype: list[int]
        """

        query = f"""
            query GetControlImplementations() {{
                controlImplementations(
                    skip: {skip}, take: {take}, where: {{
                        parentId: {{eq: {parent_id}}},
                        control: {{
                            controlObjectives: {{
                                some: {{
                                    otherId: {{
                                        contains: "{cci_name}"
                                    }}
                                }}
                            }}
                        }}
                    }}
                ) {{
                items {{
                    id
                }}
                pageInfo {{
                    hasNextPage
                }}
                totalCount
                }}
            }}
        """

        response = cls._get_api_handler().graph(query)
        if "controlImplementations" in response:
            return [item["id"] for item in response["controlImplementations"]["items"]]
        return []

    @classmethod
    def get_control_id_map_by_plan(cls, plan_id: int) -> Dict[int, int]:
        """
        Get a map of control ids to control implementations by plan ID.

        :param int plan_id: The ID of the plan
        :return: A dictionary mapping control IDs to implementation IDs
        :rtype: Dict[int, int]
        """
        logger.debug("Getting control id map by plan...")
        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("get_all_by_plan_with_controls").format(int_security_plan=plan_id)
        )
        if response and response.ok:
            logger.debug("Fetched control id map by plan successfully.")
            return {ci["control"]["id"]: ci["id"] for ci in response.json()}
        logger.warning("Unable to get control id map by plan.")
        return {}

    @staticmethod
    def post_implementation(
        app: Application, implementation: "ControlImplementation"
    ) -> Union[requests.Response, Dict]:
        """
        Post a control implementation to RegScale via API

        :param Application app:
        :param ControlImplementation implementation:
        :return: Response from RegScale API or the response if the response is not ok
        :rtype: Union[requests.Response, Dict]
        """
        api = Api()
        headers = {
            "accept": "*/*",
            "Authorization": app.config["token"],
            "Content-Type": PATCH_CONTENT_TYPE,
        }

        res = api.post(
            app.config["domain"] + "/api/controlimplementation",
            headers=headers,
            json=implementation.dict(),
        )
        if not res.raise_for_status() and res.status_code == 200:
            return res.json()
        else:
            return res

    @staticmethod
    def update(app: Application, implementation: "ControlImplementation") -> Union[requests.Response, Dict]:
        """
        Update Method for ControlImplementation

        :param Application app: Application instance
        :param ControlImplementation implementation: ControlImplementation instance
        :return: A control implementation dict or a response object
        :rtype: Union[requests.Response, Dict]
        """
        api = Api()

        res = api.put(
            app.config["domain"] + f"/api/controlimplementation/{implementation.id}",
            json=implementation.dict(),
        )
        if not res.raise_for_status() and res.status_code == 200:
            return res.json()
        else:
            return res

    @staticmethod
    def fetch_existing_implementations(app: Application, regscale_parent_id: int, regscale_module: str) -> List[Dict]:
        """
        Fetch existing implementations for the provided id and module from RegScale

        :param Application app: Application instance
        :param int regscale_parent_id: RegScale Parent ID
        :param str regscale_module: RegScale Parent Module
        :return: list of existing implementations
        :rtype: List[Dict]
        """
        api = Api()
        existing_implementations = []
        existing_implementations_response = api.get(
            url=app.config["domain"]
            + "/api/controlimplementation"
            + f"/getAllByParent/{regscale_parent_id}/{regscale_module}"
        )
        if existing_implementations_response.ok:
            existing_implementations = existing_implementations_response.json()
        return existing_implementations

    @staticmethod
    def _extract_text_and_log(
        element: Element, imp: "ControlImplementation", debug_logger: logging.Logger
    ) -> Optional[str]:
        """
        Extracts and logs text from an XML element.

        :param Element element: The XML element.
        :param ControlImplementation imp: The control implementation instance.
        :param logging.Logger debug_logger: Logger for debugging.
        :return: Stripped text from the element.
        :rtype: Optional[str]
        """

        text = element.text.strip() if element.text else None
        if text:
            debug_logger.debug("Text: %s", text)
            imp.implementation = text
        return text

    @staticmethod
    def _update_implementation_status(element: Element, imp: "ControlImplementation") -> None:
        """
        Updates the implementation statuses and control origin of the control based on the element.

        :param Element element: The XML element.
        :param ControlImplementation imp: The control implementation instance.
        :rtype: None
        """

        def update_status_from_value(value: str, status_map: Dict[str, tuple]) -> Optional[tuple]:
            """
            Updates the implementation status based on the value

            :param str value: The value to update the status from
            :param Dict[str, tuple] status_map: The status mapping
            :return: The status and the flag attribute
            :rtype: Optional[tuple]
            """
            if value in status_map:
                status, flag_attr = status_map[value]
                setattr(imp, flag_attr, True)
                return status
            logger.warning(f"Invalid value: {value}")
            return None

        status_mapping = {
            "implemented": (ControlImplementationStatus.FullyImplemented, "bStatusImplemented"),
            "partial": (ControlImplementationStatus.PartiallyImplemented, "bStatusPartiallyImplemented"),
            "not-applicable": (ControlImplementationStatus.NA, "bStatusNotApplicable"),
            "planned": (ControlImplementationStatus.Planned, "bStatusPlanned"),
            "alternative": (ControlImplementationStatus.Alternative, "bStatusAlternative"),
        }

        responsibility_mapping = {
            "sp-corporate": (ControlImplementationOrigin.Provider, "bServiceProviderCorporate"),
            "sp-system": (ControlImplementationOrigin.ProviderSS, "bServiceProviderSystemSpecific"),
            "customer-configured": (ControlImplementationOrigin.CustomerConfigured, "bConfiguredByCustomer"),
            "customer-provided": (ControlImplementationOrigin.CustomerProvided, "bProvidedByCustomer"),
            "inherited": (ControlImplementationOrigin.Inherited, "bInherited"),
        }

        if "name" in element.attrib:
            if element.attrib["name"] == "implementation-status":
                imp.status = update_status_from_value(element.attrib.get("value"), status_mapping)

            if element.attrib["name"] == "control-origination":
                imp.responsibility = update_status_from_value(element.attrib.get("value"), responsibility_mapping)

    @staticmethod
    def from_oscal_element(app: Application, obj: Element, control: dict) -> "ControlImplementation":
        """
        Create RegScale ControlImplementation from XML element.

        :param Application app: RegScale CLI Application object.
        :param Element obj: Element object.
        :param dict control: Control dictionary.
        :return: ControlImplementation class.
        :rtype: ControlImplementation
        """
        user = app.config["userId"]
        imp = ControlImplementation(controlOwnerId=user, status="notimplemented", controlID=control["id"])

        for element in obj.iter():
            ControlImplementation._extract_text_and_log(element, imp, logger)

            # This try catch is tied to modification to catalogs object returned by above API call
            # The otherId field is to be added to new OSCAL catalogs which will be migrated for existing customers.
            # If otherId exists use it to match to control otherwise use original controlId
            # Handle case where otherId does not exist in catalog object and do not throw an error

            # if otherid exists in catalog object make sure it has something in it before matching
            # this case may exist while new catalogs are being migrated to for customers
            if len(control.get("otherId", [])) > 0:
                imp.control = control["otherId"]
            else:
                logger.debug("Warning: OtherId (machine readable) not found on record.")
                imp.control = control["controlId"]

            for name, value in element.attrib.items():
                logger.debug(f"Property: {name}, Value: {value}")
                ControlImplementation._update_implementation_status(element, imp)

        return imp

    @staticmethod
    def from_dict(obj: Any) -> "ControlImplementation":
        """
        Create ControlImplementation from dictionary

        :param Any obj: Object to create ControlImplementation from
        :return: ControlImplementation class
        :rtype: ControlImplementation
        """
        if "id" in obj:
            del obj["id"]
        return ControlImplementation(**obj)

    def __hash__(self) -> int:
        """
        Hash function for ControlImplementation

        :return: Hash of ControlImplementation
        :rtype: int
        """
        return hash(
            (
                self.controlID,
                self.controlOwnerId,
                self.status,
            )
        )

    @staticmethod
    def post_batch_implementation(
        app: Application, implementations: List[Dict]
    ) -> Optional[Union[requests.Response, Dict]]:
        """
        Post a batch of control implementations to the RegScale API

        :param Application app: RegScale CLI Application object
        :param List[Dict] implementations: list of control implementations to post to RegScale
        :return: Response from RegScale API or the response content if the response is not ok
        :rtype: Optional[Union[requests.Response, Dict]]
        """
        if len(implementations) > 0:
            api = Api()
            headers = {
                "accept": "*/*",
                "Authorization": app.config["token"],
                "Content-Type": PATCH_CONTENT_TYPE,
            }
            res = api.post(
                url=urljoin(app.config["domain"], "/api/controlImplementation/batchCreate"),
                json=implementations,
                headers=headers,
            )
            if not res.raise_for_status() and res.status_code == 200:
                app.logger.info(f"Created {len(implementations)} Control Implementations, Successfully!")
                return res.json()
            else:
                return res

    @staticmethod
    def put_batch_implementation(
        app: Application, implementations: List[Dict]
    ) -> Optional[Union[requests.Response, Dict]]:
        """
        Put a batch of control implementations to the RegScale API

        :param Application app: RegScale CLI Application object
        :param List[Dict] implementations: list of control implementations to post to RegScale
        :return: Response from RegScale API or the response content if the response is not ok
        :rtype: Optional[Union[requests.Response, Dict]]
        """
        if len(implementations) > 0:
            api = Api()
            headers = {
                "accept": "*/*",
                "Authorization": app.config["token"],
                "Content-Type": PATCH_CONTENT_TYPE,
            }
            res = api.post(
                url=urljoin(app.config["domain"], "/api/controlImplementation/batchUpdate"),
                json=implementations,
                headers=headers,
            )
            if not res.raise_for_status() and res.status_code == 200:
                app.logger.info(f"Updated {len(implementations)} Control Implementations, Successfully!")
                return res.json()
            else:
                return res

    @staticmethod
    def get_existing_control_implementations(parent_id: int) -> Dict:
        """
        Fetch existing control implementations as dict with control id as the key used for
        automating control implementation creation

        :param int parent_id: parent control id
        :return: Dictionary of existing control implementations
        :rtype: Dict
        """
        app = Application()
        api = Api()
        domain = app.config.get("domain")
        existing_implementation_dict = {}
        get_url = urljoin(domain, f"/api/controlImplementation/getAllByPlan/{parent_id}")
        response = api.get(get_url)
        if response.ok:
            existing_control_implementations_json = response.json()
            for cim in existing_control_implementations_json:
                existing_implementation_dict[cim.get("controlName")] = cim
            logger.debug(f"Found {len(existing_implementation_dict)} existing control implementations")
        elif response.status_code == 404:
            logger.debug(f"No existing control implementations found for {parent_id}")
        else:
            logger.warning(f"Unable to get existing control implementations. {response.content}")
        return existing_implementation_dict

    @classmethod
    def create_control_implementations(
        cls,
        controls: list,
        parent_id: int,
        parent_module: str,
        existing_implementation_dict: dict,
        full_controls: dict,
        failing_controls: dict,
        include_not_implemented: Optional[bool] = False,
    ) -> None:
        """
        Creates and updates control implementations based on given controls

        :param list controls: List of control details
        :param int parent_id: Identifier for the parent control
        :param str parent_module: Name of the parent module
        :param dict existing_implementation_dict: Dictionary of existing implementations
        :param dict full_controls: Dictionary of fully implemented controls
        :param dict failing_controls: Dictionary of failing controls
        :param Optional[bool] include_not_implemented: Whether to include not implemented controls, defaults to False
        :rtype: None
        """
        app = Application()
        user_id = app.config.get("userId")

        to_create, to_update = cls.process_controls(
            controls,
            parent_id,
            parent_module,
            existing_implementation_dict,
            full_controls,
            failing_controls,
            user_id,
            include_not_implemented,
        )

        cls.post_batch_if_needed(app, to_create, ControlImplementation.post_batch_implementation)
        cls.put_batch_if_needed(app, to_update, ControlImplementation.put_batch_implementation)

    @classmethod
    def process_controls(
        cls,
        controls: list,
        parent_id: int,
        parent_module: str,
        existing_implementation_dict: dict,
        full_controls: dict,
        failing_controls: dict,
        user_id: Optional[str] = None,
        include_not_implemented: Optional[bool] = False,
    ) -> tuple[list, list]:
        """
        Processes each control for creation or update

        :param list controls: List of control details
        :param int parent_id: Identifier for the parent control
        :param str parent_module: Name of the parent module
        :param dict existing_implementation_dict: Dictionary of existing implementations
        :param dict full_controls: Dictionary of fully implemented controls
        :param dict failing_controls: Dictionary of failing controls
        :param Optional[str] user_id: ID of the user performing the operation, defaults to None
        :param Optional[bool] include_not_implemented: Whether to include not implemented controls, defaults to False
        :return: Tuple containing lists of controls to create and update
        :rtype: tuple[list, list]
        """
        to_create = []
        to_update = []

        for control in controls:
            lower_case_control_id = control["controlId"].lower()
            status = cls.check_implementation(full_controls, failing_controls, lower_case_control_id)
            if not include_not_implemented and status == ControlImplementationStatus.NotImplemented.value:
                continue

            controlid = control.get("controlId")

            if controlid not in existing_implementation_dict:
                cim = cls.create_new_control_implementation(control, parent_id, parent_module, status, user_id)
                to_create.append(cim)
            else:
                cls.update_existing_control_implementation(
                    control, existing_implementation_dict, status, to_update, user_id
                )

        return to_create, to_update

    @staticmethod
    def create_new_control_implementation(
        control: dict,
        parent_id: int,
        parent_module: str,
        status: str,
        user_id: Optional[str] = None,
    ) -> "ControlImplementation":
        """
        Creates a new control implementation object

        :param dict control: Control details
        :param int parent_id: Identifier for the parent control
        :param str parent_module: Name of the parent module
        :param str status: Status of the control implementation
        :param Optional[str] user_id: ID of the user performing the operation, defaults to None
        :return: New control implementation object
        :rtype: ControlImplementation
        """
        cim = ControlImplementation(
            controlOwnerId=user_id,
            dateLastAssessed=get_current_datetime(),
            implementation=control.get("implementation", None),
            status=status,
            controlID=control["id"],
            parentId=parent_id,
            parentModule=parent_module,
            createdById=user_id,
            dateCreated=get_current_datetime(),
            lastUpdatedById=user_id,
            dateLastUpdated=get_current_datetime(),
        ).dict()
        cim["controlSource"] = "Baseline"
        return cim

    @classmethod
    def update_existing_control_implementation(
        cls,
        control: dict,
        existing_implementation_dict: dict,
        status: str,
        to_update: list,
        user_id: Optional[str] = None,
    ):
        """
        Updates an existing control implementation

        :param dict control: Control details
        :param dict existing_implementation_dict: Dictionary of existing implementations
        :param str status: Status of the control implementation
        :param list to_update: List of controls to update
        :param Optional[str] user_id: ID of the user performing the operation, defaults to None
        """
        existing_imp: ControlImplementation = existing_implementation_dict[control["controlId"]]
        existing_imp.status = status
        existing_imp.dateLastAssessed = get_current_datetime()
        existing_imp.lastUpdatedById = user_id
        existing_imp.dateLastUpdated = get_current_datetime()

        if existing_imp not in to_update:
            to_update.append(existing_imp)

    @staticmethod
    def post_batch_if_needed(
        app: Application,
        to_create: list,
        post_function: Callable[[Application, list], None],
    ) -> None:
        """
        Posts a batch of new implementations if the list is not empty

        :param Application app: RegScale CLI application object
        :param list to_create: List of new implementations to post
        :param Callable[[Application, list], None] post_function: The function to call for posting the batch, if needed
        :rtype: None
        """
        if to_create:
            post_function(app, to_create)

    @staticmethod
    def put_batch_if_needed(
        app: Application,
        to_update: list,
        put_function: Callable[[Application, list], None],
    ) -> None:
        """
        Puts a batch of updated implementations if the list is not empty

        :param Application app: RegScale CLI application object
        :param list to_update: List of implementations to update
        :param Callable[[Application, list], None] put_function: The function to call for putting the batch, if needed
        """
        if to_update:
            put_function(app, to_update)

    @staticmethod
    def check_implementation(
        full_controls: dict,
        failing_controls: dict,
        control_id: str,
    ) -> str:
        """
        Checks the status of a control implementation

        :param dict full_controls: Dictionary of passing controls
        :param dict partial_controls: Dictionary of partially implemented controls
        :param dict failing_controls: Dictionary of failing control implementations
        :param str control_id: control id
        :return: status of control implementation
        :rtype: str
        """
        status = ControlImplementationStatus.NotImplemented.value
        if control_id in full_controls.keys():
            logger.debug(f"Found control passing compliance check: {control_id}")
            status = ControlImplementationStatus.PartiallyImplemented.value
        elif control_id in failing_controls.keys():
            logger.debug(f"Found control failing compliance check: {control_id}")
            status = ControlImplementationStatus.InRemediation.value
        return status

    @classmethod
    def get_sort_position_dict(cls) -> dict:
        """
        Overrides the base method.

        :return: dict The sort position in the list of properties
        :rtype: dict
        """
        return {
            "id": 1,
            "controlOwnerId": 2,
            "status": 3,
            "controlID": 4,
            "parentId": 5,
            "parentModule": 6,
            "control": 7,
            "controlName": 8,
            "controlTitle": 9,
            "description": 10,
            "createdById": -1,
            "uuid": -1,
            "policy": 11,
            "implementation": 12,
            "dateLastAssessed": 13,
            "lastAssessmentResult": 14,
            "practiceLevel": 15,
            "processLevel": 16,
            "cyberFunction": 17,
            "implementationType": 18,
            "implementationMethod": 19,
            "qdWellDesigned": 20,
            "qdProcedures": 21,
            "qdSegregation": 22,
            "qdFlowdown": 23,
            "qdAutomated": 24,
            "qdOverall": 25,
            "qiResources": 26,
            "qiMaturity": 27,
            "qiReporting": 28,
            "qiVendorCompliance": 29,
            "qiIssues": 30,
            "qiOverall": 31,
            "responsibility": 32,
            "inheritedControlId": 33,
            "inheritedRequirementId": 34,
            "inheritedSecurityPlanId": 35,
            "inheritedPolicyId": 36,
            "dateCreated": -1,
            "lastUpdatedById": -1,
            "dateLastUpdated": -1,
            "weight": 37,
            "isPublic": -1,
            "inheritable": 38,
            "systemRoleId": 39,
            "plannedImplementationDate": 40,
            "stepsToImplement": 41,
        }

    @classmethod
    def get_enum_values(cls, field_name: str) -> list:
        """
        Overrides the base method.

        :param str field_name: The property name to provide enum values for
        :return: list of strings
        :rtype: list
        """
        if field_name == "status":
            return [imp_status.value for imp_status in ControlImplementationStatus]
        if field_name == "responsibility":
            return ["Provider", "Customer", "Shared", "Not Applicable"]
        return cls.get_bool_enums(field_name)

    @classmethod
    def get_lookup_field(cls, field_name: str) -> str:
        """
        Overrides the base method.

        :param str field_name: The property name to provide enum values for
        :return: str the field name to look up
        :rtype: str
        """
        lookup_fields = {
            "controlOwnerId": "user",
            "controlID": "",
            "inheritedControlId": "",
            "inheritedRequirementId": "",
            "inheritedSecurityPlanId": "",
            "inheritedPolicyId": "",
            "systemRoleId": "",
        }
        if field_name in lookup_fields.keys():
            return lookup_fields[field_name]
        return ""

    @classmethod
    def is_date_field(cls, field_name: str) -> bool:
        """
        Overrides the base method.

        :param str field_name: The property name to provide enum values for
        :return: bool if the field should be formatted as a date
        :rtype: bool
        """
        return field_name in ["dateLastAssessed", "plannedImplementationDate"]

    @classmethod
    def get_export_query(cls, app: Application, parent_id: int, parent_module: str) -> list:
        """
        Overrides the base method.

        :param Application app: RegScale Application object
        :param int parent_id: RegScale ID of parent
        :param str parent_module: Module of parent
        :return: list GraphQL response from RegScale
        :rtype: list
        """
        body = """
                    query{
                        controlImplementations (skip: 0, take: 50, where: {parentId: {eq: parent_id} parentModule: {eq: "parent_module"}}) {
                            items {
                                id
                                controlID
                                controlOwner {
                                    firstName
                                    lastName
                                    userName
                                }
                                control {
                                    title
                                    description
                                    controlId
                                }
                                status
                                policy
                                implementation
                                responsibility
                                inheritable
                                parentId
                                parentModule
                            }
                            totalCount
                            pageInfo {
                                hasNextPage
                            }
                        }
                    }""".replace(
            "parent_module", parent_module
        ).replace(
            "parent_id", str(parent_id)
        )

        api = Api()
        existing_implementation_data = api.graph(query=body)

        if existing_implementation_data["controlImplementations"]["totalCount"] > 0:
            raw_data = existing_implementation_data["controlImplementations"]["items"]
            moded_data = []
            for item in raw_data:
                moded_item = {}
                moded_item["id"] = item["id"]
                moded_item["controlID"] = item["controlID"]
                moded_item["controlOwnerId"] = (
                    str(item["controlOwner"]["lastName"]).strip()
                    + ", "
                    + str(item["controlOwner"]["firstName"]).strip()
                    + " ("
                    + str(item["controlOwner"]["userName"]).strip()
                    + ")"
                )
                moded_item["controlName"] = item["control"]["controlId"]
                moded_item["controlTitle"] = item["control"]["title"]
                moded_item["description"] = item["control"]["description"]
                moded_item["status"] = item["status"]
                moded_item["policy"] = item["policy"]
                moded_item["implementation"] = item["implementation"]
                moded_item["responsibility"] = item["responsibility"]
                moded_item["inheritable"] = item["inheritable"]
                moded_data.append(moded_item)
            return moded_data
        return []

    @classmethod
    def use_query(cls) -> bool:
        """
        Overrides the base method.

        :return: bool
        :rtype: bool
        """
        return True

    @classmethod
    def get_extra_fields(cls) -> list:
        """
        Overrides the base method.

        :return: list of extra field names
        :rtype: list
        """
        return ["controlName", "controlTitle", "description"]

    @classmethod
    def get_include_fields(cls) -> list:
        """
        Overrides the base method.

        :return: list of  field names
        :rtype: list
        """
        return [
            "dateLastAssessed",
            "lastAssessmentResult",
            "practiceLevel",
            "processLevel",
            "cyberFunction",
            "implementationType",
            "implementationMethod",
        ]

    @classmethod
    def is_new_excel_record_allowed(cls) -> bool:
        """
        Overrides the base method.

        :return: bool indicating if the field is required
        :rtype: bool
        """
        return False

    def add_role(self, role_id: int):
        """
        Add role to the control implementation
        """
        if not self.id or self.id == 0:
            logger.error("Control Implementation ID is required to add role")
        ImplementationRole.add_role(
            role_id=role_id, control_implementation_id=self.id, parent_module=self._module_string
        )

    @classmethod
    def get_list_by_parent(cls, regscale_id: int, regscale_module: str) -> Optional[list[dict]]:
        """
        Get a list of control implementations by parent ID and module.

        :param int regscale_id: parent id of control implementation
        :param str regscale_module: parent module of control implementation
        :return: list of control implementations, or None if not found
        :rtype: Optional[list[dict]]
        """
        endpoint = cls.get_endpoint("get_list_by_parent").format(int_id=regscale_id, str_module=regscale_module)
        response = cls._get_api_handler().get(endpoint=endpoint)
        if response and response.ok:
            return response.json()
        return None

    @classmethod
    def get_list_by_parent_control(
        cls, regscale_id: int, regscale_module: str, control_id: int
    ) -> Optional["ControlImplementation"]:
        """
        Get a control implementation by parent ID, module, and control ID.
        :param int regscale_id: parent id of control implementation
        :param str regscale_module: parent module of control implementation
        :param int control_id: ID of the parent control
        :return: list of control implementations for the given parent control and record
        :rtype: List[ControlImplementation]
        """
        endpoint = cls.get_endpoint("get_list_by_parent_control").format(parent_control_id=control_id)
        response = cls._api_handler.get(endpoint=endpoint)
        control_imps: List["ControlImplementation"] = cls._handle_list_response(response)
        for control_imp in control_imps:
            if (control_imp.parentId == regscale_id) and (control_imp.parentModule == regscale_module):
                return control_imp
        return None
