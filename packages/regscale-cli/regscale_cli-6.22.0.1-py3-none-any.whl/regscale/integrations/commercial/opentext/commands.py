"""
This module contains the Click commands for the opentext integration.
"""

from datetime import datetime
from typing import Optional

import click
from pathlib import Path

from regscale.integrations.commercial.opentext.scanner import WebInspectIntegration
from regscale.models.integration_models.flat_file_importer import FlatFileImporter


# pylint: disable=W0621


@click.group()
def fortify():
    """Performs actions on the OpenText Fortify"""


@fortify.group(name="web_inspect")
def web_inspect():
    """Performs actions on the OpenText Web Inspect files."""


@web_inspect.command(name="import_scans")
@FlatFileImporter.common_scanner_options(
    message="File path to the folder containing OpenText WebInspect .xml files to process to RegScale.",
    prompt="File path for OpenText WebInspect files",
    import_name="opentext",
    support_component=True,
)
@click.option(
    "--destination",
    "-d",
    help="Path to download the files to. If not provided, files will be downloaded to the temporary directory.",
    type=click.Path(exists=True, dir_okay=True),
    required=False,
)
@click.option(
    "--file_pattern",
    "-fp",
    help="[Optional] File pattern to match (e.g., '*.xml')",
    required=False,
)
def import_scans(
    destination: Optional[Path],
    file_pattern: str,
    folder_path: Path,
    regscale_ssp_id: int,
    component_id: int,
    scan_date: datetime,
    mappings_path: Path,
    disable_mapping: bool,
    s3_bucket: str,
    s3_prefix: str,
    aws_profile: str,
    upload_file: bool = False,
):
    """
    Import and process a folder of Fortify WebInspect XML file(s).
    """
    # Use the new WebInspectIntegration class to sync assets and findings
    if s3_bucket and not folder_path:
        folder_path = s3_bucket

    if not regscale_ssp_id and not component_id:
        raise click.UsageError(
            "You must provide either a --regscale_ssp_id or a --component_id to import OpenText scans."
        )

    wi = WebInspectIntegration(
        plan_id=component_id if component_id else regscale_ssp_id,
        is_component=True if component_id else False,
        file_path=str(folder_path) if folder_path else None,
        s3_bucket=s3_bucket,
        s3_prefix=s3_prefix,
        aws_profile=aws_profile,
        scan_date=scan_date,
        mappings_path=str(mappings_path) if mappings_path else None,
        disable_mapping=disable_mapping,
        download_destination=destination,
        file_pattern=file_pattern,
        upload_file=upload_file,
    )
    wi.sync_assets_and_findings()
