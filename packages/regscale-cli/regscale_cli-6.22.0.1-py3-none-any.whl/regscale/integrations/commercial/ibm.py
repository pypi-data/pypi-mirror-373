#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IBM AppScan RegScale integration"""
from datetime import datetime
from os import PathLike
from typing import Optional

import click

from regscale.models.integration_models.flat_file_importer import FlatFileImporter
from regscale.models.integration_models.ibm import AppScan


@click.group()
def ibm():
    """Performs actions on IBM AppScan files."""


@ibm.command(name="import_appscan")
@FlatFileImporter.common_scanner_options(
    message="File path to the folder containing IBM AppScan .csv files to process to RegScale.",
    prompt="File path for IBM AppScan files",
    import_name="ibm_appscan",
)
def import_appscan(
    folder_path: PathLike[str],
    regscale_ssp_id: int,
    scan_date: datetime,
    mappings_path: PathLike[str],
    disable_mapping: bool,
    s3_bucket: str,
    s3_prefix: str,
    aws_profile: str,
    upload_file: bool,
) -> None:
    """
    Import IBM AppScan scans, vulnerabilities and assets to RegScale from IBM AppScan files
    """
    import_appscan_files(
        folder_path,
        regscale_ssp_id,
        scan_date,
        mappings_path,
        disable_mapping,
        s3_bucket,
        s3_prefix,
        aws_profile,
        upload_file,
    )


def import_appscan_files(
    folder_path: PathLike[str],
    regscale_ssp_id: int,
    scan_date: datetime,
    mappings_path: PathLike[str],
    disable_mapping: bool,
    s3_bucket: str,
    s3_prefix: str,
    aws_profile: str,
    upload_file: Optional[bool] = True,
) -> None:
    """
    Import IBM AppScan scans, vulnerabilities and assets to RegScale from IBM AppScan files

    :param PathLike[str] folder_path: File path to the folder containing IBM AppScan .csv files to process to RegScale
    :param int regscale_ssp_id: The RegScale SSP ID
    :param datetime scan_date: The date of the scan
    :param PathLike[str] mappings_path: The path to the mappings file
    :param bool disable_mapping: Whether to disable custom mappings
    :param str s3_bucket: The S3 bucket to download the files from
    :param str s3_prefix: The S3 prefix to download the files from
    :param str aws_profile: The AWS profile to use for S3 access
    :param Optional[bool] upload_file: Whether to upload the file to RegScale after processing, defaults to True
    :rtype: None
    """
    FlatFileImporter.import_files(
        import_type=AppScan,
        import_name="IBM AppScan",
        file_types=".csv",
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
