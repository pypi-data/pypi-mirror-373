#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""xray RegScale integration"""
from datetime import datetime
from os import PathLike
from typing import Optional

import click
from pathlib import Path

from regscale.models.integration_models.flat_file_importer import FlatFileImporter
from regscale.models.integration_models.xray import XRay


@click.group()
def xray():
    """Performs actions on xray files."""


@xray.command(name="import_xray")
@FlatFileImporter.common_scanner_options(
    message="File path to the folder containing JFrog XRay .json files to process to RegScale.",
    prompt="File path for JFrog XRay files",
    import_name="xray",
)
def import_xray(
    folder_path: PathLike[str],
    regscale_ssp_id: int,
    scan_date: datetime,
    mappings_path: Path,
    disable_mapping: bool,
    s3_bucket: str,
    s3_prefix: str,
    aws_profile: str,
    upload_file: bool,
) -> None:
    """
    Import JFrog XRay scans, vulnerabilities and assets to RegScale from XRay .json files
    """
    import_xray_files(
        folder_path=folder_path,
        regscale_ssp_id=regscale_ssp_id,
        scan_date=scan_date,
        mappings_path=mappings_path,
        disable_mapping=disable_mapping,
        s3_bucket=s3_bucket,
        s3_prefix=s3_prefix,
        aws_profile=aws_profile,
        upload_file=upload_file,
    )


def import_xray_files(
    folder_path: PathLike[str],
    regscale_ssp_id: int,
    scan_date: datetime,
    mappings_path: Path,
    disable_mapping: bool,
    s3_bucket: str,
    s3_prefix: str,
    aws_profile: str,
    upload_file: Optional[bool] = True,
) -> None:
    """
    Function to import XRay files to RegScale as assets and vulnerabilities

    :param PathLike[str] folder_path: Path to the folder containing XRay files
    :param int regscale_ssp_id: RegScale SSP ID
    :param datetime scan_date: Scan date
    :param Path mappings_path: Path to the header mapping file
    :param bool disable_mapping: Disable mapping
    :param str s3_bucket: S3 bucket to download the files from
    :param str s3_prefix: S3 prefix to download the files from
    :param str aws_profile: AWS profile to use for S3 access
    :param Optional[bool] upload_file: Whether to upload the file to RegScale after processing, default: True
    :rtype: None
    """
    FlatFileImporter.import_files(
        import_type=XRay,
        import_name="XRay",
        file_types=".json",
        folder_path=folder_path,
        object_id=regscale_ssp_id,
        scan_date=scan_date,
        mappings_path=mappings_path,
        disable_mapping=disable_mapping,
        s3_bucket=s3_bucket,
        s3_prefix=s3_prefix,
        aws_profile=aws_profile,
        upload_file=upload_file,
    )
