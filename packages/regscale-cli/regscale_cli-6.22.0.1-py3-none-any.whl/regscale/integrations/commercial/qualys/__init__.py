"""
Qualys integration module for RegScale CLI.
"""

import logging
import os
import pprint
import traceback
from asyncio import sleep
from datetime import datetime, timedelta, timezone
from json import JSONDecodeError
from pathlib import Path
from typing import Any, Optional, Tuple, Union
from urllib.parse import urljoin

import click
import requests
import xmltodict
from requests import Session
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskID, TextColumn, TimeElapsedColumn

from regscale.core.app.utils.app_utils import (
    check_file_path,
    check_license,
    create_progress_object,
    error_and_exit,
    get_current_datetime,
    save_data_to,
)
from regscale.core.app.utils.file_utils import download_from_s3
from regscale.integrations.commercial.qualys.containers import fetch_all_vulnerabilities
from regscale.integrations.commercial.qualys.qualys_error_handler import QualysErrorHandler
from regscale.integrations.commercial.qualys.scanner import QualysTotalCloudJSONLIntegration
from regscale.integrations.commercial.qualys.variables import QualysVariables
from regscale.integrations.scanner_integration import IntegrationAsset, IntegrationFinding
from regscale.integrations.variables import ScannerVariables
from regscale.models import Asset, Issue, Search, regscale_models
from regscale.models.app_models.click import NotRequiredIf, regscale_ssp_id, save_output_to, ssp_or_component_id
from regscale.models.integration_models.ecr_models.data import Finding
from regscale.models.integration_models.flat_file_importer import FlatFileImporter
from regscale.models.integration_models.qualys import (
    Qualys,
    QualysContainerScansImporter,
    QualysPolicyScansImporter,
    QualysWasScansImporter,
)
from regscale.validation.record import validate_regscale_object

# Create logger for this module
logger = logging.getLogger("regscale")
job_progress = create_progress_object()
HEADERS = {"X-Requested-With": "RegScale CLI"}

# Import the Qualys API session object and headers from the main qualys module
QUALYS_API = Session()


@click.group()
def qualys():
    """Performs actions from the Qualys API"""


def _prepare_qualys_params(include_tags: str, exclude_tags: str) -> dict:
    """
    Prepare parameters for Qualys API request.

    :param str include_tags: Tags to include in the filter
    :param str exclude_tags: Tags to exclude in the filter
    :return: Dictionary of parameters for the API request
    :rtype: dict
    """
    params = {
        "action": "list",
        "show_asset_id": "1",
        "show_tags": "1",
    }
    if exclude_tags or include_tags:
        params["use_tags"] = "1"
        params["tag_set_by"] = "name"
        if exclude_tags:
            params["tag_set_exclude"] = exclude_tags
        if include_tags:
            params["tag_set_include"] = include_tags

    return params


def _setup_progress_tracking(integration, progress):
    """
    Set up progress tracking for assets and findings.

    :param integration: Scanner integration instance
    :param progress: Progress bar instance
    :return: Tuple of task IDs and counts for assets and findings
    :rtype: tuple
    """
    # Count assets and findings for progress tracking
    asset_count = sum(1 for _ in open(integration.ASSETS_FILE, "r") if _.strip())
    finding_count = sum(1 for _ in open(integration.FINDINGS_FILE, "r") if _.strip())

    logger.info(f"Found {asset_count} assets and {finding_count} findings in JSONL files")

    # Create tasks
    asset_task = progress.add_task(f"[green]Importing {asset_count} assets to RegScale...", total=asset_count)
    finding_task = progress.add_task(f"[yellow]Importing {finding_count} findings to RegScale...", visible=False)

    return asset_task, finding_task, asset_count, finding_count


def _import_assets(integration, assets_iterator, progress, asset_task):
    """
    Import assets to RegScale with progress tracking.

    :param integration: Scanner integration instance
    :param assets_iterator: Iterator of assets
    :param progress: Progress bar instance to track progress
    :param asset_task: Task ID for asset progress
    :return: Number of assets imported
    :rtype: int
    """
    if not _verify_assets_file_exists(integration):
        return 0

    try:
        wrapped_iterator = _create_asset_progress_tracker(assets_iterator, progress, asset_task)
        assets_imported = integration.update_regscale_assets(wrapped_iterator)
        logger.info(f"Imported {assets_imported} assets to RegScale")
        return assets_imported
    except Exception as e:
        logger.error(f"Error importing assets to RegScale: {str(e)}")
        logger.error(traceback.format_exc())
        return 0


def _verify_assets_file_exists(integration):
    """
    Verify that the assets file exists and is not empty.

    :param integration: Scanner integration instance
    :return: True if the file exists and is not empty, False otherwise
    :rtype: bool
    """
    if not os.path.exists(integration.ASSETS_FILE) or os.path.getsize(integration.ASSETS_FILE) == 0:
        logger.warning(f"Assets file {integration.ASSETS_FILE} is empty or does not exist")
        return False
    return True


def _create_asset_progress_tracker(assets_iter, progress, asset_task):
    """
    Create a generator that tracks progress of asset processing.

    :param assets_iter: Iterator of assets
    :param progress: Progress bar instance
    :param asset_task: Task ID for asset progress
    :return: Generator that yields assets and updates progress
    """
    count = 0
    asset_ids = []

    try:
        for asset in assets_iter:
            count += 1
            if asset and hasattr(asset, "identifier"):
                asset_ids.append(asset.identifier)
            progress.update(asset_task, advance=1)
            yield asset

        _log_asset_results(count, asset_ids)
    except Exception as e:
        logger.error(f"Error while yielding assets: {str(e)}")
        logger.error(traceback.format_exc())


def _log_asset_results(count, asset_ids):
    """
    Log the results of asset processing.

    :param count: Number of assets processed
    :param asset_ids: List of asset IDs
    """
    if count == 0:
        logger.warning("No assets were created/updated from the JSONL file")
    else:
        sample_ids = asset_ids[:5]
        truncation_indicator = ", ..." if len(asset_ids) > 5 else ""
        sample_ids_str = ", ".join(sample_ids)
        logger.debug(f"Created/updated {count} assets to RegScale with IDs: {sample_ids_str}{truncation_indicator}")


def _import_findings(integration, progress, finding_task):
    """
    Import findings to RegScale with progress tracking.

    :param integration: Scanner integration instance
    :param progress: Progress bar instance
    :param finding_task: Task ID for finding progress
    :return: Number of findings imported
    :rtype: int
    """
    progress.update(finding_task, visible=True)
    total_findings = _count_findings_in_file(integration)

    if total_findings > 0:
        progress.update(finding_task, total=total_findings)

    findings_yielded = 0
    try:
        # Create findings iterator directly from the file
        tracked_iterator = _create_finding_progress_tracker(
            integration._yield_items_from_jsonl(integration.FINDINGS_FILE, IntegrationFinding), progress, finding_task
        )

        findings_imported = integration.update_regscale_findings(tracked_iterator)
        logger.info(f"Successfully imported {findings_imported} findings to RegScale")

        # Update final count for nonlocal reference from the tracked_iterator
        findings_yielded = getattr(tracked_iterator, "count", 0)

        # Ensure progress is complete
        if findings_yielded > 0:
            progress.update(finding_task, completed=findings_yielded)

        return findings_imported
    except Exception as e:
        logger.error(f"Error during RegScale findings import: {str(e)}")
        return 0


def _count_findings_in_file(integration):
    """
    Count the findings in the JSONL file.

    :param integration: Scanner integration instance
    :return: Number of findings in the file
    :rtype: int
    """
    try:
        if os.path.exists(integration.FINDINGS_FILE):
            with open(integration.FINDINGS_FILE, "r") as f:
                total_findings = sum(1 for line in f if line.strip())
                logger.info(f"Found {total_findings} findings in JSONL file")
                return total_findings
        else:
            logger.warning(f"Findings file {integration.FINDINGS_FILE} does not exist")
            return 0
    except Exception as e:
        logger.error(f"Error counting findings in JSONL file: {str(e)}")
        return 0


def _create_finding_progress_tracker(findings_iter, progress, finding_task):
    """
    Create a generator function that tracks progress of finding processing.

    :param findings_iter: Iterator of findings
    :param progress: Progress bar instance
    :param finding_task: Task ID for finding progress
    :return: Generator that yields findings and updates progress
    """
    tracker = FindingProgressTracker(findings_iter, progress, finding_task)
    return tracker


class FindingProgressTracker:
    """Class to track progress of finding processing with proper object reference."""

    def __init__(self, findings_iter, progress, finding_task):
        self.findings_iter = findings_iter
        self.progress = progress
        self.finding_task = finding_task
        self.count = 0
        self.finding_ids = []
        self.output_final_log: bool = False

    def __iter__(self):
        return self

    def __next__(self):
        try:
            finding = next(self.findings_iter)
            self.count += 1
            if finding and hasattr(finding, "external_id") and finding.external_id is not None:
                self.finding_ids.append(finding.external_id)
            self.progress.update(self.finding_task, advance=1)
            return finding
        except StopIteration:
            self._log_finding_results()
            return
        except Exception as e:
            logger.debug(f"Findings created/updated before error: {self.count}")
            error_and_exit(f"Error creating/updating findings: {str(e)}")

    def _log_finding_results(self):
        """Log the results of finding processing."""
        if self.count == 0:
            logger.warning("No findings were created/updated from the JSONL file")
        elif not self.output_final_log:
            logger.info(f"Created/Updated {self.count} findings to RegScale")
            sample_ids = self.finding_ids[:5]
            truncation_indicator = ", ..." if len(self.finding_ids) > 5 else ""
            sample_ids_str = ", ".join(sample_ids)
            logger.debug(f"Sample finding IDs: {sample_ids_str}{truncation_indicator}")
            self.output_final_log = True


