#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Finding processing and consolidation logic for Wiz Policy Compliance."""

import logging
from typing import Dict, List, Optional, Iterator, Any, Set, Union
from collections import defaultdict

from regscale.integrations.scanner_integration import IntegrationFinding
from regscale.integrations.commercial.wizv2.policy_compliance_helpers import AssetConsolidator
from regscale.models import regscale_models

logger = logging.getLogger("regscale")


class WizComplianceItem:
    """Interface representing a compliance item from the main class."""

    def __init__(self, compliance_item: Any) -> None:
        """
        Initialize wrapper for compliance item.

        :param compliance_item: The compliance item object to wrap
        """
        self._item = compliance_item

    @property
    def resource_id(self) -> str:
        return getattr(self._item, "resource_id", "")

    @property
    def control_id(self) -> str:
        return getattr(self._item, "control_id", "")

    @property
    def is_fail(self) -> bool:
        return getattr(self._item, "is_fail", False)

    def get_all_control_ids(self) -> List[str]:
        """
        Get all control IDs this item maps to.

        :return: List of control IDs this policy assessment affects
        """
        # This would be implemented by the main class
        if hasattr(self._item, "_get_all_control_ids_for_compliance_item"):
            return self._item._get_all_control_ids_for_compliance_item(self._item)
        return [self.control_id] if self.control_id else []


class FindingConsolidator:
    """Consolidates multiple compliance items into control-centric findings."""

    def __init__(self, integration_instance: Any) -> None:
        """
        Initialize the finding consolidator.

        :param integration_instance: The Wiz integration instance
        """
        self.integration = integration_instance
        self.asset_consolidator = AssetConsolidator()

    def create_consolidated_findings(self, failed_compliance_items: List[Any]) -> Iterator[IntegrationFinding]:
        """
        Create consolidated findings grouped by control ID.

        :param failed_compliance_items: List of failed compliance items
        :yield: Consolidated findings
        """
        if not failed_compliance_items:
            logger.debug("No failed compliance items to process")
            return

        logger.debug("Starting control-centric finding consolidation")

        # Group compliance items by control ID
        control_groups = self._group_by_control(failed_compliance_items)

        if not control_groups:
            logger.debug("No control groupings created")
            return

        logger.debug(f"Grouped into {len(control_groups)} controls with failing resources")

        # Create consolidated findings for each control
        findings_created = 0
        for control_id, resources in control_groups.items():
            finding = self._create_consolidated_finding_for_control(control_id, resources)
            if finding:
                findings_created += 1
                yield finding

        logger.debug(f"Generated {findings_created} consolidated findings")

    def _group_by_control(self, compliance_items: List[Any]) -> Dict[str, Dict[str, Any]]:
        """
        Group compliance items by control ID.

        :param compliance_items: List of compliance items to group
        :return: Dict mapping control IDs to resource dictionaries
        """
        control_groups = defaultdict(dict)  # {control_id: {resource_id: compliance_item}}

        for item in compliance_items:
            wrapped_item = WizComplianceItem(item)
            resource_id = wrapped_item.resource_id

            if not resource_id:
                continue

            # Get all control IDs this item maps to
            all_control_ids = wrapped_item.get_all_control_ids()
            if not all_control_ids:
                continue

            # Add this resource to each control it fails
            for control_id in all_control_ids:
                normalized_control = control_id.upper()
                resource_key = resource_id.lower()

                # Use first occurrence for each resource-control pair
                if resource_key not in control_groups[normalized_control]:
                    control_groups[normalized_control][resource_key] = item

        return dict(control_groups)

    def _create_consolidated_finding_for_control(
        self, control_id: str, resources: Dict[str, Any]
    ) -> Optional[IntegrationFinding]:
        """
        Create a consolidated finding for a control with all affected resources.

        :param control_id: Control identifier
        :param resources: Dict of resource_id -> compliance_item
        :return: Consolidated finding or None
        """
        logger.debug(f"Creating consolidated finding for control {control_id} with {len(resources)} resources")

        # Filter to only resources that exist as assets in RegScale
        asset_mappings = self._build_asset_mappings(list(resources.keys()))

        if not asset_mappings:
            logger.debug(f"No existing assets found for control {control_id}")
            return None

        logger.debug(f"Creating finding for control {control_id} with {len(asset_mappings)} existing assets")

        # Use the first compliance item as the base for the finding
        base_item = next(iter(resources.values()))

        # Create the base finding
        finding = self._create_base_finding(base_item, control_id)
        if not finding:
            return None

        # Update with consolidated asset information
        self._update_finding_with_assets(finding, asset_mappings)

        return finding

    def _build_asset_mappings(self, resource_ids: List[str]) -> Dict[str, Dict[str, str]]:
        """
        Build asset mappings for resources that exist in RegScale.

        :param resource_ids: List of Wiz resource IDs to check
        :return: Dict mapping resource_ids to asset info (name, wiz_id)
        """
        asset_mappings = {}

        for resource_id in resource_ids:
            if self.integration._asset_exists_in_regscale(resource_id):
                asset = self.integration.get_asset_by_identifier(resource_id)
                if asset and hasattr(asset, "name") and asset.name:
                    asset_mappings[resource_id] = {"name": asset.name, "wiz_id": resource_id}
                else:
                    # Fallback to resource ID if asset name not found
                    asset_mappings[resource_id] = {"name": resource_id, "wiz_id": resource_id}

        return asset_mappings

    def _create_base_finding(self, compliance_item: Any, control_id: str) -> Optional[IntegrationFinding]:
        """Create a base finding from a compliance item for a specific control."""
        try:
            # Use the integration's existing method but for specific control
            if hasattr(self.integration, "_create_finding_for_specific_control"):
                return self.integration._create_finding_for_specific_control(compliance_item, control_id)
            else:
                # Fallback to generic method
                return self.integration.create_finding_from_compliance_item(compliance_item)
        except Exception as e:
            logger.error(f"Error creating base finding for control {control_id}: {e}")
            return None

    def _update_finding_with_assets(
        self, finding: IntegrationFinding, asset_mappings: Dict[str, Dict[str, str]]
    ) -> None:
        """
        Update finding with consolidated asset information.

        :param finding: Finding to update
        :param asset_mappings: Asset mapping information
        """
        # Update asset identifier with all assets
        consolidated_identifier = self.asset_consolidator.create_consolidated_asset_identifier(asset_mappings)
        finding.asset_identifier = consolidated_identifier

        # Update description for multiple assets
        asset_names = [info["name"] for info in asset_mappings.values()]
        self.asset_consolidator.update_finding_description_for_multiple_assets(finding, len(asset_names), asset_names)


