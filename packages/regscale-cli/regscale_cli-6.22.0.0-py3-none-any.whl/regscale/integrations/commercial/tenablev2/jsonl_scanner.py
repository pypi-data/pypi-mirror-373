"""
Integration class for Tenable SC vulnerability scanning using JSONLScannerIntegration.

This module provides a direct implementation of JSONLScannerIntegration for Tenable SC,
optimized for processing large volumes of scan data.
"""

import dataclasses
import inspect
import json
import logging
import os
import re
import sys
import tempfile
from datetime import datetime
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union

from pathlib import Path

from regscale.core.app.utils.app_utils import epoch_to_datetime, get_current_datetime
from regscale.core.app.utils.file_utils import find_files
from regscale.exceptions.validation_exception import ValidationException
from regscale.integrations.commercial.tenablev2.authenticate import gen_tsc
from regscale.integrations.commercial.tenablev2.utils import get_filtered_severities
from regscale.integrations.commercial.tenablev2.variables import TenableVariables
from regscale.integrations.integration_override import IntegrationOverride
from regscale.integrations.jsonl_scanner_integration import JSONLScannerIntegration
from regscale.integrations.scanner_integration import IntegrationAsset, IntegrationFinding, issue_due_date
from regscale.integrations.transformer.data_transformer import DataTransformer
from regscale.integrations.variables import ScannerVariables
from regscale.models import regscale_models, AssetStatus, AssetType
from regscale.models.integration_models.tenable_models.models import TenableAsset

logger = logging.getLogger("regscale")

FILE_TYPE = ".jsonl"
UNKNOWN_PLUGIN = "Unknown Plugin"