@click.command(name="import_total_cloud")
@ssp_or_component_id()
@click.option(
    "--include_tags",
    "-t",
    type=click.STRING,
    required=False,
    default=None,
    help="Include tags in the import comma separated string of tag names or ids, defaults to None.",
)
@click.option(
    "--exclude_tags",
    "-e",
    type=click.STRING,
    required=False,
    default=None,
    help="Exclude tags in the import comma separated string of tag names or ids, defaults to None. If used, --include_tags must also be provided.",
)
@click.option(
    "--vulnerability-creation",
    "-v",
    type=click.Choice(["NoIssue", "IssueCreation", "PoamCreation"], case_sensitive=False),
    required=False,
    default=None,
    help="Specify how vulnerabilities are processed: NoIssue, IssueCreation, or PoamCreation.",
)
@click.option(
    "--ssl-verify/--no-ssl-verify",
    default=None,
    required=False,
    help="Enable/disable SSL certificate verification for API calls.",
)
@click.option(
    "--containers",
    type=click.BOOL,
    help="To disable fetching containers, use False. Defaults to True.",
    default=True,
)
def import_total_cloud(
    regscale_ssp_id: int = None,
    component_id: int = None,
    include_tags: str = None,
    exclude_tags: str = None,
    vulnerability_creation: str = None,
    ssl_verify: bool = None,
    containers: bool = True,
):
    """
    Import Qualys Total Cloud Assets and Vulnerabilities using JSONL scanner implementation.

    This command uses the JSONLScannerIntegration class for improved efficiency and memory management.
    """
    # Determine which ID to use and whether it's a component
    if component_id:
        plan_id = component_id
        is_component = True
        if not validate_regscale_object(component_id, "components"):
            logger.warning("Component #%i is not a valid RegScale Component.", component_id)
            return
    elif regscale_ssp_id:
        plan_id = regscale_ssp_id
        is_component = False
        if not validate_regscale_object(regscale_ssp_id, "securityplans"):
            logger.warning("SSP #%i is not a valid RegScale Security Plan.", regscale_ssp_id)
            return
    else:
        error_and_exit(
            "You must provide either a --regscale_ssp_id or a --component_id to import Qualys Total Cloud data."
        )

    # exclude tags must have include_tags
    if exclude_tags and not include_tags:
        error_and_exit("You must provide --include_tags when using --exclude_tags to import Qualys Total Cloud data.")

    # Ensure vulnerability creation is properly set
    if not vulnerability_creation:
        vulnerability_creation = "IssueCreation"  # Default to IssueCreation for Qualys
        logger.info("No vulnerability creation setting provided, defaulting to IssueCreation for Qualys Total Cloud")

    containers_lst = []
    try:
        # Configure scanner variables and fetch data
        _configure_scanner_variables(vulnerability_creation, ssl_verify)
        response_data = _fetch_qualys_api_data(include_tags, exclude_tags)
        if not response_data:
            return

        if containers:
            # Fetch containers and container findings
            params = _prepare_qualys_params(include_tags, exclude_tags)
            containers_lst = fetch_all_vulnerabilities(filters=params)

        # Initialize and run integration
        integration = _initialize_integration(
            plan_id, response_data, vulnerability_creation, ssl_verify, containers_lst, is_component
        )
        _run_integration_import(integration)

        logger.info("Qualys Total Cloud data imported successfully with JSONL scanner.")
    except Exception:
        error_message = traceback.format_exc()
        logger.error("Error occurred while processing Qualys data with JSONL scanner")
        logger.error(error_message)


def _configure_scanner_variables(vulnerability_creation, ssl_verify):
    """Configure scanner variables with appropriate precedence.

    :param str vulnerability_creation: Vulnerability creation mode from command line
    :param bool ssl_verify: SSL verification setting from command line
    """
    # Configure vulnerability creation mode
    _configure_vulnerability_creation(vulnerability_creation)

    # Configure SSL verification
    _configure_ssl_verification(ssl_verify)


def _configure_vulnerability_creation(vulnerability_creation):
    """Configure vulnerability creation mode with appropriate precedence.

    :param str vulnerability_creation: Vulnerability creation mode from command line
    """
    if vulnerability_creation:
        # Command line option takes precedence
        ScannerVariables.vulnerabilityCreation = vulnerability_creation
        logger.info(f"Setting vulnerability creation mode from command line: {vulnerability_creation}")
    elif hasattr(QualysVariables, "vulnerabilityCreation") and ScannerVariables.vulnerabilityCreation:
        # Use Qualys-specific setting if available
        logger.info(f"Using Qualys-specific vulnerability creation mode: {ScannerVariables.vulnerabilityCreation}")
    else:
        # Fall back to global ScannerVariables
        logger.info(f"Using global vulnerability creation mode: {ScannerVariables.vulnerabilityCreation}")


def _configure_ssl_verification(ssl_verify):
    """Configure SSL verification setting with appropriate precedence.

    :param bool ssl_verify: SSL verification setting from command line
    """
    if ssl_verify is not None:
        # Command line option takes precedence
        ScannerVariables.sslVerify = ssl_verify
        logger.info(f"Setting SSL verification from command line: {ssl_verify}")
    elif hasattr(QualysVariables, "sslVerify") and QualysVariables.sslVerify is not None:
        # Use Qualys-specific setting
        logger.info(f"Using Qualys-specific SSL verification setting: {ScannerVariables.sslVerify}")
    else:
        # Fall back to global ScannerVariables
        logger.info(f"Using global SSL verification setting: {ScannerVariables.sslVerify}")


def _fetch_qualys_api_data(include_tags, exclude_tags):
    """Fetch data from Qualys API.

    :param str include_tags: Tags to include in the query
    :param str exclude_tags: Tags to exclude from the query
    :return: Parsed XML data or None if request failed
    """
    from regscale.integrations.commercial.qualys.qualys_error_handler import QualysErrorHandler

    qualys_url, qualys_api = _get_qualys_api()
    params = _prepare_qualys_params(include_tags, exclude_tags)

    logger.info("Fetching Qualys Total Cloud data with JSONL scanner...")

    try:
        response = qualys_api.get(
            url=urljoin(qualys_url, "/api/2.0/fo/asset/host/vm/detection/"),
            headers=HEADERS,
            params=params,
            verify=ScannerVariables.sslVerify,  # Apply SSL verification setting
        )

        # Use the error handler to validate the response
        is_valid, error_message, parsed_data = QualysErrorHandler.validate_response(response)

        if not is_valid:
            logger.error(f"Qualys API request failed: {error_message}")

            # If we have parsed data, extract detailed error information
            if parsed_data:
                error_details = QualysErrorHandler.extract_error_details(parsed_data)
                QualysErrorHandler.log_error_details(error_details)

                # Check if this is a retryable error
                error_code = error_details.get("error_code")
                if error_code and QualysErrorHandler.should_retry(error_code):
                    retry_after = error_details.get("retry_after", 60)
                    logger.warning(f"This error may be retryable. Consider retrying after {retry_after} seconds.")

                # Check if this is a fatal error that should stop processing
                if error_code and QualysErrorHandler.is_fatal_error(error_code):
                    logger.error("Fatal error encountered. Please check your credentials and permissions.")

            return None

        # Process API response
        logger.info("Total cloud data fetched successfully. Processing with JSONL scanner...")
        return parsed_data

    except Exception as e:
        logger.error(f"Unexpected error during Qualys API request: {e}")
        logger.debug(traceback.format_exc())
        return None


def _initialize_integration(plan_id, response_data, vulnerability_creation, ssl_verify, containers, is_component=False):
    integration_kwargs = {
        "plan_id": plan_id,
        "xml_data": response_data,
        "vulnerability_creation": vulnerability_creation or ScannerVariables.vulnerabilityCreation,
        "ssl_verify": ssl_verify if ssl_verify is not None else ScannerVariables.sslVerify,
        "containers": containers,
        "is_component": is_component,
    }
    if hasattr(ScannerVariables, "threadMaxWorkers"):
        integration_kwargs["max_workers"] = ScannerVariables.threadMaxWorkers
        logger.debug(f"Using thread max workers: {ScannerVariables.threadMaxWorkers}")
    integration = QualysTotalCloudJSONLIntegration(**integration_kwargs)
    return integration


def _run_integration_import(integration):
    """Run the integration import process with progress tracking.

    :param QualysTotalCloudJSONLIntegration integration: Initialized integration object
    """
    assets_iterator, _ = integration.fetch_assets_and_findings()
    logger.info("Syncing assets to RegScale...")

    # Set up progress reporting and import data
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("•"),
        TimeElapsedColumn(),
        console=None,
    ) as progress:
        # Set up progress tasks
        asset_task, finding_task, _, _ = _setup_progress_tracking(integration, progress)

        # Import assets and findings
        _import_assets(integration, assets_iterator, progress, asset_task)
        _import_findings(integration, progress, finding_task)


@click.command(name="import_total_cloud_xml")
@ssp_or_component_id()
@click.option(
    "--xml_file",
    "-f",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    required=True,
    help="Path to Qualys Total Cloud XML file to process.",
)
def import_total_cloud_from_xml(xml_file: str, regscale_ssp_id: int = None, component_id: int = None):
    """
    Import Qualys Total Cloud Assets and Vulnerabilities from an existing XML file using JSONL scanner.

    This command processes an existing XML file instead of making an API call, useful for testing.
    """
    from regscale.integrations.commercial.qualys.qualys_error_handler import QualysErrorHandler

    try:
        logger.info(f"Processing Qualys Total Cloud XML file: {xml_file}")

        # Parse the XML file with error handling
        with open(xml_file, "r") as f:
            xml_content = f.read()

        # Use the error handler to safely parse XML
        success, response_data, error_message = QualysErrorHandler.parse_xml_safely(xml_content)

        if not success:
            logger.error(f"Failed to parse XML file: {error_message}")

            # If we have partial data, try to extract error details
            if response_data:
                error_details = QualysErrorHandler.extract_error_details(response_data)
                QualysErrorHandler.log_error_details(error_details)

            return

        # Check for Qualys-specific errors in the parsed data
        error_details = QualysErrorHandler.extract_error_details(response_data)
        if error_details.get("has_error"):
            logger.error("XML file contains Qualys error response")
            QualysErrorHandler.log_error_details(error_details)
            return

        # Determine which ID to use and whether it's a component
        if component_id:
            plan_id = component_id
            is_component = True
            if not validate_regscale_object(component_id, "components"):
                logger.warning("Component #%i is not a valid RegScale Component.", component_id)
                return
        elif regscale_ssp_id:
            plan_id = regscale_ssp_id
            is_component = False
            if not validate_regscale_object(regscale_ssp_id, "securityplans"):
                logger.warning("SSP #%i is not a valid RegScale Security Plan.", regscale_ssp_id)
                return
        else:
            error_and_exit(
                "You must provide either a --regscale_ssp_id or a --component_id to import Qualys Total Cloud data."
            )

        # Initialize the JSONLScannerIntegration implementation
        integration = QualysTotalCloudJSONLIntegration(
            plan_id=plan_id, xml_data=response_data, file_path=xml_file, is_component=is_component
        )

        # Process data and generate JSONL files
        if not _process_xml_to_jsonl(integration):
            return

        # Count and validate items for progress tracking
        asset_count, finding_count = _count_jsonl_items(integration)
        if asset_count == 0 and finding_count == 0:
            logger.error("No assets or findings found in the processed data")
            return

        # Set up progress tracking and import to RegScale
        _import_to_regscale(integration, asset_count, finding_count)

        logger.info("Qualys Total Cloud XML file imported successfully with JSONL scanner.")
    except Exception:
        error_message = traceback.format_exc()
        logger.error("Error occurred while processing Qualys XML file with JSONL scanner")
        logger.error(error_message)


