#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Model for a RegScale Issue"""
import datetime
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, TypedDict, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from regscale.models import File

from urllib.parse import urljoin

from pathlib import Path
from pydantic import Field, field_validator
from requests import JSONDecodeError
from rich.progress import Progress

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import check_file_path, get_current_datetime, reformat_str_date, save_data_to
from regscale.models.regscale_models.regscale_model import RegScaleModel
from regscale.utils.version import RegscaleVersion


# Module-level cache for open issues - avoids Pydantic conflicts
_OPEN_ISSUES_CACHE: Dict[int, Tuple[float, Dict[int, List["OpenIssueDict"]]]] = {}
_CACHE_TTL: float = 300.0  # 5 minutes TTL in seconds


class OpenIssueDict(TypedDict):
    """TypedDict for open issues"""

    id: int
    otherIdentifier: str
    integrationFindingId: str


class IssueSeverity(str, Enum):
    """Issue Severity"""

    NotAssigned = "IV - Not Assigned"
    Low = "III - Low - Other Weakness"
    Moderate = "II - Moderate - Reportable Condition"
    High = "I - High - Significant Deficiency"
    Critical = "0 - Critical - Critical Deficiency"

    def __str__(self) -> str:
        """
        Return the value of the Enum as a string

        :return: The value of the Enum as a string
        :rtype: str
        """
        return self.value


class IssueStatus(str, Enum):
    """Issue Status"""

    Draft = "Draft"
    PendingScreening = "Pending Screening"
    Open = "Open"
    PendingVerification = "Pending Verification"
    Closed = "Closed"
    Cancelled = "Cancelled"
    PendingDecommission = "Pending Decommission"
    SupplyChainProcurementDependency = "Supply Chain/Procurement Dependency"
    VendorDependency = "Vendor Dependency for Fix"
    Delayed = "Delayed"
    ExceptionWaiver = "Exception/Waiver"
    PendingApproval = "Pending Approval"

    def __str__(self) -> str:
        """
        Return the value of the Enum as a string

        :return: The value of the Enum as a string
        :rtype: str
        """
        return self.value


