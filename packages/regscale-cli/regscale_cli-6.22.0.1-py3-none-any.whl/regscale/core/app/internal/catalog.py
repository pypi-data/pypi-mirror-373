#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Integrates catalog export, diagnose and compare into RegScale"""
# standard python imports
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

import click
from pathlib import Path
from requests import Response
from rich.console import Console
from rich.progress import Progress
from rich.table import Table

from regscale.core.app.application import Application
from regscale.core.app.utils.app_utils import check_file_path, error_and_exit
from regscale.core.app.utils.catalog_utils.compare_catalog import display_menu as start_compare
from regscale.core.app.utils.catalog_utils.diagnostic_catalog import display_menu as start_diagnostic
from regscale.core.app.utils.catalog_utils.download_catalog import display_menu, select_catalog
from regscale.core.app.utils.catalog_utils.update_catalog_v3 import display_menu as start_update
from regscale.core.app.utils.catalog_utils.update_catalog_v3 import import_catalog
from regscale.core.app.utils.catalog_utils.update_plans import sync_all_plans, sync_plan_controls
from regscale.models.regscale_models.catalog import Catalog


@click.group()
def catalog():
    """Export, diagnose, and compare catalog from RegScale.com/regulations."""


@catalog.command(name="sync_security_plans")
@click.option("--all", is_flag=True, help="Flag to sync all System Security Plans.")
@click.option("--plan_id", type=int, help="Sync a specific System Security Plan by ID #.")
@click.option("--dry_run", is_flag=True, help="Perform a dry run of the sync without making any changes.")
def sync_security_plans(all: bool, plan_id: int, dry_run: bool = False):
    """Sync security plans with the catalog."""
    if all:
        sync_all_plans(dry_run=dry_run)
    elif plan_id:
        sync_plan_controls(ssp_id=plan_id, dry_run=dry_run)
    else:
        click.echo(
            "No valid option provided. Use '--all' to sync all plans or '--plan_id <id>' to sync a specific plan."
        )


@catalog.command(name="import")
@click.option(
    "--catalog_path",
    prompt="Enter the path of the Catalog file to import",
    help="RegScale will load the Catalog",
    type=click.Path(exists=True),
    required=True,
)
def import_(catalog_path: str):
    """Import a catalog.json file into RegScale."""
    console = Console()
    res = import_catalog(Path(catalog_path))
    dat = res.json()
    if dat.get("success"):
        console.print(
            f"Catalog #{dat['catalogId']} imported successfully with {dat['importedItemCount']} " + "controls.",
            style="bold green",
        )
    else:
        console.print(res.json().get("message"), style="bold red")


@catalog.command(name="download")
@click.option("--show_menu", type=bool, default=True, help="Show menu of downloadable catalogs")
@click.option("--select", type=int, help="Select a single catalog to download")
@click.option("--download_all", is_flag=True, help="Download all catalogs")
def export(show_menu: bool, download_all: bool, select: int) -> None:
    """
    Export catalog from RegScale.com/regulations.
    """
    app = Application()
    if select or download_all:
        show_menu = False
    max_index = display_menu(show_menu)
    if download_all:
        # Download every URL in the catalog
        cat_range = range(1, max_index + 1)
        downloaded_count = 0
        # use threadpool executor to download all catalogs
        with ThreadPoolExecutor(max_workers=20) as executor:
            args = [(index, False) for index in cat_range]
            with Progress() as progress:
                task = progress.add_task(f"[cyan]Downloading {len(args)} catalogs...", total=len(args))
                for cat, registry_item in executor.map(
                    lambda x: select_catalog(catalog_index=x[0], logging=x[1]), args
                ):
                    if isinstance(cat, dict):
                        downloaded_count += 1
                    else:
                        app.logger.debug(registry_item)
                        app.logger.error(f"Failed to download catalog: {registry_item['title']}")
                    progress.advance(task, 1)
        app.logger.info(f"Successfully Downloaded {downloaded_count} catalogs.")
        return
    if not select:
        select_catalog(catalog_index=0)
    else:
        select_catalog(catalog_index=select)


@catalog.command(name="diagnose", deprecated=True)
def diagnostic():
    """Diagnose catalog and output metadata."""
    start_diagnostic()


@catalog.command(name="compare", deprecated=True)
def compare():
    """Run diagnostic and compare catalogs while reporting differences."""
    start_compare()


@catalog.command(name="update", deprecated=True)
@click.option("--include_meta", is_flag=True, help="Include metadata in the import")
def update(include_meta: bool = False):
    """Update the catalog from RegScale.com/regulations."""
    start_update(include_meta)


@catalog.command(name="check_for_updates")
@click.option("--catalog_id", type=int, help="Catalog ID to check for updates", required=False)
def check_for_updates(catalog_id: Optional[int] = None):
    """Check for updates to the catalog."""
    gen_updatable_catalogs(catalog_id=catalog_id)


@catalog.command(name="update_via_platform")
def update_via_platform():
    """
    [BETA] Update application instance catalog with new platform API(s).
    """
    selected_id = get_selected_id()
    res = get_update_report(selected_id)
    handle_report(response=res)
    update_catalog(selected_id)


