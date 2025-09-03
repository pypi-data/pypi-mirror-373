from typing import List, Optional, Union

from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.integrations.scanner_integration import IntegrationAsset, IntegrationFinding
from regscale.models import Asset, ImportValidater, IssueStatus, Vulnerability
from regscale.models.integration_models.flat_file_importer import FlatFileImporter

APP_NAME = "@app_name"
VERSION = "@version"
ACCOUNT_ID = "@account_id"


class Veracode(FlatFileImporter):
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "Veracode")
        logger = create_logger()
        self.vuln_title = "PROBLEM_TITLE"
        self.fmt = "%Y-%m-%d"
        self.dt_format = "%Y-%m-%d %H:%M:%S"
        xlsx_headers = [
            "Source",
        ]
        xml_headers = [
            "app_name",
        ]
        json_headers = [
            "findings",
            "project_name",
        ]
        self.mapping_file = kwargs.get("mappings_path")
        self.disable_mapping = kwargs.get("disable_mapping")
        file_type = kwargs.get("file_type")
        xml_tag = None
        if "xml" in file_type:
            self.required_headers = xml_headers
            xml_tag = "detailedreport"
        elif "xlsx" in file_type:
            self.required_headers = xlsx_headers
        else:
            self.required_headers = json_headers
        self.validater = ImportValidater(
            self.required_headers, kwargs.get("file_path"), self.mapping_file, self.disable_mapping, xml_tag=xml_tag
        )
        self.headers = self.validater.parsed_headers
        self.mapping = self.validater.mapping
        if file_type == ".json":
            self.asset_identifier = self.mapping.get_value(self.validater.data, "project_name", "")
        super().__init__(
            logger=logger,
            headers=self.headers,
            asset_func=self.create_asset,
            vuln_func=self.create_vuln,
            extra_headers_allowed=False,
            **kwargs,
        )

    def create_asset(self, dat: Optional[dict] = None) -> List[Asset]:
        """
        Create a RegScale asset from an asset  in the Veracode export file

        :param Optional[dict] dat: The data from the Veracode export file
        :return: List of RegScale Asset objects
        :rtype: List[Asset]
        """
        version = None
        # Veracode is a Web Application Security Scanner, so these will be software assets, scanning a
        # single web application
        if "xml" in self.attributes.file_type:
            detailed_report_data = dat.get("detailedreport", {})
            name = detailed_report_data.get(APP_NAME, "")
            account_id = detailed_report_data.get(ACCOUNT_ID, "")
            version = detailed_report_data.get(VERSION, "")
        elif "json" in self.attributes.file_type:
            name = self.mapping.get_value(dat, "project_name", "")
            account_id = self.asset_identifier
        else:
            name = self.mapping.get_value(dat, "Source", "")
            account_id = str(self.mapping.get_value(dat, "ID", ""))
        asset = IntegrationAsset(
            **{
                "name": name,
                "ip_address": "0.0.0.0",
                "identifier": name,
                "other_tracking_number": account_id,
                "status": "Active (On Network)",
                "asset_category": "Hardware",
                "software_vendor": "Veracode",
                "software_name": name,
                "software_version": version,
                "asset_type": "Other",
                "scanning_tool": self.name,
            }
        )
        return [asset]

    def create_vuln(
        self, dat: Optional[dict] = None, **kwargs
    ) -> Union[List[IntegrationFinding], List[IntegrationFinding]]:
        """
        Create a RegScale vulnerability from a vulnerability in the Veracode export file

        :param Optional[dict]  dat: The data from the Veracode export file
        :return: List of RegScale Vulnerability objects
        :rtype: List[Vulnerability]
        """
        # Veracode is a Web Application Security Scanner, so these will be software assets,
        # scanning a single web application
        if "xml" in self.attributes.file_type:
            detailed_report_data = dat.get("detailedreport", {})
            name = detailed_report_data.get(APP_NAME, "")
            all_sev_data = detailed_report_data.get("severity", [])
            severity = self.severity_info(all_sev_data)[0] if all_sev_data else "low"
            if severity_data := self.severity_info(all_sev_data):
                if isinstance(severity_data, tuple) and len(severity_data) >= 2:
                    cwes = [
                        f"{c.get('@cweid')} {c.get('@cwename')}" for c in severity_data[1].get("cwe", [])
                    ]  # Multiple cwes per asset in official XML
            else:
                cwes = []
        elif "xlsx" in self.attributes.file_type:
            name = self.mapping.get_value(dat, "Source", "")
            severity = self.mapping.get_value(dat, "Sev", "").lower()
            cwes = [self.mapping.get_value(dat, "CWE ID & Name", [])]  # Coalfire should flatten data for asset -> cwes
        elif "json" in self.attributes.file_type:
            return self._parse_json_findings(**kwargs)

        return self.process_vuln_data(name, cwes, severity)

    def _parse_json_findings(self, **kwargs) -> List[IntegrationFinding]:
        """
        Parse the JSON findings from the Veracode .json export file

        :return: List of IntegrationFinding objects
        :rtype: List[IntegrationFinding]
        """
        findings: List[IntegrationFinding] = []
        for vuln in self.mapping.get_value(kwargs.get("data", self.validater.data), "findings", []):
            if title := vuln.get("issue_type", vuln.get("title", "")):
                findings.append(
                    IntegrationFinding(
                        title=title,
                        description=vuln.get("display_text", "No description available"),
                        severity=self.finding_severity_map.get(self.hit_mapping().get(vuln.get("severity", 0)), "Low"),
                        status=IssueStatus.Open,
                        plugin_name=vuln.get(title, self.name),
                        plugin_id=vuln.get("cwe_id", vuln.get("issue_id", "")),
                        plugin_text=vuln.get("issue_type", ""),
                        asset_identifier=self.asset_identifier,
                        first_seen=self.scan_date,
                        last_seen=self.scan_date,
                        scan_date=self.scan_date,
                        category="Software",
                        is_cwe=True,
                        control_labels=[],
                    )
                )
        return findings

    def process_vuln_data(self, hostname: str, cwes: List[str], severity: str) -> List[Vulnerability]:
        """
        Process the vulnerability data to create a list of vulnerabilities

        :param str hostname: The hostname
        :param List[str] cwes: The CWEs
        :param str severity: The severity
        :return: A list of vulnerabilities
        :rtype: List[Vulnerability]
        """
        vulns = []
        for cwe in cwes:
            severity = self.determine_severity(severity)
            if asset := self.get_asset(hostname):
                vuln = self.create_vulnerability_object(asset, hostname, cwe, severity, "")
                vulns.append(vuln)
        return vulns

    def create_vulnerability_object(
        self, asset: Asset, hostname: str, cwe: str, severity: str, description: str
    ) -> IntegrationFinding:
        """
        Create a vulnerability from a row in the Veracode file

        :param Asset asset: The asset
        :param str hostname: The hostname
        :param str cwe: The CWE
        :param str severity: The severity
        :param str description: The description
        :return: The equivalent IntegrationFinding object
        :rtype: IntegrationFinding
        """
        return IntegrationFinding(
            title=f"{cwe} on asset {asset.name}",
            description=description,
            status=IssueStatus.Open,
            dns=hostname,
            first_seen=self.scan_date,
            last_seen=self.scan_date,
            scan_date=self.scan_date,
            category="Software",
            is_cwe=True,
            severity=self.finding_severity_map.get(self.hit_mapping().get(severity.title(), "Low")),
            plugin_name=cwe,
            plugin_id=cwe,
            plugin_text=description,
            asset_identifier=hostname,
            control_labels=[],
        )

    def get_asset(self, hostname: str) -> Optional[Asset]:
        """
        Get the asset from the hostname

        :param str hostname: The hostname
        :return: The asset, if found
        :rtype: Optional[Asset]
        """
        asset_match = [asset for asset in self.data["assets"] if asset.name == hostname]
        return asset_match[0] if asset_match else None

    def severity_info(self, severity_list: list) -> Optional[tuple]:
        """
        Get the severity level and category of the vulnerability

        :param list severity_list: List of severity levels
        :return: Severity level and category
        :rtype: Optional[tuple]
        """
        hit = [sev for sev in severity_list if sev.get("category")]
        if hit:
            return (self.hit_mapping().get(hit[0].get("level"), "low"), hit[0].get("category"))
        return None

    @staticmethod
    def hit_mapping() -> dict:
        """
        Mapping of severity levels

        :return: Mapping of severity levels
        :rtype: dict
        """
        return {
            "5": "critical",
            "4": "high",
            "3": "moderate",
            "2": "low",
            "1": "low",
            "0": "info",
            5: "Critical",
            4: "High",
            3: "Medium",
            2: "Low",
            1: "Low",
            0: "Low",
        }
