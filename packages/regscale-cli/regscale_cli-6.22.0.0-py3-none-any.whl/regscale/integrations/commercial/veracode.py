#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Veracode RegScale integration"""
from datetime import datetime
from os import PathLike
from typing import Optional

import click
from pathlib import Path

from regscale.models.integration_models.flat_file_importer import FlatFileImporter
from regscale.models.integration_models.veracode import Veracode


@click.group()
def veracode():
    """Performs actions on Veracode export files."""


FlatFileImporter.show_mapping(
    group=veracode,
    import_name="veracode",
)


@veracode.command(name="import_veracode")
@FlatFileImporter.common_scanner_options(
    message="File path to the folder containing Veracode .xlsx files to process to RegScale.",
    prompt="File path for Veracode files",
    import_name="veracode",
    support_component=True,
)
def import_veracode(
    folder_path: PathLike[str],
    regscale_ssp_id: int,
    component_id: int,
    scan_date: datetime,
    mappings_path: Path,
    disable_mapping: bool,
    s3_bucket: str,
    s3_prefix: str,
    aws_profile: str,
    upload_file: bool,
):
    """
    Import scans, vulnerabilities and assets to RegScale from Veracode export files
    """
    if not regscale_ssp_id and not component_id:
        raise click.UsageError(
            "You must provide either a --regscale_ssp_id or a --component_id to import Veracode scans."
        )

    import_veracode_data(
        folder_path=folder_path,
        object_id=component_id if component_id else regscale_ssp_id,
        is_component=bool(component_id),
        scan_date=scan_date,
        mappings_path=mappings_path,
        disable_mapping=disable_mapping,
        s3_bucket=s3_bucket,
        s3_prefix=s3_prefix,
        aws_profile=aws_profile,
        upload_file=upload_file,
    )


def import_veracode_data(
    folder_path: PathLike[str],
    object_id: int,
    scan_date: datetime,
    mappings_path: Path,
    s3_bucket: str,
    s3_prefix: str,
    aws_profile: str,
    disable_mapping: Optional[bool] = False,
    upload_file: Optional[bool] = True,
    is_component: Optional[bool] = False,
) -> None:
    """Import scans, vulnerabilities and assets to RegScale from Veracode export files"

    :param os.PathLike[str] folder_path: Path to the folder containing Veracode files
    :param int object_id: RegScale SSP ID or Component ID
    :param bool is_component: Whether object_id is a component or not
    :param datetime scan_date: Scan date
    :param os.PathLike[str] mappings_path: Path to the header mapping file
    :param str s3_bucket: S3 bucket to download the files from
    :param str s3_prefix: S3 prefix to download the files from
    :param str aws_profile: AWS profile to use for S3 access
    :param bool disable_mapping: Disable mapping
    :param Optional[bool] upload_file: Whether to upload the file to RegScale after processing, defaults to True
    :rtype: None
    """
    FlatFileImporter.import_files(
        import_type=Veracode,
        import_name="Veracode",
        file_types=[".xml", ".xlsx", ".json"],
        folder_path=folder_path,
        object_id=object_id,
        scan_date=scan_date,
        mappings_path=mappings_path,
        disable_mapping=disable_mapping,
        s3_bucket=s3_bucket,
        s3_prefix=s3_prefix,
        aws_profile=aws_profile,
        upload_file=upload_file,
        is_component=is_component,
    )
