#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RegScale GCP Package"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from google.cloud.securitycenter_v1 import Finding
    from google.cloud.securitycenter_v1.services.security_center.pagers import ListFindingsPager
    from google.cloud import asset_v1

import copy
from typing import List, Optional

import click

from regscale.core.utils.date import default_date_format
from regscale.integrations.commercial.gcp.auth import (
    get_gcp_security_center_client,
    get_gcp_asset_service_client,
)
from regscale.integrations.commercial.gcp.control_tests import gcp_control_tests
from regscale.integrations.commercial.gcp.variables import GcpVariables
from regscale.integrations.scanner_integration import (
    logger,
    IntegrationFinding,
    ScannerIntegration,
    IntegrationAsset,
)
from regscale.models import regscale_models


@click.group()
def gcp():
    """GCP Integrations"""


@gcp.command(name="sync_findings")
@click.option(
    "--regscale_ssp_id",
    type=click.INT,
    help="The ID number from RegScale of the System Security Plan",
    prompt="Enter RegScale System Security Plan ID",
    required=True,
)
def sync_findings(regscale_ssp_id):
    """Sync GCP Findings to RegScale."""
    GCPScannerIntegration.sync_findings(plan_id=regscale_ssp_id)


@gcp.command(name="sync_assets")
@click.option(
    "--regscale_ssp_id",
    type=click.INT,
    help="The ID number from RegScale of the System Security Plan",
    prompt="Enter RegScale System Security Plan ID",
    required=True,
)
def sync_assets(regscale_ssp_id):
    """Sync GCP Assets to RegScale."""
    GCPScannerIntegration.sync_assets(plan_id=regscale_ssp_id)


