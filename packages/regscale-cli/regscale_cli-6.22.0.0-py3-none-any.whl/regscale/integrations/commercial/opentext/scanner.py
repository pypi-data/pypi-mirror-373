"""
WebInspect Scanner Integration for RegScale.

This module provides integration between OpenText WebInspect scanner and RegScale,
allowing you to import WebInspect scan results into RegScale as assets and findings.
"""

import dataclasses
import json
import logging
import os
import traceback
from typing import Any, Dict, List, Optional, Union, Tuple, cast, Iterator, Set

from pathlib import Path

from regscale.core.app.utils.app_utils import check_license, get_current_datetime
from regscale.core.app.utils.file_utils import find_files, read_file
from regscale.integrations.jsonl_scanner_integration import JSONLScannerIntegration
from regscale.integrations.scanner_integration import IntegrationAsset, IntegrationFinding, issue_due_date
from regscale.models import IssueSeverity, AssetStatus, IssueStatus, ImportValidater

logger = logging.getLogger("regscale")


class WebInspectIntegration(JSONLScannerIntegration):
    """Class for handling OpenText WebInspect scanner integration."""

    title: str = "WebInspect"
    finding_severity_map: Dict[int, Any] = {
        4: IssueSeverity.Critical.value,
        3: IssueSeverity.High.value,
        2: IssueSeverity.Moderate.value,
        1: IssueSeverity.Low.value,
        0: IssueSeverity.NotAssigned.value,
    }

    # Constants for file paths
    ASSETS_FILE = "./artifacts/webinspect_assets.jsonl"
    FINDINGS_FILE = "./artifacts/webinspect_findings.jsonl"
    file_date: Optional[str] = None

    def __init__(self, *args, **kwargs):
        """Initialize the WebInspectIntegration."""
        self.app = check_license()
        # Override file_pattern for XML files
        kwargs["file_pattern"] = "*.xml"
        kwargs["read_files_only"] = True
        self.disable_mapping = kwargs["disable_mapping"] = True
        self.set_scan_date(kwargs.get("scan_date"))
        self.is_component = kwargs.get("is_component", False)
        # logger.debug(f"scan_date: {self.scan_date}"
        super().__init__(*args, **kwargs)
        logger.debug(f"WebInspectIntegration initialized with scan date: {self.scan_date}")

    def is_valid_file(self, data: Any, file_path: Union[Path, str]) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Check if the provided data is a valid WebInspect scan result.

        Validates that the data is from a WebInspect XML file with the required structure.
        Logs a warning with the file path and returns (False, None) if invalid.

        :param Any data: Data parsed from the file (string content for XML when read_files_only is True, or file path otherwise)
        :param Union[Path, str] file_path: Path to the file being processed
        :return: Tuple of (is_valid, validated_data) where validated_data includes validater, mapping, and data if valid
        :rtype: Tuple[bool, Optional[Dict[str, Any]]]
        """
        if self.read_files_only:
            # Data is the XML content as a string
            if not isinstance(data, str):
                logger.warning(f"Data is not a string (expected XML content) for file {file_path}")
                return False, None

            try:
                # Create a temporary file since ImportValidater requires a file path
                import tempfile

                with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as temp_file:
                    temp_file.write(data)
                    temp_path = temp_file.name

                validater = ImportValidater(
                    required_headers=["Issues"],
                    file_path=temp_path,
                    mapping_file_path="",  # Empty string instead of None
                    disable_mapping=True,
                    xml_tag="Scan",  # XML root tag
                )

                # Clean up the temporary file
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass
            except Exception:
                error_message = traceback.format_exc()
                logger.warning(f"Error processing WebInspect XML content for file {file_path}: {str(error_message)}")
                return False, None
        else:
            # Data is the file path
            if not isinstance(data, (str, Path)):
                logger.warning(f"Data is not a file path when read_files_only is False for file {file_path}")
                return False, None

            try:
                validater = ImportValidater(
                    required_headers=["Issues"],
                    file_path=str(data),
                    mapping_file_path="",  # Empty string instead of None
                    disable_mapping=True,
                    xml_tag="Scan",  # XML root tag
                )
            except Exception as e:
                logger.warning(f"Error processing WebInspect file {data} for file {file_path}: {str(e)}")
                return False, None

        # Check if validater produced usable data
        if not validater.data or not validater.parsed_headers:
            logger.warning(f"Data is not a valid WebInspect XML structure for file {file_path}")
            return False, None

        # Extract mapping and issues data
        mapping = validater.mapping
        issues_data = mapping.get_value(cast(Dict[str, Any], validater.data), "Issues", {})
        # issues_data = parent_issues_data.get("Issue", [])
        # Validate that issues data contains 'Issue' elements
        if not issues_data or "Issue" not in issues_data:
            logger.warning(f"Data has no 'Issues' with 'Issue' elements for file {file_path}")
            return False, None

        return True, issues_data

    def _process_files(
        self,
        file_path: Union[str, Path],
        assets_output_file: str,
        findings_output_file: str,
        empty_assets_file: bool = True,
        empty_findings_file: bool = True,
    ) -> Tuple[int, int]:
        """
        Process files (local or S3) to extract both assets and findings in a single pass.

        Optimizes file processing by reading each file once to extract asset and finding data.

        :param Union[str, Path] file_path: Path to source file or directory (local or S3 URI)
        :param str assets_output_file: Path to output JSONL file for assets
        :param str findings_output_file: Path to output JSONL file for findings
        :param bool empty_assets_file: Whether to empty the assets file before writing (default: True)
        :param bool empty_findings_file: Whether to empty the findings file before writing (default: True)
        :return: Tuple of total asset and finding counts
        :rtype: Tuple[int, int]
        """
        asset_tracker = self._setup_tracker(assets_output_file, empty_assets_file, "asset")
        finding_tracker = self._setup_tracker(findings_output_file, empty_findings_file, "finding")
        processed_files = set()

        with open(assets_output_file, "a") as assets_file, open(findings_output_file, "a") as findings_file:
            self._process_file_data(
                file_path, assets_file, findings_file, asset_tracker, finding_tracker, processed_files
            )

        self._log_completion(asset_tracker.new_items, assets_output_file, "assets")
        self._log_completion(finding_tracker.new_items, findings_output_file, "findings")
        return asset_tracker.total_items, finding_tracker.total_items

    def _setup_tracker(self, output_file: str, empty_file: bool, item_type: str) -> "ItemTracker":
        """
        Set up a tracker for counting items.

        :param str output_file: Path to the output file
        :param bool empty_file: Whether to empty the file before processing
        :param str item_type: Type of items ('asset' or 'finding')
        :return: Tracker object for managing item counts
        :rtype: ItemTracker
        """
        from dataclasses import dataclass

        @dataclass
        class ItemTracker:
            existing_items: Dict[str, bool]
            new_items: int = 0
            total_items: int = 0

        existing_items = self._prepare_output_file(output_file, empty_file, item_type)
        return ItemTracker(existing_items=existing_items, total_items=len(existing_items))

    def _process_file_data(
        self,
        file_path: Union[str, Path],
        assets_file: Any,
        findings_file: Any,
        asset_tracker: "ItemTracker",
        finding_tracker: "ItemTracker",
        processed_files: Set[str],
    ) -> None:
        """
        Process data from all files in the given path.

        :param Union[str, Path] file_path: Path to source file or directory
        :param Any assets_file: Open file handle for writing assets
        :param Any findings_file: Open file handle for writing findings
        :param ItemTracker asset_tracker: Tracker for asset counts
        :param ItemTracker finding_tracker: Tracker for finding counts
        :param Set[str] processed_files: Set of processed file paths
        :rtype: None
        """
        for file, data in self.find_valid_files(file_path):
            file_str = str(file)
            if file_str in processed_files:
                continue

            processed_files.add(file_str)
            self._handle_single_file(file, data, assets_file, findings_file, asset_tracker, finding_tracker)

    def _handle_single_file(
        self,
        file: Union[Path, str],
        data: Optional[Dict[str, Any]],
        assets_file: Any,
        findings_file: Any,
        asset_tracker: "ItemTracker",
        finding_tracker: "ItemTracker",
    ) -> None:
        """
        Handle processing of a single file's data.

        :param Union[Path, str] file: Path to the file being processed
        :param Optional[Dict[str, Any]] data: Parsed data from the file
        :param Any assets_file: Open file handle for writing assets
        :param Any findings_file: Open file handle for writing findings
        :param ItemTracker asset_tracker: Tracker for asset counts
        :param ItemTracker finding_tracker: Tracker for finding counts
        :rtype: None
        """
        try:
            logger.info(f"Processing file: {file}")
            asset = self._prepare_asset(file, data)
            self._write_asset_if_new(asset, assets_file, asset_tracker)

            # Extract the date from the file name
            file_name = os.path.basename(str(file))
            # Extract the string after " - " and before ".xml" in the file name
            parsed_string = file_name.split(" - ")[1].rsplit(".xml", 1)[0] if " - " in file_name else ""
            # Convert parsed_string to a date in "%Y-%m-%d %H:%M:%S" format
            try:
                if len(parsed_string) == 6:  # Ensure the string is in "MMDDYY" format
                    month = int(parsed_string[:2])
                    day = int(parsed_string[2:4])
                    year = int(parsed_string[4:])
                    self.file_date = f"{year + 2000:04d}-{month:02d}-{day:02d}"
                else:
                    self.file_date = None
            except ValueError:
                self.file_date = None

            findings_data = self._get_findings_data_from_file(data)
            logger.info(f"Found {len(findings_data)} findings in file: {file}")
            findings_added = self._write_findings(findings_data, asset.identifier, findings_file, finding_tracker)

            if findings_added > 0:
                logger.info(f"Added {findings_added} new findings from file {file}")
        except Exception as e:
            logger.error(f"Error processing file {file}: {str(e)}")

    def _prepare_asset(self, file: Union[Path, str], data: Optional[Dict[str, Any]]) -> IntegrationAsset:
        """
        Prepare and validate an asset from file data.

        :param Union[Path, str] file: Path to the file being processed
        :param Optional[Dict[str, Any]] data: Parsed data from the file
        :return: Processed and validated asset object
        :rtype: IntegrationAsset
        """
        asset = self.parse_asset(file, data)
        asset_dict = dataclasses.asdict(asset)
        if not self.disable_mapping and self.mapping:
            mapped_asset_dict = self._apply_mapping(
                data or {}, asset_dict, getattr(self.mapping, "fields", {}).get("asset_mapping", {})
            )
            mapped_asset = IntegrationAsset(**mapped_asset_dict)
        else:
            mapped_asset = asset
        self._validate_fields(mapped_asset, self.required_asset_fields)
        return mapped_asset

    def _write_asset_if_new(self, asset: IntegrationAsset, assets_file: Any, tracker: "ItemTracker") -> None:
        """
        Write an asset to the file if it’s new.

        :param IntegrationAsset asset: Asset object to write
        :param Any assets_file: Open file handle for writing assets
        :param ItemTracker tracker: Tracker for asset counts
        :rtype: None
        """
        asset_key = asset.identifier
        if asset_key not in tracker.existing_items:
            assets_file.write(json.dumps(dataclasses.asdict(asset)) + "\n")
            assets_file.flush()
            tracker.existing_items[asset_key] = True
            tracker.new_items += 1
            tracker.total_items += 1
        else:
            logger.debug(f"Asset with identifier {asset_key} already exists, skipping")

    def _write_findings(
        self,
        findings_data: List[Dict[str, Any]],
        asset_id: str,
        findings_file: Any,
        tracker: "ItemTracker",
    ) -> int:
        """
        Write new findings to the file and track counts.

        :param List[Dict[str, Any]] findings_data: List of finding items
        :param str asset_id: Identifier of the associated asset
        :param Any findings_file: Open file handle for writing findings
        :param ItemTracker tracker: Tracker for finding counts
        :return: Number of new findings added
        :rtype: int
        """
        findings_added = 0
        for finding_item in findings_data:
            finding = self.parse_finding(asset_id, findings_data, finding_item)  # Pass empty dict for data if unused
            finding_dict = dataclasses.asdict(finding)
            if not self.disable_mapping and self.mapping:
                mapped_finding_dict = self._apply_mapping(
                    finding_item, finding_dict, getattr(self.mapping, "fields", {}).get("finding_mapping", {})
                )
                mapped_finding = IntegrationFinding(**mapped_finding_dict)
            else:
                mapped_finding = finding
            self._validate_fields(mapped_finding, self.required_finding_fields)

            finding_key = self._get_item_key(dataclasses.asdict(mapped_finding), "finding")
            if finding_key not in tracker.existing_items:
                findings_file.write(json.dumps(dataclasses.asdict(mapped_finding)) + "\n")
                findings_file.flush()
                tracker.existing_items[finding_key] = True
                tracker.new_items += 1
                tracker.total_items += 1
                findings_added += 1
            else:
                logger.debug(f"Finding with key {finding_key} already exists, skipping")
        return findings_added

    def _log_completion(self, new_count: int, output_file: str, item_type: str) -> None:
        """
        Log the completion of processing items.

        :param int new_count: Number of new items added
        :param str output_file: Path to the output file
        :param str item_type: Type of items processed ('assets' or 'findings')
        :rtype: None
        """
        logger.info(f"Added {new_count} new {item_type} to {output_file}")

    def find_valid_files(self, path: Union[Path, str]) -> Iterator[Tuple[Union[Path, str], Dict[str, Any]]]:
        """
        Find all valid WebInspect scan files in the given path.

        Overrides the parent method to handle XML files instead of JSON, passing content or path to is_valid_file.

        :param Union[Path, str] path: Path to a file or directory (local or S3 URI)
        :return: Iterator yielding tuples of (file_path, validated_data) for valid files
        :rtype: Iterator[Tuple[Union[Path, str], Dict[str, Any]]]
        """
        files = find_files(path, self.file_pattern)
        for file in files:
            try:
                if self.read_files_only:
                    content = read_file(file)  # Get raw XML content as string
                else:
                    content = file  # Pass file path directly
                is_valid, validated_data = self.is_valid_file(content, file)
                if is_valid and validated_data is not None:
                    yield file, validated_data
            except Exception as e:
                logger.error(f"Error processing file {file}: {str(e)}")

    def parse_asset(self, file_path: Union[Path, str], data: Dict[str, Any]) -> IntegrationAsset:
        """
        Parse a single asset from WebInspect scan data.

        :param Union[Path, str] file_path: Path to the file containing the asset data
        :param Dict[str, Any] data: The parsed data containing validater, mapping, and data
        :return: IntegrationAsset object
        :rtype: IntegrationAsset
        """
        # Get the first issue to extract host information
        issues = data.get("Issue", [])
        if not issues:
            # If no issues found, create a default asset based on the file name
            file_name = os.path.basename(str(file_path))
            return IntegrationAsset(
                identifier=file_name,
                name=file_name,
                ip_address="0.0.0.0",
                status=AssetStatus.Active,
                asset_type="Other",
                asset_category="Hardware",
                parent_id=self.plan_id,
                parent_module="securityplans" if not self.is_component else "components",
            )

        # Get the host from the first issue
        host = issues[0].get("Host", "Unknown Host")
        url = issues[0].get("URL", "")

        # Create and return the asset
        return IntegrationAsset(
            identifier=host,
            name=host,
            ip_address="0.0.0.0",  # Default IP address
            status=AssetStatus.Active,
            asset_type="Other",
            asset_category="Hardware",
            parent_id=self.plan_id,
            parent_module="securityplans" if not self.is_component else "components",
            fqdn=url,
        )

    def _get_findings_data_from_file(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract findings data from WebInspect file data.

        :param Dict[str, Any] data: The data from the WebInspect file
        :return: List of finding items
        :rtype: List[Dict[str, Any]]
        """
        if not data or not isinstance(data, dict):
            return []

        # Get the issues from the data
        issues = data.get("Issue", [])
        if not isinstance(issues, list):
            return []

        # Filter out findings with severity levels we don't want to include
        filtered_issues = []
        for issue in issues:
            severity_int = int(issue.get("Severity", 3))
            severity_value = self.finding_severity_map.get(severity_int, IssueSeverity.High.value)

            try:
                severity = IssueSeverity(severity_value)
                # Only include findings with certain severity levels
                if severity in (IssueSeverity.Critical, IssueSeverity.High, IssueSeverity.Moderate, IssueSeverity.Low):
                    filtered_issues.append(issue)
            except ValueError:
                # Include by default if we can't determine severity
                filtered_issues.append(issue)

        return filtered_issues

    @staticmethod
    def _parse_report_section(sections: List[dict], section_name: str) -> str:
        """
        Extract text from a specific report section.

        :param List[dict] sections: List of report sections
        :param str section_name: Name of the section to extract text from
        :return: Text from the specified section
        :rtype: str
        """
        if not sections:
            return ""

        return next((section.get("SectionText", "") for section in sections if section.get("Name") == section_name), "")

    def parse_finding(self, asset_identifier: str, data: Dict[str, Any], item: Dict[str, Any]) -> IntegrationFinding:
        """
        Parse a single finding from WebInspect scan data.

        :param str asset_identifier: The identifier of the asset this finding belongs to
        :param Dict[str, Any] data: The parsed data (not used here, kept for interface compatibility)
        :param Dict[str, Any] item: The finding data
        :return: IntegrationFinding object
        :rtype: IntegrationFinding
        """
        severity_int = int(item.get("Severity", 3))
        severity_value = self.finding_severity_map.get(severity_int, IssueSeverity.High.value)
        try:
            severity = IssueSeverity(severity_value)
        except ValueError:
            severity = IssueSeverity.High

        if self.scan_date is None:
            self.scan_date = self.file_date or get_current_datetime()

        title = item.get("Name", "")
        plugin_id = item.get("VulnerabilityID", "")
        external_id = str(asset_identifier + plugin_id)
        sections = item.get("ReportSection", [])

        # Extract description and mitigation from report sections
        description = self._parse_report_section(sections, "Summary")
        mitigation = self._parse_report_section(sections, "Fix")

        return IntegrationFinding(
            external_id=external_id,
            asset_identifier=asset_identifier,
            control_labels=[],
            description=description,
            status=IssueStatus.Open,
            title=title,
            severity=severity,
            category=f"{self.title} Vulnerability",
            scan_date=self.scan_date,
            first_seen=self.scan_date,
            last_seen=self.scan_date,
            date_created=self.scan_date,
            plugin_id=plugin_id,
            plugin_name=title,
            rule_id=plugin_id,
            recommendation_for_mitigation=mitigation,
            source_report=self.title,
            due_date=issue_due_date(
                severity=severity, created_date=self.scan_date, title="opentext", config=self.app.config
            ),
        )
