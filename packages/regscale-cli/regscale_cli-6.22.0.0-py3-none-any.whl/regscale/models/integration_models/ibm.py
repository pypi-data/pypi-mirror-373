"""
IBM Scan information
"""

from typing import Optional
from urllib.parse import urlparse

from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import epoch_to_datetime, get_current_datetime, is_valid_fqdn
from regscale.integrations.scanner_integration import IntegrationAsset, IntegrationFinding
from regscale.models import ImportValidater
from regscale.models.integration_models.flat_file_importer import FlatFileImporter
from regscale.models.regscale_models import Asset, IssueSeverity, IssueStatus

ISSUE_TYPE = "Issue Type"
VULNERABILITY_TITLE = ISSUE_TYPE
VULNERABILITY_ID = ISSUE_TYPE


class AppScan(FlatFileImporter):
    """
    IBM Scan information
    """

    severity_map = {
        "Critical": "critical",
        "High": "high",
        "Medium": "medium",
        "Low": "low",
        "Informational": "low",
    }

    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.vuln_title = VULNERABILITY_TITLE
        self.vuln_id = VULNERABILITY_ID
        logger = create_logger()
        self.required_headers = ["URL"]
        self.mapping_file = kwargs.get("mappings_path")
        self.disable_mapping = kwargs.get("disable_mapping")
        self.validater = ImportValidater(
            self.required_headers, kwargs.get("file_path"), self.mapping_file, self.disable_mapping, ignore_unnamed=True
        )
        self.headers = self.validater.parsed_headers
        self.mapping = self.validater.mapping
        super().__init__(
            logger=logger,
            app=Application(),
            headers=self.headers,
            asset_func=self.create_asset,
            vuln_func=self.create_vuln,
            extra_headers_allowed=True,
            **kwargs,
        )

    def create_asset(self, dat: Optional[dict] = None) -> IntegrationAsset:
        """
        Create an asset from a row in the IBM csv file

        :param Optional[dict] dat: Data row from CSV file, defaults to None
        :return: RegScale IntegrationAsset object
        :rtype: IntegrationAsset
        """
        parsed_url = urlparse(self.mapping.get_value(dat, "URL"))
        hostname: str = f"{parsed_url.scheme}://{parsed_url.netloc}"
        return IntegrationAsset(
            **{
                "name": hostname,
                "identifier": hostname,
                "status": "Active (On Network)",
                "asset_category": "Software",
                "scanning_tool": self.name,
                "asset_type": "Other",
                "fqdn": hostname if is_valid_fqdn(hostname) else None,
            }
        )

    def create_vuln(self, dat: Optional[dict] = None, **kwargs) -> Optional[IntegrationFinding]:
        """
        Create an IntegrationFinding from a row in the IBM csv file
        :param Optional[dict] dat: Data row from CSV file, defaults to None
        :return: RegScale IntegrationFinding object or None
        :rtype: Optional[IntegrationFinding]
        """

        regscale_vuln = None
        parsed_url = urlparse(self.mapping.get_value(dat, "URL"))
        hostname: str = f"{parsed_url.scheme}://{parsed_url.netloc}"
        description: str = self.mapping.get_value(dat, ISSUE_TYPE)
        app_scan_severity = self.mapping.get_value(dat, "Severity")
        severity = self.severity_map.get(app_scan_severity, "Informational")
        if dat:
            return IntegrationFinding(
                title=self.mapping.get_value(dat, self.vuln_title),
                description=description,
                cve="",
                severity=self.determine_severity(severity),
                asset_identifier=hostname,
                plugin_name=description,
                plugin_text=description[:255],
                control_labels=[],
                category="Hardware",
                status=IssueStatus.Open,
                last_seen=get_current_datetime(),
                first_seen=epoch_to_datetime(self.create_epoch),
            )
        return regscale_vuln
