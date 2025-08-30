"""
Module for processing Trivy scan results and loading them into RegScale as assets, issues, and vulnerabilities.
"""

import logging
import traceback
from typing import Any, Dict, Iterator, List, Optional

from regscale.core.app.utils.parser_utils import safe_datetime_str
from regscale.exceptions import ValidationException
from regscale.integrations.scanner_integration import IntegrationAsset, IntegrationFinding
from regscale.models import ImportValidater
from regscale.models.integration_models.flat_file_importer import FlatFileImporter
from regscale.models.regscale_models import AssetStatus, IssueSeverity, IssueStatus

logger = logging.getLogger(__name__)


class TrivyImport(FlatFileImporter):
    """Class for handling Trivy scanner integration."""

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
        self.name = kwargs.get("name", "Trivy")
        self.identifier = None
        self.required_headers = [
            "Metadata",
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
            self.scan_date = safe_datetime_str(self.validater.data.get("CreatedAt"))
        # even if a user doesn't specify a scan_date, we want to remove it from the kwargs and use the scan_date from
        # the attributes after the scan_date is set in the previous logic
        if "scan_date" in kwargs:
            kwargs.pop("scan_date")
        if "sha256-" in kwargs["file_name"]:
            logger.debug("found sha256 in file name %s", kwargs["file_name"])
            self.identifier = "sha256-" + kwargs["file_name"].split("sha256-")[1].split(".json")[0]
        else:
            logger.debug("using imageID for identifier")
            self.identifier = self.mapping.get_value(self.validater.data, "Metadata", {}).get("ImageID")
        logger.debug("self.identifier: %s", self.identifier)
        self.integration_name = self.identifier
        self.other_tracking_number = self.mapping.get_value(self.validater.data, "ArtifactName", self.identifier)
        self.notes = f"{kwargs['file_name']}"
        vuln_count = 0
        for item in self.mapping.get_value(self.validater.data, "Results", []):
            vuln_count += len(item.get("Vulnerabilities", []))
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

    def parse_asset(self, **kwargs) -> IntegrationAsset:
        """
        Parse assets from Trivy scan data.

        :return: Integration asset
        :rtype: IntegrationAsset
        """
        os_data = kwargs.pop("os_data")
        return IntegrationAsset(
            identifier=self.identifier,
            name=self.integration_name,
            ip_address="0.0.0.0",
            cpu=0,
            ram=0,
            status=AssetStatus.Active.value,
            asset_type="Other",
            asset_category="Software",
            operating_system=f"{os_data.get('Family', '')} {os_data.get('Name', '')}",
            notes=self.notes,
            other_tracking_number=self.other_tracking_number,
        )

    def create_asset(self, *args, **kwargs) -> Iterator[IntegrationAsset]:
        """
        Fetches assets from the processed json files

        :yields: Iterator[IntegrationAsset]
        """
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
        Fetch findings from Trivy scan data.

        :raises ValidationException: If there is an error fetching/parsing findings
        :return: List of IntegrationFinding
        :rtype: List[IntegrationFinding]
        """

        findings = []
        try:
            for item in self.mapping.get_value(self.validater.data, "Results", []):
                for finding in item.get("Vulnerabilities", []):
                    findings.append(
                        IntegrationFinding(
                            title=finding.get("Title", finding.get("PkgName")),
                            description=finding.get("Description", "No description available"),
                            severity=(
                                self.process_severity(finding.get("Severity"))
                                if finding.get("Severity")
                                else IssueSeverity.NotAssigned.value
                            ),
                            status=IssueStatus.Open.value,
                            cvss_v3_score=self.get_cvss_score(finding),
                            cvss_v3_base_score=self.get_cvss_score(finding),
                            plugin_name=finding.get("DataSource", {}).get("Name", self.name),
                            plugin_id=finding.get("DataSource", {}).get("ID", self.name),
                            asset_identifier=self.identifier,
                            cve=finding.get("VulnerabilityID"),
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
    def get_cvss_score(finding: Dict) -> float:
        """
        Get the CVSS score from the finding data.

        :param dict finding: The finding data
        :return: The CVSS score
        :rtype: float
        """
        value = 0.0
        if cvs := finding.get("CVSS"):
            if nvd := cvs.get("nvd"):
                value = nvd.get("V3Score", 0.0)
            elif redhat := cvs.get("redhat"):
                value = redhat.get("V3Score", 0.0)
        return value

    def fetch_assets(self, **_) -> List[IntegrationAsset]:
        """
        Fetch assets from Trivy scan data.

        :raises ValidationException: If there is an error fetching/parsing assets
        :return: List of IntegrationAsset
        :rtype: List[IntegrationAsset]
        """
        data = self.validater.data
        assets: List[IntegrationAsset] = []
        os_data = self.mapping.get_value(data, "Metadata", {}).get("OS", {})
        try:
            assets.append(self.parse_asset(asset=data, os_data=os_data))
            return assets
        except Exception:
            error_message = traceback.format_exc()
            logger.error(f"Error fetching assets: {error_message}")
            raise ValidationException(f"Error fetching assets: {error_message}")