def _process_xml_to_jsonl(integration):
    """Process XML data and generate JSONL files."""
    try:
        logger.info("Fetching assets and findings...")
        integration.fetch_assets_and_findings()

        # Validate JSONL files
        for file_path, file_type in [(integration.ASSETS_FILE, "Assets"), (integration.FINDINGS_FILE, "Findings")]:
            if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
                logger.error(f"{file_type} file not created or is empty: {file_path}")
                return False

        logger.info("Successfully created JSONL files.")
        logger.info(f"Assets file size: {os.path.getsize(integration.ASSETS_FILE)} bytes")
        logger.info(f"Findings file size: {os.path.getsize(integration.FINDINGS_FILE)} bytes")
        return True
    except Exception as e:
        logger.error(f"Error fetching assets and findings: {str(e)}")
        logger.error(traceback.format_exc())
        return False


def _count_jsonl_items(integration):
    """Count assets and findings in JSONL files."""
    # Count assets
    assets_count = 0
    asset_ids = []
    try:
        assets_iterator = integration._yield_items_from_jsonl(integration.ASSETS_FILE, IntegrationAsset)
        for asset in assets_iterator:
            assets_count += 1
            if asset and hasattr(asset, "identifier"):
                asset_ids.append(asset.identifier)

        logger.debug(f"Asset IDs: {', '.join(asset_ids[:5])}{', ...' if len(asset_ids) > 5 else ''}")
    except Exception as e:
        logger.error(f"Error counting assets: {str(e)}")

    # Count findings
    findings_count = 0
    try:
        findings_iterator = integration._yield_items_from_jsonl(integration.FINDINGS_FILE, IntegrationFinding)
        findings_count = sum(1 for _ in findings_iterator)
    except Exception as e:
        logger.error(f"Error counting findings: {str(e)}")

    logger.info(f"Found {assets_count} assets and {findings_count} findings in JSONL files")
    return assets_count, findings_count


def _create_progress_bar():
    """Create a progress bar that doesn't reset at 100%."""
    from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

    class NonResettingProgress(Progress):
        def update(self, task_id, **fields):
            """Update a task."""
            task = self._tasks[task_id]
            completed_old = task.completed

            # Update the task with the provided fields
            for field_name, value in fields.items():
                if field_name == "completed" and value is True:
                    if task.total is not None:
                        task.completed = task.total
                else:
                    setattr(task, field_name, value)

            # Prevent task from being reset to 0% after reaching 100%
            if completed_old == task.total and task.completed < task.total:
                task.completed = task.total

            self.refresh()

    return NonResettingProgress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("•"),
        TimeElapsedColumn(),
        console=None,
    )


def _track_progress_generator(iterator, progress_bar, task_id, id_attribute=None):
    """Create a generator that tracks progress as items are yielded."""
    processed = 0
    item_ids = []

    for item in iterator:
        processed += 1

        if id_attribute and hasattr(item, id_attribute):
            item_ids.append(getattr(item, id_attribute))

        progress_bar.update(task_id, completed=processed)
        yield item

    # Log debugging information
    item_type = "items"
    if id_attribute == "identifier":
        item_type = "assets"
    elif id_attribute == "external_id":
        item_type = "findings"

    logger.debug(f"Created/updated {processed} {item_type} in RegScale")

    if processed == 0:
        logger.error(f"WARNING: No {item_type} were created/updated in RegScale!")
    elif item_ids:
        logger.debug(f"First 10 {item_type} IDs: {item_ids[:10]}")


def _import_to_regscale(integration, asset_count, finding_count):
    """Import assets and findings to RegScale with progress tracking."""
    progress = _create_progress_bar()

    with progress:
        # Create tasks
        asset_task = progress.add_task(f"[green]Importing {asset_count} assets to RegScale...", total=asset_count)
        finding_task = progress.add_task(
            f"[yellow]Importing {finding_count} findings to RegScale...", visible=False, total=finding_count
        )

        # Import assets
        try:
            assets_iterator = integration._yield_items_from_jsonl(integration.ASSETS_FILE, IntegrationAsset)
            tracked_assets = _track_progress_generator(assets_iterator, progress, asset_task, "identifier")
            assets_imported = integration.update_regscale_assets(tracked_assets)
            logger.info(f"Imported {assets_imported} assets to RegScale")
            # Ensure the progress shows complete
            progress.update(asset_task, completed=asset_count)
        except Exception as e:
            logger.error(f"Error importing assets to RegScale: {str(e)}")
            logger.error(traceback.format_exc())
            # Mark the task as completed even if there was an error
            progress.update(asset_task, completed=asset_count)

        # Import findings
        progress.update(finding_task, visible=True)
        try:
            findings_iterator = integration._yield_items_from_jsonl(integration.FINDINGS_FILE, IntegrationFinding)
            tracked_findings = _track_progress_generator(findings_iterator, progress, finding_task, "external_id")
            findings_imported = integration.update_regscale_findings(tracked_findings)
            logger.info(f"Imported {findings_imported} findings to RegScale")
            # Ensure progress shows complete
            progress.update(finding_task, completed=finding_count)
        except Exception as e:
            logger.error(f"Error importing findings to RegScale: {str(e)}")
            logger.error(traceback.format_exc())
            # Mark as completed even if there was an error
            progress.update(finding_task, completed=finding_count)


@qualys.command(name="export_scans")
@save_output_to()
@click.option(
    "--days",
    type=int,
    default=30,
    help="The number of days to go back for completed scans, default is 30.",
)
@click.option(
    "--export",
    type=click.BOOL,
    help="To disable saving the scans as a .json file, use False. Defaults to True.",
    default=True,
    prompt=False,
    required=False,
)
def export_past_scans(save_output_to: Path, days: int, export: bool = True):
    """Export scans from Qualys Host that were completed
    in the last x days, defaults to last 30 days
    and defaults to save it as a .json file"""
    export_scans(
        save_path=save_output_to,
        days=days,
        export=export,
    )


@qualys.command(name="import_scans")
@FlatFileImporter.common_scanner_options(
    message="File path to the folder containing Qualys .csv or .xlsx files to process to RegScale.",
    prompt="File path for Qualys files",
    import_name="qualys",
)
@click.option(
    "--skip_rows",
    type=click.INT,
    help="The number of rows in the file to skip to get to the column headers, defaults to 129.",
    default=129,
)
def import_scans(
    folder_path: os.PathLike[str],
    regscale_ssp_id: int,
    scan_date: datetime,
    mappings_path: os.PathLike[str],
    disable_mapping: bool,
    skip_rows: int,
    s3_bucket: str,
    s3_prefix: str,
    aws_profile: str,
    upload_file: bool,
):
    """
    Import vulnerability scans from Qualys CSV or Excel (.xlsx) files.

    This command processes Qualys CSV or Excel export files and imports assets and vulnerabilities
    into RegScale. The files must contain specific required headers.

    TROUBLESHOOTING:
    If you encounter "No columns to parse from file" errors, try:
    1. Run 'regscale qualys validate_csv -f <file_path>' first
    2. Adjust the --skip_rows parameter (default: 129)
    3. Check that your file has the required headers

    REQUIRED HEADERS:
    Severity, Title, Exploitability, CVE ID, Solution, DNS, IP,
    QG Host ID, OS, NetBIOS, FQDN

    For detailed format requirements, see the documentation at:
    regscale/integrations/commercial/qualys/QUALYS_CSV_FORMAT.md
    """
    import_qualys_scans(
        folder_path=folder_path,
        regscale_ssp_id=regscale_ssp_id,
        scan_date=scan_date,
        mappings_path=mappings_path,
        disable_mapping=disable_mapping,
        skip_rows=skip_rows,
        s3_bucket=s3_bucket,
        s3_prefix=s3_prefix,
        aws_profile=aws_profile,
        upload_file=upload_file,
    )


def import_qualys_scans(
    folder_path: os.PathLike[str],
    regscale_ssp_id: int,
    scan_date: datetime,
    mappings_path: os.PathLike[str],
    disable_mapping: bool,
    skip_rows: int,
    s3_bucket: str,
    s3_prefix: str,
    aws_profile: str,
    upload_file: Optional[bool] = True,
) -> None:
    """
    Import scans from Qualys

    :param os.PathLike[str] folder_path: File path to the folder containing Qualys .csv or .xlsx files to process to RegScale
    :param int regscale_ssp_id: The RegScale SSP ID
    :param datetime scan_date: The date of the scan
    :param os.PathLike[str] mappings_path: The path to the mappings file
    :param bool disable_mapping: Whether to disable custom mappings
    :param int skip_rows: The number of rows in the file to skip to get to the column headers
    :param str s3_bucket: The S3 bucket to download the files from
    :param str s3_prefix: The S3 prefix to download the files from
    :param str aws_profile: The AWS profile to use for S3 access
    :param Optional[bool] upload_file: Whether to upload the file to RegScale after processing, defaults to True
    :rtype: None
    """
    FlatFileImporter.import_files(
        import_type=Qualys,
        import_name="Qualys",
        file_types=[".csv", ".xlsx"],
        folder_path=folder_path,
        object_id=regscale_ssp_id,
        scan_date=scan_date,
        mappings_path=mappings_path,
        disable_mapping=disable_mapping,
        s3_bucket=s3_bucket,
        s3_prefix=s3_prefix,
        aws_profile=aws_profile,
        upload_file=upload_file,
        skip_rows=skip_rows,
    )


@qualys.command(name="import_policy_scans")
@FlatFileImporter.common_scanner_options(
    message="File path to the folder containing Qualys policy .csv files to process to RegScale.",
    prompt="File path for Qualys files",
    import_name="qualys_policy_scan",
)
@click.option(
    "--skip_rows",
    type=click.INT,
    help="The number of rows in the file to skip to get to the column headers, defaults to 5.",
    default=5,
)
def import_policy_scans(
    folder_path: os.PathLike[str],
    regscale_ssp_id: int,
    scan_date: datetime,
    mappings_path: Path,
    disable_mapping: bool,
    skip_rows: int,
    s3_bucket: str,
    s3_prefix: str,
    aws_profile: str,
    upload_file: bool,
):
    """
    Import Qualys policy scans from a CSV file into a RegScale Security Plan as assets and vulnerabilities.
    """
    process_files_with_importer(
        folder_path=str(folder_path),
        importer_class=QualysPolicyScansImporter,
        regscale_ssp_id=regscale_ssp_id,
        importer_args={
            "plan_id": regscale_ssp_id,
            "name": "QualysPolicyScan",
            "parent_id": regscale_ssp_id,
            "parent_module": "securityplans",
            "scan_date": scan_date,
        },
        mappings_path=str(mappings_path),
        disable_mapping=disable_mapping,
        skip_rows=skip_rows,
        s3_bucket=s3_bucket,
        s3_prefix=s3_prefix,
        aws_profile=aws_profile,
        upload_file=upload_file,
    )