class GCPScannerIntegration(ScannerIntegration):
    title = "GCP Scanner Integration"
    asset_identifier_field = "googleIdentifier"
    gcp_control_tests: dict[str, dict[str, dict[str, str]]] = {}
    finding_severity_map = {
        0: regscale_models.IssueSeverity.Low,
        1: regscale_models.IssueSeverity.Critical,
        2: regscale_models.IssueSeverity.High,
        3: regscale_models.IssueSeverity.Moderate,
        4: regscale_models.IssueSeverity.Low,
    }

    @staticmethod
    def get_failed_findings() -> "ListFindingsPager":
        """
        Fetches GCP findings using the SecurityCenterClient

        :raises NameError: If gcpFindingSources is set incorrectly
        :return: A list of parsed findings
        :rtype: ListFindingsPager
        """
        from google.api_core.exceptions import InvalidArgument  # Optimize import performance

        logger.info("Fetching GCP findings...")

        if str(GcpVariables.gcpScanType) == "project":  # type: ignore
            sources = f"projects/{GcpVariables.gcpProjectId}/sources/-"
        else:
            sources = f"organizations/{GcpVariables.gcpOrganizationId}/sources/-"
        try:
            client = get_gcp_security_center_client()
            gcp_findings = client.list_findings(request={"parent": sources})
            logger.info("Fetched GCP findings.")
            return gcp_findings
        except InvalidArgument:
            error_msg = f"gcpFindingSources is set incorrectly: {sources}."
            logger.error(error_msg)
            raise NameError(error_msg)

    def get_passed_findings(self) -> List[IntegrationFinding]:
        """
        Gets passed findings for from the GCP control tests

        :return: A list of passed findings
        :rtype: List[IntegrationFinding]
        """
        passed_findings = []
        self.gcp_control_tests = copy.copy(gcp_control_tests)

        for control_label, categories in self.gcp_control_tests.items():
            for category, control_test in categories.items():
                if control_test.get("status", "") == "Failed":
                    logger.debug(
                        f"Control {control_label} had findings in category {category}, "
                        f"skipping passed control test creation"
                    )
                    continue
                passed_findings.append(
                    IntegrationFinding(
                        control_labels=[control_label.lower()],
                        title=f"{self.title} Control Assessment",
                        category=category,
                        description=control_test.get("description", ""),
                        severity=regscale_models.IssueSeverity.Low,
                        status=regscale_models.ControlTestResultStatus.PASS,
                        impact=regscale_models.IssueSeverity.Low,
                        plugin_name=category,
                    )
                )
        return passed_findings

    def fetch_findings(self, **kwargs) -> List[IntegrationFinding]:
        """
        Fetches GCP findings using the SecurityCenterClient

        :return: A list of parsed findings
        :rtype: List[IntegrationFinding]
        """
        gcp_findings = self.get_failed_findings()

        self.gcp_control_tests = copy.copy(gcp_control_tests)
        failed_findings = list(filter(None, [self.parse_finding(finding.finding) for finding in gcp_findings]))
        passed_findings = self.get_passed_findings()
        return failed_findings + passed_findings

    def parse_finding(self, gcp_finding: "Finding") -> Optional[IntegrationFinding]:
        """
        Parses GCP findings

        :param Finding gcp_finding: The GCP finding to parse
        :return: The parsed IntegrationFinding
        :rtype: Optional[IntegrationFinding]
        """
        from google.cloud.securitycenter_v1 import Finding  # Optimize import performance

        if any(
            control_labels := [
                label.lower() for c in gcp_finding.compliances if c.standard == "nist" for label in c.ids
            ]
        ):
            control_labels = [label.lower() for label in control_labels]

            # Set control test status to failed since we found a finding for it
            for control_label in control_labels:
                # Ensure control_id is a string when used as a key
                control_label = str(control_label)
                if self.gcp_control_tests.get(control_label, {}).get(gcp_finding.category):
                    self.gcp_control_tests[control_label][gcp_finding.category]["status"] = "Failed"

            severity = self.finding_severity_map.get(
                gcp_finding.severity, regscale_models.IssueSeverity.Low
            )  # Default to Low
            return IntegrationFinding(
                control_labels=control_labels,
                title=f"{self.title} Control Assessment",
                category=gcp_finding.category,
                description=gcp_finding.description,
                severity=severity,
                status=regscale_models.ControlTestResultStatus.FAIL,
                external_id=gcp_finding.external_uri,
                gaps=f"Resource out of compliance: {gcp_finding.resource_name}\n"
                f"Recommendation: {gcp_finding.source_properties.get('Recommendation', '')}",
                observations=gcp_finding.source_properties.get("Explanation", ""),
                evidence=Finding.to_json(gcp_finding),
                identified_risk=gcp_finding.source_properties.get("Explanation", ""),
                impact=severity,
                recommendation_for_mitigation=gcp_finding.source_properties.get("Recommendation", ""),
                plugin_name=gcp_finding.category,
            )
        logger.info(f"Finding {gcp_finding.name} has no NIST controls.")
        return None

    def fetch_assets(self):
        """
        Fetches GCP assets using the AssetServiceClient

        :yields: Iterator[IntegrationAsset]
        """
        from google.cloud import asset_v1  # Optimize import performance

        logger.info("Fetching GCP assets...")
        client = get_gcp_asset_service_client()
        if str(GcpVariables.gcpScanType) == "project":  # type: ignore
            sources = f"projects/{GcpVariables.gcpProjectId}"
        else:
            sources = f"organizations/{GcpVariables.gcpOrganizationId}"
        request = asset_v1.ListAssetsRequest(parent=sources)  # type: ignore
        logger.info("Fetched GCP assets.")
        self.num_assets_to_process = 0
        for asset in client.list_assets(request=request):
            self.num_assets_to_process += 1
            yield self.parse_asset(asset)

    def parse_asset(self, asset: "asset_v1.Asset") -> IntegrationAsset:
        """
        Parses GCP assets

        :param asset_v1.Asset asset: The GCP asset to parse
        :return: The parsed IntegrationAsset
        :rtype: IntegrationAsset
        """
        from google.cloud import asset_v1  # type: ignore  # Optimize import performance

        return IntegrationAsset(
            name=asset.name,
            identifier=asset.name,
            asset_type=asset.asset_type,
            asset_owner_id=self.assessor_id,
            parent_id=self.plan_id,
            parent_module=regscale_models.SecurityPlan.get_module_slug(),
            asset_category="GCP",
            date_last_updated=asset.update_time.strftime(default_date_format),
            component_names=[asset.asset_type],
            status="Active (On Network)",
        )
