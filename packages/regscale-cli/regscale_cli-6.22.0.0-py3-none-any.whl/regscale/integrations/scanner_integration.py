#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scanner Integration Class"""
from __future__ import annotations

import concurrent.futures
import dataclasses
import enum
import hashlib
import json
import logging
import threading
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Dict, Generic, Iterator, List, Optional, Set, TypeVar, Union

from rich.progress import Progress, TaskID

from regscale.core.app.application import Application
from regscale.core.app.utils.api_handler import APIHandler
from regscale.core.app.utils.app_utils import create_progress_object, get_current_datetime
from regscale.core.app.utils.catalog_utils.common import objective_to_control_dot
from regscale.core.utils.date import date_obj, date_str, datetime_str, days_from_today, get_day_increment
from regscale.integrations.commercial.durosuite.process_devices import scan_durosuite_devices
from regscale.integrations.commercial.durosuite.variables import DuroSuiteVariables
from regscale.integrations.commercial.stig_mapper_integration.mapping_engine import StigMappingEngine as STIGMapper
from regscale.integrations.public.cisa import pull_cisa_kev
from regscale.integrations.variables import ScannerVariables
from regscale.models import DateTimeEncoder, OpenIssueDict, Property, regscale_models
from regscale.utils.threading import ThreadSafeDict, ThreadSafeList

logger = logging.getLogger(__name__)

K = TypeVar("K")  # Key type
V = TypeVar("V")  # Value type


def get_thread_workers_max() -> int:
    """
    Get the maximum number of thread workers

    :return: The maximum number of thread workers
    :rtype: int
    """
    return ScannerVariables.threadMaxWorkers


def issue_due_date(
    severity: regscale_models.IssueSeverity,
    created_date: str,
    critical: Optional[int] = None,
    high: Optional[int] = None,
    moderate: Optional[int] = None,
    low: Optional[int] = None,
    title: Optional[str] = "",
    config: Optional[Dict[str, Dict]] = None,
) -> str:
    """
    Calculate the due date for an issue based on its severity and creation date.

    :param regscale_models.IssueSeverity severity: The severity of the issue.
    :param str created_date: The creation date of the issue.
    :param Optional[int] critical: Days until due for high severity issues.
    :param Optional[int] high: Days until due for high severity issues.
    :param Optional[int] moderate: Days until due for moderate severity issues.
    :param Optional[int] low: Days until due for low severity issues.
    :param Optional[str] title: The title of the Integration.
    :param Optional[Dict[str, Dict]] config: Configuration options for the due date calculation.
    :return: The due date for the issue.
    :rtype: str
    """
    if critical is None:
        critical = ScannerVariables.issueDueDates.get("critical", 30)
    if high is None:
        high = ScannerVariables.issueDueDates.get("high", 60)
    if moderate is None:
        moderate = ScannerVariables.issueDueDates.get("moderate", 120)
    if low is None:
        low = ScannerVariables.issueDueDates.get("low", 364)

    if config is None:
        config = {}

    due_date_map = {
        regscale_models.IssueSeverity.Critical: critical,
        regscale_models.IssueSeverity.High: high,
        regscale_models.IssueSeverity.Moderate: moderate,
        regscale_models.IssueSeverity.Low: low,
    }

    if title and config:
        # if title in a config key, use that key
        issues_dict = config.get("issues", {})
        matching_key = next((key.lower() for key in issues_dict if title.lower() in key.lower()), None)
        if matching_key:
            title_config = issues_dict.get(matching_key, {})
            due_date_map = {
                regscale_models.IssueSeverity.Critical: title_config.get("critical", critical),
                regscale_models.IssueSeverity.High: title_config.get("high", high),
                regscale_models.IssueSeverity.Moderate: title_config.get("moderate", moderate),
                regscale_models.IssueSeverity.Low: title_config.get("low", low),
            }

    days = due_date_map.get(severity, low)
    return date_str(get_day_increment(start=created_date, days=days))


class ManagedDefaultDict(Generic[K, V]):
    """
    A thread-safe default dictionary that uses a multiprocessing Manager.

    :param default_factory: A callable that produces default values for missing keys
    """

    def __init__(self, default_factory):
        self.store: ThreadSafeDict[Any, Any] = ThreadSafeDict()  # type: ignore[type-arg]
        self.default_factory = default_factory

    def __getitem__(self, key: Any) -> Any:
        """
        Get the item from the store

        :param Any key: Key to get the item from the store
        :return: Value from the store
        :rtype: Any
        """
        if key not in self.store:
            self.store[key] = self.default_factory()
        return self.store[key]

    def __setitem__(self, key: Any, value: Any) -> None:
        """
        Set the item in the store

        :param Any key: Key to set the item in the store
        :param Any value: Value to set in the store
        :rtype: None
        """
        self.store[key] = value

    def __contains__(self, key: Any) -> bool:
        """
        Check if the key is in the store

        :param Any key: Key to check in the store
        :return: Whether the key is in the store
        :rtype: bool
        """
        return key in self.store

    def __len__(self) -> int:
        """
        Get the length of the store

        :return: Number of items in the store
        :rtype: int
        """
        return len(self.store)

    def get(self, key: Any, default: Optional[Any] = None) -> Optional[Any]:
        """
        Get the value from the store

        :param Any key: Key to get the value from the store
        :param Optional[Any] default: Default value to return if the key is not in the store, defaults to None
        :return: The value from the store, or the default value
        :rtype: Optional[Any]
        """
        if key not in self.store:
            return default
        return self.store[key]

    def items(self) -> Any:
        """
        Get the items from the store

        :return: Items from the store
        :rtype: Any
        """
        return self.store.items()

    def keys(self) -> Any:
        """
        Get the keys from the store

        :return: Keys from the store
        :rtype: Any
        """
        return self.store.keys()

    def values(self) -> Any:
        """
        Get the values from the store

        :return: Values in the store
        :rtype: Any
        """
        return self.store.values()

    def update(self, *args, **kwargs) -> None:
        """
        Update the store

        :rtype: None
        """
        self.store.update(*args, **kwargs)


@dataclasses.dataclass
class IntegrationAsset:
    """
    Dataclass for integration assets.

    Represents an asset to be integrated, including its metadata and associated components.
    If a component does not exist, it will be created based on the names provided in ``component_names``.

    :param str name: The name of the asset.
    :param str identifier: A unique identifier for the asset.
    :param str asset_type: The type of the asset.
    :param str asset_category: The category of the asset.
    :param str component_type: The type of the component, defaults to ``ComponentType.Hardware``.
    :param Optional[int] parent_id: The ID of the parent asset, defaults to None.
    :param Optional[str] parent_module: The module of the parent asset, defaults to None.
    :param str status: The status of the asset, defaults to "Active (On Network)".
    :param str date_last_updated: The last update date of the asset, defaults to the current datetime.
    :param Optional[str] asset_owner_id: The ID of the asset owner, defaults to None.
    :param Optional[str] mac_address: The MAC address of the asset, defaults to None.
    :param Optional[str] fqdn: The Fully Qualified Domain Name of the asset, defaults to None.
    :param Optional[str] ip_address: The IP address of the asset, defaults to None.
    :param List[str] component_names: A list of strings that represent the names of the components associated with the
    asset, components will be created if they do not exist.
    """

    name: str
    identifier: str
    asset_type: str
    asset_category: str
    component_type: str = regscale_models.ComponentType.Hardware
    description: str = ""
    parent_id: Optional[int] = None
    parent_module: Optional[str] = None
    status: regscale_models.AssetStatus = regscale_models.AssetStatus.Active
    date_last_updated: str = dataclasses.field(default_factory=get_current_datetime)
    asset_owner_id: Optional[str] = None
    mac_address: Optional[str] = None
    fqdn: Optional[str] = None
    ip_address: Optional[str] = None
    ipv6_address: Optional[str] = None
    component_names: List[str] = dataclasses.field(default_factory=list)
    is_virtual: bool = True

    # Additional fields from Wiz integration
    external_id: Optional[str] = None
    management_type: Optional[str] = None
    software_vendor: Optional[str] = None
    software_version: Optional[str] = None
    software_name: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    other_tracking_number: Optional[str] = None
    serial_number: Optional[str] = None
    asset_tag_number: Optional[str] = None
    is_public_facing: Optional[bool] = None
    azure_identifier: Optional[str] = None
    disk_storage: Optional[int] = None
    cpu: Optional[int] = None
    ram: Optional[int] = None
    operating_system: Optional[regscale_models.AssetOperatingSystem] = None
    os_version: Optional[str] = None
    end_of_life_date: Optional[str] = None
    vlan_id: Optional[str] = None
    uri: Optional[str] = None
    aws_identifier: Optional[str] = None
    google_identifier: Optional[str] = None
    other_cloud_identifier: Optional[str] = None
    patch_level: Optional[str] = None
    cpe: Optional[str] = None
    is_latest_scan: Optional[bool] = None
    is_authenticated_scan: Optional[bool] = None
    system_administrator_id: Optional[str] = None
    scanning_tool: Optional[str] = None

    source_data: Optional[Dict[str, Any]] = None
    url: Optional[str] = None
    software_function: Optional[str] = None
    baseline_configuration: Optional[str] = None
    ports_and_protocols: List[Dict[str, Any]] = dataclasses.field(default_factory=list)
    software_inventory: List[Dict[str, Any]] = dataclasses.field(default_factory=list)

    def __post_init__(self):
        if self.ip_address in ["", "0.0.0.0"]:
            self.ip_address = None


@dataclasses.dataclass
class IntegrationFinding:
    """
    Dataclass for integration findings.

    :param list[str] control_labels: A list of control labels associated with the finding.
    :param str title: The title of the finding.
    :param str category: The category of the finding.
    :param regscale_models.IssueSeverity severity: The severity of the finding, based on regscale_models.IssueSeverity.
    :param str description: A description of the finding.
    :param regscale_models.ControlTestResultStatus status: The status of the finding, based on
    regscale_models.ControlTestResultStatus.
    :param str priority: The priority of the finding, defaults to "Medium".
    :param str issue_type: The type of issue, defaults to "Risk".
    :param str issue_title: The title of the issue, defaults to an empty string.
    :param str date_created: The creation date of the finding, defaults to the current datetime.
    :param str due_date: The due date of the finding, defaults to 60 days from the current datetime.
    :param str date_last_updated: The last update date of the finding, defaults to the current datetime.
    :param str external_id: An external identifier for the finding, defaults to an empty string.
    :param str gaps: A description of any gaps identified, defaults to an empty string.
    :param str observations: Observations related to the finding, defaults to an empty string.
    :param str evidence: Evidence supporting the finding, defaults to an empty string.
    :param str identified_risk: The risk identified by the finding, defaults to an empty string.
    :param str impact: The impact of the finding, defaults to an empty string.
    :param str recommendation_for_mitigation: Recommendations for mitigating the finding, defaults to an empty string.
    :param str asset_identifier: The identifier of the asset associated with the finding, defaults to an empty string.
    :param Optional[str] cci_ref: The Common Configuration Enumeration reference for the finding, defaults to None.
    :param str rule_id: The rule ID of the finding, defaults to an empty string.
    :param str rule_version: The version of the rule associated with the finding, defaults to an empty string.
    :param str results: The results of the finding, defaults to an empty string.
    :param Optional[str] comments: Additional comments related to the finding, defaults to None.
    :param Optional[str] source_report: The source report of the finding, defaults to None.
    :param Optional[str] point_of_contact: The point of contact for the finding, used to create property defaults to None.
    :param Optional[str] milestone_changes: Milestone Changes for the finding, defaults to None.
    :param Optional[str] adjusted_risk_rating: The adjusted risk rating of the finding, defaults to None.
    :param Optional[str] risk_adjustment: The risk adjustment of the finding, (Should be Yes, No, Pending), defaults to No.
    :param Optional[str] operational_requirements: The operational requirements of the finding, defaults to None.
    :param Optional[str] deviation_rationale: The rationale for any deviations from the finding, defaults to None.
    :param str baseline: The baseline of the finding, defaults to an empty string.
    :param str poam_comments: Comments related to the Plan of Action and Milestones (POAM) for the finding, defaults to
    :param Optional[int] vulnerability_id: The ID of the vulnerability associated with the finding, defaults to None.
    an empty string.
    :param Optional[str] basis_for_adjustment: The basis for adjusting the finding, defaults to None.
    :param Optional[str] vulnerability_number: STIG vulnerability number
    :param Optional[str] vulnerability_type: The type of vulnerability, defaults to None.
    :param Optional[str] plugin_id: The ID of the plugin associated with the finding, defaults to None.
    :param Optional[str] plugin_name: The name of the plugin associated with the finding, defaults to None.
    :param Optional[str] dns: The DNS name associated with the finding, defaults to None.
    :param int severity_int: The severity integer of the finding, defaults to 0.
    :param Optional[str] cve: The CVE of the finding, defaults to None.
    :param Optional[float] cvss_v3_score: The CVSS v3 score of the finding, defaults to None.
    :param Optional[float] cvss_v2_score: The CVSS v2 score of the finding, defaults to None.
    :param Optional[str] cvss_score: The CVSS score of the finding, defaults to None.
    :param Optional[str] cvss_v3_base_score: The CVSS v3 base score of the finding, defaults to None.
    :param Optional[str] ip_address: The IP address associated with the finding, defaults to None.
    :param Optional[str] first_seen: The first seen date of the finding, defaults to the current datetime.
    :param Optional[str] last_seen: The last seen date of the finding, defaults to the current datetime.
    :param Optional[str] oval_def: The OVAL definition of the finding, defaults to None.
    :param Optional[str] scan_date: The scan date of the finding, defaults to the current datetime.
    :param Optional[str] rule_id_full: The full rule ID of the finding, defaults to an empty string.
    :param Optional[str] group_id: The group ID of the finding, defaults to an empty string.
    :param Optional[str] vulnerable_asset: The vulnerable asset of the finding, defaults to None.
    :param Optional[str] remediation: The remediation of the finding, defaults to None.
    :param Optional[str] source_rule_id: The source rule ID of the finding, defaults to None.
    :param Optional[str] poam_id: The POAM ID of the finding, defaults to None.
    :param Optional[str] cvss_v3_vector: The CVSS v3 vector of the finding, defaults to None.
    :param Optional[str] cvss_v2_vector: The CVSS v2 vector of the finding, defaults to None.
    :param Optional[str] affected_os: The affected OS of the finding, defaults to None.
    :param Optional[str] image_digest: The image digest of the finding, defaults to None.
    :param Optional[str] affected_packages: The affected packages of the finding, defaults to None.
    :param Optional[str] installed_versions: The installed versions of the finding, defaults to None.
    :param Optional[str] fixed_versions: The fixed versions of the finding, defaults to None.
    :param Optional[str] fix_status: The fix status of the finding, defaults to None.
    :param Optional[str] build_version: The build version of the finding, defaults to None.
    """

    control_labels: List[str]
    title: str
    category: str
    plugin_name: str
    severity: regscale_models.IssueSeverity
    description: str
    status: Union[regscale_models.ControlTestResultStatus, regscale_models.ChecklistStatus, regscale_models.IssueStatus]
    priority: str = "Medium"

    # Vulns
    first_seen: str = dataclasses.field(default_factory=get_current_datetime)
    last_seen: str = dataclasses.field(default_factory=get_current_datetime)
    cve: Optional[str] = None
    cvss_v3_score: Optional[float] = None
    cvss_v2_score: Optional[float] = None
    ip_address: Optional[str] = None
    plugin_id: Optional[str] = None
    plugin_text: Optional[str] = None
    dns: Optional[str] = None
    severity_int: int = 0
    security_check: Optional[str] = None
    cvss_v3_vector: Optional[str] = None
    cvss_v2_vector: Optional[str] = None
    affected_os: Optional[str] = None
    package_path: Optional[str] = None
    image_digest: Optional[str] = None
    affected_packages: Optional[str] = None
    installed_versions: Optional[str] = None
    fixed_versions: Optional[str] = None
    fix_status: Optional[str] = None
    build_version: Optional[str] = None

    # Issues
    issue_title: str = ""
    issue_type: str = "Risk"
    date_created: str = dataclasses.field(default_factory=get_current_datetime)
    date_last_updated: str = dataclasses.field(default_factory=get_current_datetime)
    due_date: str = ""  # dataclasses.field(default_factory=lambda: date_str(days_from_today(60)))
    external_id: str = ""
    gaps: str = ""
    observations: str = ""
    evidence: str = ""
    identified_risk: str = ""
    impact: str = ""
    recommendation_for_mitigation: str = ""
    asset_identifier: str = ""
    comments: Optional[str] = None
    source_report: Optional[str] = None
    point_of_contact: Optional[str] = None
    milestone_changes: Optional[str] = None
    planned_milestone_changes: Optional[str] = None
    adjusted_risk_rating: Optional[str] = None
    risk_adjustment: str = "No"

    # Compliance fields
    assessment_id: Optional[int] = None
    operational_requirements: Optional[str] = None
    deviation_rationale: Optional[str] = None
    is_cwe: bool = False
    affected_controls: Optional[str] = None
    identification: Optional[str] = "Vulnerability Assessment"

    poam_comments: Optional[str] = None
    vulnerability_id: Optional[int] = None
    _control_implementation_ids: List[int] = dataclasses.field(default_factory=list)

    # Stig
    checklist_status: regscale_models.ChecklistStatus = dataclasses.field(
        default=regscale_models.ChecklistStatus.NOT_REVIEWED
    )
    cci_ref: Optional[str] = None
    rule_id: str = ""
    rule_version: str = ""
    results: str = ""
    baseline: str = ""
    vulnerability_number: str = ""
    oval_def: str = ""
    scan_date: str = ""
    rule_id_full: str = ""
    group_id: str = ""

    # Wiz
    vulnerable_asset: Optional[str] = None
    remediation: Optional[str] = None
    cvss_score: Optional[float] = None
    cvss_v3_base_score: Optional[float] = None
    source_rule_id: Optional[str] = None
    vulnerability_type: Optional[str] = None

    # CoalFire POAM
    basis_for_adjustment: Optional[str] = None
    poam_id: Optional[str] = None

    # Additional fields from Wiz integration
    vpr_score: Optional[float] = None

    # Extra data field for miscellaneous data
    extra_data: Dict[str, Any] = dataclasses.field(default_factory=dict)

    def __post_init__(self):
        """Validate and adjust types after initialization."""
        # Set default date values if empty
        if not self.first_seen:
            self.first_seen = get_current_datetime()
        if not self.last_seen:
            self.last_seen = get_current_datetime()
        if not self.scan_date:
            self.scan_date = get_current_datetime()

        # Validate the values of the dataclass
        if not self.title:
            self.title = "Unknown Issue"
        if not self.description:
            self.description = "No description provided"

        if self.plugin_name is None:
            self.plugin_name = self.cve or self.title
        if self.plugin_id is None:
            self.plugin_id = self.plugin_name

    def get_issue_status(self) -> regscale_models.IssueStatus:
        return (
            regscale_models.IssueStatus.Closed
            if (
                self.status == regscale_models.ControlTestResultStatus.PASS
                or self.status == regscale_models.IssueStatus.Closed
            )
            else regscale_models.IssueStatus.Open
        )

    def __eq__(self, other: Any) -> bool:
        """
        Check if the finding is equal to another finding

        :param Any other: The other finding to compare
        :return: Whether the findings are equal
        :rtype: bool
        """
        if not isinstance(other, IntegrationFinding):
            return NotImplemented
        return (self.title, self.category, self.external_id) == (other.title, other.category, other.external_id)

    def __hash__(self) -> int:
        """
        Get the hash of the finding

        :return: Hash of the finding
        :rtype: int
        """
        return hash((self.title, self.category, self.external_id))

    def is_valid(self) -> bool:
        """
        Determines if the finding is valid based on the presence of `date_last_updated` and `risk_adjustment`.

        :return: True if the finding is valid, False otherwise.
        :rtype: bool
        """
        # Check if these fields are not empty or None
        if not self.date_last_updated:
            logger.warning("Finding %s is missing date_last_updated, skipping..", self.poam_id)
            return False

        if not self.risk_adjustment:
            logger.warning("Finding %s is missing risk_adjustment, skipping..", self.poam_id)
            return False

        # Additional validation logic can be added here if needed
        # For example, ensure risk_adjustment is one of the allowed values ("Yes", "No", "Pending")
        allowed_risk_adjustments = {"Yes", "No", "Pending"}
        if self.risk_adjustment not in allowed_risk_adjustments:
            logger.warning("Finding %s has a disallowed risk adjustment, skipping..", self.poam_id)
            return False

        return True