@qualys.command(name="save_results")
@save_output_to()
@click.option(
    "--scan_id",
    type=click.STRING,
    help="Qualys scan reference ID to get results, defaults to all.",
    default="all",
)
def save_results(save_output_to: Path, scan_id: str):
    """Get scan results from Qualys using a scan ID or all scans and save them to a .json file."""
    save_scan_results_by_id(save_path=save_output_to, scan_id=scan_id)


def _resolve_plan_and_component(regscale_ssp_id: int = None, component_id: int = None):
    """
    Utility to resolve plan_id and is_component from regscale_ssp_id and component_id.
    Returns (plan_id, is_component)
    """
    if (regscale_ssp_id is None and component_id is None) or (regscale_ssp_id and component_id):
        error_and_exit("You must provide either --regscale_ssp_id or --component_id, but not both.")
    is_component = component_id is not None
    plan_id = component_id if is_component else regscale_ssp_id
    return plan_id, is_component


@qualys.command(name="sync_qualys")
@ssp_or_component_id(
    ssp_kwargs={"help": "The ID number from RegScale of the System Security Plan."},
    component_kwargs={"help": "The ID number from RegScale of the Component record to sync to."},
)
@click.option(
    "--create_issue",
    type=click.BOOL,
    required=False,
    help="Create Issue in RegScale from vulnerabilities in Qualys.",
    default=False,
)
@click.option(
    "--asset_group_id",
    type=click.INT,
    help="Filter assets from Qualys with an asset group ID.",
    default=None,
    cls=NotRequiredIf,
    not_required_if=["asset_group_name"],
)
@click.option(
    "--asset_group_name",
    type=click.STRING,
    help="Filter assets from Qualys with an asset group name.",
    default=None,
    cls=NotRequiredIf,
    not_required_if=["asset_group_id"],
)
def sync_qualys(
    regscale_ssp_id: int = None,
    component_id: int = None,
    create_issue: bool = False,
    asset_group_id: int = None,
    asset_group_name: str = None,
):
    """
    Query Qualys and sync assets & their associated vulnerabilities to a Security Plan or Component in RegScale.
    """
    plan_id, is_component = _resolve_plan_and_component(regscale_ssp_id, component_id)
    sync_qualys_to_regscale(
        plan_id=plan_id,
        create_issue=create_issue,
        asset_group_id=asset_group_id,
        asset_group_name=asset_group_name,
        is_component=is_component,
    )


@qualys.command(name="get_asset_groups")
@save_output_to()
def get_asset_groups(save_output_to: Path):
    """
    Get all asset groups from Qualys via API and save them to a .json file.
    """
    # see if user has enterprise license
    check_license()

    date = get_current_datetime("%Y%m%d")
    check_file_path(save_output_to)
    asset_groups = get_asset_groups_from_qualys()
    save_data_to(
        file=Path(f"{save_output_to}/qualys_asset_groups_{date}.json"),
        data=asset_groups,
    )


@qualys.command(name="import_container_scans")
@FlatFileImporter.common_scanner_options(
    message="File path to the folder containing container .csv files to process to RegScale.",
    prompt="File path for Qualys files",
    import_name="qualys_container_scan",
)
@click.option(
    "--skip_rows",
    type=click.INT,
    help="The number of rows in the file to skip to get to the column headers, defaults to 5.",
    default=5,
)
def import_container_scans(
    folder_path: os.PathLike[str],
    regscale_ssp_id: int,
    scan_date: datetime,
    mappings_path: Path,
    disable_mapping: bool,
    s3_bucket: str,
    s3_prefix: str,
    aws_profile: str,
    upload_file: bool,
    skip_rows: int,
):
    """
    Import Qualys container scans from a CSV file into a RegScale Security Plan as assets and vulnerabilities.
    """
    process_files_with_importer(
        folder_path=str(folder_path),
        importer_class=QualysContainerScansImporter,
        regscale_ssp_id=regscale_ssp_id,
        importer_args={
            "plan_id": regscale_ssp_id,
            "name": "QualysContainerScan",
            "parent_id": regscale_ssp_id,
            "parent_module": "securityplans",
            "scan_date": scan_date,
        },
        mappings_path=str(mappings_path),
        disable_mapping=disable_mapping,
        skip_rows=skip_rows,
        s3_bucket=s3_bucket,
        s3_prefix=s3_prefix,
        aws_profile=aws_profile,
        upload_file=upload_file,
    )


@qualys.command(name="import_was_scans")
@FlatFileImporter.common_scanner_options(
    message="File path to the folder containing was .csv files to process to RegScale.",
    prompt="File path for Qualys files",
    import_name="qualys_was_scan",
)
@click.option(
    "--skip_rows",
    type=click.INT,
    help="The number of rows in the file to skip to get to the column headers, defaults to 5.",
    default=5,
)
def import_was_scans(
    folder_path: os.PathLike[str],
    regscale_ssp_id: int,
    scan_date: datetime,
    mappings_path: Path,
    disable_mapping: bool,
    skip_rows: int,
    s3_bucket: str,
    s3_prefix: str,
    aws_profile: str,
    upload_file: bool,
):
    """
    Import Qualys was scans from a CSV file into a RegScale Security Plan as assets and vulnerabilities.
    """
    process_files_with_importer(
        folder_path=str(folder_path),
        importer_class=QualysWasScansImporter,
        regscale_ssp_id=regscale_ssp_id,
        importer_args={
            "plan_id": regscale_ssp_id,
            "name": "QualysWASScan",
            "parent_id": regscale_ssp_id,
            "parent_module": "securityplans",
            "scan_date": scan_date,
        },
        mappings_path=str(mappings_path),
        disable_mapping=disable_mapping,
        skip_rows=skip_rows,
        s3_bucket=s3_bucket,
        s3_prefix=s3_prefix,
        aws_profile=aws_profile,
        upload_file=upload_file,
    )


def process_files_with_importer(
    regscale_ssp_id: int,
    folder_path: str,
    importer_class,
    importer_args: dict,
    s3_bucket: str,
    s3_prefix: str,
    aws_profile: str,
    mappings_path: str = None,
    disable_mapping: bool = False,
    skip_rows: int = 0,
    scan_date: datetime = None,
    upload_file: Optional[bool] = True,
):
    """
    Process files in a folder using a specified importer class.

    :param int regscale_ssp_id: ID of the RegScale Security Plan to import the data into.
    :param str folder_path: Path to the folder containing files.
    :param Any importer_class: The importer class to instantiate for processing.
    :param dict importer_args: Additional arguments to pass to the importer class.
    :param str s3_bucket: S3 bucket to download the files from.
    :param str s3_prefix: S3 prefix to download the files from.
    :param str aws_profile: AWS profile to use for S3 access.
    :param str mappings_path: Path to mapping configurations.
    :param bool disable_mapping: Flag to disable mappings.
    :param int skip_rows: Number of rows to skip in files.
    :param scan_date: Date of the scan. Defaults to current datetime if not provided.
    :param Optional[bool] upload_file: Whether to upload the file to RegScale after processing, defaults to True.
    """
    import csv

    from openpyxl import Workbook

    if s3_bucket:
        download_from_s3(s3_bucket, s3_prefix, folder_path, aws_profile)

    files_lst = list(Path(folder_path).glob("*.csv"))

    # If no files are found in the folder, return a warning
    if len(files_lst) == 0:
        logger.warning("No Qualys files found in the folder path provided.")
        return

    if not scan_date:
        scan_date = datetime.now(timezone.utc)

    for file in files_lst:
        try:
            original_file_name = str(file)
            xlsx_file = (
                f"{file.name}.xlsx" if not file.name.endswith(".csv") else str(file.name).replace(".csv", ".xlsx")
            )

            # Convert CSV to XLSX
            wb = Workbook()
            ws = wb.active
            with open(file, "r") as f:
                for row in csv.reader(f):
                    ws.append(row)

            # Save the Excel file
            full_file_path = Path(f"{file.parent}/{xlsx_file}")
            wb.save(full_file_path)

            # Initialize and use the importer
            importer = importer_class(
                plan_id=regscale_ssp_id,
                name=importer_args.get("name", "QualysFileScan"),
                file_path=str(full_file_path),
                parent_id=regscale_ssp_id,
                parent_module=importer_args.get("parent_module", "securityplans"),
                scan_date=scan_date,
                mappings_path=mappings_path,
                disable_mapping=disable_mapping,
                skip_rows=skip_rows,
                upload_file=upload_file,
            )
            importer.clean_up(file_path=original_file_name)
        except Exception as e:
            error_message = traceback.format_exc()
            logger.error(f"Failed to process file {file}: {error_message}\n{e}")
            continue


def export_scans(
    save_path: Path,
    days: int = 30,
    export: bool = True,
) -> None:
    """
    Function to export scans from Qualys that were completed in the last x days, defaults to 30

    :param Path save_path: Path to save the scans to as a .json file
    :param int days: # of days of completed scans to export, defaults to 30 days
    :param bool export: Whether to save the scan data as a .json, defaults to True
    :rtype: None
    """
    # see if user has enterprise license
    check_license()
    date = get_current_datetime("%Y%m%d")
    results = get_detailed_scans(days)
    if export:
        check_file_path(save_path)
        save_data_to(
            file=Path(f"{save_path.name}/qualys_scans_{date}.json"),
            data=results,
        )
    else:
        pprint.pprint(results, indent=4)


def save_scan_results_by_id(save_path: Path, scan_id: str) -> None:
    """
    Function to save the queries from Qualys using an ID a .json file

    :param Path save_path: Path to save the scan results to as a .json file
    :param str scan_id: Qualys scan ID to get the results for
    :rtype: None
    """
    # see if user has enterprise license
    check_license()

    check_file_path(save_path)
    with job_progress:
        if scan_id.lower() == "all":
            # get all the scan results from Qualys
            scans = get_scans_summary("all")

            # add task to job progress to let user know # of scans to fetch
            task1 = job_progress.add_task(
                f"[#f8b737]Getting scan results for {len(scans['SCAN'])} scan(s)...",
                total=len(scans["SCAN"]),
            )
            # get the scan results from Qualys
            scan_data = get_scan_results(scans, task1)
        else:
            task1 = job_progress.add_task(f"[#f8b737]Getting scan results for {scan_id}...", total=1)
            # get the scan result for the provided scan id
            scan_data = get_scan_results(scan_id, task1)
    # save the scan_data as the provided file_path
    save_data_to(file=save_path, data=scan_data)


