"""
Qualys Total Cloud scanner integration class using JSONLScannerIntegration.
"""

import logging
import os
import time
import traceback
import xml.etree.ElementTree as ET
from datetime import date, datetime
from io import TextIOWrapper
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, TextIO, Tuple, Union

from rich.progress import BarColumn, Progress, SpinnerColumn, TaskID, TextColumn, TimeElapsedColumn

from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.core.utils.date import date_obj, date_str, normalize_timestamp
from regscale.integrations.commercial.qualys.qualys_error_handler import QualysErrorHandler
from regscale.integrations.commercial.qualys.variables import QualysVariables
from regscale.integrations.jsonl_scanner_integration import JSONLScannerIntegration
from regscale.integrations.scanner_integration import (
    IntegrationAsset,
    IntegrationFinding,
    ScannerIntegrationType,
    issue_due_date,
)
from regscale.integrations.variables import ScannerVariables
from regscale.models import AssetStatus, IssueSeverity, IssueStatus
from regscale import models as regscale_models

logger = logging.getLogger("regscale")

NO_RESULTS = "No results available"
NO_DESCRIPTION = "No description available"
NO_REMEDIATION = "No remediation information available"
SCANNING_TOOL_NAME = "Qualys Total Cloud"


class QualysTotalCloudJSONLIntegration(JSONLScannerIntegration):
    """Class for handling Qualys Total Cloud scanner integration using JSONL."""

    title: str = SCANNING_TOOL_NAME
    asset_identifier_field: str = "qualysId"
    finding_severity_map: Dict[str, Any] = {
        "0": IssueSeverity.NotAssigned.value,
        "1": IssueSeverity.Low.value,
        "2": IssueSeverity.Moderate.value,
        "3": IssueSeverity.Moderate.value,
        "4": IssueSeverity.High.value,
        "5": IssueSeverity.Critical.value,
    }

    finding_status_map = {
        "New": IssueStatus.Open,
        "Active": IssueStatus.Open,
        "Fixed": IssueStatus.Closed,
    }

    # Constants for file paths
    ASSETS_FILE = "./artifacts/qualys_total_cloud_assets.jsonl"
    FINDINGS_FILE = "./artifacts/qualys_total_cloud_findings.jsonl"
    CONTAINERS_FILE = "./artifacts/qualys_total_cloud_containers.jsonl"
    CONTAINER_FINDINGS_FILE = "./artifacts/qualys_total_cloud_container_findings.jsonl"

    def __init__(self, *args, **kwargs):
        """
        Initialize the QualysTotalCloudJSONLIntegration object.

        :param Any *args: Variable positional arguments
        :param Any **kwargs: Variable keyword arguments
        :param bool is_component: Whether to upload to a component record (default: False)
        """
        self.type = ScannerIntegrationType.VULNERABILITY
        self.xml_data = kwargs.pop("xml_data", None)
        self.containers = kwargs.pop("containers", None)
        self.is_component = kwargs.get("is_component", False)

        self._setup_file_path(kwargs)
        self._apply_vulnerability_creation_setting(kwargs)
        self._apply_ssl_verification_setting(kwargs)
        self._apply_thread_workers_setting(kwargs)

        super().__init__(*args, **kwargs)
        # No need to initialize clients, they are inherited from the parent class

    def _setup_file_path(self, kwargs: Dict[str, Any]) -> None:
        """Setup file path for XML data processing."""
        if self.xml_data and "file_path" not in kwargs:
            kwargs["file_path"] = None

    def _apply_vulnerability_creation_setting(self, kwargs: Dict[str, Any]) -> None:
        """Apply vulnerability creation setting from variables."""
        if kwargs.get("vulnerability_creation"):
            return

        if self._has_qualys_vulnerability_creation():
            kwargs["vulnerability_creation"] = QualysVariables.vulnerabilityCreation
            logger.info(f"Using Qualys-specific vulnerability creation mode: {kwargs['vulnerability_creation']}")
        elif self._has_scanner_vulnerability_creation():
            kwargs["vulnerability_creation"] = ScannerVariables.vulnerabilityCreation
            logger.info(f"Using global vulnerability creation mode: {kwargs['vulnerability_creation']}")

    def _has_qualys_vulnerability_creation(self) -> bool:
        """Check if QualysVariables has vulnerability creation setting."""
        return hasattr(QualysVariables, "vulnerabilityCreation") and QualysVariables.vulnerabilityCreation

    def _has_scanner_vulnerability_creation(self) -> bool:
        """Check if ScannerVariables has vulnerability creation setting."""
        return hasattr(ScannerVariables, "vulnerabilityCreation")

    def _apply_ssl_verification_setting(self, kwargs: Dict[str, Any]) -> None:
        """Apply SSL verification setting from ScannerVariables."""
        if not kwargs.get("ssl_verify") and hasattr(ScannerVariables, "sslVerify"):
            kwargs["ssl_verify"] = ScannerVariables.sslVerify
            logger.debug(f"Using SSL verification setting: {kwargs['ssl_verify']}")

    def _apply_thread_workers_setting(self, kwargs: Dict[str, Any]) -> None:
        """Apply thread max workers setting from ScannerVariables."""
        if not kwargs.get("max_workers") and hasattr(ScannerVariables, "threadMaxWorkers"):
            kwargs["max_workers"] = ScannerVariables.threadMaxWorkers
            logger.debug(f"Using thread max workers: {kwargs['max_workers']}")

    def is_valid_file(self, data: Any, file_path: Union[Path, str]) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Check if the XML data is valid for Qualys Total Cloud.

        :param Any data: XML data to validate
        :param Union[Path, str] file_path: Path to the file (not used in this implementation)
        :return: Tuple of (is_valid, data)
        :rtype: Tuple[bool, Optional[Dict[str, Any]]]
        """
        # This would normally check the file structure, but for XML data we'll assume it's valid
        # if it contains HOST_LIST_VM_DETECTION_OUTPUT
        if not data or not isinstance(data, dict):
            logger.warning("Data is not a dictionary")
            return False, None

        # Check for Qualys errors in the data
        error_details = QualysErrorHandler.extract_error_details(data)
        if error_details.get("has_error"):
            logger.error("Data contains Qualys error response")
            QualysErrorHandler.log_error_details(error_details)
            return False, None

        if "HOST_LIST_VM_DETECTION_OUTPUT" not in data:
            logger.warning("Data does not contain HOST_LIST_VM_DETECTION_OUTPUT")
            return False, None

        return True, data

    def find_valid_files(self, path: Union[Path, str]) -> Iterator[Tuple[Union[Path, str], Dict[str, Any]]]:
        """
        Process XML data instead of files on disk.

        :param Union[Path, str] path: Path (not used in this implementation)
        :return: Iterator yielding tuples of (dummy path, XML data)
        :rtype: Iterator[Tuple[Union[Path, str], Dict[str, Any]]]
        """
        if not self.xml_data:
            logger.error("No XML data provided for Qualys integration")
            return

        # Use a dummy file path since we're processing XML data directly
        dummy_path = "qualys_xml_data.xml"
        is_valid, validated_data = self.is_valid_file(self.xml_data, dummy_path)

        if is_valid and validated_data is not None:
            yield dummy_path, validated_data

    def parse_asset(self, file_path: Union[Path, str] = None, data: Dict[str, Any] = None, host=None):
        """
        Parse a single asset from a Qualys host data.

        :param Union[Path, str] file_path: Path to the file (included for compatibility)
        :param Dict[str, Any] data: The parsed data (included for compatibility)
        :param host: XML Element or dictionary representing a host
        :return: IntegrationAsset object
        :rtype: IntegrationAsset
        """
        # Determine which host data to use
        host_data = self._determine_host_data(file_path, data, host)

        # Handle None input gracefully
        if host_data is None:
            return self._create_placeholder_asset()

        # Convert XML Element to dict if necessary
        if not isinstance(host_data, dict) and hasattr(host_data, "tag"):
            host_data = self._xml_element_to_dict(host_data)

        # Process dictionary data
        if isinstance(host_data, dict):
            return self._create_asset_from_dict(host_data)

        # If we got here, we don't know how to handle the data
        logger.error(f"Unexpected host data type: {type(host_data)}")
        raise ValueError(f"Cannot parse asset from data type: {type(host_data)}")

    def _determine_host_data(self, file_path, data, host):
        """
        Determine which host data to use based on provided parameters.

        :param file_path: File path parameter (may contain host data)
        :param data: Data parameter
        :param host: Host parameter
        :return: Host data to use
        """
        # Handle the case when the file_path contains the host data (common in tests)
        if isinstance(file_path, dict) and not host and not data:
            return file_path

        # Use host parameter if provided (for backward compatibility)
        if host is not None:
            return host

        # Fall back to data parameter
        return data

    def _create_placeholder_asset(self):
        """
        Create a placeholder asset when no valid host data is provided.

        :return: IntegrationAsset with placeholder data
        :rtype: IntegrationAsset
        """
        logger.warning("No host data provided to parse_asset")
        return IntegrationAsset(
            name="Unknown-Qualys-Asset",
            identifier=str(int(time.time())),  # Use timestamp as fallback ID
            asset_type="Server",
            asset_category="IT",
            status=AssetStatus.Active,
            parent_id=self.plan_id,
            parent_module="components" if self.is_component else "securityplans",
            notes="Generated for missing Qualys data",
        )

    def _create_asset_from_dict(self, host_data):
        """
        Create an IntegrationAsset from dictionary host data.

        :param host_data: Dictionary containing host information
        :return: IntegrationAsset object
        :rtype: IntegrationAsset
        """
        # Navigate to host data if we have the full structure
        processed_host = self._extract_host_from_structure(host_data)

        # Extract host information
        host_info = self._extract_host_information(processed_host)

        # Log asset creation for debugging
        logger.debug(f"Creating asset for host ID: {host_info['host_id']}")
        logger.debug(f"Asset name: {host_info['name']}")
        logger.debug(f"Plan ID: {self.plan_id}, Parent Module: {self.parent_module}")
        logger.debug(f"Is Component: {self.is_component}")

        # Create and return the asset
        return IntegrationAsset(
            name=host_info["name"],
            identifier=host_info["host_id"],
            asset_type="Server",
            asset_category="IT",
            ip_address=host_info["ip"],
            fqdn=host_info["fqdn"],
            operating_system=host_info["os"],
            status=AssetStatus.Active,
            external_id=host_info["host_id"],
            date_last_updated=host_info["last_scan"],
            mac_address=None,
            vlan_id=host_info["network_id"],
            notes=f"Qualys Asset ID: {host_info['host_id']}",
            parent_id=self.plan_id,
            parent_module="components" if self.is_component else "securityplans",
        )

    def _extract_host_from_structure(self, host_data):
        """
        Extract host data from nested structure if needed.

        :param host_data: Host data dictionary
        :return: Processed host data
        """
        # Check if we got the full data structure or just a host dictionary
        if "HOST_LIST_VM_DETECTION_OUTPUT" not in host_data:
            return host_data

        # Navigate to the HOST data within the nested structure
        try:
            return (
                host_data.get("HOST_LIST_VM_DETECTION_OUTPUT", {})
                .get("RESPONSE", {})
                .get("HOST_LIST", {})
                .get("HOST", {})
            )
        except (AttributeError, KeyError):
            logger.error("Could not navigate to HOST data in dictionary")
            raise ValueError("Invalid host data structure")

    def _extract_host_information(self, host):
        """
        Extract host information from host dictionary.

        :param host: Host dictionary
        :return: Dictionary with extracted host information
        :rtype: dict
        """
        host_id = host.get("ID", "")
        ip = host.get("IP", "")
        dns = host.get("DNS", "")
        os = host.get("OS", "")
        last_scan = host.get("LAST_SCAN_DATETIME", "")
        network_id = host.get("NETWORK_ID", "")

        # Try to get FQDN from DNS_DATA if available
        fqdn = self._extract_fqdn(host)

        # Determine asset name
        name = dns or ip or f"QualysAsset-{host_id}"

        return {
            "host_id": host_id,
            "ip": ip,
            "dns": dns,
            "os": os,
            "last_scan": last_scan,
            "network_id": network_id,
            "fqdn": fqdn,
            "name": name,
        }

    def _extract_fqdn(self, host):
        """
        Extract FQDN from host DNS_DATA if available.

        :param host: Host dictionary
        :return: FQDN string or None
        :rtype: Optional[str]
        """
        dns_data = host.get("DNS_DATA", {})
        if dns_data:
            return dns_data.get("FQDN", "")
        return None

    def parse_finding(
        self,
        asset_identifier: str = None,
        data: Dict[str, Any] = None,
        item: Dict[str, Any] = None,
        detection=None,
        host_id=None,
    ):
        """
        Parse a single finding from a Qualys detection.

        :param str asset_identifier: The identifier of the asset this finding belongs to (for compatibility)
        :param Dict[str, Any] data: The asset data (not used in this implementation, for compatibility)
        :param Dict[str, Any] item: The finding data (for compatibility)
        :param detection: XML Element or dict representing a detection
        :param host_id: Host ID this detection belongs to
        :return: IntegrationFinding object
        :rtype: IntegrationFinding
        """
        # Determine which detection and host_id to use
        detection_to_use, host_id_to_use = self._determine_finding_parameters(
            detection, item, host_id, asset_identifier
        )

        # Handle None input gracefully
        if detection_to_use is None:
            return self._create_placeholder_finding(host_id_to_use)

        # Convert XML Element to dict if necessary
        if not isinstance(detection_to_use, dict) and hasattr(detection_to_use, "tag"):
            detection_to_use = self._xml_element_to_dict(detection_to_use)

        return self._parse_finding_from_dict(detection_to_use, host_id_to_use)

    def _determine_finding_parameters(self, detection, item, host_id, asset_identifier):
        """
        Determine which detection and host_id to use based on provided parameters.

        :param detection: Detection parameter
        :param item: Item parameter (for compatibility)
        :param host_id: Host ID parameter
        :param asset_identifier: Asset identifier parameter (for compatibility)
        :return: Tuple of (detection_to_use, host_id_to_use)
        :rtype: tuple
        """
        # For backward compatibility
        detection_to_use = detection if detection is not None else item
        host_id_to_use = host_id if host_id is not None else asset_identifier

        return detection_to_use, host_id_to_use

    def _create_placeholder_finding(self, host_id_to_use):
        """
        Create a placeholder finding when no valid detection data is provided.

        :param host_id_to_use: Host ID to use for the finding
        :return: IntegrationFinding with placeholder data
        :rtype: IntegrationFinding
        """
        logger.warning("No detection data provided to parse_finding")

        # Use host_id or generate a placeholder if none provided
        if not host_id_to_use:
            host_id_to_use = f"unknown-host-{int(time.time())}"

        # Generate a placeholder finding with minimal information
        return IntegrationFinding(
            title="Unknown Qualys Finding",
            description="No detection data was provided",
            severity=IssueSeverity.Low.value,
            status=IssueStatus.Open,
            plugin_name="QID-unknown",
            plugin_id=self.title,
            asset_identifier=host_id_to_use,
            category="Vulnerability",
            scan_date=self.scan_date or get_current_datetime(),
            external_id=f"unknown-finding-{int(time.time())}",
        )

    def _parse_finding_from_dict(self, detection, host_id):
        """
        Parse a finding from a dictionary representation.

        :param detection: Dictionary containing finding data
        :param host_id: Host ID this detection belongs to
        :return: IntegrationFinding object
        """
        # Validate detection is a dictionary
        if not isinstance(detection, dict):
            logger.warning(f"Expected dictionary for detection, got {type(detection)}")
            detection = {}  # Use empty dict to prevent further errors

        # Extract basic finding information
        finding_data = self._extract_basic_finding_data_dict(detection)

        # Get CVE information
        finding_data["cve_id"] = self._extract_cve_id_from_dict(detection)

        # Extract issue data
        self._extract_issue_data_from_dict(detection, finding_data)

        # Build evidence
        finding_data["evidence"] = self._build_evidence(
            finding_data.get("qid", "Unknown"),
            host_id or "unknown-host",
            finding_data.get("first_found", self.scan_date or get_current_datetime()),
            finding_data.get("last_found", self.scan_date or get_current_datetime()),
            finding_data.get("results", NO_RESULTS),
        )

        # Create the finding object
        finding = self._create_finding_object(finding_data, host_id or "unknown-host")

        # Normalize dates for JSON serialization
        self._normalize_finding_dates(finding)

        return finding

    def _extract_basic_finding_data_dict(self, detection: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract basic finding information from dictionary data.

        :param Dict[str, Any] detection: Detection data
        :return: Dictionary with basic finding data
        :rtype: Dict[str, Any]
        """
        if not detection:
            detection = {}  # Ensure we have at least an empty dict

        current_time = self.scan_date or get_current_datetime()

        # Extract CVSS scores and convert to float if possible
        cvss_v3_score = detection.get("CVSS3_BASE")
        cvss_v2_score = detection.get("CVSS_BASE")

        # Convert CVSS scores to float if they're strings
        if cvss_v3_score and isinstance(cvss_v3_score, str):
            try:
                cvss_v3_score = float(cvss_v3_score)
            except (ValueError, TypeError):
                cvss_v3_score = None

        if cvss_v2_score and isinstance(cvss_v2_score, str):
            try:
                cvss_v2_score = float(cvss_v2_score)
            except (ValueError, TypeError):
                cvss_v2_score = None

        return {
            "qid": detection.get("QID", "Unknown"),
            "severity": detection.get("SEVERITY", "0"),
            "status": detection.get("STATUS", "New"),
            "first_found": detection.get("FIRST_FOUND_DATETIME", current_time),
            "last_found": detection.get("LAST_FOUND_DATETIME", current_time),
            "unique_id": detection.get("UNIQUE_VULN_ID", f"QID-{detection.get('QID', 'Unknown')}"),
            "results": detection.get("RESULTS", NO_RESULTS),
            "cvss_v3_score": cvss_v3_score,
            "cvss_v3_vector": detection.get("CVSS3_VECTOR", ""),
            "cvss_v2_score": cvss_v2_score,
            "cvss_v2_vector": detection.get("CVSS_VECTOR", ""),
        }

    def _extract_basic_finding_data_xml(self, detection: Optional[Union[Dict[str, Any], ET.Element]]) -> Dict[str, Any]:
        """
        Deprecated: Convert to dict first then use _extract_basic_finding_data_dict.

        :param Optional[Union[Dict[str, Any], ET.Element]] detection: Detection data as dictionary or XML Element
        :return: Dictionary with basic finding data
        :rtype: Dict[str, Any]
        """
        if detection is None:
            # Return default values if detection is None
            return {
                "qid": "Unknown",
                "severity": "0",
                "status": "New",
                "first_found": self.scan_date,
                "last_found": self.scan_date,
                "unique_id": "Unknown",
                "results": NO_RESULTS,
                "cvss_v3_score": None,
                "cvss_v3_vector": "",
                "cvss_v2_score": None,
                "cvss_v2_vector": "",
            }

        # Convert XML to dict if needed
        if not isinstance(detection, dict) and hasattr(detection, "tag"):
            detection = self._xml_element_to_dict(detection)

        # Use dict extraction method
        return self._extract_basic_finding_data_dict(detection)

    def _extract_cve_id_from_dict(self, detection: Optional[Dict[str, Any]]) -> str:
        """
        Extract CVE ID from dictionary data.

        :param Optional[Dict[str, Any]] detection: Detection data
        :return: CVE ID string
        :rtype: str
        """
        if not detection:
            return ""

        try:
            # Try to extract CVE from CVE_ID_LIST first
            cve_id = self._extract_cve_from_cve_list(detection)
            if cve_id:
                return cve_id

            # Try direct CVE fields if CVE_ID_LIST didn't work
            cve_id = self._extract_cve_from_direct_fields(detection)
            if cve_id:
                return cve_id

        except Exception as e:
            logger.warning(f"Error extracting CVE_ID: {str(e)}")

        return ""

    def _extract_cve_from_cve_list(self, detection: Dict[str, Any]) -> str:
        """
        Extract CVE ID from CVE_ID_LIST field.

        :param Dict[str, Any] detection: Detection data
        :return: CVE ID string
        :rtype: str
        """
        cve_list = detection.get("CVE_ID_LIST", {})
        if not cve_list:
            return ""

        if not isinstance(cve_list, dict):
            logger.warning(f"Expected dictionary for CVE_ID_LIST, got {type(cve_list)}")
            return ""

        if "CVE_ID" not in cve_list:
            return ""

        cve_data = cve_list.get("CVE_ID", [])
        return self._convert_cve_data_to_string(cve_data)

    def _extract_cve_from_direct_fields(self, detection: Dict[str, Any]) -> str:
        """
        Extract CVE ID from direct CVE fields.

        :param Dict[str, Any] detection: Detection data
        :return: CVE ID string
        :rtype: str
        """
        # Try CVE field directly
        cve_id = detection.get("CVE", "")
        if cve_id:
            return str(cve_id)

        # Try CVE_ID field directly
        cve_id = detection.get("CVE_ID", "")
        if cve_id:
            return str(cve_id)

        return ""

    def _convert_cve_data_to_string(self, cve_data: Any) -> str:
        """
        Convert CVE data to string format.

        :param Any cve_data: CVE data to convert
        :return: CVE ID string
        :rtype: str
        """
        if isinstance(cve_data, list) and cve_data:
            return str(cve_data[0]) if cve_data[0] else ""
        elif isinstance(cve_data, str):
            return cve_data
        elif cve_data:
            return str(cve_data)
        return ""

    def _extract_cve_id_from_xml(self, detection: Optional[Union[Dict[str, Any], ET.Element]]) -> str:
        """
        Deprecated: Convert to dict first then use _extract_cve_id_from_dict.

        :param Optional[Union[Dict[str, Any], ET.Element]] detection: Detection data as dictionary or XML Element
        :return: CVE ID string
        :rtype: str
        """
        if detection is None:
            return ""

        # Convert XML to dict if needed
        if not isinstance(detection, dict) and hasattr(detection, "tag"):
            detection = self._xml_element_to_dict(detection)

        # Use dict extraction method
        return self._extract_cve_id_from_dict(detection)

    def _extract_issue_data_from_dict(self, detection: Optional[Dict[str, Any]], finding_data: Dict[str, Any]) -> None:
        """
        Extract issue data from dictionary and update finding_data in place.

        :param Optional[Dict[str, Any]] detection: Detection data
        :param Dict[str, Any] finding_data: Finding data to update
        :return: None
        """
        if not detection:
            detection = {}

        qid = finding_data.get("qid", "Unknown")
        issue_data = detection.get("ISSUE_DATA", {})

        # Default values
        finding_data["title"] = f"Qualys Vulnerability QID-{qid}"
        finding_data["diagnosis"] = NO_DESCRIPTION
        finding_data["solution"] = NO_REMEDIATION

        # Update with actual values if present
        if issue_data:
            if isinstance(issue_data, dict):
                finding_data["title"] = issue_data.get("TITLE", finding_data["title"])
                finding_data["diagnosis"] = issue_data.get("DIAGNOSIS", finding_data["diagnosis"])
                finding_data["solution"] = issue_data.get("SOLUTION", finding_data["solution"])
            else:
                logger.warning(f"Expected dictionary for ISSUE_DATA, got {type(issue_data)}")

        # Ensure values are strings
        finding_data["title"] = (
            str(finding_data["title"]) if finding_data["title"] else f"Qualys Vulnerability QID-{qid}"
        )
        finding_data["diagnosis"] = str(finding_data["diagnosis"]) if finding_data["diagnosis"] else NO_DESCRIPTION
        finding_data["solution"] = str(finding_data["solution"]) if finding_data["solution"] else NO_REMEDIATION

    def _extract_issue_data_from_xml(
        self, detection: Optional[Union[Dict[str, Any], ET.Element]], finding_data: Dict[str, Any]
    ) -> None:
        """
        Deprecated: Convert to dict first then use _extract_issue_data_from_dict.

        :param Optional[Union[Dict[str, Any], ET.Element]] detection: Detection data as dictionary or XML Element
        :param Dict[str, Any] finding_data: Finding data to update
        :return: None
        """
        if detection is None:
            # Set default values
            qid = finding_data["qid"]
            finding_data["title"] = f"Qualys Vulnerability QID-{qid}"
            finding_data["diagnosis"] = NO_DESCRIPTION
            finding_data["solution"] = NO_REMEDIATION
            return

        # Convert XML to dict if needed
        if not isinstance(detection, dict) and hasattr(detection, "tag"):
            detection = self._xml_element_to_dict(detection)

        # Use dict extraction method
        self._extract_issue_data_from_dict(detection, finding_data)

    def _build_evidence(self, qid: str, host_id: str, first_found: str, last_found: str, results: Optional[str]) -> str:
        """
        Build evidence string from finding data.

        :param str qid: QID identifier
        :param str host_id: Host ID
        :param str first_found: First found datetime
        :param str last_found: Last found datetime
        :param Optional[str] results: Results data
        :return: Formatted evidence string
        :rtype: str
        """
        evidence_parts = [
            f"QID: {qid}",
            f"Host ID: {host_id}",
            f"First Found: {first_found}",
            f"Last Found: {last_found}",
        ]

        if results:
            evidence_parts.append(f"\nResults:\n{results}")

        return "\n".join(evidence_parts)

    def _create_finding_object(self, finding_data: Dict[str, Any], host_id: str) -> IntegrationFinding:
        """
        Create IntegrationFinding object from extracted finding data.

        :param Dict[str, Any] finding_data: Finding data dictionary
        :param str host_id: Host ID
        :return: IntegrationFinding object
        :rtype: IntegrationFinding
        """
        if not finding_data:
            finding_data = {}  # Ensure we have at least an empty dict

        severity_value = self.finding_severity_map.get(finding_data.get("severity", "0"), IssueSeverity.Moderate.value)

        # Get current time for any missing date fields
        current_time = self.scan_date or get_current_datetime()
        qid = finding_data.get("qid", "Unknown")

        # Log the finding data for debugging
        logger.debug(f"Creating finding for QID {qid}, host {host_id}")
        logger.debug(f"CVE: {finding_data.get('cve_id', 'None')}")
        logger.debug(f"CVSS V3 Score: {finding_data.get('cvss_v3_score', 'None')}")
        logger.debug(f"CVSS V2 Score: {finding_data.get('cvss_v2_score', 'None')}")

        return IntegrationFinding(
            title=finding_data.get("title", f"Qualys Vulnerability QID-{qid}"),
            description=finding_data.get("diagnosis", NO_DESCRIPTION),
            severity=severity_value,
            status=self.get_finding_status(finding_data.get("status", "New")),
            cvss_v3_score=finding_data.get("cvss_v3_score"),
            cvss_v3_vector=finding_data.get("cvss_v3_vector", ""),
            cvss_v2_score=finding_data.get("cvss_v2_score"),
            cvss_v2_vector=finding_data.get("cvss_v2_vector", ""),
            plugin_name=f"QID-{qid}",
            plugin_id=self.title,
            asset_identifier=host_id,
            category="Vulnerability",
            cve=finding_data.get("cve_id", ""),
            control_labels=[f"QID-{qid}"],
            evidence=finding_data.get("evidence", "No evidence available"),
            identified_risk=finding_data.get("title", f"Qualys Vulnerability QID-{qid}"),
            recommendation_for_mitigation=finding_data.get("solution", NO_REMEDIATION),
            scan_date=current_time,
            first_seen=finding_data.get("first_found", current_time),
            last_seen=finding_data.get("last_found", current_time),
            external_id=finding_data.get("unique_id", f"QID-{qid}-{host_id}"),
            due_date=issue_due_date(
                severity=severity_value,
                created_date=finding_data.get("first_found", current_time),
                title=self.title,
                config=self.app.config,
            ),
        )

    def _normalize_finding_dates(self, finding):
        """Ensure all dates are strings for JSON serialization."""
        date_fields = ["scan_date", "first_seen", "last_seen", "due_date"]

        for field in date_fields:
            value = getattr(finding, field, None)
            if not isinstance(value, str) and value:
                setattr(finding, field, value.isoformat() if hasattr(value, "isoformat") else str(value))

    def _get_findings_data_from_file(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract findings data from Qualys XML data.

        :param Dict[str, Any] data: The data from the XML
        :return: List of finding items
        :rtype: List[Dict[str, Any]]
        """
        host_list = data.get("HOST_LIST_VM_DETECTION_OUTPUT", {}).get("RESPONSE", {}).get("HOST_LIST")
        hosts = host_list.get("HOST", []) if host_list else []

        if isinstance(hosts, dict):
            hosts = [hosts]

        findings = []
        for host in hosts:
            host_id = host.get("ID", "")
            detection_list = host.get("DETECTION_LIST", {})
            detections = detection_list.get("DETECTION", []) if detection_list else []

            if isinstance(detections, dict):
                detections = [detections]

            for detection in detections:
                detection["host_id"] = host_id  # Add host_id to each detection
                findings.append(detection)

        return findings

    def _build_evidence_from_detection(self, item: Dict[str, Any], host: Dict[str, Any]) -> str:
        """
        Build evidence string from detection data.

        :param Dict[str, Any] item: Detection data
        :param Dict[str, Any] host: Host data
        :return: Formatted evidence string
        :rtype: str
        """
        evidence_parts = [
            f"QID: {item.get('QID', 'Unknown')}",
            f"Host: {host.get('IP', 'Unknown')} ({host.get('DNS', 'Unknown')})",
            f"OS: {host.get('OS', 'Unknown')}",
            f"First Found: {item.get('FIRST_FOUND_DATETIME', 'Unknown')}",
            f"Last Found: {item.get('LAST_FOUND_DATETIME', 'Unknown')}",
        ]

        if item.get("RESULTS"):
            evidence_parts.append(f"\nResults:\n{item.get('RESULTS')}")

        return "\n".join(evidence_parts)

    def _build_remediation(self, item: Dict[str, Any]) -> str:
        """
        Build remediation string from detection data.

        :param Dict[str, Any] item: Detection data
        :return: Formatted remediation string
        :rtype: str
        """
        if item.get("SOLUTION"):
            return item.get("SOLUTION")
        return "No remediation information available."

    def _get_cve_id(self, item: Dict[str, Any]) -> str:
        """
        Extract CVE ID from detection data.

        :param Dict[str, Any] item: Detection data
        :return: CVE ID if available
        :rtype: str
        """
        # Check for CVEs in the item
        if item.get("CVE_ID_LIST", {}).get("CVE_ID"):
            cve_data = item.get("CVE_ID_LIST", {}).get("CVE_ID", [])
            if isinstance(cve_data, list) and cve_data:
                return cve_data[0]
            elif isinstance(cve_data, str):
                return cve_data

        return ""

    def fetch_assets_and_findings(self, file_path: str = None, empty_files: bool = True):
        """
        Fetch assets and findings from Qualys Total Cloud JSONL file or XML data.
        This method orchestrates the process flow based on input type.

        :param str file_path: Path to source file or directory (for compatibility with parent class)
        :param bool empty_files: Whether to empty both output files before writing (for compatibility)
        :return: None or Tuple of (assets_iterator, findings_iterator) for compatibility with parent class
        """
        if file_path:
            self.file_path = file_path
        self.empty_files = empty_files

        self._verify_file_path()
        self._prepare_output_files()

        try:
            if self.xml_data:
                self._process_xml_data()
            else:
                self._process_jsonl_file(file_path, empty_files)

            # For compatibility with parent class that returns iterators
            if self.xml_data:
                assets_iterator = self._yield_items_from_jsonl(self.ASSETS_FILE, IntegrationAsset)
                findings_iterator = self._yield_items_from_jsonl(self.FINDINGS_FILE, IntegrationFinding)
                return assets_iterator, findings_iterator
        except Exception as e:
            logger.error(f"Error fetching assets and findings: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def _verify_file_path(self):
        """Verify that the file path exists if provided."""
        if self.file_path and not os.path.isfile(self.file_path):
            logger.error(f"QualysTotalCloudJSONLIntegration file path does not exist: {self.file_path}")
            raise FileNotFoundError(f"File path does not exist: {self.file_path}")

    def _prepare_output_files(self):
        """Create output directories and clear existing output files."""
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(self.ASSETS_FILE), exist_ok=True)
        os.makedirs(os.path.dirname(self.FINDINGS_FILE), exist_ok=True)

        # Clear any existing output files
        if os.path.exists(self.ASSETS_FILE):
            os.remove(self.ASSETS_FILE)
        if os.path.exists(self.FINDINGS_FILE):
            os.remove(self.FINDINGS_FILE)

    def _process_xml_data(self):
        """Process XML data from string or dictionary format."""
        logger.info("Processing XML data directly")

        if isinstance(self.xml_data, str):
            self._process_xml_string()
        elif isinstance(self.xml_data, dict):
            self._process_xml_dict()
        else:
            logger.error(f"Unsupported XML data type: {type(self.xml_data)}")

    def _process_xml_string(self):
        """Process XML data provided as a string."""
        logger.debug("Parsing XML string data")
        try:
            # Convert XML string to dictionary first, then process it
            xml_dict = self._convert_xml_string_to_dict(self.xml_data)
            self.xml_data = xml_dict  # Replace string with dict for consistent processing
            self._process_xml_dict()  # Use the dict processing pathway
        except Exception as e:
            logger.error(f"Error processing XML string: {str(e)}")
            logger.debug(traceback.format_exc())

    def _convert_xml_string_to_dict(self, xml_string: str) -> Dict[str, Any]:
        """
        Convert an XML string to a dictionary.

        :param str xml_string: XML string to convert
        :return: Dictionary representation of the XML
        :rtype: Dict[str, Any]
        """
        success, parsed_data, error_message = QualysErrorHandler.parse_xml_safely(xml_string)

        if not success:
            logger.error(f"Failed to parse XML string: {error_message}")
            return {}

        # Check for Qualys-specific errors
        if parsed_data:
            error_details = QualysErrorHandler.extract_error_details(parsed_data)
            if error_details.get("has_error"):
                logger.error("XML contains Qualys error response")
                QualysErrorHandler.log_error_details(error_details)
                return {}

        return parsed_data or {}

    def _process_xml_dict(self):
        """Process XML data provided as a dictionary."""
        logger.debug("Using already parsed XML data (dict)")

        # Find all hosts in the XML data dictionary
        hosts_data = self._extract_hosts_from_dict()
        if not hosts_data:
            return

        num_hosts = len(hosts_data)
        logger.info(f"Found {num_hosts} hosts in XML dictionary data")

        # Extract all findings
        all_findings = self._extract_findings_from_hosts(hosts_data)
        num_findings = len(all_findings)
        logger.info(f"Found {num_findings} total findings in XML dictionary data")

        # Process assets and findings
        self._process_dict_assets_and_findings(
            hosts_data=hosts_data, all_findings=all_findings, containers_data=self.containers
        )

    def _extract_hosts_from_dict(self):
        """Extract host data from XML dictionary structure."""
        hosts_data = (
            self.xml_data.get("HOST_LIST_VM_DETECTION_OUTPUT", {})
            .get("RESPONSE", {})
            .get("HOST_LIST", {})
            .get("HOST", [])
        )

        # Normalize to ensure hosts_data is always a list
        if isinstance(hosts_data, dict):
            hosts_data = [hosts_data]

        return hosts_data

    @staticmethod
    def _extract_findings_from_hosts(hosts_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract all findings from host data dictionaries.
        :param List[Dict[str, Any]] hosts_data: List of host data dictionaries
        :return: List of findings dictionaries
        :rtype: List[Dict[str, Any]]
        """
        all_findings = []
        for host in hosts_data:
            host_id = host.get("ID", "")
            detections = host.get("DETECTION_LIST", {}).get("DETECTION", [])

            # Normalize to ensure detections is always a list
            if isinstance(detections, dict):
                detections = [detections]

            for detection in detections:
                detection["host_id"] = host_id
                all_findings.append(detection)

        return all_findings

    def _process_dict_assets_and_findings(self, hosts_data, all_findings, containers_data=None):
        """
        Process assets and findings from dictionary data.
        :param List[Dict[str, Any]] hosts_data: List of host data dictionaries
        :param List[Dict[str, Any]] all_findings: List of findings dictionaries
        :param List[Dict[str, Any]] containers_data: List of container data dictionaries
        """
        with open(self.ASSETS_FILE, "w") as assets_file, open(self.FINDINGS_FILE, "w") as findings_file:
            self._write_assets_from_dict(assets_file, hosts_data)
            self._write_findings_from_dict(findings_file, all_findings)
            if containers_data:
                self._write_containers_from_dict(assets_file, containers_data)
                self._write_container_findings_from_dict(findings_file, containers_data)

    def _write_assets_from_dict(self, assets_file, hosts_data):
        """Write assets from dictionary data to JSONL file."""
        assets_written = 0
        for host in hosts_data:
            try:
                asset = self.parse_asset(host=host)
                self._write_item(assets_file, asset)
                assets_written += 1
            except Exception as e:
                logger.error(f"Error processing asset: {str(e)}")
                logger.debug(traceback.format_exc())

        logger.info(f"Wrote {assets_written} assets to {self.ASSETS_FILE}")

    def _write_findings_from_dict(self, findings_file, all_findings):
        """Write findings from dictionary data to JSONL file."""
        findings_written = 0
        for finding in all_findings:
            try:
                host_id = finding.get("host_id", "")
                parsed_finding = self.parse_finding(detection=finding, host_id=host_id)
                self._write_item(findings_file, parsed_finding)
                findings_written += 1
            except Exception as e:
                logger.error(f"Error processing finding: {str(e)}")
                logger.debug(traceback.format_exc())

        logger.info(f"Wrote {findings_written} findings to {self.FINDINGS_FILE}")

    def _write_containers_from_dict(
        self, containers_file: TextIOWrapper, containers_data: List[Dict[str, Any]]
    ) -> None:
        """
        Write containers from dictionary data to JSONL file.

        :param TextIOWrapper containers_file: Open file handle to write containers to
        :param List[Dict[str, Any]] containers_data: List of container dictionaries to process
        """
        containers_written = 0
        for container in containers_data:
            try:
                if container_asset := self.parse_container_asset(container=container):
                    self._write_item(containers_file, container_asset)
                    containers_written += 1
            except Exception as e:
                logger.error(f"Error processing container: {str(e)}")
                logger.debug(traceback.format_exc())

        logger.info("Wrote %s containers to %s", containers_written, containers_file.name)

    def _write_container_findings_from_dict(
        self, container_findings_file: TextIOWrapper, container_findings_data: List[Dict[str, Any]]
    ):
        """
        Write container findings from dictionary data to JSONL file.

        :param TextIOWrapper container_findings_file: Path to the container findings file
        :param List[Dict[str, Any]] container_findings_data: Dictionary of container findings data
        """
        findings_written = 0
        for finding in container_findings_data:
            try:
                container_id = finding.get("containerId", "")
                if parsed_finding := self.parse_container_finding(finding=finding, container_id=container_id):
                    self._write_item(container_findings_file, parsed_finding)
                    findings_written += 1
            except Exception as e:
                logger.error(f"Error processing container finding: {str(e)}")
                logger.debug(traceback.format_exc())

        logger.info("Wrote %s container findings to %s", findings_written, container_findings_file.name)

    def parse_container_asset(self, container: dict) -> Optional[IntegrationAsset]:
        """
        Parse a single container asset from Qualys container data.

        :param container: Dictionary representing a container
        :return: IntegrationAsset object
        :rtype: Optional[IntegrationAsset]
        """
        state_map = {
            "running": AssetStatus.Active,
            "stopped": AssetStatus.Inactive,
            "paused": AssetStatus.Inactive,
            "restarting": AssetStatus.Active,
            "exited": AssetStatus.Inactive,
        }
        try:
            # Extract container information
            container_id = container.get("containerId", "")
            name = container.get("name", "Unknown Container")
            image_id = container.get("imageId", "")
            state = container.get("state", "stopped")
            sha = container.get("sha", "")
            state_changed = self._convert_timestamp_to_date_str(container.get("stateChanged", ""))

            return IntegrationAsset(
                name=name,
                identifier=container_id,
                asset_type="Virtual Machine (VM)",
                asset_category="Hardware",
                operating_system="Linux",
                status=state_map.get((state or "running").lower(), AssetStatus.Inactive),
                external_id=container_id,
                date_last_updated=state_changed,
                mac_address=None,
                notes=f"Qualys Container ID: {container_id}. Image ID: {image_id}. SHA: {sha}",
                parent_id=self.plan_id,
                parent_module="components" if self.is_component else "securityplans",
                is_virtual=True,
            )

        except Exception as e:
            logger.error(f"Error parsing container asset: {str(e)}")
            logger.debug(traceback.format_exc())

    def parse_container_finding(self, finding: dict, container_id: str):
        """
        Parse a single container finding from Qualys container vulnerability data.

        :param dict finding: Dictionary representing a container vulnerability
        :param str container_id: Container ID associated with the finding
        :return: IntegrationFinding object
        :rtype: Optional[IntegrationFinding]
        """

        vulns: List[dict] = finding.get("vulnerabilities")
        severity_map = {
            "1": IssueSeverity.Critical,
            "2": IssueSeverity.High,
            "3": IssueSeverity.Moderate,
            "4": IssueSeverity.Low,
            "5": IssueSeverity.NotAssigned,
        }

        for vuln in vulns:
            try:
                # Extract finding information
                title = vuln.get("title", "Unknown Container Vulnerability")
                severity_num = vuln.get("severity", 0)
                severity = severity_map.get(str(severity_num), IssueSeverity.NotAssigned)
                description = vuln.get("result", "No description available")
                status = vuln.get("status", "New")
                vuln_id = vuln.get("id", "")

                qid = vuln.get("qid", "")

                # Get current time for any missing date fields
                current_time = self.scan_date or get_current_datetime()

                # Convert timestamp to datetime if needed
                first_found = vuln.get("firstFound", current_time)
                last_found = vuln.get("lastFound", current_time)

                # Handle timestamp conversion if it's a numeric timestamp
                first_found = self._convert_timestamp_to_date_str(first_found)
                last_found = self._convert_timestamp_to_date_str(last_found)

                # sometimes cvss3Info is not a dict, so we ensure it is
                cvs3_info = vuln.get("cvss3Info")
                if not isinstance(cvs3_info, dict):
                    cvs3_info = {}

                cve = next(iter(vuln.get("cveids", [])), "")
                # Create finding object
                return IntegrationFinding(
                    title=title,
                    description=description,
                    severity=severity,
                    status=self.get_finding_status(status),
                    external_id=vuln_id,
                    asset_identifier=container_id,
                    cve=cve,
                    category="Vulnerability",
                    plugin_name=cve or f"QID-{qid}",
                    control_labels=[f"QID-{qid}"],
                    cvss_v3_base_score=cvs3_info.get("baseScore"),
                    cvss_v3_vector=cvs3_info.get("temporalScore"),
                    first_seen=first_found,
                    last_seen=last_found,
                    evidence=vuln.get("result", "No evidence available"),
                )

            except Exception as e:
                logger.error(f"Error parsing container finding: {str(e)}")
                logger.debug(traceback.format_exc())
                continue  # Continue to next vulnerability if this one fails

    def _process_xml_elements(self, hosts):
        """Process XML element hosts and detections with progress tracking."""
        # Convert XML elements to dictionaries first
        hosts_dict = self._convert_xml_elements_to_dict(hosts)
        all_findings = []

        # Extract all findings with host_ids
        for host in hosts_dict:
            host_id = host.get("ID", "")
            detections = host.get("DETECTION_LIST", {}).get("DETECTION", [])

            # Normalize to ensure detections is always a list
            if isinstance(detections, dict):
                detections = [detections]

            # Add host_id to each detection and collect
            for detection in detections:
                detection["host_id"] = host_id
                all_findings.append(detection)

        # Now process using the dictionary methods
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("({task.completed}/{task.total})"),
            TimeElapsedColumn(),
        ) as progress:
            # Setup progress tasks
            asset_task = progress.add_task("[cyan]Processing assets...", total=len(hosts_dict))
            finding_task = progress.add_task("[green]Processing findings...", total=len(all_findings))

            # Process using dictionary methods with progress tracking
            with open(self.ASSETS_FILE, "w") as assets_file, open(self.FINDINGS_FILE, "w") as findings_file:
                self._process_dict_assets_with_progress(hosts_dict, assets_file, progress, asset_task)
                # Use the findings list we extracted instead of trying to extract again
                self._process_findings_list_with_progress(all_findings, findings_file, progress, finding_task)

    def _process_dict_assets_with_progress(self, hosts_dict, assets_file, progress, asset_task):
        """Process assets from dictionaries with progress tracking."""
        assets_written = 0
        host_ids_processed = set()

        for host in hosts_dict:
            progress.update(asset_task, advance=1)
            try:
                host_id = host.get("ID", "")
                if host_id and host_id not in host_ids_processed:
                    asset = self.parse_asset(host=host)
                    self._write_item(assets_file, asset)
                    assets_written += 1
                    host_ids_processed.add(host_id)
            except Exception as e:
                logger.error(f"Error parsing asset: {str(e)}")
                logger.debug(traceback.format_exc())

        logger.info(f"Wrote {assets_written} unique assets to {self.ASSETS_FILE}")

    def _process_findings_list_with_progress(
        self, findings: List[Dict[str, Any]], findings_file: TextIO, progress: Progress, finding_task: TaskID
    ) -> None:
        """
        Process a list of finding dictionaries with progress tracking.

        :param List[Dict[str, Any]] findings: List of finding dictionaries
        :param TextIO findings_file: Open file handle for writing findings
        :param Progress progress: Progress tracker
        :param TaskID finding_task: Task ID for progress tracking
        :return: None
        """
        findings_written = 0
        finding_ids_processed = set()

        for finding in findings:
            progress.update(finding_task, advance=1)

            try:
                host_id = finding.get("host_id", "")
                # Get unique finding ID
                unique_id = self._get_detection_unique_id(finding, host_id)

                if unique_id and unique_id not in finding_ids_processed:
                    parsed_finding = self.parse_finding(detection=finding, host_id=host_id)
                    self._write_item(findings_file, parsed_finding)
                    findings_written += 1
                    finding_ids_processed.add(unique_id)
            except Exception as e:
                logger.error(f"Error parsing finding: {str(e)}")
                logger.debug(traceback.format_exc())

        logger.info(f"Wrote {findings_written} unique findings to {self.FINDINGS_FILE}")

    def _process_jsonl_file(self, file_path: Optional[str] = None, empty_files: bool = True) -> None:
        """
        Process JSONL file using parent class implementation.

        :param Optional[str] file_path: Path to JSONL file to process, defaults to None
        :param bool empty_files: Whether to empty files before processing, defaults to True
        :return: None
        """
        logger.info(f"Processing JSONL file: {self.file_path}")
        super().fetch_assets_and_findings(file_path, empty_files)

    def update_regscale_assets(self, assets_iterator: Iterator[IntegrationAsset]) -> int:
        """
        Update RegScale with assets.

        :param Iterator[IntegrationAsset] assets_iterator: Iterator of assets
        :return: Number of assets created
        :rtype: int
        """
        # Use the parent class implementation
        return super().update_regscale_assets(assets_iterator)

    def _extract_host_and_detections(self, host):
        """Extract host ID and detections from host data.

        :param host: Host data (dict or XML Element)
        :return: Tuple of (host_id, detections)
        """
        # Convert XML to dict if needed
        if not isinstance(host, dict) and hasattr(host, "tag"):
            host = self._xml_element_to_dict(host)

        host_id = host.get("ID", "")
        detections = host.get("DETECTION_LIST", {}).get("DETECTION", [])

        # Normalize to ensure detections is always a list
        if isinstance(detections, dict):
            detections = [detections]

        return host_id, detections

    def _convert_xml_elements_to_dict(self, elements: List[ET.Element]) -> List[Dict[str, Any]]:
        """
        Convert XML elements to a list of dictionaries.

        :param List[ET.Element] elements: List of XML Element objects
        :return: List of dictionaries with the same data
        :rtype: List[Dict[str, Any]]
        """
        result: List[Dict[str, Any]] = []
        for element in elements:
            result.append(self._xml_element_to_dict(element))
        return result

    def _xml_element_to_dict(self, element: Optional[ET.Element]) -> Dict[str, Any]:
        """
        Convert a single XML element to a dictionary with all its data.

        :param Optional[ET.Element] element: XML Element object
        :return: Dictionary with the element's data
        :rtype: Dict[str, Any]
        """
        if element is None:
            return {}

        result: Dict[str, Any] = {}

        # Add attributes
        for key, value in element.attrib.items():
            result[key] = value

        # Add text content if element has no children
        if len(element) == 0:
            text = element.text
            if text is not None and text.strip():
                # If this is a leaf node with text, just return the text
                return text.strip()

        # Add child elements
        for child in element:
            child_data = self._xml_element_to_dict(child)
            tag = child.tag

            # Handle multiple elements with the same tag
            if tag in result:
                if isinstance(result[tag], list):
                    result[tag].append(child_data)
                else:
                    result[tag] = [result[tag], child_data]
            else:
                result[tag] = child_data

        return result

    def _get_detection_unique_id(self, detection: Union[Dict[str, Any], ET.Element], host_id: str) -> str:
        """
        Get a unique identifier for a detection.

        :param Union[Dict[str, Any], ET.Element] detection: Detection data as dictionary or XML Element
        :param str host_id: Host ID
        :return: Unique identifier string
        :rtype: str
        """
        # Convert XML to dict if needed
        if not isinstance(detection, dict) and hasattr(detection, "tag"):
            detection = self._xml_element_to_dict(detection)

        qid = detection.get("QID", "")
        unique_id = detection.get("UNIQUE_VULN_ID", f"{host_id}-{qid}")

        return unique_id

    def _convert_timestamp_to_date_str(self, timestamp_value: Any) -> str:
        """
        Convert a timestamp value to a date string with validation.

        :param Any timestamp_value: The timestamp value to convert
        :return: Date string in ISO format
        :raises ValueError: If the timestamp is not numeric
        :rtype: str
        """
        try:
            # Handle empty or None values early
            if not timestamp_value and timestamp_value != 0:
                raise ValueError(f"Invalid timestamp value: {timestamp_value}, defaulting to current datetime")

            # Convert to integer timestamp
            timestamp_int = normalize_timestamp(timestamp_value)

            s = date_obj(timestamp_int)
            if not s or timestamp_int == 0:
                raise ValueError(f"Invalid timestamp value: {timestamp_value}, defaulting to current datetime")
            return date_str(s)
        except ValueError as e:
            logger.error(f"Error converting timestamp to date string: {str(e)}")
            return get_current_datetime()

    def get_finding_status(self, status: Optional[str]) -> IssueStatus:
        """
        Convert the Qualys status to a RegScale issue status.

        :param Optional[str] status: The status from Qualys
        :return: RegScale IssueStatus
        :rtype: IssueStatus
        """
        if not status:
            return IssueStatus.Open

        # Normalize the status string to handle case variations
        normalized_status = status.strip().lower() if isinstance(status, str) else ""

        # Map to our status values
        if normalized_status in ("fixed", "closed"):
            return IssueStatus.Closed

        # Default to Open for any unknown status
        return IssueStatus.Open

    def create_vulnerability_from_finding(
        self, finding: IntegrationFinding, asset: regscale_models.Asset, scan_history: regscale_models.ScanHistory
    ) -> regscale_models.Vulnerability:
        """
        Override the parent method to add better debugging and ensure proper vulnerability mapping creation.

        :param IntegrationFinding finding: The integration finding
        :param regscale_models.Asset asset: The associated asset
        :param regscale_models.ScanHistory scan_history: The scan history
        :return: The created vulnerability
        :rtype: regscale_models.Vulnerability
        """
        logger.debug(f"Creating vulnerability from finding: {finding.title}")
        logger.debug(f"Asset ID: {asset.id}, Asset Name: {asset.name}")
        logger.debug(f"Scan History ID: {scan_history.id}")
        logger.debug(f"Plan ID: {self.plan_id}, Parent Module: {self.parent_module}")
        logger.debug(f"Is Component: {self.is_component}")

        # Call the parent method
        vulnerability = super().create_vulnerability_from_finding(finding, asset, scan_history)

        logger.debug(f"Created vulnerability with ID: {vulnerability.id}")
        logger.debug(f"Vulnerability parentId: {vulnerability.parentId}")
        logger.debug(f"Vulnerability parentModule: {vulnerability.parentModule}")

        # Verify the vulnerability mapping was created
        try:
            mappings = regscale_models.VulnerabilityMapping.find_by_vulnerability(vulnerability.id)
            logger.debug(f"Found {len(mappings)} vulnerability mappings for vulnerability {vulnerability.id}")
            for mapping in mappings:
                logger.debug(
                    f"Mapping - Asset ID: {mapping.assetId}, Scan ID: {mapping.scanId}, Security Plan ID: {mapping.securityPlanId}"
                )
        except Exception as e:
            logger.warning(f"Error checking vulnerability mappings: {e}")

        return vulnerability

    def handle_vulnerability(
        self,
        finding: IntegrationFinding,
        asset: Optional[regscale_models.Asset],
        scan_history: regscale_models.ScanHistory,
    ) -> Optional[int]:
        """
        Override parent method to ensure Qualys findings always create vulnerabilities.
        This ensures that Qualys vulnerabilities are properly populated in RegScale.

        :param IntegrationFinding finding: The integration finding
        :param Optional[regscale_models.Asset] asset: The associated asset
        :param regscale_models.ScanHistory scan_history: The scan history
        :rtype: Optional[int]
        :return: The vulnerability ID
        """
        # Check for required fields - either plugin_name or cve must be present
        if not (finding.plugin_name or finding.cve):
            logger.warning(
                f"Qualys: Skipping vulnerability creation - missing plugin_name and cve for finding {finding.external_id}"
            )
            return None

        # Ensure vulnerability creation is enabled for Qualys
        logger.debug(f"Qualys: Vulnerability creation setting: {self.vulnerability_creation}")
        if self.vulnerability_creation == "NoIssue":
            logger.debug(f"Qualys: Vulnerability creation disabled, skipping finding {finding.external_id}")
            return None

        # Create vulnerability using parent method
        logger.debug(f"Qualys: Calling parent handle_vulnerability for finding {finding.external_id}")
        vulnerability_id = super().handle_vulnerability(finding, asset, scan_history)

        if vulnerability_id:
            logger.debug(f"Qualys: Created vulnerability {vulnerability_id} for finding {finding.external_id}")
        else:
            logger.warning(f"Qualys: Failed to create vulnerability for finding {finding.external_id}")

        return vulnerability_id

    def set_severity_count_for_scan(self, severity: str, scan_history: regscale_models.ScanHistory) -> None:
        """
        Override parent method to ensure Qualys scan history severity counts are properly updated.
        This ensures that the vulnerability counts are accurately reflected in the scan history.

        :param str severity: Severity of the vulnerability
        :param regscale_models.ScanHistory scan_history: Scan history object
        :rtype: None
        """
        # Use parent method to update severity counts
        super().set_severity_count_for_scan(severity, scan_history)

    def create_scan_history(self) -> regscale_models.ScanHistory:
        """
        Override parent method to ensure Qualys scan history is properly created.
        This ensures that the scanning tool name is correctly set for Qualys scans.
        Also reuses existing scan history records for the same day and tool to avoid duplicates.

        :return: A newly created or reused ScanHistory object
        :rtype: regscale_models.ScanHistory
        """
        logger.debug(f"Creating scan history for plan {self.plan_id}, module {self.parent_module}")

        try:
            # Load existing scans for the plan/module
            existing_scans = regscale_models.ScanHistory.get_all_by_parent(
                parent_id=self.plan_id, parent_module=self.parent_module
            )

            # Normalize target date to date component only
            target_dt = self.scan_date if self.scan_date else get_current_datetime()
            target_date_only = target_dt.split("T")[0] if isinstance(target_dt, str) else str(target_dt)[:10]

            # Find an existing scan for today and this tool
            for scan in existing_scans:
                try:
                    if getattr(scan, "scanningTool", None) == SCANNING_TOOL_NAME and getattr(scan, "scanDate", None):
                        scan_date = str(scan.scanDate)
                        scan_date_only = scan_date.split("T")[0]
                        if scan_date_only == target_date_only:
                            # Reuse this scan history; refresh last updated
                            logger.debug(f"Reusing existing scan history {scan.id} for {target_date_only}")
                            scan.dateLastUpdated = get_current_datetime()
                            scan.lastUpdatedById = self.assessor_id
                            scan.save()
                            return scan
                except Exception:
                    # Skip any malformed scan records
                    continue

            # No existing same-day scan found, create new
            logger.debug("No existing scan history found for today, creating new one")
            scan_history = regscale_models.ScanHistory(
                parentId=self.plan_id,
                parentModule=self.parent_module,
                scanningTool=SCANNING_TOOL_NAME,  # Ensure proper scanning tool name
                scanDate=self.scan_date if self.scan_date else get_current_datetime(),
                createdById=self.assessor_id,
                lastUpdatedById=self.assessor_id,
                tenantsId=self.tenant_id,
                vLow=0,
                vMedium=0,
                vHigh=0,
                vCritical=0,
            ).create()

            logger.debug(f"Created new scan history with ID: {scan_history.id}")

            # Ensure the scan history is properly created and cached
            count = 0
            regscale_models.ScanHistory.delete_object_cache(scan_history)
            while not regscale_models.ScanHistory.get_object(object_id=scan_history.id) or count > 10:
                logger.info("Waiting for ScanHistory to be created...")
                time.sleep(1)
                count += 1
                regscale_models.ScanHistory.delete_object_cache(scan_history)

            return scan_history

        except Exception as e:
            logger.error(f"Error in create_scan_history: {e}")
            # Fallback: create new scan history using parent method
            return super().create_scan_history()
