#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wiz Policy Compliance Integration for RegScale CLI."""

import json
import logging
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Iterator, Any

from regscale.core.app.application import Application
from regscale.core.app.utils.app_utils import error_and_exit, check_license, get_current_datetime
from regscale.integrations.commercial.wizv2.async_client import run_async_queries
from regscale.integrations.commercial.wizv2.constants import (
    WizVulnerabilityType,
    WIZ_POLICY_QUERY,
    WIZ_FRAMEWORK_QUERY,
    FRAMEWORK_MAPPINGS,
    FRAMEWORK_SHORTCUTS,
    FRAMEWORK_CATEGORIES,
)
from regscale.integrations.commercial.wizv2.data_fetcher import PolicyAssessmentFetcher
from regscale.integrations.commercial.wizv2.finding_processor import (
    FindingConsolidator,
    FindingToIssueProcessor,
)
from regscale.integrations.commercial.wizv2.policy_compliance_helpers import (
    ControlImplementationCache,
    AssetConsolidator,
    IssueFieldSetter,
    ControlAssessmentProcessor,
)
from regscale.integrations.commercial.wizv2.wiz_auth import wiz_authenticate
from regscale.integrations.compliance_integration import ComplianceIntegration, ComplianceItem
from regscale.integrations.scanner_integration import (
    ScannerIntegrationType,
    IntegrationAsset,
    IntegrationFinding,
    issue_due_date,
)
from regscale.integrations.variables import ScannerVariables
from regscale.models import regscale_models

logger = logging.getLogger("regscale")


# Constants for file operations
JSON_FILE_EXT = ".json"
JSONL_FILE_EXT = ".jsonl"
MAX_DISPLAY_ASSETS = 10  # Maximum number of asset names to display in descriptions
CACHE_CLEANUP_KEEP_COUNT = 5  # Number of recent cache files to keep during cleanup
WIZ_URL = "https://api.wiz.io/graphql"

# Safer, linear-time regex for control-id normalization.
# Examples supported: 'AC-4', 'AC-4(2)', 'AC-4 (2)', 'AC-4-2', 'AC-4 2'
# This avoids ambiguous nested optional whitespace with alternation that can
# trigger excessive backtracking. Each branch starts with a distinct token
# ('(', '-' or whitespace), so the engine proceeds deterministically.
SAFE_CONTROL_ID_RE = re.compile(  # NOSONAR
    r"^([A-Za-z]{2}-\d+)(?:\s*\(\s*(\d+)\s*\)|-\s*(\d+)|\s+(\d+))?$",  # NOSONAR
    re.IGNORECASE,  # NOSONAR
)  # NOSONAR


class WizComplianceItem(ComplianceItem):
    """Wiz implementation of ComplianceItem."""

    def __init__(self, raw_data: Dict[str, Any], integration: Optional["WizPolicyComplianceIntegration"] = None):
        """
        Initialize WizComplianceItem from raw GraphQL response.

        :param Dict[str, Any] raw_data: Raw policy assessment data from Wiz
        :param Optional['WizPolicyComplianceIntegration'] integration: Integration instance for framework mapping
        """
        self.id = raw_data.get("id", "")
        self.result = raw_data.get("result", "")
        self.policy = raw_data.get("policy", {})
        self.resource = raw_data.get("resource", {})
        self.output = raw_data.get("output", {})
        self._integration = integration

    def _get_filtered_subcategories(self) -> List[Dict[str, Any]]:
        """
        Return only subcategories that belong to the selected framework.

        If no integration or framework filter is available, return all.

        :return: List of filtered security subcategories
        :rtype: List[Dict[str, Any]]
        """
        subcategories = self.policy.get("securitySubCategories", []) if self.policy else []
        if not subcategories or not self._integration or not getattr(self._integration, "framework_id", None):
            return subcategories

        target_framework_id = self._integration.framework_id
        filtered = [
            sc for sc in subcategories if sc.get("category", {}).get("framework", {}).get("id") == target_framework_id
        ]
        # Return filtered results - if empty, the control_id will be empty (framework filtering working as intended)
        return filtered

    @property
    def resource_id(self) -> str:
        """Unique identifier for the resource being assessed."""
        return self.resource.get("id", "")

    @property
    def resource_name(self) -> str:
        """Human-readable name of the resource."""
        return self.resource.get("name", "")

    @property
    def control_id(self) -> str:
        """Control identifier (e.g., AC-3, SI-2)."""
        if not self.policy:
            return ""

        subcategories = self._get_filtered_subcategories()
        if subcategories:
            return subcategories[0].get("externalId", "")
        return ""

    @property
    def compliance_result(self) -> str:
        """Result of compliance check (PASS, FAIL, etc)."""
        return self.result

    @property
    def severity(self) -> Optional[str]:
        """Severity level of the compliance violation (if failed)."""
        return self.policy.get("severity")

    @property
    def description(self) -> str:
        """Description of the compliance check."""
        desc = self.policy.get("description") or self.policy.get("ruleDescription", "")
        if not desc:
            desc = f"Compliance check for {self.policy.get('name', 'unknown policy')}"
        return desc

    @property
    def framework(self) -> str:
        """Compliance framework (e.g., NIST800-53R5, CSF)."""
        if not self.policy:
            return ""

        subcategories = self._get_filtered_subcategories()
        if subcategories:
            category = subcategories[0].get("category", {})
            framework = category.get("framework", {})
            framework_id = framework.get("id", "")

            # Prefer integration mapping using the actual framework id from the item
            if self._integration and framework_id:
                return self._integration.get_framework_name(framework_id)

            return framework.get("name", "")
        return ""

    @property
    def framework_id(self) -> Optional[str]:
        """Extract framework ID."""
        if not self.policy:
            return None

        subcategories = self._get_filtered_subcategories()
        if subcategories:
            category = subcategories[0].get("category", {})
            framework = category.get("framework", {})
            return framework.get("id")
        return None

    @property
    def is_pass(self) -> bool:
        """Check if assessment result is PASS."""
        return self.result == "PASS"

    @property
    def is_fail(self) -> bool:
        """Check if assessment result is FAIL."""
        return self.result == "FAIL"


