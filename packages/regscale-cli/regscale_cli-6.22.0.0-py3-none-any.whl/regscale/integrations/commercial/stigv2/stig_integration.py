#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RegScale STIG Integration
"""
import datetime
import logging
from typing import Iterator, Optional, Generator, TYPE_CHECKING

from regscale.core.app.utils.app_utils import error_and_exit

if TYPE_CHECKING:
    from regscale.integrations.scanner_integration import IntegrationAsset, IntegrationFinding

from pathlib import Path

from regscale.core.utils.date import date_str, days_from_today
from regscale.integrations.commercial.stigv2.ckl_parser import (
    parse_checklist,
    find_stig_files,
    Checklist,
    Vuln,
    STIG,
)
from regscale.integrations.scanner_integration import (
    logger,
    ScannerIntegration,
    ScannerIntegrationType,
)
from regscale.models import regscale_models


logger = logging.getLogger("regscale")


class StigIntegration(ScannerIntegration):
    options_map_assets_to_components = True

    title = "STIG Integration"
    asset_identifier_field = "fqdn"
    type = ScannerIntegrationType.CHECKLIST
    checklist_status_map = {
        "NotAFinding": regscale_models.ChecklistStatus.PASS,
        "Open": regscale_models.ChecklistStatus.FAIL,
    }
    finding_severity_map = {
        "critical": regscale_models.IssueSeverity.Critical,
        "high": regscale_models.IssueSeverity.High,
        "medium": regscale_models.IssueSeverity.Moderate,
        "low": regscale_models.IssueSeverity.Low,
    }

    def fetch_findings(self, path: Path, **kwargs) -> Generator["IntegrationFinding", None, None]:  # type: ignore
        """
        Fetches GCP findings using the SecurityCenterClient

        :param Path path: The path to the STIG files, defaults to None
        :yields IntegrationFinding: An IntegrationFinding object for each finding
        :return: A list of parsed findings
        :rtype: Generator[IntegrationFinding, None, None]
        """

        logger.info("Fetching findings...")
        stig_files = find_stig_files(path)

        self.num_findings_to_process = 0
        for stig_file in stig_files:
            logger.info(f"Processing '{stig_file}'")
            checklist = parse_checklist(stig_file)
            logger.info(f"Found {len(checklist.stigs[0].vulns)} Vulnerabilities in '{stig_file}'")
            self.num_findings_to_process += len(checklist.stigs[0].vulns)
            for stig in checklist.stigs:
                for vuln in stig.vulns:
                    for finding in self.process_vulnerabilities(checklist, vuln, stig):
                        yield finding

    def process_vulnerabilities(
        self, checklist: Checklist, vuln: Vuln, stig: STIG
    ) -> Generator["IntegrationFinding", None, None]:
        """
        Processes vulnerabilities for each asset in the checklist.

        Iterates through each asset in the provided checklist, extracts the asset identifier (host_fqdn),
        and yields an IntegrationFinding for each vulnerability associated with the asset.

        :param Checklist checklist: The checklist containing assets to process.
        :param Vuln vuln: The vulnerability information to be processed.
        :param STIG stig: The STIG information to be processed.
        :return: An iterator of IntegrationFinding objects.
        :rtype: Generator[IntegrationFinding, None, None]
        :yields: An IntegrationFinding object for each asset in the checklist.
        :ytype: IntegrationFinding
        """
        for asset in checklist.assets:
            asset_identifier = getattr(asset, "host_fqdn", None)
            if not asset_identifier:
                self.log_error(f"Failed to extract host_fqdn from Asset: {asset} and vuln from {vuln}")
                continue

            yield from self.create_integration_finding(asset_identifier, vuln, stig)

    def create_integration_finding(
        self, asset_identifier: str, vuln: Vuln, stig: STIG
    ) -> Generator["IntegrationFinding", None, None]:
        """
        Creates an IntegrationFinding object from the provided asset identifier and vulnerability information.

        :param str asset_identifier: The identifier of the asset associated with the finding.
        :param Vuln vuln: The vulnerability information used to populate the finding.
        :param STIG stig: The STIG information used to populate the finding.
        :return: An iterator of IntegrationFinding objects populated with the provided information.
        :rtype: Generator[IntegrationFinding, None, None]
        :yields: An IntegrationFinding object for each asset in the checklist.
        :ytype: IntegrationFinding
        """
        from regscale.integrations.scanner_integration import IntegrationFinding

        severity = self.get_finding_severity(vuln.severity)
        due_date_map = {
            regscale_models.IssueSeverity.Critical: date_str(days_from_today(30)),
            regscale_models.IssueSeverity.High: date_str(days_from_today(60)),
            regscale_models.IssueSeverity.Moderate: date_str(days_from_today(210)),
            regscale_models.IssueSeverity.Low: date_str(days_from_today(364)),
        }
        if not vuln.cci_ref:
            vuln.cci_ref = ["CCI-000366"]

        for cci_ref in vuln.cci_ref:
            yield IntegrationFinding(
                asset_identifier=asset_identifier,
                control_labels=[],  # Determine how to populate this
                title=f"{vuln.rule_title} {vuln.rule_ver} {stig.stig_info.releaseinfo} {vuln.vuln_num}",
                issue_title=f"{vuln.rule_title} {vuln.rule_ver} {stig.stig_info.releaseinfo} {vuln.vuln_num}",
                category=vuln.group_title,
                severity=severity,
                description=f"{vuln.check_content} {vuln.vuln_discuss} {vuln.fix_text}",
                status=self.get_finding_status(vuln.status),
                checklist_status=self.get_checklist_status(vuln.status),
                external_id=f"{cci_ref}:{vuln.vuln_num}:{asset_identifier}",
                vulnerability_number=vuln.vuln_num,
                cci_ref=cci_ref,
                rule_id=vuln.rule_id,
                rule_version=vuln.rule_ver,
                results=f"Vulnerability Number: {vuln.vuln_num}, Severity: {vuln.severity}, "
                f"Rule Title: {vuln.rule_title}<br><br>Check Content: {vuln.check_content}<br><br>"
                f"Fix Text: {vuln.fix_text}<br><br>STIG Reference: {vuln.stigref}<br><br>"
                f"Vulnerability Discussion: {vuln.vuln_discuss}",
                recommendation_for_mitigation=vuln.fix_text,
                comments=vuln.comments,
                poam_comments=vuln.finding_details,
                date_created=date_str(datetime.datetime.now()),
                due_date=due_date_map.get(severity, date_str(days_from_today(394))),
                baseline=stig.baseline,
                plugin_name=vuln.rule_id,
                observations=vuln.finding_details or "",
                gaps=vuln.check_content or "",
                evidence=vuln.check_content or "",
                impact=vuln.potential_impact or "",
            )

    @staticmethod
    def get_component_names(checklist: Checklist, component_title: Optional[str] = None) -> list[str]:
        """
        Extracts component names from the checklist and STIG.

        :param Checklist checklist: The checklist containing assets to process.
        :param Optional[str] component_title: The title of the component to filter by, defaults to None
        :return: A list of component names associated with the STIG.
        :rtype: list[str]
        """
        component_names = []
        if component_title:
            component_names.append(component_title)
        else:
            for stig in checklist.stigs:
                component_names.append(stig.component_title)
        return component_names

    def should_process_asset(
        self, stig_asset: regscale_models.Asset, is_component: bool, component_names: Optional[list[str]] = None
    ) -> bool:
        """
        Determines if an asset should be processed based on the provided parameters.

        :param Asset stig_asset: The asset to be processed.
        :param bool is_component: Whether the asset is a component.
        :param Optional[list[str]] component_names: The list of component names to filter by, defaults to None
        :return: True if the asset should be processed, False otherwise.
        :rtype: bool
        """
        if not stig_asset.host_name and not stig_asset.host_fqdn:
            self.log_error(f"Failed to extract asset from {stig_asset}")
            return False
        elif is_component and not component_names:
            return False
        return True

    def fetch_assets(self, path: Optional[Path] = None, **kwargs) -> Iterator["IntegrationAsset"]:
        """
        Fetches GCP assets using the AssetServiceClient

        :param Optional[Path] path: The path to the STIG files, defaults to None
        :raises ValueError: If no path is provided
        :yield: An IntegrationAsset object representing an Assest extracted from a STIG file
        :ytype: IntegrationAsset
        :return: An iterator of parsed assets
        :rtype: Iterator[IntegrationAsset]
        """
        from regscale.integrations.scanner_integration import IntegrationAsset

        if not path:
            raise ValueError("Path to STIG files is required.")
        logger.info("Fetching assets...")
        stig_files = find_stig_files(path)
        component_title = ""
        if is_component := kwargs.get("is_component", False):
            from regscale.validation.record import validate_regscale_object

            if not validate_regscale_object(parent_id=self.plan_id, parent_module="components"):
                raise error_and_exit("The provided Component ID is not valid.")
            component = regscale_models.Component.get_object(self.plan_id)
            component_title = component.title
        self.num_assets_to_process = len(stig_files)

        loading_stig_files = self.asset_progress.add_task(
            f"[#f8b737]Loading {len(stig_files)} STIG files.",
            total=len(stig_files),
        )
        for stig_file in stig_files:
            logger.info(f"Processing '{stig_file}'")
            checklist = parse_checklist(stig_file)
            for stig_asset in checklist.assets:
                component_names = self.get_component_names(checklist, component_title)

                if not self.should_process_asset(stig_asset, is_component, component_names):
                    continue

                yield IntegrationAsset(
                    name=stig_asset.host_name or stig_asset.host_fqdn,
                    ip_address=stig_asset.host_ip,
                    fqdn=stig_asset.host_fqdn or stig_asset.host_name,
                    identifier=stig_asset.host_fqdn,
                    asset_type=stig_asset.asset_type,
                    asset_owner_id=self.assessor_id,
                    parent_id=self.plan_id,
                    parent_module=(
                        regscale_models.Component.get_module_slug()
                        if kwargs.get("is_component", False)
                        else regscale_models.SecurityPlan.get_module_slug()
                    ),
                    asset_category=regscale_models.AssetCategory.Hardware,
                    component_names=component_names,
                    # TODO: Determine correct component type
                    component_type=regscale_models.ComponentType.Hardware,
                )
            self.asset_progress.update(loading_stig_files, advance=1)
