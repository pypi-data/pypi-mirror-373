"""
Snyk Scan information
"""

from datetime import datetime
from typing import List, Optional, Union

from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import epoch_to_datetime, is_valid_fqdn
from regscale.integrations.scanner_integration import IntegrationAsset, IntegrationFinding
from regscale.models import Asset, AssetCategory, AssetStatus, AssetType, ImportValidater, IssueSeverity, IssueStatus
from regscale.models.integration_models.flat_file_importer import FlatFileImporter


class Snyk(FlatFileImporter):
    """
    Snyk Scan information
    """

    def __init__(self, **kwargs):
        # Group related attributes to reduce instance attribute count
        self.scanner_config = {
            "name": kwargs.get("name"),
            "auto_fixable": "AUTOFIXABLE",
            "fmt": "%Y-%m-%d",
            "dt_format": "%Y-%m-%d %H:%M:%S",
            "not_implemented_error": "Unsupported file type for Snyk integration. Only XLSX and JSON are supported.",
        }
        self.mapping_config = {
            "mapping_file": kwargs.get("mappings_path"),
            "disable_mapping": kwargs.get("disable_mapping"),
        }
        self.file_config = {
            "file_type": kwargs.get("file_type", ""),
        }

        # Set up file-specific configurations
        if "json" in self.file_config["file_type"]:
            self.file_specific_config = {
                "project_name": "projectName",
                "issue_severity": "severity",
                "vuln_title": "title",
                "required_headers": ["projectName", "vulnerabilities"],
            }
        else:
            self.file_specific_config = {
                "project_name": "PROJECT_NAME",
                "issue_severity": "ISSUE_SEVERITY",
                "vuln_title": "PROBLEM_TITLE",
                "required_headers": [
                    "PROJECT_NAME",
                    "ISSUE_SEVERITY",
                    "PROBLEM_TITLE",
                    self.scanner_config["auto_fixable"],
                ],
            }

        self.validater = ImportValidater(
            self.file_specific_config["required_headers"],
            kwargs.get("file_path"),
            self.mapping_config["mapping_file"],
            self.mapping_config["disable_mapping"],
        )
        self.headers = self.validater.parsed_headers
        self.mapping = self.validater.mapping

        # Set counts based on file type
        if "json" in self.file_config["file_type"]:
            asset_count = 1
            vuln_count = len(self.mapping.get_value(self.validater.data, "vulnerabilities", []))
        else:
            asset_count = None
            vuln_count = None

        logger = create_logger()
        self.logger = logger
        super().__init__(
            logger=logger,
            app=Application(),
            headers=self.headers,
            asset_func=self.create_asset,
            vuln_func=self.create_vuln,
            asset_count=asset_count,
            vuln_count=vuln_count,
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
        epoch_time = epoch_to_datetime(self.create_epoch, self.scanner_config["fmt"])
        datetime_obj = datetime.strptime(epoch_time, self.scanner_config["dt_format"])
        return datetime.combine(
            datetime_obj,
            self.mapping.get_value(dat, "FIRST_INTRODUCED", datetime.now().time()),
        ).strftime(self.scanner_config["dt_format"])

    def create_asset(self, dat: Optional[dict] = None) -> Union[Asset, IntegrationAsset]:
        """
        Create an asset from a row in the Snyk file

        :param Optional[dict] dat: Data row from XLSX file or JSON file, defaults to None
        :return: RegScale Asset if XLSX, IntegrationAsset if JSON
        :rtype: Union[Asset, IntegrationAsset]
        """
        if "json" in self.attributes.file_type:
            return self._parse_json_asset(data=dat)
        if "xlsx" in self.attributes.file_type:
            return self._parse_xlsx_asset(dat)
        raise NotImplementedError(self.scanner_config["not_implemented_error"])

    def _create_asset(self, project_name: str) -> IntegrationAsset:
        """
        Helper function to create an IntegrationAsset with common attributes

        :param str project_name: The project name to extract hostname from
        :return: IntegrationAsset object
        :rtype: IntegrationAsset
        """
        name = self.extract_host(project_name)
        valid_name = is_valid_fqdn(name)
        return IntegrationAsset(
            scanning_tool=self.scanner_config["name"],
            identifier=name,
            name=name,
            status=AssetStatus.Active,
            asset_category=AssetCategory.Software,
            asset_type=AssetType.Other,
            fqdn=name if valid_name else None,
        )

    def _parse_xlsx_asset(self, dat: Optional[dict] = None) -> IntegrationAsset:
        """
        Create an asset from a row in the Snyk XLSX file

        :param Optional[dict] dat: Data row from XLSX file, defaults to None
        :return: IntegrationAsset object
        :rtype: IntegrationAsset
        """
        project_name = self.mapping.get_value(dat, self.file_specific_config["project_name"])
        return self._create_asset(project_name)

    def _parse_json_asset(self, **kwargs) -> IntegrationAsset:
        """
        Parse assets from Snyk json scan data.

        :return: Integration asset
        :rtype: IntegrationAsset
        """
        data = kwargs.pop("data")
        project_name = self.mapping.get_value(data, self.file_specific_config["project_name"])
        return self._create_asset(project_name)

    def create_vuln(
        self, dat: Optional[dict] = None, **kwargs
    ) -> Optional[Union[List[IntegrationFinding], IntegrationFinding]]:
        """
        Create a vulnerability from a row in the Snyk file

        :param Optional[dict] dat: Data row from XLSX or JSON file, defaults to None
        :raises TypeError: If dat is not a dictionary
        :return: RegScale Vulnerability object if xlsx or list of IntegrationFindings if JSON
        :rtype: Optional[Union[List[IntegrationFinding], Vulnerability]]
        """
        if "json" in self.attributes.file_type:
            return self._parse_json_findings(**kwargs)
        if "xlsx" in self.attributes.file_type:
            if isinstance(dat, dict):
                return self._parse_xlsx_finding(dat, **kwargs)
            if isinstance(dat, list):
                findings = []
                for finding in dat:
                    findings.extend(self._parse_xlsx_finding(finding, **kwargs))
                return findings
        raise NotImplementedError(self.scanner_config["not_implemented_error"])

    def _create_finding(self, finding_data: dict) -> IntegrationFinding:
        """
        Helper function to create an IntegrationFinding with common attributes

        :param dict finding_data: Dictionary containing finding data
        :return: IntegrationFinding object
        :rtype: IntegrationFinding
        """
        if finding_data.get("title") is None:
            finding_data["title"] = f"{finding_data['description']} on asset {finding_data['hostname']}"

        return IntegrationFinding(
            title=finding_data["title"],
            description=finding_data["description"],
            severity=finding_data["severity"],
            status=IssueStatus.Open.value,
            plugin_name=finding_data["description"],
            plugin_id=finding_data.get("plugin_id"),
            recommendation_for_mitigation=finding_data["solution"],
            plugin_text=self.mapping.get_value(finding_data["dat"], self.file_specific_config["vuln_title"]),
            asset_identifier=finding_data["hostname"],
            cve=finding_data["cve"],
            cvss_score=finding_data.get("cvss_score"),
            first_seen=self.determine_first_seen(finding_data["dat"]),
            last_seen=self.scan_date,
            scan_date=self.scan_date,
            dns=finding_data["hostname"],
            vpr_score=finding_data.get("vpr_score"),
            remediation=finding_data["solution"],
            category="Software",
            control_labels=[],
        )

    def _parse_xlsx_finding(self, dat: Optional[dict] = None, **_) -> List[IntegrationFinding]:
        """
        Create a list of IntegrationFinding objects from a row in the Snyk xlsx file

        :param Optional[dict] dat: Data row from XLSX file, defaults to None
        :return: A list of IntegrationFinding objects
        :rtype: List[IntegrationFinding]
        """
        if not dat:
            return []

        findings: List[IntegrationFinding] = []
        severity = self.determine_severity(
            self.mapping.get_value(dat, self.file_specific_config["issue_severity"]).lower()
        )
        hostname = self.extract_host(self.mapping.get_value(dat, self.file_specific_config["project_name"]))
        description = self.mapping.get_value(dat, self.file_specific_config["vuln_title"])
        solution = self.mapping.get_value(dat, self.scanner_config["auto_fixable"])
        cves = self.mapping.get_value(dat, "CVE", [])

        if cves:
            for cve in cves:
                finding_data = {
                    "dat": dat,
                    "hostname": hostname,
                    "description": description,
                    "severity": severity,
                    "solution": solution,
                    "cve": cve,
                }
                findings.append(self._create_finding(finding_data))
        else:
            finding_data = {
                "dat": dat,
                "hostname": hostname,
                "description": description,
                "severity": severity,
                "solution": solution,
                "cve": "",
            }
            findings.append(self._create_finding(finding_data))
        return findings

    def _extract_json_finding_data(self, dat: dict) -> dict:
        """
        Extract common finding data from JSON vulnerability data

        :param dict dat: The vulnerability data
        :return: Dictionary containing extracted finding data
        :rtype: dict
        """
        severity_key = self.file_specific_config["issue_severity"]
        severity = self.determine_snyk_severity(dat.get(severity_key, "Low").lower())
        project_name = self.file_specific_config["project_name"]
        hostname = self.extract_host(self.mapping.get_value(dat, project_name)) or self.extract_host(
            self.mapping.get_value(self.validater.data, project_name)
        )
        vuln_title = self.file_specific_config["vuln_title"]
        description = self.mapping.get_value(dat, "description") or self.mapping.get_value(dat, vuln_title)
        solution = self.mapping.get_value(dat, self.scanner_config["auto_fixable"])

        # if auto fixable is not available, check for upgradeable or patchable, this is for .json files
        if not solution:
            upgradeable = self.mapping.get_value(dat, "isUpgradeable", False)
            patchable = self.mapping.get_value(dat, "isPatchable", False)
            if upgradeable or patchable:
                solution = "Upgrade or patch the vulnerable component."

        return {
            "severity": severity,
            "hostname": hostname,
            "description": description,
            "solution": solution,
        }

    def _parse_json_findings(self, **kwargs) -> List[IntegrationFinding]:
        """
        Create a list of IntegrationFinding objects from the Snyk json file

        :return: List of IntegrationFinding objects
        :rtype: List[IntegrationFinding]
        """
        findings = []
        vulns = self.mapping.get_value(kwargs.get("data", self.validater.data), "vulnerabilities", [])
        if not vulns:
            return findings

        for dat in vulns:
            finding_data = self._extract_json_finding_data(dat)
            cves = self.mapping.get_value(dat, "CVE", [])
            if not cves:
                cves = dat.get("identifiers", {}).get("CVE", [])

            # Handle multiple CVEs or single CVE
            if cves:
                for cve in cves:
                    finding_data.update(
                        {
                            "dat": dat,
                            "cve": cve,
                            "title": dat.get("title") or finding_data["description"],
                            "plugin_id": dat.get("id"),
                            "cvss_score": dat.get("cvssScore"),
                            "vpr_score": None,
                        }
                    )
                    findings.append(self._create_finding(finding_data))
            else:
                finding_data.update(
                    {
                        "dat": dat,
                        "cve": "",
                        "title": dat.get("title") or finding_data["description"],
                        "plugin_id": dat.get("id"),
                        "cvss_score": dat.get("cvssScore"),
                        "vpr_score": None,
                    }
                )
                findings.append(self._create_finding(finding_data))

        return findings

    @staticmethod
    def extract_host(s: str) -> str:
        """
        Extract the host from the project name

        :param str s: The project name
        :return: The host
        :rtype: str
        """
        try:
            res = (s.split("|"))[1].split("/")[0]
        except IndexError:
            res = s
        return res
