"""
Scanner integration for Nessus vulnerability scanning.
"""

import logging
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union, cast
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import ElementTree

import nessus_file_reader as nfr  # type: ignore

from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.core.app.utils.file_utils import find_files, get_processed_file_path, iterate_files, move_file, read_file
from regscale.core.app.utils.parser_utils import safe_float
from regscale.core.utils.date import date_str
from regscale.integrations.commercial.nessus.nessus_utils import cpe_xml_to_dict, software
from regscale.integrations.scanner_integration import IntegrationAsset, IntegrationFinding, ScannerIntegration
from regscale.integrations.variables import ScannerVariables
from regscale.models import ImportValidater, regscale_models

logger = logging.getLogger("regscale")


class NessusIntegration(ScannerIntegration):
    """Integration class for Nessus vulnerability scanning."""

    title = "Nessus"
    asset_identifier_field = "tenableId"
    finding_severity_map = {
        "4": regscale_models.IssueSeverity.Critical,
        "3": regscale_models.IssueSeverity.High,
        "2": regscale_models.IssueSeverity.Moderate,
        "1": regscale_models.IssueSeverity.Low,
        "critical": regscale_models.IssueSeverity.Critical,
        "high": regscale_models.IssueSeverity.High,
        "medium": regscale_models.IssueSeverity.Moderate,
        "low": regscale_models.IssueSeverity.Low,
    }

    @staticmethod
    def log_file_warning_and_exit(path: str, exit_app: bool = True) -> None:
        """
        Log a warning message stating that the Nessus file was not found.

        :param str path: The path to the Nessus file that was not found
        :param bool exit_app: Whether to exit the program after logging the warning, defaults to True
        :rtype: None
        """
        logger.warning("No Nessus files found in path %s", path)
        if exit_app:
            sys.exit(0)

    @staticmethod
    def _check_path(path: Optional[str] = None) -> None:
        """
        Check if the path is a valid Nessus file path.

        :param Optional[str] path: The path to check, defaults to None
        :raises ValueError: If the path is provided path is not provided
        :rtype: None
        """
        if not path:
            raise ValueError("Nessus file path must end with .nessus")

    def fetch_findings(self, *args: Tuple, **kwargs: dict) -> Iterator[IntegrationFinding]:
        """
        Fetches Nessus findings from the processed Nessus files.

        :return: Iterator of IntegrationFinding objects
        :rtype: Iterator[IntegrationFinding]
        """
        path: Optional[str] = cast(Optional[str], kwargs.get("path"))
        self._check_path(path)
        file_collection = find_files(path, "*.nessus")
        if not file_collection:
            self.log_file_warning_and_exit(path)
        if not self.check_collection(file_collection, path):
            return
        self.num_findings_to_process = 0
        for file in iterate_files(file_collection):
            content = read_file(file)
            root = ET.fromstring(content)
            if scan_dt := nfr.scan.scan_time_start(root):
                self.scan_date = scan_dt.strftime("%Y-%m-%d")
            for nessus_asset in nfr.scan.report_hosts(root):
                asset_name = nfr.host.report_host_name(nessus_asset)
                for nessus_vulnerability in root.iterfind(f"./Report/ReportHost[@name='{asset_name}']/ReportItem"):
                    parsed_vulnerability = self.parse_finding(nessus_vulnerability, asset_name)
                    if parsed_vulnerability:
                        self.num_findings_to_process += 1
                        yield parsed_vulnerability
        self.move_files(file_collection)

    def parse_finding(self, vuln: Any, asset_id: str) -> Optional[IntegrationFinding]:
        """
        Parses a Nessus vulnerability or informational item into an IntegrationFinding object.

        :param Any vuln: The Nessus vulnerability or informational item to parse
        :param str asset_id: The asset identifier
        :return: The parsed IntegrationFinding or None if parsing fails
        :rtype: Optional[IntegrationFinding]
        """
        try:
            vulnerability_data = self.get_vulnerability_data(vuln)
            if hasattr(vuln, "attrib"):
                vuln = vuln.attrib
            vuln.update(vulnerability_data)

            # Determine if this is an informational item or a vulnerability
            is_informational = vuln.get("severity") == "0" and vuln.get("risk_factor", "").lower() == "none"

            if is_informational:
                category = f"Nessus Information: {vuln.get('pluginFamily', 'General')}"
                issue_type = "Information"
                severity = None
                status = regscale_models.IssueStatus.Closed
            else:
                category = f"Nessus Vulnerability: {vuln.get('pluginFamily', 'General')}"
                issue_type = "Vulnerability"
                severity = self.finding_severity_map.get(vuln["severity"].lower(), regscale_models.IssueSeverity.Low)
                status = regscale_models.IssueStatus.Open

            synopsis = vuln.get("synopsis", "")
            plugin_name = vuln.get("pluginName", "Unknown Plugin")

            # Get severity_int, defaulting to 0 if not found
            severity_int = int(vuln.get("severity", "0"))
            identifier = vuln.get("cve") or plugin_name

            if is_informational:
                return None

            return IntegrationFinding(
                control_labels=[],
                category=category,
                title=f"{identifier}: {synopsis}",
                issue_title=f"{identifier}: {synopsis}",
                description=vuln.get("description"),
                severity=severity or regscale_models.IssueSeverity.Low,
                status=status,
                asset_identifier=asset_id,
                external_id=vuln.get("pluginID", "Unknown"),
                first_seen=vuln.get("firstSeen") or get_current_datetime(),
                last_seen=vuln.get("lastSeen") or get_current_datetime(),
                remediation=vuln.get("solution", ""),
                cvss_score=float(vuln.get("cvss_base_score") or 0),
                cve=vuln.get("cve"),
                vulnerability_type=self.title,
                plugin_id=vuln.get("pluginID"),
                plugin_name=identifier,
                ip_address=asset_id,
                dns=None,
                severity_int=severity_int,
                issue_type=issue_type,
                date_created=get_current_datetime(),
                date_last_updated=get_current_datetime(),
                gaps="",
                observations=vuln.get("plugin_output", ""),
                evidence=vuln.get("plugin_output", ""),
                identified_risk=vuln.get("risk_factor", ""),
                impact="",
                recommendation_for_mitigation=vuln.get("solution", ""),
                rule_id=vuln.get("pluginID"),
                rule_version=vuln.get("script_version"),
                results=vuln.get("plugin_output", ""),
                comments=None,
                baseline="",
                poam_comments=None,
                vulnerable_asset=asset_id,
                source_rule_id=vuln.get("fname"),
            )
        except Exception as e:
            logger.error("Error parsing Nessus finding: %s", str(e), exc_info=True)
            return None

    def check_collection(self, file_collection: List[Union[Path, str]], path: str) -> bool:
        """
        Check if any Nessus files were found in the given path.

        :param List[Union[Path, str]] file_collection: List of Path objects for .nessus files or S3 URIs
        :param str path: Path to a .nessus file or a folder containing Nessus files
        :return: boolean indicating if any Nessus files were found
        :rtype: bool
        """
        res = True
        if len(file_collection) == 0:
            self.log_file_warning_and_exit(path, exit_app=False)
            res = False
        return res

    def fetch_assets(self, *args: Any, **kwargs: dict) -> Iterator[IntegrationAsset]:  # type: ignore
        """
        Fetches Nessus assets from the processed Nessus files.

        :param str path: Path to the Nessus files
        :yields: Iterator[IntegrationAsset]
        """
        path: Optional[str] = cast(Optional[str], kwargs.get("path"))

        file_collection = find_files(path, "*.nessus")
        if not file_collection:
            self.log_file_warning_and_exit(path)
        if self.check_collection(file_collection, path):
            for file in iterate_files(file_collection):
                ImportValidater(
                    file_path=file,
                    disable_mapping=True,
                    required_headers=["Policy", "Report"],
                    mapping_file_path=tempfile.gettempdir(),
                    xml_tag="NessusClientData_v2",
                    prompt=False,
                )
                content = read_file(file)
                root = ET.fromstring(content)
                tree = ElementTree(root)
                assets = nfr.scan.report_hosts(root)
                cpe_items = cpe_xml_to_dict(tree)  # type: ignore
                self.num_assets_to_process = len(assets)
                for asset in assets:
                    asset_properties = self.get_asset_properties(root, cpe_items, asset)
                    parsed_asset = self.parse_asset(asset_properties)
                    yield parsed_asset

    def parse_asset(self, asset: Dict[str, Any]) -> IntegrationAsset:
        """
        Parses Nessus assets.

        :param Dict[str, Any] asset: The Nessus asset to parse
        :return: The parsed IntegrationAsset
        :rtype: IntegrationAsset
        """
        software_inventory = [
            {
                "name": software_obj.get("title"),
                "version": software_obj.get("version"),
                "references": software_obj.get("references", []),
            }
            for software_obj in asset.get("software_inventory", [])
        ]

        return IntegrationAsset(
            name=asset.get("name", ""),
            identifier=asset.get("name")
            or asset.get("host_ip", "")
            or asset.get("fqdn", "")
            or asset.get("tenable_id", ""),
            asset_type=asset.get("asset_type", "Other"),
            asset_category=regscale_models.AssetCategory.Hardware,
            asset_owner_id=ScannerVariables.userId,
            parent_id=self.plan_id,
            parent_module=regscale_models.SecurityPlan.get_module_slug(),
            status=asset.get("status", "Active (On Network)"),
            date_last_updated=date_str(asset.get("last_scan") or get_current_datetime()),
            mac_address=asset.get("mac_address", ""),
            fqdn=asset.get("fqdn", ""),
            ip_address=asset.get("host_ip", ""),
            operating_system=asset.get("operating_system", ""),
            aws_identifier=asset.get("aws_identifier", ""),
            vlan_id=asset.get("vlan_id", ""),
            location=asset.get("location", ""),
            software_inventory=software_inventory,
        )

    @staticmethod
    def get_asset_properties(root, cpe_items, file_asset) -> dict:
        """
        Get the asset properties

        :param root: The Nessus root element
        :param cpe_items: The CPE items
        :param file_asset: The file asset
        :return: dict of asset properties
        :rtype: dict
        """

        nessus_report_uuid = nfr.scan.server_preference_value(root, "report_task_id")
        asset_name = nfr.host.report_host_name(file_asset)
        temp = f"./Report/ReportHost[@name='{asset_name}']/HostProperties/tag"
        operating_system = nfr.host.detected_os(file_asset)
        netbios = nfr.host.netbios_network_name(root, file_asset)
        resolved_ip = nfr.host.resolved_ip(file_asset)
        scanner_ip = nfr.host.scanner_ip(root, file_asset)
        software_inventory = software(cpe_items, file_asset)  # Placeholder for CPE lookup,
        tag_map = {
            "id": "tenable_id",
            "host-ip": "host_ip",
            "host-fqdn": "fqdn",
            "mac-address": "macaddress",
            "HOST_START_TIMESTAMP": "begin_scan",
            "HOST_END_TIMESTAMP": "last_scan",
            "aws-instance-instanceId": "aws_instance_id",
            "aws-instance-vpc-id": "vlan_id",
            "aws-instance-region": "location",
        }

        tag_values = {value: "" for key, value in tag_map.items()}

        for file_asset_tag in root.iterfind(temp):
            tag_name = file_asset_tag.attrib.get("name")
            tag_value = file_asset_tag.text
            if tag_name in tag_map:
                variable_name = tag_map[tag_name]
                tag_values[variable_name] = tag_value
        return {
            "name": asset_name,
            "operating_system": operating_system,
            "tenable_id": (tag_values["tenable_id"] if "tenable_id" in tag_values else ""),
            "netbios_name": netbios["netbios_computer_name"],
            "all_tags": [{"name": attrib.attrib["name"], "val": attrib.text} for attrib in root.iterfind(temp)],
            "mac_address": tag_values["macaddress"],
            "last_scan": tag_values["last_scan"],
            "resolved_ip": resolved_ip,
            "asset_count": len(list(root.iter("ReportHost"))),
            "scanner_ip": scanner_ip,
            "host_ip": tag_values["host_ip"],
            "fqdn": tag_values["fqdn"],
            "software_inventory": software_inventory,
            "nessus_report_uuid": nessus_report_uuid,
            "aws_identifier": tag_values["aws_instance_id"],
            "vlan_id": tag_values["vlan_id"],
            "location": tag_values["location"],
        }

    @classmethod
    def all_element_data(cls, element: Any, indent: str = "") -> str:
        """
        Recursively walk down the XML element and return a string representation.

        :param Any element: A file vulnerability XML element
        :param str indent: Current indentation level (for pretty printing)
        :return: String representation of the vulnerability data
        :rtype: str
        """
        result = []

        if element.text and element.text.strip():
            result.append(f"{indent}{element.tag}: {element.text.strip()}")

        for attr, value in element.attrib.items():
            result.append(f"{indent}{element.tag}.{attr}: {value}")

        for child in element:
            result.append(cls.all_element_data(child, indent + "  "))

        return "\n".join(result)

    @classmethod
    def get_vulnerability_data(cls, file_vuln: Any) -> dict:
        """
        Get the vulnerability data from a Nessus XML element.

        :param Any file_vuln: A file vulnerability XML element
        :return: dict of vulnerability data
        :rtype: dict
        """

        def get(field_name: str) -> Optional[str]:
            """
            Get the field value from the XML element.

            :param str field_name: The field name to get
            :return: Field value
            :rtype: Optional[str]
            """
            element = file_vuln.find(field_name)
            return element.text if element is not None else None

        def get_attrib(attr_name: str) -> Optional[str]:
            """
            Get the attribute value from the XML element.

            :param str attr_name: The attribute name to get
            :return: Attribute value
            :rtype: Optional[str]
            """
            return file_vuln.get(attr_name)

        description = get("description")
        plugin_output = get("plugin_output")
        cvss_base_score = safe_float(get("cvss3_base_score"))
        cve = get("cve")
        synopsis = get("synopsis")
        solution = get("solution")
        severity = get_attrib("severity")
        plugin_id = get_attrib("pluginID")
        plugin_name = get_attrib("pluginName")
        risk_factor = get("risk_factor")
        script_version = get("script_version")
        fname = get("fname")

        return {
            "description": description,
            "synopsis": synopsis,
            "plugin_output": plugin_output,
            "cve": cve,
            "cvss_base_score": cvss_base_score,
            "severity": severity,
            "solution": solution,
            "pluginID": plugin_id,
            "pluginName": plugin_name,
            "risk_factor": risk_factor,
            "script_version": script_version,
            "fname": fname,
        }

    @staticmethod
    def move_files(file_collection: List[Union[Path, str]]) -> None:
        """
        Move the list of files to a folder called 'processed' in the same directory.

        :param List[Union[Path, str]] file_collection: List of file paths or S3 URIs
        :return: None
        :rtype: None
        """
        for file in file_collection:
            new_file = get_processed_file_path(file)
            move_file(file, new_file)
            logger.info("Moved Nessus file %s to %s", file, new_file)