def get_selected_id() -> int:
    """Get the selected catalog ID.

    :return: Selected catalog ID
    :rtype: int
    """
    cats = {cat["id"]: cat for cat in Catalog.get_updatable_catalogs()}
    existing_cats = [cat.id for cat in Catalog.get_list()]
    selected_id = prompt_for_catalog("Please select catalog to update")
    while selected_id not in cats:
        message = "The catalog ID selected is not updatable, please try again."
        # endless loop until a valid catalog is selected
        if selected_id not in existing_cats:
            message = "The catalog ID does not exist on this system."
        selected_id = prompt_for_catalog(message)
    return selected_id


def get_update_report(selected_id: int) -> Response:
    """
    Get the update report for the selected catalog.

    :param int selected_id: Selected catalog ID
    :return: Response object, new_catalog
    :rtype: Response
    """
    res = Catalog.get_update_report_for_catalog(catalog_id=selected_id)
    return res


def update_catalog(selected_id: int) -> None:
    """
    Update the catalog.

    :param int selected_id: Selected catalog ID
    :return: None
    :rtype: None
    """
    app = Application()
    val = click.prompt("Would you like to update the catalog? [Y/N]", type=str, default="N")
    if val.lower().startswith("y"):
        safety_prompt = click.prompt(
            "Are you sure? This operation cannot be canceled or reversed! [Y/N]", type=str, default="N"
        )
        if safety_prompt.lower().startswith("y"):
            app.logger.debug("Updating the catalog the easy way!")
            res = Catalog.update_regscale_catalog(catalog_id=selected_id)
            if isinstance(res, dict):
                app.logger.info("Catalog updated successfully!")
                return
            message = res.reason + ", " + res.content.decode("utf-8") if res.content else res.reason
            app.logger.error(f"Failed to update the catalog.\nStatus Code: {res.status_code}\nReason: {message}")


def handle_report(response: Response) -> None:
    """Handle the report data.

    :param Response response: Response object
    :return: None
    :rtype: None
    """
    console = Console()
    check_file_path("artifacts")
    data_type = get_response_data_type(response)

    if not response.ok:
        error_and_exit(f"Failed to get the report: {response.text}")
    file_ext = data_type.lower() if data_type in ["JSON", "CSV"] else error_and_exit("Unknown Report Type, exiting.")
    save_path = Path(f"./artifacts/report.{file_ext}")
    with open(save_path, "wb") as f:
        f.write(response.content)
    console.print(f"A Comparison Report saved to {save_path.absolute()}")
    val = click.prompt("Press Y to view the report", type=str, default="N")
    if val.lower().startswith("y"):
        if data_type == "CSV":
            view_csv_report(console, save_path)
        else:
            console.print(response.text)


def view_csv_report(console: Console, file_path: Path) -> None:
    """View the CSV report.

    :param Console console: Console object
    :param Path file_path: Path to the CSV file
    :return: None
    :rtype: None
    """
    import csv

    from rich.table import Table

    # Create a table
    table = Table(show_header=True)
    max_rows = os.get_terminal_size().lines
    # Open the CSV file
    with open(file_path.absolute(), "r") as file:
        csv_reader = csv.reader(file)
        if sum(1 for _ in csv_reader) > max_rows:
            console.print(
                "Unable to view report, too many rows to display on console.\nOpen the file in a text editor."
            )
            return
        headers = next(csv_reader)  # Get the headers from the first line

        # Add columns to the table
        for header in headers:
            table.add_column(header)

        # Add rows to the table
        for row in csv_reader:
            table.add_row(*row)

    # Print the table
    console.print(table)


def get_response_data_type(response: Response) -> str:
    """
    Get the data type of the response content

    :param Response response: Response object
    :return: Data type of the response content
    :rtype: str
    """
    content_type = response.headers.get("Content-Type")

    if "application/json" in content_type:
        return "JSON"
    elif "text/csv" in content_type:
        return "CSV"
    else:
        return "Unknown"


def gen_updatable_catalogs(catalog_id: Optional[int] = None) -> list[dict]:
    """
    Generate updatable catalogs.

    :param Optional[int] catalog_id: Catalog ID, defaults to None
    :return: List of updatable catalogs
    :rtype: list[dict]
    """
    console = Console()
    cats = Catalog.get_updatable_catalogs()
    # format nicely in rich table
    table = Table(title="Updatable Catalogs")
    table.add_column("Catalog ID")
    table.add_column("Catalog Title")
    if catalog_id:
        cats = [cat for cat in cats if cat["id"] == catalog_id]
    for cat in cats:
        cat_id = cat["id"]
        cat_title = cat["title"]
        table.add_row(f"[yellow]{cat_id}", f"[green] {cat_title}")
    if not cats:
        console.print("No catalogs to update", style="yellow")
    else:
        console.print(table)
    return cats


def prompt_for_catalog(message: str) -> int:
    """
    Prompt user for catalog ID

    :param str message: Message to display to user
    :return: Catalog ID
    :rtype: int
    """
    catalog_id = click.prompt(message, type=int)
    return catalog_id