def sync_qualys_to_regscale(
    plan_id: int,
    create_issue: bool = False,
    asset_group_id: int = None,
    asset_group_name: str = None,
    is_component: bool = False,
) -> None:
    """
    Sync Qualys assets and vulnerabilities to a security plan or component in RegScale

    :param int plan_id: ID # of the SSP or Component in RegScale
    :param bool create_issue: Flag whether to create an issue in RegScale from Qualys vulnerabilities, defaults to False
    :param int asset_group_id: Optional filter for assets in Qualys with an asset group ID, defaults to None
    :param str asset_group_name: Optional filter for assets in Qualys with an asset group name, defaults to None
    :param bool is_component: Whether the sync is for a component (True) or security plan (False)
    :rtype: None
    """
    # see if user has enterprise license
    check_license()

    # check if the user provided an asset group id or name
    if asset_group_id:
        sync_qualys_assets_and_vulns(
            ssp_id=plan_id,
            create_issue=create_issue,
            asset_group_filter=asset_group_name,
            is_component=is_component,
        )
    elif asset_group_name:
        sync_qualys_assets_and_vulns(
            ssp_id=plan_id,
            create_issue=create_issue,
            asset_group_filter=asset_group_id,
            is_component=is_component,
        )
    else:
        sync_qualys_assets_and_vulns(ssp_id=plan_id, create_issue=create_issue, is_component=is_component)


def get_scan_results(scans: Any, task: TaskID) -> dict:
    """
    Function to retrieve scan results from Qualys using provided scan list and returns a dictionary

    :param Any scans: list of scans to retrieve from Qualys
    :param TaskID task: task to update in the progress object
    :return: dictionary of detailed Qualys scans
    :rtype: dict
    """
    qualys_url, QUALYS_API = _get_qualys_api()

    scan_data = {}
    # check number of scans requested
    if isinstance(scans, str):
        # only one scan was requested, set up variable for the for loop
        scans = {"SCAN": [{"REF": scans}]}
    for scan in scans["SCAN"]:
        # set up data and parameters for the scans query
        try:
            # try and get the scan id ref #
            scan_id = scan["REF"]
            # set the parameters for the Qualys API call
            params = {
                "action": "fetch",
                "scan_ref": scan_id,
                "mode": "extended",
                "output_format": "json_extended",
            }
            # get the scan data via API
            res = QUALYS_API.get(
                url=urljoin(qualys_url, "/api/2.0/fo/scan/"),
                headers=HEADERS,
                params=params,
            )
            # convert response to json
            if res.status_code == 200:
                try:
                    res_data = res.json()
                    scan_data[scan_id] = res_data
                except JSONDecodeError:
                    error_and_exit("Unable to convert response to JSON.")
            else:
                error_and_exit(f"Received unexpected response from Qualys API: {res.status_code}: {res.text}")
        except KeyError:
            # unable to get the scan id ref #
            continue
        job_progress.update(task, advance=1)
    return scan_data


def get_detailed_scans(days: int) -> list:
    """
    function to get the list of all scans from Qualys using QUALYS_API

    :param int days: # of days before today to filter scans
    :return: list of results from Qualys API
    :rtype: list
    """
    qualys_url, QUALYS_API = _get_qualys_api()

    today = datetime.now()
    scan_date = today - timedelta(days=days)

    # set up data and parameters for the scans query
    params = {
        "action": "list",
        "scan_date_since": scan_date.strftime("%Y-%m-%d"),
        "output_format": "json",
    }
    params2 = {
        "action": "list",
        "scan_datetime_since": scan_date.strftime("%Y-%m-%dT%H:%I:%S%ZZ"),
    }
    res = QUALYS_API.get(
        url=urljoin(qualys_url, "/api/2.0/fo/scan/summary/"),
        headers=HEADERS,
        params=params,
    )
    response = QUALYS_API.get(
        url=urljoin(qualys_url, "/api/2.0/fo/scan/vm/summary/"),
        headers=HEADERS,
        params=params2,
    )
    # convert response to json
    res_data = res.json()
    try:
        response_data = xmltodict.parse(response.text)["SCAN_SUMMARY_OUTPUT"]["RESPONSE"]["SCAN_SUMMARY_LIST"][
            "SCAN_SUMMARY"
        ]
        if len(res_data) < 1:
            res_data = response_data
        else:
            res_data.extend(response_data)
    except JSONDecodeError:
        logger.error("ERROR: Unable to convert to JSON.")
    return res_data


def _get_config():
    """
    Get the Qualys configuration

    :return: Qualys configuration
    :rtype: dict
    """
    app = check_license()
    config = app.config
    return config


def _get_qualys_api():
    """
    Get the Qualys API session

    :return: Qualys API session
    :rtype: Session
    """
    config = _get_config()

    # set the auth for the QUALYS_API session
    QUALYS_API.auth = (config.get("qualysUserName"), config.get("qualysPassword"))
    QUALYS_API.verify = config.get("sslVerify", True)
    qualys_url = config.get("qualysUrl")
    return qualys_url, QUALYS_API


def get_scans_summary(scan_choice: str) -> dict:
    """
    Get all scans from Qualys Host

    :param str scan_choice: The type of scan to retrieve from Qualys API
    :return: Detailed summary of scans from Qualys API as a dictionary
    :rtype: dict
    """
    qualys_url, QUALYS_API = _get_qualys_api()
    urls = []

    # set up variables for function
    scan_data = {}
    responses = []
    scan_url = urljoin(qualys_url, "/api/2.0/fo/scan/")

    # set up parameters for the scans query
    params = {"action": "list"}
    # check what scan list was requested and set urls list accordingly
    if scan_choice.lower() == "all":
        urls = [scan_url, scan_url + "compliance", scan_url + "scap"]
    elif scan_choice.lower() == "vm":
        urls = [scan_url]
    elif scan_choice.lower() in ["compliance", "scap"]:
        urls = [scan_url + scan_choice.lower()]
    # get the list of vm scans
    for url in urls:
        # get the scan data
        response = QUALYS_API.get(url=url, headers=HEADERS, params=params)
        # store response into a list
        responses.append(response)
    # check the responses received for data
    for response in responses:
        # see if response was successful
        if response.status_code == 200:
            # parse the data
            data = xmltodict.parse(response.text)["SCAN_LIST_OUTPUT"]["RESPONSE"]
            # see if the scan has any data
            try:
                # add the data to the scan_data dictionary
                scan_data.update(data["SCAN_LIST"])
            except KeyError:
                # no data found, continue the for loop
                continue
    return scan_data


