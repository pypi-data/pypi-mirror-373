"""
Module for processing Grype scan results and loading them into RegScale as assets, issues, and vulnerabilities.
"""

import logging
import traceback
from typing import Any, Iterator, List, Optional

from regscale.core.app.utils.parser_utils import safe_datetime_str
from regscale.exceptions import ValidationException
from regscale.integrations.scanner_integration import IntegrationAsset, IntegrationFinding
from regscale.models import ImportValidater
from regscale.models.integration_models.flat_file_importer import FlatFileImporter
from regscale.models.regscale_models import AssetStatus, IssueSeverity, IssueStatus

logger = logging.getLogger(__name__)


class GrypeImport(FlatFileImporter):
    """Class for handling Grype scanner integration."""

    asset_identifier_field = "otherTrackingNumber"
    finding_severity_map = {
        "CRITICAL": IssueSeverity.Critical.value,
        "HIGH": IssueSeverity.High.value,
        "MEDIUM": IssueSeverity.Moderate.value,
        "LOW": IssueSeverity.Low.value,
        "UNKNOWN": IssueSeverity.High.value,
        "NEGLIGIBLE": IssueSeverity.High.value,
    }
    identifier: Optional[str] = None

    def __init__(self, **kwargs: Any):
        self.name = kwargs.get("name", "Grype")
        self.required_headers = [
            "matches",
        ]
        self.mapping_file = kwargs.get("mappings_path")
        self.disable_mapping = kwargs.get("disable_mapping")
        self.validater = ImportValidater(
            self.required_headers,
            kwargs.get("file_path"),
            self.mapping_file,
            self.disable_mapping,
        )
        self.headers = self.validater.parsed_headers
        self.mapping = self.validater.mapping
        if kwargs.get("scan_date"):
            self.scan_date = kwargs.pop("scan_date")
        else:
            self.scan_date = safe_datetime_str(self.mapping.get_value(self.validater.data, "timestamp"))
        # even if a user doesn't specify a scan_date, we want to remove it from the kwargs and use the scan_date from
        # the attributes after the scan_date is set in the previous logic
        if "scan_date" in kwargs:
            kwargs.pop("scan_date")
        source_target_data = self.mapping.get_value(self.validater.data, "source", {}).get("target", {})

        if "sha256-" in kwargs["file_name"]:
            logger.debug("found sha256 in file name %s", kwargs["file_name"])
            self.identifier = "sha256-" + kwargs["file_name"].split("sha256-")[1].split(".json")[0]
        else:
            logger.debug("using imageID for identifier")
            self.identifier = source_target_data.get("imageID", "Unknown")
        logger.debug("self.identifier: %s", self.identifier)
        self.integration_name = self.identifier
        self.other_tracking_number = source_target_data.get("userInput", "Unknown")
        self.os = source_target_data.get("os", "Linux")
        self.notes = f"{kwargs['file_name']}"
        vuln_count = len(self.mapping.get_value(self.validater.data, "matches", []))
        super().__init__(
            logger=logger,
            headers=self.headers,
            extra_headers_allowed=True,
            finding_severity_map=self.finding_severity_map,
            vuln_func=self.create_vuln,
            asset_func=self.create_asset,
            scan_date=self.scan_date,
            asset_identifier_field=self.asset_identifier_field,
            vuln_count=vuln_count,
            asset_count=1,
            **kwargs,
        )

    def create_asset(self, *args, **kwargs) -> Iterator[IntegrationAsset]:
        """
        Fetches assets from the processed json files

        :yields: Iterator[IntegrationAsset]
        """
        # Get a list of issues from xml node Issues
        if assets := self.fetch_assets(**kwargs):
            for asset in assets:
                yield asset

    def create_vuln(self, *args, **kwargs) -> Iterator[IntegrationFinding]:
        """
        Fetches findings from the processed json files

        :return: A list of findings
        :rtype: List[IntegrationFinding]
        """
        if findings := self.fetch_findings(**kwargs):
            for finding in findings:
                yield finding

    def fetch_findings(self, **_) -> List[IntegrationFinding]:
        """
        Fetch findings from Grype scan data.

        :raises ValidationException: If there is an error fetching/parsing findings
        :return: List of IntegrationFinding
        :rtype: List[IntegrationFinding]
        """

        findings = []
        try:
            for item in self.mapping.get_value(self.validater.data, "matches", []):
                finding = item.get("vulnerability", {})
                cve_id = finding.get("id")
                artifact = item.get("artifact", {})
                cvss = finding.get("cvss", [])
                related_vulns = item.get("relatedVulnerabilities", [])
                description = "No description available"
                if related_vulns:
                    for v in related_vulns:
                        if v.get("id") == cve_id:
                            description = v.get("description", "No description available")
                            cvss = v.get("cvss", [])
                            break

                findings.append(
                    IntegrationFinding(
                        title=artifact.get("name", "unknown"),
                        description=description,
                        severity=(
                            self.process_severity(finding.get("severity"))
                            if finding.get("severity")
                            else IssueSeverity.NotAssigned.value
                        ),
                        status=IssueStatus.Open.value,
                        cvss_v3_score=self.get_cvss_score(cvss_list=cvss),
                        cvss_v3_base_score=self.get_cvss_base_score(cvss_list=cvss),
                        plugin_name=self.name,
                        asset_identifier=self.identifier,
                        cve=finding.get("id"),
                        first_seen=self.scan_date,
                        last_seen=self.scan_date,
                        scan_date=self.scan_date,
                        category="Software",
                        control_labels=[],
                    )
                )
            return findings
        except Exception:
            error_message = traceback.format_exc()
            logger.error(f"Error fetching findings: {error_message}")
            raise ValidationException(f"Error fetching findings: {error_message}")

    def process_severity(self, severity: str) -> str:
        """
        Process the severity of a finding.

        :param str severity: The severity of the finding
        :return: IssueSeverity corresponding to the severity
        :rtype: str
        """
        from regscale.core.app.application import Application

        app = Application()
        severity_default = app.config.get("vulnerabilityMappingDefault", IssueSeverity.NotAssigned.value)
        return self.finding_severity_map.get(severity.upper(), severity_default)

    @staticmethod
    def process_status(status: str) -> str:
        """
        Process the status of a finding.

        :param str status: The status of the finding
        :return: The corresponding Issue status
        :rtype: str
        """
        if status.lower() == "fixed":
            return IssueStatus.Closed.value
        else:
            return IssueStatus.Open.value

    @staticmethod
    def get_cvss_base_score(cvss_list: List) -> float:
        """
        Get the CVSS base score from the vulnerability data.
        :param List cvss_list: List of CVSS objects
        :return: The CVSS base score
        :rtype: float
        """
        v3_base_score = 0.0
        for cvss in cvss_list:
            if cvss.get("type") == "Primary":
                if cvs := cvss.get("metrics"):
                    v3_base_score = cvs.get("baseScore")
                    break
        return v3_base_score

    @staticmethod
    def get_cvss_score(cvss_list: List) -> float:
        """
        Get the CVSS score from the finding data.
        :param List cvss_list: List of CVSS objects
        :return: The CVSS score
        :rtype: float
        """
        value = 0.0
        for cvss in cvss_list:
            if cvss.get("type") == "Primary":
                if cvs := cvss.get("metrics"):
                    if impact_score := cvs.get("impactScore"):
                        value = impact_score
                return value

    def fetch_assets(self, **_) -> List[IntegrationAsset]:
        """
        Fetch assets from Grype scan data.

        :return: List of IntegrationAsset
        :rtype: List[IntegrationAsset]
        """
        assets: List[IntegrationAsset] = []
        try:
            assets.append(
                IntegrationAsset(
                    identifier=self.identifier,
                    name=self.integration_name,
                    ip_address="0.0.0.0",
                    cpu=0,
                    ram=0,
                    status=AssetStatus.Active.value,
                    asset_type="Other",
                    asset_category="Software",
                    operating_system=self.os,
                    notes=self.notes,
                    other_tracking_number=self.other_tracking_number,
                )
            )
            return assets
        except Exception:
            error_message = traceback.format_exc()
            logger.error(f"Error fetching assets: {error_message}")
            raise ValidationException(f"Error fetching assets: {error_message}")
