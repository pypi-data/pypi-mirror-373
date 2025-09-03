"""
Abstract base class for scanner integrations that use JSONL files for intermediate storage.
"""

import dataclasses
import json
import logging
import os
import shutil
import tempfile
import traceback
from datetime import datetime, time
from typing import Any, Dict, Iterator, Optional, Union, Tuple, TypeVar, Type, List

import boto3
from pathlib import Path

from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.core.app.utils.file_utils import is_s3_path, read_file, find_files, download_from_s3
from regscale.exceptions import ValidationException
from regscale.integrations.scanner_integration import IntegrationAsset, IntegrationFinding, ScannerIntegration
from regscale.models import regscale_models
from regscale.models.app_models.mapping import Mapping

logger = logging.getLogger("regscale")

# Define generic types for items that can be written to file
T = TypeVar("T")
ItemType = TypeVar("ItemType", IntegrationAsset, IntegrationFinding)


class JSONLScannerIntegration(ScannerIntegration):
    """
    Abstract base class for scanner integrations that use JSONL files for intermediate storage.

    This class extends ScannerIntegration to provide common functionality for scanners
    that process source files (local or S3) and store the results in JSONL files before syncing to RegScale.
    Supports reading files directly without downloading when read_files_only is True.

    Subclasses must implement:
    - find_valid_files: To find valid source files
    - parse_asset: To parse an asset from a source file
    - parse_finding: To parse a finding from a source file
    - is_valid_file: To validate a file before processing
    """

    # Constants for file paths - subclasses should override these
    ASSETS_FILE = "./artifacts/assets.jsonl"
    FINDINGS_FILE = "./artifacts/findings.jsonl"
    DT_FORMAT = "%Y-%m-%d"

    def __init__(self, *args, **kwargs):
        """
        Initialize the JSONLScannerIntegration.
        """
        logger.info("Initializing JSONLScannerIntegration")
        self.plan_id = kwargs.get("plan_id", None)

        # Pass vulnerability creation option to parent class
        self.vulnerability_creation = kwargs.get("vulnerability_creation", None)

        # plan_id is required for all integrations
        super().__init__(**kwargs)
        self.is_component = kwargs.get("is_component", False)
        # Extract S3-related kwargs
        self.s3_bucket = kwargs.get("s3_bucket", None)
        self.s3_prefix = kwargs.get("s3_prefix", "")
        self.aws_profile = kwargs.get("aws_profile", "default")

        self.file_path = kwargs.get("file_path", None)
        self.empty_files: bool = True
        self.download_destination = kwargs.get("destination", None)
        self.file_pattern = kwargs.get("file_pattern", "*.json")
        self.read_files_only = kwargs.get("read_files_only", False)

        # Extract mapping-related kwargs
        self.disable_mapping = kwargs.get("disable_mapping", False)
        self.mapping_path = kwargs.get("mapping_path", f"./mappings/{self.__class__.__name__.lower()}/mapping.json")
        self.required_asset_fields = kwargs.get("required_asset_fields", ["identifier", "name"])
        self.required_finding_fields = kwargs.get("required_finding_fields", ["asset_identifier", "title", "severity"])
        self.mapping = self._load_mapping() if not self.disable_mapping else None

        self.set_scan_date(kwargs.get("scan_date", get_current_datetime()))

        self.existing_assets = {}

        self.s3_client = None
        if self.s3_bucket and not self.read_files_only:
            try:
                session = boto3.Session(profile_name=self.aws_profile)
                self.s3_client = session.client("s3")
            except Exception as e:
                logger.error(f"Failed to initialize S3 client with profile {self.aws_profile}: {str(e)}")
                raise ValidationException(f"S3 client initialization failed: {str(e)}")

    def set_scan_date(self, scan_date_input: str):
        """
        Set the scan date input.

        :param str scan_date_input: The scan date input (string or datetime)
        :return: The cleaned scan date in 'YYYY-MM-DD' format
        :rtype: str
        """

        self.scan_date: str = self.clean_scan_date(scan_date_input)
        logger.info(f"Setting scan date input to {self.scan_date}")

    def get_scan_date(self) -> str:
        """
        Get the scan date in 'YYYY-MM-DD' format.

        :return: The scan date as a string
        :rtype: str
        """
        if self.scan_date:
            return self.clean_scan_date(self.scan_date)
        return get_current_datetime()

    def create_scan_history(self) -> "regscale_models.ScanHistory":
        """
        Creates a new ScanHistory object for the current scan, using self.scan_date if available.

        :param str scan_date: The date of the scan in 'YYYY-MM-DD' format
        :return: A newly created ScanHistory object
        :rtype: regscale_models.ScanHistory
        """
        scan_date = self.get_scan_date()
        logger.info(f"Creating ScanHistory with scan_date: {scan_date}")
        scan_history = regscale_models.ScanHistory(
            parentId=self.plan_id,
            parentModule=(
                regscale_models.Component.get_module_string()
                if self.is_component
                else regscale_models.SecurityPlan.get_module_string()
            ),
            scanningTool=self.title,
            scanDate=scan_date,
            createdById=self.assessor_id,
            tenantsId=self.tenant_id,
            vLow=0,
            vMedium=0,
            vHigh=0,
            vCritical=0,
        ).create()

        count = 0
        regscale_models.ScanHistory.delete_object_cache(scan_history)
        while not regscale_models.ScanHistory.get_object(object_id=scan_history.id) and count < 10:
            logger.info("Waiting for ScanHistory to be created...")
            time.sleep(1)
            count += 1
            regscale_models.ScanHistory.delete_object_cache(scan_history)
        return scan_history

    @staticmethod
    def clean_scan_date(date_input: Optional[Union[str, datetime]]) -> Optional[str]:
        """
        Convert a date (string or datetime object) to a JSON-serializable string.

        Args:
            date_input: A date as a string (e.g., '2025-02-01') or datetime object, or None.

        Returns:
            A string in 'YYYY-MM-DD' format if date_input is valid, otherwise None.

        Examples:
            >>> to_json_date('2025-02-01')
            '2025-02-01'
            >>> to_json_date(datetime(2025, 2, 1))
            '2025-02-01'
            >>> to_json_date(None)
            None
        """
        if date_input is None:
            return None
        if isinstance(date_input, datetime):
            return date_input.strftime("%Y-%m-%d")
        if isinstance(date_input, str):
            try:
                datetime.strptime(date_input, "%Y-%m-%d")
                return date_input
            except ValueError:
                # Try parsing other common formats if needed
                try:
                    try:
                        dt = datetime.strptime(date_input, "%Y-%m-%dT%H:%M:%S")  # e.g., '2025-01-29T00:43:04'
                    except ValueError:
                        dt = datetime.strptime(date_input, "%Y-%m-%dT%H:%M:%S%z")  # e.g., '2025-01-29T00:43:51+0000'
                    return dt.strftime("%Y-%m-%d")
                except ValueError:
                    return None
        return None

    def _load_mapping(self) -> Optional[Mapping]:
        """Load the mapping configuration from a JSON file."""
        try:
            mapping_file = Path(self.mapping_path)
            if mapping_file.exists():
                with mapping_file.open("r") as f:
                    mapping_data = json.load(f)
                    return Mapping(**mapping_data)
            logger.debug(f"No mapping file found at {self.mapping_path}, using default mapping")
            return None
        except Exception as e:
            logger.error(f"Error loading mapping file {self.mapping_path}: {str(e)}")
            return None

    def _apply_mapping(
        self, source_data: Dict[str, Any], target_fields: Dict[str, Any], mapping: Dict[str, str]
    ) -> Dict[str, Any]:
        """Apply field mapping from source data to target fields."""
        mapped_data = target_fields.copy()

        if self.disable_mapping or not self.mapping or not hasattr(self.mapping, "fields"):
            return {**source_data, **mapped_data}

        for target_field, source_field in mapping.items():
            if source_field in source_data:
                mapped_data[target_field] = source_data[source_field]
            elif isinstance(source_field, dict) and "default" in source_field:
                mapped_data[target_field] = source_field["default"]

        return mapped_data

    def _validate_fields(self, item: Union[IntegrationAsset, IntegrationFinding], required_fields: list) -> None:
        """Validate that all required fields are present and non-empty."""
        missing_fields = []
        item_dict = dataclasses.asdict(item)

        for field in required_fields:
            if field not in item_dict or not item_dict[field]:
                missing_fields.append(field)

        if missing_fields:
            item_type = "asset" if isinstance(item, IntegrationAsset) else "finding"
            raise ValueError(f"Missing or empty required fields for {item_type}: {', '.join(missing_fields)}")

    def create_artifacts_dir(self) -> Path:
        """Create artifacts directory if it doesn't exist."""
        artifacts_dir = Path("./artifacts")
        artifacts_dir.mkdir(exist_ok=True, parents=True)
        return artifacts_dir

    def _get_item_key(self, item_dict: Dict[str, Any], item_type: str) -> str:
        """Generate a unique key for an item (asset or finding) dictionary."""
        if item_type == "asset":
            return item_dict.get("identifier", "unknown")
        else:  # finding
            asset_id = item_dict.get("asset_identifier", "unknown")
            cve = item_dict.get("cve", "")
            title = item_dict.get("title", "")
            if cve:
                return f"{asset_id}:{cve}"
            return f"{asset_id}:{title}"

    def _prepare_output_file(self, output_file: str, empty_file: bool, item_type: str) -> Dict[str, bool]:
        """Prepare output file and load existing records if necessary."""
        existing_items: Dict[str, bool] = {}

        if empty_file and os.path.exists(output_file):
            logger.info(f"Emptying existing file: {output_file}")
            open(output_file, "w").close()
        elif os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            logger.info(f"Reading existing records from: {output_file}")
            try:
                with open(output_file, "r") as f:
                    for line in f:
                        try:
                            record = json.loads(line.strip())
                            key = self._get_item_key(record, item_type)
                            existing_items[key] = True
                        except json.JSONDecodeError:
                            logger.warning(f"Could not parse line in {output_file}")
            except Exception as e:
                logger.warning(f"Error reading existing records: {str(e)}")

        return existing_items

    def _write_items_to_jsonl(
        self,
        file_path: str,
        output_file: str,
        item_type: str,
        empty_file: bool = True,
    ) -> int:
        """
        Process source files (local or S3) and write items (assets or findings) to JSONL.

        :param str file_path: Path to source file or directory (local or S3 URI)
        :param str output_file: Path to output JSONL file
        :param str item_type: Type of items to process ('asset' or 'finding')
        :param bool empty_file: Whether to empty the output file before writing (default: True)
        :return: Total count of items written
        :rtype: int
        """
        existing_items = self._prepare_output_file(output_file, empty_file, item_type)
        total_items_count = len(existing_items)
        processed_files = set()
        new_items_count = 0

        with open(output_file, "a") as output_f:
            for file_data in self.find_valid_files(file_path):
                file, data = self._extract_file_and_data(file_data)

                file_str = str(file)
                if file_str in processed_files:
                    continue

                processed_files.add(file_str)

                items_added = self._process_file_by_type(file, data, output_f, existing_items, item_type)
                new_items_count += items_added
                total_items_count += items_added

        self._log_items_added(new_items_count, item_type, output_file)
        return total_items_count

    def _extract_file_and_data(self, file_data: Any) -> Tuple[Union[Path, str], Optional[Dict[str, Any]]]:
        """
        Extract file path and data from file_data which might be a tuple or a single value.

        :param Any file_data: File data from find_valid_files
        :return: Tuple of (file_path, file_data)
        :rtype: Tuple[Union[Path, str], Optional[Dict[str, Any]]]
        """
        if isinstance(file_data, tuple) and len(file_data) >= 2:
            return file_data[0], file_data[1]
        return file_data, None

    def _process_file_by_type(
        self,
        file: Union[Path, str],
        data: Optional[Dict[str, Any]],
        output_f: Any,
        existing_items: Dict[str, bool],
        item_type: str,
    ) -> int:
        """
        Process a file based on the item type (asset or finding).

        :param Union[Path, str] file: File path
        :param Optional[Dict[str, Any]] data: File data
        :param Any output_f: Output file handle
        :param Dict[str, bool] existing_items: Dictionary of existing item keys
        :param str item_type: Type of items to process ('asset' or 'finding')
        :return: Number of items added
        :rtype: int
        """
        try:
            logger.info(f"Processing file: {file}")
            if item_type == "asset":
                return self._process_asset_file(file, data, output_f, existing_items)
            else:
                return self._process_finding_file(file, data, output_f, existing_items)
        except Exception as e:
            logger.error(f"Error processing file {file}: {str(e)}")
            return 0

    def _log_items_added(self, new_items_count: int, item_type: str, output_file: str) -> None:
        """
        Log information about the number of items added.

        :param int new_items_count: Number of new items added
        :param str item_type: Type of items processed ('asset' or 'finding')
        :param str output_file: Path to the output file
        """
        item_type_label = "assets" if item_type == "asset" else "findings"
        logger.info(f"Added {new_items_count} new {item_type_label} to {output_file}")

    def _process_asset_file(self, file, data, output_f, existing_items):
        """
        Process a single file for assets with mapping and validation.

        :param file: The file being processed
        :param data: The data from the file
        :param output_f: The output file handle
        :param existing_items: Dictionary of existing items
        :return: Number of assets processed
        :rtype: int
        """
        asset = self.parse_asset(file, data)
        asset_dict = dataclasses.asdict(asset)

        if not self.disable_mapping:
            mapped_asset_dict = self._apply_mapping(
                data or {},
                asset_dict,
                getattr(self.mapping, "fields", {}).get("asset_mapping", {}) if self.mapping else {},
            )
            mapped_asset = IntegrationAsset(**mapped_asset_dict)
        else:
            mapped_asset = asset

        self._validate_fields(mapped_asset, self.required_asset_fields)

        key = self._get_item_key(dataclasses.asdict(mapped_asset), "asset")
        if key in existing_items:
            logger.debug(f"Asset with identifier {key} already exists, skipping")
            return 0

        self._write_item(output_f, mapped_asset)
        existing_items[key] = True
        return 1

    def _process_finding_file(self, file, data, output_f, existing_items):
        """
        Process a single file for findings with mapping and validation.

        :param file: The file being processed
        :param data: The data from the file
        :param output_f: The output file handle
        :param existing_items: Dictionary of existing items
        :return: Number of findings processed
        :rtype: int
        """
        asset = self.parse_asset(file, data)
        identifier = asset.identifier
        findings_data = self._get_findings_data_from_file(data)

        findings_in_file = 0
        for finding_item in findings_data:
            finding = self.parse_finding(identifier, data, finding_item)
            finding_dict = dataclasses.asdict(finding)

            if not self.disable_mapping:
                mapped_finding_dict = self._apply_mapping(
                    finding_item,
                    finding_dict,
                    getattr(self.mapping, "fields", {}).get("finding_mapping", {}) if self.mapping else {},
                )
                mapped_finding = IntegrationFinding(**mapped_finding_dict)
            else:
                mapped_finding = finding

            self._validate_fields(mapped_finding, self.required_finding_fields)

            key = self._get_item_key(dataclasses.asdict(mapped_finding), "finding")
            if key in existing_items:
                logger.debug(f"Finding with key {key} already exists, skipping")
                continue

            self._write_item(output_f, mapped_finding)
            existing_items[key] = True
            findings_in_file += 1

        if findings_in_file > 0:
            logger.info(f"Added {findings_in_file} new findings from file {file}")
        return findings_in_file

    def _get_findings_data_from_file(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract findings data from file data (default implementation).

        Subclasses must override this method to extract findings data from their specific file format.

        :param Dict[str, Any] data: The data from the file
        :return: Iterable of finding items
        """
        # Default implementation returns an empty list
        # Subclasses must override this method
        return []

    def _yield_items_from_jsonl(self, jsonl_file: str, item_class: Type[ItemType]) -> Iterator[ItemType]:
        """
        Read items from JSONL file and yield them one by one with optimizations for large files.

        This method automatically selects an appropriate processing strategy based on file size:
        - Small files (<100MB): Simple line-by-line processing
        - Medium files (100MB-500MB): Batch processing with increased buffer size
        - Large files (>500MB): Parallel processing with multiprocessing

        :param str jsonl_file: Path to JSONL file containing items
        :param Type[ItemType] item_class: Class to convert dictionary items to (IntegrationAsset or IntegrationFinding)
        :yields: Items one at a time
        :rtype: Iterator[ItemType]
        """
        # Standard library imports should be at the module level, but these are only needed here
        # and having them at the top would create unnecessary dependencies for small files

        if not os.path.exists(jsonl_file):
            logger.warning(f"JSONL file {jsonl_file} does not exist")
            return

        # Check file size to determine best strategy
        file_size = os.path.getsize(jsonl_file)
        file_size_mb = file_size / (1024 * 1024)
        logger.info(f"Reading items from {jsonl_file} (size: {file_size_mb:.2f} MB)")

        # Select processing strategy based on file size
        if file_size < 100 * 1024 * 1024:  # < 100MB
            yield from self._process_small_file(jsonl_file, item_class)
        elif file_size < 500 * 1024 * 1024:  # 100MB-500MB
            yield from self._process_medium_file(jsonl_file, item_class)
        else:  # > 500MB
            yield from self._process_large_file(jsonl_file, item_class)

        logger.info(f"Finished reading items from {jsonl_file}")

    def _process_small_file(self, jsonl_file: str, item_class: Type[ItemType]) -> Iterator[ItemType]:
        """
        Process a small JSONL file (<100MB) using line-by-line processing.

        :param str jsonl_file: Path to JSONL file
        :param Type[ItemType] item_class: Class to convert dictionary items to
        :yields: Items one at a time
        :rtype: Iterator[ItemType]
        """
        with open(jsonl_file, "r") as f:
            for line_number, line in enumerate(f, 1):
                if not line.strip():  # Skip empty lines
                    continue

                try:
                    item_dict = json.loads(line.strip())
                    yield item_class(**item_dict)
                except json.JSONDecodeError:
                    logger.warning(f"Could not parse line {line_number} in {jsonl_file}")
                except Exception as e:
                    logger.error(f"Error processing line {line_number} in {jsonl_file}: {str(e)}")

    def _process_batch(self, batch: List[str], item_class: Type[ItemType]) -> List[ItemType]:
        """
        Process a batch of lines into item objects.

        :param List[str] batch: List of JSON lines to process
        :param Type[ItemType] item_class: Class to convert dictionary items to
        :return: List of processed items
        :rtype: List[ItemType]
        """
        results = []
        for line in batch:
            if not line.strip():  # Skip empty lines
                continue

            try:
                item_dict = json.loads(line.strip())
                results.append(item_class(**item_dict))
            except json.JSONDecodeError:
                logger.warning("Could not parse line in batch")
            except Exception as e:
                logger.error(f"Error processing line in batch: {str(e)}")
        return results

    def _process_medium_file(self, jsonl_file: str, item_class: Type[ItemType]) -> Iterator[ItemType]:
        """
        Process a medium-sized JSONL file (100MB-500MB) using batch processing.

        :param str jsonl_file: Path to JSONL file
        :param Type[ItemType] item_class: Class to convert dictionary items to
        :yields: Items one at a time
        :rtype: Iterator[ItemType]
        """
        batch_size = 10000  # Process 10,000 lines at a time
        buffer_size = 10 * 1024 * 1024  # 10MB buffer

        with open(jsonl_file, "r", buffering=buffer_size) as f:
            batch = []

            for line in f:
                batch.append(line)

                if len(batch) >= batch_size:
                    for item in self._process_batch(batch, item_class):
                        yield item
                    batch = []

            # Process any remaining lines
            if batch:
                for item in self._process_batch(batch, item_class):
                    yield item

    def _process_large_file(self, jsonl_file: str, item_class: Type[ItemType]) -> Iterator[ItemType]:
        """
        Process a large JSONL file (>500MB) using parallel processing.

        :param str jsonl_file: Path to JSONL file
        :param Type[ItemType] item_class: Class to convert dictionary items to
        :yields: Items one at a time
        :rtype: Iterator[ItemType]
        """
        from concurrent.futures import ProcessPoolExecutor
        from functools import partial

        max_workers = min(os.cpu_count() or 4, 8)
        batch_size = 10000  # Process 10,000 lines at a time
        buffer_size = 10 * 1024 * 1024  # 10MB buffer

        logger.info(f"Processing large file with {max_workers} workers, batch size: {batch_size}")

        with open(jsonl_file, "r", buffering=buffer_size) as f:
            batch = []
            process_func = partial(self._process_batch, item_class=item_class)

            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                for line in f:
                    batch.append(line)

                    if len(batch) >= batch_size:
                        future = executor.submit(process_func, batch)
                        batch = []
                        # Yield results as they complete
                        for item in future.result():
                            yield item

                # Process any remaining lines
                if batch:
                    for item in executor.submit(process_func, batch).result():
                        yield item

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
        existing_assets = self._prepare_output_file(assets_output_file, empty_assets_file, "asset")
        existing_findings = self._prepare_output_file(findings_output_file, empty_findings_file, "finding")

        asset_tracker = self._init_tracker(existing_assets)
        finding_tracker = self._init_tracker(existing_findings)
        processed_files = set()

        with open(assets_output_file, "a") as assets_file, open(findings_output_file, "a") as findings_file:
            for file, data in self._get_valid_file_data(file_path):
                if str(file) in processed_files:
                    continue

                processed_files.add(str(file))
                self._process_file(file, data, assets_file, findings_file, asset_tracker, finding_tracker)

        self._log_processing_results(asset_tracker.new_count, assets_output_file, "assets")
        self._log_processing_results(finding_tracker.new_count, findings_output_file, "findings")
        return asset_tracker.total_count, finding_tracker.total_count

    def _init_tracker(self, existing_items: Dict[str, bool]) -> "CountTracker":
        """
        Initialize a tracker for counting new and total items.

        :param Dict[str, bool] existing_items: Dictionary of existing item keys
        :return: Tracker object for managing counts
        :rtype: CountTracker
        """
        from dataclasses import dataclass

        @dataclass
        class CountTracker:
            existing: Dict[str, bool]
            new_count: int = 0
            total_count: int = 0

        return CountTracker(existing=existing_items, total_count=len(existing_items))

    def _get_valid_file_data(
        self, file_path: Union[str, Path]
    ) -> Iterator[Tuple[Union[Path, str], Optional[Dict[str, Any]]]]:
        """
        Yield valid file data from the given path.

        :param Union[str, Path] file_path: Path to source file or directory (local or S3 URI)
        :return: Iterator yielding tuples of (file path, parsed data)
        :rtype: Iterator[Tuple[Union[Path, str], Optional[Dict[str, Any]]]]
        """
        for file_data in self.find_valid_files(file_path):
            if isinstance(file_data, tuple) and len(file_data) >= 2:
                yield file_data[0], file_data[1]
            else:
                yield file_data, None

    def _process_file(
        self,
        file: Union[Path, str],
        data: Optional[Dict[str, Any]],
        assets_file: Any,
        findings_file: Any,
        asset_tracker: "CountTracker",
        finding_tracker: "CountTracker",
    ) -> None:
        """
        Process a single file for assets and findings.

        :param Union[Path, str] file: Path to the file being processed
        :param Optional[Dict[str, Any]] data: Parsed data from the file
        :param Any assets_file: Open file handle for writing assets
        :param Any findings_file: Open file handle for writing findings
        :param CountTracker asset_tracker: Tracker for asset counts
        :param CountTracker finding_tracker: Tracker for finding counts
        :rtype: None
        """
        try:
            logger.info(f"Processing file: {file}")
            self._process_asset(file, data, assets_file, asset_tracker)
            self._process_findings(file, data, findings_file, asset_tracker.existing, finding_tracker)
        except Exception:
            error_message = traceback.format_exc()
            logger.error(f"Error processing file {file}: {str(error_message)}")

    def _process_asset(
        self,
        file: Union[Path, str],
        data: Optional[Dict[str, Any]],
        assets_file: Any,
        tracker: "CountTracker",
    ) -> None:
        """
        Process and write a single asset from file data.

        :param Union[Path, str] file: Path to the file being processed
        :param Optional[Dict[str, Any]] data: Parsed data from the file
        :param Any assets_file: Open file handle for writing assets
        :param CountTracker tracker: Tracker for asset counts
        :rtype: None
        """
        asset = self.parse_asset(file, data)
        asset_dict = dataclasses.asdict(asset)
        mapped_asset = self._map_item(asset_dict, "asset_mapping", IntegrationAsset)
        self._validate_fields(mapped_asset, self.required_asset_fields)

        asset_key = mapped_asset.identifier
        if asset_key not in tracker.existing:
            self._write_item(assets_file, mapped_asset)
            tracker.existing[asset_key] = True
            tracker.new_count += 1
            tracker.total_count += 1
        else:
            logger.debug(f"Asset with identifier {asset_key} already exists, skipping")

    def _process_findings(
        self,
        file: Union[Path, str],
        data: Optional[Dict[str, Any]],
        findings_file: Any,
        existing_assets: Dict[str, bool],
        tracker: "CountTracker",
    ) -> None:
        """
        Process and write findings from file data.

        :param Union[Path, str] file: Path to the file being processed
        :param Optional[Dict[str, Any]] data: Parsed data from the file
        :param Any findings_file: Open file handle for writing findings
        :param Dict[str, bool] existing_assets: Dictionary of existing asset keys
        :param CountTracker tracker: Tracker for finding counts
        :rtype: None
        """
        findings_data = self._get_findings_data_from_file(data)
        logger.info(f"Found {len(findings_data)} findings in file: {file}")
        self.existing_assets = existing_assets
        asset_id = self._get_asset_id_from_assets()
        findings_added = self._process_finding_items(findings_data, asset_id, data, findings_file, tracker)

        if findings_added > 0:
            logger.info(f"Added {findings_added} new findings from file {file}")

    def _get_asset_id_from_assets(self) -> str:
        """
        Get the first asset ID from existing assets, or 'unknown' if none exist.

        :return: The first asset ID found or 'unknown'
        :rtype: str
        """
        return list(self.existing_assets.keys())[0] if self.existing_assets else "unknown"

    def _process_finding_items(
        self,
        findings_data: List[Dict[str, Any]],
        asset_id: str,
        data: Optional[Dict[str, Any]],
        findings_file: Any,
        tracker: "CountTracker",
    ) -> int:
        """
        Process individual finding items and write them to the findings file.

        :param List[Dict[str, Any]] findings_data: List of findings data
        :param str asset_id: Asset ID to associate with findings
        :param Optional[Dict[str, Any]] data: Source data from the file
        :param Any findings_file: Open file handle for writing findings
        :param CountTracker tracker: Tracker for finding counts
        :return: Number of findings added
        :rtype: int
        """
        findings_added = 0

        # Create a default asset_id to use only if absolutely necessary
        default_asset_id = self._get_asset_id_from_assets()

        # Process each finding individually
        for finding_item in findings_data:
            # Let the parse_finding implementation determine the correct asset_identifier
            # This relies on subclasses implementing parse_finding to extract the right asset ID
            # from the finding_item directly
            finding = self.parse_finding(default_asset_id, data, finding_item)
            finding_dict = dataclasses.asdict(finding)
            mapped_finding = self._map_item(finding_dict, "finding_mapping", IntegrationFinding)
            self._validate_fields(mapped_finding, self.required_finding_fields)

            finding_key = self._get_item_key(dataclasses.asdict(mapped_finding), "finding")
            if finding_key not in tracker.existing:
                self._write_item(findings_file, mapped_finding)
                tracker.existing[finding_key] = True
                tracker.new_count += 1
                tracker.total_count += 1

            if self._process_single_finding(finding_item, asset_id, data, findings_file, tracker):
                findings_added += 1

        return findings_added

    def _process_single_finding(
        self,
        finding_item: Dict[str, Any],
        asset_id: str,
        data: Optional[Dict[str, Any]],
        findings_file: Any,
        tracker: "CountTracker",
    ) -> bool:
        """
        Process a single finding item and write it if it's new.

        :param Dict[str, Any] finding_item: Finding data
        :param str asset_id: Asset ID to associate with the finding
        :param Optional[Dict[str, Any]] data: Source data from the file
        :param Any findings_file: Open file handle for writing findings
        :param CountTracker tracker: Tracker for finding counts
        :return: True if the finding was added, False otherwise
        :rtype: bool
        """
        finding = self.parse_finding(asset_id, data, finding_item)
        finding_dict = dataclasses.asdict(finding)
        mapped_finding = self._map_item(finding_dict, "finding_mapping", IntegrationFinding)
        self._validate_fields(mapped_finding, self.required_finding_fields)

        finding_key = self._get_item_key(dataclasses.asdict(mapped_finding), "finding")

        if finding_key in tracker.existing:
            logger.debug(f"Finding with key {finding_key} already exists, skipping")
            return False

        self._write_item(findings_file, mapped_finding)
        tracker.existing[finding_key] = True
        tracker.new_count += 1
        tracker.total_count += 1
        return True

    def _map_item(self, item_dict: Dict[str, Any], mapping_key: str, item_class: Type) -> Any:
        """
        Apply mapping to an item dictionary if enabled.

        :param Dict[str, Any] item_dict: Dictionary of item data
        :param str mapping_key: Key in the mapping configuration to use (e.g., 'asset_mapping')
        :param Type item_class: Class to instantiate with mapped data (IntegrationAsset or IntegrationFinding)
        :return: Instantiated item object with mapped data
        :rtype: Any
        """
        if not self.disable_mapping and self.mapping and hasattr(self.mapping, "fields"):
            mapped_dict = self._apply_mapping(
                item_dict, item_dict, getattr(self.mapping, "fields", {}).get(mapping_key, {})
            )
            return item_class(**mapped_dict)
        return item_class(**item_dict)

    def _write_item(self, file_handle_or_path: Any, item: Any) -> None:
        """
        Write an item to a JSONL file.

        :param Any file_handle_or_path: Open file handle or file path to write to
        :param Any item: Item to write (IntegrationAsset or IntegrationFinding)
        """
        try:
            item_dict = self._convert_item_to_dict(item)
            item_dict = self._ensure_serializable(item_dict)
            self._write_dict_to_file(file_handle_or_path, item_dict)
        except Exception as e:
            logger.error(f"Error writing item: {str(e)}")
            logger.debug(f"Problem item: {str(item)}")
            self._write_fallback_record(file_handle_or_path, item, e)

    def _convert_item_to_dict(self, item: Any) -> Dict[str, Any]:
        """
        Convert an item to a dictionary using the most appropriate method.

        :param Any item: Item to convert
        :return: Dictionary representation of the item
        :rtype: Dict[str, Any]
        """
        if dataclasses.is_dataclass(item):
            return dataclasses.asdict(item)

        if hasattr(item, "to_dict") and callable(item.to_dict):
            return item.to_dict()

        if hasattr(item, "__dict__"):
            return item.__dict__

        if isinstance(item, dict):
            return item

        return {"value": str(item)}

    def _write_dict_to_file(self, file_handle_or_path: Any, item_dict: Dict[str, Any]) -> None:
        """
        Write a dictionary to a file as JSON.

        :param Any file_handle_or_path: Open file handle or file path
        :param Dict[str, Any] item_dict: Dictionary to write
        """
        json_line = json.dumps(item_dict) + "\n"

        if self._is_file_handle(file_handle_or_path):
            file_handle_or_path.write(json_line)
            file_handle_or_path.flush()
        else:
            with open(file_handle_or_path, "a") as f:
                f.write(json_line)

    def _is_file_handle(self, file_handle_or_path: Any) -> bool:
        """
        Check if the given object is a file handle.

        :param Any file_handle_or_path: Object to check
        :return: True if it's a file handle, False otherwise
        :rtype: bool
        """
        return hasattr(file_handle_or_path, "write") and callable(file_handle_or_path.write)

    def _write_fallback_record(self, file_handle_or_path: Any, item: Any, error: Exception) -> None:
        """
        Write a simplified fallback record when normal serialization fails.

        :param Any file_handle_or_path: Open file handle or file path
        :param Any item: Original item that failed to serialize
        :param Exception error: The exception that occurred
        """
        try:
            simplified = {
                "error": "Failed to serialize original item",
                "item_type": str(type(item)),
                "error_message": str(error),
            }

            if hasattr(item, "__str__"):
                simplified["item_string"] = str(item)

            self._write_dict_to_file(file_handle_or_path, simplified)
            logger.warning("Wrote simplified version of item after serialization error")
        except Exception as e2:
            logger.error(f"Failed to write simplified item: {str(e2)}")

    def _ensure_serializable(self, obj: Any) -> Any:
        """
        Ensure all values in an object are JSON serializable.

        :param Any obj: Object to make serializable
        :return: Serializable object
        """
        if isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: self._ensure_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._ensure_serializable(i) for i in obj]
        elif dataclasses.is_dataclass(obj):
            return self._ensure_serializable(dataclasses.asdict(obj))
        elif hasattr(obj, "to_dict") and callable(obj.to_dict):
            return self._ensure_serializable(obj.to_dict())
        elif hasattr(obj, "__dict__"):
            return self._ensure_serializable(obj.__dict__)
        else:
            return str(obj)

    def _log_processing_results(self, new_count: int, output_file: str, item_type: str) -> None:
        """
        Log the results of processing items.

        :param int new_count: Number of new items added
        :param str output_file: Path to the output file
        :param str item_type: Type of items processed ('assets' or 'findings')
        :rtype: None
        """
        logger.info(f"Added {new_count} new {item_type} to {output_file}")

    def _validate_file_path(self, file_path: Optional[str]) -> str:
        """
        Validates the file path and raises an exception if it's invalid.

        :param Optional[str] file_path: Path to validate
        :return: The validated file path
        :rtype: str
        :raises ValidationException: If the file path is invalid
        """
        if not file_path:
            logger.error("No file path provided")
            raise ValidationException("File path is required")

        if not is_s3_path(file_path) and not os.path.exists(file_path):
            logger.error(f"File path does not exist: {file_path}")
            raise ValidationException(f"Path does not exist: {file_path}")

        return file_path

    def fetch_assets(self, *args: Any, **kwargs: Any) -> Iterator[IntegrationAsset]:
        """
        Fetches assets from processed source files (local or S3).

        This method supports both local files/directories and S3 paths.

        :param str file_path: Path to a source file or directory
        :param bool empty_file: Whether to empty the output file before writing (default: True)
        :param bool process_together: Whether to process assets and findings together (default: False)
        :param bool use_jsonl_file: Whether to use an existing JSONL file instead of processing source files
        (default: False)
        :yields: Iterator[IntegrationAsset]
        """
        logger.info("Starting fetch_assets")

        return self._fetch_items(
            "asset",
            self.ASSETS_FILE,
            IntegrationAsset,
            kwargs.get("file_path", self.file_path),
            kwargs.get("empty_file", True),
            kwargs.get("process_together", False),
            kwargs.get("use_jsonl_file", False),
        )

    def fetch_findings(self, *args: Any, **kwargs: Any) -> Iterator[IntegrationFinding]:
        """
        Fetches findings from processed source files (local or S3).

        This method supports both local files/directories and S3 paths.

        :param str file_path: Path to source file or directory
        :param bool empty_file: Whether to empty the output file before writing (default: True)
        :param bool process_together: Whether to process assets and findings together (default: False)
        :param bool use_jsonl_file: Whether to use an existing JSONL file instead of processing source files (default: False)
        :yields: Iterator[IntegrationFinding]
        """
        logger.info("Starting fetch_findings")

        return self._fetch_items(
            "finding",
            self.FINDINGS_FILE,
            IntegrationFinding,
            kwargs.get("file_path", self.file_path),
            kwargs.get("empty_file", True),
            kwargs.get("process_together", False),
            kwargs.get("use_jsonl_file", False),
        )

    def _fetch_items(
        self,
        item_type: str,
        jsonl_file: str,
        item_class: Type[ItemType],
        file_path: Optional[str] = None,
        empty_file: bool = True,
        process_together: bool = False,
        use_jsonl_file: bool = False,
    ) -> Iterator[ItemType]:
        """
        Common method to fetch assets or findings from processed source files.

        :param str item_type: Type of items to fetch ('asset' or 'finding')
        :param str jsonl_file: Path to the JSONL file containing items
        :param Type[ItemType] item_class: Class to convert dictionary items to
        :param Optional[str] file_path: Path to source file or directory
        :param bool empty_file: Whether to empty the output file before writing
        :param bool process_together: Whether to process assets and findings together
        :param bool use_jsonl_file: Whether to use an existing JSONL file
        :yields: Iterator[ItemType]
        :rtype: Iterator[ItemType]
        """
        self.create_artifacts_dir()
        is_asset = item_type == "asset"
        counter_attr = "num_assets_to_process" if is_asset else "num_findings_to_process"

        if use_jsonl_file:
            logger.info(f"Using existing JSONL file: {jsonl_file}")
            total_items = sum(1 for _ in open(jsonl_file, "r")) if os.path.exists(jsonl_file) else 0
            setattr(self, counter_attr, total_items)
            logger.info(f"Found {total_items} {item_type}s in existing JSONL file")
        else:
            file_path = self._validate_file_path(file_path)
            total_items = self._process_source_files(
                file_path, jsonl_file, item_type, empty_file, process_together, counter_attr
            )
            logger.info(f"Total {item_type}s to process: {total_items}")

        # Yield items from the JSONL file
        for item in self._yield_items_from_jsonl(jsonl_file, item_class):
            yield item

        logger.info(
            f"{item_type.capitalize()}s read from JSONL complete. Total {item_type}s identified: {getattr(self, counter_attr)}"
        )

    def _process_source_files(
        self,
        file_path: str,
        jsonl_file: str,
        item_type: str,
        empty_file: bool,
        process_together: bool,
        counter_attr: str,
    ) -> int:
        """
        Process source files and return the total count of items.

        :param str file_path: Path to source file or directory
        :param str jsonl_file: Path to the JSONL file to write
        :param str item_type: Type of items to process ('asset' or 'finding')
        :param bool empty_file: Whether to empty output files
        :param bool process_together: Whether to process assets and findings together
        :param str counter_attr: Attribute name for storing the count
        :return: Total count of items
        :rtype: int
        """
        is_asset = item_type == "asset"

        if process_together:
            # Handle joint processing of assets and findings
            asset_count, finding_count = self._process_files(
                file_path,
                self.ASSETS_FILE,
                self.FINDINGS_FILE,
                empty_assets_file=empty_file if is_asset else False,
                empty_findings_file=empty_file if not is_asset else False,
            )
            total_items = asset_count if is_asset else finding_count
        else:
            # Process just one type
            total_items = self._write_items_to_jsonl(file_path, jsonl_file, item_type, empty_file=empty_file)

        setattr(self, counter_attr, total_items)
        return total_items

    def parse_asset(self, file_path: Union[Path, str], data: Dict[str, Any]) -> IntegrationAsset:
        """
        Parse a single asset from source data.

        Subclasses must implement this method to parse assets from their specific file format.

        :param Union[Path, str] file_path: Path to the file containing the asset data
        :param Dict[str, Any] data: The parsed data
        :return: IntegrationAsset object
        :rtype: IntegrationAsset
        """
        raise NotImplementedError("Subclasses must implement parse_asset")

    def parse_finding(self, asset_identifier: str, data: Dict[str, Any], item: Dict[str, Any]) -> IntegrationFinding:
        """Parse a single finding from source data.

        Subclasses must implement this method to parse findings from their specific file format.

        :param str asset_identifier: The identifier of the asset this finding belongs to
        :param Dict[str, Any] data: The asset data
        :param Dict[str, Any] item: The finding data
        :return: IntegrationFinding object
        :rtype: IntegrationFinding
        """
        raise NotImplementedError("Subclasses must implement parse_finding")

    def is_valid_file(self, data: Any, file_path: Union[Path, str]) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Check if the provided data is valid for processing.

        This default implementation ensures the data is a non-empty dictionary.
        Subclasses should override this to implement specific validation logic.

        :param Any data: Data parsed from the file to validate
        :param Union[Path, str] file_path: Path to the file being processed
        :return: Tuple of (is_valid, data) where is_valid indicates validity and data is the validated content or None
        :rtype: Tuple[bool, Optional[Dict[str, Any]]]
        """
        if not isinstance(data, dict):
            logger.warning(f"Data is not a dictionary for file {file_path}, skipping")
            return False, None

        if not data:
            logger.warning(f"Data is an empty dictionary for file {file_path}, skipping")
            return False, None

        return True, data

    def fetch_assets_and_findings(
        self, file_path: str = None, empty_files: bool = True
    ) -> Tuple[Iterator[IntegrationAsset], Iterator[IntegrationFinding]]:
        """Process both assets and findings (local or S3) in a single pass and return iterators.

        This method optimizes the processing by reading each file only once and extracting
        both asset and finding information in a single pass. It returns two iterators,
        one for assets and one for findings.

        :param str file_path: Path to source file or directory
        :param bool empty_files: Whether to empty both output files before writing (default: True)
        :return: Tuple of (assets_iterator, findings_iterator)
        :rtype: Tuple[Iterator[IntegrationAsset], Iterator[IntegrationFinding]]
        """
        file_path = self._validate_file_path(file_path or self.file_path)
        self.create_artifacts_dir()

        logger.info("Processing assets and findings together from %s", file_path)
        total_assets, total_findings = self._process_files(
            file_path=file_path,
            assets_output_file=self.ASSETS_FILE,
            findings_output_file=self.FINDINGS_FILE,
            empty_assets_file=empty_files,
            empty_findings_file=empty_files,
        )

        self.num_assets_to_process = total_assets
        self.num_findings_to_process = total_findings

        assets_iterator = self._yield_items_from_jsonl(self.ASSETS_FILE, IntegrationAsset)
        findings_iterator = self._yield_items_from_jsonl(self.FINDINGS_FILE, IntegrationFinding)
        return assets_iterator, findings_iterator

    def sync_assets_and_findings(self) -> None:
        """Process both assets and findings (local or S3) in a single pass and sync to RegScale.

        This method optimizes the processing by reading each file only once and
        extracting both asset and finding information in a single pass.

        :param int plan_id: RegScale Security Plan ID
        :param str file_path: Path to source file or directory
        :param bool empty_files: Whether to empty both output files before writing (default: True)
        :rtype: None
        """
        file_path = self._validate_file_path(self.file_path)
        logger.info("Processing assets and findings together from %s", file_path)
        total_assets, total_findings = self._process_files(
            file_path=file_path,
            assets_output_file=self.ASSETS_FILE,
            findings_output_file=self.FINDINGS_FILE,
            empty_assets_file=self.empty_files,
            empty_findings_file=self.empty_files,
        )

        logger.info("Syncing %d assets to RegScale", total_assets)
        self.sync_assets(
            plan_id=self.plan_id,
            file_path=file_path,
            use_jsonl_file=True,
            asset_count=total_assets,
            scan_date=self.scan_date,
            is_component=self.is_component,
        )

        logger.info("Syncing %d findings to RegScale", total_findings)
        self.sync_findings(
            plan_id=self.plan_id,
            file_path=file_path,
            use_jsonl_file=True,
            finding_count=total_findings,
            scan_date=self.scan_date,
            is_component=self.is_component,
        )

        logger.info("Assets and findings sync complete")

    # Abstract method with default implementation for reading files
    def find_valid_files(self, path: Union[Path, str]) -> Iterator[Tuple[Union[Path, str], Dict[str, Any]]]:
        """
        Find all valid source files in the given path and read their contents if read_files_only is True.

        Subclasses must override this method to customize file validation and data extraction.

        :param Union[Path, str] path: Path to a file or directory (local or S3 URI)
        :return: Iterator yielding tuples of (file path, validated data)
        :rtype: Iterator[Tuple[Union[Path, str], Dict[str, Any]]]
        """
        for file in find_files(path, self.file_pattern):
            data = self._read_file_content(file)
            if data is not None:
                yield from self._validate_and_yield(file, data)

    def _read_file_content(self, file: Union[Path, str]) -> Optional[Dict[str, Any]]:
        """
        Read and parse the content of a file based on read_files_only setting.

        :param Union[Path, str] file: Path to the file to read
        :return: Parsed JSON data or None if reading fails
        :rtype: Optional[Dict[str, Any]]
        """
        try:
            if self.read_files_only:
                return self._read_content_directly(file)
            return self._read_content_with_download(file)
        except json.JSONDecodeError:
            logger.warning(f"File {file} is not valid JSON, skipping")
            return None
        except Exception as e:
            logger.error(f"Error reading file {file}: {str(e)}")
            return None

    def _read_content_directly(self, file: Union[Path, str]) -> Dict[str, Any]:
        """
        Read file content directly when read_files_only is True.

        :param Union[Path, str] file: Path to the file
        :return: Parsed JSON data
        :rtype: Dict[str, Any]
        """
        content = read_file(file)
        return json.loads(content) if content else {}

    def _read_content_with_download(self, file: Union[Path, str]) -> Dict[str, Any]:
        """
        Read file content, downloading from S3 if necessary, when read_files_only is False.

        :param Union[Path, str] file: Path to the file (local or S3 URI)
        :return: Parsed JSON data
        :rtype: Dict[str, Any]
        """
        if is_s3_path(file):
            temp_dir = Path(tempfile.mkdtemp())
            try:
                s3_parts = file[5:].split("/", 1)
                bucket = s3_parts[0]
                prefix = s3_parts[1] if len(s3_parts) > 1 else ""
                download_from_s3(bucket, prefix, temp_dir, self.aws_profile)
                local_file = temp_dir / os.path.basename(prefix)
                with open(local_file, "r") as f:
                    return json.load(f)
            finally:
                shutil.rmtree(temp_dir)
        else:
            with open(file, "r") as f:
                return json.load(f)

    def _validate_and_yield(
        self, file: Union[Path, str], data: Dict[str, Any]
    ) -> Iterator[Tuple[Union[Path, str], Dict[str, Any]]]:
        """
        Validate file data and yield it if valid.

        :param Union[Path, str] file: Path to the file
        :param Dict[str, Any] data: Parsed data from the file
        :return: Iterator yielding valid file data tuples
        :rtype: Iterator[Tuple[Union[Path, str], Dict[str, Any]]]
        """
        is_valid, validated_data = self.is_valid_file(data, file)
        if is_valid and validated_data is not None:
            yield file, validated_data
