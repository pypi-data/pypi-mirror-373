"""
ECR Scan information
"""

from typing import List, Optional, Union

from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.integrations.scanner_integration import IntegrationAsset, IntegrationFinding
from regscale.models import ImportValidater
from regscale.models.integration_models.flat_file_importer import FlatFileImporter
from regscale.models.regscale_models import AssetStatus, IssueSeverity, IssueStatus
from regscale.models.regscale_models.asset import Asset


class ECR(FlatFileImporter):
    """ECR Scan information"""

    def __init__(self, **kwargs):
        # Group related attributes to reduce instance attribute count
        self.scanner_config = {
            "name": kwargs.get("name"),
            "vuln_title": "name",
            "fmt": "%m/%d/%y",
            "dt_format": "%Y-%m-%d %H:%M:%S",
            "image_name": "Name",
        }
        self.mapping_config = {
            "mapping_file": kwargs.get("mappings_path"),
            "disable_mapping": kwargs.get("disable_mapping"),
        }
        self.file_config = {
            "file_type": kwargs.get("file_type"),
            "raw_dict": {},
        }
        self.required_headers = [self.scanner_config["image_name"]]
        keys = ["imageScanFindings", "findings"] if self.file_config["file_type"] == ".json" else None
        self.validater = ImportValidater(
            self.required_headers,
            kwargs.get("file_path"),
            self.mapping_config["mapping_file"],
            self.mapping_config["disable_mapping"],
            keys=keys,
        )
        self.headers = self.validater.parsed_headers
        self.mapping = self.validater.mapping
        logger = create_logger()
        super().__init__(
            logger=logger,
            app=Application(),
            headers=self.headers,
            asset_func=self.create_asset,
            vuln_func=self.create_vuln,
            **kwargs,
        )

    def create_asset(self, dat: Optional[dict] = None) -> IntegrationAsset:
        """
        Create an integration asset from a row in the ECR file

        :param Optional[dict] dat: Data row from file, defaults to None
        :return: RegScale IntegrationAsset object
        :rtype: IntegrationAsset
        """
        name = self.mapping.get_value(dat, "Name") or self.mapping.get_value(dat, "name")
        if repository_name := self.mapping.get_value(
            dat, "repositoryName", self.file_config["raw_dict"].get("repositoryName", "")
        ):
            image_id_data = self.file_config["raw_dict"].get("imageId", {}).get("imageDigest", "").split(":")
            if image_id_data and len(image_id_data) > 1:
                image_id = image_id_data[1]
            else:
                image_id = image_id_data[0]
            name = f"{repository_name}:{image_id}"

        # Check if string has a forward slash
        return IntegrationAsset(
            identifier=name,
            name=name,
            ip_address="0.0.0.0",
            cpu=0,
            ram=0,
            scanning_tool=self.scanner_config["name"],
            status=AssetStatus.Active.value,
            asset_type="Other",
            asset_category="Software",
            operating_system="Linux",
        )

    def create_vuln(
        self, dat: Optional[dict] = None, **_kwargs
    ) -> Union[IntegrationFinding, List[IntegrationFinding], None]:
        """
        Create a finding from a row in the ECR csv file

        :param Optional[dict] dat: Data row from file, defaults to None
        :return: RegScale IntegrationFinding object, a list of RegScale IntegrationFinding objects or None
        :rtype: Union[IntegrationFinding, List[IntegrationFinding], None]
        """
        vulns: List[IntegrationFinding] = []
        hostname = dat.get("Name") or dat.get("name")
        if repository_name := self.mapping.get_value(
            dat, "repositoryName", self.file_config["raw_dict"].get("repositoryName", "")
        ):
            image_id_data = self.file_config["raw_dict"].get("imageId", {}).get("imageDigest", "").split(":")
            if len(image_id_data) > 1:
                image_id = image_id_data[1]
            else:
                image_id = image_id_data[0]
            hostname = f"{repository_name}:{image_id}"
        if dat.get("imageScanFindings"):
            vulns = self.process_json_vulns(dat, hostname)
        else:
            single_vuln = self.process_csv_vulns(dat, hostname)
            if single_vuln:
                return single_vuln
        return vulns

    def create_finding(self, finding_data: dict) -> IntegrationFinding:
        """
        Create an IntegrationFinding from finding data

        :param dict finding_data: Dictionary containing finding data
        :return: The IntegrationFinding
        :rtype: IntegrationFinding
        """
        title = f"{finding_data['cve']} on asset {finding_data['hostname']}"
        return IntegrationFinding(
            title=title,
            dns=finding_data["hostname"],
            description=finding_data["cve"],
            severity=self.determine_severity(finding_data["severity"]),
            status=IssueStatus.Open.value,
            plugin_name=finding_data["cve"],
            plugin_id=finding_data["cve"],
            plugin_text=finding_data["description"],
            asset_identifier=finding_data["hostname"],
            cve=finding_data["cve"],
            first_seen=self.scan_date,
            last_seen=self.scan_date,
            scan_date=self.scan_date,
            category="Software",
            control_labels=[],
        )

    def process_csv_vulns(self, dat: dict, hostname: str) -> Optional[IntegrationFinding]:
        """
        Process the CSV findings from the ECR scan

        :param dict dat: The data from the ECR scan
        :param str hostname: The hostname
        :return: The vulnerability or None
        :rtype: Optional[IntegrationFinding]

        """
        cve = dat.get("CVE", "")
        severity = self.determine_severity(dat.get("Severity", "Info"))
        finding_data = {
            "hostname": hostname,
            "cve": cve,
            "severity": severity,
            "description": dat.get("uri", ""),
        }
        return self.create_finding(finding_data)

    def process_json_vulns(self, dat: dict, hostname: str) -> List[IntegrationFinding]:
        """
        Process the JSON findings from the ECR scan

        :param dict dat: The data from the ECR scan
        :param str hostname: The hostname
        :return: The list of vulnerabilities
        :rtype: List[IntegrationFinding]
        """
        vulns: List[IntegrationFinding] = []
        if findings := dat.get("imageScanFindings", {}).get("findings"):
            for finding in findings:
                cve = finding.get("name")
                severity = self.determine_severity(finding["severity"])
                finding_data = {
                    "hostname": hostname,
                    "cve": cve,
                    "severity": severity,
                    "description": finding.get("uri", ""),
                }
                vuln = self.create_finding(finding_data)
                vulns.append(vuln)
        return vulns