class TenableSCJsonlScanner(JSONLScannerIntegration):
    """
    Integration class for Tenable SC vulnerability scanning using JSONLScannerIntegration.

    This class provides functionality for processing Tenable SC data files and
    syncing assets and findings to RegScale.
    """

    # Class attributes - customized for Tenable SC
    title: str = "Tenable SC Vulnerability Scanner"
    asset_identifier_field: str = "tenableId"

    # Custom file paths for Tenable SC data
    ASSETS_FILE = "./artifacts/tenable_sc_assets.jsonl"
    FINDINGS_FILE = "./artifacts/tenable_sc_findings.jsonl"
    file_pattern = "sc_*.*"  # Match both JSON and JSONL files

    # Severity mapping dictionary
    finding_severity_map = {
        "5": regscale_models.IssueSeverity.Critical,  # Critical
        "4": regscale_models.IssueSeverity.High,  # High
        "3": regscale_models.IssueSeverity.Moderate,  # Medium
        "2": regscale_models.IssueSeverity.Low,  # Low
        "1": regscale_models.IssueSeverity.Low,  # Info
        "0": regscale_models.IssueSeverity.Low,  # None
        "Info": regscale_models.IssueSeverity.NotAssigned,
        "Low": regscale_models.IssueSeverity.Low,
        "Medium": regscale_models.IssueSeverity.Moderate,
        "High": regscale_models.IssueSeverity.High,
        "Critical": regscale_models.IssueSeverity.Critical,
    }

    def __init__(
        self,
        plan_id: int,
        tenant_id: int = 1,
        scan_date: datetime = None,
        query_id: int = None,
        batch_size: int = None,
        optimize_memory: bool = True,
        force_download: bool = False,
        **kwargs,
    ):
        """
        Initialize the Tenable SC JSONLScannerIntegration.

        :param int plan_id: The ID of the security plan
        :param int tenant_id: The ID of the tenant, defaults to 1
        :param datetime scan_date: The date of the scan, defaults to None
        :param int query_id: The ID of the query to use, defaults to None
        :param int batch_size: Batch size for API requests, defaults to 1000
        :param bool optimize_memory: Whether to optimize memory usage, defaults to True
        :param bool force_download: Whether to force download data from Tenable SC, defaults to False
        """
        # Set specific file pattern for Tenable SC files
        kwargs["file_pattern"] = self.file_pattern
        kwargs["read_files_only"] = True
        # Pass scan_date through kwargs to parent class
        if scan_date:
            kwargs["scan_date"] = scan_date

        super().__init__(plan_id=plan_id, tenant_id=tenant_id, **kwargs)

        self.query_id = query_id
        self.batch_size = batch_size or 1000
        self.optimize_memory = optimize_memory
        self.force_download = force_download
        self.auth_token = None
        self.base_url = None
        self.username = None
        self.password = None
        self.verify_ssl = None
        self.client = None
        self.scan_date = scan_date or get_current_datetime()
        self.closed_count = 0
        self.app = kwargs.get("app")
        self.temp_dir = None

    def authenticate(self) -> bool:
        """
        Authenticate to Tenable SC.

        :return: True if authentication was successful, False otherwise
        :rtype: bool
        """
        try:
            # Log Tenable URL and other settings
            logger.info(f"Authenticating to Tenable SC with URL: {TenableVariables.tenableUrl}")
            logger.info(f"Batch size: {self.batch_size}")

            # Log other relevant connection settings
            ssl_verify = getattr(ScannerVariables, "sslVerify", True)
            logger.info(f"Using SSL verification: {ssl_verify}")

            # Initialize the Tenable SC client
            self.client = gen_tsc()

            # Test authentication by making a simple API call
            if self.client:
                # Try a simple API call to verify connection
                try:
                    # Get Tenable SC version to verify connection - fixed to use the proper API
                    status = self.client.status.status()  # Use status.status() instead of status()
                    version = status.get("version", "unknown")
                    logger.info(f"Successfully authenticated to Tenable SC (version: {version})")

                    # Set client timeout for large queries if supported
                    if hasattr(self.client, "timeout"):
                        logger.info("Setting increased timeout for large queries")
                        self.client.timeout = 300  # 5 minutes

                    return True
                except Exception as e:
                    logger.error(f"Authentication successful but API test failed: {str(e)}", exc_info=True)
                    # Still return True as we authenticated, even if the test call failed
                    return True
            else:
                logger.error("Failed to create Tenable SC client")
                return False
        except Exception as e:
            logger.error(f"Error authenticating to Tenable SC: {str(e)}", exc_info=True)
            return False

    def find_valid_files(self, path: Union[Path, str]) -> Iterator[Tuple[Union[Path, str], Dict[str, Any]]]:
        """
        Find all valid Tenable SC data files in the given path.

        :param Union[Path, str] path: Path to search for files
        :return: Iterator of (file_path, data) tuples
        :rtype: Iterator[Tuple[Union[Path, str], Dict[str, Any]]]
        """
        if not path or path == "":
            # If no specific path provided, search artifacts directory
            path = self.create_artifacts_dir()

        # Add debug logging
        logger.info(f"Looking for files in path: {path}")

        # Add support for JSONL files
        jsonl_pattern = "sc_*.jsonl"

        # Find both JSON and JSONL files
        found_files = 0

        # First yield regular JSON files using parent implementation
        for file_data in super().find_valid_files(path):
            found_files += 1
            if isinstance(file_data, tuple) and len(file_data) >= 2:
                file_path = file_data[0]
                logger.info(f"Found valid file: {file_path}")

                # Check if it's an assets file and log details
                str_path = str(file_path)
                if "sc_assets" in str_path:
                    data = file_data[1]
                    if data and isinstance(data, dict):
                        assets = data.get("response", {}).get("usable", [])
                        logger.info(f"Assets file contains {len(assets)} assets")
            yield file_data

        # Now look for JSONL files
        for file_path in find_files(path, jsonl_pattern):
            found_files += 1
            logger.info(f"Found JSONL file: {file_path}")

            # For JSONL files, create an empty dict as placeholder
            # Actual processing is handled in _process_jsonl_findings
            yield file_path, {}

        logger.info(f"Total valid files found: {found_files}")

    def is_valid_file(self, data: Any, file_path: Union[Path, str]) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Validate Tenable SC data file structure.

        :param Any data: Data from the file
        :param Union[Path, str] file_path: Path to the file
        :return: Tuple of (is_valid, validated_data)
        :rtype: Tuple[bool, Optional[Dict[str, Any]]]
        """
        # Handle JSONL files separately
        str_path = str(file_path)
        if str_path.endswith(FILE_TYPE):
            logger.info(f"Validating JSONL file: {file_path}")
            # For JSONL files, we just verify the file exists and is readable
            if os.path.exists(str_path) and os.path.getsize(str_path) > 0:
                return True, {}
            return False, None

        # First use parent validation to ensure it's a non-empty dict
        is_valid, data = super().is_valid_file(data, file_path)
        if not is_valid or not data:
            return False, None

        # Now check for Tenable SC specific structures
        if "sc_assets" in str_path:
            if "response" not in data or "usable" not in data.get("response", {}):
                logger.warning(f"Invalid Tenable SC assets file format: {file_path}")
                return False, None
            return True, data

        # Validate vulnerabilities file
        if "sc_vulns" in str_path:
            if "response" not in data or "results" not in data.get("response", {}):
                logger.warning(f"Invalid Tenable SC vulnerabilities file format: {file_path}")
                return False, None
            return True, data

        # File doesn't match our expected patterns
        logger.warning(f"File doesn't appear to be a Tenable SC data file: {file_path}")
        return False, None

    def parse_asset(self, file_path: Union[Path, str], data: Dict[str, Any]) -> IntegrationAsset:
        """
        Parse a Tenable SC asset from source data.

        :param Union[Path, str] file_path: Path to the file
        :param Dict[str, Any] data: Parsed data
        :return: IntegrationAsset object
        :rtype: IntegrationAsset
        """
        if not data:
            logger.warning("Empty data provided to parse_asset")
            # Return a minimal valid asset to avoid NoneType errors
            return IntegrationAsset(
                identifier="unknown",
                name="Unknown Asset",
                ip_address="",
                status=AssetStatus.Active,
                asset_type="Other",
                asset_category="Software",
                parent_id=self.plan_id,
                parent_module=regscale_models.SecurityPlan.get_module_slug(),
            )

        try:
            # Attempt to convert to TenableAsset object if from vulnerability data
            if "response" in data and "results" in data.get("response", {}):
                results = data.get("response", {}).get("results", [])
                if results:
                    try:
                        vuln_data = TenableAsset(**results[0])
                        return self.to_integration_asset(
                            vuln_data, app=self.app, override=IntegrationOverride(self.app)
                        )
                    except Exception as e:
                        logger.warning(f"Could not parse vulnerability as TenableAsset: {str(e)}")
                        # Continue to parse as a basic asset instead of returning None

            # If we reach here, it's either an assets file or no valid data was found
            return self._parse_asset_from_assets_file(data)
        except Exception as e:
            logger.error(f"Error parsing Tenable SC asset: {str(e)}", exc_info=True)
            # Return a minimal valid asset to avoid NoneType errors
            return IntegrationAsset(
                identifier="error",
                name=f"Error Asset ({str(file_path)})",
                ip_address="",
                status=AssetStatus.Active,
                asset_type="Other",
                asset_category="Software",
                parent_id=self.plan_id,
                parent_module=regscale_models.SecurityPlan.get_module_slug(),
            )

    def _parse_asset_from_assets_file(self, data: Dict[str, Any]) -> IntegrationAsset:
        """
        Parse asset from a Tenable SC assets file.

        :param Dict[str, Any] data: Assets file data
        :return: IntegrationAsset object
        :rtype: IntegrationAsset
        """
        # Get first asset from usable list
        assets = data.get("response", {}).get("usable", [])
        if not assets:
            logger.warning("No assets found in Tenable SC assets file")
            return IntegrationAsset(
                identifier="unknown",
                name="Unknown Asset",
                ip_address="",
                status=AssetStatus.ACTIVE,
                asset_type="Other",
                asset_category="Software",
                parent_id=self.plan_id,
                parent_module=regscale_models.SecurityPlan.get_module_slug(),
            )

        asset = assets[0]

        # Extract asset data
        asset_id = asset.get("id", "")
        asset_name = asset.get("name", "")

        if not asset_id:
            logger.warning("Asset is missing ID, using default ID")
            asset_id = "missing_id"

        # Extract IP information if available
        ip_info = ""
        definition = asset.get("definition", "")
        if "ip=" in definition:
            ip_parts = definition.split("ip=")[1].split("&")[0]
            ip_info = ip_parts.replace("%3B", ";")

        # Use IP address as the identifier for consistency
        # If we can extract an IP from the definition, use that as the identifier
        identifier = ip_info if ip_info else asset_id

        return IntegrationAsset(
            identifier=identifier,
            name=asset_name or f"Asset {asset_id}",
            ip_address=ip_info,
            parent_id=self.plan_id,
            parent_module=regscale_models.SecurityPlan.get_module_slug(),
            asset_owner_id=ScannerVariables.userId,
            asset_category=regscale_models.AssetCategory.Hardware,
            asset_type=regscale_models.AssetType.Other,
            status=AssetStatus.ACTIVE,
            date_last_updated=get_current_datetime(),
        )

    def to_integration_asset(self, asset: TenableAsset, **kwargs: dict) -> IntegrationAsset:
        """Converts a TenableAsset object to an IntegrationAsset object

        :param TenableAsset asset: The Tenable SC asset
        :param dict **kwargs: Additional keyword arguments
        :return: An IntegrationAsset object
        :rtype: IntegrationAsset
        """
        override = kwargs.get("override")

        validated_match = None
        if override:
            validated_match = override.field_map_validation(obj=asset, model_type="asset")

        # Use IP as the primary identifier for consistency between assets and findings
        asset_identifier = asset.ip
        # If no IP, fall back to other identifiers
        if not asset_identifier:
            asset_identifier = validated_match or asset.dnsName or asset.dns or "unknown"

        name = asset.dnsName or asset.ip

        return IntegrationAsset(
            name=name,
            identifier=asset_identifier,
            ip_address=asset.ip,
            mac_address=asset.macAddress,
            asset_owner_id=ScannerVariables.userId,
            status=(
                AssetStatus.ACTIVE
                if getattr(asset, "family", None) and getattr(asset.family, "type", None)
                else AssetStatus.Inactive
            ),
            asset_type=AssetType.Other,
            asset_category="Hardware",
        )

    def parse_finding(
        self, asset_identifier: str, data: Dict[str, Any], item: Dict[str, Any]
    ) -> Optional[IntegrationFinding]:
        """
        Parse a finding from a Tenable SC vulnerability.

        :param str asset_identifier: Asset identifier
        :param Dict[str, Any] data: Asset data
        :param Dict[str, Any] item: Finding data (vulnerability)
        :return: IntegrationFinding object
        :rtype: Optional[IntegrationFinding]
        """
        if not item:
            return None

        try:
            # Try to convert to TenableAsset for consistent processing
            try:
                vuln = TenableAsset(**item)
            except Exception as e:
                logger.warning(f"Could not create TenableAsset from finding data: {str(e)}")
                # Get the IP from the vulnerability item directly rather than using passed asset_identifier
                finding_asset_id = item.get("ip", asset_identifier)

                # Create a minimal finding since TenableAsset creation failed
                return IntegrationFinding(
                    control_labels=[],  # Add an empty list for control_labels
                    title=item.get("pluginName", "Unknown Finding"),
                    description=item.get("description", "No description available"),
                    severity=regscale_models.IssueSeverity.Low,
                    status=regscale_models.IssueStatus.Open,
                    asset_identifier=finding_asset_id,  # Use the IP from the finding
                    category="Vulnerability",
                    scan_date=self.scan_date,
                    plugin_name=item.get("pluginName", UNKNOWN_PLUGIN),
                )

            # Use the integration_mapping if available
            integration_mapping = IntegrationOverride(self.app) if self.app else None

            # Process findings similar to SC scanner
            findings = self.parse_findings(vuln, integration_mapping)

            if findings:
                return findings[0]  # Return the first finding

            # If no findings were created, return a basic finding
            # Get the IP from the vulnerability directly rather than using passed asset_identifier
            finding_asset_id = vuln.ip or asset_identifier
            logger.debug(item)
            return IntegrationFinding(
                title=item.get("pluginName", "Unknown Finding"),
                description=item.get("description", "No description available"),
                severity=regscale_models.IssueSeverity.Low,
                status=regscale_models.IssueStatus.Open,
                asset_identifier=finding_asset_id,  # Use the IP from the finding
                category="Vulnerability",
                scan_date=self.scan_date,
                plugin_name=item.get("pluginName", UNKNOWN_PLUGIN),
                control_labels=item.get("controlLabels", []),
            )

        except Exception as e:
            logger.error(f"Error parsing Tenable SC finding: {str(e)}", exc_info=True)
            # Return a minimal finding on error
            return IntegrationFinding(
                control_labels=[],  # Add an empty list for control_labels
                title="Error Finding",
                description=f"Error parsing finding: {str(e)}",
                severity=regscale_models.IssueSeverity.Low,
                status=regscale_models.IssueStatus.Open,
                asset_identifier=asset_identifier,
                category="Vulnerability",
                scan_date=self.scan_date,
                plugin_name=UNKNOWN_PLUGIN,
            )

    def parse_findings(self, vuln: TenableAsset, integration_mapping: Any) -> List[IntegrationFinding]:
        """
        Parses a TenableAsset into an IntegrationFinding object

        :param TenableAsset vuln: The Tenable SC finding
        :param Any integration_mapping: The IntegrationMapping object
        :return: A list of IntegrationFinding objects
        :rtype: List[IntegrationFinding]
        """
        findings = []
        try:
            severity = self.finding_severity_map.get(vuln.severity.name, regscale_models.IssueSeverity.Low)
            cve_set = set(vuln.cve.split(",")) if vuln.cve else set()
            if severity in get_filtered_severities():
                if cve_set:
                    for cve in cve_set:
                        findings.append(
                            self._create_finding(vuln=vuln, cve=cve, integration_mapping=integration_mapping)
                        )
                else:
                    findings.append(self._create_finding(vuln=vuln, cve="", integration_mapping=integration_mapping))
        except (KeyError, TypeError, ValueError) as e:
            logger.error("Error parsing Tenable SC finding: %s", str(e), exc_info=True)

        return findings

    def _create_finding(
        self, vuln: TenableAsset, cve: str, integration_mapping: IntegrationOverride
    ) -> IntegrationFinding:
        """
        Helper method to create an IntegrationFinding object

        :param TenableAsset vuln: The Tenable SC finding
        :param str cve: The CVE identifier
        :param IntegrationOverride integration_mapping: The IntegrationMapping object
        :return: An IntegrationFinding object
        :rtype: IntegrationFinding
        """

        # Extract helper method to simplify the main method
        def getter(field_name: str) -> Optional[str]:
            """
            Helper method to get the field value from the integration mapping

            :param str field_name: The field name to get the value for
            :return: The field value
            :rtype: Optional[str]
            """
            if integration_mapping and (val := integration_mapping.load("tenable_sc", field_name)):
                return getattr(vuln, val, None)
            return None

        # Get asset identifier
        asset_identifier = self._get_asset_identifier(vuln, integration_mapping)

        # Get CVSS scores
        cvss_scores = self.get_cvss_scores(vuln)

        # Map severity
        severity = self.finding_severity_map.get(vuln.severity.name, regscale_models.IssueSeverity.Low)

        # Extract version information
        installed_versions_str, fixed_versions_str, package_path_str = self._extract_version_info(vuln)

        # Handle dates
        first_seen = epoch_to_datetime(vuln.firstSeen) if vuln.firstSeen else self.scan_date
        last_seen = epoch_to_datetime(vuln.lastSeen) if vuln.lastSeen else self.scan_date

        # Create finding title
        title = self._create_finding_title(vuln, cve, getter)

        # Create and return the finding
        return IntegrationFinding(
            control_labels=[],  # Add an empty list for control_labels
            category="Tenable SC Vulnerability",  # Add a default category
            dns=vuln.dnsName,
            title=title,
            description=getter("description") or (vuln.description or vuln.pluginInfo),
            severity=severity,
            status=regscale_models.IssueStatus.Open,  # Findings of > Low are considered as FAIL
            asset_identifier=asset_identifier,
            external_id=vuln.pluginID,  # Weakness Source Identifier
            first_seen=first_seen,
            last_seen=last_seen,
            date_created=first_seen,
            date_last_updated=last_seen,
            recommendation_for_mitigation=vuln.solution,
            cve=cve,
            cvss_v3_score=cvss_scores.get("cvss_v3_base_score", 0.0),
            cvss_score=cvss_scores.get("cvss_v3_base_score", 0.0),
            cvss_v3_vector=vuln.cvssV3Vector,
            cvss_v2_score=cvss_scores.get("cvss_v2_base_score", 0.0),
            cvss_v2_vector=vuln.cvssVector,
            vpr_score=float(vuln.vprScore) if vuln.vprScore else None,
            comments=vuln.cvssV3Vector,
            plugin_id=vuln.pluginID,
            plugin_name=vuln.pluginName,
            rule_id=vuln.pluginID,
            rule_version=vuln.pluginName,
            basis_for_adjustment="Tenable SC import",
            vulnerability_type="Tenable SC Vulnerability",
            vulnerable_asset=vuln.dnsName,
            build_version="",
            affected_os=vuln.operatingSystem,
            affected_packages=vuln.pluginName,
            package_path=package_path_str,
            installed_versions=installed_versions_str,
            fixed_versions=fixed_versions_str,
            fix_status="",
            scan_date=self.scan_date,
            due_date=issue_due_date(
                severity=severity, created_date=first_seen, title="tenable", config=self.app.config if self.app else {}
            ),
        )

    def _get_asset_identifier(self, vuln: TenableAsset, integration_mapping: IntegrationOverride) -> str:
        """
        Extract asset identifier from vulnerability data

        :param TenableAsset vuln: The Tenable SC finding
        :param IntegrationOverride integration_mapping: The IntegrationMapping object
        :return: Asset identifier
        :rtype: str
        """
        validated_match = None
        if integration_mapping:
            validated_match = integration_mapping.field_map_validation(obj=vuln, model_type="asset")

        # Use IP as the primary identifier for consistency between assets and findings
        if vuln.ip:
            return vuln.ip

        # If no IP, fall back to other identifiers
        return validated_match or vuln.dnsName or vuln.dns or "unknown"

    def _extract_version_info(self, vuln: TenableAsset) -> Tuple[str, str, str]:
        """
        Extract version information from vulnerability plugin text

        :param TenableAsset vuln: The Tenable SC finding
        :return: Tuple of (installed_versions, fixed_versions, package_path)
        :rtype: Tuple[str, str, str]
        """
        installed_versions_str = ""
        fixed_versions_str = ""
        package_path_str = ""

        if not hasattr(vuln, "pluginText"):
            return installed_versions_str, fixed_versions_str, package_path_str

        plugin_text = vuln.pluginText

        # Extract installed package information
        if "Installed package" in plugin_text:
            installed_versions = re.findall(r"Installed package\s*:\s*(\S+)", plugin_text)
            installed_versions_str = ", ".join(installed_versions)
        elif "Installed version" in plugin_text:
            installed_versions = re.findall(r"Installed version\s*:\s*(.+)", plugin_text)
            installed_versions_str = ", ".join(installed_versions)

        # Extract fixed package information
        if "Fixed package" in plugin_text:
            fixed_versions = re.findall(r"Fixed package\s*:\s*(\S+)", plugin_text)
            fixed_versions_str = ", ".join(fixed_versions)
        elif "Fixed version" in plugin_text:
            fixed_versions = re.findall(r"Fixed version\s*:\s*(.+)", plugin_text)
            fixed_versions_str = ", ".join(fixed_versions)

        # Extract package path
        if "Path" in plugin_text:
            package_path = re.findall(r"Path\s*:\s*(\S+)", plugin_text)
            package_path_str = ", ".join(package_path)

        return installed_versions_str, fixed_versions_str, package_path_str

    def _create_finding_title(self, vuln: TenableAsset, cve: str, getter_func) -> str:
        """
        Create a title for the finding

        :param TenableAsset vuln: The Tenable SC finding
        :param str cve: The CVE identifier
        :param callable getter_func: Function to get mapped fields
        :return: Finding title
        :rtype: str
        """
        # First try to get title from mapping
        title = getter_func("title")
        if title:
            return title

        # Fall back to constructing title from CVE and synopsis
        if cve:
            return f"{cve}: {vuln.synopsis}"

        # Last resort: use synopsis or plugin name
        return vuln.synopsis or vuln.pluginName

    def get_cvss_scores(self, vuln: TenableAsset) -> dict:
        """
        Returns the CVSS score for the finding

        :param TenableAsset vuln: The Tenable SC finding
        :return: The CVSS score
        :rtype: float
        """
        res = {}
        try:
            res["cvss_v3_base_score"] = float(vuln.cvssV3BaseScore) if vuln.cvssV3BaseScore else 0.0
            res["cvss_v2_base_score"] = float(vuln.baseScore) if vuln.baseScore else 0.0
        except (ValueError, TypeError):
            res["cvss_v3_base_score"] = 0.0
            res["cvss_v2_base_score"] = 0.0

        return res

    def process_source_files(self, file_paths: List[str], assets_output_file: str, findings_output_file: str) -> None:
        """
        Process source files to extract assets and findings.

        :param List[str] file_paths: List of file paths to process
        :param str assets_output_file: Path to write assets to
        :param str findings_output_file: Path to write findings to
        """
        # Ensure output directories exist
        os.makedirs(os.path.dirname(assets_output_file), exist_ok=True)
        os.makedirs(os.path.dirname(findings_output_file), exist_ok=True)

        # Prepare output files
        asset_info = self._prepare_output_file(assets_output_file, True, "asset")
        finding_info = self._prepare_output_file(findings_output_file, True, "finding")

        # Process each file
        for file_path in file_paths:
            file_path_str = str(file_path)
            logger.info(f"Processing file: {file_path_str}")

            try:
                # Read and parse the file
                with open(file_path_str, "r") as f:
                    data = json.load(f)

                # Validate the file
                is_valid, validated_data = self.is_valid_file(data, file_path_str)
                if not is_valid or validated_data is None:
                    logger.warning(f"Invalid file: {file_path_str}")
                    continue

                # Process assets or findings based on file path
                if "sc_assets" in file_path_str:
                    # Process assets file
                    with open(assets_output_file, asset_info.get("mode", "w")) as output_f:
                        self._process_asset_file(
                            file_path_str, validated_data, output_f, asset_info.get("existing_items", {})
                        )
                    # Use append mode for subsequent files
                    asset_info["mode"] = "a"

                elif "sc_vulns" in file_path_str:
                    # Process findings file
                    with open(findings_output_file, finding_info.get("mode", "w")) as output_f:
                        self._process_finding_file(
                            file_path_str, validated_data, output_f, finding_info.get("existing_items", {})
                        )
                    # Use append mode for subsequent files
                    finding_info["mode"] = "a"

            except Exception as e:
                logger.error(f"Error processing file {file_path_str}: {str(e)}", exc_info=True)

    def _download_sc_data(self, output_dir: str) -> List[str]:
        """
        Download Tenable SC data using the SC client and save to files.

        This method fetches vulnerabilities from Tenable SC API
        using the Tenable SC client library for proper authentication and
        API access. Assets are derived from the vulnerability data.

        :param str output_dir: Directory to save the files to
        :return: List of file paths that were created
        :rtype: List[str]
        """
        logger.info("Downloading Tenable SC data...")
        files_created = []

        try:
            # Ensure authentication and directory setup
            if not self._initialize_client_and_directory(output_dir):
                return files_created

            # Define output files
            vulns_file = os.path.join(output_dir, "sc_vulns.json")

            # Fetch vulnerabilities if query_id is available
            files_created = self._fetch_vulnerabilities(vulns_file, files_created)

            # Create assets file if needed
            assets_file = os.path.join(output_dir, "sc_assets.json")
            if not os.path.exists(assets_file):
                self._create_assets_file_from_vulns(assets_file, vulns_file, files_created)

        except Exception as e:
            logger.error(f"Error downloading Tenable SC data: {str(e)}", exc_info=True)

        return files_created

    def _initialize_client_and_directory(self, output_dir: str) -> bool:
        """
        Initialize the client and ensure the output directory exists

        :param str output_dir: Directory to save files to
        :return: True if initialization successful, False otherwise
        :rtype: bool
        """
        # Ensure client is initialized
        if not self.client:
            logger.info("Authenticating to Tenable SC...")
            if not self.authenticate():
                logger.error("Failed to authenticate to Tenable SC")
                return False

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Output directory: {output_dir}")
        return True

    def _fetch_vulnerabilities(self, vulns_file: str, files_created: List[str]) -> List[str]:
        """
        Fetch vulnerabilities from Tenable SC

        :param str vulns_file: Path to save vulnerabilities to
        :param List[str] files_created: Current list of created files
        :return: Updated list of created files
        :rtype: List[str]
        """
        # Make a copy of the list to avoid modifying the original
        updated_files = files_created.copy()

        if not self.query_id:
            logger.warning("No query_id provided, skipping vulnerability download")
            return updated_files

        logger.info(f"Fetching vulnerabilities using query ID: {self.query_id}")
        vulns_count = self._fetch_vulns_with_client(vulns_file, self.query_id)

        if vulns_count > 0:
            updated_files.append(vulns_file)
            logger.info(f"Successfully downloaded {vulns_count} vulnerabilities to {vulns_file}")
        else:
            # Create an empty file to avoid errors later
            self._create_empty_vulns_file(vulns_file, updated_files)

        return updated_files

    def _create_empty_vulns_file(self, vulns_file: str, files_created: List[str]) -> None:
        """
        Create an empty vulnerabilities file

        :param str vulns_file: Path to create file at
        :param List[str] files_created: List to append the file path to
        """
        logger.warning(f"No vulnerabilities found for query ID: {self.query_id}")
        # Create an empty file to avoid errors later
        with open(vulns_file, "w") as f:
            json.dump({"response": {"results": []}}, f)
        files_created.append(vulns_file)
        logger.info(f"Created empty vulnerabilities file: {vulns_file}")

    def _create_assets_file_from_vulns(self, assets_file: str, vulns_file: str, files_created: List[str]) -> None:
        """
        Create an assets file from vulnerability data

        :param str assets_file: Path to create assets file
        :param str vulns_file: Path to vulnerabilities file
        :param List[str] files_created: List to append file path to
        """
        logger.info("Creating assets file from vulnerability results...")
        # Create a minimal assets file from the vulnerabilities data
        asset_data = {"response": {"usable": []}}

        # Try to extract unique assets from vulnerability data
        if not os.path.exists(vulns_file):
            self._write_assets_file(assets_file, asset_data, files_created)
            return

        try:
            unique_assets = self._extract_assets_from_vulns(vulns_file)

            # Add unique assets to the asset data
            asset_data["response"]["usable"] = list(unique_assets.values())
            logger.info(f"Extracted {len(unique_assets)} unique assets from vulnerability data")
        except Exception as e:
            logger.error(f"Error extracting assets from vulnerability data: {str(e)}", exc_info=True)

        # Write the assets file
        self._write_assets_file(assets_file, asset_data, files_created)

    def _extract_assets_from_vulns(self, vulns_file: str) -> Dict[str, Dict]:
        """
        Extract unique assets from vulnerability data

        :param str vulns_file: Path to vulnerability file
        :return: Dictionary of unique assets
        :rtype: Dict[str, Dict]
        """
        unique_assets = {}

        # Read vulnerabilities file
        with open(vulns_file, "r") as f:
            vuln_data = json.load(f)

        # Extract unique assets from vulnerability results
        for vuln in vuln_data.get("response", {}).get("results", []):
            # Use IP or hostname as identifier
            identifier = vuln.get("ip", "") or vuln.get("dnsName", "")
            if identifier and identifier not in unique_assets:
                # Create an asset entry
                asset_entry = {
                    "id": identifier,
                    "name": vuln.get("dnsName", identifier),
                    "definition": f"ip={identifier}",
                    "description": "Asset created from vulnerability data",
                }
                unique_assets[identifier] = asset_entry

        return unique_assets

    def _write_assets_file(self, assets_file: str, asset_data: Dict, files_created: List[str]) -> None:
        """
        Write asset data to file

        :param str assets_file: File path to write to
        :param Dict asset_data: Asset data to write
        :param List[str] files_created: List to append file path to
        """
        with open(assets_file, "w") as f:
            json.dump(asset_data, f)

        files_created.append(assets_file)
        logger.info(f"Created assets file: {assets_file} with {len(asset_data['response']['usable'])} assets")

    def _fetch_vulns_with_client(self, output_file: str, query_id: int) -> int:
        """
        Fetch vulnerabilities from Tenable SC using the client library.

        This version writes results incrementally to avoid memory issues with large datasets.

        :param str output_file: File to save the vulnerabilities to
        :param int query_id: ID of the query to use
        :return: Number of vulnerabilities fetched
        :rtype: int
        """
        logger.info(f"Fetching vulnerabilities from Tenable SC using query ID: {query_id}...")

        # Check TenableVariables for minimum severity filter
        min_severity = getattr(TenableVariables, "tenableMinimumSeverityFilter", "critical").lower()
        logger.info(f"Using minimum severity filter: {min_severity}")

        # Initialize counters
        total_vulns = 0

        try:
            # Set up for processing
            temp_dir = os.path.dirname(output_file)
            findings_jsonl = self._initialize_jsonl_file(temp_dir)

            # Get and process vuln data
            vulns_iterator = self._create_vulns_iterator(query_id)

            # Process the vulnerabilities
            total_vulns = self._process_vuln_iterator(vulns_iterator, findings_jsonl, output_file)

            # Log completion
            logger.info(f"Successfully processed {total_vulns} vulnerabilities")
            logger.info(f"Data written to temporary JSONL file: {findings_jsonl}")

        except Exception as e:
            self._handle_vuln_fetch_error(e, output_file, query_id)

        return total_vulns

    def _initialize_jsonl_file(self, temp_dir: str) -> str:
        """
        Initialize JSONL file for findings

        :param str temp_dir: Directory to create the file in
        :return: Path to the JSONL file
        :rtype: str
        """
        # Create a temp JSONL file for processing
        findings_jsonl = os.path.join(temp_dir, "sc_findings.jsonl")
        logger.info("Starting to process vulnerability data...")
        logger.info(f"Creating temporary JSONL file: {findings_jsonl}")
        return findings_jsonl

    def _create_vulns_iterator(self, query_id: int):
        """
        Create an iterator for Tenable SC vulnerabilities

        :param int query_id: Query ID to use
        :return: Iterator for vulnerabilities
        """
        # For large queries, we need to use pagination
        logger.info(f"Using analysis.vulns with query_id={query_id}")

        # Set up query parameters
        query_params = {"query_id": query_id, "tool": "vulndetails", "sourceType": "cumulative"}

        # Log the query parameters for debugging
        logger.info(f"Query parameters: {query_params}")

        # The client library handles pagination internally via an iterator
        return self.client.analysis.vulns(**query_params)

    def _process_vuln_iterator(self, vulns_iterator, findings_jsonl: str, output_file: str) -> int:
        """
        Process vulnerability iterator and write data to files

        :param vulns_iterator: Iterator for vulnerabilities
        :param str findings_jsonl: Path to JSONL file for findings
        :param str output_file: Path to output file
        :return: Number of vulnerabilities processed
        :rtype: int
        """
        # Process results in batches directly writing to files
        batch = []
        batch_size = self.batch_size or 1000
        batch_count = 0
        total_vulns = 0
        unique_assets = {}

        # Open the findings JSONL file for writing
        with open(findings_jsonl, "w") as jsonl_file:
            for vuln in vulns_iterator:
                # Write this vulnerability to the JSONL file immediately
                jsonl_file.write(json.dumps(vuln) + "\n")

                # Extract asset information
                self._extract_asset_from_vuln(vuln, unique_assets)

                # Count processed items
                total_vulns += 1
                batch.append(vuln)

                # Log progress on batch completion
                if len(batch) >= batch_size:
                    batch_count += 1
                    logger.info(f"Processed batch {batch_count} - {total_vulns} vulnerabilities so far...")
                    # Clear the batch but don't keep results in memory
                    batch = []

        # Log final count
        if batch:
            logger.info(f"Processed final batch - total: {total_vulns} vulnerabilities")

        # Write the output file
        self._write_output_file(output_file, total_vulns)

        # Create assets file if needed
        self._create_assets_file_from_unique(unique_assets, output_file)

        return total_vulns

    def _extract_asset_from_vuln(self, vuln: Dict, unique_assets: Dict) -> None:
        """
        Extract asset information from vulnerability data

        :param Dict vuln: Vulnerability data
        :param Dict unique_assets: Dictionary to store unique assets
        """
        identifier = vuln.get("ip", "") or vuln.get("dnsName", "")
        if identifier and identifier not in unique_assets:
            # Create an asset entry
            asset_entry = {
                "id": identifier,
                "name": vuln.get("dnsName", identifier),
                "definition": f"ip={identifier}",
                "description": "Asset created from vulnerability data",
            }
            unique_assets[identifier] = asset_entry

    def _write_output_file(self, output_file: str, total_vulns: int) -> None:
        """
        Write output file with vulnerability data

        :param str output_file: Path to output file
        :param int total_vulns: Number of vulnerabilities processed
        """
        logger.info(f"Writing {total_vulns} vulnerabilities to output file: {output_file}")
        with open(output_file, "w") as f:
            # Write the header only - we'll read from the JSONL for actual data processing
            f.write('{"response": {"results": []}}')

    def _create_assets_file_from_unique(self, unique_assets: Dict, output_file: str) -> None:
        """
        Create assets file from unique assets

        :param Dict unique_assets: Dictionary of unique assets
        :param str output_file: Path to output file used to determine directory
        """
        if not unique_assets:
            return

        temp_dir = os.path.dirname(output_file)
        assets_file = os.path.join(temp_dir, "sc_assets.json")

        asset_data = {"response": {"usable": list(unique_assets.values())}}
        with open(assets_file, "w") as f:
            json.dump(asset_data, f)
        logger.info(f"Created assets file with {len(unique_assets)} unique assets: {assets_file}")

    def _handle_vuln_fetch_error(self, error: Exception, output_file: str, query_id: int) -> None:
        """
        Handle errors during vulnerability fetching

        :param Exception error: The exception that occurred
        :param str output_file: Path to output file
        :param int query_id: Query ID that was used
        """
        logger.error(f"Error fetching vulnerabilities: {str(error)}", exc_info=True)

        # Try to provide more helpful error messages
        if "unauthorized" in str(error).lower() or "401" in str(error):
            logger.error("Authentication error. Please check credentials.")
        elif "not found" in str(error).lower() or "404" in str(error):
            logger.error(f"Query ID {query_id} not found. Please verify the query exists.")
        elif "timeout" in str(error).lower():
            logger.error("Request timed out. The query may be too large or the server is busy.")

        # Create an empty result if we couldn't get any data
        with open(output_file, "w") as f:
            json.dump({"response": {"results": []}}, f)
        logger.info(f"Created empty results file {output_file}")

    def find_or_download_data(self) -> List[str]:
        """
        Find existing Tenable SC data files or download new ones.

        :return: List of file paths
        :rtype: List[str]
        """
        # Create temporary directory if needed
        self._ensure_temp_directory()
        artifacts_dir = self.create_artifacts_dir()

        # Check for existing files and clean them up
        self._find_existing_files(artifacts_dir)

        # Download new data
        return self._download_data_files(artifacts_dir)

    def _ensure_temp_directory(self) -> None:
        """
        Ensure a temporary directory exists for processing files.
        """
        if not self.temp_dir:
            self.temp_dir = tempfile.mkdtemp(prefix="tenable_sc_")
            logger.info(f"Created temporary directory: {self.temp_dir}")

    def _find_existing_files(self, artifacts_dir: str) -> List[str]:
        """
        Find existing Tenable SC data files in the artifacts directory.
        Always returns an empty list since we want to force download fresh data.

        :param str artifacts_dir: Path to the artifacts directory
        :return: Empty list (never use existing files)
        :rtype: List[str]
        """
        # Identify any existing files
        existing_files = list(find_files(artifacts_dir, self.file_pattern))
        if existing_files:
            logger.info(f"Found {len(existing_files)} existing Tenable SC data files to clean up")
            # Clean up existing files
            for file_path in existing_files:
                try:
                    os.remove(file_path)
                    logger.info(f"Removed existing file: {file_path}")
                except OSError as e:
                    logger.warning(f"Failed to remove file {file_path}: {e}")

        # Always return empty list to force fresh download
        return []

    def _download_data_files(self, artifacts_dir: str) -> List[str]:
        """
        Download Tenable SC data files to the artifacts directory.

        :param str artifacts_dir: Path to the artifacts directory
        :return: List of downloaded file paths
        :rtype: List[str]
        """
        logger.info("Downloading new Tenable SC data...")

        # Clean up any existing output JSONL files
        for output_file in [self.ASSETS_FILE, self.FINDINGS_FILE]:
            if os.path.exists(output_file):
                try:
                    os.remove(output_file)
                    logger.info(f"Removed existing output file: {output_file}")
                except OSError as e:
                    logger.warning(f"Failed to remove output file {output_file}: {e}")

        # Verify query_id is provided for downloading
        if not self.query_id:
            logger.error("No query_id provided and no existing files found")
            raise ValidationException("Cannot download data: No query_id provided and no existing files found")

        logger.info(f"Downloading data using query_id: {self.query_id}")
        downloaded_files = self._download_sc_data(artifacts_dir)

        # Create placeholder file if no files were downloaded
        if not downloaded_files:
            downloaded_files = [self._create_placeholder_file(artifacts_dir)]

        logger.info(f"Downloaded {len(downloaded_files)} files:")
        for file_path in downloaded_files:
            logger.info(f"  - {file_path}")

        return downloaded_files

    def _create_placeholder_file(self, artifacts_dir: str) -> str:
        """
        Create a placeholder file for debugging when no files are downloaded.

        :param str artifacts_dir: Path to the artifacts directory
        :return: Path to the created placeholder file
        :rtype: str
        """
        logger.warning("No files were downloaded. Creating a placeholder file for debugging.")
        debug_file = os.path.join(artifacts_dir, "sc_vulns.json")
        with open(debug_file, "w") as f:
            json.dump({"response": {"results": []}}, f)
        logger.info(f"Created placeholder file: {debug_file}")
        return debug_file

    def _process_asset_file(self, file, data, output_f, existing_items):
        """
        Process a Tenable SC data file for assets with mapping and validation.
        Overrides the parent method to handle multiple assets in a single file.

        :param file: The file being processed
        :param data: The data from the file
        :param output_f: The output file handle
        :param existing_items: Dictionary of existing items
        :return: Number of assets processed
        :rtype: int
        """
        # Check if this is an assets file with a "usable" array
        assets_list = data.get("response", {}).get("usable", [])

        # Process multiple assets if available
        if assets_list and len(assets_list) > 0:
            return self._process_multiple_assets(file, assets_list, output_f, existing_items)
        else:
            # For non-assets files or empty assets files, process as single asset
            return self._process_single_file_asset(file, data, output_f, existing_items)

    def _process_multiple_assets(self, file, assets_list, output_f, existing_items):
        """
        Process multiple assets from an assets file.

        :param file: The file being processed
        :param assets_list: List of asset data
        :param output_f: The output file handle
        :param existing_items: Dictionary of existing items
        :return: Number of assets processed
        :rtype: int
        """
        assets_added = 0
        logger.info(f"Processing {len(assets_list)} assets from file {file}")

        for asset_data in assets_list:
            # Extract asset data and create asset
            asset_id, asset_name, ip_info = self._extract_asset_info(asset_data)
            identifier = ip_info if ip_info else asset_id
            asset = self._create_basic_asset(identifier, asset_name or f"Asset {asset_id}", ip_info)

            # Apply mapping if needed and validate
            mapped_asset = self._apply_asset_mapping(asset, asset_data, asset_id, asset_name, ip_info)

            try:
                # Validate and write to output
                if self._validate_and_write_asset(mapped_asset, existing_items, output_f):
                    assets_added += 1
            except Exception as e:
                logger.error(f"Error processing asset {asset_id}: {str(e)}")

        logger.info(f"Added {assets_added} assets from file {file}")
        return assets_added

    def _process_single_file_asset(self, file, data, output_f, existing_items):
        """
        Process a single asset from a file.

        :param file: The file being processed
        :param data: The data from the file
        :param output_f: The output file handle
        :param existing_items: Dictionary of existing items
        :return: Number of assets processed (0 or 1)
        :rtype: int
        """
        try:
            # Parse asset from file
            asset = self.parse_asset(file, data)

            # Apply mapping if needed
            mapped_asset = self._apply_asset_mapping(asset, data)

            # Validate and write to output
            if self._validate_and_write_asset(mapped_asset, existing_items, output_f):
                return 1
            return 0
        except Exception as e:
            logger.error(f"Error processing asset from file {file}: {str(e)}")
            return 0

    def _extract_asset_info(self, asset_data):
        """
        Extract asset information from the asset data.

        :param asset_data: The asset data
        :return: Tuple of (asset_id, asset_name, ip_info)
        :rtype: Tuple[str, str, str]
        """
        asset_id = asset_data.get("id", "")
        asset_name = asset_data.get("name", "")

        # Extract IP information if available
        ip_info = ""
        definition = asset_data.get("definition", "")
        if "ip=" in definition:
            ip_parts = definition.split("ip=")[1].split("&")[0]
            ip_info = ip_parts.replace("%3B", ";")

        return asset_id, asset_name, ip_info

    def _create_basic_asset(self, identifier, name, ip_address):
        """
        Create a basic IntegrationAsset object.

        :param str identifier: Asset identifier
        :param str name: Asset name
        :param str ip_address: Asset IP address
        :return: IntegrationAsset object
        :rtype: IntegrationAsset
        """
        return IntegrationAsset(
            identifier=identifier,
            name=name,
            ip_address=ip_address,
            parent_id=self.plan_id,
            parent_module=regscale_models.SecurityPlan.get_module_slug(),
            asset_owner_id=ScannerVariables.userId,
            asset_category=regscale_models.AssetCategory.Hardware,
            asset_type=regscale_models.AssetType.Other,
            status=AssetStatus.ACTIVE,
            date_last_updated=get_current_datetime(),
        )

    def _apply_asset_mapping(self, asset, source_data, asset_id=None, asset_name=None, ip_info=None):
        """
        Apply field mapping to an asset.

        :param IntegrationAsset asset: The asset to apply mapping to
        :param dict source_data: Source data for mapping
        :param str asset_id: Optional asset ID for single-asset mapping
        :param str asset_name: Optional asset name for single-asset mapping
        :param str ip_info: Optional IP info for single-asset mapping
        :return: Mapped IntegrationAsset
        :rtype: IntegrationAsset
        """
        asset_dict = dataclasses.asdict(asset)

        # For single assets from assets file, create simplified data structure
        if asset_id is not None:
            source_data = {"id": asset_id, "name": asset_name, "ip": ip_info}

        if not self.disable_mapping:
            mapping = getattr(self.mapping, "fields", {}).get("asset_mapping", {}) if self.mapping else {}
            mapped_asset_dict = self._apply_mapping(source_data or {}, asset_dict, mapping)

            # Ensure we only pass valid fields to IntegrationAsset
            valid_fields = {}
            for field, value in mapped_asset_dict.items():
                if hasattr(IntegrationAsset, field) or field in inspect.signature(IntegrationAsset.__init__).parameters:
                    valid_fields[field] = value

            return IntegrationAsset(**valid_fields)
        else:
            return asset

    def _validate_and_write_asset(self, asset, existing_items, output_f):
        """
        Validate an asset and write it to the output file if valid.

        :param IntegrationAsset asset: The asset to validate and write
        :param dict existing_items: Dictionary of existing items
        :param file output_f: The output file handle
        :return: True if asset was written, False otherwise
        :rtype: bool
        """
        self._validate_fields(asset, self.required_asset_fields)

        # Check if asset already exists
        key = self._get_item_key(dataclasses.asdict(asset), "asset")
        if key in existing_items:
            logger.debug(f"Asset with identifier {key} already exists, skipping")
            return False

        # Write to output
        output_f.write(json.dumps(dataclasses.asdict(asset)) + "\n")
        output_f.flush()
        existing_items[key] = True
        return True

    def _process_finding_file(self, file, data, output_f, existing_items):
        """
        Process a single file for findings with memory-efficient streaming.

        :param file: The file being processed
        :param data: The data from the file
        :param output_f: The output file handle
        :param existing_items: Dictionary of existing items
        :return: Number of findings processed
        :rtype: int
        """
        file_path_str = str(file)

        # Check if this is a JSONL file from our incremental processing
        if file_path_str.endswith(FILE_TYPE):
            logger.info(f"Processing JSONL findings file: {file_path_str}")
            return self._process_jsonl_findings(file_path_str, output_f, existing_items)

        # Get asset identifier from file
        identifier = self._get_asset_identifier_from_file(file, data)

        # Extract findings data
        findings_data = data.get("response", {}).get("results", []) if data and "response" in data else []

        # Process each finding
        return self._process_findings_list(file, findings_data, identifier, output_f, existing_items)

    def _get_asset_identifier_from_file(self, file, data):
        """
        Extract asset identifier from file data.

        :param file: The file being processed
        :param data: The data from the file
        :return: Asset identifier
        :rtype: str
        """
        try:
            asset = self.parse_asset(file, data)
            return asset.identifier
        except Exception as e:
            logger.error(f"Error parsing asset from file {file}: {str(e)}")
            # Use a fallback identifier from the data if possible
            identifier = "unknown"
            if data and isinstance(data, dict):
                # Try to extract IP from vuln data
                if "response" in data and "results" in data.get("response", {}):
                    results = data.get("response", {}).get("results", [])
                    if results and len(results) > 0:
                        identifier = results[0].get("ip", "unknown")
        return identifier

    def _process_findings_list(self, file, findings_data, default_identifier, output_f, existing_items):
        """
        Process a list of findings and write them to the output file.

        :param file: The source file
        :param list findings_data: List of finding data
        :param str default_identifier: Default asset identifier to use
        :param file output_f: Output file handle
        :param dict existing_items: Dictionary of existing items
        :return: Number of findings processed
        :rtype: int
        """
        findings_in_file = 0

        for finding_item in findings_data:
            # Get IP directly from finding item if available
            finding_asset_id = finding_item.get("ip", default_identifier)

            # Process the individual finding
            if self._process_individual_finding(file, finding_item, finding_asset_id, output_f, existing_items):
                findings_in_file += 1

        if findings_in_file > 0:
            logger.info(f"Added {findings_in_file} new findings from file {file}")
        return findings_in_file

    def _process_jsonl_findings(self, jsonl_file_path, output_f, existing_items):
        """
        Process findings from a JSONL file in a memory-efficient way.

        :param str jsonl_file_path: Path to the JSONL file
        :param file output_f: Output file handle
        :param dict existing_items: Dictionary of existing items
        :return: Number of findings processed
        :rtype: int
        """
        findings_in_file = 0
        processed_count = 0

        try:
            # Process the JSONL file line by line
            with open(jsonl_file_path, "r") as f:
                for line_num, line in enumerate(f, 1):
                    processed_count += 1

                    # Log progress every 1000 lines
                    if processed_count % 1000 == 0:
                        logger.info(f"Processing finding {processed_count} from JSONL file...")

                    try:
                        # Parse the JSON line
                        finding_item = json.loads(line)

                        # Extract the asset identifier and process the finding
                        finding_asset_id = finding_item.get("ip", "unknown")
                        if self._process_individual_finding(
                            jsonl_file_path, finding_item, finding_asset_id, output_f, existing_items, line_num
                        ):
                            findings_in_file += 1

                    except json.JSONDecodeError as e:
                        logger.warning(f"Invalid JSON at line {line_num} in {jsonl_file_path}: {e}")
                    except Exception as e:
                        logger.warning(f"Error processing finding at line {line_num} in {jsonl_file_path}: {e}")

            logger.info(f"Processed {processed_count} total findings from JSONL, added {findings_in_file} new findings")

        except Exception as e:
            logger.error(f"Error processing JSONL file {jsonl_file_path}: {e}", exc_info=True)

        return findings_in_file

    def _process_individual_finding(self, file, finding_item, asset_id, output_f, existing_items, line_num=None):
        """
        Process an individual finding and write it to the output file if valid.

        :param file: Source file or file path
        :param dict finding_item: The finding data
        :param str asset_id: Asset identifier
        :param file output_f: Output file handle
        :param dict existing_items: Dictionary of existing items
        :param int line_num: Optional line number for JSONL processing
        :return: True if finding was written, False otherwise
        :rtype: bool
        """
        # Parse the finding
        data = None  # Only needed for specific implementations
        finding = self.parse_finding(asset_id, data, finding_item)

        if not finding:
            logger_fn = logger.debug if line_num else logger.warning
            logger_fn(f"Failed to parse finding from {file}" + (f" at line {line_num}" if line_num else ""))
            return False

        # Apply mapping
        mapped_finding = self._apply_finding_mapping(finding, finding_item)

        # Validate and check for duplicates
        try:
            self._validate_fields(mapped_finding, self.required_finding_fields)

            key = self._get_item_key(dataclasses.asdict(mapped_finding), "finding")
            if key in existing_items:
                logger.debug(f"Finding with key {key} already exists, skipping")
                return False

            # Write to output
            output_f.write(json.dumps(dataclasses.asdict(mapped_finding)) + "\n")
            output_f.flush()
            existing_items[key] = True
            return True
        except Exception as e:
            logger_fn = logger.debug if line_num else logger.error
            logger_fn(f"Error processing finding: {e}")
            return False

    def _apply_finding_mapping(self, finding, finding_item):
        """
        Apply mapping to a finding.

        :param IntegrationFinding finding: The finding to map
        :param dict finding_item: The source finding data
        :return: Mapped IntegrationFinding
        :rtype: IntegrationFinding
        """
        finding_dict = dataclasses.asdict(finding)

        if self.disable_mapping:
            return finding

        mapped_finding_dict = self._apply_mapping(
            finding_item,
            finding_dict,
            getattr(self.mapping, "fields", {}).get("finding_mapping", {}) if self.mapping else {},
        )

        # Normalize field names - convert camelCase to snake_case and remove unknown fields
        normalized_dict = {}
        for key, value in mapped_finding_dict.items():
            # Convert camelCase to snake_case
            if key == "pluginID":
                normalized_dict["plugin_id"] = value
            elif key == "pluginName":
                normalized_dict["plugin_name"] = value
            # Only add known fields to avoid unexpected keyword argument errors
            elif hasattr(IntegrationFinding, key) or key in inspect.signature(IntegrationFinding.__init__).parameters:
                normalized_dict[key] = value

        # Make sure required fields are present
        for field in self.required_finding_fields:
            if field not in normalized_dict and field in mapped_finding_dict:
                normalized_dict[field] = mapped_finding_dict[field]

        try:
            return IntegrationFinding(**normalized_dict)
        except TypeError as e:
            logger.debug(f"Error creating IntegrationFinding: {e}. Using original finding.")
            return finding

    def sync_assets_and_findings(self) -> None:
        """
        Process both assets and findings, downloading if necessary, and sync to RegScale.

        This method overrides the parent method to handle the case where file_path is not provided
        but query_id is, by first finding or downloading Tenable SC data files and then processing them.

        :rtype: None
        """
        try:
            # Ensure we have a valid file path, downloading data if needed
            file_path = self._get_or_download_file_path()

            # Process files into JSONL format for assets and findings
            total_assets, total_findings = self._process_and_prepare_data(file_path)

            # Sync assets and findings to RegScale
            self._sync_data_to_regscale(total_assets, total_findings)

        except Exception as e:
            logger.error(f"Error in sync_assets_and_findings: {str(e)}", exc_info=True)
            raise

    def _get_or_download_file_path(self) -> str:
        """
        Get a valid file path, downloading data if necessary.

        :return: Valid file path to process
        :rtype: str
        """
        # If file_path is not provided, find or download files
        if not self.file_path:
            logger.info("No file path provided, finding or downloading Tenable SC data files")
            found_files = self.find_or_download_data()

            if not found_files:
                logger.error("No Tenable SC data files found or downloaded")
                raise ValidationException("No Tenable SC data files found or downloaded")

            # Use the directory containing the found files as the file_path
            if len(found_files) > 0:
                # Get the directory containing the files
                first_file = found_files[0]
                self.file_path = os.path.dirname(first_file)
                logger.info(f"Using directory containing found files as file_path: {self.file_path}")

        # Validate the file path
        return self._validate_file_path(self.file_path)

    def _process_and_prepare_data(self, file_path: str) -> Tuple[int, int]:
        """
        Process files into JSONL format for assets and findings.

        :param str file_path: Path to source files
        :return: Tuple of (asset_count, finding_count)
        :rtype: Tuple[int, int]
        """
        logger.info("Processing assets and findings together from %s", file_path)
        return self._process_files(
            file_path=file_path,
            assets_output_file=self.ASSETS_FILE,
            findings_output_file=self.FINDINGS_FILE,
            empty_assets_file=self.empty_files,
            empty_findings_file=self.empty_files,
        )

    def _sync_data_to_regscale(self, total_assets: int, total_findings: int) -> None:
        """
        Sync processed assets and findings to RegScale.

        :param int total_assets: Number of assets to sync
        :param int total_findings: Number of findings to sync
        """
        # Sync assets
        logger.info("Syncing %d assets to RegScale", total_assets)
        self.sync_assets(
            plan_id=self.plan_id,
            file_path=self.file_path,
            use_jsonl_file=True,
            asset_count=total_assets,
            scan_date=self.scan_date,
        )

        # Sync findings
        logger.info("Syncing %d findings to RegScale", total_findings)
        self.sync_findings(
            plan_id=self.plan_id,
            file_path=self.file_path,
            use_jsonl_file=True,
            finding_count=total_findings,
            scan_date=self.scan_date,
        )

        logger.info("Assets and findings sync complete")

    def check_data_file(self, data_files: List[str]) -> bool:
        """
        Check if any Tenable SC data files exist.
        """
        if not data_files:
            logger.warning("No Tenable SC data files found, nothing to sync")
            sys.exit(0)

    def sync_with_transformer(self, mapping_file: Optional[str] = None) -> None:
        """
        Sync assets and findings to RegScale using the DataTransformer.

        This method combines the ApiPaginator and DataTransformer to efficiently download
        and transform Tenable SC data for RegScale integration.

        Args:
            mapping_file (Optional[str]): Path to custom mapping file (uses default if None)

        Raises:
            Exception: If there is an error during synchronization
        """
        try:
            logger.info("Starting synchronization using DataTransformer...")

            # Step 1: Download or find data files
            data_files = self._get_data_files_for_sync()

            # Step 2: Create transformer
            transformer = self._create_transformer(mapping_file)

            # Step 3: Load and process data from files
            assets_list, findings_list = self._load_assets_and_findings(data_files)

            # Step 4: Transform data
            assets, findings = self._transform_data(transformer, assets_list, findings_list)

            # Step 5: Sync with RegScale
            self._sync_transformed_data(assets, findings)

        except Exception as e:
            logger.error(f"Error syncing with transformer: {str(e)}", exc_info=True)
            raise

    def _get_data_files_for_sync(self) -> List[str]:
        """
        Get data files for synchronization

        :return: List of data file paths
        :rtype: List[str]
        """
        data_files = self.find_or_download_data()
        self.check_data_file(data_files)
        logger.info(f"Processing {len(data_files)} Tenable SC data files")
        return data_files

    def _create_transformer(self, mapping_file: Optional[str] = None) -> DataTransformer:
        """
        Create a DataTransformer instance

        :param Optional[str] mapping_file: Path to custom mapping file
        :return: Configured DataTransformer instance
        :rtype: DataTransformer
        """
        transformer = DataTransformer(mapping_file=mapping_file)
        transformer.scan_date = self.scan_date
        return transformer

    def _load_assets_and_findings(self, data_files: List[str]) -> Tuple[List[Dict], List[Dict]]:
        """
        Load assets and findings from data files

        :param List[str] data_files: List of data file paths
        :return: Tuple of (assets_list, findings_list)
        :rtype: Tuple[List[Dict], List[Dict]]
        """
        assets_list = []
        findings_list = []

        for file_path in data_files:
            file_path_str = str(file_path)
            logger.info(f"Processing file: {file_path_str}")

            try:
                self._process_data_file(file_path_str, assets_list, findings_list)
            except Exception as e:
                logger.error(f"Error processing file {file_path_str}: {str(e)}", exc_info=True)

        return assets_list, findings_list

    def _process_data_file(self, file_path: str, assets_list: List[Dict], findings_list: List[Dict]) -> None:
        """
        Process a single data file and extract assets and findings

        :param str file_path: Path to data file
        :param List[Dict] assets_list: List to append assets to
        :param List[Dict] findings_list: List to append findings to
        """
        # Load the file data
        with open(file_path, "r") as f:
            data = json.load(f)

        # Validate the file
        is_valid, validated_data = self.is_valid_file(data, file_path)
        if not is_valid or validated_data is None:
            logger.warning(f"Invalid file: {file_path}")
            return

        # Process assets and findings based on file type
        if "sc_assets" in file_path:
            self._extract_assets(validated_data, assets_list, file_path)
        elif "sc_vulns" in file_path:
            self._extract_findings(validated_data, findings_list, file_path)

    def _extract_assets(self, validated_data: Dict, assets_list: List[Dict], file_path: str) -> None:
        """
        Extract assets from validated data

        :param Dict validated_data: Validated data from file
        :param List[Dict] assets_list: List to append assets to
        :param str file_path: Path to source file (for logging)
        """
        # Extract assets from assets file
        assets = validated_data.get("response", {}).get("usable", [])
        for asset_data in assets:
            assets_list.append(asset_data)
        logger.info(f"Added {len(assets)} assets from file: {file_path}")

    def _extract_findings(self, validated_data: Dict, findings_list: List[Dict], file_path: str) -> None:
        """
        Extract findings from validated data

        :param Dict validated_data: Validated data from file
        :param List[Dict] findings_list: List to append findings to
        :param str file_path: Path to source file (for logging)
        """
        # Extract findings from vulnerabilities file
        findings = validated_data.get("response", {}).get("results", [])
        for finding_data in findings:
            findings_list.append(finding_data)
        logger.info(f"Added {len(findings)} findings from file: {file_path}")

    def _transform_data(
        self, transformer: DataTransformer, assets_list: List[Dict], findings_list: List[Dict]
    ) -> Tuple[List[IntegrationAsset], List[IntegrationFinding]]:
        """
        Transform raw data into IntegrationAsset and IntegrationFinding objects

        :param DataTransformer transformer: DataTransformer instance
        :param List[Dict] assets_list: List of asset data
        :param List[Dict] findings_list: List of finding data
        :return: Tuple of (assets, findings)
        :rtype: Tuple[List[IntegrationAsset], List[IntegrationFinding]]
        """
        # Transform assets
        assets = list(transformer.batch_transform_to_assets(assets_list, plan_id=self.plan_id))

        # Link findings to assets
        self._link_findings_to_assets(assets, findings_list)

        # Transform findings
        findings = list(transformer.batch_transform_to_findings(findings_list))

        logger.info(f"Transformed {len(assets)} assets and {len(findings)} findings")
        return assets, findings

    def _link_findings_to_assets(self, assets: List[IntegrationAsset], findings_list: List[Dict]) -> None:
        """
        Link findings to assets using IP address

        :param List[IntegrationAsset] assets: List of assets
        :param List[Dict] findings_list: List of finding data to update
        """
        # Create mapping from IP to asset identifier
        asset_identifier_map = {asset.ip_address: asset.identifier for asset in assets if asset.ip_address}

        # Add asset identifier to each finding
        for finding_data in findings_list:
            ip = finding_data.get("ip", "")
            asset_id = asset_identifier_map.get(ip, ip)
            finding_data["asset_identifier"] = asset_id

    def _sync_transformed_data(self, assets: List[IntegrationAsset], findings: List[IntegrationFinding]) -> None:
        """
        Sync transformed data to RegScale

        :param List[IntegrationAsset] assets: List of assets
        :param List[IntegrationFinding] findings: List of findings
        """
        # Sync assets and findings to RegScale
        asset_count = self.update_regscale_assets(iter(assets))
        finding_count = self.update_regscale_findings(iter(findings))

        logger.info(f"Synchronized {asset_count} assets and {finding_count} findings to RegScale")

    def _process_files(
        self,
        file_path: Union[str, Path],
        assets_output_file: str,
        findings_output_file: str,
        empty_assets_file: bool = True,
        empty_findings_file: bool = True,
    ) -> Tuple[int, int]:
        """
        Process source files to extract assets and findings.

        :param Union[str, Path] file_path: Path to source file or directory
        :param str assets_output_file: Path to write assets to
        :param str findings_output_file: Path to write findings to
        :param bool empty_assets_file: Whether to empty the assets file before writing
        :param bool empty_findings_file: Whether to empty the findings file before writing
        :return: Tuple of (asset_count, finding_count)
        :rtype: Tuple[int, int]
        """
        # Ensure output directories exist
        os.makedirs(os.path.dirname(assets_output_file), exist_ok=True)
        os.makedirs(os.path.dirname(findings_output_file), exist_ok=True)

        # Prepare output files
        asset_info = self._prepare_output_file(assets_output_file, empty_assets_file, "asset")
        finding_info = self._prepare_output_file(findings_output_file, empty_findings_file, "finding")

        # Initialize counters for memory-efficient tracking
        asset_count = 0
        finding_count = 0
        processed_files = 0

        # Log start of processing
        logger.info(f"Starting to process files from {file_path}")

        # Process each file
        for file_path_obj, data in self.find_valid_files(file_path):
            processed_files += 1
            file_path_str = str(file_path_obj)
            file_size_mb = os.path.getsize(file_path_str) / (1024 * 1024) if os.path.exists(file_path_str) else 0

            logger.info(f"Processing file {processed_files}: {file_path_str} ({file_size_mb:.2f} MB)")

            try:
                # Check for JSONL files first - these are already in our optimized format
                if file_path_str.endswith(FILE_TYPE):
                    if "findings" in file_path_str.lower():
                        # Process findings JSONL file
                        with open(findings_output_file, finding_info.get("mode", "w")) as f:
                            count = self._process_jsonl_findings(
                                file_path_str, f, finding_info.get("existing_items", {})
                            )
                            finding_count += count
                            logger.info(f"Added {count} findings from JSONL file {file_path_str}")
                        # Use append mode after first file
                        finding_info["mode"] = "a"
                    continue

                # For JSON files, process normally
                if not self.is_valid_file(data, file_path_str)[0]:
                    logger.warning(f"Invalid file format: {file_path_str}")
                    continue

                # Process assets or findings based on file path
                if "sc_assets" in file_path_str:
                    # Process assets file
                    with open(assets_output_file, asset_info.get("mode", "w")) as output_f:
                        count = self._process_asset_file(
                            file_path_str, data, output_f, asset_info.get("existing_items", {})
                        )
                        asset_count += count
                    # Use append mode for subsequent files
                    asset_info["mode"] = "a"

                elif "sc_vulns" in file_path_str:
                    # Process findings file
                    with open(findings_output_file, finding_info.get("mode", "w")) as output_f:
                        count = self._process_finding_file(
                            file_path_str, data, output_f, finding_info.get("existing_items", {})
                        )
                        finding_count += count
                    # Use append mode for subsequent files
                    finding_info["mode"] = "a"

            except Exception as e:
                logger.error(f"Error processing file {file_path_str}: {str(e)}", exc_info=True)

        # Log completion
        logger.info(f"Finished processing {processed_files} files")
        logger.info(f"Added {asset_count} assets and {finding_count} findings to JSONL files")

        return asset_count, finding_count

    # Add method to support scanner_integration.py
    def _process_single_asset(self, asset, loading_assets=False):
        """
        Process a single asset for the scanner integration framework.
        This method is called by scanner_integration.py's _process_assets method.

        :param asset: The asset to process
        :param loading_assets: Whether assets are being loaded
        :return: True if successful, False otherwise
        :rtype: bool
        """
        try:
            # Process the asset as needed for integration
            # This is a simplified version just to handle the scanner integration's expectations
            return True
        except Exception as e:
            logger.error(f"Error processing asset: {str(e)}")
            return False
