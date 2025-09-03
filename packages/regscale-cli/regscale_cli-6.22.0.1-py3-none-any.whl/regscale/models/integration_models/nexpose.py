"""
Nexpose Scan information
"""

from typing import Optional

from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import epoch_to_datetime, is_valid_fqdn
from regscale.core.utils.date import date_str
from regscale.integrations.scanner_integration import IntegrationAsset, IntegrationFinding
from regscale.models import ImportValidater
from regscale.models.integration_models.flat_file_importer import FlatFileImporter
from regscale.models.regscale_models import Asset, IssueSeverity, IssueStatus

VULNERABILITY_TITLE = "Vulnerability Title"
VULNERABILITY_ID = "Vulnerability ID"
CVSS3_SCORE = "CVSSv3 Score"
CVSS2_SCORE = "CVSSv2 Score"
IP_ADDRESS = "IP_Address"
FIRST_SEEN = "first_seen"
SCAN_DATE = "scan_start_time"
CVE = "CVEs"


class Nexpose(FlatFileImporter):  # pylint: disable=too-many-instance-attributes
    """
    Nexpose Scan information
    """

    def __init__(self, **kwargs):  # pylint: disable=R0902
        self.name = kwargs.get("name")
        self.vuln_title = VULNERABILITY_TITLE
        self.vuln_id = VULNERABILITY_ID
        self.cvss3_score = CVSS3_SCORE
        self.first_seen = FIRST_SEEN
        self.scan_date_field = SCAN_DATE
        self.cve = CVE
        self.required_headers = [
            "Hostname",
            "Vulnerability Title",
            "Vulnerability ID",
            "CVSSv2 Score",
            "CVSSv3 Score",
            "Description",
            "Solution",
            "CVEs",
        ]
        self.mapping_file = kwargs.get("mappings_path")
        self.disable_mapping = kwargs.get("disable_mapping")
        self.validater = ImportValidater(
            self.required_headers, kwargs.get("file_path"), self.mapping_file, self.disable_mapping
        )
        self.headers = self.validater.parsed_headers
        self.mapping = self.validater.mapping
        logger = create_logger()
        super().__init__(
            logger=logger,
            app=Application(),
            headers=self.mapping.to_header(),
            asset_func=self.create_asset,
            vuln_func=self.create_vuln,
            extra_headers_allowed=True,
            **kwargs,
        )

    def create_asset(self, dat: Optional[dict] = None) -> Optional[IntegrationAsset]:
        """
        Create an asset from a row in the Nexpose csv file

        :param Optional[dict] dat: Data row from CSV file, defaults to None
        :return: RegScale IntegrationAsset object, if it has a hostname
        :rtype: Optional[IntegrationAsset]
        """
        if hostname := self.mapping.get_value(dat, "Hostname"):
            return IntegrationAsset(
                **{
                    "name": hostname,
                    "ip_address": self.mapping.get_value(dat, IP_ADDRESS, "0.0.0.0"),
                    "identifier": hostname,
                    "other_tracking_number": hostname,
                    "status": "Active (On Network)",
                    "asset_category": "Hardware",
                    "asset_type": "Other",
                    "scanning_tool": self.name,
                    "fqdn": hostname if is_valid_fqdn(hostname) else None,
                    "operating_system": Asset.find_os(self.mapping.get_value(dat, "OS")),
                }
            )
        return None

    @staticmethod
    def determine_severity_from_cvss_score(cvss_score: float, cvss_version: str = "v3") -> IssueSeverity:
        """
        Determine CVSS Severity Text from CVSS Base Score

        :param float cvss_score: CVSS Base Score
        :param str cvss_version: CVSS version ("v2" or "v3"), defaults to "v3"
        :return: CVSS Severity Text
        :rtype: IssueSeverity
        """
        results = IssueSeverity.Low

        if cvss_version.lower() == "v3":
            # CVSSv3 severity ranges
            if 4.0 <= cvss_score <= 6.9:
                results = IssueSeverity.Moderate
            elif 7.0 <= cvss_score <= 8.9:
                results = IssueSeverity.High
            elif cvss_score > 8.9:
                results = IssueSeverity.Critical
        elif cvss_version.lower() == "v2":
            # CVSSv2 severity ranges
            if 4.0 <= cvss_score <= 6.9:
                results = IssueSeverity.Moderate
            elif 7.0 <= cvss_score <= 10.0:
                results = IssueSeverity.High
            # CVSSv2 doesn't have a "Critical" category, High is the highest

        return results

    def severity_from_text(self, text_severity: str) -> Optional[IssueSeverity]:
        """
        Determine severity from text severity

        :param str text_severity: Text severity
        :return: IssueSeverity or None
        :rtype: Optional[IssueSeverity]
        """
        if text_severity.lower() == "low":
            return IssueSeverity.Low
        if text_severity.lower() in ["medium", "moderate"]:
            return IssueSeverity.Moderate
        if text_severity.lower() == "high":
            return IssueSeverity.High
        if text_severity.lower() in ["critical", "severe"]:
            return IssueSeverity.Critical
        return None

    def _determine_severity(self, dat: Optional[dict] = None) -> IssueSeverity:
        """
        Determine severity using the priority order: text severity > CVSSv3 > CVSSv2 > default

        :param Optional[dict] dat: Data row from CSV file, defaults to None
        :return: Determined IssueSeverity
        :rtype: IssueSeverity
        """
        # Default severity
        severity = IssueSeverity.Low

        # Extract CVSS scores
        cvss3_score = self.mapping.get_value(dat, self.cvss3_score) or 0.0
        cvss2_score = self.mapping.get_value(dat, CVSS2_SCORE) or 0.0

        # Priority 1: Check for text-based severity (client-specific)
        # This is client specific, need to be able to override the severity source
        text_severity = self.severity_from_text(
            self.mapping.get_value(dat, "adobe_severity")
        ) or self.severity_from_text(self.mapping.get_value(dat, "nexpose_severity"))

        if text_severity:
            severity = text_severity
        else:
            # Priority 2: Use CVSSv3 score if available and valid
            if cvss3_score and cvss3_score > 0:
                severity = self.determine_severity_from_cvss_score(float(cvss3_score), "v3")
            # Priority 3: Fall back to CVSSv2 score if available and valid
            elif cvss2_score and cvss2_score > 0:
                severity = self.determine_severity_from_cvss_score(float(cvss2_score), "v2")

        return severity

    def create_vuln(self, dat: Optional[dict] = None, **kwargs) -> Optional[IntegrationFinding]:
        """
        Create an IntegrationFinding from a row in the Prisma/Nexpose csv file

        :param Optional[dict] dat: Data row from CSV file, defaults to None
        :param kwargs: Additional keyword arguments
        :return: RegScale IntegrationFinding object or None
        :rtype: Optional[IntegrationFinding]
        """
        regscale_finding = None

        # Extract basic data
        hostname: str = self.mapping.get_value(dat, "Hostname")
        description: str = self.mapping.get_value(dat, "Description")
        cvss3_score = self.mapping.get_value(dat, self.cvss3_score) or 0.0

        # Determine severity using priority logic
        severity = self._determine_severity(dat)

        # Find matching asset

        # Extract date information
        first_seen = (
            self.mapping.get_value(dat, self.first_seen)
            or self.mapping.get_value(dat, "first_seen")
            or epoch_to_datetime(self.create_epoch)
        )

        if scan_date := self.mapping.get_value(dat, SCAN_DATE):
            self.scan_date = scan_date
        cvss_score = self.mapping.get_value(dat, CVSS2_SCORE)

        # Create IntegrationFinding if we have valid data and asset match
        if dat:
            return IntegrationFinding(
                control_labels=[],  # Add an empty list for control_labels
                title=self.mapping.get_value(dat, self.vuln_title),
                description=description,
                cve=self.mapping.get_value(dat, self.cve, "").upper(),
                severity=severity,
                asset_identifier=hostname,
                plugin_name=self.mapping.get_value(dat, self.vuln_title),
                plugin_id=str(self.mapping.get_value(dat, self.vuln_id)),
                cvss_score=cvss_score or 0.0,
                cvss_v3_score=cvss3_score or 0.0,
                cvss_v2_score=cvss_score or 0.0,
                plugin_text=description[:255],
                remediation=self.mapping.get_value(dat, "Solution"),
                category="Hardware",
                status=IssueStatus.Open,
                first_seen=self.scan_date or date_str(first_seen),
                scan_date=date_str(scan_date) or self.scan_date,
                vulnerability_type="Vulnerability Scan",
                baseline=f"{self.name} Host",
            )
        return regscale_finding