class ScannerIntegrationType(str, enum.Enum):
    """
    Enumeration for scanner integration types.
    """

    CHECKLIST = "checklist"
    CONTROL_TEST = "control_test"
    VULNERABILITY = "vulnerability"


class FindingStatus(str, enum.Enum):
    OPEN = regscale_models.IssueStatus.Open
    CLOSED = regscale_models.IssueStatus.Closed
    FAIL = regscale_models.IssueStatus.Open
    PASS = regscale_models.IssueStatus.Closed
    NOT_APPLICABLE = regscale_models.IssueStatus.Closed
    NOT_REVIEWED = regscale_models.IssueStatus.Open


class ScannerIntegration(ABC):
    """
    Abstract class for scanner integrations.

    :param int plan_id: The ID of the security plan
    :param int tenant_id: The ID of the tenant, defaults to 1

    Configuration options available via kwargs:
    - suppress_asset_not_found_errors (bool): When True, suppresses "Asset not found" error messages
      that are commonly logged when assets referenced in findings don't exist in RegScale.
      This can help reduce log noise in environments with many missing assets.
    """

    stig_mapper = None
    # Basic configuration options
    options_map_assets_to_components: bool = False
    type: ScannerIntegrationType = ScannerIntegrationType.CONTROL_TEST
    title: str = "Scanner Integration"
    asset_identifier_field: str = "otherTrackingNumber"
    issue_identifier_field: str = ""
    _max_poam_id: Optional[int] = None  # Value holder for get_max_poam_id

    # Progress trackers
    asset_progress: Progress
    finding_progress: Progress

    # Processing counts
    num_assets_to_process: Optional[int] = None
    num_findings_to_process: Optional[int] = None

    # Lock registry
    _lock_registry: ThreadSafeDict = ThreadSafeDict()
    _global_lock = threading.Lock()  # Class-level lock
    _kev_data = ThreadSafeDict()  # Class-level lock
    _results = ThreadSafeDict()

    # Error handling
    errors: List[str] = []

    # Mapping dictionaries
    finding_status_map: dict[Any, regscale_models.IssueStatus] = {}
    checklist_status_map: dict[Any, regscale_models.ChecklistStatus] = {}
    finding_severity_map: dict[Any, regscale_models.IssueSeverity] = {}
    issue_to_vulnerability_map: dict[regscale_models.IssueSeverity, regscale_models.VulnerabilitySeverity] = {
        regscale_models.IssueSeverity.Low: regscale_models.VulnerabilitySeverity.Low,
        regscale_models.IssueSeverity.Moderate: regscale_models.VulnerabilitySeverity.Medium,
        regscale_models.IssueSeverity.High: regscale_models.VulnerabilitySeverity.High,
        regscale_models.IssueSeverity.Critical: regscale_models.VulnerabilitySeverity.Critical,
    }
    asset_map: dict[str, regscale_models.Asset] = {}
    # cci_to_control_map: dict[str, set[int]] = {}
    control_implementation_id_map: dict[str, int] = {}
    control_map: dict[int, str] = {}
    control_id_to_implementation_map: dict[int, int] = {}

    # Existing issues map
    existing_issue_ids_by_implementation_map: dict[int, List[OpenIssueDict]] = defaultdict(list)

    # Scan Date
    scan_date: str = ""
    enable_finding_date_update = False

    # Close Outdated Findings
    close_outdated_findings = True
    closed_count = 0

    # Error suppression options
    suppress_asset_not_found_errors = False

    def __init__(self, plan_id: int, tenant_id: int = 1, is_component: bool = False, **kwargs):
        """
        Initialize the ScannerIntegration.

        :param int plan_id: The ID of the security plan
        :param int tenant_id: The ID of the tenant, defaults to 1
        :param bool is_component: Whether this is a component integration
        :param kwargs: Additional keyword arguments
            - suppress_asset_not_found_errors (bool): If True, suppress "Asset not found" error messages
        """
        self.app = Application()
        self.alerted_assets: Set[str] = set()
        self.regscale_version: str = APIHandler().regscale_version  # noqa
        logger.debug(f"RegScale Version: {self.regscale_version}")
        self.plan_id: int = plan_id
        self.tenant_id: int = tenant_id
        self.is_component: bool = is_component

        # Set configuration options from kwargs
        self.suppress_asset_not_found_errors = kwargs.get("suppress_asset_not_found_errors", False)
        if self.is_component:
            self.component = regscale_models.Component.get_object(self.plan_id)
            self.parent_module: str = regscale_models.Component.get_module_string()
        else:
            self.parent_module: str = regscale_models.SecurityPlan.get_module_string()
        self.components: ThreadSafeList[Any] = ThreadSafeList()
        self.asset_map_by_identifier: ThreadSafeDict[str, regscale_models.Asset] = ThreadSafeDict()
        self.software_to_create: ThreadSafeList[regscale_models.SoftwareInventory] = ThreadSafeList()
        self.software_to_update: ThreadSafeList[regscale_models.SoftwareInventory] = ThreadSafeList()
        self.data_to_create: ThreadSafeList[regscale_models.Data] = ThreadSafeList()
        self.data_to_update: ThreadSafeList[regscale_models.Data] = ThreadSafeList()
        self.link_to_create: ThreadSafeList[regscale_models.Link] = ThreadSafeList()
        self.link_to_update: ThreadSafeList[regscale_models.Link] = ThreadSafeList()

        self.existing_issues_map: ThreadSafeDict[int, List[regscale_models.Issue]] = ThreadSafeDict()
        self.components_by_title: ThreadSafeDict[str, regscale_models.Component] = ThreadSafeDict()
        self.control_tests_map: ManagedDefaultDict[int, regscale_models.ControlTest] = ManagedDefaultDict(list)

        self.implementation_objective_map: ThreadSafeDict[str, int] = ThreadSafeDict()
        self.implementation_option_map: ThreadSafeDict[str, int] = ThreadSafeDict()
        self.control_implementation_map: ThreadSafeDict[int, regscale_models.ControlImplementation] = ThreadSafeDict()

        self.control_implementation_id_map = regscale_models.ControlImplementation.get_control_label_map_by_parent(
            parent_id=self.plan_id, parent_module=self.parent_module
        )
        self.control_map = {v: k for k, v in self.control_implementation_id_map.items()}
        self.existing_issue_ids_by_implementation_map = regscale_models.Issue.get_open_issues_ids_by_implementation_id(
            plan_id=self.plan_id, is_component=self.is_component
        )  # GraphQL Call
        self.control_id_to_implementation_map = regscale_models.ControlImplementation.get_control_id_map_by_parent(
            parent_id=self.plan_id, parent_module=self.parent_module
        )

        self.cci_to_control_map: ThreadSafeDict[str, set[int]] = ThreadSafeDict()
        self._no_ccis: bool = False
        self.cci_to_control_map_lock: threading.Lock = threading.Lock()

        self.assessment_map: ThreadSafeDict[int, regscale_models.Assessment] = ThreadSafeDict()
        self.assessor_id: str = self.get_assessor_id()
        self.asset_progress: Progress = create_progress_object()
        self.finding_progress: Progress = create_progress_object()
        self.stig_mapper = self.load_stig_mapper()
        kev_data = pull_cisa_kev()
        thread_safe_kev_data = ThreadSafeDict()
        thread_safe_kev_data.update(kev_data)
        self._kev_data = thread_safe_kev_data

    @classmethod
    def _get_lock(cls, key: str) -> threading.RLock:
        """
        Get or create a lock associated with a key.

        :param str key: The cache key
        :return: A reentrant lock
        :rtype: RLock
        """
        lock = cls._lock_registry.get(key)
        if lock is None:
            with cls._global_lock:  # Use a class-level lock to ensure thread safety
                lock = cls._lock_registry.get(key)
                if lock is None:
                    lock = threading.RLock()
                    cls._lock_registry[key] = lock
        return lock

    @staticmethod
    def load_stig_mapper() -> Optional[STIGMapper]:
        """
        Load the STIG Mapper file

        :return: None
        """
        from os import path

        stig_mapper_file = ScannerVariables.stigMapperFile
        if not path.exists(stig_mapper_file):
            return None
        try:
            stig_mapper = STIGMapper(json_file=stig_mapper_file)
            return stig_mapper
        except Exception as e:
            logger.debug(f"Warning Unable to loading STIG Mapper file: {e}")
        return None

    @staticmethod
    def get_assessor_id() -> str:
        """
        Gets the ID of the assessor

        :return: The ID of the assessor
        :rtype: str
        """

        return regscale_models.Issue.get_user_id()

    def get_cci_to_control_map(self) -> ThreadSafeDict[str, set[int]] | dict:
        """
        Gets the CCI to control map

        :return: The CCI to control map
        :rtype: ThreadSafeDict[str, set[int]] | dict
        """
        if self._no_ccis:
            return self.cci_to_control_map
        with self.cci_to_control_map_lock:
            if any(self.cci_to_control_map):
                return self.cci_to_control_map
            logger.info("Getting CCI to control map...")
            self.cci_to_control_map = regscale_models.map_ccis_to_control_ids(parent_id=self.plan_id)  # type: ignore
            if not any(self.cci_to_control_map):
                self._no_ccis = True
            return self.cci_to_control_map

    def get_control_to_cci_map(self) -> dict[int, set[str]]:
        """
        Gets the security control id to CCI map

        :return: The security control id to CCI map
        :rtype: dict[int, set[str]]
        """
        control_id_to_cci_map = defaultdict(set)
        for cci, control_ids in self.get_cci_to_control_map().items():
            for control_id in control_ids:
                control_id_to_cci_map[control_id].add(cci)
        return control_id_to_cci_map

    def get_control_implementation_id_for_cci(self, cci: Optional[str]) -> Optional[int]:
        """
        Gets the control implementation ID for a CCI

        :param Optional[str] cci: The CCI
        :return: The control ID
        :rtype: Optional[int]
        """
        if not cci:
            return None

        cci_to_control_map = self.get_cci_to_control_map()
        if cci not in cci_to_control_map:
            cci = "CCI-000366"

        if control_ids := cci_to_control_map.get(cci, set()):
            for control_id in control_ids:
                return self.control_id_to_implementation_map.get(control_id)
        return None

    def get_asset_map(self) -> dict[str, regscale_models.Asset]:
        """
        Retrieves a mapping of asset identifiers to their corresponding Asset objects. This method supports two modes
        of operation based on the `options_map_assets_to_components` flag. If the flag is set, it fetches the asset
        map using a specified key field from the assets associated with the given plan ID. Otherwise, it constructs
        the map by fetching all assets under the specified plan and using the asset identifier field as the key.

        :return: A dictionary mapping asset identifiers to Asset objects.
        :rtype: dict[str, regscale_models.Asset]
        """
        if self.options_map_assets_to_components:
            # Fetches the asset map directly using a specified key field.
            return regscale_models.Asset.get_map(
                plan_id=self.plan_id, key_field=self.asset_identifier_field, is_component=self.is_component
            )
        else:
            # Constructs the asset map by fetching all assets under the plan and using the asset identifier field as
            # the key.
            return {  # type: ignore
                getattr(x, self.asset_identifier_field): x
                for x in regscale_models.Asset.get_all_by_parent(
                    parent_id=self.plan_id,
                    parent_module=self.parent_module,
                )
            }

    def get_issues_map(self) -> dict[int, regscale_models.Issue]:
        """
        Gets the issues map

        :return: The issues map
        :rtype: dict[int, regscale_models.Issue]
        """
        all_issues = regscale_models.Issue.get_all_by_parent(
            parent_id=self.plan_id,
            parent_module=self.parent_module,
        )
        return {issue.integrationFindingId: issue for issue in all_issues}

    @abstractmethod
    def fetch_findings(self, *args, **kwargs) -> Iterator[IntegrationFinding]:
        """
        Fetches findings from the integration.

        :return: An iterator of findings
        :yield: Iterator[IntegrationFinding]
        """
        pass

    @abstractmethod
    def fetch_assets(self, *args, **kwargs) -> Iterator[IntegrationAsset]:
        """
        Fetches assets from the integration

        :return: An iterator of assets
        :yield: Iterator[IntegrationAsset]
        """

    def get_finding_status(self, status: Optional[str]) -> regscale_models.IssueStatus:
        """
        Gets the RegScale issue status based on the integration finding status

        :param Optional[str] status: The status of the finding
        :return: The RegScale issue status
        :rtype: regscale_models.IssueStatus
        """
        return self.finding_status_map.get(status, regscale_models.IssueStatus.Open)

    def get_checklist_status(self, status: Optional[str]) -> regscale_models.ChecklistStatus:
        """
        Gets the RegScale checklist status based on the integration finding status

        :param Optional[str] status: The status of the finding
        :return: The RegScale checklist status
        :rtype: regscale_models.ChecklistStatus
        """
        return self.checklist_status_map.get(status, regscale_models.ChecklistStatus.NOT_REVIEWED)

    def get_finding_severity(self, severity: Optional[str]) -> regscale_models.IssueSeverity:
        """
        Gets the RegScale issue severity based on the integration finding severity

        :param Optional[str] severity: The severity of the finding
        :return: The RegScale issue severity
        :rtype: regscale_models.IssueSeverity
        """
        return self.finding_severity_map.get(severity, regscale_models.IssueSeverity.NotAssigned)

    def get_finding_identifier(self, finding: IntegrationFinding) -> str:
        """
        Gets the finding identifier for the finding

        :param IntegrationFinding finding: The finding
        :return: The finding identifier
        :rtype: str
        """
        # We could have a string truncation error platform side on IntegrationFindingId nvarchar(450)
        prefix = f"{self.plan_id}:"
        if (
            ScannerVariables.tenableGroupByPlugin
            and finding.plugin_id
            and "tenable" in (finding.source_report or self.title).lower()
        ):
            res = f"{prefix}{finding.plugin_id}"
            return res[:450]
        prefix += finding.cve or finding.plugin_id or finding.rule_id or self.hash_string(finding.external_id).__str__()
        if ScannerVariables.issueCreation.lower() == "perasset":
            res = f"{prefix}:{finding.asset_identifier}"
            return res[:450]
        return prefix[:450]

    def get_or_create_assessment(self, control_implementation_id: int) -> regscale_models.Assessment:
        """
        Gets or creates a RegScale assessment

        :param int control_implementation_id: The ID of the control implementation
        :return: The assessment
        :rtype: regscale_models.Assessment
        """
        logger.info("Getting or create assessment for control implementation %d", control_implementation_id)
        assessment: Optional[regscale_models.Assessment] = self.assessment_map.get(control_implementation_id)
        if assessment:
            logger.debug(
                "Found cached assessment %s for control implementation %s", assessment.id, control_implementation_id
            )
        else:
            logger.debug("Assessment not found for control implementation %d", control_implementation_id)
            assessment = regscale_models.Assessment(
                plannedStart=get_current_datetime(),
                plannedFinish=get_current_datetime(),
                status=regscale_models.AssessmentStatus.COMPLETE.value,
                assessmentResult=regscale_models.AssessmentResultsStatus.FAIL.value,
                actualFinish=get_current_datetime(),
                leadAssessorId=self.assessor_id,
                parentId=control_implementation_id,
                parentModule=regscale_models.ControlImplementation.get_module_string(),
                title=f"{self.title} Assessment",
                assessmentType=regscale_models.AssessmentType.QA_SURVEILLANCE.value,
            ).create()
        self.assessment_map[control_implementation_id] = assessment
        return assessment

    def get_components(self) -> ThreadSafeList[regscale_models.Component]:
        """
        Get all components from the integration

        :return: A list of components
        :rtype: ThreadSafeList[regscale_models.Component]
        """
        if any(self.components):
            return self.components
        if self.is_component:
            components: List[regscale_models.Component] = [
                regscale_models.Component.get_object(
                    object_id=self.plan_id,
                )
            ]
        else:
            components: List[regscale_models.Component] = regscale_models.Component.get_all_by_parent(
                parent_id=self.plan_id,
                parent_module=regscale_models.SecurityPlan.get_module_string(),
            )
        self.components = ThreadSafeList(components)
        return self.components

    def get_component_by_title(self) -> dict:
        """
        Get all components from the integration

        :return: A dictionary of components
        :rtype: dict
        """
        return {component.title: component for component in self.get_components()}

    # Asset Methods
    def set_asset_defaults(self, asset: IntegrationAsset) -> IntegrationAsset:
        """
        Set default values for the asset (Thread Safe)

        :param IntegrationAsset asset: The integration asset
        :return: The asset with which defaults should be set
        :rtype: IntegrationAsset
        """
        if not asset.asset_owner_id:
            asset.asset_owner_id = self.get_assessor_id()
        if not asset.status:
            asset.status = regscale_models.AssetStatus.Active
        return asset

    def process_asset(
        self,
        asset: IntegrationAsset,
        loading_assets: TaskID,
    ) -> None:
        """
        Safely processes a single asset in a concurrent environment. This method ensures thread safety
        by utilizing a threading lock. It assigns default values to the asset if necessary, maps the asset
        to components if specified, and updates the progress of asset loading.
        (Thread Safe)

        :param IntegrationAsset asset: The integration asset to be processed.
        :param TaskID loading_assets: The identifier for the task tracking the progress of asset loading.
        :rtype: None
        """

        # Assign default values to the asset if they are not already set.
        asset = self.set_asset_defaults(asset)

        # If mapping assets to components is enabled and the asset has associated component names,
        # attempt to update or create each asset under its respective component.
        if any(asset.component_names):
            for component_name in asset.component_names:
                self.update_or_create_asset(asset, component_name)
        else:
            # If no component mapping is required, add the asset directly to the security plan without a component.
            self.update_or_create_asset(asset, None)

        if self.num_assets_to_process and self.asset_progress.tasks[loading_assets].total != float(
            self.num_assets_to_process
        ):
            self.asset_progress.update(
                loading_assets,
                total=self.num_assets_to_process,
                description=f"[#f8b737]Creating and updating {self.num_assets_to_process} assets from {self.title}.",
            )
        self.asset_progress.advance(loading_assets, 1)

    def update_or_create_asset(
        self,
        asset: IntegrationAsset,
        component_name: Optional[str] = None,
    ) -> None:
        """
        Update or create an asset in RegScale.

        This method either updates an existing asset or creates a new one within a thread-safe manner. It handles
        the asset's association with a component, creating the component if it does not exist.
        (Thread Safe)

        :param IntegrationAsset asset: The asset to be updated or created.
        :param Optional[str] component_name: The name of the component to associate the asset with. If None, the asset
                                          is added directly to the security plan without a component association.
        """
        # Continue with normal asset creation/update
        if not asset.identifier:
            logger.warning("Asset has no identifier, skipping")
            return

        component = getattr(self, "component") if self.is_component else None
        if component_name:
            logger.debug("Searching for component: %s...", component_name)
            component = component or self.components_by_title.get(component_name)
            if not component:
                logger.debug("No existing component found with name %s, proceeding to create it...", component_name)
                component = regscale_models.Component(
                    title=component_name,
                    componentType=asset.component_type,
                    securityPlansId=self.plan_id,
                    description=component_name,
                    componentOwnerId=self.get_assessor_id(),
                ).get_or_create()
                self.components.append(component)
            if component.securityPlansId and not self.is_component:
                component_mapping = regscale_models.ComponentMapping(
                    componentId=component.id,
                    securityPlanId=self.plan_id,
                )
                component_mapping.get_or_create()
            self.components_by_title[component_name] = component

        created, existing_or_new_asset = self.create_new_asset(asset, component=None)

        # update results expects a dict[str, list] to update result counts
        self.update_result_counts("assets", {"created": [1] if created else [], "updated": [] if created else [1]})

        # If the asset is associated with a component, create a mapping between them.
        if existing_or_new_asset and component:
            _was_created, _asset_mapping = regscale_models.AssetMapping(
                assetId=existing_or_new_asset.id,
                componentId=component.id,
            ).get_or_create_with_status()

        if created and DuroSuiteVariables.duroSuiteEnabled:
            # Check if this is a DuroSuite compatible asset
            scan_durosuite_devices(asset=asset, plan_id=self.plan_id, progress=self.asset_progress)

    def create_new_asset(
        self, asset: IntegrationAsset, component: Optional[regscale_models.Component]
    ) -> tuple[bool, Optional[regscale_models.Asset]]:
        """
        Creates a new asset in the system based on the provided integration asset details.
        Associates the asset with a component or directly with the security plan.

        :param IntegrationAsset asset: The integration asset from which the new asset will be created.
        :param Optional[regscale_models.Component] component: The component to link the asset to, or None.
        :return: Tuple of (was_created, newly created asset instance).
        :rtype: tuple[bool, Optional[regscale_models.Asset]]
        """
        # Ensure the asset has a name
        if not asset.name:
            logger.warning(
                "Asset name is required for asset creation. Skipping asset creation of asset_type: %s", asset.asset_type
            )
            return False, None

        new_asset = regscale_models.Asset(
            name=asset.name,
            description=asset.description,
            bVirtual=asset.is_virtual,
            otherTrackingNumber=asset.other_tracking_number or asset.identifier,
            assetOwnerId=asset.asset_owner_id or "Unknown",
            parentId=component.id if component else self.plan_id,
            parentModule=self.parent_module,
            assetType=asset.asset_type,
            dateLastUpdated=asset.date_last_updated or get_current_datetime(),
            status=asset.status,
            assetCategory=asset.asset_category,
            managementType=asset.management_type,
            notes=asset.notes,
            model=asset.model,
            manufacturer=asset.manufacturer,
            serialNumber=asset.serial_number,
            assetTagNumber=asset.asset_tag_number,
            bPublicFacing=asset.is_public_facing,
            azureIdentifier=asset.azure_identifier,
            location=asset.location,
            ipAddress=asset.ip_address,
            iPv6Address=asset.ipv6_address,
            fqdn=asset.fqdn,
            macAddress=asset.mac_address,
            diskStorage=asset.disk_storage,
            cpu=asset.cpu,
            ram=asset.ram or 0,
            operatingSystem=asset.operating_system,
            osVersion=asset.os_version,
            endOfLifeDate=asset.end_of_life_date,
            vlanId=asset.vlan_id,
            uri=asset.uri,
            awsIdentifier=asset.aws_identifier,
            googleIdentifier=asset.google_identifier,
            otherCloudIdentifier=asset.other_cloud_identifier,
            patchLevel=asset.patch_level,
            cpe=asset.cpe,
            softwareVersion=asset.software_version,
            softwareName=asset.software_name,
            softwareVendor=asset.software_vendor,
            bLatestScan=asset.is_latest_scan,
            bAuthenticatedScan=asset.is_authenticated_scan,
            systemAdministratorId=asset.system_administrator_id,
            scanningTool=asset.scanning_tool,
            softwareFunction=asset.software_function,
            baselineConfiguration=asset.baseline_configuration,
        )
        if self.asset_identifier_field:
            setattr(new_asset, self.asset_identifier_field, asset.identifier)

        created, new_asset = new_asset.create_or_update_with_status(bulk_update=True)
        # add to asset_map_by_identifier
        self.asset_map_by_identifier[asset.identifier] = new_asset
        logger.debug("Created new asset with identifier %s", asset.identifier)

        self.handle_software_inventory(new_asset, asset.software_inventory, created)
        self.create_asset_data_and_link(new_asset, asset)
        self.create_or_update_ports_protocol(new_asset, asset)
        if self.stig_mapper:
            self.stig_mapper.map_associated_stigs_to_asset(asset=new_asset, ssp_id=self.plan_id)
        return created, new_asset

    def handle_software_inventory(
        self, new_asset: regscale_models.Asset, software_inventory: List[Dict[str, Any]], created: bool
    ) -> None:
        """
        Handles the software inventory for the asset.

        :param regscale_models.Asset new_asset: The newly created asset
        :param List[Dict[str, Any]] software_inventory: List of software inventory items
        :param bool created: Flag indicating if the asset was newly created
        :rtype: None
        """
        if not software_inventory:
            return

        existing_software: list[regscale_models.SoftwareInventory] = (
            []
            if created
            else regscale_models.SoftwareInventory.get_all_by_parent(
                parent_id=new_asset.id,
                parent_module=None,
            )
        )
        existing_software_dict = {(s.name, s.version): s for s in existing_software}
        software_in_scan = set()

        for software in software_inventory:
            software_name = software.get("name")
            if not software_name:
                logger.error("Software name is required for software inventory")
                continue

            software_version = software.get("version")
            software_in_scan.add((software_name, software_version))

            if (software_name, software_version) not in existing_software_dict:
                self.software_to_create.append(
                    regscale_models.SoftwareInventory(
                        name=software_name,
                        parentHardwareAssetId=new_asset.id,
                        version=software_version,
                    )
                )
            else:
                self.software_to_update.append(existing_software_dict[(software_name, software_version)])

        # Remove software that is no longer in the scan
        for software_key, software_obj in existing_software_dict.items():
            if software_key not in software_in_scan:
                software_obj.delete()

    def create_asset_data_and_link(self, asset: regscale_models.Asset, integration_asset: IntegrationAsset) -> None:
        """
        Creates Data and Link objects for the given asset.

        :param regscale_models.Asset asset: The asset to create Data and Link for
        :param IntegrationAsset integration_asset: The integration asset containing source data and URL
        :rtype: None
        """
        if integration_asset.source_data:
            # Optimization, create an api that gets the data by plan and parent module
            regscale_models.Data(
                parentId=asset.id,
                parentModule=asset.get_module_string(),
                dataSource=self.title,
                dataType=regscale_models.DataDataType.JSON.value,
                rawData=json.dumps(integration_asset.source_data, indent=2, cls=DateTimeEncoder),
                lastUpdatedById=integration_asset.asset_owner_id or "Unknown",
                createdById=integration_asset.asset_owner_id or "Unknown",
            ).create_or_update(bulk_create=True, bulk_update=True)
        if integration_asset.url:
            link = regscale_models.Link(
                parentID=asset.id,
                parentModule=asset.get_module_string(),
                url=integration_asset.url,
                title="Asset Provider URL",
            )
            if link.find_by_unique():
                self.link_to_update.append(link)
            else:
                self.link_to_create.append(link)

    @staticmethod
    def create_or_update_ports_protocol(asset: regscale_models.Asset, integration_asset: IntegrationAsset) -> None:
        """
        Creates or updates PortsProtocol objects for the given asset.

        :param regscale_models.Asset asset: The asset to create or update PortsProtocol for
        :param IntegrationAsset integration_asset: The integration asset containing ports and protocols information
        :rtype: None
        """
        if integration_asset.ports_and_protocols:
            for port_protocol in integration_asset.ports_and_protocols:
                if not port_protocol.get("start_port") or not port_protocol.get("end_port"):
                    logger.error("Invalid port protocol data: %s", port_protocol)
                    continue
                regscale_models.PortsProtocol(
                    parentId=asset.id,
                    parentModule=asset.get_module_string(),
                    startPort=port_protocol.get("start_port", 0),
                    endPort=port_protocol.get("end_port", 0),
                    service=port_protocol.get("service", asset.name),
                    protocol=port_protocol.get("protocol"),
                    purpose=port_protocol.get("purpose", f"Grant access to {asset.name}"),
                    usedBy=asset.name,
                ).create_or_update()

    def update_regscale_assets(self, assets: Iterator[IntegrationAsset]) -> int:
        """
        Updates RegScale assets based on the integration assets

        :param Iterator[IntegrationAsset] assets: The integration assets
        :return: The number of assets processed
        :rtype: int
        """
        logger.info("Updating RegScale assets...")
        loading_assets = self._setup_progress_bar()
        logger.debug("Pre-populating cache")
        regscale_models.AssetMapping.populate_cache_by_plan(self.plan_id)
        regscale_models.ComponentMapping.populate_cache_by_plan(self.plan_id)

        if self.options_map_assets_to_components:
            thread_safe_dict: ThreadSafeDict[str, regscale_models.Component] = ThreadSafeDict()
            thread_safe_dict.update(self.get_component_by_title())
            self.components_by_title = thread_safe_dict

        assets_processed = self._process_assets(assets, loading_assets)

        self._perform_batch_operations(self.asset_progress)
        if self.num_assets_to_process and self.asset_progress.tasks[loading_assets].completed != float(
            self.num_assets_to_process
        ):
            self.asset_progress.update(loading_assets, completed=self.num_assets_to_process)

        return assets_processed

    def _setup_progress_bar(self) -> TaskID:
        """
        Sets up the progress bar for asset processing.

        :return: The task ID for the progress bar
        :rtype: TaskID
        """
        asset_count = self.num_assets_to_process or None
        return self.asset_progress.add_task(
            f"[#f8b737]Creating and updating{f' {asset_count}' if asset_count else ''} asset(s) from {self.title}.",
            total=asset_count,
        )

    def _process_assets(self, assets: Iterator[IntegrationAsset], loading_assets: TaskID) -> int:
        """
        Process assets using single or multi-threaded approach based on THREAD_MAX_WORKERS.

        :param Iterator[IntegrationAsset] assets: Assets to process
        :param TaskID loading_assets: Task ID for the progress bar
        :return: Number of assets processed
        :rtype: int
        """
        self._prime_asset_cache()
        process_func = self._create_process_function(loading_assets)
        max_workers = get_thread_workers_max()

        if max_workers == 1:
            return self._process_single_threaded(assets, process_func)
        return self._process_multi_threaded(assets, process_func, max_workers)

    def _prime_asset_cache(self) -> None:
        """
        Prime the asset cache by fetching assets for the given plan.

        :rtype: None
        """
        regscale_models.Asset.get_all_by_parent(parent_id=self.plan_id, parent_module=self.parent_module)

    def _create_process_function(self, loading_assets: TaskID) -> Callable[[IntegrationAsset], bool]:
        """
        Create a function to process a single asset.

        :param TaskID loading_assets: Task ID for the progress bar
        :return: Function that processes an asset and returns success status
        :rtype: Callable[[IntegrationAsset], bool]
        """
        return lambda asset: self._process_single_asset(asset, loading_assets)

    def _process_single_threaded(
        self, assets: Iterator[IntegrationAsset], process_func: Callable[[IntegrationAsset], bool]
    ) -> int:
        """
        Process assets sequentially in a single thread.

        :param Iterator[IntegrationAsset] assets: Assets to process
        :param Callable[[IntegrationAsset], bool] process_func: Function to process each asset
        :return: Number of assets processed
        :rtype: int
        """
        assets_processed = 0
        for asset in assets:
            if process_func(asset):
                assets_processed = self._update_processed_count(assets_processed)
        return assets_processed

    def _process_multi_threaded(
        self, assets: Iterator[IntegrationAsset], process_func: Callable[[IntegrationAsset], bool], max_workers: int
    ) -> int:
        """
        Process assets in batches using multiple threads.

        :param Iterator[IntegrationAsset] assets: Assets to process
        :param Callable[[IntegrationAsset], bool] process_func: Function to process each asset
        :param int max_workers: Maximum number of worker threads
        :return: Number of assets processed
        :rtype: int
        """
        batch_size = max_workers * 2
        assets_processed = 0

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            batch = []
            futures = []

            for asset in assets:
                batch.append(asset)
                if len(batch) >= batch_size:
                    assets_processed += self._submit_and_process_batch(executor, process_func, batch, futures)
                    batch = []
                    futures = []

            if batch:  # Process any remaining items
                assets_processed += self._submit_and_process_batch(executor, process_func, batch, futures)

        return assets_processed

    def _submit_and_process_batch(
        self,
        executor: ThreadPoolExecutor,
        process_func: Callable[[IntegrationAsset], bool],
        batch: List[IntegrationAsset],
        futures: List,
    ) -> int:
        """
        Submit a batch of assets for processing and count successful completions.

        :param ThreadPoolExecutor executor: Thread pool executor for parallel processing
        :param Callable[[IntegrationAsset], bool] process_func: Function to process each asset
        :param List[IntegrationAsset] batch: Batch of assets to process
        :param List futures: List to store future objects
        :return: Number of assets processed in this batch
        :rtype: int
        """
        assets_processed = 0
        for asset in batch:
            futures.append(executor.submit(process_func, asset))

        for future in concurrent.futures.as_completed(futures):
            if future.result():
                assets_processed = self._update_processed_count(assets_processed)

        return assets_processed

    def _update_processed_count(self, current_count: int) -> int:
        """
        Increment the processed count.

        :param int current_count: Current number of processed items
        :return: Updated count
        :rtype: int
        """
        return current_count + 1

    def _process_single_asset(self, asset: IntegrationAsset, loading_assets: TaskID) -> bool:
        """
        Processes a single asset and handles any exceptions.

        :param IntegrationAsset asset: The asset to process
        :param TaskID loading_assets: The task ID for the progress bar
        :return: True if the asset was processed successfully, False otherwise
        :rtype: bool
        """
        try:
            self.process_asset(asset, loading_assets)
            return True
        except Exception as exc:
            self.log_error("An error occurred when processing asset %s: %s", asset.name, exc)
            return False

    @staticmethod
    def _update_processed_count(assets_processed: int) -> int:
        """
        Updates and logs the count of processed assets.

        :param int assets_processed: The current count of processed assets
        :return: The updated count of processed assets
        :rtype: int
        """
        assets_processed += 1
        if assets_processed % 100 == 0:
            logger.info("Processed %d assets.", assets_processed)
        return assets_processed

    def update_result_counts(self, key: str, results: dict[str, list]) -> None:
        """
        Updates the results dictionary with the given key and results.

        :param str key: The key to update
        :param dict[str, list] results: The results to update, example: ["updated": [], "created": []]
        :rtype: None
        """
        if key not in self._results:
            self._results[key] = {"created_count": 0, "updated_count": 0}
        self._results[key]["created_count"] += len(results.get("created", []))
        self._results[key]["updated_count"] += len(results.get("updated", []))

    def _perform_batch_operations(self, progress: Progress) -> None:
        """
        Performs batch operations for assets, software inventory, and data.

        :rtype: None
        """
        logger.debug("Bulk saving assets...")
        self.update_result_counts("assets", regscale_models.Asset.bulk_save(progress_context=progress))
        logger.debug("Done bulk saving assets.")
        logger.debug("Bulk saving issues...")
        self.update_result_counts("issues", regscale_models.Issue.bulk_save(progress_context=progress))
        logger.debug("Done bulk saving issues.")
        logger.debug("Bulk saving properties...")
        self.update_result_counts("properties", regscale_models.Property.bulk_save(progress_context=progress))
        logger.debug("Done bulk saving properties.")

        software_inventory = {}
        if self.software_to_create:
            logger.debug("Bulk creating software inventory...")
            software_inventory["created_count"] = len(
                regscale_models.SoftwareInventory.batch_create(items=self.software_to_create, progress_context=progress)
            )
            logger.debug("Done bulk creating software inventory.")
        if self.software_to_update:
            logger.debug("Bulk updating software inventory...")
            software_inventory["updated_updated"] = len(
                regscale_models.SoftwareInventory.batch_update(items=self.software_to_update, progress_context=progress)
            )
            logger.debug("Done bulk updating software inventory.")
        self._results["software_inventory"] = software_inventory
        logger.debug("Bulk saving data records...")
        self.update_result_counts("data", regscale_models.Data.bulk_save(progress_context=progress))
        logger.debug("Done bulk saving data records.")

    @staticmethod
    def get_issue_title(finding: IntegrationFinding) -> str:
        """
        Gets the issue title based on the POAM Title Type variable.

        :param IntegrationFinding finding: The finding data
        :return: The issue title
        :rtype: str
        """
        issue_title = finding.title or ""
        if ScannerVariables.poamTitleType.lower() == "pluginid" or not issue_title:
            issue_title = (
                f"{finding.plugin_id or finding.cve or finding.rule_id}: {finding.plugin_name or finding.description}"
            )
        return issue_title[:450]

    # Finding Methods
    def create_or_update_issue_from_finding(
        self,
        title: str,
        finding: IntegrationFinding,
    ) -> regscale_models.Issue:
        """
        Creates or updates a RegScale issue from a finding

        :param str title: The title of the issue
        :param IntegrationFinding finding: The finding data
        :return: The created or updated RegScale issue
        :rtype: regscale_models.Issue
        """
        issue_status = finding.get_issue_status()
        finding_id = self.get_finding_identifier(finding)
        finding_id_lock = self._get_lock(finding_id)

        with finding_id_lock:
            if ScannerVariables.issueCreation.lower() != "perasset":
                # Check if we should consolidate open issues based on integrationFindingId
                if issue_status == regscale_models.IssueStatus.Open:
                    existing_issues = regscale_models.Issue.find_by_integration_finding_id(finding_id)
                    # Find an open issue to update
                    issue = next(
                        (issue for issue in existing_issues if issue.status != regscale_models.IssueStatus.Closed), None
                    )
                    if issue:
                        return self._create_or_update_issue(finding, issue_status, title, issue)

                # Check if we should consolidate closed issues based on integrationFindingId and issueDueDates
                elif issue_status == regscale_models.IssueStatus.Closed:
                    existing_issues = regscale_models.Issue.find_by_integration_finding_id(finding_id)
                    # Find a closed issue with matching due date to consolidate with
                    matching_closed_issue = next(
                        (
                            issue
                            for issue in existing_issues
                            if issue.status == regscale_models.IssueStatus.Closed
                            and date_str(issue.dueDate) == date_str(finding.due_date)
                        ),
                        None,
                    )
                    if matching_closed_issue:
                        return self._create_or_update_issue(finding, issue_status, title, matching_closed_issue)

            return self._create_or_update_issue(finding, issue_status, title)

    def _create_or_update_issue(
        self,
        finding: IntegrationFinding,
        issue_status: regscale_models.IssueStatus,
        title: str,
        existing_issue: Optional[regscale_models.Issue] = None,
    ) -> regscale_models.Issue:
        """
        Creates or updates a RegScale issue

        :param IntegrationFinding finding: The finding data
        :param str issue_status: The status of the issue
        :param str title: The title of the issue
        :param Optional[regscale_models.Issue] existing_issue: Existing issue to update, if any
        :return: The created or updated RegScale issue
        :rtype: regscale_models.Issue
        """
        # Prepare issue data
        issue_title = self.get_issue_title(finding) or title
        description = finding.description or ""
        remediation_description = finding.recommendation_for_mitigation or finding.remediation or ""
        is_poam = self.is_poam(finding)

        if existing_issue:
            logger.debug(
                "Updating existing issue %s with assetIdentifier %s", existing_issue.id, finding.asset_identifier
            )

        # If we have an existing issue, update its fields instead of creating a new one
        issue = existing_issue or regscale_models.Issue()

        # Get consolidated asset identifier
        asset_identifier = self.get_consolidated_asset_identifier(finding, existing_issue)

        # Set basic issue fields
        self._set_basic_issue_fields(issue, finding, issue_status, issue_title, asset_identifier)

        # Set due date
        self._set_issue_due_date(issue, finding)

        # Set additional issue fields
        self._set_additional_issue_fields(issue, finding, description, remediation_description)

        # Set control-related fields
        self._set_control_fields(issue, finding)

        # Set risk and operational fields
        self._set_risk_and_operational_fields(issue, finding, is_poam)

        # Update KEV data if CVE exists
        if finding.cve:
            issue = self.lookup_kev_and_update_issue(cve=finding.cve, issue=issue, cisa_kevs=self._kev_data)

        # Save or create the issue
        self._save_or_create_issue(issue, finding, existing_issue, is_poam)

        self._handle_property_and_milestone_creation(issue, finding, existing_issue)
        return issue

    def _set_basic_issue_fields(
        self,
        issue: regscale_models.Issue,
        finding: IntegrationFinding,
        issue_status: regscale_models.IssueStatus,
        issue_title: str,
        asset_identifier: str,
    ) -> None:
        """Set basic fields for the issue."""
        issue.parentId = self.plan_id
        issue.parentModule = self.parent_module
        issue.vulnerabilityId = finding.vulnerability_id
        issue.title = issue_title
        issue.dateCreated = finding.date_created
        issue.status = issue_status
        issue.dateCompleted = (
            self.get_date_completed(finding, issue_status)
            if issue_status == regscale_models.IssueStatus.Closed
            else None
        )
        issue.severityLevel = finding.severity
        issue.issueOwnerId = self.assessor_id
        issue.securityPlanId = self.plan_id if not self.is_component else None
        issue.identification = finding.identification
        issue.dateFirstDetected = finding.first_seen
        issue.assetIdentifier = asset_identifier

    def _set_issue_due_date(self, issue: regscale_models.Issue, finding: IntegrationFinding) -> None:
        """Set the due date for the issue."""
        if not finding.due_date:
            try:
                base_created = finding.date_created or issue.dateCreated
                finding.due_date = issue_due_date(
                    severity=finding.severity,
                    created_date=base_created,
                    title=self.title,
                )
            except Exception:
                # Final fallback to a Low severity default if anything goes wrong
                base_created = finding.date_created or issue.dateCreated
                finding.due_date = issue_due_date(
                    severity=regscale_models.IssueSeverity.Low,
                    created_date=base_created,
                    title=self.title,
                )
        issue.dueDate = finding.due_date

    def _set_additional_issue_fields(
        self, issue: regscale_models.Issue, finding: IntegrationFinding, description: str, remediation_description: str
    ) -> None:
        """Set additional fields for the issue."""
        issue.description = description
        issue.sourceReport = finding.source_report or self.title
        issue.recommendedActions = finding.recommendation_for_mitigation
        issue.securityChecks = finding.security_check or finding.external_id
        issue.remediationDescription = remediation_description
        issue.integrationFindingId = self.get_finding_identifier(finding)
        issue.poamComments = finding.poam_comments
        issue.cve = finding.cve
        issue.assessmentId = finding.assessment_id

    def _set_control_fields(self, issue: regscale_models.Issue, finding: IntegrationFinding) -> None:
        """Set control-related fields for the issue."""
        control_id = self.get_control_implementation_id_for_cci(finding.cci_ref) if finding.cci_ref else None
        # Note: controlId is deprecated, using controlImplementationIds instead
        cci_control_ids = [control_id] if control_id is not None else []

        # Ensure failed control labels (e.g., AC-4(21)) are present in affectedControls
        if finding.affected_controls:
            issue.affectedControls = finding.affected_controls
        elif finding.control_labels:
            issue.affectedControls = ", ".join(sorted({cl for cl in finding.control_labels if cl}))

        issue.controlImplementationIds = list(set(finding._control_implementation_ids + cci_control_ids))  # noqa

    def _set_risk_and_operational_fields(
        self, issue: regscale_models.Issue, finding: IntegrationFinding, is_poam: bool
    ) -> None:
        """Set risk and operational fields for the issue."""
        issue.isPoam = is_poam
        issue.basisForAdjustment = (
            finding.basis_for_adjustment if finding.basis_for_adjustment else f"{self.title} import"
        )
        issue.pluginId = finding.plugin_id
        issue.originalRiskRating = regscale_models.Issue.assign_risk_rating(finding.severity)
        issue.changes = "<p>Current: {}</p><p>Planned: {}</p>".format(
            finding.milestone_changes, finding.planned_milestone_changes
        )
        issue.adjustedRiskRating = finding.adjusted_risk_rating
        issue.riskAdjustment = finding.risk_adjustment
        issue.operationalRequirement = finding.operational_requirements
        issue.deviationRationale = finding.deviation_rationale
        issue.dateLastUpdated = get_current_datetime()
        issue.affectedControls = finding.affected_controls

    def _save_or_create_issue(
        self,
        issue: regscale_models.Issue,
        finding: IntegrationFinding,
        existing_issue: Optional[regscale_models.Issue],
        is_poam: bool,
    ) -> None:
        """Save or create the issue."""
        if existing_issue:
            logger.debug("Saving Old Issue: %s  with assetIdentifier: %s", issue.id, issue.assetIdentifier)
            issue.save(bulk=True)
            logger.debug("Saved existing issue %s with assetIdentifier: %s", issue.id, issue.assetIdentifier)
        else:
            issue = issue.create_or_update(
                bulk_update=True, defaults={"otherIdentifier": self._get_other_identifier(finding, is_poam)}
            )
            self.extra_data_to_properties(finding, issue.id)

        self._handle_property_and_milestone_creation(issue, finding, existing_issue)
        return issue

    def _handle_property_and_milestone_creation(
        self,
        issue: regscale_models.Issue,
        finding: IntegrationFinding,
        existing_issue: Optional[regscale_models.Issue] = None,
    ) -> None:
        """
        Handles property creation for an issue based on the finding data

        :param regscale_models.Issue issue: The issue to handle properties for
        :param IntegrationFinding finding: The finding data
        :param bool new_issue: Whether this is a new issue
        :rtype: None
        """
        if poc := finding.point_of_contact:
            regscale_models.Property(
                key="POC",
                value=poc,
                parentId=issue.id,
                parentModule="issues",
            ).create_or_update()
            logger.debug("Added POC property %s to issue %s", poc, issue.id)

        if finding.is_cwe:
            regscale_models.Property(
                key="CWE",
                value=finding.plugin_id,
                parentId=issue.id,
                parentModule="issues",
            ).create_or_update()
            logger.debug("Added CWE property %s to issue %s", finding.plugin_id, issue.id)

        if ScannerVariables.useMilestones and issue.id:
            if (
                existing_issue
                and existing_issue.status == regscale_models.IssueStatus.Closed
                and issue.status == regscale_models.IssueStatus.Open
            ):
                regscale_models.Milestone(
                    title=f"Issue reopened from {self.title} scan",
                    milestoneDate=get_current_datetime(),
                    responsiblePersonId=self.assessor_id,
                    parentID=issue.id,
                    parentModule="issues",
                ).create()
                logger.debug("Added milestone for issue %s from finding %s", issue.id, finding.external_id)
            elif (
                existing_issue
                and existing_issue.status == regscale_models.IssueStatus.Open
                and issue.status == regscale_models.IssueStatus.Closed
            ):
                regscale_models.Milestone(
                    title=f"Issue closed from {self.title} scan",
                    milestoneDate=issue.dateCompleted,
                    responsiblePersonId=self.assessor_id,
                    parentID=issue.id,
                    parentModule="issues",
                ).create()
                logger.debug("Added milestone for issue %s from finding %s", issue.id, finding.external_id)
            elif not existing_issue:
                regscale_models.Milestone(
                    title=f"Issue created from {self.title} scan",
                    milestoneDate=self.scan_date,
                    responsiblePersonId=self.assessor_id,
                    parentID=issue.id,
                    parentModule="issues",
                ).create()
                logger.debug("Created milestone for issue %s from finding %s", issue.id, finding.external_id)
            else:
                logger.debug("No milestone created for issue %s from finding %s", issue.id, finding.external_id)

    @staticmethod
    def extra_data_to_properties(finding: IntegrationFinding, issue_id: int) -> None:
        """
        Adds extra data to properties for an issue in a separate thread

        :param IntegrationFinding finding: The finding data
        :param int issue_id: The ID of the issue
        :rtype: None
        """

        def _create_property():
            """Create the property in a separate thread"""
            if not finding.extra_data:
                return
            try:
                Property(
                    key="source_file_path",
                    value=finding.extra_data.get("source_file_path"),
                    parentId=issue_id,
                    parentModule="issues",
                ).create()
            except Exception as exc:
                # Log any errors that occur in the thread
                logger.error(f"Error creating property for issue {issue_id}: {exc}")

        # Start the property creation in a separate thread
        thread = threading.Thread(target=_create_property, daemon=True)
        thread.start()

    @staticmethod
    def get_consolidated_asset_identifier(
        finding: IntegrationFinding,
        existing_issue: Optional[regscale_models.Issue] = None,
    ) -> str:
        """
        Gets the consolidated asset identifier, combining the finding's asset identifier
        with any existing asset identifiers from the issue.

        :param IntegrationFinding finding: The finding data
        :param Optional[regscale_models.Issue] existing_issue: The existing issue to consolidate with, if any
        :return: The consolidated asset identifier
        :rtype: str
        """
        delimiter = "\n"
        if not existing_issue or ScannerVariables.issueCreation.lower() == "perasset":
            return finding.asset_identifier

        # Get existing asset identifiers
        existing_asset_identifiers = set((existing_issue.assetIdentifier or "").split(delimiter))
        if finding.asset_identifier not in existing_asset_identifiers:
            existing_asset_identifiers.add(finding.asset_identifier)

        return delimiter.join(existing_asset_identifiers)

    def _get_other_identifier(self, finding: IntegrationFinding, is_poam: bool) -> Optional[str]:
        """
        Gets the other identifier for an issue

        :param IntegrationFinding finding: The finding data
        :param bool is_poam: Whether this is a POAM issue
        :return: The other identifier if applicable
        :rtype: Optional[str]
        """
        # If existing POAM ID is greater than the cached max, update the cached max
        if finding.poam_id:
            if (poam_id := self.parse_poam_id(finding.poam_id)) and poam_id > (self._max_poam_id or 0):
                self._max_poam_id = poam_id
            return finding.poam_id

        # Only called if isPoam is True and creating a new issue
        if is_poam and ScannerVariables.incrementPoamIdentifier:
            return f"V-{self.get_next_poam_id():04d}"
        return None

    @staticmethod
    def lookup_kev_and_update_issue(
        cve: str, issue: regscale_models.Issue, cisa_kevs: Optional[ThreadSafeDict[str, Any]] = None
    ) -> regscale_models.Issue:
        """
        Determine if the cve is part of the published CISA KEV list

        :param str cve: The CVE to lookup in CISAs KEV list
        :param regscale_models.Issue issue: The issue to update kevList field and dueDate if found in KEV List
        :param Optional[ThreadSafeDict[str, Any]] cisa_kevs: The CISA KEV data to search the findings
        :return: The updated issue
        :rtype: regscale_models.Issue
        """
        from datetime import datetime

        from regscale.core.app.utils.app_utils import convert_datetime_to_regscale_string

        issue.kevList = "No"

        if cisa_kevs:
            kev_data = next(
                (
                    entry
                    for entry in cisa_kevs.get("vulnerabilities", [])
                    if entry.get("cveID", "").lower() == cve.lower()
                ),
                None,
            )
            if kev_data:
                # If kev due date is before the issue date created, add the difference to the date created
                calculated_due_date = ScannerIntegration._calculate_kev_due_date(kev_data, issue.dateCreated)
                if calculated_due_date:
                    issue.dueDate = calculated_due_date
                else:
                    issue.dueDate = convert_datetime_to_regscale_string(
                        datetime.strptime(kev_data["dueDate"], "%Y-%m-%d")
                    )
                issue.kevList = "Yes"

        return issue

    @staticmethod
    def group_by_plugin(existing_issue: regscale_models.Issue, finding: IntegrationFinding) -> regscale_models.Issue:
        """
        Merges the CVEs for the issue if the group by plugin is enabled

        :param regscale_models.Issue regscale_models.Issue existing_issue: The existing issue
        :param IntegrationFinding finding: The finding data
        :return: The existing issue
        :rtype: regscale_models.Issue
        """
        if ScannerVariables.tenableGroupByPlugin and finding.cve:
            # consolidate cve, but only for this switch
            existing_cves = (existing_issue.cve or "").split(",")
            existing_issue.cve = ",".join(set(existing_cves + [finding.cve]))
        return existing_issue

    @staticmethod
    def is_poam(finding: IntegrationFinding) -> bool:
        """
        Determines if an issue should be considered a Plan of Action and Milestones (POAM).

        :param IntegrationFinding finding: The finding to check
        :return: True if the issue should be a POAM, False otherwise
        :rtype: bool
        """
        if (
            ScannerVariables.vulnerabilityCreation.lower() == "poamcreation"
            or ScannerVariables.complianceCreation.lower() == "poam"
        ):
            return True
        if finding.due_date < get_current_datetime():
            return True
        return False

    def handle_failing_finding(
        self,
        issue_title: str,
        finding: IntegrationFinding,
    ) -> None:
        """
        Handles findings that have failed by creating or updating an issue.

        :param str issue_title: The title of the issue
        :param IntegrationFinding finding: The finding data that has failed
        :rtype: None
        """
        if ScannerVariables.vulnerabilityCreation.lower() != "noissue":
            logger.debug("Creating issue for failing finding %s", finding.external_id)
            found_issue = self.create_or_update_issue_from_finding(
                title=issue_title,
                finding=finding,
            )
            # Update the control implementation status to NOT_IMPLEMENTED since we have a failing finding
            if found_issue.controlImplementationIds:
                for control_id in found_issue.controlImplementationIds:
                    self.update_control_implementation_status_after_close(control_id)

    def handle_failing_checklist(
        self,
        finding: IntegrationFinding,
        plan_id: int,
    ) -> None:
        """
        Handles failing checklists by creating or updating implementation options and objectives.

        :param IntegrationFinding finding: The finding data
        :param int plan_id: The ID of the security plan
        :rtype: None
        """
        if finding.cci_ref:
            failing_objectives = regscale_models.ControlObjective.fetch_control_objectives_by_other_id(
                parent_id=plan_id, other_id_contains=finding.cci_ref
            )
            failing_objectives += regscale_models.ControlObjective.fetch_control_objectives_by_name(
                parent_id=plan_id, name_contains=finding.cci_ref
            )
            for failing_objective in failing_objectives:
                if failing_objective.name.lower().startswith("cci-"):
                    implementation_id = self.get_control_implementation_id_for_cci(failing_objective.name)
                else:
                    control_label = objective_to_control_dot(failing_objective.name)
                    if control_label not in self.control_implementation_id_map:
                        logger.warning("Control %s not found for %s", control_label, control_label)
                        continue
                    implementation_id = self.control_implementation_id_map[control_label]

                failing_option = regscale_models.ImplementationOption(
                    name="Failed STIG",
                    description="Failed STIG Security Checks",
                    acceptability=regscale_models.ImplementationStatus.NOT_IMPLEMENTED,
                    objectiveId=failing_objective.id,
                    securityControlId=failing_objective.securityControlId,
                    responsibility="Customer",
                ).create_or_update()

                _ = regscale_models.ImplementationObjective(
                    securityControlId=failing_objective.securityControlId,
                    implementationId=implementation_id,
                    objectiveId=failing_objective.id,
                    optionId=failing_option.id,
                    status=regscale_models.ImplementationStatus.NOT_IMPLEMENTED,
                    statement=failing_objective.description,
                    responsibility="Customer",
                ).create_or_update()

                # Create assessment and control test result
                assessment = self.get_or_create_assessment(implementation_id)
                if implementation_id:
                    control_test = self.create_or_get_control_test(finding, implementation_id)
                    self.create_control_test_result(
                        finding, control_test, assessment, regscale_models.ControlTestResultStatus.FAIL
                    )

    def handle_passing_checklist(
        self,
        finding: IntegrationFinding,
        plan_id: int,
    ) -> None:
        """
        Handles passing checklists by creating or updating implementation options and objectives.

        :param IntegrationFinding finding: The finding data
        :param int plan_id: The ID of the security plan
        :rtype: None
        """
        if finding.cci_ref:
            passing_objectives = regscale_models.ControlObjective.fetch_control_objectives_by_other_id(
                parent_id=plan_id, other_id_contains=finding.cci_ref
            )
            passing_objectives += regscale_models.ControlObjective.fetch_control_objectives_by_name(
                parent_id=plan_id, name_contains=finding.cci_ref
            )
            for passing_objective in passing_objectives:
                if passing_objective.name.lower().startswith("cci-"):
                    implementation_id = self.get_control_implementation_id_for_cci(passing_objective.name)
                else:
                    control_label = objective_to_control_dot(passing_objective.name)
                    if control_label not in self.control_implementation_id_map:
                        logger.warning("Control %s not found for %s", control_label, control_label)
                        continue
                    implementation_id = self.control_implementation_id_map[control_label]

                # Skip if we couldn't determine the implementation ID
                if implementation_id is None:
                    logger.warning("Could not determine implementation ID for objective %s", passing_objective.name)
                    continue

                passing_option = regscale_models.ImplementationOption(
                    name="Passed STIG",
                    description="Passed STIG Security Checks",
                    acceptability=regscale_models.ImplementationStatus.FULLY_IMPLEMENTED,
                    objectiveId=passing_objective.id,
                    securityControlId=passing_objective.securityControlId,
                    responsibility="Customer",
                ).create_or_update()

                _ = regscale_models.ImplementationObjective(
                    securityControlId=passing_objective.securityControlId,
                    implementationId=implementation_id,
                    objectiveId=passing_objective.id,
                    optionId=passing_option.id,
                    status=regscale_models.ImplementationStatus.FULLY_IMPLEMENTED,
                    statement=passing_objective.description,
                    responsibility="Customer",
                ).create_or_update()

                # Create assessment and control test result
                assessment = self.get_or_create_assessment(implementation_id)
                control_test = self.create_or_get_control_test(finding, implementation_id)
                self.create_control_test_result(
                    finding, control_test, assessment, regscale_models.ControlTestResultStatus.PASS
                )

    @staticmethod
    def create_or_get_control_test(
        finding: IntegrationFinding, control_implementation_id: int
    ) -> regscale_models.ControlTest:
        """
        Create or get an existing control test.

        :param IntegrationFinding finding: The finding associated with the control test
        :param int control_implementation_id: The ID of the control implementation
        :return: The created or existing control test
        :rtype: regscale_models.ControlTest
        """
        return regscale_models.ControlTest(
            uuid=finding.external_id,
            parentControlId=control_implementation_id,
            testCriteria=finding.cci_ref or finding.description,
        ).get_or_create()

    def get_asset_by_identifier(self, identifier: str) -> Optional[regscale_models.Asset]:
        """
        Gets an asset by its identifier

        :param str identifier: The identifier of the asset
        :return: The asset
        :rtype: Optional[regscale_models.Asset]
        """
        asset = self.asset_map_by_identifier.get(identifier)
        if not asset and identifier not in self.alerted_assets:
            self.alerted_assets.add(identifier)
            if not getattr(self, "suppress_asset_not_found_errors", False):
                self.log_error("1. Asset not found for identifier %s", identifier)
        return asset

    def get_issue_by_integration_finding_id(self, integration_finding_id: str) -> Optional[regscale_models.Issue]:
        """
        Gets an issue by its integration finding ID

        :param str integration_finding_id: The integration finding ID
        :return: The issue
        """
        return self.issues_map.get(integration_finding_id)

    def process_checklist(self, finding: IntegrationFinding) -> int:
        """
        Processes a single checklist item based on the provided finding.

        This method checks if the asset related to the finding exists, updates or creates a checklist item,
        and handles the finding based on its status (pass/fail).

        :param IntegrationFinding finding: The finding to process
        :return: 1 if the checklist was processed, 0 if not
        :rtype: int
        """
        logger.debug("Processing checklist %s", finding.external_id)
        if not (asset := self.get_asset_by_identifier(finding.asset_identifier)):
            if not getattr(self, "suppress_asset_not_found_errors", False):
                logger.error("2. Asset not found for identifier %s", finding.asset_identifier)
            return 0

        tool = regscale_models.ChecklistTool.STIGs
        if finding.vulnerability_type == "Vulnerability Scan":
            tool = regscale_models.ChecklistTool.VulnerabilityScanner

        if not finding.cci_ref:
            finding.cci_ref = "CCI-000366"

        logger.debug("Create or update checklist for %s", finding.external_id)
        regscale_models.Checklist(
            status=finding.checklist_status,
            assetId=asset.id,
            tool=tool,
            baseline=finding.baseline,
            vulnerabilityId=finding.vulnerability_number,
            results=finding.results,
            check=finding.title,
            cci=finding.cci_ref,
            ruleId=finding.rule_id,
            version=finding.rule_version,
            comments=finding.comments,
            datePerformed=finding.date_created,
        ).create_or_update()

        # For both passing and failing findings, let the vulnerability mapping handle the closure
        if finding.status != regscale_models.ChecklistStatus.PASS:
            logger.debug("Handling failing checklist for %s", finding.external_id)
            if self.type == ScannerIntegrationType.CHECKLIST:
                self.handle_failing_checklist(finding=finding, plan_id=self.plan_id)
            self.handle_failing_finding(
                issue_title=finding.issue_title or finding.title,
                finding=finding,
            )
        return 1

    def handle_control_finding(self, finding: IntegrationFinding) -> None:
        """
        Handle a control finding, either passing or failing.

        :param IntegrationFinding finding: The finding to handle
        :rtype: None
        """
        if finding.status == regscale_models.ControlTestResultStatus.PASS:
            # For passing findings, we'll let the normal vulnerability mapping closure handle it
            pass
        else:
            self.handle_failing_finding(
                issue_title="Finding %s failed",
                finding=finding,
            )

    def update_regscale_findings(self, findings: Iterator[IntegrationFinding]) -> int:
        """
        Updates RegScale findings, checklists, and vulnerabilities in a single pass.

        :param Iterator[IntegrationFinding] findings: The integration findings
        :return: The number of findings processed
        :rtype: int
        """
        logger.info("Updating RegScale findings...")
        scan_history = self.create_scan_history()
        current_vulnerabilities: Dict[int, Set[int]] = defaultdict(set)
        processed_findings_count = 0
        loading_findings = self._setup_finding_progress()

        # Process findings
        processed_findings_count = self._process_findings_with_threading(
            findings, scan_history, current_vulnerabilities, loading_findings
        )

        # Finalize processing
        self._finalize_finding_processing(scan_history, current_vulnerabilities)

        return processed_findings_count

    def _setup_finding_progress(self):
        """Setup progress tracking for findings processing."""
        return self.finding_progress.add_task(
            f"[#f8b737]Processing {f'{self.num_findings_to_process} ' if self.num_findings_to_process else ''}finding(s) from {self.title}",
            total=self.num_findings_to_process if self.num_findings_to_process else None,
        )

    def _process_findings_with_threading(
        self,
        findings: Iterator[IntegrationFinding],
        scan_history: regscale_models.ScanHistory,
        current_vulnerabilities: Dict[int, Set[int]],
        loading_findings,
    ) -> int:
        """Process findings using threading or sequential processing."""
        processed_findings_count = 0
        count_lock = threading.RLock()

        def process_finding_with_progress(finding_to_process: IntegrationFinding) -> None:
            """Process a single finding and update progress."""
            nonlocal processed_findings_count
            try:
                self.process_finding(finding_to_process, scan_history, current_vulnerabilities)
                with count_lock:
                    processed_findings_count += 1
                    self._update_finding_progress(loading_findings)
            except Exception as exc:
                self.log_error(
                    "An error occurred when processing finding %s: %s",
                    finding_to_process.external_id,
                    exc,
                )

        if get_thread_workers_max() == 1:
            for finding in findings:
                process_finding_with_progress(finding)
        else:
            processed_findings_count = self._process_findings_in_batches(findings, process_finding_with_progress)

        return processed_findings_count

    def _update_finding_progress(self, loading_findings):
        """Update the finding progress bar."""
        if self.num_findings_to_process:
            self.finding_progress.update(
                loading_findings,
                total=self.num_findings_to_process,
                description=f"[#f8b737]Processing {self.num_findings_to_process} findings from {self.title}.",
            )
        self.finding_progress.advance(loading_findings, 1)

    def _process_findings_in_batches(
        self, findings: Iterator[IntegrationFinding], process_finding_with_progress
    ) -> int:
        """Process findings in batches using thread pool executor."""
        processed_findings_count = 0
        batch_size = get_thread_workers_max() * 2

        with concurrent.futures.ThreadPoolExecutor(max_workers=get_thread_workers_max()) as executor:
            batch = []
            for finding in findings:
                batch.append(finding)
                if len(batch) >= batch_size:
                    # Process this batch
                    list(executor.map(process_finding_with_progress, batch))
                    processed_findings_count += len(batch)
                    # Clear the batch
                    batch = []

            # Process any remaining items
            if batch:
                list(executor.map(process_finding_with_progress, batch))
                processed_findings_count += len(batch)

        return processed_findings_count

    def _finalize_finding_processing(
        self, scan_history: regscale_models.ScanHistory, current_vulnerabilities: Dict[int, Set[int]]
    ) -> None:
        """Finalize the finding processing by saving scan history and closing outdated issues."""
        logger.info(
            f"Saving scan history with final counts - Low: {scan_history.vLow}, Medium: {scan_history.vMedium}, High: {scan_history.vHigh}, Critical: {scan_history.vCritical}, Info: {scan_history.vInfo}"
        )

        # Ensure scan history is properly saved with updated counts
        try:
            scan_history.save()
        except Exception as e:
            logger.error(f"Error saving scan history: {e}")
            # Try to save again with a fresh fetch
            try:
                scan_history.fetch()
                scan_history.save()
            except Exception as e2:
                logger.error(f"Failed to save scan history after retry: {e2}")

        self._results["scan_history"] = scan_history
        self.update_result_counts("issues", regscale_models.Issue.bulk_save(progress_context=self.finding_progress))
        self.close_outdated_issues(current_vulnerabilities)
        self._perform_batch_operations(self.finding_progress)

    @staticmethod
    def parse_poam_id(poam_identifier: str) -> Optional[int]:
        """
        Parses a POAM identifier string to extract the numeric ID.

        :param str poam_identifier: The POAM identifier string (e.g. "V-1234")
        :return: The numeric ID portion, or None if invalid format
        :rtype: Optional[int]
        """
        if not poam_identifier or not poam_identifier.startswith("V-"):
            return None
        try:
            return int("".join(c for c in poam_identifier.split("-")[1] if c.isdigit()))
        except (IndexError, ValueError):
            return None

    def get_next_poam_id(self) -> int:
        """
        Retrieves the Next POAM ID for the current security plan in a thread-safe manner.

        :return: The Next POAM ID
        :rtype: int
        """
        # Use the class's _get_lock method to get a thread-safe lock
        with self._get_lock("poam_id"):
            # If we haven't cached the max ID yet
            if not isinstance(self._max_poam_id, int):
                logger.info("Fetching max POAM ID...")
                # Get all existing POAM IDs and find the maximum
                issues: List[regscale_models.Issue] = regscale_models.Issue.get_all_by_parent(
                    parent_id=self.plan_id,
                    parent_module=self.parent_module,
                )
                # Extract parsed IDs for valid identifiers
                parsed_ids = []
                for issue in issues:
                    if issue.otherIdentifier:
                        parsed_id = self.parse_poam_id(issue.otherIdentifier)
                        if parsed_id is not None:
                            parsed_ids.append(parsed_id)

                self._max_poam_id = max(parsed_ids, default=0)

            # Increment the cached max ID and store it
            self._max_poam_id = (self._max_poam_id or 0) + 1
            return self._max_poam_id

    def create_scan_history(self) -> regscale_models.ScanHistory:
        """
        Creates a new ScanHistory object for the current scan.

        :return: A newly created ScanHistory object
        :rtype: regscale_models.ScanHistory
        """
        scan_history = regscale_models.ScanHistory(
            parentId=self.plan_id,
            parentModule=self.parent_module,
            scanningTool=self.title,
            scanDate=self.scan_date if self.scan_date else get_current_datetime(),
            createdById=self.assessor_id,
            tenantsId=self.tenant_id,
            vLow=0,
            vMedium=0,
            vHigh=0,
            vCritical=0,
        ).create()

        count = 0
        regscale_models.ScanHistory.delete_object_cache(scan_history)
        while not regscale_models.ScanHistory.get_object(object_id=scan_history.id) or count > 10:
            logger.info("Waiting for ScanHistory to be created...")
            time.sleep(1)
            count += 1
            regscale_models.ScanHistory.delete_object_cache(scan_history)
        return scan_history

    def process_finding(
        self,
        finding: IntegrationFinding,
        scan_history: regscale_models.ScanHistory,
        current_vulnerabilities: Dict[int, Set[int]],
    ) -> None:
        """
        Process a single finding, handling both checklist and vulnerability cases.

        :param IntegrationFinding finding: The finding to process
        :param regscale_models.ScanHistory scan_history: The current scan history
        :param Dict[int, Set[int]] current_vulnerabilities: Dictionary of current vulnerabilities
        :rtype: None
        """
        # Update finding dates if scan date is set
        finding = self.update_integration_finding_dates(
            finding=finding,
            existing_issues_dict={},  # We'll handle issue lookup in create_or_update_issue_from_finding
            scan_history=scan_history,
        )

        # Process checklist if applicable
        if self.type == ScannerIntegrationType.CHECKLIST:
            self._process_checklist_finding(finding)

        # Process vulnerability if applicable
        if finding.status != regscale_models.IssueStatus.Closed or ScannerVariables.ingestClosedIssues:
            vulnerability_created = self._process_vulnerability_finding(finding, scan_history, current_vulnerabilities)

            self.handle_failing_finding(
                issue_title=finding.issue_title or finding.title,
                finding=finding,
            )

            # Update scan history severity counts only if vulnerability was successfully created
            if vulnerability_created:
                logger.debug(
                    f"Updating severity count for successfully created vulnerability with severity: {finding.severity}"
                )
                self.set_severity_count_for_scan(finding.severity, scan_history)
            else:
                logger.debug(
                    f"Skipping severity count update for finding {finding.external_id} - no vulnerability created"
                )

    def _process_checklist_finding(self, finding: IntegrationFinding) -> None:
        """Process a checklist finding."""
        if not (asset := self.get_asset_by_identifier(finding.asset_identifier)):
            if not getattr(self, "suppress_asset_not_found_errors", False):
                logger.error("2. Asset not found for identifier %s", finding.asset_identifier)
            return

        tool = regscale_models.ChecklistTool.STIGs
        if finding.vulnerability_type == "Vulnerability Scan":
            tool = regscale_models.ChecklistTool.VulnerabilityScanner

        if not finding.cci_ref:
            finding.cci_ref = "CCI-000366"

        # Convert checklist status to string
        checklist_status_str = str(finding.checklist_status.value)

        logger.debug("Create or update checklist for %s", finding.external_id)
        regscale_models.Checklist(
            status=checklist_status_str,
            assetId=asset.id,
            tool=tool,
            baseline=finding.baseline,
            vulnerabilityId=finding.vulnerability_number,
            results=finding.results,
            check=finding.title,
            cci=finding.cci_ref,
            ruleId=finding.rule_id,
            version=finding.rule_version,
            comments=finding.comments,
            datePerformed=finding.date_created,
        ).create_or_update()

        # Handle checklist status
        self._handle_checklist_status(finding)

    def _handle_checklist_status(self, finding: IntegrationFinding) -> None:
        """Handle the status of a checklist finding."""
        if finding.status != regscale_models.IssueStatus.Closed:
            logger.debug("Handling failing checklist for %s", finding.external_id)
            if self.type == ScannerIntegrationType.CHECKLIST:
                self.handle_failing_checklist(finding=finding, plan_id=self.plan_id)
        else:
            logger.debug("Handling passing checklist for %s", finding.external_id)
            self.handle_passing_checklist(finding=finding, plan_id=self.plan_id)

    def _process_vulnerability_finding(
        self,
        finding: IntegrationFinding,
        scan_history: regscale_models.ScanHistory,
        current_vulnerabilities: Dict[int, Set[int]],
    ) -> bool:
        """Process a vulnerability finding and return whether vulnerability was created."""
        logger.debug(f"Processing vulnerability for finding {finding.external_id} with status {finding.status}")

        if asset := self.get_asset_by_identifier(finding.asset_identifier):
            logger.debug(f"Found asset {asset.id} for finding {finding.external_id}")
            if vulnerability_id := self.handle_vulnerability(finding, asset, scan_history):
                current_vulnerabilities[asset.id].add(vulnerability_id)
                logger.debug(
                    f"Vulnerability created successfully for finding {finding.external_id} with ID {vulnerability_id}"
                )
                return True
            else:
                logger.debug(f"Vulnerability creation failed for finding {finding.external_id}")
        else:
            logger.debug(f"No asset found for finding {finding.external_id} with identifier {finding.asset_identifier}")

        return False

    def handle_vulnerability(
        self,
        finding: IntegrationFinding,
        asset: Optional[regscale_models.Asset],
        scan_history: regscale_models.ScanHistory,
    ) -> Optional[int]:
        """
        Handles the vulnerabilities for a finding.

        :param IntegrationFinding finding: The integration finding
        :param Optional[regscale_models.Asset] asset: The associated asset
        :param regscale_models.ScanHistory scan_history: The scan history
        :rtype: Optional[int]
        :return: The vulnerability ID
        """
        logger.debug(f"Processing vulnerability for finding: {finding.external_id} - {finding.title}")

        # Check for required fields - either plugin_name or cve must be present
        plugin_name = getattr(finding, "plugin_name", None)
        cve = getattr(finding, "cve", None)

        if not plugin_name and not cve:
            logger.warning("No Plugin Name or CVE found for finding %s", finding.title)
            logger.debug(f"Finding plugin_name: {plugin_name}, cve: {cve}")
            return None

        if not asset:
            if not getattr(self, "suppress_asset_not_found_errors", False):
                logger.warning(
                    "VulnerabilityMapping Error: Asset not found for identifier %s", finding.asset_identifier
                )
            return None

        logger.debug(f"Found asset: {asset.id} for finding {finding.external_id}")
        logger.debug(f"Finding plugin_name: {plugin_name}, cve: {cve}")

        # Add retry logic for vulnerability creation
        max_retries = 3
        retry_delay = 2  # seconds

        for attempt in range(max_retries):
            try:
                logger.debug(f"Creating vulnerability for finding {finding.external_id} (attempt {attempt + 1})")
                vulnerability = self.create_vulnerability_from_finding(finding, asset, scan_history)
                finding.vulnerability_id = vulnerability.id
                logger.info(f"Successfully created vulnerability {vulnerability.id} for finding {finding.external_id}")

                if ScannerVariables.vulnerabilityCreation.lower() != "noissue":
                    # Handle associated issue
                    self.create_or_update_issue_from_finding(
                        title=finding.title,
                        finding=finding,
                    )

                return vulnerability.id

            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Vulnerability creation failed for finding {finding.external_id} (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {retry_delay} seconds..."
                    )
                    import time

                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error(
                        f"Failed to create vulnerability for finding {finding.external_id} after {max_retries} attempts: {e}"
                    )
                    return None

    def create_vulnerability_from_finding(
        self, finding: IntegrationFinding, asset: regscale_models.Asset, scan_history: regscale_models.ScanHistory
    ) -> regscale_models.Vulnerability:
        """
        Creates a vulnerability from an integration finding.

        :param IntegrationFinding finding: The integration finding
        :param regscale_models.Asset asset: The associated asset
        :param regscale_models.ScanHistory scan_history: The scan history
        :return: The created vulnerability
        :rtype: regscale_models.Vulnerability
        """
        logger.debug(f"Creating vulnerability object for finding {finding.external_id}")

        logger.debug(f"Finding severity: '{finding.severity}' (type: {type(finding.severity)})")
        mapped_severity = self.issue_to_vulnerability_map.get(
            finding.severity, regscale_models.VulnerabilitySeverity.Low
        )
        logger.debug(f"Mapped severity: {mapped_severity}")

        vulnerability = regscale_models.Vulnerability(
            title=finding.title,
            cve=finding.cve,
            vprScore=(
                finding.vpr_score if hasattr(finding, "vprScore") else None
            ),  # If this is the VPR score, otherwise use a different field
            cvsSv3BaseScore=finding.cvss_v3_base_score or finding.cvss_v3_score or finding.cvss_score,
            cvsSv2BaseScore=finding.cvss_v2_score,
            cvsSv3BaseVector=finding.cvss_v3_vector,
            cvsSv2BaseVector=finding.cvss_v2_vector,
            scanId=scan_history.id,
            severity=mapped_severity,
            description=finding.description,
            dateLastUpdated=finding.date_last_updated,
            parentId=self.plan_id,
            parentModule=self.parent_module,
            dns=asset.fqdn or "unknown",
            status=regscale_models.VulnerabilityStatus.Open,
            ipAddress=finding.ip_address or asset.ipAddress or "",
            firstSeen=finding.first_seen,
            lastSeen=finding.last_seen,
            plugInName=finding.cve or finding.plugin_name,  # Use CVE if available, otherwise use plugin name
            plugInId=finding.plugin_id,
            exploitAvailable=None,  # Set this if you have information about exploit availability
            plugInText=finding.plugin_text
            or finding.observations,  # or finding.evidence, whichever is more appropriate
            port=finding.port if hasattr(finding, "port") else None,
            protocol=finding.protocol if hasattr(finding, "protocol") else None,
            operatingSystem=asset.operatingSystem if hasattr(asset, "operatingSystem") else None,
            fixedVersions=finding.fixed_versions,
            buildVersion=finding.build_version,
            fixStatus=finding.fix_status,
            installedVersions=finding.installed_versions,
            affectedOS=finding.affected_os,
            packagePath=finding.package_path,
            imageDigest=finding.image_digest,
            affectedPackages=finding.affected_packages,
        )

        logger.debug(f"Calling create_or_update for vulnerability with title: {vulnerability.title}")
        vulnerability = vulnerability.create_or_update()
        logger.debug(f"Vulnerability created/updated with ID: {vulnerability.id}")

        logger.debug(f"Creating vulnerability mapping for vulnerability {vulnerability.id}")
        logger.debug(f"Scan History ID: {scan_history.id}, Asset ID: {asset.id}, Plan ID: {self.plan_id}")

        vulnerability_mapping = regscale_models.VulnerabilityMapping(
            vulnerabilityId=vulnerability.id,
            assetId=asset.id,
            scanId=scan_history.id,
            securityPlanId=self.plan_id if not self.is_component else None,
            createdById=self.assessor_id,
            tenantsId=self.tenant_id,
            isPublic=True,
            dateCreated=get_current_datetime(),
            firstSeen=finding.first_seen,
            lastSeen=finding.last_seen,
            status=finding.status,
            dateLastUpdated=get_current_datetime(),
        )

        logger.debug(
            f"Vulnerability mapping payload: vulnerabilityId={vulnerability_mapping.vulnerabilityId}, "
            f"assetId={vulnerability_mapping.assetId}, scanId={vulnerability_mapping.scanId}"
        )

        vulnerability_mapping.create_unique()
        logger.debug(f"Vulnerability mapping created for vulnerability {vulnerability.id}")

        return vulnerability

    def _filter_vulns_open_by_other_tools(
        self, all_vulns: list[regscale_models.Vulnerability]
    ) -> list[regscale_models.Vulnerability]:
        """
        Fetch vulnerabilities that are open and not associated with other tools.
        :param list[regscale_models.Vulnerability] all_vulns: List of all vulnerabilities to check the scanningTool
        :return: List of matching vulnerabilities
        :rtype: list[regscale_models.Vulnerability]
        """
        vuln_list = []
        for vuln in all_vulns:
            other_tool = False
            open_vuln_mappings = regscale_models.VulnerabilityMapping.find_by_vulnerability(vuln.id, status="Open")
            for vuln_mapping in open_vuln_mappings:
                if vuln_mapping.scanId is not None:
                    scan_history = regscale_models.ScanHistory.get_object(vuln_mapping.scanId)
                    if scan_history and scan_history.scanningTool != self.title:
                        other_tool = True
                        break
            if not other_tool:
                vuln_list.append(vuln)
        return vuln_list

    def close_outdated_vulnerabilities(self, current_vulnerabilities: Dict[int, Set[int]]) -> None:
        """
        Closes vulnerabilities that are not in the current set of vulnerability IDs for each asset.

        :param Dict[int, Set[int]] current_vulnerabilities: Dictionary of asset IDs to lists of current vulnerability IDs
        :rtype: None
        """
        # Get all current vulnerability IDs
        current_vuln_ids = {vuln_id for vuln_ids in current_vulnerabilities.values() for vuln_id in vuln_ids}

        # Get all vulnerabilities for this security plan
        all_vulnerabilities: list[regscale_models.Vulnerability] = regscale_models.Vulnerability.get_all_by_parent(
            parent_id=self.plan_id, parent_module=self.parent_module
        )

        # Pre-filter vulnerabilities that are not in current set
        outdated_vulns = [v for v in all_vulnerabilities if v.id not in current_vuln_ids]

        # Filter by tool
        tool_vulns = self._filter_vulns_open_by_other_tools(all_vulns=outdated_vulns)

        closed_count = 0
        for vuln in tool_vulns:
            if vuln.status != regscale_models.VulnerabilityStatus.Closed:
                self.close_mappings_list(vuln)  # Close matching mappings
                vuln.status = regscale_models.VulnerabilityStatus.Closed
                vuln.dateClosed = get_current_datetime()
                vuln.save()
                closed_count += 1
                logger.info("Closed vulnerability %d", vuln.id)

        logger.info("Closed %d outdated vulnerabilities.", closed_count)

    @classmethod
    def close_mappings_list(cls, vuln: regscale_models.Vulnerability) -> None:
        """
        Close all mappings for a vulnerability.

        :param regscale_models.Vulnerability vuln: The vulnerability to close mappings for
        :rtype: None
        """
        mappings: List[regscale_models.VulnerabilityMapping] = [
            mapping
            for mapping in regscale_models.VulnerabilityMapping.find_by_vulnerability(
                vuln.id, status=regscale_models.IssueStatus.Open
            )
            if mapping is not None
        ]
        for mapping in mappings:
            # Don't close for other tools
            if mapping.scanId:
                scan = regscale_models.ScanHistory.get_object(mapping.scanId)
                if scan and scan.scanningTool != cls.title:
                    continue

            # This one uses IssueStatus
            mapping.status = regscale_models.IssueStatus.Closed
            mapping.dateClosed = get_current_datetime()
            mapping.save()

    def close_outdated_issues(self, current_vulnerabilities: Dict[int, Set[int]]) -> int:
        """
        Closes issues that are not associated with current vulnerabilities for each asset.
        After closing issues, updates the status of affected control implementations.

        :param Dict[int, Set[int]] current_vulnerabilities: Dictionary mapping asset IDs to sets of current vulnerability IDs
        :return: Number of issues closed
        :rtype: int
        """
        if not self.close_outdated_findings:
            logger.info("Skipping closing outdated issues.")
            return 0

        closed_count = 0
        affected_control_ids = set()
        count_lock = threading.Lock()

        open_issues = regscale_models.Issue.fetch_issues_by_ssp(
            None, ssp_id=self.plan_id, status=regscale_models.IssueStatus.Open.value
        )
        task_id = self.finding_progress.add_task(
            f"[cyan]Analyzing {len(open_issues)} issue(s) and closing any outdated issue(s)...", total=len(open_issues)
        )

        def _process_single_issue(iss: regscale_models.Issue):
            """
            Process a single issue and update its status if necessary.

            :param regscale_models.Issue iss: The issue to process
            """
            if self.should_close_issue(iss, current_vulnerabilities):
                self._close_issue(iss, count_lock, affected_control_ids)
            with count_lock:
                self.finding_progress.update(task_id, advance=1)

        max_workers = get_thread_workers_max()
        if max_workers == 1:
            for issue in open_issues:
                _process_single_issue(issue)
        else:
            self._process_issues_multithreaded(open_issues, _process_single_issue, max_workers)

        for control_id in affected_control_ids:
            self.update_control_implementation_status_after_close(control_id)

        (
            logger.info("Closed %d outdated issues.", closed_count)
            if closed_count > 0
            else logger.info("No outdated issues to close.")
        )
        return closed_count

    def _close_issue(self, issue: regscale_models.Issue, count_lock: threading.Lock, affected_control_ids: set):
        """
        Close an issue and update related data.

        :param regscale_models.Issue issue: The issue to close
        :param threading.Lock count_lock: A lock to synchronize access to shared variables
        :param set affected_control_ids: A set to store affected control implementation IDs
        """
        issue.status = regscale_models.IssueStatus.Closed
        issue.dateCompleted = get_current_datetime()
        changes_text = (
            f"{get_current_datetime('%b %d, %Y')} - Closed by {self.title} for having no current vulnerabilities."
        )
        issue.changes = f"{issue.changes}\n{changes_text}" if issue.changes else changes_text
        issue.dateLastUpdated = get_current_datetime()
        issue.save()

        if ScannerVariables.useMilestones and issue.id:
            regscale_models.Milestone(
                title=f"Issue closed from {self.title} scan",
                milestoneDate=issue.dateCompleted,
                responsiblePersonId=self.assessor_id,
                completed=True,
                parentID=issue.id,
                parentModule="issues",
            ).create()
            logger.debug("Created milestone for issue %s from %s tool", issue.id, self.title)

        with count_lock:
            self.closed_count += 1
            if issue.controlImplementationIds:
                affected_control_ids.update(issue.controlImplementationIds)

    def _process_issues_multithreaded(self, open_issues: list, process_issue: callable, max_workers: int):
        """
        Process issues using multiple threads.

        :param list open_issues: List of open issues to process
        :param callable process_issue: Function to process an issue
        :param int max_workers: Maximum number of threads
        """
        batch_size = max_workers * 2
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            batch = []
            futures = []

            for issue in open_issues:
                batch.append(issue)
                if len(batch) >= batch_size:
                    futures.extend([executor.submit(process_issue, issue) for issue in batch])
                    batch = []

            if batch:
                futures.extend([executor.submit(process_issue, issue) for issue in batch])

            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as exc:
                    self.log_error("Error processing issue: %s", exc)

    def update_control_implementation_status_after_close(self, control_id: int) -> None:
        """
        Updates the status of a control implementation after closing issues.
        Sets to FULLY_IMPLEMENTED if no open issues remain, NOT_IMPLEMENTED if any issues are open.

        :param int control_id: The ID of the control implementation to update
        :rtype: None
        """
        # Get the control implementation
        control_implementation = self.control_implementation_map.get(
            control_id
        ) or regscale_models.ControlImplementation.get_object(object_id=control_id)

        if not control_implementation:
            logger.warning("Control implementation %d not found", control_id)
            return

        # Check if there are any open issues for this control implementation
        open_issues = self.existing_issue_ids_by_implementation_map.get(control_id, [])

        # Set status based on presence of open issues
        new_status = (
            regscale_models.ImplementationStatus.FULLY_IMPLEMENTED
            if not open_issues
            else regscale_models.ImplementationStatus.NOT_IMPLEMENTED
        )

        if control_implementation.status != new_status:
            control_implementation.status = new_status
            self.control_implementation_map[control_id] = control_implementation.save()
            logger.info("Updated control implementation %d status to %s", control_id, new_status)

    def should_close_issue(self, issue: regscale_models.Issue, current_vulnerabilities: Dict[int, Set[int]]) -> bool:
        """
        Determines if an issue should be closed based on current vulnerabilities.
        An issue should be closed if it has no more active vulnerability mappings for any assets.

        :param regscale_models.Issue issue: The issue to check
        :param Dict[int, Set[int]] current_vulnerabilities: Dictionary of current vulnerabilities
        :return: True if the issue should be closed, False otherwise
        :rtype: bool
        """
        # Do not close issues from other tools
        if issue.sourceReport != self.title:
            logger.debug(
                "Skipping issue %d from different source: %s (expected: %s)", issue.id, issue.sourceReport, self.title
            )
            return False

        # If the issue has a vulnerability ID, check if it's still current for any asset
        if issue.vulnerabilityId:
            # Get vulnerability mappings for this issue
            vuln_mappings = regscale_models.VulnerabilityMapping.find_by_issue(
                issue.id, status=regscale_models.IssueStatus.Open
            )

            # Check if the issue's vulnerability is still current for any asset
            # If it is, we shouldn't close the issue
            for mapping in vuln_mappings:
                if mapping.assetId in current_vulnerabilities:
                    if issue.vulnerabilityId in current_vulnerabilities[mapping.assetId]:
                        logger.debug(
                            "Issue %d has current vulnerability %d for asset %d",
                            issue.id,
                            issue.vulnerabilityId,
                            mapping.assetId,
                        )
                        return False

        # If we've checked all conditions and found no current vulnerabilities, we should close it
        logger.debug("Issue %d has no current vulnerabilities, marking for closure", issue.id)
        return True

    @staticmethod
    def set_severity_count_for_scan(severity: str, scan_history: regscale_models.ScanHistory) -> None:
        """
        Increments the count of the severity
        :param str severity: Severity of the vulnerability
        :param regscale_models.ScanHistory scan_history: Scan history object
        :rtype: None
        """
        logger.debug(f"Setting severity count for scan {scan_history.id}: severity='{severity}'")
        logger.debug(
            f"Current counts - Low: {scan_history.vLow}, Medium: {scan_history.vMedium}, High: {scan_history.vHigh}, Critical: {scan_history.vCritical}, Info: {scan_history.vInfo}"
        )

        if severity == regscale_models.IssueSeverity.Low.value:
            scan_history.vLow += 1
            logger.debug(f"Incremented vLow count to {scan_history.vLow}")
        elif severity == regscale_models.IssueSeverity.Moderate.value:
            scan_history.vMedium += 1
            logger.debug(f"Incremented vMedium count to {scan_history.vMedium}")
        elif severity == regscale_models.IssueSeverity.High.value:
            scan_history.vHigh += 1
            logger.debug(f"Incremented vHigh count to {scan_history.vHigh}")
        elif severity == regscale_models.IssueSeverity.Critical.value:
            scan_history.vCritical += 1
            logger.debug(f"Incremented vCritical count to {scan_history.vCritical}")
        else:
            scan_history.vInfo += 1
            logger.debug(f"Incremented vInfo count to {scan_history.vInfo}")

        logger.debug(
            f"Final counts - Low: {scan_history.vLow}, Medium: {scan_history.vMedium}, High: {scan_history.vHigh}, Critical: {scan_history.vCritical}, Info: {scan_history.vInfo}"
        )

        # Save the scan history immediately to persist the count changes
        try:
            scan_history.save()
            logger.debug(f"Successfully saved scan history {scan_history.id} with updated counts")
        except Exception as e:
            logger.error(f"Error saving scan history {scan_history.id} after updating counts: {e}")
            # Try to save again with a fresh fetch
            try:
                scan_history.fetch()
                scan_history.save()
                logger.debug(f"Successfully saved scan history {scan_history.id} after retry")
            except Exception as e2:
                logger.error(f"Failed to save scan history {scan_history.id} after retry: {e2}")

    @classmethod
    def cci_assessment(cls, plan_id: int) -> None:
        """
        Creates or updates CCI assessments in RegScale

        :param int plan_id: The ID of the security plan
        :rtype: None
        """
        instance = cls(plan_id=plan_id)
        for control_id, ccis in instance.get_control_to_cci_map().items():
            if not (implementation_id := instance.control_id_to_implementation_map.get(control_id)):
                logger.error("Control Implementation for %d not found in RegScale", control_id)
                continue
            assessment = instance.get_or_create_assessment(implementation_id)
            assessment_result = regscale_models.AssessmentResultsStatus.PASS
            open_issues: List[OpenIssueDict] = instance.existing_issue_ids_by_implementation_map.get(
                implementation_id, []
            )
            ccis.add("CCI-000366")
            for cci in sorted(ccis):
                logger.debug("Creating assessment for CCI %s for implementation %d", cci, implementation_id)
                result = regscale_models.ControlTestResultStatus.PASS
                for issue in open_issues:
                    if cci.lower() in issue.get("integrationFindingId", "").lower():
                        result = regscale_models.ControlTestResultStatus.FAIL
                        assessment_result = regscale_models.AssessmentResultsStatus.FAIL
                        break

                control_test_key = f"{implementation_id}-{cci}"
                control_test = instance.control_tests_map.get(
                    control_test_key,
                    regscale_models.ControlTest(
                        parentControlId=implementation_id,
                        testCriteria=cci,
                    ).get_or_create(),
                )
                regscale_models.ControlTestResult(
                    parentTestId=control_test.id if control_test else None,
                    parentAssessmentId=assessment.id,
                    result=result,
                    dateAssessed=get_current_datetime(),
                    assessedById=instance.assessor_id,
                ).create()
            assessment.assessmentResult = assessment_result
            assessment.save()

    @classmethod
    def sync_findings(cls, plan_id: int, **kwargs) -> int:
        """
        Synchronizes findings from the integration to RegScale.

        :param int plan_id: The ID of the RegScale SSP
        :return: The number of findings processed
        :rtype: int
        """
        logger.info("Syncing %s findings...", kwargs.get("title", cls.title))
        instance = cls(plan_id=plan_id, **kwargs)
        instance.set_keys(**kwargs)
        instance.ensure_data_types()
        # If a progress object was passed, use it instead of creating a new one
        instance.finding_progress = kwargs.pop("progress") if "progress" in kwargs else create_progress_object()
        instance.enable_finding_date_update = kwargs.get("enable_finding_date_update", False)
        if finding_count := kwargs.get("finding_count"):
            instance.num_findings_to_process = finding_count
        kwargs["plan_id"] = plan_id

        with instance.finding_progress:
            findings = instance.fetch_findings(**kwargs)
            # Update the asset map with the latest assets
            logger.info("Getting asset map...")
            instance.asset_map_by_identifier.update(instance.get_asset_map())
            findings_processed = instance.update_regscale_findings(findings=findings)

        if instance.errors:
            logger.error("Summary of errors encountered:")
            for error in instance.errors:
                logger.error(error)
        else:
            logger.info("All findings have been processed successfully.")

        if scan_history := instance._results.get("scan_history"):
            open_count = (
                scan_history.vCritical
                + scan_history.vHigh
                + scan_history.vMedium
                + scan_history.vLow
                + scan_history.vInfo
            )
            closed_count = findings_processed - open_count
            logger.info(
                "Processed %d total findings. Open vulnerabilities: %d & Closed vulnerabilities: %d",
                findings_processed,
                open_count,
                closed_count,
            )
            logger.info(
                "%d Open vulnerabilities: Critical(s): %d, High(s): %d, Medium(s): %d, Low(s): %d, and %d Info(s).",
                open_count,
                scan_history.vCritical,
                scan_history.vHigh,
                scan_history.vMedium,
                scan_history.vLow,
                scan_history.vInfo,
            )
        else:
            logger.info("Processed %d findings.", findings_processed)
        issue_created_count = instance._results.get("issues", {}).get("created_count", 0)
        issue_updated_count = instance._results.get("issues", {}).get("updated_count", 0)
        if issue_created_count or issue_updated_count:
            logger.info(
                "Created %d issue(s) and updated %d issue(s) in RegScale.",
                issue_created_count,
                issue_updated_count,
            )
        return findings_processed

    @classmethod
    def sync_assets(cls, plan_id: int, **kwargs) -> int:
        """
        Synchronizes assets from the integration to RegScale.

        :param int plan_id: The ID of the RegScale SSP
        :return: The number of assets processed
        :rtype: int
        """
        logger.info("Syncing %s assets...", kwargs.get("title", cls.title))
        instance = cls(plan_id=plan_id, **kwargs)
        instance.set_keys(**kwargs)
        instance.ensure_data_types()
        instance.asset_progress = kwargs.pop("progress") if "progress" in kwargs else create_progress_object()
        if asset_count := kwargs.get("asset_count"):
            instance.num_assets_to_process = asset_count

        with instance.asset_progress:
            assets = instance.fetch_assets(**kwargs)
            assets_processed = instance.update_regscale_assets(assets=assets)

        if instance.errors:
            logger.error("Summary of errors encountered:")
            for error in instance.errors:
                logger.error(error)
        else:
            logger.info("All assets have been processed successfully.")

        APIHandler().log_api_summary()
        created_count = instance._results.get("assets", {}).get("created_count", 0)
        updated_count = instance._results.get("assets", {}).get("updated_count", 0)
        dedupe_count = (instance.num_assets_to_process or assets_processed) - (created_count + updated_count)
        # Ensure dedupe_count is always a positive value
        dedupe_count = dedupe_count if dedupe_count >= 0 else dedupe_count * -1
        logger.info(
            "%d assets processed and %d asset(s) deduped. %d asset(s) created & %d asset(s) updated in RegScale.",
            assets_processed,
            dedupe_count,
            created_count,
            updated_count,
        )
        return assets_processed

    @classmethod
    def set_keys(cls, **kwargs):
        """
        Set the attributes for an integration
        :rtype: None
        """
        for key, value in kwargs.items():
            if hasattr(cls, key):
                setattr(cls, key, value)
            else:
                logger.debug("Unable to set the %s attribute", key)

    def ensure_data_types(self) -> None:
        """
        A method to enforce kwarg data types.

        :return: None
        :rtype: None
        """
        # Ensure scan_date is a string
        if not isinstance(self.scan_date, str):
            self.scan_date = date_str(self.scan_date)

    def log_error(self, msg: str, *args) -> None:
        """
        Logs an error message

        :param str msg: The error message
        :rtype: None
        """
        logger.error(msg, *args, exc_info=True)
        self.errors.append(msg % args)

    def update_integration_finding_dates(
        self,
        finding: IntegrationFinding,
        existing_issues_dict: Dict[str, regscale_models.Issue],
        scan_history: regscale_models.ScanHistory,
    ) -> IntegrationFinding:
        """
        Update the dates of the integration finding based on the scan date and whether the finding is new or existing.

        :param IntegrationFinding finding: The integration finding
        :param Dict[str, regscale_models.Issue] existing_issues_dict: Dictionary of existing issues
        :param regscale_models.ScanHistory scan_history: List of existing scan history objects
        :return: The updated integration finding or the original finding if the scan date is not set
        :rtype: IntegrationFinding
        """
        if self.scan_date and self.enable_finding_date_update:
            issue = self.get_issue(existing_issues_dict, finding)
            vulnerabilities = (
                self.get_vulnerabilities(issue=issue, status=regscale_models.IssueStatus.Open) if issue else []
            )
            existing_vuln = self.get_existing_vuln(vulnerabilities, finding)
            finding = self.update_finding_dates(finding, existing_vuln, issue)
            self.update_scan(scan_history=scan_history)

        return finding

    def get_issue(
        self, existing_issues_dict: Dict[str, regscale_models.Issue], finding: IntegrationFinding
    ) -> Optional[regscale_models.Issue]:
        """
        Get the existing issue for the integration finding

        :param Dict[str, regscale_models.Issue] existing_issues_dict: Dictionary of existing issues
        :param IntegrationFinding finding: The integration finding
        :return: The existing issue
        :rtype: Optional[regscale_models.Issue]
        """
        return existing_issues_dict.get(f"{self.get_finding_identifier(finding)}_{finding.asset_identifier}")

    @staticmethod
    def get_vulnerabilities(issue: regscale_models.Issue, status: str) -> List[regscale_models.VulnerabilityMapping]:
        """
        Get the vulnerabilities for the issue

        :param regscale_models.Issue issue: The issue
        :param str status: The status of the vulnerability
        :return: The list of vulnerabilities
        :rtype: List[regscale_models.VulnerabilityMapping]
        """
        return regscale_models.VulnerabilityMapping.find_by_issue(issue.id, status=status) if issue else []

    def get_existing_vuln(
        self, vulnerabilities: List[regscale_models.VulnerabilityMapping], finding: IntegrationFinding
    ) -> Optional[regscale_models.VulnerabilityMapping]:
        """
        Get the existing vulnerability for the integration finding

        :param List[regscale_models.VulnerabilityMapping] vulnerabilities: The list of existing vulnerabilities
        :param IntegrationFinding finding: The integration finding
        :return: The existing vulnerability
        :rtype: Optional[regscale_models.VulnerabilityMapping]
        """
        existing_vuln = min(vulnerabilities, key=lambda vuln: vuln.firstSeen) if vulnerabilities else None
        scan_date = date_obj(self.scan_date)
        first_seen = date_obj(finding.first_seen)
        if existing_vuln and scan_date and first_seen and scan_date < first_seen:
            finding.first_seen = self.scan_date
        return existing_vuln

    def _update_first_seen_date(
        self, finding: IntegrationFinding, existing_vuln: Optional[regscale_models.VulnerabilityMapping]
    ) -> None:
        """
        Update the first_seen date based on existing vulnerability mapping or scan date.

        :param IntegrationFinding finding: The integration finding
        :param Optional[regscale_models.VulnerabilityMapping] existing_vuln: The existing vulnerability mapping
        :return: None
        :rtype: None
        """
        if existing_vuln and existing_vuln.firstSeen:
            finding.first_seen = existing_vuln.firstSeen
        elif not finding.first_seen:
            finding.first_seen = self.scan_date

    def _update_date_created(self, finding: IntegrationFinding, issue: Optional[regscale_models.Issue]) -> None:
        """
        Update the date_created based on issue or scan date.

        :param IntegrationFinding finding: The integration finding
        :param Optional[regscale_models.Issue] issue: The existing issue
        :return: None
        :rtype: None
        """
        if issue and issue.dateFirstDetected:
            finding.date_created = issue.dateFirstDetected
        elif not finding.date_created:
            finding.date_created = self.scan_date

    def _update_due_date(self, finding: IntegrationFinding) -> None:
        """
        Update the due_date based on severity and configuration.

        :param IntegrationFinding finding: The integration finding
        :return: None
        :rtype: None
        """
        finding.due_date = issue_due_date(
            severity=finding.severity,
            created_date=finding.date_created or self.scan_date,
            title=self.title,
            config=self.app.config,
        )

    def _update_last_seen_date(self, finding: IntegrationFinding) -> None:
        """
        Update the last_seen date if scan date is after first_seen.

        :param IntegrationFinding finding: The integration finding
        :return: None
        :rtype: None
        """
        scan_date = date_obj(self.scan_date)
        first_seen = date_obj(finding.first_seen)

        if scan_date and first_seen and scan_date >= first_seen:
            finding.last_seen = self.scan_date

    def update_finding_dates(
        self,
        finding: IntegrationFinding,
        existing_vuln: Optional[regscale_models.VulnerabilityMapping],
        issue: Optional[regscale_models.Issue],
    ) -> IntegrationFinding:
        """
        Update the dates of the integration finding based on the scan date and whether the finding is new or existing.

        :param IntegrationFinding finding: The integration finding
        :param Optional[regscale_models.VulnerabilityMapping] existing_vuln: The existing vulnerability mapping
        :param Optional[regscale_models.Issue] issue: The existing issue
        :return: The updated integration finding
        :rtype: IntegrationFinding
        """
        if finding.due_date:
            # If due_date is already set, only update last_seen if needed
            self._update_last_seen_date(finding)
            return finding

        # Update dates for new findings
        self._update_first_seen_date(finding, existing_vuln)
        self._update_date_created(finding, issue)
        self._update_due_date(finding)
        self._update_last_seen_date(finding)

        return finding

    def update_scan(self, scan_history: regscale_models.ScanHistory) -> None:
        """
        Update the scan history object for the current security plan

        :param regscale_models.ScanHistory scan_history: The list of existing scan history objects
        :return: None
        :rtype: None
        """
        if scan_history.scanDate != datetime_str(self.scan_date):
            logger.debug("Updating scan history scan date to %s", datetime_str(self.scan_date))
            scan_history.scanDate = datetime_str(self.scan_date)
            scan_history.save()

    @staticmethod
    def get_date_completed(finding: IntegrationFinding, issue_status: regscale_models.IssueStatus) -> Optional[str]:
        """
        Returns the date when the issue was completed based on the issue status.

        :param IntegrationFinding finding: The finding data
        :param regscale_models.IssueStatus issue_status: The status of the issue
        :return: The date when the issue was completed if the issue status is Closed, else None
        :rtype: Optional[str]
        """
        return finding.date_last_updated if issue_status == regscale_models.IssueStatus.Closed else None

    @staticmethod
    def hash_string(input_string: str) -> str:
        """
        Hashes a string using SHA-256

        :param str input_string: The string to hash
        :return: The hashed string
        :rtype: str
        """
        return hashlib.sha256(input_string.encode()).hexdigest()

    def update_control_implementation_status(
        self,
        issue: regscale_models.Issue,
        open_issue_ids: List[int],
        status: regscale_models.ImplementationStatus,
    ) -> None:
        """
        Updates the control implementation status based on the open issues.

        :param regscale_models.Issue issue: The issue being closed
        :param List[int] open_issue_ids: List of open issue IDs
        :param regscale_models.ImplementationStatus status: The status to set
        :rtype: None
        """
        # Method is deprecated - using update_control_implementation_status_after_close instead
        logger.warning(
            "update_control_implementation_status is deprecated - using update_control_implementation_status_after_close instead"
        )

    def update_regscale_checklists(self, findings: List[IntegrationFinding]) -> int:
        """
        Process checklists from IntegrationFindings, optionally using multiple threads.

        :param List[IntegrationFinding] findings: The findings to process
        :return: The number of checklists processed
        :rtype: int
        """
        logger.info("Updating RegScale checklists...")
        loading_findings = self.finding_progress.add_task(
            f"[#f8b737]Creating and updating checklists from {self.title}."
        )
        checklists_processed = 0

        def process_finding(finding_to_process: IntegrationFinding) -> None:
            """
            Process a single finding and update the progress bar.

            :param IntegrationFinding finding_to_process: The finding to process
            :rtype: None
            """
            nonlocal checklists_processed
            try:
                self.process_checklist(finding_to_process)
                if self.num_findings_to_process and self.finding_progress.tasks[loading_findings].total != float(
                    self.num_findings_to_process
                ):
                    self.finding_progress.update(
                        loading_findings,
                        total=self.num_findings_to_process,
                        description=f"[#f8b737]Creating and updating {self.num_findings_to_process} checklists from {self.title}.",
                    )
                self.finding_progress.advance(loading_findings, 1)
                checklists_processed += 1
            except Exception as exc:
                self.log_error(
                    "An error occurred when processing asset %s for finding %s: %s",
                    finding.asset_identifier,
                    finding_to_process.external_id,
                    exc,
                )

        if get_thread_workers_max() == 1:
            for finding in findings:
                process_finding(finding)
        else:
            with concurrent.futures.ThreadPoolExecutor(max_workers=get_thread_workers_max()) as executor:
                list(executor.map(process_finding, findings))

        return checklists_processed

    def create_control_test_result(
        self,
        finding: IntegrationFinding,
        control_test: regscale_models.ControlTest,
        assessment: regscale_models.Assessment,
        result: regscale_models.ControlTestResultStatus,
    ) -> None:
        """
        Create a control test result.

        :param IntegrationFinding finding: The finding associated with the test result
        :param regscale_models.ControlTest control_test: The control test
        :param regscale_models.Assessment assessment: The assessment
        :param regscale_models.ControlTestResultStatus result: The result of the test
        :rtype: None
        """
        regscale_models.ControlTestResult(
            parentTestId=control_test.id,
            parentAssessmentId=assessment.id,
            uuid=finding.external_id,
            result=result,
            dateAssessed=finding.date_created,
            assessedById=self.assessor_id,
            gaps=finding.gaps,
            observations=finding.observations,
            evidence=finding.evidence,
            identifiedRisk=finding.identified_risk,
            impact=finding.impact,
            recommendationForMitigation=finding.recommendation_for_mitigation,
        ).create()

    @staticmethod
    def _calculate_kev_due_date(kev_data: dict, issue_date_created: str) -> Optional[str]:
        """
        Calculate the due date for a KEV issue based on the difference between
        KEV due date and date added, then add that difference to the issue creation date.

        :param dict kev_data: KEV data containing dueDate and dateAdded
        :param str issue_date_created: The issue creation date string
        :return: Calculated due date as a RegScale formatted string or None
        :rtype: Optional[str]
        """
        from datetime import datetime

        from regscale.core.app.utils.app_utils import convert_datetime_to_regscale_string

        if datetime.strptime(kev_data["dueDate"], "%Y-%m-%d") < datetime.strptime(
            issue_date_created, "%Y-%m-%d %H:%M:%S"
        ):
            # diff kev due date and kev dateAdded
            diff = datetime.strptime(kev_data["dueDate"], "%Y-%m-%d") - datetime.strptime(
                kev_data["dateAdded"], "%Y-%m-%d"
            )
            # add diff to issue.dateCreated
            return convert_datetime_to_regscale_string(
                datetime.strptime(issue_date_created, "%Y-%m-%d %H:%M:%S") + diff
            )
        return None

    def create_vulnerabilities_bulk(
        self,
        findings: List[IntegrationFinding],
        assets: Dict[str, regscale_models.Asset],
        scan_history: regscale_models.ScanHistory,
    ) -> Dict[str, int]:
        """
        Create vulnerabilities in bulk to improve performance and reduce API calls.

        :param List[IntegrationFinding] findings: List of findings to create vulnerabilities for
        :param Dict[str, regscale_models.Asset] assets: Dictionary of assets by identifier
        :param regscale_models.ScanHistory scan_history: The scan history
        :return: Dictionary mapping finding external_id to vulnerability_id
        :rtype: Dict[str, int]
        """
        vulnerabilities_to_create, finding_to_vuln_map = self._prepare_vulnerabilities_for_bulk(
            findings, assets, scan_history
        )

        if not vulnerabilities_to_create:
            logger.warning("No vulnerabilities to create in bulk")
            return {}

        return self._execute_bulk_vulnerability_creation(
            vulnerabilities_to_create, finding_to_vuln_map, findings, assets, scan_history
        )

    def _prepare_vulnerabilities_for_bulk(
        self,
        findings: List[IntegrationFinding],
        assets: Dict[str, regscale_models.Asset],
        scan_history: regscale_models.ScanHistory,
    ) -> tuple[List, Dict]:
        """Prepare vulnerability objects for bulk creation."""
        vulnerabilities_to_create = []
        finding_to_vuln_map = {}

        for finding in findings:
            if not self._is_finding_valid_for_vulnerability(finding):
                continue

            asset = assets.get(finding.asset_identifier)
            if not self._is_asset_valid(asset, finding):
                continue

            vulnerability = self._create_vulnerability_object(finding, asset, scan_history)
            if vulnerability:
                vulnerabilities_to_create.append(vulnerability)
                finding_to_vuln_map[finding.external_id] = vulnerability

        return vulnerabilities_to_create, finding_to_vuln_map

    def _is_finding_valid_for_vulnerability(self, finding: IntegrationFinding) -> bool:
        """Check if a finding is valid for vulnerability creation."""
        if not (finding.plugin_name or finding.cve):
            logger.warning("No Plugin Name or CVE found for finding %s", finding.title)
            return False
        return True

    def _is_asset_valid(self, asset: Optional[regscale_models.Asset], finding: IntegrationFinding) -> bool:
        """Check if an asset is valid for vulnerability creation."""
        if not asset:
            if not getattr(self, "suppress_asset_not_found_errors", False):
                logger.warning(
                    "VulnerabilityMapping Error: Asset not found for identifier %s", finding.asset_identifier
                )
            return False
        return True

    def _create_vulnerability_object(
        self,
        finding: IntegrationFinding,
        asset: regscale_models.Asset,
        scan_history: regscale_models.ScanHistory,
    ) -> Optional[regscale_models.Vulnerability]:
        """Create a vulnerability object from a finding."""
        try:
            return self.create_vulnerability_from_finding(finding, asset, scan_history)
        except Exception as e:
            logger.error(f"Failed to prepare vulnerability for finding {finding.external_id}: {e}")
            return None

    def _execute_bulk_vulnerability_creation(
        self,
        vulnerabilities_to_create: List,
        finding_to_vuln_map: Dict,
        findings: List[IntegrationFinding],
        assets: Dict[str, regscale_models.Asset],
        scan_history: regscale_models.ScanHistory,
    ) -> Dict[str, int]:
        """Execute bulk vulnerability creation with fallback to individual creation."""
        try:
            created_vulnerabilities = regscale_models.Vulnerability.batch_create(
                vulnerabilities_to_create, progress_context=self.finding_progress
            )

            result = self._map_vulnerabilities_to_findings(
                created_vulnerabilities, vulnerabilities_to_create, finding_to_vuln_map
            )

            logger.info(f"Successfully created {len(created_vulnerabilities)} vulnerabilities in bulk")
            return result

        except Exception as e:
            logger.error(f"Bulk vulnerability creation failed: {e}")
            logger.info("Falling back to individual vulnerability creation...")
            return self._create_vulnerabilities_individual(findings, assets, scan_history)

    def _map_vulnerabilities_to_findings(
        self,
        created_vulnerabilities: List,
        vulnerabilities_to_create: List,
        finding_to_vuln_map: Dict,
    ) -> Dict[str, int]:
        """Map created vulnerabilities back to findings."""
        result = {}
        for i, created_vuln in enumerate(created_vulnerabilities):
            if i < len(vulnerabilities_to_create):
                original_vuln = vulnerabilities_to_create[i]
                # Find the finding that corresponds to this vulnerability
                for finding_id, vuln in finding_to_vuln_map.items():
                    if vuln == original_vuln:
                        result[finding_id] = created_vuln.id
                        break
        return result

    def _create_vulnerabilities_individual(
        self,
        findings: List[IntegrationFinding],
        assets: Dict[str, regscale_models.Asset],
        scan_history: regscale_models.ScanHistory,
    ) -> Dict[str, int]:
        """
        Create vulnerabilities individually as fallback.

        :param List[IntegrationFinding] findings: List of findings
        :param Dict[str, regscale_models.Asset] assets: Dictionary of assets
        :param regscale_models.ScanHistory scan_history: The scan history
        :return: Dictionary mapping finding external_id to vulnerability_id
        :rtype: Dict[str, int]
        """
        result = {}
        for finding in findings:
            vulnerability_id = self.handle_vulnerability(finding, assets.get(finding.asset_identifier), scan_history)
            if vulnerability_id:
                result[finding.external_id] = vulnerability_id
        return result