class Issue(RegScaleModel):
    """Issue Model"""

    _module_slug = "issues"
    _x_api_version = "2"
    _unique_fields = [
        ["integrationFindingId", "vulnerabilityId", "status"],
        ["otherIdentifier", "parentModule", "parentId", "status"],
    ]
    _exclude_graphql_fields = [
        "facility",
        "org",
        "createdBy",
        "lastUpdatedBy",
        "extra_data",
        "tenantsId",
        "issueOwner",
        "controlImplementationIds",
    ]

    title: Optional[str] = ""
    severityLevel: Union[IssueSeverity, str] = IssueSeverity.NotAssigned
    issueOwnerId: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    dueDate: Optional[str] = ""
    id: int = 0
    tenantsId: int = 1
    uuid: Optional[str] = None
    dateCreated: Optional[str] = Field(default_factory=get_current_datetime)
    description: Optional[str] = None
    issueOwner: Optional[str] = None
    costEstimate: Optional[int] = None
    levelOfEffort: Optional[int] = None
    identification: Optional[str] = ""  # Has to be an empty string or else it will fail to create
    capStatus: Optional[str] = None
    sourceReport: Optional[str] = None
    status: Optional[Union[IssueStatus, str]] = None
    dateCompleted: Optional[str] = None
    activitiesObserved: Optional[str] = None
    failuresObserved: Optional[str] = None
    requirementsViolated: Optional[str] = None
    safetyImpact: Optional[str] = None
    securityImpact: Optional[str] = None
    qualityImpact: Optional[str] = None
    facility: Optional[str] = None
    facilityId: Optional[int] = None
    org: Optional[str] = None
    orgId: Optional[int] = None
    controlId: Optional[int] = None
    assessmentId: Optional[int] = None
    requirementId: Optional[int] = None
    securityPlanId: Optional[int] = None
    projectId: Optional[int] = None
    supplyChainId: Optional[int] = None
    policyId: Optional[int] = None
    componentId: Optional[int] = None
    incidentId: Optional[int] = None
    jiraId: Optional[str] = None
    serviceNowId: Optional[str] = None
    wizId: Optional[str] = None
    burpId: Optional[str] = None
    defenderId: Optional[str] = None
    defenderAlertId: Optional[str] = None
    defenderCloudId: Optional[str] = None
    salesforceId: Optional[str] = None
    prismaId: Optional[str] = None
    tenableId: Optional[str] = None
    tenableNessusId: Optional[str] = None
    qualysId: Optional[str] = None
    pluginId: Optional[str] = None
    cve: Optional[str] = None
    assetIdentifier: Optional[str] = None
    falsePositive: Optional[str] = None
    operationalRequirement: Optional[str] = None
    autoApproved: Optional[str] = None
    kevList: Optional[str] = None
    dateFirstDetected: Optional[str] = None
    changes: Optional[str] = None
    vendorDependency: Optional[str] = None
    vendorName: Optional[str] = None
    vendorLastUpdate: Optional[str] = None
    vendorActions: Optional[str] = None
    deviationRationale: Optional[str] = None
    parentId: Optional[int] = None
    parentModule: Optional[str] = None
    createdBy: Optional[str] = None
    createdById: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    lastUpdatedBy: Optional[str] = None
    lastUpdatedById: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    dateLastUpdated: Optional[str] = Field(default_factory=get_current_datetime)
    securityChecks: Optional[str] = None
    recommendedActions: Optional[str] = None
    isPublic: Optional[bool] = True
    dependabotId: Optional[str] = None
    isPoam: Optional[bool] = False
    originalRiskRating: Optional[str] = None
    adjustedRiskRating: Optional[str] = None
    bRiskAdjustment: Optional[bool] = None
    basisForAdjustment: Optional[str] = None
    poamComments: Optional[str] = None
    otherIdentifier: Optional[str] = None
    integrationFindingId: Optional[str] = None
    wizCicdScanId: Optional[str] = None
    wizCicdScanVuln: Optional[str] = None
    sonarQubeIssueId: Optional[str] = None
    qualityAssurerId: Optional[str] = None
    remediationDescription: Optional[str] = None
    manualDetectionSource: Optional[str] = None
    manualDetectionId: Optional[str] = None
    vulnerabilityId: Optional[int] = None
    riskAdjustment: Optional[str] = None
    controlImplementationIds: List[int] = Field(default_factory=list)
    affectedControls: Optional[str] = None

    @staticmethod
    def is_multiple_controls_supported() -> bool:
        """
        Check if multiple control is supported

        :return: True if multiple controls is supported
        :rtype: bool
        """
        return RegscaleVersion.meets_minimum_version("7.0.0", dev_is_latest=False)

    def __init__(self, **data: Any):
        # Handle aliases internally
        if "parent_id" in data:
            data["parentId"] = data.pop("parent_id")
        if "parent_module" in data:
            data["parentModule"] = data.pop("parent_module")
        super().__init__(**data)

    @staticmethod
    def _get_additional_endpoints() -> dict:
        """
        Get additional endpoints for the Issues model.

        :return: A dictionary of additional endpoints
        :rtype: dict
        """
        return {
            "user_open_items_days": "/api/{model_slug}/userOpenItemsDays/{strUserId}/{intDays}",
            "set_quality_assurer": "/api/{model_slug}/setQualityAssurer/{intIssueId}/{strQaUserId}",
            "remove_quality_assurer": "/api/{model_slug}/removeQualityAssurer/{intIssueId}",
            "process_lineage": "/api/{model_slug}/processLineage/{intIssueId}",
            "get_count": "/api/{model_slug}/getCount",
            "get_by_date_range": "/api/{model_slug}/getByDateRange/{dtStart}/{dtEnd}",
            "get_by_date_range_and_date_field": "/api/{model_slug}/getByDateRangeAndDateField/{dateField}/{dtStart}/{dtEnd}",
            "graph_by_owner_then_status": "/api/{model_slug}/graphByOwnerThenStatus/{dateField}/{dtStart}/{dtEnd}",
            "group_by_owner_and_plan_then_status_forever": "/api/{model_slug}/groupByOwnerAndPlanThenStatusForever",
            "group_by_owner_and_plan_then_status": "/api/{model_slug}/groupByOwnerAndPlanThenStatus/{dateField}/{dtStart}/{dtEnd}",
            "group_by_owner_and_component_then_status": "/api/{model_slug}/groupByOwnerAndComponentThenStatus/{dateField}/{dtStart}/{dtEnd}",
            "group_by_owner_and_component_then_status_forever": "/api/{model_slug}/groupByOwnerAndComponentThenStatusForever",
            "group_by_owner_and_component_then_status_drilldown": "/api/{model_slug}/groupByOwnerAndComponentThenStatusDrilldown/{intId}/{ownerId}/{dateField}/{dtStart}/{dtEnd}",
            "group_by_owner_and_plan_then_status_drilldown": "/api/{model_slug}/groupByOwnerAndPlanThenStatusDrilldown/{intId}/{ownerId}/{dateField}/{dtStart}/{dtEnd}",
            "get_by_date_closed": "/api/{model_slug}/getByDateClosed/{dtStart}/{dtEnd}",
            "get_all_by_integration_field": "/api/{model_slug}/getAllByIntegrationField/{strFieldName}",
            "get_active_by_integration_field": "/api/{model_slug}/getActiveByIntegrationField/{strFieldName}",
            "get_filtered_list": "/api/{model_slug}/getFilteredList/{strFind}",
            "get_all_by_grand_parent": "/api/{model_slug}/getAllByGrandParent/{intParentId}/{strModule}",
            "query_by_custom_field": "/api/{model_slug}/queryByCustomField/{strFieldName}/{strValue}",
            "issue_timeline": "/api/{model_slug}/issueTimeline/{intId}/{strModule}/{strType}",
            "calendar_issues": "/api/{model_slug}/calendarIssues/{dtDate}/{fId}/{orgId}/{userId}",
            "graph": "/api/{model_slug}/graph",
            "graph_by_date": "/api/{model_slug}/graphByDate/{strGroupBy}/{year}",
            "filter_issues": "/api/{model_slug}/filterIssues",
            "update_issue_screening": "/api/{model_slug}/screening/{id}",
            "retrieve_issue": "/api/{model_slug}/{intId}",
            "emass_component_export": "/api/{model_slug}/emassComponentExport/{intId}",
            "emass_ssp_export": "/api/{model_slug}/emassSSPExport/{intId}",
            "find_by_other_identifier": "/api/{model_slug}/findByOtherIdentifier/{id}",
            "find_by_service_now_id": "/api/{model_slug}/findByServiceNowId/{id}",
            "find_by_salesforce_case": "/api/{model_slug}/findBySalesforceCase/{id}",
            "find_by_jira_id": "/api/{model_slug}/findByJiraId/{id}",
            "find_by_dependabot_id": "/api/{model_slug}/findByDependabotId/{id}",
            "find_by_prisma_id": "/api/{model_slug}/findByPrismaId/{id}",
            "find_by_wiz_id": "/api/{model_slug}/findByWizId/{id}",
            "find_by_wiz_cicd_scan_id": "/api/{model_slug}/findByWizCicdScanId/{wizCicdScanId}",
            "get_all_by_wiz_cicd_scan_vuln": "/api/{model_slug}/getAllByWizCicdScanVuln/{wizCicdScanVuln}",
            "get_active_by_wiz_cicd_scan_vuln": "/api/{model_slug}/getActiveByWizCicdScanVuln/{wizCicdScanVuln}",
            "find_by_sonar_qube_issue_id": "/api/{model_slug}/findBySonarQubeIssueId/{projectId}/{issueId}",
            "find_by_defender_365_id": "/api/{model_slug}/findByDefender365Id/{id}",
            "find_by_defender_365_alert_id": "/api/{model_slug}/findByDefender365AlertId/{id}",
            "find_by_defender_cloud_id": "/api/{model_slug}/findByDefenderCloudId/{id}",
            "report": "/api/{model_slug}/report/{strReport}",
            "schedule": "/api/{model_slug}/schedule/{dtStart}/{dtEnd}/{dvar}",
            "graph_due_date": "/api/{model_slug}/graphDueDate/{year}",
            "graph_date_identified": "/api/{model_slug}/graphDateIdentified/{year}/{status}",
            "graph_severity_level_by_date_identified": "/api/{model_slug}/graphSeverityLevelByDateIdentified/{year}",
            "graph_cost_by_date_identified": "/api/{model_slug}/graphCostByDateIdentified/{year}",
            "graph_facility_by_date_identified": "/api/{model_slug}/graphFacilityByDateIdentified/{year}",
            "get_severity_level_by_status": "/api/{model_slug}/getSeverityLevelByStatus/{dtStart}/{dtEnd}",
            "graph_due_date_by_status": "/api/{model_slug}/graphDueDateByStatus/{year}",
            "dashboard": "/api/{model_slug}/dashboard/{strGroupBy}",
            "drilldown": "/api/{model_slug}/drilldown/{strMonth}/{temporal}/{strCategory}/{chartType}",
            "main_dashboard": "/api/{model_slug}/mainDashboard/{intYear}",
            "main_dashboard_chart": "/api/{model_slug}/mainDashboardChart/{year}",
            "dashboard_by_parent": "/api/{model_slug}/dashboardByParent/{strGroupBy}/{intId}/{strModule}",
            "batch_create": "/api/{model_slug}/batchCreate",
            "batch_update": "/api/{model_slug}/batchUpdate",
            "find_by_integration_finding_id": "/api/{model_slug}/findByIntegrationFindingId/{id}",
        }

    @classmethod
    def _is_cache_valid(cls, plan_id: int) -> bool:
        """
        Check if cached data for a plan_id is still valid

        :param int plan_id: The plan ID to check cache validity for
        :return: True if cache is valid, False otherwise
        :rtype: bool
        """
        if plan_id not in _OPEN_ISSUES_CACHE:
            return False

        cached_time, _ = _OPEN_ISSUES_CACHE[plan_id]
        return (time.time() - cached_time) < _CACHE_TTL

    @classmethod
    def _get_from_cache(cls, plan_id: int) -> Optional[Dict[int, List[OpenIssueDict]]]:
        """
        Get cached data for a plan_id if it exists and is valid

        :param int plan_id: The plan ID to get cached data for
        :return: Cached data if valid, None otherwise
        :rtype: Optional[Dict[int, List[OpenIssueDict]]]
        """
        if cls._is_cache_valid(plan_id):
            _, cached_data = _OPEN_ISSUES_CACHE[plan_id]
            return cached_data
        return None

    @classmethod
    def _cache_data(cls, plan_id: int, data: Dict[int, List[OpenIssueDict]]) -> None:
        """
        Cache data for a plan_id

        :param int plan_id: The plan ID to cache data for
        :param Dict[int, List[OpenIssueDict]] data: The data to cache
        :rtype: None
        """
        _OPEN_ISSUES_CACHE[plan_id] = (time.time(), data)

    @classmethod
    def clear_cache(cls, plan_id: Optional[int] = None) -> None:
        """
        Clear cache for a specific plan_id or all cached data

        :param Optional[int] plan_id: The plan ID to clear cache for, or None to clear all cache
        :rtype: None
        """
        if plan_id is not None:
            _OPEN_ISSUES_CACHE.pop(plan_id, None)
        else:
            _OPEN_ISSUES_CACHE.clear()

    @classmethod
    def find_by_other_identifier(cls, other_identifier: str) -> List["Issue"]:
        """
        Find an issue by its other identifier.

        :param str other_identifier: The other identifier to search for
        :return: The found Issues
        :rtype: List[Issue]
        """
        api_handler = cls._get_api_handler()
        endpoint = cls.get_endpoint("find_by_other_identifier").format(id=other_identifier)

        response = api_handler.get(endpoint)
        issues: List["Issue"] = cls._handle_list_response(response)
        return issues

    @classmethod
    def find_by_integration_finding_id(cls, integration_finding_id: str) -> List["Issue"]:
        """
        Find an issue by its integration finding id.

        :param str integration_finding_id: The integration finding id to search for
        :return: The found Issues
        :rtype: List[Issue]
        """
        endpoint = cls.get_endpoint("find_by_integration_finding_id").format(id=integration_finding_id)
        response = cls._get_api_handler().get(endpoint)
        issues: List["Issue"] = cls._handle_list_response(response)
        # Ensure we are returning the cached object if it exists to ensure bulk updates work
        issues = [cls.get_cached_object(cls._get_cache_key(issue, {})) or issue for issue in issues]
        return issues

    @classmethod
    def get_all_by_integration_field(cls, field: str) -> List["Issue"]:
        """
        Get all issues by integration field.

        :param str field: The integration field to search for
        :return: The found Issues
        :rtype: List[Issue]
        """
        endpoint = cls.get_endpoint("get_all_by_integration_field").format(strFieldName=field)
        response = cls._get_api_handler().get(endpoint)
        return cls._handle_list_response(response)

    @classmethod
    def get_all_by_manual_detection_source(cls, value: str) -> List["Issue"]:
        """
        Get all issues with the manual detection source

        :param str value: The manual detection source to search for
        :return: The found Issues
        :rtype: List[Issue]
        """
        query = f"""
            query {{
                issues(take: 50, skip: 0, where: {{ manualDetectionSource: {{eq: "{value}"}}}})
                {{
                items {{
                    {Issue.build_graphql_fields()}
                }}
                pageInfo {{
                    hasNextPage
                }}
                ,totalCount}}
            }}
        """
        try:
            existing_issues = cls._get_api_handler().graph(query=query)["issues"]["items"]
        except (JSONDecodeError, TypeError, KeyError):
            existing_issues = []
        return [Issue(**issue) for issue in existing_issues]

    @staticmethod
    def get_issues_by_asset_map(plan_id: int) -> Dict[str, List["Issue"]]:
        """
        Get a dictionary of issues grouped by asset identifier for a given security plan.

        :param int plan_id: The ID of the security plan
        :return: A dictionary where keys are asset identifiers and values are lists of associated issues
        :rtype: Dict[str, List[Issue]]
        """
        issues = Issue.fetch_issues_by_ssp(None, ssp_id=plan_id, status=IssueStatus.Open.value)
        issues_by_asset = defaultdict(list)
        for issue in issues:
            if issue.assetIdentifier:
                for asset_identifier in issue.assetIdentifier.split("\n"):
                    issues_by_asset[asset_identifier].append(issue)
        return issues_by_asset

    @classmethod
    def assign_risk_rating(cls, value: Any) -> str:
        """
        Function to assign risk rating for an issue in RegScale using the provided value

        :param Any value: The value to analyze to determine the issue's risk rating
        :return: String of risk rating for RegScale issue, or "" if not found
        :rtype: str
        """
        if isinstance(value, str):
            if "low" in value.lower():
                return "Low"
            if "medium" in value.lower() or "moderate" in value.lower():
                return "Moderate"
            if "high" in value.lower() or "critical" in value.lower():
                return "High"
        return ""

    @classmethod
    def get_due_date(
        cls,
        severity: Union[IssueSeverity, str],
        config: dict,
        key: str,
        start_date: Union[str, datetime.datetime, None] = None,
        dt_format: Optional[str] = "%Y-%m-%dT%H:%M:%S",
    ) -> str:
        """
        Function to return due date based on the severity of the issue; the values are in the init.yaml
        and if not, it will default to 60 days from the current date.

        :param Union[IssueSeverity, str] severity: Severity of the issue, can be an IssueSeverity enum or a string
        :param dict config: Application config
        :param str key: The key to use for init.yaml from the issues section to determine the due date
        :param Union[str, datetime.datetime, None] start_date: The date to start the due date calculation from, defaults to current date
        :param Optional[str] dt_format: String of the date format to use, defaults to "%Y-%m-%dT%H:%M:%S"
        :return: Due date for the issue
        :rtype: str
        """
        if isinstance(start_date, str):
            from regscale.core.utils.date import datetime_obj

            start_date = datetime_obj(start_date)
        elif start_date is None:
            start_date = datetime.datetime.now()

        # if the severity is an enum, get the value
        if isinstance(severity, IssueSeverity):
            severity = severity.value
        elif severity.lower() not in [severity.value.lower() for severity in IssueSeverity]:
            severity = IssueSeverity.NotAssigned.value

        if severity == IssueSeverity.Critical.value:
            days = cls._get_days_for_values(["critical"], config, key)
            start_date = start_date + datetime.timedelta(days=days)
        elif severity == IssueSeverity.High.value:
            days = cls._get_days_for_values(["high"], config, key)
        elif severity == IssueSeverity.Moderate.value:
            days = cls._get_days_for_values(["moderate", "medium"], config, key)
        elif severity == IssueSeverity.Low.value:
            days = cls._get_days_for_values(["low", "minor"], config, key)
        else:
            days = 60
        due_date = start_date + datetime.timedelta(days=days)
        return due_date.strftime(dt_format)

    @staticmethod
    def _get_days_for_values(possible_values: List[str], config: dict, key: str, default: Optional[int] = 30) -> int:
        """
        Get the number of days for the given possible values from the configuration.

        :param List[str] possible_values: List of possible values to check
        :param dict config: Application config
        :param str key: The key to use for init.yaml from the issues section to determine the due date
        :param Optional[int] default: Default number of days to return if no values match, defaults to 30
        :return: Number of days for the first matching value, or 0 if none match
        :rtype: int
        """
        for value in possible_values:
            days = config["issues"].get(key, {}).get(value, 0)
            if days > 0:
                return days
        return default

    @staticmethod
    def assign_severity(value: Optional[Any] = None) -> str:
        """
        Function to assign severity for an issue in RegScale using the provided value

        :param Optional[Any] value: The value to analyze to determine the issue's severity, defaults to None
        :return: String of severity level for RegScale issue
        :rtype: str
        """
        severity_levels = {
            "low": IssueSeverity.Low.value,
            "moderate": IssueSeverity.Moderate.value,
            "high": IssueSeverity.High.value,
        }
        severity = IssueSeverity.NotAssigned.value
        # see if the value is an int or float
        if isinstance(value, (int, float)):
            # check severity score and assign it to the appropriate RegScale severity
            if value >= 7:
                severity = severity_levels["high"]
            elif 4 <= value < 7:
                severity = severity_levels["moderate"]
            else:
                severity = severity_levels["low"]
        elif isinstance(value, str):
            if value.lower() in ["low", "lowest", "minor"]:
                severity = severity_levels["low"]
            elif value.lower() in ["medium", "moderate", "major"]:
                severity = severity_levels["moderate"]
            elif value.lower() in ["high", "critical", "highest", "critical", "blocker"]:
                severity = severity_levels["high"]
            elif value in list(severity_levels.values()):
                severity = value
        return severity

    @staticmethod
    def update_issue(app: Application, issue: "Issue") -> Optional["Issue"]:
        """
        Update an issue in RegScale

        :param Application app: Application Instance
        :param Issue issue: Issue to update in RegScale
        :return: Updated issue in RegScale
        :rtype: Optional[Issue]
        """
        if isinstance(issue, dict):
            issue = Issue(**issue)
        api = Api()
        issue_id = issue.id

        response = api.put(app.config["domain"] + f"/api/issues/{issue_id}", json=issue.dict())
        if response.status_code == 200:
            try:
                issue = Issue(**response.json())
            except JSONDecodeError:
                return None
        return issue

    @staticmethod
    def insert_issue(app: Application, issue: "Issue") -> Optional["Issue"]:
        """
        Insert an issue in RegScale

        :param Application app: Application Instance
        :param Issue issue: Issue to insert to RegScale
        :return: Newly created issue in RegScale
        :rtype: Optional[Issue]
        """
        if isinstance(issue, dict):
            issue = Issue(**issue)
        api = Api()
        logger = create_logger()
        response = api.post(app.config["domain"] + "/api/issues", json=issue.dict())
        if response.status_code == 200:
            try:
                issue = Issue(**response.json())
            except JSONDecodeError as jex:
                logger.error("Unable to read issue:\n%s", jex)
                return None
        else:
            logger.warning("Unable to insert issue: %s", issue.title)
        return issue

    @staticmethod
    def bulk_insert(
        app: Application,
        issues: List["Issue"],
        max_workers: Optional[int] = 10,
        batch_size: int = 100,
        batch: bool = False,
    ) -> List["Issue"]:
        """
        Bulk insert issues using the RegScale API and ThreadPoolExecutor

        :param Application app: Application Instance
        :param List["Issue"] issues: List of issues to insert
        :param Optional[int] max_workers: Max Workers, defaults to 10
        :param int batch_size: Number of issues to insert per batch, defaults to 100
        :param bool batch: Insert issues in batches, defaults to False
        :return: List of Issues from RegScale
        :rtype: List[Issue]
        """
        api = Api()
        url = urljoin(app.config["domain"], "/api/{model_slug}/batchcreate")
        results = []
        api.logger.info("Creating %i new issue(s) in RegScale...", len(issues))
        with Progress(transient=False) as progress:
            task = progress.add_task(f"Creating {len(issues)} new issue(s) in RegScale...", total=len(issues))
            if batch:
                # Chunk list into batches
                batches = [issues[i : i + batch_size] for i in range(0, len(issues), batch_size)]
                for my_batch in batches:
                    res = api.post(url=url.format(model_slug="issues"), json=[iss.dict() for iss in my_batch])
                    if not res.ok:
                        app.logger.error(
                            "%i: %s\nError creating batch of issues: %s",
                            res.status_code,
                            res.text,
                            res.reason,
                        )
                    results.append(res)
                    progress.update(task, advance=len(my_batch))
            else:
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = [
                        executor.submit(
                            issue.create,
                        )
                        for issue in issues
                    ]
                    for future in as_completed(futures):
                        issue = future.result()
                        results.append(issue)
                        progress.update(task, advance=1)
        return results

    @staticmethod
    def bulk_update(
        app: Application,
        issues: List["Issue"],
        max_workers: int = 10,
        batch_size: int = 100,
        batch: bool = False,
    ) -> List["Issue"]:
        """
        Bulk update issues using the RegScale API and ThreadPoolExecutor

        :param Application app: Application Instance
        :param List["Issue"] issues: List of issues to update
        :param int max_workers: Max Workers, defaults to 10
        :param int batch_size: Number of issues to update per batch, defaults to 100
        :param bool batch: Update issues in batches, defaults to False
        :return: List of Issues from RegScale
        :rtype: List[Issue]
        """
        api = Api()
        url = urljoin(app.config["domain"], "/api/{model_slug}/batchupdate")
        results = []
        api.logger.info("Updating %i issue(s) in RegScale...", len(issues))
        with Progress(transient=False) as progress:
            task = progress.add_task(f"Updating {len(issues)} issue(s) in RegScale...", total=len(issues))
            if batch:
                # Chunk list into batches
                batches = [issues[i : i + batch_size] for i in range(0, len(issues), batch_size)]
                for my_batch in batches:
                    res = api.put(url=url.format(model_slug="issues"), json=[iss.dict() for iss in my_batch])
                    if not res.ok:
                        app.logger.error(
                            "%i: %s\nError creating batch of issues: %s",
                            res.status_code,
                            res.text,
                            res.reason,
                        )
                    results.append(res)
                    progress.update(task, advance=len(my_batch))
            else:
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = [executor.submit(issue.save) for issue in issues]
                    for future in as_completed(futures):
                        issue = future.result()
                        results.append(issue)
                        progress.update(task, advance=1)

        return results

    @staticmethod
    def fetch_issues_by_parent(
        app: Application,
        regscale_id: int,
        regscale_module: str,
    ) -> List["Issue"]:
        """
        Find all issues by parent id and parent module

        :param Application app: Application Instance
        :param int regscale_id: Parent ID
        :param str regscale_module: Parent Module
        :return: List of issues from RegScale
        :rtype: List[Issue]
        """
        api = Api()
        body = f"""
                query {{
                    issues(take: 50, skip: 0, where: {{ parentModule: {{eq: "{regscale_module}"}} parentId: {{
                      eq: {regscale_id}
                    }}}}) {{
                    items {{
                        {Issue.build_graphql_fields()}
                    }}
                    pageInfo {{
                        hasNextPage
                    }}
                    ,totalCount}}
                }}
                """
        try:
            existing_issues = api.graph(query=body)["issues"]["items"]
        except (JSONDecodeError, TypeError, KeyError):
            existing_issues = []
        return [Issue(**issue) for issue in existing_issues]

    @staticmethod
    def fetch_issues_by_ssp(
        app: Optional[Application],
        ssp_id: int,
        status: Optional[str] = None,
    ) -> List["Issue"]:
        """
        Find all issues by parent id and parent module

        :param Application app: Application Instance
        :param int ssp_id: RegScale SSP Id
        :param Optional[str] status: Issue Status, defaults to None
        :return: List of Issues from RegScale SSP
        :rtype: List[Issue]
        """
        api = Api()
        where_conditions = [f"securityPlanId: {{eq: {ssp_id}}}"]
        if status:
            where_conditions.append(f'status: {{eq: "{status}"}}')
        where_str = ", ".join(where_conditions)
        body = f"""
                query {{
                    issues(take: 50, skip: 0, where: {{ {where_str} }}) {{
                    items {{
                        {Issue.build_graphql_fields()}
                    }}
                    pageInfo {{
                        hasNextPage
                    }}
                    totalCount
                    }}
                }}
                """
        try:
            existing_issues = api.graph(query=body)["issues"]["items"]
        except (JSONDecodeError, TypeError, KeyError):
            existing_issues = []
        return [Issue(**issue) for issue in existing_issues]

    @staticmethod
    def fetch_all_issues(
        app: Application,
    ) -> List["Issue"]:
        """
        Find all issues in RegScale

        :param Application app: Application Instance
        :return: List of Issues from RegScale
        :rtype: List[Issue]
        """
        api = Api()
        body = f"""
                    query {{
                        issues(take: 50, skip: 0) {{
                        items {{
                            {Issue.build_graphql_fields()}
                        }}
                        pageInfo {{
                            hasNextPage
                        }}
                        ,totalCount}}
                    }}
                    """
        try:
            api.logger.info("Retrieving all issues from RegScale...")
            existing_issues = api.graph(query=body)["issues"]["items"]
            api.logger.info("Retrieved %i issue(s) from RegScale.", len(existing_issues))
        except (JSONDecodeError, KeyError):
            existing_issues = []
        return [Issue(**issue) for issue in existing_issues]

    @staticmethod
    def fetch_issue_by_id(
        app: Application,
        issue_id: int,
    ) -> Optional["Issue"]:
        """
        Find a RegScale issue by its id

        :param Application app: Application Instance
        :param int issue_id: RegScale Issue Id
        :return: Issue from RegScale or None if it doesn't exist
        :rtype: Optional[Issue]
        """
        api = Api()
        issue_response = api.get(url=f"{app.config['domain']}/api/issues/{issue_id}")
        issue = None
        try:
            issue = Issue(**issue_response.json())
        except JSONDecodeError:
            logger = create_logger()
            logger.warning("Unable to find issue with id %i", issue_id)
        return issue

    @staticmethod
    def fetch_issues_and_attachments_by_parent(
        parent_id: int,
        parent_module: str,
        fetch_attachments: Optional[bool] = True,
        save_issues: Optional[bool] = True,
    ) -> Tuple[List["Issue"], Optional[Dict[int, List["File"]]]]:
        """
        Fetch all issues from RegScale for the provided parent record

        :param int parent_id: Parent record ID in RegScale
        :param str parent_module: Parent record module in RegScale
        :param Optional[Application] app: Application object, deprecated 3.26.2024, defaults to None
        :param Optional[bool] fetch_attachments: Whether to fetch attachments from RegScale, defaults to True
        :param Optional[bool] save_issues: Save RegScale issues to a .json in artifacts, defaults to True
        :return: List of RegScale issues, dictionary of issue's attachments as File objects
        :rtype: Tuple[List[Issue], Optional[Dict[int, List[File]]]]
        """
        from regscale.models import File

        attachments: Optional[Dict[int, List[File]]] = None
        logger = create_logger()
        # get the existing issues for the parent record that are already in RegScale
        logger.info("Fetching full issue list from RegScale %s #%i.", parent_module, parent_id)
        issues_data = Issue().get_all_by_parent(
            parent_id=parent_id,
            parent_module=parent_module,
        )

        # check for null/not found response
        if len(issues_data) == 0:
            logger.warning(
                "No existing issues for this RegScale record #%i in %s.",
                parent_id,
                parent_module,
            )
        else:
            if fetch_attachments:
                # get the attachments for the issue
                api = Api()
                attachments = {
                    issue.id: files
                    for issue in issues_data
                    if (
                        files := File.get_files_for_parent_from_regscale(
                            parent_id=issue.id,
                            parent_module="issues",
                            api=api,
                        )
                    )
                }
            logger.info(
                "Found %i issue(s) from RegScale %s #%i for processing.",
                len(issues_data),
                parent_module,
                parent_id,
            )
            if save_issues:
                # write issue data to a json file
                check_file_path("artifacts")
                file_name = "existingRegScaleIssues.json"
                file_path = Path("./artifacts") / file_name
                save_data_to(
                    file=file_path,
                    data=[issue.dict() for issue in issues_data],
                    output_log=False,
                )
                logger.info(
                    "Saved RegScale issue(s) for %s #%i, see %s", parent_module, parent_id, str(file_path.absolute())
                )
        return issues_data, attachments

    @classmethod
    def get_open_issues_ids_by_implementation_id(
        cls, plan_id: int, is_component: Optional[bool] = False
    ) -> Dict[int, List[OpenIssueDict]]:
        """
        Get all open issues by implementation id for a given security plan with optimized performance and caching

        :param int plan_id: The ID of the parent
        :param bool is_component: Optional[bool] Defaults to False
        :return: A dictionary of control ids and their associated issue ids
        :rtype: Dict[int, List[OpenIssueDict]]
        """
        import logging

        cache_disabled = cls._is_cache_disabled()
        use_cache: bool = not cache_disabled

        logger = logging.getLogger("regscale")
        # Check cache first
        if use_cache:
            cached_data = cls._get_from_cache(plan_id)
            if cached_data is not None:
                logger.info(f"Using cached open issues data for security plan {plan_id}")
                return cached_data

        # Performance optimization: Use larger batch size and optimize query
        take = 50  # Increased from 50 to reduce API roundtrips
        skip = 0
        control_issues: Dict[int, List[OpenIssueDict]] = defaultdict(list)

        start_time = time.time()
        logger.info(f"Fetching open issues for controls and for security plan {plan_id}...")

        module_str = "component" if is_component else "security plan"
        logger.info(
            f"Fetching open issues for controls and for {module_str} {plan_id}...",
        )
        supports_multiple_controls: bool = cls.is_multiple_controls_supported()

        # Optimize field selection - only get what we need
        if supports_multiple_controls:
            fields = "id, otherIdentifier, integrationFindingId, controlImplementations { id }"
        else:
            fields = "id, controlId, otherIdentifier, integrationFindingId"

        total_fetched = 0

        try:
            while True:
                query = f"""
                    query GetOpenIssuesByPlanOrComponent {{
                        {cls.get_module_string()}(
                            skip: {skip},
                            take: {take},
                            where: {{
                                {"componentId" if is_component else "securityPlanId"}: {{eq: {plan_id}}},
                                status: {{eq: "Open"}}
                            }}
                        ) {{
                            items {{ {fields} }}
                            pageInfo {{ hasNextPage }}
                            totalCount
                        }}
                    }}
                """

                response = cls._get_api_handler().graph(query)
                items = response.get(cls.get_module_string(), {}).get("items", [])
                total_count = response.get(cls.get_module_string(), {}).get("totalCount", 0)

                # Log progress for large datasets
                if total_count > 1000:
                    logger.info(
                        f"Processing batch {skip // take + 1} - fetched {len(items)} items ({skip + len(items)}/{total_count})"
                    )

                for item in items:
                    issue_dict = OpenIssueDict(
                        id=item["id"],
                        otherIdentifier=item.get("otherIdentifier", ""),
                        integrationFindingId=item.get("integrationFindingId", ""),
                    )

                    if supports_multiple_controls and item.get("controlImplementations"):
                        for control in item.get("controlImplementations", []):
                            control_issues[control["id"]].append(issue_dict)
                    elif item.get("controlId"):
                        control_issues[item["controlId"]].append(issue_dict)

                total_fetched += len(items)
                if not response.get(cls.get_module_string(), {}).get("pageInfo", {}).get("hasNextPage", False):
                    break
                skip += take

        except Exception as e:
            logger.error(f"Error fetching open issues for security plan {plan_id}: {e}")
            # Return empty dict on error to prevent breaking the calling code
            return defaultdict(list)

        elapsed_time = time.time() - start_time
        logger.info(
            f"Finished fetching {total_fetched} open issue(s) for {len(control_issues)} control(s) "
            f"in security plan {plan_id} - took {elapsed_time:.2f} seconds"
        )

        # Cache the results
        if use_cache:
            cls._cache_data(plan_id, control_issues)

        return control_issues

    @classmethod
    def get_sort_position_dict(cls) -> Dict[str, int]:
        """
        Overrides the base method.

        :return: The sort position in the list of properties
        :rtype: Dict[str, int]
        """
        return {
            "id": 1,
            "title": 2,
            "severityLevel": 3,
            "issueOwnerId": 4,
            "dueDate": 5,
            "uuid": -1,
            "dateCreated": 6,
            "description": 7,
            "issueOwner": -1,
            "costEstimate": 9,
            "levelOfEffort": 10,
            "identification": 11,
            "capStatus": 12,
            "sourceReport": 13,
            "status": 14,
            "dateCompleted": 15,
            "activitiesObserved": 16,
            "failuresObserved": 17,
            "requirementsViolated": 18,
            "safetyImpact": 19,
            "securityImpact": 20,
            "qualityImpact": 21,
            "facility": -1,
            "facilityId": -1,
            "org": -1,
            "orgId": -1,
            "controlId": 26,
            "assessmentId": 27,
            "requirementId": 28,
            "securityPlanId": 29,
            "projectId": 30,
            "supplyChainId": 31,
            "policyId": 32,
            "componentId": 33,
            "incidentId": 34,
            "jiraId": 35,
            "serviceNowId": 36,
            "wizId": 37,
            "burpId": 38,
            "defenderId": 39,
            "defenderAlertId": 40,
            "defenderCloudId": 41,
            "salesforceId": 42,
            "prismaId": 43,
            "tenableId": 44,
            "tenableNessusId": 45,
            "qualysId": 46,
            "pluginId": 47,
            "cve": 48,
            "assetIdentifier": 49,
            "falsePositive": 50,
            "operationalRequirement": 51,
            "autoApproved": 52,
            "kevList": 53,
            "dateFirstDetected": 54,
            "changes": 55,
            "vendorDependency": 56,
            "vendorName": 57,
            "vendorLastUpdate": 58,
            "vendorActions": 59,
            "deviationRationale": 60,
            "parentId": 61,
            "parentModule": 62,
            "createdBy": -1,
            "createdById": -1,
            "lastUpdatedBy": -1,
            "lastUpdatedById": -1,
            "dateLastUpdated": -1,
            "securityChecks": 63,
            "recommendedActions": 64,
            "isPublic": 65,
            "dependabotId": 66,
            "isPoam": 67,
            "originalRiskRating": 68,
            "adjustedRiskRating": 69,
            "bRiskAdjustment": 70,
            "basisForAdjustment": 71,
        }

    @classmethod
    def get_enum_values(cls, field_name: str) -> List[Union[IssueSeverity, IssueStatus, str]]:
        """
        Overrides the base method.

        :param str field_name: The property name to provide enum values for
        :return: List of enum values or strings
        :rtype: List[Union[IssueSeverity, IssueStatus, str]]
        """
        if field_name == "severityLevel":
            return [severity.__str__() for severity in IssueSeverity]
        if field_name == "status":
            return [status.__str__() for status in IssueStatus]
        if field_name == "identification":
            return [
                "A-123 Review",
                "Assessment/Audit (External)",
                "Assessment/Audit (Internal)",
                "Critical Control Review",
                "FDCC/USGCB",
                "GAO Audit",
                "IG Audit",
                "Incidnet Response Lessons Learned",
                "ITAR",
                "Other",
                "Penetration Test",
                "Risk Assessment",
                "Security Authorization",
                "Security Control Assessment",
                "Vulnerability Assessment",
            ]
        return cls.get_bool_enums(field_name)

    @classmethod
    def get_lookup_field(cls, field_name: str) -> str:
        """
        Overrides the base method.

        :param str field_name: The property name to provide enum values for
        :return: The field name to look up
        :rtype: str
        """
        lookup_fields = {"issueOwnerId": "user", "facilityId": "facilities", "orgId": "organizations"}
        if field_name in lookup_fields.keys():
            return lookup_fields[field_name]
        return ""

    @classmethod
    def is_date_field(cls, field_name: str) -> bool:
        """
        Overrides the base method.

        :param str field_name: The property name to provide enum values for
        :return: If the field should be formatted as a date
        :rtype: bool
        """
        return field_name in ["dueDate", "dateCreated", "dateCompleted", "dateFirstDetected"]

    # pylint: disable=C0301
    @classmethod
    def get_export_query(cls, app: Application, parent_id: int, parent_module: str) -> List[Dict[str, Any]]:
        """
        Overrides the base method.

        :param Application app: RegScale Application object
        :param int parent_id: RegScale ID of parent
        :param str parent_module: Module of parent
        :return: GraphQL response from RegScale
        :rtype: List[Dict[str, Any]]
        """
        body = """
                query {
                        issues (skip: 0, take: 50, where: {parentId: {eq: parent_id} parentModule: {eq: "parent_module"}}) {
                          items {
                           id
                           issueOwnerId
                           issueOwner {
                             firstName
                             lastName
                             userName
                           }
                           title
                           dateCreated
                           description
                           severityLevel
                           costEstimate
                           levelOfEffort
                           dueDate
                           identification
                           status
                           dateCompleted
                           activitiesObserved
                           failuresObserved
                           requirementsViolated
                           safetyImpact
                           securityImpact
                           qualityImpact
                           securityChecks
                           recommendedActions
                           isPoam
                           parentId
                           parentModule
                          }
                          totalCount
                          pageInfo {
                            hasNextPage
                          }
                        }
                     }
                    """.replace(
            "parent_module", parent_module
        ).replace(
            "parent_id", str(parent_id)
        )

        api = Api()
        existing_issue_data = api.graph(query=body)

        if existing_issue_data["issues"]["totalCount"] > 0:
            raw_data = existing_issue_data["issues"]["items"]
            moded_data = []
            for a in raw_data:
                moded_data.append(build_issue_dict_from_query(a))
            return moded_data
        return []

    # pylint: emable=C0301

    @classmethod
    def find_by_service_now_id(cls, snow_id: str) -> List["Issue"]:
        """
        Find issues by its serviceNowId

        :param str snow_id: The serviceNowId to search for
        :return: The found Issues
        :rtype: List[Issue]
        """
        api_handler = cls._get_api_handler()
        endpoint = cls.get_endpoint("find_by_service_now_id").format(id=snow_id)

        response = api_handler.get(endpoint)
        issues: List["Issue"] = cls._handle_list_response(response)
        return issues

    @classmethod
    def use_query(cls) -> bool:
        """
        Overrides the base method.

        :return: Whether to use query
        :rtype: bool
        """
        return True

    @classmethod
    def get_extra_fields(cls) -> List[str]:
        """
        Overrides the base method.

        :return: List of extra field names
        :rtype: List[str]
        """
        return []

    @classmethod
    def get_include_fields(cls) -> List[str]:
        """
        Overrides the base method.

        :return: List of field names to include
        :rtype: List[str]
        """
        return []

    @field_validator("riskAdjustment")
    def validate_risk_adjustment(cls, v: str) -> str:
        """
        Validates the riskAdjustment field.

        :param str v: The value to validate
        :raise ValueError: If the value is not valid

        :return: The validated values
        :rtype: str

        """
        allowed_values = ["No", "Yes", "Pending", None]
        if v not in allowed_values:
            raise ValueError(f"riskAdjustment must be one of {allowed_values}")
        return v

    # New method to determine and set isPoam based on NIST/FedRAMP criteria
    def set_is_poam(
        self,
        config: Optional[Dict[str, Any]] = None,
        standard: str = "fedramp",
        current_date: Optional[datetime.datetime] = None,
    ) -> None:
        """
        Sets the isPoam field based on NIST 800-53 or FedRAMP criteria, preserving historical POAM status.

        Criteria:
        - Preserves isPoam=True for imported data, even if closed, for reporting purposes.
        - For new issues:
          - Skips if false positive, operational requirement, or deviation rationale exists.
          - FedRAMP: High/Critical issues are POAMs if open; scan-based issues are POAMs if overdue; non-scan issues are POAMs if open.
          - NIST: POAM for any open deficiency unless accepted as residual risk.
          - Uses config thresholds (e.g., {'critical': 30, 'high': 90, 'medium': 90, 'low': 365, 'status': 'Open'}).

        Args:
            config: Optional dictionary with severity thresholds and status from init.yaml.
                    Defaults to FedRAMP: {'critical': 30, 'high': 30, 'medium': 90, 'low': 180, 'status': 'Open'}.
                    For NIST, uses {'critical': 30, 'high': 90, 'medium': 90, 'low': 180, 'status': 'Open'}.
            standard: 'fedramp' (default) or 'nist'.
            current_date: Optional datetime for calculation (defaults to current time).

        Returns:
            None: Sets the isPoam attribute directly.
        """
        # Use current time if not provided
        current_date = current_date or datetime.datetime.now()

        # Preserve historical POAM status for imported data
        if self.isPoam:
            return

        # Define open statuses
        open_statuses = {
            IssueStatus.Open,
            IssueStatus.Delayed,
            IssueStatus.PendingVerification,
            IssueStatus.VendorDependency,
            IssueStatus.PendingApproval,
        }

        # Skip if issue is accepted as residual risk
        if self.falsePositive or self.operationalRequirement or self.deviationRationale:
            self.isPoam = False
            return

        # Load default thresholds based on standard if config is not provided
        config = config or (
            {"critical": 30, "high": 30, "medium": 90, "low": 180, "status": "Open"}
            if standard == "fedramp"
            else {"critical": 30, "high": 90, "medium": 90, "low": 180, "status": "Open"}
        )

        # Map severity to remediation days
        severity_map = {
            IssueSeverity.Critical: config.get("critical", 30),
            IssueSeverity.High: config.get("high", 90),
            IssueSeverity.Moderate: config.get("medium", 90),
            IssueSeverity.Low: config.get("low", 365),
            IssueSeverity.NotAssigned: config.get("low", 365),
        }

        # Normalize severity
        severity = (
            IssueSeverity(self.severityLevel)
            if self.severityLevel in {s.value for s in IssueSeverity}
            else IssueSeverity.NotAssigned
        )
        threshold_days = severity_map[severity]

        # Get detection date
        detection_date_str = self.dateFirstDetected or self.dateCreated
        if not detection_date_str:
            self.isPoam = False
            return

        try:
            detection_date = datetime.datetime.strptime(detection_date_str, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            try:
                detection_date = datetime.datetime.strptime(detection_date_str, "%Y-%m-%d")
            except ValueError:
                self.isPoam = False
                return

        days_since_detection = (current_date - detection_date).days

        # Define scan sources
        scan_sources = {"Vulnerability Assessment", "FDCC/USGCB", "Penetration Test"}
        is_scan = self.identification in scan_sources

        # Apply standard-specific logic
        if standard == "fedramp":
            # FedRAMP: High/Critical are always POAMs if open
            if severity in {IssueSeverity.High, IssueSeverity.Critical}:
                self.isPoam = self.status in open_statuses
            # Scan-based: POAM if overdue
            elif is_scan:
                self.isPoam = days_since_detection > threshold_days
            # Non-scan: POAM if open
            else:
                self.isPoam = self.status in open_statuses

            # Handle vendor dependencies
            if self.vendorDependency and self.vendorLastUpdate:
                try:
                    vendor_date = datetime.datetime.strptime(self.vendorLastUpdate, "%Y-%m-%dT%H:%M:%S")
                    days_since_vendor = (current_date - vendor_date).days
                    self.isPoam = days_since_vendor > threshold_days
                except ValueError:
                    pass  # Fall back to detection date logic

        else:  # NIST 800-53
            # NIST: POAM for any open deficiency
            self.isPoam = self.status in open_statuses

        # Apply status filter from config if specified
        if "status" in config:
            self.isPoam = self.isPoam and self.status == config["status"]


def build_issue_dict_from_query(a: Dict[str, Any]) -> Dict[str, Any]:
    """
    This method takes in a single record from the graphQL query and reformat
    it into an issue dict.

    :param Dict[str, Any] a: A single record returned from the query
    :return: Reformatted dict for the data needs
    :rtype: Dict[str, Any]
    """
    modeled_item = {}
    modeled_item["id"] = a["id"]
    modeled_item["issueOwnerId"] = (
        (
            str(a["issueOwner"]["lastName"]).strip()
            + ", "
            + str(a["issueOwner"]["firstName"]).strip()
            + " ("
            + str(a["issueOwner"]["userName"]).strip()
            + ")"
        )
        if a["issueOwner"]
        else "None"
    )
    modeled_item["title"] = a["title"]
    modeled_item["dateCreated"] = reformat_str_date(a["dateCreated"])
    modeled_item["isPoam"] = a["isPoam"]
    modeled_item["description"] = a["description"] if a["description"] else "None"
    modeled_item["severityLevel"] = a["severityLevel"]
    modeled_item["costEstimate"] = a["costEstimate"] if a["costEstimate"] and a["costEstimate"] != "None" else 0.00
    modeled_item["levelOfEffort"] = a["levelOfEffort"] if a["levelOfEffort"] and a["levelOfEffort"] != "None" else 0
    modeled_item["dueDate"] = reformat_str_date(a["dueDate"])
    modeled_item["identification"] = a["identification"] if a["identification"] else "None"
    modeled_item["status"] = a["status"] if a["status"] else "None"
    modeled_item["dateCompleted"] = reformat_str_date(a["dateCompleted"]) if a["dateCompleted"] else ""
    modeled_item["activitiesObserved"] = blank_if_empty(a, "activitiesObserved")
    modeled_item["failuresObserved"] = blank_if_empty(a, "failuresObserved")
    modeled_item["requirementsViolated"] = blank_if_empty(a, "requirementsViolated")
    modeled_item["safetyImpact"] = blank_if_empty(a, "safetyImpact")
    modeled_item["securityImpact"] = blank_if_empty(a, "securityImpact")
    modeled_item["qualityImpact"] = blank_if_empty(a, "qualityImpact")
    modeled_item["securityChecks"] = blank_if_empty(a, "securityChecks")
    modeled_item["recommendedActions"] = blank_if_empty(a, "recommendedActions")
    return modeled_item


def blank_if_empty(data: dict, field: str) -> str:
    """
    This method will return the value of the specified field from the passed dict if it exists. If
    it doesn't, an empty string will be returned.

    :param dict data: the data to be queried for the field
    :param str field: the field to return if it exists in the dict
    :return: str the field value or an empty string
    :rtype: str
    """
    return data.get(field, "")
