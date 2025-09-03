#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tenable commands for the RegScale CLI.

This module provides Click command definitions for interacting with Tenable.io and Tenable SC.
"""
import json
import logging
import os
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

import click
from pathlib import Path
from requests.exceptions import RequestException
from rich.console import Console
from rich.progress import track

from regscale.core.app.utils.app_utils import (
    check_license,
    check_file_path,
    get_current_datetime,
    save_data_to,
)
from regscale.integrations.commercial.nessus.nessus_utils import get_cpe_file
from regscale.integrations.commercial.nessus.scanner import NessusIntegration
from regscale.integrations.commercial.tenablev2.authenticate import gen_tsc, gen_tio
from regscale.integrations.commercial.tenablev2.jsonl_scanner import TenableSCJsonlScanner
from regscale.integrations.commercial.tenablev2.sc_scanner import SCIntegration
from regscale.integrations.commercial.tenablev2.variables import TenableVariables
from regscale.models import regscale_id, regscale_ssp_id
from regscale.models.app_models.click import file_types, hidden_file_path, save_output_to, ssp_or_component_id
from regscale.models.regscale_models import SecurityPlan

logger = logging.getLogger("regscale")
console = Console()
artifacts_dir = "./artifacts"
REGSCALE_INC = "RegScale, Inc."
REGSCALE_CLI = "RegScale CLI"
FULLY_IMPLEMENTED = "Fully Implemented"
NOT_IMPLEMENTED = "Not Implemented"
IN_REMEDIATION = "In Remediation"


# Define a helper function for gen_client to replace the original one
def gen_client():
    """
    Generate the appropriate Tenable client based on configuration.

    :return: Either a TenableIO or TenableSC client
    """
    return gen_tsc()  # Default to TenableSC for now


@click.group(name="tenable", help="Tenable commands.")
def tenable():
    """Tenable commands."""
    pass


@tenable.group(name="sc")
def sc():
    """Tenable SC commands."""
    pass


@tenable.group(name="io")
def io():
    """Tenable.io commands."""
    pass


@tenable.group(help="Import Nessus scans and assets to RegScale.")
def nessus():
    """Operations for Nessus scanner files."""
    pass


def validate_tags(ctx: click.Context, param: click.Option, value: str) -> List[Tuple[str, str]]:
    """
    Validate the tuple elements.

    :param click.Context ctx: Click context
    :param click.Option param: Click option
    :param str value: A string value to parse and validate
    :return: Tuple of validated values
    :rtype: List[Tuple[str,str]]
    :raise ValueError: If the value is not in the correct format
    """
    if not value:
        return []

    tuple_list = []
    for item in value.split(","):
        parts = [part for part in item.strip().split(":") if part]
        if len(parts) != 2:
            raise ValueError(f"""Invalid format: "{item}". Expected 'key:value'""")
        tuple_list.append((parts[0], parts[1]))

    return tuple_list


@io.command(name="info")
def io_info():
    """Display information about the configured Tenable.io instance."""
    console.print("[bold]Tenable.io Configuration Information[/bold]")

    try:
        client = gen_tio()

        # Get scanner information
        scanner_info = client.scanners.details()

        # Get user information
        user_info = client.session.details()

        # Display information
        console.print(f"[bold]URL:[/bold] {TenableVariables.tenableUrl}")
        console.print(f"[bold]User:[/bold] {user_info.get('username', 'Unknown')}")
        console.print(f"[bold]Username:[/bold] {user_info.get('email', 'Unknown')}")
        console.print(f"[bold]Scanner Count:[/bold] {len(scanner_info)}")

        # Display scanner information
        if scanner_info:
            console.print("\n[bold]Scanner Information:[/bold]")
            for scanner in scanner_info:
                console.print(f"  [bold]Name:[/bold] {scanner.get('name', 'Unknown')}")
                console.print(f"  [bold]Status:[/bold] {scanner.get('status', 'Unknown')}")
                console.print("")

    except Exception as e:
        logger.error(f"Error getting Tenable.io information: {e}", exc_info=True)
        console.print("[bold red]Error connecting to Tenable.io. Please check your configuration.[/bold red]")


@io.command(name="sync_assets")
@regscale_ssp_id(help="RegScale will create and update assets as children of this security plan.")
@click.option(
    "--tags",
    type=str,
    help="Filter assets by tags (format: 'key:value,key2:value2').",
    callback=validate_tags,
    required=False,
)
def io_sync_assets(regscale_ssp_id: int, tags: List[Tuple[str, str]] = None):
    """Sync assets from Tenable.io to RegScale."""
    console.print("[bold]Starting Tenable.io asset synchronization...[/bold]")

    try:
        from regscale.integrations.commercial.tenablev2.scanner import TenableIntegration

        integration = TenableIntegration(plan_id=regscale_ssp_id, tags=tags)
        integration.sync_assets(plan_id=regscale_ssp_id)

        console.print("[bold green]Tenable.io asset synchronization complete.[/bold green]")
    except Exception as e:
        logger.error(f"Error syncing assets from Tenable.io: {e}", exc_info=True)


@io.command(name="sync_findings")
@regscale_ssp_id(help="RegScale will create findings as children of this security plan.")
@click.option(
    "--tags",
    type=str,
    help="Filter assets by tags (format: 'key:value,key2:value2').",
    callback=validate_tags,
    required=False,
)
@click.option(
    "--severity",
    type=click.Choice(["critical", "high", "medium", "low", "all"], case_sensitive=False),
    default="all",
    help="Filter findings by severity.",
    required=False,
)
@click.option(
    "--scan_date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="The scan date of the findings.",
    required=False,
)
def io_sync_findings(
    regscale_ssp_id: int, tags: List[Tuple[str, str]] = None, severity: str = "all", scan_date: datetime = None
):
    """Sync vulnerability findings from Tenable.io to RegScale."""
    console.print("[bold]Starting Tenable.io finding synchronization...[/bold]")

    try:
        from regscale.integrations.commercial.tenablev2.scanner import TenableIntegration

        integration = TenableIntegration(plan_id=regscale_ssp_id, tags=tags, scan_date=scan_date)
        integration.sync_findings(plan_id=regscale_ssp_id, severity=severity)

        console.print("[bold green]Tenable.io finding synchronization complete.[/bold green]")
    except Exception as e:
        logger.error(f"Error syncing findings from Tenable.io: {e}", exc_info=True)


@io.command(name="export_assets")
@save_output_to()
@file_types([".json", ".csv", ".xlsx"])
@click.option(
    "--tags",
    type=str,
    help="Filter assets by tags (format: 'key:value,key2:value2').",
    callback=validate_tags,
    required=False,
)
def export_io_assets(save_output_to: Path, file_type: str, tags: List[Tuple[str, str]] = None):
    """Export assets from Tenable.io to a .json, .csv or .xlsx file."""
    console.print("[bold]Exporting Tenable.io assets...[/bold]")

    try:
        client = gen_tio()

        # Create artifacts directory if not exists
        Path(artifacts_dir).mkdir(exist_ok=True, parents=True)
        current_datetime = datetime.now().strftime("%Y%m%d%H")
        temp_file = Path(artifacts_dir) / Path(f"tenable_assets_{current_datetime}.json")

        # Fetch assets
        logger.info("Fetching Tenable.io assets...")
        assets = []
        assets_iterator = client.exports.assets(tags=tags) if tags else client.exports.assets()
        i = 0

        with open(temp_file, "w") as f:
            for i, asset in enumerate(assets_iterator, 1):
                f.write(json.dumps(asset) + "\n")
                assets.append(asset)
                if i % 100 == 0:
                    logger.info(f"Fetched {i} assets")

        logger.info(f"Total assets fetched: {i}")

        # Set the output file name
        file_name = f"tenable_io_assets_{get_current_datetime('%m%d%Y')}"
        output_file = Path(f"{save_output_to}/{file_name}{file_type}")

        # Save the data to the selected file format
        save_data_to(
            file=output_file,
            data=assets,
        )

        console.print(f"[bold green]Tenable.io assets exported to {output_file}[/bold green]")
    except Exception as e:
        logger.error(f"Error exporting assets from Tenable.io: {e}", exc_info=True)


@io.command(name="export_findings")
@save_output_to()
@file_types([".json", ".csv", ".xlsx"])
@click.option(
    "--severity",
    type=click.Choice(["critical", "high", "medium", "low", "all"], case_sensitive=False),
    default="all",
    help="Filter findings by severity.",
    required=False,
)
@click.option(
    "--days",
    type=click.INT,
    default=30,
    help="Number of days to look back for vulnerabilities (default: 30).",
    required=False,
)
def export_io_findings(save_output_to: Path, file_type: str, severity: str = "all", days: int = 30):
    """Export vulnerability findings from Tenable.io to a .json, .csv or .xlsx file."""
    console.print("[bold]Exporting Tenable.io vulnerability findings...[/bold]")

    try:
        client = gen_tio()

        # Create artifacts directory if not exists
        Path(artifacts_dir).mkdir(exist_ok=True, parents=True)
        current_datetime = datetime.now().strftime("%Y%m%d%H")
        temp_file = Path(artifacts_dir) / Path(f"tenable_findings_{current_datetime}.json")

        # Calculate lookback time
        lookback_time = int((datetime.now() - timedelta(days=days)).timestamp())

        # Set severity filter
        severity_filter = None
        if severity != "all":
            severity_map = {"critical": "4", "high": "3", "medium": "2", "low": "1"}
            severity_filter = severity_map.get(severity.lower())

        # Fetch vulnerabilities
        logger.info("Fetching Tenable.io vulnerability findings...")
        vulns = []

        vuln_iterator = client.exports.vulnerabilities(last_found=lookback_time, severity=severity_filter)

        i = 0
        with open(temp_file, "w") as f:
            for i, vuln in enumerate(vuln_iterator, 1):
                f.write(json.dumps(vuln) + "\n")
                vulns.append(vuln)
                if i % 100 == 0:
                    logger.info(f"Fetched {i} findings")

        logger.info(f"Total findings fetched: {i}")

        # Set the output file name
        file_name = f"tenable_io_findings_{get_current_datetime('%m%d%Y')}"
        output_file = Path(f"{save_output_to}/{file_name}{file_type}")

        # Save the data to the selected file format
        save_data_to(
            file=output_file,
            data=vulns,
        )

        console.print(f"[bold green]Tenable.io findings exported to {output_file}[/bold green]")
    except Exception as e:
        logger.error(f"Error exporting findings from Tenable.io: {e}", exc_info=True)


@nessus.command(name="import_nessus")
@click.option(
    "--folder_path",
    prompt="Enter the folder path of the Nessus files to process",
    help="RegScale will load the Nessus Scans",
    type=click.Path(exists=True),
)
@click.option(
    "--scan_date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="The scan date of the file.",
    required=False,
)
@regscale_ssp_id()
def import_nessus(folder_path: click.Path, regscale_ssp_id: int, scan_date: datetime = None):
    """Import Nessus scans, vulnerabilities and assets to RegScale."""
    from regscale.validation.record import validate_regscale_object

    if not validate_regscale_object(regscale_ssp_id, "securityplans"):
        logger.warning("SSP #%i is not a valid RegScale Security Plan.", regscale_ssp_id)
        return

    console.print("[bold]Starting Nessus import...[/bold]")
    NessusIntegration.sync_assets(plan_id=regscale_ssp_id, path=folder_path)
    NessusIntegration.sync_findings(
        plan_id=regscale_ssp_id, path=folder_path, enable_finding_date_update=True, scan_date=scan_date
    )
    console.print("[bold green]Nessus import complete.[/bold green]")


@nessus.command(name="update_cpe_dictionary")
def update_cpe_dictionary():
    """
    Manually update the CPE 2.2 dictionary from NIST.
    """
    console.print("[bold]Updating CPE dictionary...[/bold]")
    get_cpe_file(download=True)
    console.print("[bold green]CPE dictionary update complete.[/bold green]")


@sc.command(name="export_scans")
@save_output_to()
@file_types([".json", ".csv", ".xlsx"])
def export_scans(save_output_to: Path, file_type: str):
    """Export scans from Tenable Host to a .json, .csv or .xlsx file."""
    console.print("[bold]Exporting Tenable SC scans...[/bold]")

    # get the scan results
    results = get_usable_scan_list()

    # check if file path exists
    check_file_path(save_output_to)

    # set the file name
    file_name = f"tenable_scans_{get_current_datetime('%m%d%Y')}"

    # save the data as the selected file by the user
    save_data_to(
        file=Path(f"{save_output_to}/{file_name}{file_type}"),
        data=results,
    )

    console.print(f"[bold green]Tenable SC scans exported to {save_output_to}/{file_name}{file_type}[/bold green]")


def get_usable_scan_list() -> list:
    """
    Get usable scans from Tenable Host.

    :return: List of scans from Tenable
    :rtype: list
    """
    results = []
    try:
        client = gen_client()
        results = client.scans.list()["usable"]
    except Exception as ex:
        logger.error(f"Error getting scan list: {ex}")
    return results


def get_detailed_scans(scan_list: list = None) -> list:
    """
    Generate list of detailed scans.

    Warning: this action could take a long time to complete.

    :param list scan_list: List of scans from Tenable, defaults to None
    :raise SystemExit: If there is an error with the request
    :return: Detailed list of Tenable scans
    :rtype: list
    """
    client = gen_client()
    detailed_scans = []
    for scan in track(scan_list, description="Fetching detailed scans..."):
        try:
            det = client.scans.details(id=scan["id"])
            detailed_scans.append(det)
        except RequestException as ex:
            raise SystemExit(ex) from ex

    return detailed_scans


@sc.command(name="save_queries")
@save_output_to()
@file_types([".json", ".csv", ".xlsx"])
def save_queries(save_output_to: Path, file_type: str):
    """Get a list of query definitions and save them as a .json, .csv or .xlsx file."""
    console.print("[bold]Exporting Tenable SC queries...[/bold]")

    # get the queries from Tenable
    query_list = get_queries()

    # check if file path exists
    check_file_path(save_output_to)

    # set the file name
    file_name = f"tenable_queries_{get_current_datetime('%m%d%Y')}"

    # save the data as a file
    save_data_to(
        file=Path(f"{save_output_to}{os.sep}{file_name}{file_type}"),
        data=query_list,
    )

    console.print(
        f"[bold green]Tenable SC queries exported to {save_output_to}{os.sep}{file_name}{file_type}[/bold green]"
    )


def get_queries() -> list:
    """
    Get list of query definitions from Tenable SC.

    :return: List of queries from Tenable
    :rtype: list
    """
    tsc = gen_tsc()
    return tsc.queries.list()


@sc.command(name="query_vuln")
@click.option(
    "--query_id",
    type=click.INT,
    help="Tenable query ID to retrieve via API",
    prompt="Enter Tenable query ID",
    required=True,
)
@ssp_or_component_id()
@click.option(
    "--scan_date",
    "-sd",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="The scan date of the file.",
    required=False,
)
def query_vuln(query_id: int, regscale_ssp_id: int, component_id: int, scan_date: datetime = None):
    """Query Tenable SC vulnerabilities and sync assets to RegScale."""
    try:
        # Validate license
        check_license()

        console.print("[bold]Starting Tenable SC vulnerability query...[/bold]")

        # Use the SCIntegration class method to fetch vulnerabilities by query ID
        if component_id:
            sc_integration = SCIntegration(plan_id=component_id, scan_date=scan_date, is_component=True)
        elif regscale_ssp_id:
            sc_integration = SCIntegration(plan_id=regscale_ssp_id, scan_date=scan_date)
        else:
            raise click.UsageError(
                "You must provide either a --regscale_ssp_id or a --component_id to query Tenable vulnerabilities."
            )

        sc_integration.fetch_vulns_query(query_id=query_id)

        console.print("[bold green]Tenable SC vulnerability query complete.[/bold green]")
    except Exception as e:
        logger.error(f"Error querying Tenable SC vulnerabilities: {str(e)}", exc_info=True)
        console.print(f"[bold red]Error querying Tenable SC vulnerabilities: {str(e)}[/bold red]")


@sc.command(name="list_tags")
def sc_tags():
    """List the tags available in Tenable SC."""
    list_tags()


def list_tags() -> None:
    """
    List the tags from Tenable SC.
    """
    tags = get_tags()
    for tag in tags:
        console.print(f"[bold]{tag['id']}[/bold]: {tag['name']} ({tag['description']})")


def get_tags() -> list:
    """
    Get the list of tags from Tenable SC.

    :return: List of tags
    :rtype: list
    """
    try:
        tsc = gen_tsc()
        return tsc.tags.list()["response"] if "response" in tsc.tags.list() else []
    except Exception as ex:
        logger.error(f"Error getting tags: {ex}")
        return []


@sc.command(name="sync_jsonl")
@regscale_ssp_id()
@click.option(
    "--query_id",
    type=click.INT,
    help="Tenable query ID to retrieve via API. Either query_id or file_path must be provided.",
    required=False,
)
@click.option(
    "--scan_date",
    "-sd",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="The scan date of the file.",
    required=False,
)
@click.option(
    "--file_path",
    type=click.Path(exists=True),
    help="Path to existing Tenable SC data files to process instead of downloading from API. Either query_id or file_path must be provided.",
    required=False,
)
@click.option(
    "--batch_size",
    type=click.INT,
    help="Number of items to process in each batch for large datasets.",
    default=1000,
    show_default=True,
    required=False,
)
@click.option(
    "--optimize-memory",
    is_flag=True,
    help="Enable memory optimization to reduce RAM usage.",
    default=True,
    show_default=True,
)
@click.option(
    "--mapping_file",
    type=click.Path(exists=True),
    help="Optional custom mapping file for transformer-based processing.",
    required=False,
)
@click.option(
    "--skip-validation",
    is_flag=True,
    help="Skip RegScale object validation (use for development environments)",
    default=True,
)
@click.option(
    "--force-download",
    is_flag=True,
    help="Force download of fresh data from Tenable SC, ignoring any existing files.",
    default=False,
)
def sc_sync_jsonl(
    regscale_ssp_id: int,
    query_id: int = None,
    scan_date: datetime = None,
    file_path: str = None,
    batch_size: int = 1000,
    optimize_memory: bool = True,
    mapping_file: str = None,
    skip_validation: bool = False,
    force_download: bool = False,
):
    """
    Sync Tenable SC query results to RegScale using the JSONL implementation.

    This command uses the JSONLScannerIntegration to process Tenable SC data,
    which provides better performance and memory efficiency for large datasets.

    The implementation includes efficient batch processing and optional
    transformer-based mapping of complex data fields.

    Vulnerabilities are fetched from Tenable SC using the specified query ID,
    or existing data files can be processed from the specified file path.

    Note: Either query_id or file_path must be provided.
    """
    # Validate security plan (if not skipping validation)
    if not skip_validation:
        ssp = SecurityPlan.get_object(object_id=regscale_ssp_id)
        if not ssp:
            console.print(f"[bold red]Error:[/bold red] No security plan with ID {regscale_ssp_id} exists.")
            return
    else:
        console.print("[yellow]Skipping RegScale validation for development mode[/yellow]")

    # Validate that either query_id or file_path is provided
    if not query_id and not file_path:
        console.print("[bold red]Error:[/bold red] Either --query_id or --file_path must be provided.")
        return

    console.print("[bold]Starting Tenable SC sync with JSONL Scanner...[/bold]")

    # Add a helpful explanation about the implementation
    console.print("[yellow]This command uses efficient batch processing for optimal performance.[/yellow]")

    try:
        # Create the integration
        scanner = TenableSCJsonlScanner(
            plan_id=regscale_ssp_id,
            query_id=query_id,
            file_path=file_path,
            scan_date=scan_date.strftime("%Y-%m-%d") if scan_date else None,
            batch_size=batch_size,
            optimize_memory=optimize_memory,
            force_download=force_download,
        )

        # Run the synchronization
        if mapping_file:
            # If mapping file provided, use transformer-based processing
            console.print("[yellow]Using custom mapping file for transformer-based processing.[/yellow]")
            scanner.sync_with_transformer(mapping_file=mapping_file)
        else:
            # If query_id is provided but no file_path, the scanner will download data
            if query_id and not file_path:
                console.print(f"[yellow]Downloading data from Tenable SC using query ID: {query_id}[/yellow]")
                # Find or download method will be called inside sync_assets_and_findings
                scanner.sync_assets_and_findings()
            else:
                # Use the provided file_path for synchronization
                scanner.sync_assets_and_findings()

        console.print("[bold green]Tenable SC sync completed successfully.[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.error(f"Error in Tenable SC JSONL sync: {str(e)}", exc_info=True)


# Command from existing commands.py
@tenable.command(name="sync_vulns")
@regscale_id(help="RegScale will create findings as children of this security plan.")
@click.option(
    "--query-id",
    type=click.INT,
    required=True,
    help="Tenable SC Query ID to retrieve vulnerability data from.",
    prompt="Enter Tenable SC Query ID",
)
def sync_vulns(regscale_id: int, query_id: int):
    """
    Sync vulnerabilities from Tenable SC to RegScale.

    Fetches vulnerability data from Tenable SC based on the specified query ID
    and syncs it to RegScale as findings under the specified security plan.
    """
    try:
        # Use the original SC scanner for direct API sync
        console.print("[bold]Starting Tenable SC vulnerability sync...[/bold]")
        scanner = SCIntegration(plan_id=regscale_id, scan_date=get_current_datetime())
        scanner.fetch_vulns_query(query_id=query_id)
        console.print("[bold green]Tenable SC vulnerability sync complete.[/bold green]")
    except Exception as e:
        logger.error(f"Error syncing Tenable SC vulnerabilities: {str(e)}", exc_info=True)
        console.print(f"[bold red]Error syncing Tenable SC vulnerabilities: {str(e)}[/bold red]")


# Command from existing commands.py
@tenable.command(name="sync_jsonl")
@regscale_id(help="RegScale will create findings as children of this security plan.")
@click.option(
    "--query-id",
    type=click.INT,
    required=False,
    help="Tenable SC Query ID to retrieve vulnerability data from.",
)
@click.option(
    "--file-path",
    type=click.Path(exists=True),
    required=False,
    help="Path to directory containing Tenable SC data files (json or jsonl).",
)
@click.option(
    "--batch-size",
    type=click.INT,
    default=1000,
    help="Batch size for API requests (default: 1000).",
)
@click.option(
    "--mapping-file",
    type=click.Path(exists=True),
    help="Custom mapping file for data transformation.",
    required=False,
)
@click.option(
    "--skip-validation",
    is_flag=True,
    help="Skip RegScale object validation (use for development environments)",
    default=True,
)
def sync_jsonl(
    regscale_id: int,
    query_id: Optional[int],
    file_path: Optional[str],
    batch_size: int,
    mapping_file: Optional[str] = None,
    skip_validation: bool = False,
):
    """
    Sync Tenable SC data to RegScale using the optimized JSONL implementation.

    This command uses the JSONL implementation which is optimized for handling
    large datasets with better memory efficiency and performance.

    The implementation includes efficient batch processing for API requests and
    transformer-based mapping of complex data fields when a mapping file is provided.

    If neither query-id nor file-path is provided, the command will look for
    existing data files in the artifacts directory.
    """
    # Check license
    if not check_license():
        click.echo("No license available, exiting.")
        return

    # Validate the security plan ID (if not skipping validation)
    if not skip_validation:
        ssp = SecurityPlan.get_object(object_id=regscale_id)
        if not ssp:
            console.print(f"[bold red]Error:[/bold red] No security plan with ID {regscale_id} exists.")
            return
    else:
        console.print("[yellow]Skipping RegScale validation for development mode[/yellow]")

    # Run the integration
    try:
        # Create the integration with the specified parameters
        scanner = TenableSCJsonlScanner(
            plan_id=regscale_id,
            query_id=query_id,
            file_path=file_path,
            batch_size=batch_size,
        )

        # Run the synchronization based on whether a mapping file was provided
        if mapping_file:
            console.print("[yellow]Using custom mapping file for transformer-based processing.[/yellow]")
            scanner.sync_with_transformer(mapping_file=mapping_file)
        else:
            scanner.sync_assets_and_findings()

        console.print("[bold green]Tenable SC sync completed successfully.[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.error(f"Error in Tenable SC JSONL sync: {str(e)}", exc_info=True)


@io.command(name="sync_compliance_controls")
@regscale_ssp_id()
@click.option(
    "--catalog_id",
    type=click.INT,
    help="The ID number from RegScale Catalog that the System Security Plan's controls belong to",
    prompt="Enter RegScale Catalog ID",
    required=True,
)
@click.option(
    "--framework",
    required=True,
    type=click.Choice(["800-53", "800-53r5", "CSF", "800-171"], case_sensitive=True),
    help="The framework to use. from Tenable.io frameworks MUST be the same RegScale Catalog of controls",
)
@hidden_file_path(help="The file path to load control data instead of fetching from Tenable.io")
def sync_compliance_data(regscale_ssp_id: int, catalog_id: int, framework: str, offline: Optional[Path] = None):
    """
    Sync the compliance data from Tenable.io to create control implementations for controls in frameworks.
    """
    from regscale.integrations.commercial.tenablev2.sync_compliance import sync_compliance_data

    sync_compliance_data(ssp_id=regscale_ssp_id, catalog_id=catalog_id, framework=framework, offline=offline)


# Add import_nessus to __all__ exports at the end of the file
__all__ = [
    "tenable",
    "sc",
    "nessus",
    "import_nessus",
    "sync_vulns",
    "sync_jsonl",
]
