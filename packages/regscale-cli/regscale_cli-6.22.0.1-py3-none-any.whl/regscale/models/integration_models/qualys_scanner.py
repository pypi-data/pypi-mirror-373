import logging
from typing import Iterator

import xmltodict

from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.integrations.scanner_integration import (
    ScannerIntegration,
    IntegrationAsset,
    IntegrationFinding,
    issue_due_date,
    ScannerIntegrationType,
)
from regscale.models import regscale_models

logger = logging.getLogger(__name__)


class QualysTotalCloudIntegration(ScannerIntegration):
    """Qualys-specific implementation of ScannerIntegration"""

    title = "Qualys Total Cloud API Integration"
    type = ScannerIntegrationType.VULNERABILITY
    asset_identifier_field = "qualysId"

    finding_severity_map = {
        "0": regscale_models.IssueSeverity.NotAssigned,
        "1": regscale_models.IssueSeverity.Low,
        "2": regscale_models.IssueSeverity.Moderate,
        "3": regscale_models.IssueSeverity.Moderate,
        "4": regscale_models.IssueSeverity.High,
        "5": regscale_models.IssueSeverity.Critical,
    }

    finding_status_map = {
        "New": regscale_models.IssueStatus.Open,
        "Active": regscale_models.IssueStatus.Open,
        "Fixed": regscale_models.IssueStatus.Closed,
    }

    def __init__(self, plan_id: int, tenant_id: int = 1, **kwargs):
        super().__init__(plan_id, tenant_id, **kwargs)
        self.xml_data = kwargs.get("xml_data", "")

    def fetch_assets(self, *args, **kwargs) -> Iterator[IntegrationAsset]:
        """
        Fetches assets from the processed XML files

        :yields: Iterator[IntegrationAsset]
        """
        if not self.xml_data:
            logger.error("No XML data provided for Qualys integration")
            return

        parsed_data = xmltodict.parse(self.xml_data)
        host_list = parsed_data.get("HOST_LIST_VM_DETECTION_OUTPUT", {}).get("RESPONSE", {}).get("HOST_LIST")
        hosts = host_list.get("HOST", []) if host_list else []

        if isinstance(hosts, dict):
            hosts = [hosts]

        self.num_assets_to_process = len(hosts)

        for host in hosts:
            dns_data = host.get("DNS_DATA", {}) or {}
            asset = IntegrationAsset(
                name=host.get("DNS") or host.get("IP") or f"QualysAsset-{host.get('ID', 'Unknown')}",
                identifier=host.get("ID", ""),
                asset_type="Server",
                asset_category="IT",
                ip_address=host.get("IP"),
                fqdn=dns_data.get("FQDN"),
                operating_system=host.get("OS"),
                external_id=host.get("ID"),
                date_last_updated=host.get("LAST_SCAN_DATETIME"),
                mac_address=None,
                vlan_id=host.get("NETWORK_ID"),
                source_data={
                    "tracking_method": host.get("TRACKING_METHOD"),
                    "network_name": host.get("NETWORK_NAME"),
                    "last_vm_scanned_date": host.get("LAST_VM_SCANNED_DATE"),
                    "last_vm_scanned_duration": host.get("LAST_VM_SCANNED_DURATION"),
                    "last_vm_auth_scanned_date": host.get("LAST_VM_AUTH_SCANNED_DATE"),
                    "last_vm_auth_scanned_duration": host.get("LAST_VM_AUTH_SCANNED_DURATION"),
                },
            )
            yield asset

    def fetch_findings(self, *args, **kwargs) -> Iterator[IntegrationFinding]:
        """
        Fetches findings from the processed XML files

        :yields: Iterator[IntegrationFinding]
        """
        if not self.xml_data:
            logger.error("No XML data provided for Qualys integration")
            return
        parsed_data = xmltodict.parse(self.xml_data)
        host_list = parsed_data.get("HOST_LIST_VM_DETECTION_OUTPUT", {}).get("RESPONSE", {}).get("HOST_LIST")
        hosts = host_list.get("HOST", []) if host_list else []

        if isinstance(hosts, dict):
            hosts = [hosts]

        total_findings = self.calculate_total_findings(hosts)
        self.num_findings_to_process = total_findings

        for host in hosts:
            host_id = host.get("ID", "")
            detection_list = host.get("DETECTION_LIST", {})
            detections = detection_list.get("DETECTION", []) if detection_list else []

            if isinstance(detections, dict):
                detections = [detections]

            for detection in detections:
                severity = detection.get("SEVERITY", "0")
                finding = IntegrationFinding(
                    control_labels=[f"QID-{detection.get('QID', 'Unknown')}"],
                    title=f"Qualys Vulnerability QID-{detection.get('QID', 'Unknown')}",
                    category="Vulnerability",
                    plugin_name=f"QID-{detection.get('QID', 'Unknown')}",
                    severity=self.get_finding_severity(severity),
                    severity_int=int(severity),
                    description=detection.get("RESULTS", ""),
                    status=self.get_finding_status(detection.get("STATUS")),
                    asset_identifier=host_id,
                    external_id=detection.get("UNIQUE_VULN_ID", ""),
                    first_seen=detection.get("FIRST_FOUND_DATETIME"),
                    last_seen=detection.get("LAST_FOUND_DATETIME"),
                    plugin_id=detection.get("QID"),
                    ip_address=host.get("IP"),
                    dns=host.get("DNS"),
                    vulnerability_type="Vulnerability Scan",
                    due_date=issue_due_date(
                        severity=self.get_finding_severity(severity),
                        created_date=detection.get("FIRST_FOUND_DATETIME", get_current_datetime()),
                        title=self.title,
                        config=self.app.config if hasattr(self.app, "config") else None,
                    ),
                )
                yield finding

    @staticmethod
    def calculate_total_findings(hosts: list) -> int:
        """
        Calculate the total number of findings in the XML data

        :param list hosts: List of host dictionaries
        :return: The total number of findings
        :rtype: int
        """
        return sum(
            (
                len(host.get("DETECTION_LIST", {}).get("DETECTION", []))
                if isinstance(host.get("DETECTION_LIST", {}).get("DETECTION"), list)
                else 1 if host.get("DETECTION_LIST", {}).get("DETECTION") else 0
            )
            for host in hosts
        )
