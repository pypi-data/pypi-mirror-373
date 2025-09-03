"""
Grype scanner integration class.
"""

import logging
import os
from typing import (
    Any,
    Dict,
    Optional,
    Union,
    Tuple,
    TypeVar,
)

from pathlib import Path

from regscale.core.app.utils.parser_utils import safe_datetime_str
from regscale.integrations.jsonl_scanner_integration import JSONLScannerIntegration
from regscale.integrations.scanner_integration import IntegrationAsset, IntegrationFinding, issue_due_date
from regscale.models import IssueSeverity, AssetStatus, IssueStatus

logger = logging.getLogger("regscale")

# Define generic types for items that can be written to file
T = TypeVar("T")
ItemType = TypeVar("ItemType", IntegrationAsset, IntegrationFinding)


class GrypeIntegration(JSONLScannerIntegration):
    """Class for handling Grype scanner integration."""

    title: str = "Grype"
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
    ASSETS_FILE = "./artifacts/grype_assets.jsonl"
    FINDINGS_FILE = "./artifacts/grype_findings.jsonl"

    def __init__(self, *args, **kwargs):
        """
        Initialize the TrivyIntegration object.

        :param Any kwargs: Keyword arguments
        """
        kwargs["read_files_only"] = True
        kwargs["file_pattern"] = "*.json"
        self.disable_mapping = kwargs["disable_mapping"] = True
        self.is_component = kwargs.get("is_component", False)
        super().__init__(*args, **kwargs)

    def is_valid_file(self, data: Any, file_path: Union[Path, str]) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Check if a file is a valid Grype scan file.

        :param Any data: Data parsed from the file to validate
        :param Union[Path, str] file_path: Path to the file being processed
        :return: Tuple of (is_valid, data) where is_valid indicates validity and data is the validated content or None
        :rtype: Tuple[bool, Optional[Dict[str, Any]]]
        """
        try:
            # Check if this looks like a Grype scan file
            # Grype files should have matches array and source object
            if not isinstance(data, dict):
                logger.warning(f"File {file_path} is not a dict, skipping")
                return False, None

            if "matches" not in data:
                logger.warning(f"File {file_path} has no 'matches' key, skipping")
                return False, None

            if not isinstance(data.get("matches"), list):
                logger.warning(f"File {file_path} 'matches' is not a list, skipping")
                return False, None

            if "source" not in data:
                logger.warning(f"File {file_path} has no 'source' key, skipping")
                return False, None

            logger.debug(f"File {file_path} validated successfully")
            return True, data
        except Exception as e:
            logger.warning(f"Error reading file {file_path}: {str(e)}")
            return False, None

    def parse_asset(self, file_path: Union[Path, str], data: Dict[str, Any]) -> IntegrationAsset:
        """
        Parse a single asset from Grype scan data.

        :param Union[Path, str] file_path: Path to the file containing the asset data
        :param Dict[str, Any] data: The parsed JSON data
        :return: IntegrationAsset object
        :rtype: IntegrationAsset
        """
        source_target_data = data.get("source", {}).get("target", {})
        # Convert path to string if it's not already
        file_path_str = str(file_path)

        # Determine identifier from file name or data
        if "sha256-" in file_path_str:
            # Extract the sha256 from the filename
            base_name = os.path.basename(file_path_str)
            identifier = "sha256-" + base_name.split("sha256-")[1].split(".json")[0]
        else:
            identifier = source_target_data.get("imageID", "Unknown")

        return IntegrationAsset(
            identifier=identifier,
            name=identifier,
            ip_address="0.0.0.0",
            cpu=0,
            ram=0,
            status=AssetStatus.Active,
            asset_type="Other",
            asset_category="Software",
            operating_system=source_target_data.get("os", source_target_data.get("OS", "Linux")),
            notes=f"{os.path.basename(file_path_str)}",
            other_tracking_number=source_target_data.get("userInput", source_target_data.get("UserInput", "Unknown")),
            fqdn=source_target_data.get("userInput", source_target_data.get("UserInput", "Unknown")),
            parent_id=self.plan_id,
            parent_module="securityplans" if not self.is_component else "components",
        )

    def parse_finding(self, asset_identifier: str, data: Dict[str, Any], item: Dict[str, Any]) -> IntegrationFinding:
        """
        Parse a single finding from Grype scan data.

        Constructs a finding object by extracting and processing vulnerability details.

        :param str asset_identifier: Identifier of the asset this finding belongs to
        :param Dict[str, Any] data: Parsed scan data containing metadata
        :param Dict[str, Any] item: Individual finding data
        :return: Parsed finding object
        :rtype: IntegrationFinding
        """
        finding_info = self._extract_finding_info(item, data)
        artifact_info = self._extract_artifact_info(item)
        severity_info = self._determine_severity(finding_info)
        cvss_fields = self._get_cvss_fields(finding_info.get("cvss"))
        file_scan_date = safe_datetime_str(finding_info.get("descriptor", {}).get("timestamp", ""))
        if not self.scan_date:
            self.scan_date = file_scan_date
        evidence = self._build_evidence(artifact_info)
        observations = self._build_observations(finding_info)
        remediation_info = self._build_remediation_info(finding_info.get("fix"))

        severity = severity_info["severity"]

        return IntegrationFinding(
            title=(
                f"{severity_info.get('cve_id')}: {artifact_info.get('name', 'unknown')}"
                if severity_info.get("cve_id")
                else artifact_info.get("name", "unknown")
            ),
            description=severity_info["description"],
            severity=severity,
            status=IssueStatus.Open,
            cvss_v3_score=cvss_fields.get("V3Score"),
            cvss_v3_vector=cvss_fields.get("V3Vector") or "",
            cvss_v2_score=cvss_fields.get("V2Score"),
            cvss_v2_vector=cvss_fields.get("V2Vector") or "",
            plugin_name=artifact_info.get("name"),
            plugin_id=self.title,
            asset_identifier=asset_identifier,
            category="Vulnerability",
            cve=severity_info.get("cve_id"),
            control_labels=["CM-7", "SI-2"],
            evidence=evidence,
            observations=observations,
            identified_risk=f"Vulnerable {artifact_info.get('type', 'package')} detected: {artifact_info.get('name', 'unknown')} {artifact_info.get('version', 'unknown')}",
            recommendation_for_mitigation=remediation_info["remediation"],
            scan_date=self.scan_date,
            first_seen=file_scan_date,
            last_seen=self.scan_date,
            date_created=self.scan_date,
            vulnerability_type=finding_info.get("type"),
            rule_id=finding_info.get("id"),
            source_rule_id=finding_info.get("id"),
            remediation=remediation_info.get("remediation"),
            vulnerable_asset=f"{artifact_info.get('name', 'unknown')}:{artifact_info.get('version', 'unknown')}",
            security_check=finding_info.get("matcher"),
            external_id=finding_info.get("data_source"),
            installed_versions=artifact_info.get("version"),
            affected_os=finding_info.get("affected_os"),
            affected_packages=artifact_info.get("name"),
            image_digest=finding_info.get("manifest_digest"),
            package_path=artifact_info.get("purl"),
            build_version=finding_info.get("build_version"),
            fixed_versions=remediation_info.get("fixed_versions"),
            fix_status=remediation_info.get("fix_status"),
            due_date=issue_due_date(
                severity=severity, created_date=file_scan_date, title="grype", config=self.app.config
            ),
        )

    def _extract_finding_info(self, item: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract core finding information from Grype scan data.

        :param Dict[str, Any] item: Individual finding data
        :param Dict[str, Any] data: Parsed scan data containing metadata
        :return: Dictionary of extracted finding details
        :rtype: Dict[str, Any]
        """
        finding = item.get("vulnerability", {})
        source_target = data.get("source", {}).get("target", {})
        labels = source_target.get("labels", {})
        return {
            "id": finding.get("id", ""),
            "type": finding.get("type", ""),
            "data_source": finding.get("dataSource", ""),
            "namespace": finding.get("namespace", ""),
            "urls": finding.get("urls", []),
            "cvss": finding.get("cvss", []),
            "related_vulns": item.get("relatedVulnerabilities", []),
            "descriptor": data.get("descriptor", {}),
            "match_details": item.get("matchDetails", []),
            "description": finding.get("description", "No description available"),
            "build_version": str(labels.get("io.buildah.version", "")),
            "manifest_digest": source_target.get("manifestDigest", ""),
            "affected_os": labels.get("org.opencontainers.image.base.name")
            or f"{labels.get('org.opencontainers.image.ref.name', '')} {labels.get('org.opencontainers.image.version', '')}".strip(),
            "fix": finding.get("fix", {}),
            "severity": finding.get("severity", "UNKNOWN"),
            "matcher": item.get("matchDetails", [{}])[0].get("matcher", ""),
        }

    def _extract_artifact_info(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract artifact-related information from Grype finding data.

        :param Dict[str, Any] item: Individual finding data
        :return: Dictionary of artifact details
        :rtype: Dict[str, Any]
        """
        artifact = item.get("artifact", {})
        locations = [loc.get("path", "") for loc in artifact.get("locations", [])]
        return {
            "type": artifact.get("type", ""),
            "version": artifact.get("version", ""),
            "name": artifact.get("name", ""),
            "licenses": ", ".join(artifact.get("licenses", [])),
            "purl": artifact.get("purl", ""),
            "locations": locations,
        }

    def _determine_severity(self, finding_info: Dict[str, Any]) -> Dict[str, str]:
        """
        Determine the severity and related details for the finding.

        Prefers NVD data if available among related vulnerabilities.

        :param Dict[str, Any] finding_info: Extracted finding details
        :return: Dictionary with severity, CVE ID, and description
        :rtype: Dict[str, str]
        """
        severity_str = finding_info["severity"]
        cve_id = finding_info["id"]
        description = finding_info["description"]
        cvss = finding_info["cvss"]

        for vuln in finding_info["related_vulns"]:
            if "nvd" in vuln.get("dataSource", ""):
                cve_id = vuln.get("id", cve_id)
                severity_str = vuln.get("severity", severity_str)
                description = vuln.get("description", description)
                cvss = vuln.get("cvss", cvss)
                break

        severity_value = self.finding_severity_map.get(severity_str.upper(), IssueSeverity.High.value)
        try:
            severity = IssueSeverity(severity_value)
        except ValueError:
            severity = IssueSeverity.High

        return {"severity": severity, "cve_id": cve_id, "description": description, "cvss": cvss}

    def _build_evidence(self, artifact_info: Dict[str, Any]) -> str:
        """
        Build the evidence string for the finding.

        :param Dict[str, Any] artifact_info: Artifact details
        :return: Formatted evidence string
        :rtype: str
        """
        evidence = f"Found in {artifact_info['name']} {artifact_info['version']}"
        details = [
            f"type: {artifact_info['type']}" if artifact_info["type"] else "",
            f"Locations: {', '.join(artifact_info['locations'])}" if artifact_info["locations"] else "",
            f"Licenses: {artifact_info['licenses']}" if artifact_info["licenses"] else "",
            f"Package URL: {artifact_info['purl']}" if artifact_info["purl"] else "",
            f"References: {', '.join(artifact_info.get('urls', []))}" if artifact_info.get("urls", []) else "",
        ]
        return evidence + "\n".join(filter(None, details))

    def _build_observations(self, finding_info: Dict[str, Any]) -> str:
        """
        Build the observations string for the finding.

        :param Dict[str, Any] finding_info: Extracted finding details
        :return: Formatted observations string
        :rtype: str
        """
        match_type = finding_info["match_details"][0].get("type", "") if finding_info["match_details"] else ""
        matcher = finding_info["matcher"]
        return "\n".join(
            filter(
                None,
                [
                    f"Match type: {match_type}" if match_type else "",
                    f"Matcher: {matcher}" if matcher else "",
                    f"Data source: {finding_info['data_source']}" if finding_info["data_source"] else "",
                    f"Namespace: {finding_info['namespace']}" if finding_info["namespace"] else "",
                ],
            )
        )

    def _build_remediation_info(self, fix_info: Dict[str, Any]) -> Dict[str, str]:
        """
        Build remediation information for the finding.

        :param Dict[str, Any] fix_info: Fix details from the finding
        :return: Dictionary with remediation details
        :rtype: Dict[str, str]
        """
        state = fix_info.get("state", "No fix available")
        remediation = f"State: {state}"
        fixed_versions = ""
        if versions := fix_info.get("versions", []):
            fixed_versions = ", ".join(versions)
            remediation += f", Fixed versions: {fixed_versions}"
        return {"remediation": remediation, "fixed_versions": fixed_versions, "fix_status": state}

    def _get_findings_data_from_file(self, data: Dict[str, Any]) -> list:
        """
        Extract findings data from Grype file data.

        :param Dict[str, Any] data: The data from the Grype file
        :return: List of finding items
        :rtype: list
        """
        if not data or not isinstance(data, dict):
            return []

        matches = data.get("matches", [])
        if not isinstance(matches, list):
            return []
        return matches

    @staticmethod
    def _get_cvss_fields(cvss):
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

        i = 0
        while i < len(cvss):
            item = cvss[i]
            cvss_type = item.get("type", "")
            version = item.get("version")
            if "3." in version and cvss_type == "Primary":
                values["V3Score"] = item.get("metrics", {}).get("baseScore", None)
                values["V3Vector"] = item.get("vector", "")
            elif "2." in version and item.get("type") == "Primary":
                values["V2Score"] = item.get("metrics", {}).get("baseScore", None)
                values["V2Vector"] = item.get("vector", "")

            if values["V3Score"] is not None and values["V2Score"] is not None:
                break

            if values["V3Score"] is None and "3." in version and cvss_type == "Secondary":
                values["V3Score"] = item.get("metrics", {}).get("baseScore", None)
                values["V3Vector"] = item.get("vector", "")

            if values["V2Score"] is None and "2." in version and cvss_type == "Secondary":
                values["V2Score"] = item.get("metrics", {}).get("baseScore", None)
                values["V2Vector"] = item.get("vector", "")

            i += 1

        return values
