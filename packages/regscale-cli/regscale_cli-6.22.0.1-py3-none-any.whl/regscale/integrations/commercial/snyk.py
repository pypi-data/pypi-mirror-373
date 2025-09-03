#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Snyk RegScale integration"""
from datetime import datetime
from os import PathLike
from typing import Optional

import click

from regscale.models.integration_models.flat_file_importer import FlatFileImporter
from regscale.models.integration_models.snyk import Snyk


@click.group()
def snyk():
    """Performs actions on Snyk export files."""


@snyk.command(name="import_snyk")
@FlatFileImporter.common_scanner_options(
    message="File path to the folder containing Snyk .xlsx or .json files to process to RegScale.",
    prompt="File path for Snyk files",
    import_name="snyk",
    support_component=True,
)
def import_snyk(
    folder_path: PathLike[str],
    regscale_ssp_id: int,
    component_id: int,
    scan_date: datetime,
    mappings_path: PathLike[str],
    disable_mapping: bool,
    s3_bucket: str,
    s3_prefix: str,
    aws_profile: str,
    upload_file: bool,
):
    """
    Import scans, vulnerabilities and assets to RegScale from Snyk export files
    """

    if not regscale_ssp_id and not component_id:
        raise click.UsageError("You must provide either a --regscale_ssp_id or a --component_id to import Snyk scans.")

    import_synk_files(
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


def import_synk_files(
    folder_path: PathLike[str],
    object_id: int,
    is_component: bool,
    scan_date: datetime,
    mappings_path: PathLike[str],
    disable_mapping: bool,
    s3_bucket: str,
    s3_prefix: str,
    aws_profile: str,
    upload_file: Optional[bool] = True,
) -> None:
    """
    Import Snyk scans, vulnerabilities and assets to RegScale from Snyk files

    :param PathLike[str] folder_path: File path to the folder containing Snyk .xlsx files to process to RegScale
    :param int object_id: The RegScale SSP ID or Component ID
    :param datetime scan_date: The date of the scan
    :param PathLike[str] mappings_path: The path to the mappings file
    :param bool disable_mapping: Whether to disable custom mappings
    :param str s3_bucket: The S3 bucket to download the files from
    :param str s3_prefix: The S3 prefix to download the files from
    :param str aws_profile: The AWS profile to use for S3 access
    :param Optional[bool] upload_file: Whether to upload the file to RegScale after processing, defaults to True
    :param bool is_component: Whether the object is a component
    :rtype: None
    """
    FlatFileImporter.import_files(
        import_type=Snyk,
        import_name="Snyk",
        file_types=[".xlsx", ".json"],
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