class FindingToIssueProcessor:
    """Processes findings into RegScale issues."""

    def __init__(self, integration_instance: Any) -> None:
        """
        Initialize the finding to issue processor.

        :param integration_instance: The Wiz integration instance
        """
        self.integration = integration_instance

    def process_findings_to_issues(self, findings: List[IntegrationFinding]) -> tuple[int, int]:
        """
        Process findings into issues and return counts.

        :param findings: List of consolidated findings to process
        :return: Tuple of (issues_created, issues_skipped)
        """
        issues_created = 0
        issues_skipped = 0

        for finding in findings:
            try:
                if self._process_single_finding(finding):
                    issues_created += 1
                else:
                    issues_skipped += 1
            except Exception as e:
                logger.error(f"Error processing finding: {e}")
                issues_skipped += 1

        return issues_created, issues_skipped

    def _process_single_finding(self, finding: IntegrationFinding) -> bool:
        """
        Process a single finding into an issue.

        :param finding: Finding to process
        :return: True if successful, False if skipped
        """
        # Verify assets exist
        if not self._verify_assets_exist(finding):
            logger.debug(f"Asset not found for finding {finding.external_id}")
            return False

        # Create or update the issue
        try:
            issue_title = self.integration.get_issue_title(finding)
            issue = self.integration.create_or_update_issue_from_finding(title=issue_title, finding=finding)
            return issue is not None
        except Exception as e:
            logger.error(f"Error creating/updating issue: {e}")
            return False

    def _verify_assets_exist(self, finding: IntegrationFinding) -> bool:
        """
        Verify that assets referenced in the finding exist.

        :param finding: Finding with asset identifiers to verify
        :return: True if all assets exist in RegScale, False otherwise
        """
        if not hasattr(finding, "asset_identifier") or not finding.asset_identifier:
            return False

        # For consolidated findings, asset_identifier may contain multiple assets
        identifiers = finding.asset_identifier.split("\n")

        for identifier in identifiers:
            identifier = identifier.strip()
            if not identifier:
                continue

            # Extract resource ID from format "Asset Name (resource-id)"
            if "(" in identifier and identifier.endswith(")"):
                resource_id = identifier.split("(")[-1].rstrip(")")
            else:
                resource_id = identifier

            # Check if asset exists
            if not self.integration._asset_exists_in_regscale(resource_id):
                logger.debug(f"Asset {resource_id} does not exist in RegScale")
                return False

        return True