class WizPolicyComplianceIntegration(ComplianceIntegration):
    """
    Wiz Policy Compliance Integration for syncing policy assessments from Wiz to RegScale.

    This integration fetches policy assessment data from Wiz, processes the results,
    and creates control assessments in RegScale based on compliance status.
    """

    title = "Wiz Policy Compliance Integration"
    type = ScannerIntegrationType.CONTROL_TEST
    # Use wizId field for asset identification (matches other Wiz integrations)
    asset_identifier_field = "wizId"
    issue_identifier_field = "wizId"

    # Do not create assets - they come from separate inventory import
    options_map_assets_to_components: bool = False
    # Do not create vulnerabilities from compliance policy results
    create_vulnerabilities: bool = False
    # Do not create scan history - this is compliance report ingest, not a vulnerability scan
    enable_scan_history: bool = False

    # Control whether JSONL control-centric export is written alongside JSON
    write_jsonl_output: bool = False

    def __init__(
        self,
        plan_id: int,
        wiz_project_id: str,
        client_id: str,
        client_secret: str,
        framework_id: str = "wf-id-4",  # Default to NIST SP 800-53 Revision 5
        catalog_id: Optional[int] = None,
        tenant_id: int = 1,
        create_issues: bool = True,
        update_control_status: bool = True,
        create_poams: bool = False,
        regscale_module: Optional[str] = "securityplans",
        **kwargs,
    ):
        """
        Initialize the Wiz Policy Compliance Integration.

        :param int plan_id: RegScale Security Plan ID
        :param str wiz_project_id: Wiz Project ID to query
        :param str client_id: Wiz API client ID
        :param str client_secret: Wiz API client secret
        :param str framework_id: Wiz framework ID to filter by (default: wf-id-4)
        :param Optional[int] catalog_id: RegScale catalog ID
        :param int tenant_id: RegScale tenant ID
        :param bool create_issues: Whether to create issues for failed compliance
        :param bool update_control_status: Whether to update control implementation status
        :param bool create_poams: Whether to mark issues as POAMs
        :param Optional[str] regscale_module: RegScale module string (overrides default parent_module)
        """
        super().__init__(
            plan_id=plan_id,
            parent_module=regscale_module,
            catalog_id=catalog_id,
            framework=self._map_framework_id_to_name(framework_id),
            create_issues=create_issues,
            update_control_status=update_control_status,
            create_poams=create_poams,
            tenant_id=tenant_id,
            **kwargs,
        )

        # Override parent_module if regscale_module is provided
        if regscale_module:
            self.parent_module = regscale_module

        self.wiz_project_id = wiz_project_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.framework_id = framework_id
        self.wiz_endpoint = ""
        self.access_token = ""
        self.framework_mapping: Dict[str, str] = {}
        self.framework_cache_file = os.path.join("artifacts", "wiz", "framework_mapping.json")
        self.raw_policy_assessments: List[Dict[str, Any]] = []

        # Caching configuration for policy assessments
        # Default: disabled for tests; CLI enables via --cache-duration
        self.cache_duration_minutes: int = int(kwargs.get("cache_duration_minutes", 0))
        self.force_refresh: bool = bool(kwargs.get("force_refresh", False))
        self.policy_cache_dir: str = os.path.join("artifacts", "wiz")
        self.policy_cache_file: str = os.path.join(
            self.policy_cache_dir, f"policy_assessments_{wiz_project_id}_{framework_id}.json"
        )

        # Initialize helper classes for cleaner code organization
        self._control_cache = ControlImplementationCache()
        self._asset_consolidator = AssetConsolidator()
        self._issue_field_setter = IssueFieldSetter(self._control_cache, plan_id, regscale_module or "securityplans")
        self._finding_consolidator = FindingConsolidator(self)
        self._finding_processor = FindingToIssueProcessor(self)
        self._assessment_processor = ControlAssessmentProcessor(
            plan_id,
            regscale_module or "securityplans",
            self.scan_date,
            self.title,
            self._map_framework_id_to_name(framework_id),
        )

    def fetch_compliance_data(self) -> List[Any]:
        """
        Fetch compliance data from Wiz GraphQL API and filter to framework-specific
        items for existing assets only.

        :return: List of filtered raw compliance data
        :rtype: List[Any]
        """
        # Authenticate if not already done
        if not self.access_token:
            self.authenticate_wiz()

        # Load existing assets early for filtering
        self._load_regscale_assets()

        # Use the data fetcher for cleaner code
        fetcher = PolicyAssessmentFetcher(
            wiz_endpoint=self.wiz_endpoint or WIZ_URL,
            access_token=self.access_token,
            wiz_project_id=self.wiz_project_id,
            framework_id=self.framework_id,
            cache_duration_minutes=self.cache_duration_minutes,
        )

        all_policy_assessments = fetcher.fetch_policy_assessments()

        if not all_policy_assessments:
            logger.info("No policy assessments fetched from Wiz")
            self.raw_policy_assessments = []
            return []

        # Filter to only items with existing assets in RegScale
        filtered_assessments = self._filter_assessments_to_existing_assets(all_policy_assessments)

        self.raw_policy_assessments = filtered_assessments
        return filtered_assessments

    def _filter_assessments_to_existing_assets(self, assessments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter assessments to only include items with existing assets and control IDs.

        :param assessments: List of raw assessments from Wiz
        :return: Filtered list of assessments
        """
        assets_exist = getattr(self, "_regscale_assets_by_wiz_id", {})
        filtered_assessments = []
        skipped_no_control = 0
        skipped_no_asset = 0

        for assessment in assessments:
            # Convert to compliance item to check framework and asset existence
            temp_item = WizComplianceItem(assessment, self)

            # Skip if no control ID (not in selected framework)
            if not temp_item.control_id:
                skipped_no_control += 1
                continue

            # Skip if asset doesn't exist in RegScale (use cached lookup)
            if temp_item.resource_id not in assets_exist:
                skipped_no_asset += 1
                continue

            filtered_assessments.append(assessment)
        logger.debug(f"Skipped {skipped_no_control} assessments with no control ID for framework.")
        logger.debug(f"Skipped {skipped_no_asset} assessments with no existing asset in RegScale.")
        return filtered_assessments

    def create_compliance_item(self, raw_data: Any) -> ComplianceItem:
        """
        Create a ComplianceItem from raw compliance data.

        :param Any raw_data: Raw compliance data from Wiz
        :return: ComplianceItem instance
        :rtype: ComplianceItem
        """
        return WizComplianceItem(raw_data, self)

    def _map_resource_type_to_asset_type(self, compliance_item: ComplianceItem) -> str:
        """
        Map Wiz resource type to RegScale asset type.

        :param ComplianceItem compliance_item: Compliance item
        :return: Asset type string
        :rtype: str
        """
        if isinstance(compliance_item, WizComplianceItem):
            resource_type = compliance_item.resource.get("type", "").upper()

            # Minimal mapping expected by tests; default to generic type name
            name_mapping = {
                "VIRTUAL_MACHINE": "Virtual Machine",
                "CONTAINER": "Container",
                "DATABASE": "Database",
                "BUCKET": "Storage",
            }
            if resource_type in name_mapping:
                return name_mapping[resource_type]

        return "Cloud Resource"

    def _get_component_name_from_source_type(self, compliance_item: WizComplianceItem) -> str:
        """
        Build a component name from the original Wiz resource type (source type).

        Example: "STORAGE_ACCOUNT" -> "Storage Account"

        :param WizComplianceItem compliance_item: Compliance item containing resource information
        :return: Human-readable component name derived from resource type
        :rtype: str
        """
        raw_type = (compliance_item.resource or {}).get("type", "Unknown Resource")
        return raw_type.replace("_", " ").title()

    def fetch_assets(self, *args, **kwargs) -> Iterator[IntegrationAsset]:
        """
        No assets are created in policy compliance integration.
        Assets come from separate Wiz inventory import.
        """
        return iter([])

    def fetch_findings(self, *args, **kwargs) -> Iterator[IntegrationFinding]:
        """
        Create consolidated findings grouped by control, with all affected resources under each control.

        This approach groups by control first, then collects all resources that fail that control.
        This results in one finding per control with multiple resources, making consolidation much easier.
        """
        if not self.failed_compliance_items:
            return

        # Use the finding consolidator for cleaner code
        yield from self._finding_consolidator.create_consolidated_findings(self.failed_compliance_items)

    def _get_all_control_ids_for_compliance_item(self, compliance_item: WizComplianceItem) -> List[str]:
        """
        Get ALL control IDs that a compliance item maps to.

        Wiz policies can map to multiple controls (e.g., one policy failure might affect
        AC-4(2), AC-4(4), and SC-28(1) controls). This method returns all of them.

        :param WizComplianceItem compliance_item: Compliance item to extract control IDs from
        :return: List of control IDs this policy maps to
        :rtype: List[str]
        """
        if not compliance_item.policy:
            return []

        subcategories = compliance_item._get_filtered_subcategories()
        if not subcategories:
            return []

        # Extract control IDs and deduplicate in one pass
        unique_control_ids = []
        seen = set()

        for subcat in subcategories:
            external_id = subcat.get("externalId", "")
            if external_id and external_id not in seen:
                seen.add(external_id)
                unique_control_ids.append(external_id)

        return unique_control_ids

    def _group_compliance_items_by_control(self) -> Dict[str, Dict[str, WizComplianceItem]]:
        """
        Group failed compliance items by control ID.

        :return: Dictionary mapping control IDs to resource dictionaries
        :rtype: Dict[str, Dict[str, WizComplianceItem]]
        """
        control_to_resources = {}  # {control_id: {resource_id: compliance_item}}

        for compliance_item in self.failed_compliance_items:
            if not isinstance(compliance_item, WizComplianceItem):
                continue

            asset_id = (compliance_item.resource_id or "").lower()
            if not asset_id:
                continue

            # Get ALL control IDs that this policy assessment maps to
            all_control_ids = self._get_all_control_ids_for_compliance_item(compliance_item)
            if not all_control_ids:
                continue

            # Add this resource to each control it fails
            for control_id in all_control_ids:
                control = control_id.upper()

                if control not in control_to_resources:
                    control_to_resources[control] = {}

                # Use the first compliance item we find for this resource-control pair
                # (there might be duplicates from multiple policy assessments)
                if asset_id not in control_to_resources[control]:
                    control_to_resources[control][asset_id] = compliance_item

        return control_to_resources

    def _create_consolidated_findings(
        self, control_to_resources: Dict[str, Dict[str, WizComplianceItem]]
    ) -> Iterator[IntegrationFinding]:
        """
        Create consolidated findings from grouped control-resource mappings.

        :param Dict[str, Dict[str, WizComplianceItem]] control_to_resources: Control groupings
        :yield: Consolidated findings
        :rtype: Iterator[IntegrationFinding]
        """
        for control_id, resources in control_to_resources.items():

            # Use the first compliance item as the base for this control's finding
            base_compliance_item = next(iter(resources.values()))

            # Create a consolidated finding for this control
            finding = self._create_consolidated_finding_for_control(
                control_id=control_id, compliance_item=base_compliance_item, affected_resources=list(resources.keys())
            )

            if finding:
                yield finding

    def _create_consolidated_finding_for_control(
        self, control_id: str, compliance_item: WizComplianceItem, affected_resources: List[str]
    ) -> Optional[IntegrationFinding]:
        """
        Create a consolidated finding for a control with all affected resources.

        :param str control_id: The control ID (e.g., 'AC-4(2)')
        :param WizComplianceItem compliance_item: Base compliance item for this control
        :param List[str] affected_resources: List of Wiz resource IDs that fail this control
        :return: Consolidated finding with all affected resources
        :rtype: Optional[IntegrationFinding]
        """
        # Filter to only resources that exist as assets in RegScale
        asset_mappings = self._build_asset_mappings(affected_resources)

        if not asset_mappings:
            return None

        # Create the base finding using the control-specific approach
        finding = self._create_finding_for_specific_control(compliance_item, control_id)
        if not finding:
            return None

        # Update the asset identifier and description with consolidated info
        self._update_finding_with_consolidated_assets(finding, asset_mappings)
        return finding

    def _build_asset_mappings(self, resource_ids: List[str]) -> Dict[str, Dict[str, str]]:
        """
        Build asset mappings for resources that exist in RegScale.

        :param List[str] resource_ids: List of Wiz resource IDs
        :return: Mapping of resource IDs to asset information
        :rtype: Dict[str, Dict[str, str]]
        """
        asset_mappings = {}

        for resource_id in resource_ids:
            if self._asset_exists_in_regscale(resource_id):
                asset = self.get_asset_by_identifier(resource_id)
                if asset and asset.name:
                    asset_mappings[resource_id] = {"name": asset.name, "wiz_id": resource_id}
                else:
                    # Fallback to resource ID if asset name not found
                    asset_mappings[resource_id] = {"name": resource_id, "wiz_id": resource_id}

        return asset_mappings

    def _update_finding_with_consolidated_assets(
        self, finding: IntegrationFinding, asset_mappings: Dict[str, Dict[str, str]]
    ) -> None:
        """
        Update a finding with consolidated asset information.

        :param IntegrationFinding finding: Finding to update
        :param Dict[str, Dict[str, str]] asset_mappings: Asset mapping information
        :return: None
        :rtype: None
        """
        # Update the asset identifier to include all asset names (clean format for POAMs)
        consolidated_asset_identifier = self._create_consolidated_asset_identifier(asset_mappings)
        finding.asset_identifier = consolidated_asset_identifier

        # Update finding description to indicate multiple resources
        asset_names = [info["name"] for info in asset_mappings.values()]
        if len(asset_names) > 1:
            finding.description = f"{finding.description}\n\nThis control failure affects {len(asset_names)} assets: {', '.join(asset_names[:MAX_DISPLAY_ASSETS])}"
            if len(asset_names) > MAX_DISPLAY_ASSETS:
                finding.description += f" (and {len(asset_names) - MAX_DISPLAY_ASSETS} more)"

    def _create_finding_for_specific_control(
        self, compliance_item: WizComplianceItem, control_id: str
    ) -> Optional[IntegrationFinding]:
        """
        Create a finding for a specific control ID from a compliance item.

        This is similar to create_finding_from_compliance_item but ensures the finding
        uses the specific control ID rather than just the first one.

        :param WizComplianceItem compliance_item: Source compliance item
        :param str control_id: Specific control ID to create finding for
        :return: Integration finding for this specific control
        :rtype: Optional[IntegrationFinding]
        """
        try:
            control_labels = [control_id] if control_id else []
            severity = self._map_severity(compliance_item.severity)
            policy_name = self._get_policy_name(compliance_item)
            title = f"{policy_name} ({control_id})" if control_id else policy_name
            description = self._compose_description(policy_name, compliance_item)

            finding = self._build_finding(
                control_labels=control_labels,
                title=title,
                description=description,
                severity=severity,
                compliance_item=compliance_item,
            )

            # Set the specific control ID for this finding
            finding.rule_id = control_id
            finding.affected_controls = self._normalize_control_id_string(control_id)

            # Ensure unique external_id for each control to prevent unwanted updates
            finding.external_id = f"wiz-policy-control-{control_id.upper()}-{self.framework_id}"

            self._set_assessment_id_if_available(finding, compliance_item)
            return finding

        except Exception as e:
            logger.error(f"Error creating finding for control {control_id}: {e}")
            return None

    def _asset_exists_in_regscale(self, resource_id: str) -> bool:
        """
        Check if an asset with the given Wiz resource ID exists in RegScale.

        :param str resource_id: Wiz resource ID to check (stored in RegScale asset wizId field)
        :return: True if asset exists, False otherwise
        :rtype: bool
        """
        if not resource_id:
            return False

        try:
            # Check if we have a cached lookup of existing assets
            if not hasattr(self, "_regscale_assets_by_wiz_id"):
                self._load_regscale_assets()

            return resource_id in self._regscale_assets_by_wiz_id
        except Exception:
            return False

    def _load_regscale_assets(self) -> None:
        """
        Load all existing assets from RegScale into a Wiz ID-based lookup cache.
        Wiz resource IDs are stored in the RegScale asset wizId field.
        """
        try:
            logger.info("Loading existing assets from RegScale for asset existence checks...")
            # Get all assets for the current plan
            existing_assets = regscale_models.Asset.get_all_by_parent(
                parent_id=self.plan_id,
                parent_module=self.parent_module,
            )

            # Create Wiz ID-based lookup cache (Wiz resource ID -> RegScale asset)
            self._regscale_assets_by_wiz_id = {asset.wizId: asset for asset in existing_assets if asset.wizId}
            logger.info(f"Loaded {len(self._regscale_assets_by_wiz_id)} existing assets for lookup")

        except Exception as e:
            logger.error(f"Error loading RegScale assets: {e}")
            # Initialize empty cache to avoid repeated failures
            self._regscale_assets_by_wiz_id = {}

    def _map_framework_id_to_name(self, framework_id: str) -> str:
        """
        Map framework ID to framework name.

        :param str framework_id: Framework ID to map
        :return: Human-readable framework name
        :rtype: str
        """
        # Default mappings - will be enhanced with cached data
        default_mappings = {
            "wf-id-4": "NIST800-53R5",
            "wf-id-48": "NIST800-53R4",
            "wf-id-5": "FedRAMP",
        }

        return default_mappings.get(framework_id, framework_id)

    def create_finding_from_compliance_item(self, compliance_item: ComplianceItem) -> Optional[IntegrationFinding]:
        """
        Create an IntegrationFinding from a failed compliance item with proper asset/issue matching.

        :param ComplianceItem compliance_item: The compliance item
        :return: IntegrationFinding or None
        :rtype: Optional[IntegrationFinding]
        """
        if not isinstance(compliance_item, WizComplianceItem):
            return super().create_finding_from_compliance_item(compliance_item)

        try:
            control_labels = self._get_control_labels(compliance_item)
            severity = self._map_severity(compliance_item.severity)
            policy_name = self._get_policy_name(compliance_item)
            title = self._compose_title(policy_name, compliance_item)
            description = self._compose_description(policy_name, compliance_item)
            finding = self._build_finding(
                control_labels=control_labels,
                title=title,
                description=description,
                severity=severity,
                compliance_item=compliance_item,
            )
            self._set_affected_controls(finding, compliance_item)
            self._set_assessment_id_if_available(finding, compliance_item)
            return finding
        except Exception as e:
            logger.error(f"Error creating finding from Wiz compliance item: {e}")
            return None

    # ---------- Private helpers (low-complexity building blocks) ----------

    @staticmethod
    def _get_control_labels(item: WizComplianceItem) -> List[str]:
        """
        Extract control labels from a Wiz compliance item.

        :param WizComplianceItem item: Compliance item to extract labels from
        :return: List of control labels
        :rtype: List[str]
        """
        return [item.control_id] if item.control_id else []

    @staticmethod
    def _get_policy_name(item: WizComplianceItem) -> str:
        """
        Extract policy name from a Wiz compliance item.

        :param WizComplianceItem item: Compliance item to extract policy name from
        :return: Policy name or 'Unknown Policy' if not found
        :rtype: str
        """
        return (item.policy.get("name") or "Unknown Policy").strip()

    @staticmethod
    def _compose_title(policy_name: str, item: WizComplianceItem) -> str:
        """
        Compose a finding title from policy name and control information.

        :param str policy_name: Name of the policy
        :param WizComplianceItem item: Compliance item with control information
        :return: Formatted title for the finding
        :rtype: str
        """
        return f"{policy_name} ({item.control_id})" if item.control_id else policy_name

    def _compose_description(self, policy_name: str, item: WizComplianceItem) -> str:
        """
        Compose a detailed description for a compliance finding.

        :param str policy_name: Name of the policy that failed
        :param WizComplianceItem item: Compliance item with resource and policy details
        :return: Formatted markdown description
        :rtype: str
        """
        parts: List[str] = [
            f"Policy compliance failure detected by Wiz for resource '{item.resource_name}'.",
            "",
            f"**Policy:** {policy_name}",
            f"**Resource:** {item.resource_name} ({item.resource.get('type', 'Unknown')})",
            f"**Control:** {item.control_id}",
            f"**Framework:** {item.framework}",
            f"**Result:** {item.result}",
        ]

        # Policy/Remediation details
        policy_desc = item.policy.get("description") or item.policy.get("ruleDescription")
        if policy_desc:
            parts.extend(["", "**Policy Description:**", policy_desc])

        remediation = item.policy.get("remediationInstructions")
        if remediation:
            parts.extend(["", "**Remediation Instructions:**", remediation])

        # Location details
        if item.resource.get("region"):
            parts.append(f"**Region:** {item.resource['region']}")
        if item.resource.get("subscription"):
            sub = item.resource["subscription"]
            parts.append(
                f"**Cloud Provider:** {sub.get('cloudProvider', 'Unknown')} "
                f"(Subscription: {sub.get('name', 'Unknown')})"
            )

        return "\n".join(parts)

    def _build_finding(
        self,
        *,
        control_labels: List[str],
        title: str,
        description: str,
        severity: regscale_models.IssueSeverity,
        compliance_item: WizComplianceItem,
    ) -> IntegrationFinding:
        """
        Build an IntegrationFinding from compliance item components.

        :param List[str] control_labels: List of control labels
        :param str title: Finding title
        :param str description: Finding description
        :param regscale_models.IssueSeverity severity: Finding severity
        :param WizComplianceItem compliance_item: Source compliance item
        :return: Constructed integration finding
        :rtype: IntegrationFinding
        """
        stable_rule = compliance_item.control_id or ""
        return IntegrationFinding(
            control_labels=control_labels,
            title=f"Policy Compliance Failure: {title}" if compliance_item.is_fail else title,
            category="Policy Compliance",
            plugin_name=f"{self.title}",
            severity=severity,
            description=description,
            status=regscale_models.IssueStatus.Open,
            priority=self._map_severity_to_priority(severity),
            plugin_id=f"policy-control:{self.framework_id}:{stable_rule}",
            external_id=(
                f"wiz-policy-{compliance_item.id}" if compliance_item.id else f"wiz-policy-control-{stable_rule}"
            ),
            identification="Security Control Assessment",
            first_seen=self.scan_date,
            last_seen=self.scan_date,
            scan_date=self.scan_date,
            asset_identifier=self._get_regscale_asset_identifier(compliance_item),
            vulnerability_type="Policy Compliance Violation",
            rule_id=compliance_item.control_id,
            baseline=compliance_item.framework,
            remediation=compliance_item.policy.get("remediationInstructions") or "",
        )

    def _set_affected_controls(self, finding: IntegrationFinding, item: WizComplianceItem) -> None:
        """
        Set the affected controls field on a finding from a compliance item.

        :param IntegrationFinding finding: Finding to update
        :param WizComplianceItem item: Compliance item with control information
        :return: None
        :rtype: None
        """
        if item.control_id:
            finding.affected_controls = self._normalize_control_id_string(item.control_id)

    def _set_assessment_id_if_available(self, finding: IntegrationFinding, item: WizComplianceItem) -> None:
        """
        Set the assessment ID on a finding if available from cached mappings.

        :param IntegrationFinding finding: Finding to update with assessment ID
        :param WizComplianceItem item: Compliance item with control information
        :return: None
        :rtype: None
        """
        try:
            ctrl_norm = self._normalize_control_id_string(item.control_id)
            if ctrl_norm and hasattr(self, "_impl_id_by_control"):
                impl_id = self._impl_id_by_control.get(ctrl_norm)
                if impl_id and hasattr(self, "_assessment_by_impl_today"):
                    assess = self._assessment_by_impl_today.get(impl_id)
                    if assess:
                        finding.assessment_id = assess.id
        except Exception:
            pass

    def create_asset_from_compliance_item(self, compliance_item: ComplianceItem) -> Optional[IntegrationAsset]:
        """
        Create an IntegrationAsset from a Wiz compliance item with enhanced metadata.

        :param ComplianceItem compliance_item: The compliance item
        :return: IntegrationAsset or None
        :rtype: Optional[IntegrationAsset]
        """
        if not isinstance(compliance_item, WizComplianceItem):
            return super().create_asset_from_compliance_item(compliance_item)

        try:
            resource = compliance_item.resource
            asset_type = self._map_resource_type_to_asset_type(compliance_item)

            # Build asset description with cloud metadata
            description_parts = [
                "Cloud resource from Wiz compliance scan",
                f"Type: {resource.get('type', 'Unknown')}",
            ]

            if resource.get("region"):
                description_parts.append(f"Region: {resource['region']}")

            if resource.get("subscription"):
                sub = resource["subscription"]
                description_parts.append(
                    f"Cloud Provider: {sub.get('cloudProvider', 'Unknown')} "
                    f"(Subscription: {sub.get('name', 'Unknown')})"
                )

            # Add tags if available
            tags = resource.get("tags", [])
            if tags:
                tag_strings = [f"{tag.get('key')}:{tag.get('value')}" for tag in tags if tag.get("key")]
                if tag_strings:
                    description_parts.append(f"Tags: {', '.join(tag_strings)}")

            # Get user ID directly from application config
            app = Application()
            config = app.config
            user_id = config.get("userId")

            asset = IntegrationAsset(
                name=compliance_item.resource_name,
                identifier=compliance_item.resource_name,  # Use name only without UUID
                external_id=compliance_item.resource_id,
                other_tracking_number=compliance_item.resource_id,  # For deduplication
                asset_type=asset_type,
                asset_category=regscale_models.AssetCategory.Hardware,
                description="\n".join(description_parts),
                parent_id=self.plan_id,
                parent_module=self.parent_module,
                status=regscale_models.AssetStatus.Active,
                date_last_updated=self.scan_date,
                notes=self._create_asset_notes(compliance_item),
                # Set asset owner ID from config
                asset_owner_id=user_id,
                # Enable component mapping flow downstream
                component_names=[],
            )

            return asset

        except Exception as e:
            logger.error(f"Error creating asset from Wiz compliance item: {e}")
            return None

    def create_scan_history(self):  # type: ignore[override]
        """No scan history created for compliance report ingest."""
        return None

    def _create_asset_notes(self, compliance_item: WizComplianceItem) -> str:
        """
        Create detailed notes for asset with compliance context.

        :param WizComplianceItem compliance_item: Compliance item with resource details
        :return: Formatted asset notes in markdown
        :rtype: str
        """
        resource = compliance_item.resource
        notes_parts = [
            "# Wiz Asset Details",
            f"**Resource ID:** {compliance_item.resource_id}",
            f"**Resource Type:** {resource.get('type', 'Unknown')}",
        ]

        # Add subscription details
        if resource.get("subscription"):
            sub = resource["subscription"]
            notes_parts.extend(
                [
                    "",
                    "## Cloud Provider Details",
                    f"**Provider:** {sub.get('cloudProvider', 'Unknown')}",
                    f"**Subscription Name:** {sub.get('name', 'Unknown')}",
                    f"**Subscription ID:** {sub.get('externalId', 'Unknown')}",
                ]
            )

        # Add compliance summary
        total_items = len(self.asset_compliance_map.get(compliance_item.resource_id, []))
        failed_items = len(
            [
                item
                for item in self.asset_compliance_map.get(compliance_item.resource_id, [])
                if item.compliance_result in self.FAIL_STATUSES
            ]
        )

        if total_items > 0:
            notes_parts.extend(
                [
                    "",
                    "## Compliance Summary",
                    f"**Total Assessments:** {total_items}",
                    f"**Failed Assessments:** {failed_items}",
                    f"**Compliance Rate:** {((total_items - failed_items) / total_items * 100):.1f}%",
                ]
            )

        return "\n".join(notes_parts)

    def authenticate_wiz(self) -> str:
        """
        Authenticate with Wiz and return access token.

        :return: Wiz access token
        :rtype: str
        """
        logger.info("Authenticating with Wiz...")
        try:
            token = wiz_authenticate(client_id=self.client_id, client_secret=self.client_secret)
            if not token:
                error_and_exit("Failed to authenticate with Wiz")

            # Get Wiz endpoint from config
            app = check_license()
            config = app.config
            self.wiz_endpoint = config.get("wizUrl", "")
            if not self.wiz_endpoint:
                error_and_exit("No Wiz URL found in configuration")

            self.access_token = token
            logger.info("Successfully authenticated with Wiz")
            return token

        except Exception as e:
            logger.error(f"Wiz authentication failed: {str(e)}")
            error_and_exit(f"Wiz authentication failed: {str(e)}")

    def _fetch_policy_assessments_from_wiz(self) -> List[Dict[str, Any]]:
        """
        Fetch policy assessments from Wiz GraphQL API.

        :return: List of raw policy assessment data
        :rtype: List[Dict[str, Any]]
        """
        logger.info("Fetching policy assessments from Wiz...")

        # Authenticate if not already done
        if not self.access_token:
            self.authenticate_wiz()

        headers = self._build_wiz_headers()
        session = self._prepare_wiz_requests_session()

        # Try cache first unless forced refresh
        cached_nodes = self._load_assessments_from_cache()
        if cached_nodes is not None:
            logger.info("Using cached Wiz policy assessments")
            return cached_nodes

        # Only include variables supported by the query (avoid validation errors)
        page_size = 100
        base_variables = {"first": page_size}

        # Try multiple filter key variants to avoid schema differences across tenants
        filter_variants = [
            {"project": [self.wiz_project_id]},
            {"projectId": [self.wiz_project_id]},
            {"projects": [self.wiz_project_id]},
            {},  # Empty filterBy
            None,  # Omit filterBy entirely
        ]

        # First, try async client (unit tests patch this path)
        try:
            from regscale.integrations.commercial.wizv2.utils import compliance_job_progress

            with compliance_job_progress:
                task = compliance_job_progress.add_task(
                    f"[#f68d1f]Fetching Wiz policy assessments (async, page size: {page_size})...",
                    total=1,
                )
                results = run_async_queries(
                    endpoint=self.wiz_endpoint or WIZ_URL,
                    headers=headers,
                    query_configs=[
                        {
                            "type": WizVulnerabilityType.CONFIGURATION,
                            "query": WIZ_POLICY_QUERY,
                            "topic_key": "policyAssessments",
                            "variables": {"first": page_size},
                        }
                    ],
                    progress_tracker=compliance_job_progress,
                    max_concurrent=1,
                )
                compliance_job_progress.update(task, completed=1, advance=1)
            if results and len(results) == 1 and not results[0][2]:
                nodes = results[0][1] or []
                filtered = self._filter_nodes_to_framework(nodes)
                self._write_assessments_cache(filtered)
                return filtered
        except Exception:
            # Fall back to requests-based method below
            pass

        filtered_nodes = self._fetch_assessments_with_variants(
            session=session,
            headers=headers,
            base_variables=base_variables,
            page_size=page_size,
            filter_variants=filter_variants,
        )
        self._write_assessments_cache(filtered_nodes)
        return filtered_nodes

    def _build_wiz_headers(self) -> Dict[str, str]:
        """
        Build HTTP headers for Wiz GraphQL API requests.

        :return: Dictionary of HTTP headers including authorization
        :rtype: Dict[str, str]
        """
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def _prepare_wiz_requests_session(self):
        """
        Prepare a requests session with retry logic for Wiz API calls.

        :return: Configured requests session with retry adapter
        :rtype: requests.Session
        """
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry

        session = requests.Session()
        retry = Retry(
            total=5,
            connect=5,
            read=5,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def _fetch_assessments_with_variants(
        self,
        *,
        session,
        headers: Dict[str, str],
        base_variables: Dict[str, Any],
        page_size: int,
        filter_variants: List[Optional[Dict[str, Any]]],
    ) -> List[Dict[str, Any]]:
        from regscale.integrations.commercial.wizv2.utils import compliance_job_progress

        last_error: Optional[Exception] = None

        # In unit tests, the async client is patched and we should not hit network.

        with compliance_job_progress:
            task = compliance_job_progress.add_task(
                f"[#f68d1f]Fetching Wiz policy assessments (page size: {page_size})...",
                total=None,
            )
            for fv in filter_variants:
                try:
                    # If endpoint is not set (tests), short-circuit to async path mock
                    if not self.wiz_endpoint:
                        results = run_async_queries(
                            endpoint=WIZ_URL,
                            headers=headers,
                            query_configs=[
                                {
                                    "type": WizVulnerabilityType.CONFIGURATION,
                                    "query": WIZ_POLICY_QUERY,
                                    "topic_key": "policyAssessments",
                                    "variables": {**base_variables, **({"filterBy": fv} if fv is not None else {})},
                                }
                            ],
                            progress_tracker=compliance_job_progress,
                            max_concurrent=1,
                        )
                        # Expected mocked structure: [(type, nodes, error)]
                        if results and len(results) == 1 and not results[0][2]:
                            nodes = results[0][1] or []
                            return self._filter_nodes_to_framework(nodes)

                    return self._fetch_with_filter_variant(
                        session=session,
                        headers=headers,
                        base_variables=base_variables,
                        filter_variant=fv,
                        page_size=page_size,
                        progress=compliance_job_progress,
                        task=task,
                    )
                except Exception as exc:  # noqa: BLE001 - propagate last error
                    last_error = exc

        msg = f"Failed to fetch policy assessments after trying all filter variants: {last_error}"
        logger.error(msg)
        error_and_exit(msg)

    def _variant_name(self, fv: Optional[Dict[str, Any]]) -> str:
        """
        Get a human-readable name for a filter variant.

        :param Optional[Dict[str, Any]] fv: Filter variant dictionary
        :return: Human-readable variant name
        :rtype: str
        """
        if fv is None:
            return "omitted"
        if fv == {}:
            return "empty"
        try:
            return next(iter(fv.keys()))
        except Exception:
            return "unknown"

    def _fetch_with_filter_variant(
        self,
        *,
        session,
        headers: Dict[str, str],
        base_variables: Dict[str, Any],
        filter_variant: Optional[Dict[str, Any]],
        page_size: int,
        progress,
        task,
    ) -> List[Dict[str, Any]]:
        variant_name = self._variant_name(filter_variant)
        progress.update(
            task,
            description=(f"[#f68d1f]Fetching Wiz policy assessments (limit: {page_size}, variant: {variant_name})..."),
            advance=1,
        )

        variables = base_variables.copy() if filter_variant is None else {**base_variables, "filterBy": filter_variant}

        def on_page(page_idx: int, page_count: int, total_nodes: int) -> None:
            progress.update(
                task,
                description=(
                    f"[cyan]Fetching policy assessments: page {page_idx}, "
                    f"fetched {total_nodes} nodes (last page: {page_count})"
                ),
                advance=1,
            )

        nodes = self._execute_wiz_policy_query_paginated(
            session=session, headers=headers, variables=variables, on_page=on_page
        )
        filtered_nodes = self._filter_nodes_to_framework(nodes)
        progress.update(
            task,
            description=f"[green]Completed Wiz policy assessments: {len(filtered_nodes)} nodes",
            completed=1,
            total=1,
        )
        logger.info("Successfully fetched Wiz policy assessments")

        return filtered_nodes

    def _execute_wiz_policy_query_paginated(
        self,
        *,
        session,
        headers: Dict[str, str],
        variables: Dict[str, Any],
        on_page=None,
    ) -> List[Dict[str, Any]]:
        import requests

        nodes: List[Dict[str, Any]] = []
        after_cursor: Optional[str] = variables.get("after")
        page_index = 0
        while True:
            payload_vars = variables.copy()
            payload_vars["after"] = after_cursor
            payload = {"query": WIZ_POLICY_QUERY, "variables": payload_vars}
            resp = session.post(self.wiz_endpoint, json=payload, headers=headers, timeout=300)
            if resp.status_code >= 400:
                raise requests.HTTPError(f"{resp.status_code} {resp.text[:500]}")
            data = resp.json()
            if "errors" in data:
                raise RuntimeError(str(data["errors"]))
            topic = data.get("data", {}).get("policyAssessments", {})
            page_nodes = topic.get("nodes", [])
            page_info = topic.get("pageInfo", {})
            nodes.extend(page_nodes)
            page_index += 1
            if on_page:
                try:
                    on_page(page_index, len(page_nodes), len(nodes))
                except Exception:
                    pass
            has_next = page_info.get("hasNextPage", False)
            after_cursor = page_info.get("endCursor")
            if not has_next:
                break
        return nodes

    def _filter_nodes_to_framework(self, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        filtered_nodes: List[Dict[str, Any]] = []
        for n in nodes:
            try:
                subcats = ((n or {}).get("policy") or {}).get("securitySubCategories", [])
                # If no subcategories info is present, include the node (cannot evaluate framework)
                if not subcats:
                    filtered_nodes.append(n)
                    continue
                if any((sc.get("category", {}).get("framework", {}).get("id") == self.framework_id) for sc in subcats):
                    filtered_nodes.append(n)
            except Exception:
                filtered_nodes.append(n)
        return filtered_nodes

    def _get_assessments_cache_path(self) -> str:
        """
        Get the file path for policy assessments cache.

        :return: Full path to cache file
        :rtype: str
        """
        try:
            os.makedirs(self.policy_cache_dir, exist_ok=True)
        except Exception:
            pass
        return self.policy_cache_file

    def _load_assessments_from_cache(self) -> Optional[List[Dict[str, Any]]]:
        """
        Load policy assessments from cache file if valid and within TTL.

        :return: Cached assessment nodes or None if cache is invalid/expired
        :rtype: Optional[List[Dict[str, Any]]]
        """
        if self.force_refresh or self.cache_duration_minutes <= 0:
            return None
        try:
            path = self._get_assessments_cache_path()
            if not os.path.exists(path):
                return None
            # File age check
            max_age_seconds = max(0, int(self.cache_duration_minutes)) * 60
            age = max(0.0, (datetime.now().timestamp() - os.path.getmtime(path)))
            if age > max_age_seconds:
                return None
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            nodes = data.get("nodes") or data.get("assessments") or []
            # Defensive: ensure list
            if not isinstance(nodes, list):
                return None
            return nodes
        except Exception:
            return None

    def _write_assessments_cache(self, nodes: List[Dict[str, Any]]) -> None:
        """
        Write policy assessment nodes to cache file.

        :param List[Dict[str, Any]] nodes: Assessment nodes to cache
        :return: None
        :rtype: None
        """
        # Only write cache when enabled
        if self.cache_duration_minutes <= 0:
            return None
        try:
            path = self._get_assessments_cache_path()
            payload = {
                "timestamp": datetime.now().isoformat(),
                "wiz_project_id": self.wiz_project_id,
                "framework_id": self.framework_id,
                "nodes": nodes,
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False)
        except Exception:
            # Cache write failures should not interrupt flow
            pass

    def write_policy_data_to_json(self) -> str:
        """
        Write policy assessment data to JSON and JSONL files with timestamp.

        :return: Path to the written JSON file
        :rtype: str
        """
        # Create artifacts/wiz directory if it doesn't exist
        artifacts_dir = os.path.join("artifacts", "wiz")
        os.makedirs(artifacts_dir, exist_ok=True)

        # Generate timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_json = f"policy_compliance_report_{timestamp}.json"
        filename_jsonl = f"policy_compliance_report_{timestamp}.jsonl"
        file_path = os.path.join(artifacts_dir, filename_json)
        file_path_jsonl = os.path.join(artifacts_dir, filename_jsonl)

        # Prepare data for JSON export
        export_data = {
            "metadata": {
                "timestamp": timestamp,
                "wiz_project_id": self.wiz_project_id,
                "framework_id": self.framework_id,
                "framework_name": self.get_framework_name(self.framework_id),
                "total_assessments": len(self.all_compliance_items),
                "pass_count": len(self.all_compliance_items) - len(self.failed_compliance_items),
                "fail_count": len(self.failed_compliance_items),
                "unique_controls": len({item.control_id for item in self.all_compliance_items if item.control_id}),
            },
            "framework_mapping": self.framework_mapping,
            "policy_assessments": [],
        }

        # Convert compliance items to serializable format
        for compliance_item in self.all_compliance_items:
            if isinstance(compliance_item, WizComplianceItem):
                # Filter policy subcategories to only the selected framework to avoid noise
                filtered_policy = dict(compliance_item.policy) if compliance_item.policy else {}
                if filtered_policy:
                    subcats = filtered_policy.get("securitySubCategories", [])
                    if subcats:
                        target_framework_id = self.framework_id
                        filtered_subcats = [
                            sc
                            for sc in subcats
                            if sc.get("category", {}).get("framework", {}).get("id") == target_framework_id
                        ]
                        if filtered_subcats:
                            filtered_policy["securitySubCategories"] = filtered_subcats
                        else:
                            # If filter removes all, keep original to retain context
                            pass
                assessment_data = {
                    "id": compliance_item.id,
                    "result": compliance_item.result,
                    "control_id": compliance_item.control_id,
                    "framework_name": compliance_item.framework,
                    "framework_id": compliance_item.framework_id,
                    "policy": filtered_policy or compliance_item.policy,
                    "resource": compliance_item.resource,
                    "output": compliance_item.output,
                }
                export_data["policy_assessments"].append(assessment_data)

        # Write to JSON and JSONL files
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Policy compliance data written to: {file_path}")
            # JSONL: aggregated by control_id (optional)
            if getattr(self, "write_jsonl_output", False):
                control_agg = self._build_control_aggregation()
                with open(file_path_jsonl, "w", encoding="utf-8") as jf:
                    for control_id, ctrl in control_agg.items():
                        jf.write(json.dumps(ctrl, ensure_ascii=False) + "\n")
                logger.info(f"Policy compliance JSONL written to: {file_path_jsonl}")
            self._cleanup_artifacts(artifacts_dir, keep=CACHE_CLEANUP_KEEP_COUNT)
            return file_path

        except Exception as e:
            error_and_exit(f"Failed to write policy data to JSON: {str(e)}")

    def _build_control_aggregation(self) -> Dict[str, Dict[str, Any]]:
        """
        Build an aggregated view per control_id for JSONL export.

        Creates a control-centric view with assets affected and policy checks.

        :return: Dictionary mapping control IDs to aggregated data
        :rtype: Dict[str, Dict[str, Any]]

        {
          control_id: {
            "control_id": "AC-2(1)",
            "framework_id": "wf-id-4",
            "framework_name": "NIST SP 800-53 Revision 5",
            "failed": true,
            "assets_affected": [
               {
                 "resource_id": "...",
                 "resource_name": "...",
                 "resource_type": "...",
                 "region": "...",
                 "subscription": "...",
                 "checks": [
                    {"title": "Policy name", "result": "FAIL", "remediation": "..."}
                 ]
               }
            ]
          }
        }
        """
        control_map: Dict[str, Dict[str, Any]] = {}

        for item in self.all_compliance_items:
            if not isinstance(item, WizComplianceItem):
                # Skip non-wiz items in this aggregation
                continue

            ctrl_id = self._normalize_control_id_string(item.control_id)
            if not ctrl_id:
                continue

            ctrl_entry = control_map.get(ctrl_id)
            if not ctrl_entry:
                ctrl_entry = {
                    "control_id": ctrl_id,
                    "framework_id": self.framework_id,
                    "framework_name": self.get_framework_name(self.framework_id),
                    "failed": False,
                    "assets_affected": [],
                }
                # Track assets in a dict for dedupe while building, convert to list at end
                ctrl_entry["_assets_idx"] = {}
                control_map[ctrl_id] = ctrl_entry

            # Determine fail/pass at control level
            if item.compliance_result in self.FAIL_STATUSES:
                ctrl_entry["failed"] = True

            # Asset bucket
            asset_id = item.resource_id
            assets_idx: Dict[str, Any] = ctrl_entry["_assets_idx"]  # type: ignore
            asset_entry = assets_idx.get(asset_id)
            if not asset_entry:
                asset_entry = {
                    "resource_id": item.resource_id,
                    "resource_name": item.resource_name,
                    "resource_type": (item.resource or {}).get("type"),
                    "region": (item.resource or {}).get("region"),
                    "subscription": ((item.resource or {}).get("subscription") or {}).get("name"),
                    "checks": [],
                }
                assets_idx[asset_id] = asset_entry

            # Append policy check info
            policy_name = (item.policy or {}).get("name") or (item.policy or {}).get("hostConfigurationRule", {}).get(
                "name"
            )
            remediation = (item.policy or {}).get("remediationInstructions")
            if policy_name:
                # Deduplicate identical checks by title within an asset
                titles = {c.get("title") for c in asset_entry["checks"]}
                if policy_name not in titles:
                    check = {
                        "title": policy_name,
                        "result": item.compliance_result,
                        "remediation": remediation,
                    }
                    asset_entry["checks"].append(check)

        # Convert asset index maps to lists for final output
        for ctrl in control_map.values():
            assets_idx = ctrl.pop("_assets_idx", {})  # type: ignore
            ctrl["assets_affected"] = list(assets_idx.values())

        return control_map

    @staticmethod
    def _normalize_control_id_string(control_id: Optional[str]) -> Optional[str]:
        """
        Normalize control id variants to a canonical form, e.g. 'AC-4(2)'.
        Accepts 'ac-4 (2)', 'AC-4-2', 'AC-4(2)'. Returns uppercase base with optional '(sub)'.
        """
        if not control_id:
            return None
        cid = control_id.strip()
        # Use precompiled safe regex to avoid catastrophic backtracking on crafted input
        m = SAFE_CONTROL_ID_RE.match(cid)
        if not m:
            return cid.upper()
        base = m.group(1).upper()
        # Subcontrol may be captured in group 2, 3, or 4 depending on the branch matched
        sub = m.group(2) or m.group(3) or m.group(4)
        return f"{base}({sub})" if sub else base

    @staticmethod
    def parse_control_jsonl(jsonl_path: str) -> Dict[str, Dict[str, Any]]:
        """
        Parse the aggregated control JSONL back into a dict keyed by control_id.
        """
        aggregated: Dict[str, Dict[str, Any]] = {}
        try:
            with open(jsonl_path, "r", encoding="utf-8") as jf:
                for line in jf:
                    line = line.strip()
                    if not line:
                        continue
                    obj = json.loads(line)
                    ctrl_id = obj.get("control_id")
                    if ctrl_id:
                        aggregated[ctrl_id] = obj
        except Exception as exc:
            logger.error(f"Error parsing JSONL {jsonl_path}: {exc}")
        return aggregated

    def _cleanup_artifacts(self, dir_path: str, keep: int = CACHE_CLEANUP_KEEP_COUNT) -> None:
        """
        Keep the most recent JSON and JSONL policy_compliance_report files, delete older ones.

        :param str dir_path: Directory containing artifacts to clean
        :param int keep: Number of most recent files per extension to keep
        :return: None
        :rtype: None
        """
        try:
            entries = [
                (f, os.path.join(dir_path, f))
                for f in os.listdir(dir_path)
                if f.startswith("policy_compliance_report_")
                and (f.endswith(JSON_FILE_EXT) or f.endswith(JSONL_FILE_EXT))
            ]
            # Group by extension to keep per-type
            by_ext: Dict[str, List[tuple[str, str]]] = {JSON_FILE_EXT: [], JSONL_FILE_EXT: []}
            for name, path in entries:
                ext = JSONL_FILE_EXT if name.endswith(JSONL_FILE_EXT) else JSON_FILE_EXT
                by_ext[ext].append((name, path))

            for ext, files in by_ext.items():
                files.sort(key=lambda p: os.path.getmtime(p[1]), reverse=True)
                for _, old_path in files[keep:]:
                    try:
                        os.remove(old_path)
                    except Exception:
                        # Non-fatal; continue cleanup
                        pass
        except Exception:
            pass

    def load_or_create_framework_mapping(self) -> Dict[str, str]:
        """
        Load framework mapping from cache file or create it by fetching from Wiz.

        :return: Framework ID to name mapping dictionary
        :rtype: Dict[str, str]
        """
        # Check if cache file exists
        if os.path.exists(self.framework_cache_file):
            logger.info("Loading framework mapping from cache file")
            return self._load_framework_mapping_from_cache()

        logger.info("Framework mapping cache not found, fetching from Wiz API")
        return self._fetch_and_cache_framework_mapping()

    def _load_framework_mapping_from_cache(self) -> Dict[str, str]:
        """
        Load framework mapping from existing JSON cache file.

        :return: Framework ID to name mapping
        :rtype: Dict[str, str]
        """
        try:
            with open(self.framework_cache_file, "r", encoding="utf-8") as f:
                cache_data = json.load(f)

            framework_mapping = cache_data.get("framework_mapping", {})
            cache_timestamp = cache_data.get("timestamp", "")

            logger.info(f"Loaded {len(framework_mapping)} frameworks from cache (created: {cache_timestamp})")
            self.framework_mapping = framework_mapping
            return framework_mapping

        except Exception as e:
            logger.error(f"Error loading framework mapping from cache: {str(e)}")
            logger.info("Falling back to fetching fresh framework data")
            return self._fetch_and_cache_framework_mapping()

    def _fetch_and_cache_framework_mapping(self) -> Dict[str, str]:
        """
        Fetch framework data from Wiz API and cache it to JSON file.

        :return: Framework ID to name mapping
        :rtype: Dict[str, str]
        """
        frameworks = self._fetch_security_frameworks()
        framework_mapping = self._create_framework_mapping(frameworks)
        self._write_framework_mapping_to_json(framework_mapping, frameworks)

        self.framework_mapping = framework_mapping
        return framework_mapping

    def _fetch_security_frameworks(self) -> List[Dict[str, Any]]:
        """
        Fetch security frameworks from Wiz GraphQL API.

        :return: List of framework data
        :rtype: List[Dict[str, Any]]
        """
        logger.info("Fetching security frameworks from Wiz...")

        # Authenticate if not already done
        if not self.access_token:
            self.authenticate_wiz()

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        query_config = {
            "type": WizVulnerabilityType.CONFIGURATION,  # Using existing enum type
            "query": WIZ_FRAMEWORK_QUERY,
            "topic_key": "securityFrameworks",
            "variables": {"first": 200, "filterBy": {}},  # Get all frameworks, no filtering
        }

        try:
            # Execute the query using async client with visible progress
            from regscale.integrations.commercial.wizv2.utils import compliance_job_progress

            with compliance_job_progress:
                task = compliance_job_progress.add_task("[#f68d1f]Fetching Wiz security frameworks...", total=1)
            results = run_async_queries(
                endpoint=self.wiz_endpoint,
                headers=headers,
                query_configs=[query_config],
                progress_tracker=compliance_job_progress,
                max_concurrent=1,
            )
            compliance_job_progress.update(task, completed=1, advance=1)

            if not results or len(results) == 0:
                logger.warning("No framework results returned from Wiz")
                return []

            _, nodes, error = results[0]

            if error:
                logger.error(f"Error fetching security frameworks: {error}")
                error_and_exit(f"Error fetching security frameworks: {error}")

            logger.info(f"Successfully fetched {len(nodes)} security frameworks")
            return nodes

        except Exception as e:
            error_and_exit(f"Failed to fetch security frameworks: {str(e)}")

    def _create_framework_mapping(self, frameworks: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Create framework ID to name mapping from framework data.

        :param List[Dict[str, Any]] frameworks: Raw framework data from Wiz API
        :return: Dictionary mapping framework IDs to human-readable names
        :rtype: Dict[str, str]
        """
        framework_mapping = {}

        for framework in frameworks:
            framework_id = framework.get("id")
            framework_name = framework.get("name")

            if framework_id and framework_name:
                framework_mapping[framework_id] = framework_name

        logger.info(f"Created mapping for {len(framework_mapping)} frameworks")
        return framework_mapping

    def _write_framework_mapping_to_json(
        self, framework_mapping: Dict[str, str], raw_frameworks: List[Dict[str, Any]]
    ) -> None:
        """
        Write framework mapping and raw data to JSON cache file.

        :param Dict[str, str] framework_mapping: Framework ID to name mapping dictionary
        :param List[Dict[str, Any]] raw_frameworks: Raw framework data from Wiz API
        :return: None
        :rtype: None
        """
        # Create artifacts/wiz directory if it doesn't exist
        artifacts_dir = os.path.dirname(self.framework_cache_file)
        os.makedirs(artifacts_dir, exist_ok=True)

        # Prepare data for JSON export
        cache_data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_frameworks": len(framework_mapping),
                "enabled_frameworks": len([f for f in raw_frameworks if f.get("enabled", False)]),
                "builtin_frameworks": len([f for f in raw_frameworks if f.get("builtin", False)]),
                "description": "Cached Wiz security framework mappings",
            },
            "framework_mapping": framework_mapping,
            "raw_frameworks": raw_frameworks,
        }

        # Write to JSON file
        try:
            with open(self.framework_cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Framework mapping cached to: {self.framework_cache_file}")

        except Exception as e:
            logger.error(f"Failed to write framework mapping to cache: {str(e)}")
            # Don't exit here - this is not critical to the main functionality

    def get_framework_name(self, framework_id: str) -> str:
        """
        Get framework name by ID from cached mapping.

        :param str framework_id: Framework ID
        :return: Framework name or ID if not found
        :rtype: str
        """
        # Load mapping if not already loaded
        if not self.framework_mapping:
            self.load_or_create_framework_mapping()

        return self.framework_mapping.get(framework_id, framework_id)

    def sync_compliance(self) -> None:
        """
        Override base sync_compliance to ensure proper order for controlId/assessmentId assignment.

        CRITICAL: Control assessments MUST be created BEFORE issues are processed
        to ensure controlId and assessmentId can be properly set.
        """
        logger.info(f"Starting {self.title} compliance sync with proper assessment ordering...")

        try:
            scan_history = self.create_scan_history()
            self.process_compliance_data()

            # Step 1: Sync assets first
            self._sync_assets()

            # Step 2: CRITICAL - Pre-populate control implementation cache BEFORE creating assessments
            logger.info("Pre-populating control implementation cache for issue processing...")
            self._populate_control_implementation_cache()

            # Step 3: Create control assessments BEFORE issues (ensures assessmentId is available)
            logger.info("Creating control assessments BEFORE issue processing...")
            self._sync_control_assessments()

            # Step 3.5: CRITICAL - Refresh assessment cache after assessments are created
            logger.info("Refreshing assessment cache with newly created assessments...")
            self._refresh_assessment_cache_after_creation()

            # Step 4: NOW process issues with controlId and assessmentId properly set
            logger.info("Processing issues with control and assessment IDs available...")
            self._sync_issues()

            self._finalize_scan_history(scan_history)

            logger.info(f"Completed {self.title} compliance sync with proper assessment ordering")

        except Exception as e:
            error_and_exit(f"Error during compliance sync: {e}")

    def sync_policy_compliance(self, create_issues: bool = None, update_control_status: bool = None) -> None:
        """
        Main method to sync policy compliance data from Wiz.

        :param bool create_issues: Whether to create issues for failed assessments (uses instance default if None)
        :param bool update_control_status: Whether to update control implementation status (uses instance default if None)
        """
        logger.info("Starting Wiz policy compliance sync...")

        try:
            # Use instance defaults if not specified
            if create_issues is None:
                create_issues = self.create_issues
            if update_control_status is None:
                update_control_status = self.update_control_status

            # Step 1: Authenticate with Wiz
            self.authenticate_wiz()

            # Step 2: Load or create framework mapping cache
            self.load_or_create_framework_mapping()

            # Persist flags on the instance for downstream logic
            if create_issues is not None:
                self.create_issues = create_issues
            if update_control_status is not None:
                self.update_control_status = update_control_status

            # Step 3: Sync using the overridden method (which ensures proper ordering)
            logger.info(
                f"Sync parameters: create_issues={self.create_issues}, update_control_status={self.update_control_status}"
            )

            self.sync_compliance()

            # Step 4: Write data to JSON file for reference (post-processing)
            json_file = self.write_policy_data_to_json()
            logger.info(f"Policy compliance data saved to: {json_file}")

            logger.info("Policy compliance sync completed successfully")

        except Exception as e:
            error_and_exit(f"Policy compliance sync failed: {str(e)}")

    def sync_wiz_compliance(self) -> None:
        """
        Convenience method for backward compatibility.

        :return: None
        :rtype: None
        """
        self.sync_policy_compliance()

    def is_poam(self, finding: IntegrationFinding) -> bool:  # type: ignore[override]
        """
        Determine if an issue should be a POAM.

        If the CLI flag `--create-poams/-cp` was provided (mapped to `self.create_poams`),
        force POAM for all created/updated issues. Otherwise, fall back to the default
        scanner behavior.
        """
        try:
            if getattr(self, "create_poams", False):
                return True
        except Exception:
            pass
        return super().is_poam(finding)

    def create_or_update_issue_from_finding(
        self,
        title: str,
        finding: IntegrationFinding,
    ) -> regscale_models.Issue:
        """
        Create/update the issue with ALL fields set BEFORE saving.

        This method ensures proper data flow:
        1. Check for existing issues to prevent duplicates
        2. Pre-populate compliance fields on the finding
        3. Use parent class logic which saves with all fields set

        This fixes the duplicate issue creation problem by using proper
        duplicate detection and avoids double-saving.
        """
        # Load cache if not already loaded for duplicate detection
        self._load_existing_records_cache()

        # CRITICAL: Pre-populate compliance fields on the finding BEFORE parent call
        # This ensures the parent class saves the issue with all fields already set
        self._populate_compliance_fields_on_finding(finding)

        # CRITICAL FIX: If assessment_id is set, prepare the finding for assessment parenting
        if hasattr(finding, "assessment_id") and finding.assessment_id:
            assessment_id = finding.assessment_id
            logger.debug(f"PRE-SETTING ASSESSMENT PARENT: assessmentId={assessment_id}")

            # Add parent override fields to the finding for the ScannerIntegration to use
            finding._override_parent_id = assessment_id
            finding._override_parent_module = "assessments"

            logger.debug(f"   ✅ Finding will use parent: assessments #{assessment_id}")

        # Check for existing issue by external_id first
        external_id = finding.external_id
        existing_issue = self._find_existing_issue_cached(external_id)

        if existing_issue:
            return self._update_existing_issue_with_compliance_fields(existing_issue, title, finding)
        else:
            # Set finding context for our override method to access
            self._current_finding_context = finding
            try:
                # Parent class will now create/save the issue with compliance fields already set
                return super().create_or_update_issue_from_finding(title, finding)
            finally:
                # Clean up context
                if hasattr(self, "_current_finding_context"):
                    delattr(self, "_current_finding_context")

    def _update_existing_issue_with_compliance_fields(
        self, existing_issue: regscale_models.Issue, title: str, finding: IntegrationFinding
    ) -> regscale_models.Issue:
        """
        Update existing issue with basic fields and enhance with compliance-specific fields.

        :param existing_issue: The existing issue to update
        :param title: New issue title
        :param finding: Finding with updated data
        :return: Updated issue with all fields set
        """

        # Update basic fields (similar to parent class logic)
        existing_issue.title = title
        existing_issue.description = finding.description
        existing_issue.severity = finding.severity
        existing_issue.status = finding.status
        existing_issue.dateLastUpdated = self.scan_date

        # Set control-related field
        if getattr(finding, "control_labels", None):
            existing_issue.affectedControls = ",".join(finding.control_labels)
        elif getattr(finding, "affected_controls", None):
            existing_issue.affectedControls = finding.affected_controls

        # Enhance with compliance-specific fields
        self._enhance_issue_with_compliance_fields(existing_issue, finding)

        # CRITICAL FIX: Handle assessment parenting for existing issues too
        if hasattr(finding, "assessment_id") and finding.assessment_id:
            assessment_id = finding.assessment_id

            # Set assessment as the parent
            existing_issue.parentId = assessment_id
            existing_issue.parentModule = "assessments"
            existing_issue.assessmentId = assessment_id

        existing_issue.save()

        return existing_issue

    def _create_or_update_issue(
        self,
        finding: IntegrationFinding,
        issue_status,
        title: str,
        existing_issue=None,
    ):
        """
        Override parent method to handle assessment parenting correctly.

        CRITICAL FIX: Check if the finding has assessment parent overrides and apply them.
        """
        # Get consolidated asset identifier
        asset_identifier = self.get_consolidated_asset_identifier(finding, existing_issue)

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

        # CRITICAL FIX: Check for parent overrides from the finding
        if hasattr(finding, "_override_parent_id") and hasattr(finding, "_override_parent_module"):
            parent_id = finding._override_parent_id
            parent_module = finding._override_parent_module
            logger.debug(f"USING OVERRIDE PARENT: {parent_module} #{parent_id}")
        else:
            parent_id = self.plan_id
            parent_module = self.parent_module

        # Update all fields (copying from ScannerIntegration but with override parent)
        issue.parentId = parent_id
        issue.parentModule = parent_module
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

        # Ensure a due date is always set using configured policy defaults (e.g., FedRAMP)
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
        issue.description = description
        issue.sourceReport = finding.source_report or self.title
        issue.recommendedActions = finding.recommendation_for_mitigation
        issue.assetIdentifier = asset_identifier
        issue.securityChecks = finding.security_check or finding.external_id
        issue.remediationDescription = remediation_description
        issue.integrationFindingId = self.get_finding_identifier(finding)
        issue.poamComments = finding.poam_comments
        issue.cve = finding.cve

        # CRITICAL: Set assessmentId (this is the key fix)
        issue.assessmentId = finding.assessment_id
        logger.debug(f"SETTING assessmentId = {finding.assessment_id} with parent = {parent_module} #{parent_id}")

        control_id = self.get_control_implementation_id_for_cci(finding.cci_ref) if finding.cci_ref else None
        issue.controlId = control_id

        # Add the control implementation ids and the cci ref if it exists
        cci_control_ids = [control_id] if control_id is not None else []
        if finding.affected_controls:
            issue.affectedControls = finding.affected_controls
        elif finding.control_labels:
            issue.affectedControls = ", ".join(sorted({cl for cl in finding.control_labels if cl}))

        issue.controlImplementationIds = list(set(finding._control_implementation_ids + cci_control_ids))  # noqa
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

        if finding.cve:
            issue = self.lookup_kev_and_update_issue(cve=finding.cve, issue=issue, cisa_kevs=self._kev_data)

        if existing_issue:
            logger.debug(f"Saving existing issue {issue.id} with assessmentId={issue.assessmentId}")
            issue.save(bulk=True)
        else:
            logger.info(f"Creating new issue with assessmentId={issue.assessmentId}")
            issue = issue.create_or_update(
                bulk_update=True, defaults={"otherIdentifier": self._get_other_identifier(finding, is_poam)}
            )
            if issue and issue.id:
                logger.debug(f"Issue created with ID: {issue.id}")
                self.extra_data_to_properties(finding, issue.id)
            else:
                logger.error(f" Issue creation failed - no ID returned for finding {finding.external_id}")
                return None

        # Only create milestones if issue has an ID
        if issue and issue.id:
            # Check if existing issue needs initial milestone creation
            if existing_issue and ScannerVariables.useMilestones:
                self._ensure_issue_has_milestone(issue, finding)

            self._handle_property_and_milestone_creation(issue, finding, existing_issue)
        else:
            logger.debug("Skipping milestone creation - issue has no ID")

        return issue

    def _populate_compliance_fields_on_finding(self, finding: IntegrationFinding) -> None:
        """
        Pre-populate compliance-specific fields on the finding before issue creation.

        This ensures controlId and assessmentId are set on the finding object
        so the parent class can save the issue with all fields in one operation.

        The parent class expects:
        - finding.assessment_id -> issue.assessmentId
        - finding.cci_ref -> calls get_control_implementation_id_for_cci() -> issue.controlId

        :param finding: Finding to populate with compliance fields
        """
        try:
            # Set compliance fields on the finding itself before issue creation
            if hasattr(finding, "rule_id") and finding.rule_id:
                control_id = self._normalize_control_id_string(finding.rule_id)
                if control_id:

                    # Get control implementation ID
                    impl_id = self._issue_field_setter._get_or_find_implementation_id(control_id)
                    if impl_id:
                        # Store the control ID as cci_ref so parent class calls our override method
                        finding.cci_ref = control_id
                        # Cache the implementation ID for our override method
                        finding._wiz_control_implementation_id = impl_id

                        # Get assessment ID and set it on the finding (parent class uses this directly)
                        assess_id = self._issue_field_setter._get_or_find_assessment_id(impl_id)
                        if assess_id:
                            finding.assessment_id = assess_id
        except Exception:
            pass

    def _ensure_issue_has_milestone(self, issue: regscale_models.Issue, finding: IntegrationFinding) -> None:
        """
        Ensure that an existing issue has at least one milestone.

        This method checks if an existing issue has any milestones, and if not,
        creates an initial "Issue created" milestone. This handles cases where
        issues were created before milestone tracking was enabled, or were
        created through other means without milestones.

        :param issue: The existing issue to check for milestones
        :param finding: The finding data
        :return: None
        """
        try:
            # Check if the issue already has milestones
            # We need to make a direct API call because the Milestone model's endpoint configuration
            # doesn't include the module parameter that the API expects
            from regscale.models.regscale_models.milestone import Milestone

            try:
                existing_milestones = Milestone.get_all_by_parent(parent_id=issue.id, parent_module="issues")
                logger.debug(f"Fetched {len(existing_milestones)} existing milestones for issue {issue.id}")
            except Exception as api_error:
                # If the API call fails, log it and assume no milestones exist
                logger.debug(f"Could not fetch existing milestones for issue {issue.id}: {api_error}")
                existing_milestones = []

            if not existing_milestones:
                # Create an initial milestone for the existing issue
                logger.debug(f"Creating initial milestone for existing issue {issue.id} that had no milestones")

                # Use the issue's dateCreated if available, otherwise use current date
                if hasattr(issue, "dateCreated") and issue.dateCreated:
                    # Convert to string if it's a datetime object (e.g., in tests)
                    if hasattr(issue.dateCreated, "isoformat"):
                        milestone_date = issue.dateCreated.isoformat()
                    else:
                        milestone_date = issue.dateCreated
                else:
                    milestone_date = get_current_datetime()

                regscale_models.Milestone(
                    title=f"Issue created by {self.title}",
                    milestoneDate=milestone_date,
                    responsiblePersonId=self.assessor_id,
                    parentID=issue.id,
                    parentModule=regscale_models.Issue.get_module_slug(),
                ).create()

                logger.debug(f"Created initial milestone for existing issue {issue.id}")
        except Exception as e:
            logger.warning(f"Could not check/create milestone for issue {issue.id}: {e}")

    def _enhance_issue_with_compliance_fields(self, issue: regscale_models.Issue, finding: IntegrationFinding) -> None:
        """
        Enhance an issue with compliance-specific fields (controlId and assessmentId).

        NOTE: This method is now primarily for the existing issue update path.
        New issues should have fields set via _populate_compliance_fields_on_finding.

        :param issue: Issue object to enhance
        :param finding: Finding with control data
        """
        try:
            # Set control implementation and assessment IDs using our field setter
            if hasattr(finding, "rule_id") and finding.rule_id:
                control_id = self._normalize_control_id_string(finding.rule_id)
                if control_id:
                    result = self._issue_field_setter.set_control_and_assessment_ids(issue, control_id)
                    if not result.success:
                        logger.warning(f"Failed to set compliance fields for '{control_id}': {result.error_message}")
        except Exception:
            pass

    def get_control_implementation_id_for_cci(self, cci: Optional[str]) -> Optional[int]:
        """
        Override parent method to return control implementation ID for Wiz control IDs.

        The parent class calls this method when finding.cci_ref is set, and uses the
        returned value to set issue.controlId. We store our control implementation
        ID on the finding and return it here.

        :param cci: Control identifier (e.g., 'AC-2(1)') stored in finding.cci_ref
        :return: Control implementation ID if found, None otherwise
        """
        # Check if this is a call with our cached implementation ID on the current finding
        if hasattr(self, "_current_finding_context"):
            finding = self._current_finding_context
            if (
                hasattr(finding, "_wiz_control_implementation_id")
                and hasattr(finding, "cci_ref")
                and finding.cci_ref == cci
            ):
                impl_id = finding._wiz_control_implementation_id
                return impl_id

        # Fallback: try to look it up directly (for edge cases)
        if cci:
            control_id = self._normalize_control_id_string(cci)
            if control_id:
                impl_id = self._issue_field_setter._get_or_find_implementation_id(control_id)
                if impl_id:
                    return impl_id

        # Final fallback to parent class behavior
        return super().get_control_implementation_id_for_cci(cci)

    def _populate_control_implementation_cache(self) -> None:
        """
        Pre-populate the control implementation and assessment caches.

        CRITICAL: This ensures controlId and assessmentId can be reliably set on issues.
        This method loads control implementations and their associated assessments into
        cache to enable fast lookups during issue processing.

        :return: None
        :rtype: None
        """
        try:
            from regscale.models import regscale_models

            logger.info("Pre-populating control implementation cache for issue processing...")

            # Get all control implementations for this plan
            implementations = regscale_models.ControlImplementation.get_all_by_parent(
                parent_id=self.plan_id, parent_module=self.parent_module
            )

            if not implementations:
                logger.warning("No control implementations found for this plan")
                return

            logger.info(f"Found {len(implementations)} control implementations to cache")

            # Cache SecurityControl lookups to avoid repeated API calls
            security_control_cache = {}
            controls_mapped = 0
            assessments_mapped = 0

            for impl in implementations:
                try:
                    # Skip if no controlID reference
                    if not hasattr(impl, "controlID") or not impl.controlID:
                        continue

                    # Get or cache the security control
                    if impl.controlID not in security_control_cache:
                        security_control = regscale_models.SecurityControl.get_object(object_id=impl.controlID)
                        security_control_cache[impl.controlID] = security_control
                    else:
                        security_control = security_control_cache[impl.controlID]

                    if security_control and hasattr(security_control, "controlId"):
                        # Normalize and cache the control ID mapping
                        normalized_id = self._normalize_control_id_string(security_control.controlId)
                        if normalized_id:
                            self._impl_id_by_control[normalized_id] = impl.id
                            controls_mapped += 1

                            # Also try to cache the most recent assessment
                            try:
                                assessments = regscale_models.Assessment.get_all_by_parent(
                                    parent_id=impl.id, parent_module="controls"
                                )
                                if assessments:
                                    # Get the most recent assessment
                                    assessments.sort(key=lambda a: a.id if hasattr(a, "id") else 0, reverse=True)
                                    self._assessment_by_impl_today[impl.id] = assessments[0]
                                    assessments_mapped += 1
                            except Exception:
                                pass

                except Exception:
                    continue

            logger.info("Control implementation cache populated:")
            logger.info(f"  - {controls_mapped} control ID mappings")
            logger.info(f"  - {assessments_mapped} assessment mappings")

        except Exception as e:
            logger.error(f"Error populating control implementation cache: {e}")

    def _refresh_assessment_cache_after_creation(self) -> None:
        """
        Refresh the assessment cache after control assessments have been created.

        CRITICAL: This ensures that newly created assessments from the sync_control_assessments
        step are available when processing issues. Without this, assessmentId will not be set
        on issues because the cache only contains old assessments.

        :return: None
        :rtype: None
        """
        try:
            from regscale.models import regscale_models
            from datetime import datetime

            logger.info("Refreshing assessment cache with newly created assessments...")

            refreshed_count = 0
            today = datetime.now().date()

            # Only refresh assessments for implementations we know about
            for control_id, impl_id in self._impl_id_by_control.items():
                try:
                    # Get all assessments for this implementation
                    assessments = regscale_models.Assessment.get_all_by_parent(
                        parent_id=impl_id, parent_module="controls"
                    )

                    if not assessments:
                        continue

                    # Find today's assessment (most recent created today)
                    today_assessments = []
                    for assessment in assessments:
                        assessment_date = None
                        try:
                            # Try to get assessment date from various fields
                            date_fields = ["actualFinish", "plannedFinish", "dateCreated"]
                            for field in date_fields:
                                if hasattr(assessment, field) and getattr(assessment, field):
                                    date_value = getattr(assessment, field)
                                    if isinstance(date_value, str):
                                        from regscale.core.app.utils.app_utils import regscale_string_to_datetime

                                        assessment_date = regscale_string_to_datetime(date_value).date()
                                    elif hasattr(date_value, "date"):
                                        assessment_date = date_value.date()
                                    else:
                                        assessment_date = date_value
                                    break

                            if assessment_date == today:
                                today_assessments.append(assessment)
                        except Exception:
                            continue

                    # Use most recent today's assessment, or fallback to most recent overall
                    if today_assessments:
                        best_assessment = max(today_assessments, key=lambda a: getattr(a, "id", 0))
                    else:
                        best_assessment = max(assessments, key=lambda a: getattr(a, "id", 0))

                    # Update the cache
                    self._assessment_by_impl_today[impl_id] = best_assessment
                    refreshed_count += 1

                except Exception:
                    continue

            logger.info(f"Assessment cache refreshed: {refreshed_count} assessments updated")

        except Exception as e:
            logger.error(f"Error refreshing assessment cache: {e}")

    def _find_control_implementation_id(self, control_id: str) -> Optional[int]:
        """
        Find control implementation ID by querying the database directly.
        OPTIMIZED: Uses controlID field directly and caches SecurityControl lookups.

        :param str control_id: Normalized control ID (e.g., 'AC-2(1)')
        :return: Control implementation ID if found
        :rtype: Optional[int]
        """
        try:
            from regscale.models import regscale_models

            # First check cache
            if hasattr(self, "_impl_id_by_control") and control_id in self._impl_id_by_control:
                cached_id = self._impl_id_by_control[control_id]
                return cached_id

            # Get all control implementations for this plan
            implementations = regscale_models.ControlImplementation.get_all_by_parent(
                parent_id=self.plan_id, parent_module=self.parent_module
            )

            # Create a cache for SecurityControl lookups to avoid repeated API calls
            security_control_cache = {}

            for impl in implementations:
                try:
                    # Use controlID field which references the SecurityControl
                    if not hasattr(impl, "controlID") or not impl.controlID:
                        continue

                    # Check if we've already looked up this security control
                    if impl.controlID not in security_control_cache:
                        security_control = regscale_models.SecurityControl.get_object(object_id=impl.controlID)
                        security_control_cache[impl.controlID] = security_control
                    else:
                        security_control = security_control_cache[impl.controlID]

                    if security_control and hasattr(security_control, "controlId"):
                        impl_control_id = self._normalize_control_id_string(security_control.controlId)

                        if impl_control_id == control_id:
                            logger.info(f"Found control implementation {impl.id} for control {control_id}")
                            # Cache it for future lookups
                            if not hasattr(self, "_impl_id_by_control"):
                                self._impl_id_by_control = {}
                            self._impl_id_by_control[control_id] = impl.id
                            return impl.id
                except Exception:
                    continue

            logger.warning(
                f"No control implementation found for control {control_id} among {len(implementations)} implementations"
            )
            return None
        except Exception as e:
            logger.error(f"Error finding control implementation for {control_id}: {e}")
            return None

    def _find_assessment_id_for_implementation(self, implementation_id: int) -> Optional[int]:
        """
        Find the most recent assessment ID for a control implementation.
        IMPROVED: Better date handling and caching.

        :param int implementation_id: Control implementation ID
        :return: Assessment ID if found
        :rtype: Optional[int]
        """
        try:
            from regscale.models import regscale_models
            from datetime import datetime
            from regscale.core.app.utils.app_utils import regscale_string_to_datetime

            # Check cache first
            if hasattr(self, "_assessment_by_impl_today") and implementation_id in self._assessment_by_impl_today:
                cached_assessment = self._assessment_by_impl_today[implementation_id]
                if cached_assessment and hasattr(cached_assessment, "id"):
                    logger.debug(
                        f"Found cached assessment {cached_assessment.id} for implementation {implementation_id}"
                    )
                    return cached_assessment.id

            # Get assessments for this control implementation
            assessments = regscale_models.Assessment.get_all_by_parent(
                parent_id=implementation_id, parent_module="controls"
            )

            if not assessments:
                logger.warning(f"No assessments found for control implementation {implementation_id}")
                return None

            # Find the most recent assessment (preferably from today)
            today = datetime.now().date()
            today_assessments = []
            recent_assessments = []

            for assessment in assessments:
                try:
                    assessment_date = None

                    # Try multiple date fields in order of preference
                    date_fields = ["plannedStart", "actualFinish", "plannedFinish", "dateCreated"]
                    for field in date_fields:
                        if hasattr(assessment, field) and getattr(assessment, field):
                            date_value = getattr(assessment, field)
                            if isinstance(date_value, str):
                                assessment_date = regscale_string_to_datetime(date_value).date()
                            elif hasattr(date_value, "date"):
                                assessment_date = date_value.date()
                            else:
                                assessment_date = date_value
                            break

                    if assessment_date:
                        if assessment_date == today:
                            today_assessments.append(assessment)
                        else:
                            recent_assessments.append((assessment, assessment_date))
                    else:
                        # Assessment with no parseable date
                        recent_assessments.append((assessment, None))
                except Exception:
                    recent_assessments.append((assessment, None))

            # Prefer today's assessments
            if today_assessments:
                # Sort by ID (highest/newest first) if multiple today
                today_assessments.sort(key=lambda a: a.id if hasattr(a, "id") else 0, reverse=True)
                assessment = today_assessments[0]
                logger.info(f"Found today's assessment {assessment.id} for control implementation {implementation_id}")
                # Cache it for future lookups
                if not hasattr(self, "_assessment_by_impl_today"):
                    self._assessment_by_impl_today = {}
                self._assessment_by_impl_today[implementation_id] = assessment
                return assessment.id

            # Fall back to most recent assessment
            if recent_assessments:
                # Sort by date (newest first), handling None dates
                recent_assessments.sort(
                    key=lambda x: (x[1] if x[1] else datetime.min.date(), x[0].id if hasattr(x[0], "id") else 0),
                    reverse=True,
                )
                assessment = recent_assessments[0][0]
                logger.info(f"Found recent assessment {assessment.id} for control implementation {implementation_id}")
                # Cache it even if not today's
                if not hasattr(self, "_assessment_by_impl_today"):
                    self._assessment_by_impl_today = {}
                self._assessment_by_impl_today[implementation_id] = assessment
                return assessment.id

            logger.warning(f"No usable assessments found for control implementation {implementation_id}")
            return None
        except Exception as e:
            logger.error(f"Error finding assessment for control implementation {implementation_id}: {e}")
            return None

    def _reparent_issue_to_asset(self, issue: regscale_models.Issue) -> None:
        """
        Reparent issue to the control implementation instead of the security plan.
        This ensures issues are properly associated with their control implementations.

        :param regscale_models.Issue issue: Issue to reparent to control implementation
        :param IntegrationFinding finding: Finding with control information
        :return: None
        :rtype: None
        """
        # If we have a control implementation ID, parent the issue to it
        if issue.controlId:
            issue.parentId = issue.controlId
            issue.parentModule = "controls"
        else:
            # Fall back to security plan if no control implementation found
            pass

    def _update_scan_history(self, scan_history: regscale_models.ScanHistory) -> None:
        """
        No scan history updates for compliance report ingest.

        :param regscale_models.ScanHistory scan_history: Scan history record (unused)
        """
        # No scan history for compliance report ingest
        pass

    def _process_control_assessments(self) -> None:
        """
        Process control assessments only for controls that have validated compliance items
        with existing assets in RegScale. This ensures we don't create assessments for
        controls that have no assets in our boundary.
        """
        logger.info("Starting control assessment processing for Wiz compliance integration")

        # Ensure existing records cache is loaded
        self._load_existing_records_cache()

        implementations = self._get_control_implementations()
        if not implementations:
            logger.warning("No control implementations found for assessment processing")
            return

        # Get all potential control IDs from compliance data
        all_potential_controls = set(self.passing_controls.keys()) | set(self.failing_controls.keys())
        logger.debug(
            f"Found {len(all_potential_controls)} potential controls from compliance data: {sorted(all_potential_controls)}"
        )

        # Validate each control has actual assets in our boundary before processing
        validated_controls_with_assets = {}
        validated_passing_controls = {}
        validated_failing_controls = {}

        for control_id in all_potential_controls:
            # Get all compliance items for this control
            control_items = self._get_validated_control_compliance_items(control_id)

            if not control_items:
                continue

            # Check if we have any assets for the compliance items
            asset_identifiers = set()
            assets_found = 0

            for item in control_items:
                if hasattr(item, "resource_name") and item.resource_name:
                    resource_id = getattr(item, "resource_id", "")
                    # Verify the asset actually exists in RegScale
                    if self._asset_exists_in_regscale(resource_id):
                        asset_identifiers.add(item.resource_name)
                        assets_found += 1
                    else:
                        logger.debug(
                            f"Control {control_id}: Asset {resource_id} ({item.resource_name}) not found in RegScale"
                        )
            logger.debug(f"Found {assets_found} valid assets for control {control_id}")
            if not asset_identifiers:
                continue

            # This control has valid assets, include it in processing
            validated_controls_with_assets[control_id] = list(asset_identifiers)

            # Preserve the pass/fail status for validated controls
            if control_id in self.failing_controls:
                validated_failing_controls[control_id] = self.failing_controls[control_id]
            elif control_id in self.passing_controls:
                validated_passing_controls[control_id] = self.passing_controls[control_id]

        if not validated_controls_with_assets:
            logger.warning(" No controls have assets in RegScale boundary - no control assessments will be created")
            logger.info("SUMMARY: 0 control assessments created (no assets exist in RegScale)")
            return

        assessments_created = 0
        processed_impl_today: set[int] = set()

        # Only process validated controls that have assets in our boundary
        for control_id in validated_controls_with_assets.keys():
            created = self._process_single_control_assessment(
                control_id=control_id,
                implementations=implementations,
                processed_impl_today=processed_impl_today,
            )
            assessments_created += created

        # Calculate stats only for validated controls
        validated_control_ids = set(validated_controls_with_assets.keys())
        passing_assessments = len([cid for cid in validated_control_ids if cid not in validated_failing_controls])
        failing_assessments = len([cid for cid in validated_control_ids if cid in validated_failing_controls])

        if assessments_created > 0:
            logger.info(
                f"Created {assessments_created} control assessments: {passing_assessments} passing, {failing_assessments} failing"
            )
        else:
            logger.warning(
                f"No control assessments were actually created (0 assessments) despite finding {len(validated_controls_with_assets)} controls with assets"
            )

        logger.info(
            f"CONTROL ASSESSMENT SUMMARY: {assessments_created} assessments created for {len(validated_controls_with_assets)} validated controls"
        )

    def _sync_assessment_cache_from_base_class(self) -> None:
        """
        Sync assessments from base class cache to our control cache.

        This ensures that assessments created by the base class ComplianceIntegration
        are available to our IssueFieldSetter for linking issues to assessments.
        """
        try:
            # Copy assessments from base class cache to our cache
            base_cache = getattr(self, "_assessment_by_impl_today", {})
            synced_count = 0

            for impl_id, assessment in base_cache.items():
                self._control_cache.set_assessment(impl_id, assessment)
                synced_count += 1

            logger.info(f"Synced {synced_count} assessments from base class cache to control cache")

        except Exception as e:
            logger.warning(f"Failed to sync assessment cache: {e}")

    def _get_validated_control_compliance_items(self, control_id: str) -> List[ComplianceItem]:
        """
        Get validated compliance items for a specific control.
        Only returns items that have existing assets in RegScale boundary.

        :param str control_id: Control identifier to filter by
        :return: List of validated compliance items for the control
        :rtype: List[ComplianceItem]
        """
        validated_items: List[ComplianceItem] = []

        for item in self.all_compliance_items:
            # Check if this item matches the control
            matches_control = False
            if hasattr(item, "control_ids"):
                item_control_ids = getattr(item, "control_ids", [])
                if any(cid.lower() == control_id.lower() for cid in item_control_ids):
                    matches_control = True
            elif hasattr(item, "control_id") and item.control_id.lower() == control_id.lower():
                matches_control = True

            if not matches_control:
                continue

            # Additional validation: ensure the asset exists in RegScale
            resource_id = getattr(item, "resource_id", "")
            if resource_id and self._asset_exists_in_regscale(resource_id):
                validated_items.append(item)
            else:
                logger.debug(
                    f"Filtered out compliance item for control {control_id} - asset {resource_id} not in RegScale"
                )

        return validated_items

    def _get_control_compliance_items(self, control_id: str) -> List[ComplianceItem]:
        """
        Get all compliance items for a specific control.
        All items have already been filtered to framework-specific items with existing assets.

        :param str control_id: Control identifier to filter by
        :return: List of compliance items for the control
        :rtype: List[ComplianceItem]
        """
        items: List[ComplianceItem] = []

        for item in self.all_compliance_items:
            # Check if this item matches the control
            matches_control = False
            if hasattr(item, "control_ids"):
                item_control_ids = getattr(item, "control_ids", [])
                if any(cid.lower() == control_id.lower() for cid in item_control_ids):
                    matches_control = True
            elif hasattr(item, "control_id") and item.control_id.lower() == control_id.lower():
                matches_control = True

            if matches_control:
                items.append(item)

        return items

    # flake8: noqa: C901
    def get_asset_by_identifier(self, identifier: str) -> Optional["regscale_models.Asset"]:
        """
        Override asset lookup for Wiz policy compliance integration.

        For policy compliance, the identifier should be the Wiz resource ID.
        We'll try multiple lookup strategies to find the corresponding RegScale asset.

        :param str identifier: Asset identifier (should be Wiz resource ID)
        :return: Asset if found, None otherwise
        :rtype: Optional[regscale_models.Asset]
        """

        # First try the standard lookup by identifier (uses asset_map_by_identifier)
        asset = super().get_asset_by_identifier(identifier)
        if asset:
            return asset

        # If not found, try to find using our cached RegScale assets by Wiz ID
        try:
            if hasattr(self, "_regscale_assets_by_wiz_id") and self._regscale_assets_by_wiz_id:
                # Direct lookup by Wiz ID (most common case)
                if identifier in self._regscale_assets_by_wiz_id:
                    regscale_asset = self._regscale_assets_by_wiz_id[identifier]
                    return regscale_asset

                # Fallback: check all assets for name/identifier matches
                for wiz_id, regscale_asset in self._regscale_assets_by_wiz_id.items():
                    # Check if asset name matches the identifier
                    if regscale_asset.name == identifier:
                        return regscale_asset

                    # Also check identifier field
                    if hasattr(regscale_asset, "identifier") and regscale_asset.identifier == identifier:
                        return regscale_asset

                    # Check other tracking number
                    if (
                        hasattr(regscale_asset, "otherTrackingNumber")
                        and regscale_asset.otherTrackingNumber == identifier
                    ):
                        logger.debug(
                            f"Found asset via otherTrackingNumber match: {regscale_asset.name} (Wiz ID: {wiz_id})"
                        )
                        return regscale_asset

        except Exception:
            pass

        # Asset not found
        return None

    def _ensure_asset_for_finding(self, finding: IntegrationFinding) -> Optional["regscale_models.Asset"]:
        """
        Override asset creation for Wiz policy compliance integration.

        We don't create assets in policy compliance integration - they come from
        separate Wiz inventory import. If an asset isn't found, we skip the finding.

        :param IntegrationFinding finding: Finding that needs an asset
        :return: None (we don't create assets)
        :rtype: Optional[regscale_models.Asset]
        """
        return None

    def _process_consolidated_issues(self, findings: List[IntegrationFinding]) -> None:
        """
        Process pre-consolidated findings to create issues.

        Since fetch_findings() now creates consolidated findings (one per control with all resources),
        this method simply creates issues directly from each finding.

        :param List[IntegrationFinding] findings: List of pre-consolidated findings to process
        """
        if not findings:
            return

        issues_processed = 0

        for finding in findings:
            try:
                control_id = self._normalize_control_id_string(finding.rule_id) or finding.rule_id

                # Create issue title
                issue_title = self.get_issue_title(finding)

                # Create issue directly from the consolidated finding
                issue = self.create_or_update_issue_from_finding(title=issue_title, finding=finding)
                if issue:
                    issues_processed += 1

                else:
                    logger.debug(
                        f"Failed to create issue for control {control_id} - create_or_update_issue_from_finding returned None"
                    )

            except Exception as e:
                logger.error(f"Error processing consolidated issue for control {control_id}: {e}")

        # Store the count for summary reporting
        self._issues_processed_count = issues_processed

    def _find_existing_issue_for_control(self) -> Optional["regscale_models.Issue"]:
        """
        Find existing issue for a specific control.

        :param str control_id: Control ID to search for
        :return: Existing issue if found
        :rtype: Optional[regscale_models.Issue]
        """
        # This is a simplified check - in practice you might want to search by external_id or other fields
        # that uniquely identify control-specific issues
        return None  # For now, always create new issues

    def sync_compliance(self, *args, **kwargs) -> None:
        """Override sync to use consolidated issue processing and add summary reporting."""
        # Initialize issue counter
        self._issues_created_count = 0

        try:
            # Initialize cache dictionaries if not already initialized
            if not hasattr(self, "_impl_id_by_control"):
                self._impl_id_by_control = {}
            if not hasattr(self, "_assessment_by_impl_today"):
                self._assessment_by_impl_today = {}

            # Ensure existing records cache is loaded before processing
            self._load_existing_records_cache()

            # CRITICAL: Pre-populate control implementation cache before any processing
            logger.info("Pre-populating control implementation cache for reliable issue linking...")
            self._populate_control_implementation_cache()

            # Call parent's compliance data processing (assessments, etc.) but skip issue creation
            original_create_issues = self.create_issues
            self.create_issues = False  # Disable base class issue creation
            super().sync_compliance()  # Call the base ComplianceIntegration.sync_compliance method
            self.create_issues = original_create_issues  # Restore setting

            # CRITICAL: Copy assessments from base class cache to our cache so IssueFieldSetter can find them
            self._sync_assessment_cache_from_base_class()

            # Now handle issue creation with consolidated logic
            if self.create_issues:
                findings = list(self.fetch_findings())
                if findings:
                    self._process_consolidated_issues(findings)

            # Provide concise summary
            issues_processed = getattr(self, "_issues_processed_count", 0)

            if issues_processed > 0:
                # Count actual unique issues in the database for this security plan
                from regscale.models import regscale_models

                actual_issues = len(
                    regscale_models.Issue.get_all_by_parent(parent_id=self.plan_id, parent_module=self.parent_module)
                )

                logger.info(
                    f"SUMMARY: Processed {issues_processed} policy violations resulting in {actual_issues} consolidated issues for failed controls for assets in RegScale"
                )
            else:
                logger.info("SUMMARY: No issues processed - no failed controls with existing assets")

        except Exception as e:
            error_and_exit(f"Error during Wiz compliance sync: {e}")

    def _get_regscale_asset_identifier(self, compliance_item: "WizComplianceItem") -> str:
        """
        Get the appropriate RegScale asset identifier for a compliance item.

        For Wiz integrations, the asset_identifier_field is "wizId", so we need to return
        the Wiz resource ID that will match what's stored in the RegScale Asset's wizId field.

        :param WizComplianceItem compliance_item: Compliance item with resource information
        :return: Wiz resource ID that matches the RegScale Asset's wizId field
        :rtype: str
        """
        resource_id = getattr(compliance_item, "resource_id", "")
        resource_name = getattr(compliance_item, "resource_name", "")

        # For Wiz policy compliance, the asset identifier should be the Wiz resource ID
        # because that's what gets stored in RegScale Asset's wizId field (asset_identifier_field = "wizId")
        if resource_id:
            return resource_id

        # Fallback (should not normally happen since resource_id is required)
        return resource_name or "Unknown Resource"

    def _create_consolidated_asset_identifier(self, asset_mappings: Dict[str, Dict[str, str]]) -> str:
        """
        Create a consolidated asset identifier with only asset names (one per line).

        Format: "Asset Name 1\nAsset Name 2\nAsset Name 3"
        This format provides clean, human-readable asset names for POAMs and issues
        without cluttering them with Wiz resource IDs.

        :param Dict[str, Dict[str, str]] asset_mappings: Map of Wiz resource IDs to asset info
        :return: Consolidated identifier string with asset names only
        :rtype: str
        """
        if not asset_mappings:
            return ""

        # Create entries that show only asset names (one per line)
        identifier_parts = []
        # Sort by asset name for consistent ordering
        sorted_mappings = sorted(asset_mappings.items(), key=lambda x: x[1]["name"])
        for wiz_id, asset_info in sorted_mappings:
            asset_name = asset_info["name"]
            wiz_resource_id = asset_info["wiz_id"]

            # Format: Just the asset name (no Wiz resource ID for cleaner POAMs)
            if asset_name != wiz_resource_id:
                # Asset was successfully mapped, show only the name
                identifier_part = asset_name
            else:
                # Asset lookup failed, use the Wiz resource ID as fallback
                identifier_part = wiz_resource_id

            identifier_parts.append(identifier_part)

        # Join with newlines for multi-asset issues
        consolidated_identifier = "\n".join(identifier_parts)
        logger.debug(
            f"Created consolidated asset identifier with {len(identifier_parts)} assets: {consolidated_identifier}"
        )
        return consolidated_identifier


def resolve_framework_id(framework_input: str) -> str:
    """
    Resolve framework input to actual Wiz framework ID.

    Supports:
    - Direct framework IDs (wf-id-4)
    - Shorthand names (nist, aws, soc2)
    - Partial matches (case insensitive)

    :param str framework_input: User input for framework
    :return: Resolved framework ID
    :rtype: str
    :raises ValueError: If framework cannot be resolved
    """
    if not framework_input or not framework_input.strip():
        error_and_exit("Framework input cannot be empty. Use --list-frameworks to see available options.")

    framework_input = framework_input.lower().strip()

    # Direct framework ID
    if framework_input.startswith("wf-id-"):
        if framework_input in FRAMEWORK_MAPPINGS:
            return framework_input
        else:
            error_and_exit(f"Unknown framework ID: {framework_input}")

    # Shorthand lookup
    if framework_input in FRAMEWORK_SHORTCUTS:
        return FRAMEWORK_SHORTCUTS[framework_input]

    # Partial name matching
    for shorthand, framework_id in FRAMEWORK_SHORTCUTS.items():
        if framework_input in shorthand:
            return framework_id

    # Search in full framework names (case insensitive)
    for framework_id, framework_name in FRAMEWORK_MAPPINGS.items():
        if framework_input in framework_name.lower():
            return framework_id

    error_and_exit(f"Could not resolve framework: '{framework_input}'. Use --list-frameworks to see available options.")


def list_available_frameworks() -> str:
    """
    Generate a formatted list of available frameworks.

    :return: Formatted framework list
    :rtype: str
    """
    output = []
    output.append("🔒 Available Wiz Compliance Frameworks")
    output.append("=" * 50)

    # Show shorthand mappings first
    output.append("\nQuick Shortcuts:")
    output.append("-" * 20)
    shortcut_items = sorted(FRAMEWORK_SHORTCUTS.items())
    for shorthand, framework_id in shortcut_items[:10]:  # Show first 10
        framework_name = FRAMEWORK_MAPPINGS.get(framework_id, "Unknown")
        output.append(f"  {shorthand:<15} → {framework_name}")

    if len(shortcut_items) > 10:
        output.append(f"  ... and {len(shortcut_items) - 10} more shortcuts")

    # Show frameworks by category
    output.append("\n📚 All Frameworks by Category:")
    output.append("-" * 35)

    for category, framework_ids in FRAMEWORK_CATEGORIES.items():
        output.append(f"\n🏷️  {category}:")
        for framework_id in framework_ids:
            if framework_id in FRAMEWORK_MAPPINGS:
                framework_name = FRAMEWORK_MAPPINGS[framework_id]
                output.append(f"   {framework_id:<12} → {framework_name}")

    # Usage examples
    output.append("\n💡 Usage Examples:")
    output.append("-" * 18)
    output.append("  # Using shortcuts:")
    output.append("  regscale wiz sync-policy-compliance -f nist")
    output.append("  regscale wiz sync-policy-compliance -f aws")
    output.append("  regscale wiz sync-policy-compliance -f soc2")
    output.append("")
    output.append("  # Using full framework IDs:")
    output.append("  regscale wiz sync-policy-compliance -f wf-id-4")
    output.append("  regscale wiz sync-policy-compliance -f wf-id-197")
    output.append("")
    output.append("  # Using partial names (case insensitive):")
    output.append("  regscale wiz sync-policy-compliance -f 'nist 800-53'")
    output.append("  regscale wiz sync-policy-compliance -f kubernetes")

    return "\n".join(output)
