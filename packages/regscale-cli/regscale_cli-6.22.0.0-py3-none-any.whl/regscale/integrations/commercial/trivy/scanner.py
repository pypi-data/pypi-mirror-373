"""
Trivy Scanner Integration for RegScale.

This module provides integration between Trivy scanner and RegScale,
allowing you to import Trivy scan results into RegScale as assets and findings.
"""

import logging
import os
from typing import Any, Dict, List, Optional, Union, Tuple, TypeVar

from pathlib import Path

from regscale.core.app.utils.parser_utils import safe_datetime_str
from regscale.integrations.jsonl_scanner_integration import JSONLScannerIntegration
from regscale.integrations.scanner_integration import IntegrationAsset, IntegrationFinding, issue_due_date
from regscale.models import IssueSeverity, AssetStatus, IssueStatus

logger = logging.getLogger("regscale")

# Define generic types for items that can be written to file
T = TypeVar("T")
ItemType = TypeVar("ItemType", IntegrationAsset, IntegrationFinding)


class TrivyIntegration(JSONLScannerIntegration):
    """Class for handling Trivy scanner integration."""

    title: str = "Trivy"
    asset_identifier_field: str = "otherTrackingNumber"
    finding_severity_map: Dict[str, Any] = {
        "CRITICAL": IssueSeverity.Critical.value,
        "HIGH": IssueSeverity.High.value,
        "MEDIUM": IssueSeverity.Moderate.value,
        "LOW": IssueSeverity.Low.value,
        "UNKNOWN": IssueSeverity.High.value,
        "NEGLIGIBLE": IssueSeverity.High.value,
    }

    # Constants for file paths
    ASSETS_FILE = "./artifacts/trivy_assets.jsonl"
    FINDINGS_FILE = "./artifacts/trivy_findings.jsonl"

    def __init__(self, *args, **kwargs):
        """
        Initialize the TrivyIntegration object.

        :param Any kwargs: Keyword arguments
        """
        kwargs["read_files_only"] = True
        kwargs["file_pattern"] = "*.json"
        self.disable_mapping = kwargs["disable_mapping"] = True
        self.scan_date = kwargs.get("scan_date") if "scan_date" in kwargs else None
        if self.scan_date:
            self.scan_date = self.clean_scan_date(self.scan_date)
        self.is_component = kwargs.get("is_component", False)
        super().__init__(*args, **kwargs)

    def is_valid_file(self, data: Any, file_path: Union[Path, str]) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Check if the provided data is a valid Trivy scan result.

        Validates that the data is from a Trivy JSON file with the required structure.
        Logs a warning with the file path and returns (False, None) if invalid.

        :param Any data: Data parsed from the file (string content when read_files_only is True, or file path otherwise)
        :param Union[Path, str] file_path: Path to the file being processed
        :return: Tuple of (is_valid, validated_data) where validated_data is the parsed JSON if valid
        :rtype: Tuple[bool, Optional[Dict[str, Any]]]
        """

        # Check Trivy-specific structure
        if not isinstance(data, dict):
            logger.warning(f"File {file_path} is not a dict, skipping")
            return False, None

        if "Results" not in data:
            logger.warning(f"File {file_path} has no 'Results' key, skipping")
            return False, None

        if not isinstance(data.get("Results"), list):
            logger.warning(f"File {file_path} 'Results' is not a list, skipping")
            return False, None

        if "Metadata" not in data:
            logger.warning(f"File {file_path} has no 'Metadata' key, skipping")
            return False, None

        return True, data

    def parse_asset(self, file_path: Union[Path, str], data: Dict[str, Any]) -> IntegrationAsset:
        """
        Parse a single asset from Trivy scan data.

        :param Union[Path, str] file_path: Path to the file containing the asset data
        :param Dict[str, Any] data: The parsed JSON data
        :return: IntegrationAsset object
        :rtype: IntegrationAsset
        """
        # Convert path to string if it's not already
        file_path_str = str(file_path)

        # Get metadata and OS information
        metadata = data.get("Metadata", {})
        os_data = metadata.get("OS", {})

        # Determine identifier from file name or data
        if "sha256-" in file_path_str:
            # Extract the sha256 from the filename
            base_name = os.path.basename(file_path_str)
            identifier = "sha256-" + base_name.split("sha256-")[1].split(".json")[0]
        else:
            identifier = metadata.get("ImageID", "Unknown")

        # Get artifact name for other tracking number and fqdn
        artifact_name = data.get("ArtifactName", identifier)

        # Create and return the asset
        return IntegrationAsset(
            identifier=identifier,
            name=identifier,
            ip_address="0.0.0.0",
            cpu=0,
            ram=0,
            status=AssetStatus.Active,
            asset_type="Other",
            asset_category="Software",
            operating_system=f"{os_data.get('Family', '')} {os_data.get('Name', '')}",
            notes=f"{os.path.basename(file_path_str)}",
            other_tracking_number=artifact_name,
            parent_id=self.plan_id,
            parent_module="securityplans" if not self.is_component else "components",
            fqdn=artifact_name,
        )

    def _get_findings_data_from_file(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract findings data from Trivy file data.

        :param Dict[str, Any] data: The data from the Trivy file
        :return: List of finding items
        :rtype: List[Dict[str, Any]]
        """
        if not data or not isinstance(data, dict):
            return []

        findings = []

        # Process all results
        for result in data.get("Results", []):
            if not isinstance(result, dict):
                continue

            # Extract vulnerabilities from the result
            vulnerabilities = result.get("Vulnerabilities", [])
            if not isinstance(vulnerabilities, list):
                continue

            # Add each vulnerability to the findings list
            findings.extend(vulnerabilities)

        return findings

    def parse_finding(self, asset_identifier: str, data: Dict[str, Any], item: Dict[str, Any]) -> IntegrationFinding:
        """
        Parse a single finding from Trivy scan data.

        :param str asset_identifier: The identifier of the asset this finding belongs to
        :param Dict[str, Any] data: The parsed JSON data (for metadata)
        :param Dict[str, Any] item: The finding data
        :return: IntegrationFinding object
        :rtype: IntegrationFinding
        """
        created_date = safe_datetime_str(data.get("CreatedAt"))
        # Get scan date from the finding or use current time
        if self.scan_date is None:
            self.scan_date = created_date

        # Process severity
        severity_str = item.get("Severity", "UNKNOWN")
        severity_value = self.finding_severity_map.get(severity_str.upper(), IssueSeverity.High.value)
        try:
            severity = IssueSeverity(severity_value)
        except ValueError:
            severity = IssueSeverity.High

        # Get CVSS fields
        cvss_fields = self._get_cvss_score(item)

        # Get data source information
        data_source = item.get("DataSource", {})
        plugin_name = data_source.get("Name", self.title)
        plugin_id = data_source.get("ID", self.title)

        metadata = data.get("Metadata", {})
        os_family = metadata.get("OS", {}).get("Family", "")
        os_name = metadata.get("OS", {}).get("Name", "")
        if os_family and os_name == "unknown":
            affected_os = "unknown"
        else:
            affected_os = f"{os_family} {os_name}"

        # Set image digest from artifact name
        artifact_name = data.get("ArtifactName", "")
        image_digest = ""
        if "@" in artifact_name:
            image_digest = artifact_name.split("@")[1]

        build_version = (
            metadata.get("ImageConfig", {}).get("config", {}).get("Labels", {}).get("io.buildah.version", "")
        )
        pkg_name = item.get("PkgName", "")
        cve = item.get("VulnerabilityID", "")

        # Create and return the finding
        return IntegrationFinding(
            title=f"{cve}: {pkg_name}" if cve else pkg_name,
            description=item.get("Description", "No description available"),
            severity=severity,
            status=IssueStatus.Open,
            cvss_v3_score=cvss_fields.get("V3Score"),
            cvss_v3_vector=cvss_fields.get("V3Vector") or "",
            cvss_v2_score=cvss_fields.get("V2Score"),
            cvss_v2_vector=cvss_fields.get("V2Vector") or "",
            plugin_name=plugin_name,
            plugin_id=plugin_id,
            asset_identifier=asset_identifier,
            cve=cve,
            first_seen=safe_datetime_str(data.get("CreatedAt")),
            last_seen=self.scan_date,
            scan_date=self.scan_date,
            date_created=item.get("CreatedAt"),
            category="Software",
            control_labels=[],
            installed_versions=item.get("InstalledVersion", ""),
            affected_os=affected_os,
            affected_packages=item.get("PkgID", ""),
            image_digest=image_digest,
            package_path=item.get("PkgIdentifier", {}).get("PURL", ""),
            build_version=build_version,
            fixed_versions=item.get("FixedVersion", ""),
            fix_status=item.get("Status", ""),
            due_date=issue_due_date(
                severity=severity, created_date=created_date, title="trivy", config=self.app.config
            ),
        )

    @staticmethod
    def _get_cvss_score(finding: Dict) -> dict:
        """
        Get the CVSS v3 and v2 scores and vectors from the cvss data.

        :param Dict finding: The cvss data
        :return: The CVSS fields
        :rtype: dict
        """
        values = {
            "V3Score": None,
            "V2Score": None,
            "V3Vector": None,
            "V2Vector": None,
        }

        if cvs := finding.get("CVSS"):
            if nvd := cvs.get("nvd"):
                values["V3Score"] = nvd.get("V3Score", None)
                values["V3Vector"] = nvd.get("V3Vector", None)
                values["V2Score"] = nvd.get("V2Score", None)
                values["V2Vector"] = nvd.get("V2Vector", None)
            elif redhat := cvs.get("redhat"):
                values["V3Score"] = redhat.get("V3Score", None)
                values["V3Vector"] = redhat.get("V3Vector", None)
                values["V2Score"] = redhat.get("V2Score", None)
                values["V2Vector"] = redhat.get("V2Vector", None)
            elif ghsa := cvs.get("ghsa"):
                values["V3Score"] = ghsa.get("V3Score", None)
                values["V3Vector"] = ghsa.get("V3Vector", None)
                values["V2Score"] = ghsa.get("V2Score", None)
                values["V2Vector"] = ghsa.get("V2Vector", None)
            elif bitnami := cvs.get("bitnami"):
                values["V3Score"] = bitnami.get("V3Score", None)
                values["V3Vector"] = bitnami.get("V3Vector", None)
                values["V2Score"] = bitnami.get("V2Score", None)
                values["V2Vector"] = bitnami.get("V2Vector", None)
        return values
