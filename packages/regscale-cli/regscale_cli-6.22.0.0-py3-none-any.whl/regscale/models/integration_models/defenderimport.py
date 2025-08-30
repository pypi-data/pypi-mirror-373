"""
Integration model to import data from Defender .csv export
"""

import json
from typing import Iterator, List, Optional

from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import is_valid_fqdn
from regscale.core.utils.date import datetime_obj, datetime_str
from regscale.integrations.scanner_integration import IntegrationAsset, IntegrationFinding
from regscale.models import Asset, ImportValidater, IssueSeverity, IssueStatus
from regscale.models.integration_models.flat_file_importer import FlatFileImporter


class DefenderImport(FlatFileImporter):
    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.vuln_title = "SUBASSESSMENTNAME"
        self.vuln_id = "SUBASSESSMENTID"
        logger = create_logger()
        self.fmt = "%Y-%m-%d"
        self.dt_format = "%Y-%m-%d %H:%M:%S"
        self.required_headers = [
            "SEVERITY",
            self.vuln_title,
            self.vuln_id,
        ]
        self.mapping_file = kwargs.get("mappings_path")
        self.disable_mapping = kwargs.get("disable_mapping")
        self.validater = ImportValidater(
            self.required_headers, kwargs.get("file_path"), self.mapping_file, self.disable_mapping
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

    def determine_first_seen(self, dat: dict) -> str:
        """
        Determine the first seen date of the vulnerability

        :param dict dat: Data row from CSV file
        :return: The first seen date as a string
        :rtype: str
        """
        # Remove the 'Z' at the end
        iso_string = self.mapping.get_value(dat, "TIMEGENERATED", "").rstrip("Z")

        # Convert to datetime object
        dt_object = datetime_obj(iso_string)

        return datetime_str(dt_object, self.dt_format)

    def create_asset(self, dat: Optional[dict] = None) -> IntegrationAsset:
        """
        Create an asset from a row in the Snyk file

        :param Optional[dict] dat: Data row from CSV file, defaults to None
        :return: RegScale Asset object
        :rtype: Asset
        """
        additional_data = json.loads(self.mapping.get_value(dat, "ADDITIONALDATA", {}))
        os = Asset.find_os(additional_data.get("imageDetails", {}).get("osDetails", ""))
        name = additional_data.get("repositoryName", "")
        valid_name = is_valid_fqdn(name)
        return IntegrationAsset(
            identifier=name,
            name=name,
            ip_address="0.0.0.0",
            status="Active (On Network)",
            asset_category="Software",
            scanning_tool=self.name,
            asset_type="Other",
            fqdn=name if valid_name else None,
            operating_system=os,
        )

    def create_vuln(self, dat: Optional[dict] = None, **kwargs: dict) -> Iterator[IntegrationFinding]:
        """
        Create a vulnerability from a row in the Snyk csv file

        :param Optional[dict] dat: Data row from CSV file, defaults to None
        :param dict **kwargs: Additional keyword arguments
        :return: RegScale Iterator of findings
        :rtype: Iterator[IntegrationFinding]
        """
        regscale_findings: List[IntegrationFinding] = []
        severity = self.determine_severity(self.mapping.get_value(dat, "SEVERITY", "").lower())
        additional_data = json.loads(self.mapping.get_value(dat, "ADDITIONALDATA", {}))
        hostname = additional_data.get("repositoryName", "")
        description = self.mapping.get_value(dat, self.vuln_title)
        solution = self.mapping.get_value(dat, self.vuln_id)
        cves = [cve.get("title", "") for cve in additional_data.get("cve", [])]
        cvss_v3_score = float(additional_data.get("cvssV30Score", 0))
        if dat:
            if cves and isinstance(cves, list):
                for cve in cves:
                    regscale_finding = IntegrationFinding(
                        title=f"{description} on asset {hostname}",
                        asset_identifier=hostname,
                        description=description,
                        severity=severity,
                        status=IssueStatus.Open.value,
                        cvss_v3_score=cvss_v3_score,
                        cvss_v3_base_score=cvss_v3_score,
                        plugin_name=description,
                        plugin_text=self.mapping.get_value(dat, self.vuln_title),
                        cve=cve,
                        recommendation_for_mitigation=solution,
                        first_seen=self.determine_first_seen(dat),
                        last_seen=self.scan_date,
                        scan_date=self.scan_date,
                        category="Software",
                        control_labels=[],
                    )
                    regscale_findings.append(regscale_finding)
            else:
                regscale_finding = IntegrationFinding(
                    title=f"{description} on asset {hostname}",
                    description=description,
                    severity=severity,
                    status=IssueStatus.Open.value,
                    cvss_v3_score=cvss_v3_score,
                    cvss_v3_base_score=cvss_v3_score,
                    plugin_name=description,
                    plugin_text=self.mapping.get_value(dat, self.vuln_title),
                    asset_identifier=hostname,
                    cve=self.mapping.get_value(dat, self.vuln_title),
                    recommendation_for_mitigation=solution,
                    first_seen=self.determine_first_seen(dat),
                    last_seen=self.scan_date,
                    scan_date=self.scan_date,
                    category="Software",
                    control_labels=[],
                )
                regscale_findings.append(regscale_finding)

        yield from regscale_findings