def get_scan_details(days: int) -> list:
    """
    Retrieve completed scans from last x days from Qualys Host

    :param int days: # of days before today to filter scans
    :return: Detailed summary of scans from Qualys API as a dictionary
    :rtype: list
    """
    qualys_url, QUALYS_API = _get_qualys_api()
    # get since date for API call
    since_date = datetime.now() - timedelta(days=days)
    # set up data and parameters for the scans query
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Requested-With": "RegScale CLI",
    }
    params = {
        "action": "list",
        "scan_date_since": since_date.strftime("%Y-%m-%d"),
        "output_format": "json",
    }
    params2 = {
        "action": "list",
        "scan_datetime_since": since_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    res = QUALYS_API.get(
        url=urljoin(qualys_url, "/api/2.0/fo/scan/summary/"),
        headers=headers,
        params=params,
    )
    response = QUALYS_API.get(
        url=urljoin(qualys_url, "/api/2.0/fo/scan/vm/summary/"),
        headers=headers,
        params=params2,
    )
    # convert response to json
    res_data = res.json()
    try:
        response_data = xmltodict.parse(response.text)["SCAN_SUMMARY_OUTPUT"]["RESPONSE"]["SCAN_SUMMARY_LIST"][
            "SCAN_SUMMARY"
        ]
        if len(res_data) < 1:
            res_data = response_data
        else:
            res_data.update(response_data)
    except JSONDecodeError as ex:
        error_and_exit(f"Unable to convert to JSON.\n{ex}")
    except KeyError:
        error_and_exit(f"No data found.\n{response.text}")
    return res_data


def sync_qualys_assets_and_vulns(
    ssp_id: int,
    create_issue: bool,
    asset_group_filter: Optional[Union[int, str]] = None,
    is_component: bool = False,
) -> None:
    """
    Function to query Qualys and sync assets & associated vulnerabilities to RegScale (Security Plan or Component)

    :param int ssp_id: RegScale System Security Plan or Component ID
    :param bool create_issue: Flag to create an issue in RegScale for each vulnerability from Qualys
    :param Optional[Union[int, str]] asset_group_filter: Filter the Qualys assets by an asset group ID or name, if any
    :param bool is_component: Whether the sync is for a component (True) or security plan (False)
    :rtype: None
    """
    config = _get_config()
    parent_module = "components" if is_component else "securityplans"

    # Get the assets from RegScale with the provided parent ID
    logger.info(f"Getting assets from RegScale for {parent_module} #{ssp_id}...")
    reg_assets = Asset.get_all_by_search(search=Search(parentID=ssp_id, module=parent_module))
    logger.info(
        "Located %s asset(s) associated with %s #%s in RegScale.",
        len(reg_assets),
        parent_module,
        ssp_id,
    )
    logger.debug(reg_assets)

    if qualys_assets := get_qualys_assets_and_scan_results(asset_group_filter=asset_group_filter):
        logger.info("Received %s assets from Qualys.", len(qualys_assets))
        logger.debug(qualys_assets)
    else:
        error_and_exit("No assets found in Qualys.")
    sync_assets(
        qualys_assets=qualys_assets,
        reg_assets=reg_assets,
        ssp_id=ssp_id,
        config=config,
        is_component=is_component,
    )
    if create_issue:
        # Get vulnerabilities from Qualys for the Qualys assets
        logger.info("Getting vulnerabilities for %s asset(s) from Qualys...", len(qualys_assets))
        qualys_assets_and_issues, total_vuln_count = get_issue_data_for_assets(qualys_assets)
        logger.info("Received %s vulnerabilities from Qualys.", total_vuln_count)
        logger.debug(qualys_assets_and_issues)
        sync_issues(
            ssp_id=ssp_id,
            qualys_assets_and_issues=qualys_assets_and_issues,
            is_component=is_component,
        )


def sync_assets(
    qualys_assets: list[dict], reg_assets: list[Asset], ssp_id: int, config: dict, is_component: bool = False
) -> None:
    """
    Function to sync Qualys assets to RegScale (Security Plan or Component)

    :param list[dict] qualys_assets: List of Qualys assets
    :param list[Asset] reg_assets: List of RegScale assets
    :param int ssp_id: RegScale System Security Plan or Component ID
    :param dict config: Configuration dictionary
    :param bool is_component: Whether the sync is for a component (True) or security plan (False)
    :rtype: None
    """
    parent_module = "components" if is_component else "securityplans"
    update_assets = []

    for qualys_asset in qualys_assets:
        processed_asset = _process_single_qualys_asset(qualys_asset, reg_assets, ssp_id, parent_module)
        if processed_asset:
            update_assets.append(processed_asset)

    update_and_insert_assets(
        qualys_assets=qualys_assets,
        reg_assets=reg_assets,
        ssp_id=ssp_id,
        config=config,
        update_assets=update_assets,
        is_component=is_component,
    )


def _process_single_qualys_asset(
    qualys_asset: dict, reg_assets: list[Asset], ssp_id: int, parent_module: str
) -> Optional[Asset]:
    """
    Process a single Qualys asset and return the updated RegScale asset if found.

    :param dict qualys_asset: Single Qualys asset dictionary
    :param list[Asset] reg_assets: List of RegScale assets
    :param int ssp_id: RegScale System Security Plan or Component ID
    :param str parent_module: Parent module name
    :return: Updated RegScale asset or None if not found
    :rtype: Optional[Asset]
    """
    logger.debug("qualys_asset: %s", qualys_asset)

    if not isinstance(qualys_asset, dict):
        logger.error("Expected dict, got %s: %s", type(qualys_asset), qualys_asset)
        return None

    lookup_assets = lookup_asset(reg_assets, qualys_asset["ASSET_ID"])
    if not lookup_assets:
        return None

    return _update_regscale_asset(lookup_assets[0], qualys_asset, ssp_id, parent_module)


def _update_regscale_asset(asset: Asset, qualys_asset: dict, ssp_id: int, parent_module: str) -> Optional[Asset]:
    """
    Update a RegScale asset with Qualys asset data.

    :param Asset asset: RegScale asset to update
    :param dict qualys_asset: Qualys asset data
    :param int ssp_id: RegScale System Security Plan or Component ID
    :param str parent_module: Parent module name
    :return: Updated asset or None if update failed
    :rtype: Optional[Asset]
    """
    try:
        asset.parentId = ssp_id
        asset.parentModule = parent_module
        asset.otherTrackingNumber = qualys_asset["ID"]
        asset.ipAddress = qualys_asset["IP"]
        asset.qualysId = qualys_asset["ASSET_ID"]

        assert asset.id
        return asset
    except AssertionError as aex:
        logger.error("Asset does not have an id, unable to update!\n%s", aex)
        return None


def update_and_insert_assets(
    qualys_assets: list[dict],
    reg_assets: list[Asset],
    ssp_id: int,
    config: dict,
    update_assets: list[Asset],
    is_component: bool = False,
) -> None:
    """
    Function to update and insert Qualys assets into RegScale (Security Plan or Component)

    :param list[dict] qualys_assets: List of Qualys assets as dictionaries
    :param list[Asset] reg_assets: List of RegScale assets
    :param int ssp_id: RegScale System Security Plan or Component ID
    :param dict config: RegScale CLI Configuration dictionary
    :param list[Asset] update_assets: List of assets to update in RegScale
    :param bool is_component: Whether the sync is for a component (True) or security plan (False)
    :rtype: None
    """
    parent_module = "components" if is_component else "securityplans"

    # Handle asset insertion
    insert_assets = _prepare_assets_for_insertion(qualys_assets, reg_assets, ssp_id, parent_module, config)
    if insert_assets:
        _create_assets_in_batch(insert_assets)

    # Handle asset updates
    if update_assets:
        _update_assets_in_batch(update_assets)


def _prepare_assets_for_insertion(
    qualys_assets: list[dict], reg_assets: list[Asset], ssp_id: int, parent_module: str, config: dict
) -> list[Asset]:
    """
    Prepare new assets for insertion into RegScale.

    :param list[dict] qualys_assets: List of Qualys assets
    :param list[Asset] reg_assets: List of RegScale assets
    :param int ssp_id: RegScale System Security Plan or Component ID
    :param str parent_module: Parent module name
    :param dict config: Configuration dictionary
    :return: List of assets to insert
    :rtype: list[Asset]
    """
    assets_to_be_inserted = [
        qualys_asset
        for qualys_asset in qualys_assets
        if qualys_asset["ASSET_ID"] not in [asset["ASSET_ID"] for asset in inner_join(reg_assets, qualys_assets)]
    ]

    insert_assets = []
    for qualys_asset in assets_to_be_inserted:
        r_asset = _create_regscale_asset_from_qualys(qualys_asset, ssp_id, parent_module, config)
        # avoid duplication
        if r_asset.qualysId not in {v["qualysId"] for v in insert_assets}:
            insert_assets.append(r_asset)

    return insert_assets


def _create_regscale_asset_from_qualys(qualys_asset: dict, ssp_id: int, parent_module: str, config: dict) -> Asset:
    """
    Create a RegScale asset from Qualys asset data.

    :param dict qualys_asset: Qualys asset data
    :param int ssp_id: RegScale System Security Plan or Component ID
    :param str parent_module: Parent module name
    :param dict config: Configuration dictionary
    :return: New RegScale asset
    :rtype: Asset
    """
    return Asset(
        name=f'Qualys Asset #{qualys_asset["ASSET_ID"]} IP: {qualys_asset["IP"]}',
        otherTrackingNumber=qualys_asset["ID"],
        parentId=ssp_id,
        parentModule=parent_module,
        ipAddress=qualys_asset["IP"],
        assetOwnerId=config["userId"],
        assetType="Other",
        assetCategory=regscale_models.AssetCategory.Hardware,
        status="Off-Network",
        qualysId=qualys_asset["ASSET_ID"],
    )


def _create_assets_in_batch(insert_assets: list[Asset]) -> None:
    """
    Create assets in batch and handle any errors.

    :param list[Asset] insert_assets: List of assets to create
    :rtype: None
    """
    try:
        created_assets = Asset.batch_create(insert_assets, job_progress)
        logger.info(
            "RegScale Asset(s) successfully created: %i/%i",
            len(created_assets),
            len(insert_assets),
        )
    except requests.exceptions.RequestException as rex:
        logger.error("Unable to create Qualys Assets in RegScale\n%s", rex)


def _update_assets_in_batch(update_assets: list[Asset]) -> None:
    """
    Update assets in batch and handle any errors.

    :param list[Asset] update_assets: List of assets to update
    :rtype: None
    """
    try:
        updated_assets = Asset.batch_update(update_assets, job_progress)
        logger.info(
            "RegScale Asset(s) successfully updated: %i/%i",
            len(updated_assets),
            len(update_assets),
        )
    except requests.RequestException as rex:
        logger.error("Unable to Update Qualys Assets to RegScale\n%s", rex)


def sync_issues(ssp_id: int, qualys_assets_and_issues: list[dict], is_component: bool = False) -> None:
    """
    Function to sync Qualys issues to RegScale (Security Plan or Component)

    :param int ssp_id: RegScale System Security Plan or Component ID
    :param list[dict] qualys_assets_and_issues: List of Qualys assets and their issues
    :param bool is_component: Whether the sync is for a component (True) or security plan (False)
    :rtype: None
    """
    parent_module = "components" if is_component else "securityplans"
    update_issues = []
    insert_issues = []
    vuln_count = 0
    ssp_assets = Asset.get_all_by_parent(parent_id=ssp_id, parent_module=parent_module)
    for asset in qualys_assets_and_issues:
        # Create issues in RegScale from Qualys vulnerabilities
        regscale_issue_updates, regscale_new_issues = create_regscale_issue_from_vuln(
            regscale_ssp_id=ssp_id,
            qualys_asset=asset,
            regscale_assets=ssp_assets,
            vulns=asset["ISSUES"],
            is_component=is_component,
        )
        update_issues.extend(regscale_issue_updates)
        insert_issues.extend(regscale_new_issues)
        vuln_count += len(asset.get("ISSUES", []))
    if insert_issues:
        deduped_vulns = combine_duplicate_qualys_vulns(insert_issues)
        logger.info(
            "Creating %i new issue(s) in RegScale, condensed from %i Qualys vulnerabilities.",
            len(deduped_vulns),
            vuln_count,
        )
        created_issues = Issue.batch_create(deduped_vulns, job_progress)
        logger.info(
            "RegScale Issue(s) successfully created: %i/%i",
            len(created_issues),
            len(deduped_vulns),
        )
    if update_issues:
        deduped_vulns = combine_duplicate_qualys_vulns(update_issues)
        logger.info(
            "Updating %i existing issue(s) in RegScale, condensed from %i Qualys vulnerabilities.",
            len(deduped_vulns),
            vuln_count,
        )
        updated_issues = Issue.batch_update(deduped_vulns, job_progress)
        logger.info("RegScale Issue(s) successfully updated: %i/%i", len(updated_issues), len(deduped_vulns))


def combine_duplicate_qualys_vulns(qualys_vulns: list[Issue]) -> list:
    """
    Function to combine duplicate Qualys vulnerabilities

    :param list[Issue] qualys_vulns: List of Qualys vulnerabilities as RegScale issues
    :return: List of Qualys vulnerabilities with duplicates combined
    :rtype: list
    """
    with job_progress:
        logger.info("Combining duplicate Qualys vulnerabilities found across multiple assets...")
        deduping_task = job_progress.add_task(
            f"Combining {len(qualys_vulns)} Qualys vulnerabilities...",
            total=len(qualys_vulns),
        )
        combined_vulns: dict[str, Issue] = {}
        for vuln in qualys_vulns:
            if vuln.qualysId in combined_vulns:
                if current_identifier := combined_vulns[vuln.qualysId].assetIdentifier:
                    combined_vulns[vuln.qualysId].assetIdentifier = update_asset_identifier(
                        vuln.assetIdentifier, current_identifier
                    )
                else:
                    combined_vulns[vuln.qualysId].assetIdentifier = vuln.assetIdentifier
            else:
                combined_vulns[vuln.qualysId] = vuln
            job_progress.update(deduping_task, advance=1)
    return list(combined_vulns.values())


def get_qualys_assets_and_scan_results(
    url: Optional[str] = None, asset_group_filter: Optional[Union[int, str]] = None
) -> list:
    """
    function to gather all assets from Qualys API host along with their scan results

    :param Optional[str] url: URL to get the assets from, defaults to None, used for pagination
    :param Optional[Union[int, str]] asset_group_filter: Qualys asset group ID or name to filter by, if provided
    :return: list of dictionaries containing asset data
    :rtype: list
    """
    qualys_url, QUALYS_API = _get_qualys_api()
    # set url
    if not url:
        url = urljoin(qualys_url, "api/2.0/fo/asset/host/vm/detection?action=list&show_asset_id=1")

    # check if an asset group filter was provided and append it to the url
    if asset_group_filter:
        if isinstance(asset_group_filter, str):
            # Get the asset group ID from Qualys
            url += f"&ag_titles={asset_group_filter}"
            logger.info("Getting assets from Qualys by group name: %s...", asset_group_filter)
        else:
            url += f"&ag_ids={asset_group_filter}"
            logger.info(
                "Getting assets from from Qualys by group ID: #%s...",
                asset_group_filter,
            )
    else:
        # Get all assets from Qualys
        logger.info("Getting all assets from Qualys...")

    # get the data via Qualys API host
    response = QUALYS_API.get(url=url, headers=HEADERS)
    res_data = xmltodict.parse(response.text)

    try:
        # parse the xml data from response.text and convert it to a dictionary
        # and try to extract the data from the parsed XML dictionary
        asset_data = res_data["HOST_LIST_VM_DETECTION_OUTPUT"]["RESPONSE"]["HOST_LIST"]["HOST"]
        # Always make asset_data a list
        if isinstance(asset_data, dict):
            asset_data = [asset_data]
        elif not isinstance(asset_data, list):
            asset_data = []
        # check if we need to paginate the asset data
        if "WARNING" in res_data["HOST_LIST_VM_DETECTION_OUTPUT"]["RESPONSE"]:
            logger.warning("Not all assets were fetched, fetching more assets from Qualys...")
            asset_data.extend(
                get_qualys_assets_and_scan_results(
                    url=res_data["HOST_LIST_VM_DETECTION_OUTPUT"]["RESPONSE"]["WARNING"]["URL"],
                    asset_group_filter=asset_group_filter,
                )
            )
    except KeyError:
        # if there is a KeyError set the dictionary to nothing
        asset_data = []
    # return the asset_data variable
    return asset_data


def get_issue_data_for_assets(asset_list: list) -> Tuple[list[dict], int]:
    """
    Function to get issue data from Qualys via API for assets in Qualys

    :param list asset_list: Assets and their scan results from Qualys
    :return:  Updated asset list of Qualys assets and their associated vulnerabilities, total number of vulnerabilities
    :rtype: Tuple[list[dict], int]
    """
    config = _get_config()
    with job_progress:
        issues = {}
        for asset in asset_list:
            # check if the asset has any vulnerabilities
            if vulns := asset.get("DETECTION_LIST", {}).get("DETECTION", {}):
                asset_vulns = {}
                analyzing_vulns = job_progress.add_task(
                    f"Analyzing {len(vulns)} vulnerabilities for asset #{asset['ASSET_ID']} from Qualys..."
                )
                # iterate through the vulnerabilities & verify they have a confirmed status
                for vuln in vulns:
                    if vuln["TYPE"] == "Confirmed":
                        issues[vuln["QID"]] = vuln
                        asset_vulns[vuln["QID"]] = vuln
                    job_progress.update(analyzing_vulns, advance=1)
                job_progress.update(analyzing_vulns, completed=len(vulns))
                # add the issues to the asset's dictionary
                asset["ISSUES"] = asset_vulns
                job_progress.remove_task(analyzing_vulns)
    asset_list = fetch_vulns_from_qualys(issue_ids=list(issues.keys()), asset_list=asset_list, config=config)
    return asset_list, len(issues)


def parse_and_map_vuln_data(xml_data: str) -> dict:
    """
    Function to parse Qualys vulnerability data from XML and map it to a dictionary using the Qualys ID as the key

    :param str xml_data: XML data from Qualys API
    :return: Dictionary of Qualys vulnerability data
    :rtype: dict
    """
    issue_data = (
        xmltodict.parse(xml_data)
        .get("KNOWLEDGE_BASE_VULN_LIST_OUTPUT", {})
        .get("RESPONSE", {})
        .get("VULN_LIST", {})
        .get("VULN", {})
    )
    # change the key for the fetched issues to be the qualys ID
    return {issue["QID"]: issue for issue in issue_data}


def fetch_vulns_from_qualys(issue_ids: list[str], asset_list: list[dict], config: dict, retries: int = 0) -> list[dict]:
    """
    Function to fetch vulnerability data from Qualys for a list of issues and assets

    :param list[str] issue_ids: List of Qualys issue IDs to fetch data for
    :param list[dict] asset_list: List of Qualys assets to update with vulnerability data
    :param dict config: CLI Configuration dictionary
    :param int retries: Number of retries for fetching data, defaults to 0
    :return: Updated asset list with vulnerability data
    :rtype: list[dict]
    """
    logger.info(
        f"Getting vulnerability data for {len(issue_ids)} issue(s) from Qualys for {len(asset_list)} asset(s)..."
    )
    base_url = urljoin(config["qualysUrl"], "api/2.0/fo/knowledge_base/vuln?action=list&details=All")
    if len(issue_ids) > 100:
        logger.warning(
            "Too many issues to fetch from Qualys. Downloading the Qualys database to prevent rate limits..."
        )
        # since there are a lot of vulnerabilities, download the database and reference it locally
        chunk_size_calc = 20 * 1024
        with QUALYS_API.post(
            url=base_url,
            headers=HEADERS,
            stream=True,
        ) as response:
            check_file_path("artifacts")
            with open("./artifacts/qualys_vuln_db.xml", "wb") as f:
                for chunk in response.iter_content(chunk_size=chunk_size_calc):
                    f.write(chunk)
        with open("./artifacts/qualys_vuln_db.xml", "r") as f:
            qualys_issue_data = parse_and_map_vuln_data(f.read())
    else:
        response = QUALYS_API.get(
            url=f"{base_url}&ids={','.join(issue_ids)}",
            headers=HEADERS,
        )
        if response.ok:
            qualys_issue_data = parse_and_map_vuln_data(response.text)
            logger.info("Received vulnerability data for %s issues from Qualys.", len(qualys_issue_data))
        elif response.status_code == 409:
            response_data = xmltodict.parse(response.text)["SIMPLE_RETURN"]["RESPONSE"]
            logger.warning(
                "Received timeout error from Qualys API: %s. Waiting %s seconds...",
                response_data["TEXT"],
                response_data["ITEM_LIST"]["ITEM"]["VALUE"],
            )
            sleep(int(response_data["ITEM_LIST"]["ITEM"]["VALUE"]))
            if retries < 3:
                fetch_vulns_from_qualys(issue_ids, asset_list, config, retries + 1)
            else:
                error_and_exit(
                    "Unable to fetch vulnerability data from Qualys after 3 attempts. Please try again later."
                )
        else:
            error_and_exit(
                f"Received unexpected response from Qualys: {response.status_code}: {response.text}: {response.reason}"
            )
    return map_issue_data_to_assets(asset_list, qualys_issue_data)


def map_issue_data_to_assets(assets: list[dict], qualys_issue_data: dict) -> list[dict]:
    """
    Function to map Qualys issue data to Qualys assets

    :param list[dict] assets: List of Qualys assets to map issue data to
    :param dict qualys_issue_data: List of Qualys issues to map to assets
    :return: Updated asset list with Qualys issue data
    :rtype: list[dict]
    """
    for asset in assets:
        if issues := asset.get("ISSUES"):
            mapping_vulns = job_progress.add_task(
                f"Mapping {len(issues)} vulnerabilities to Asset #{asset['ASSET_ID']} from Qualys...",
                total=len(issues),
            )
            for issue in issues:
                if issue in qualys_issue_data:
                    issues[issue]["ISSUE_DATA"] = qualys_issue_data[issue]
                job_progress.update(mapping_vulns, advance=1)
            job_progress.remove_task(mapping_vulns)
    return assets


def lookup_asset(asset_list: list, asset_id: str = None) -> list[Asset]:
    """
    Look up assets in the asset list by Qualys asset ID or return all unique assets.

    Args:
        asset_list (list): List of assets from RegScale.
        asset_id (str, optional): Qualys asset ID to search for. Defaults to None.

    Returns:
        list[Asset]: List of unique Asset objects matching the asset_id, or all unique assets if asset_id is None.
    """
    if asset_id:
        return list({asset for asset in asset_list if getattr(asset, "qualysId", None) == asset_id})
    return list(set(asset_list)) or []


def map_qualys_severity_to_regscale(severity: int) -> tuple[str, str]:
    """
    Map Qualys vulnerability severity to RegScale Issue severity

    :param int severity: Qualys vulnerability severity
    :return: RegScale Issue severity and key for init.yaml
    :rtype: tuple[str, str]
    """
    if severity <= 2:
        return "III - Low - Other Weakness", "low"
    if severity == 3:
        return "II - Moderate - Reportable Condition", "moderate"
    if severity > 3:
        return "I - High - Significant Deficiency", "high"
    return "IV - Not Assigned", "low"


def create_regscale_issue_from_vuln(
    regscale_ssp_id: int, qualys_asset: dict, regscale_assets: list[Asset], vulns: dict, is_component: bool = False
) -> Tuple[list[Issue], list[Issue]]:
    """
    Sync Qualys vulnerabilities to RegScale issues (Security Plan or Component).

    :param int regscale_ssp_id: RegScale SSP or Component ID
    :param dict qualys_asset: Qualys asset as a dictionary
    :param list[Asset] regscale_assets: list of RegScale assets
    :param dict vulns: dictionary of Qualys vulnerabilities associated with the provided asset
    :param bool is_component: Whether the sync is for a component (True) or security plan (False)
    :return: list of RegScale issues to update, and a list of issues to be created
    :rtype: Tuple[list[Issue], list[Issue]]
    """
    config = _get_config()
    default_status = config["issues"]["qualys"]["status"]
    regscale_issues = []
    parent_module = "components" if is_component else "securityplans"
    regscale_existing_issues = Issue.get_all_by_parent(parent_id=regscale_ssp_id, parent_module=parent_module)
    for vuln in vulns.values():
        asset_identifier = None
        severity, key = map_qualys_severity_to_regscale(int(vuln["SEVERITY"]))

        default_due_delta = config["issues"]["qualys"][key]
        logger.debug("Processing vulnerability# %s", vuln["QID"])
        fmt = "%Y-%m-%dT%H:%M:%SZ"
        due_date = datetime.strptime(vuln["LAST_FOUND_DATETIME"], fmt) + timedelta(days=default_due_delta)
        regscale_asset = [asset for asset in regscale_assets if asset.qualysId == qualys_asset["ASSET_ID"]]
        if "DNS" not in qualys_asset.keys() or "IP" not in qualys_asset.keys():
            if regscale_asset:
                asset_identifier = f"RegScale Asset #{regscale_asset[0].id}: {regscale_asset[0].name}"
        else:
            if regscale_asset:
                asset_identifier = (
                    f'RegScale Asset #{regscale_asset[0].id}: {regscale_asset[0].name} Qualys DNS: "'
                    f'{qualys_asset["DNS"]} - IP: {qualys_asset["IP"]}'
                )
            else:
                asset_identifier = f'DNS: {qualys_asset["DNS"]} - IP: {qualys_asset["IP"]}'
        issue = Issue(
            title=vuln["ISSUE_DATA"]["TITLE"],
            description=vuln["ISSUE_DATA"]["CONSEQUENCE"] + "</br>" + vuln["ISSUE_DATA"]["DIAGNOSIS"],
            issueOwnerId=config["userId"],
            status=default_status,
            severityLevel=severity,
            qualysId=vuln["QID"],
            dueDate=due_date.strftime(fmt),
            identification="Vulnerability Assessment",
            parentId=regscale_ssp_id,
            parentModule=parent_module,
            recommendedActions=vuln["ISSUE_DATA"]["SOLUTION"],
            assetIdentifier=asset_identifier,
        )
        regscale_issues.append(issue)
    regscale_new_issues, regscale_update_issues = determine_issue_update_or_create(
        regscale_issues, regscale_existing_issues
    )
    return regscale_update_issues, regscale_new_issues


def update_asset_identifier(new_identifier: Optional[str], current_identifier: Optional[str]) -> Optional[str]:
    """
    Function to update the asset identifier for a RegScale issue

    :param Optional[str] new_identifier: New asset identifier to add
    :param Optional[str] current_identifier: Current asset identifier
    :return: Updated asset identifier
    :rtype: str
    """
    if not current_identifier and new_identifier:
        return new_identifier
    if current_identifier and new_identifier:
        if new_identifier not in current_identifier:
            return f"{current_identifier}<br>{new_identifier}"
        if new_identifier in current_identifier:
            return current_identifier
        if new_identifier == current_identifier:
            return current_identifier


def determine_issue_update_or_create(
    qualys_issues: list[Issue], regscale_issues: list[Issue]
) -> Tuple[list[Issue], list[Issue]]:
    """
    Function to determine if Qualys issues needs to be updated or created in RegScale

    :param list[Issue] qualys_issues: List of Qualys issues
    :param list[Issue] regscale_issues: List of existing RegScale issues
    :return: List of new issues and list of issues to update
    :rtype: Tuple[list[Issue], list[Issue]]
    """
    new_issues = []
    update_issues = []
    for issue in qualys_issues:
        if issue.qualysId in [iss.qualysId for iss in regscale_issues]:
            update_issue = [iss for iss in regscale_issues if iss.qualysId == issue.qualysId][0]
            # Check if we need to concatenate the asset identifier
            update_issue.assetIdentifier = update_asset_identifier(issue.assetIdentifier, update_issue.assetIdentifier)
            update_issues.append(update_issue)
        else:
            new_issues.append(issue)
    return new_issues, update_issues


def inner_join(reg_list: list, qualys_list: list) -> list:
    """
    Function to compare assets from Qualys and assets from RegScale

    :param list reg_list: list of assets from RegScale
    :param list qualys_list: list of assets from Qualys
    :return: list of assets that are in both RegScale and Qualys
    :rtype: list
    """

    set1 = {getattr(asset, "qualysId", None) for asset in reg_list}
    data = []
    try:
        data = [list_qualys for list_qualys in qualys_list if getattr(list_qualys, "ASSET_ID", None) in set1]
    except KeyError as ex:
        logger.error(ex)
    return data


def get_asset_groups_from_qualys() -> list:
    """
    Get all asset groups from Qualys via API

    :return: list of assets from Qualys
    :rtype: list
    """
    asset_groups = []

    qualys_url, QUALYS_API = _get_qualys_api()
    response = QUALYS_API.get(url=urljoin(qualys_url, "api/2.0/fo/asset/group?action=list"), headers=HEADERS)
    if response.ok:
        logger.debug(response.text)
        try:
            asset_groups = xmltodict.parse(response.text)["ASSET_GROUP_LIST_OUTPUT"]["RESPONSE"]["ASSET_GROUP_LIST"][
                "ASSET_GROUP"
            ]
        except KeyError:
            logger.debug(response.text)
            error_and_exit(
                f"Unable to retrieve asset groups from Qualys.\nReceived: #{response.status_code}: {response.text}"
            )
    return asset_groups


def _get_required_headers() -> list[str]:
    """
    Get the list of required headers for Qualys CSV validation.

    :return: List of required header names
    :rtype: list[str]
    """
    return [
        "Severity",
        "Title",
        "Exploitability",
        "CVE ID",
        "Solution",
        "DNS",
        "IP",
        "QG Host ID",
        "OS",
        "NetBIOS",
        "FQDN",
    ]


def _read_csv_file(file_path: str, skip_rows: int, console):
    """
    Read and validate CSV file structure.

    :param str file_path: Path to the CSV file
    :param int skip_rows: Number of rows to skip
    :param console: Rich console instance for output
    :return: DataFrame if successful, None if failed
    :rtype: Optional[pd.DataFrame]
    """
    import pandas as pd

    console.print(f"[blue]Reading CSV file: {file_path}[/blue]")
    console.print(f"[blue]Skipping first {skip_rows} rows[/blue]")

    try:
        if skip_rows > 0:
            df = pd.read_csv(file_path, skiprows=skip_rows - 1, on_bad_lines="warn")
        else:
            df = pd.read_csv(file_path, on_bad_lines="warn")

        if df.empty:
            console.print("[red]❌ File is empty after skipping rows[/red]")
            return None

        if len(df.columns) == 0:
            console.print("[red]❌ No columns found in the file[/red]")
            return None

        console.print("[green]✅ Successfully read CSV file[/green]")
        console.print(f"[green]✅ Found {len(df.columns)} columns and {len(df)} rows[/green]")
        return df

    except pd.errors.EmptyDataError:
        console.print("[red]❌ File is empty or contains no parseable data[/red]")
        console.print("[yellow]💡 Try adjusting the skip_rows parameter[/yellow]")
        return None
    except pd.errors.ParserError as e:
        console.print(f"[red]❌ Error parsing CSV file: {e}[/red]")
        console.print("[yellow]💡 Check if the file is properly formatted CSV[/yellow]")
        return None


def _display_columns_table(df, console):
    """
    Display a table showing all columns found in the CSV.

    :param df: DataFrame containing the CSV data
    :param console: Rich console instance for output
    """
    from rich.table import Table

    table = Table(title="Columns Found in CSV")
    table.add_column("Index", style="cyan")
    table.add_column("Column Name", style="magenta")

    for i, col in enumerate(df.columns):
        table.add_row(str(i), str(col))

    console.print(table)


def _check_required_headers(df, console):
    """
    Check for required headers and display results.

    :param df: DataFrame containing the CSV data
    :param console: Rich console instance for output
    :return: Tuple of (missing_headers, found_headers)
    :rtype: tuple[list[str], list[str]]
    """
    required_headers = _get_required_headers()

    console.print("\n[blue]Checking for required headers:[/blue]")
    missing_headers = []
    found_headers = []

    for header in required_headers:
        if header in df.columns:
            found_headers.append(header)
            console.print(f"[green]✅ {header}[/green]")
        else:
            missing_headers.append(header)
            console.print(f"[red]❌ {header}[/red]")

    return missing_headers, found_headers


def _display_header_validation_summary(missing_headers, console):
    """
    Display summary of header validation results.

    :param list[str] missing_headers: List of missing required headers
    :param console: Rich console instance for output
    """
    if missing_headers:
        console.print(f"\n[yellow]⚠️  Missing {len(missing_headers)} required headers[/yellow]")
        console.print("[yellow]You may need to adjust the skip_rows parameter or check your file format[/yellow]")
    else:
        console.print("\n[green]🎉 All required headers found! File should import successfully.[/green]")


def _display_sample_data(df, console):
    """
    Display sample data from the CSV file.

    :param df: DataFrame containing the CSV data
    :param console: Rich console instance for output
    """
    from rich.table import Table

    if len(df) == 0:
        return

    console.print("\n[blue]Sample data (first 3 rows):[/blue]")
    sample_table = Table()

    # Add columns (limit to first 5 for readability)
    display_cols = list(df.columns)[:5]
    for col in display_cols:
        sample_table.add_column(str(col)[:20], style="cyan")

    # Add rows
    for i in range(min(3, len(df))):
        row_data = [str(df.iloc[i][col])[:30] for col in display_cols]
        sample_table.add_row(*row_data)

    console.print(sample_table)

    if len(df.columns) > 5:
        console.print(f"[dim]... and {len(df.columns) - 5} more columns[/dim]")


@qualys.command(name="validate_csv")
@click.option(
    "--file_path",
    "-f",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    required=True,
    help="Path to the Qualys CSV file to validate.",
    prompt="Enter the path to the Qualys CSV file",
)
@click.option(
    "--skip_rows",
    type=click.INT,
    help="The number of rows in the file to skip to get to the column headers, defaults to 129.",
    default=129,
)
def validate_csv(file_path: str, skip_rows: int):
    """
    Validate a Qualys CSV file format and headers before importing.

    This command helps troubleshoot CSV file issues by checking:
    - File readability
    - Proper column headers after skipping rows
    - Required headers presence
    """
    from rich.console import Console

    console = Console()

    try:
        # Read and validate CSV file
        df = _read_csv_file(file_path, skip_rows, console)
        if df is None:
            return

        # Display columns found
        _display_columns_table(df, console)

        # Check required headers
        missing_headers, _ = _check_required_headers(df, console)

        # Display validation summary
        _display_header_validation_summary(missing_headers, console)

        # Show sample data
        _display_sample_data(df, console)

    except Exception as e:
        console.print(f"[red]❌ Unexpected error: {e}[/red]")


__all__ = [
    "QualysTotalCloudJSONLIntegration",
    "import_total_cloud",
    "import_total_cloud_from_xml",
    "save_results",
    "sync_qualys",
    "get_asset_groups",
    "import_container_scans",
    "import_was_scans",
    "import_policy_scans",
]

# Register commands with the qualys group
qualys.add_command(import_total_cloud)
qualys.add_command(import_total_cloud_from_xml)
qualys.add_command(export_past_scans)
qualys.add_command(import_scans)
qualys.add_command(import_policy_scans)
qualys.add_command(save_results)
qualys.add_command(sync_qualys)
qualys.add_command(get_asset_groups)
qualys.add_command(import_container_scans)
qualys.add_command(import_was_scans)
