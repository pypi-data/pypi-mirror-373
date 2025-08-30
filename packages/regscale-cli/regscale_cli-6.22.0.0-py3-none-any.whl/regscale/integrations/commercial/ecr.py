#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ECR RegScale integration"""
import os
from datetime import datetime
from typing import Optional

import click

from regscale.models.integration_models.ecr_models.ecr import ECR
from regscale.models.integration_models.flat_file_importer import FlatFileImporter


@click.group()
def ecr():
    """Performs actions on ECR Scanner artifacts."""


@ecr.command(name="import_ecr")
@FlatFileImporter.common_scanner_options(
    message="File path to the folder containing ECR files to process to RegScale.",
    prompt="File path for ECR files",
    import_name="ecr",
)
def import_ecr(
    folder_path: os.PathLike[str],
    regscale_ssp_id: click.INT,
    scan_date: datetime,
    mappings_path: os.PathLike[str],
    disable_mapping: click.BOOL,
    s3_bucket: str,
    s3_prefix: str,
    aws_profile: str,
    upload_file: bool,
):
    """
    Import ECR scans, vulnerabilities and assets to RegScale from ECR JSON files
    """
    import_ecr_scans(
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


def import_ecr_scans(
    folder_path: os.PathLike[str],
    regscale_ssp_id: click.INT,
    scan_date: datetime,
    mappings_path: os.PathLike[str],
    disable_mapping: click.BOOL,
    s3_bucket: str,
    s3_prefix: str,
    aws_profile: str,
    upload_file: Optional[bool] = True,
) -> None:
    """
    Function to import ECR scans to RegScale as assets and vulnerabilities

    :param os.PathLike[str] folder_path: Path to the folder containing ECR files
    :param int regscale_ssp_id: RegScale System Security Plan ID
    :param datetime scan_date: Date of the scan
    :param click.Path mappings_path: Path to the header mapping file
    :param bool disable_mapping: Disable header mapping
    :param str s3_bucket: S3 bucket name
    :param str s3_prefix: S3 prefix
    :param str aws_profile: AWS profile
    :param bool upload_file: Whether to upload the file to RegScale after processing, defaults to True
    :rtype: None
    """
    FlatFileImporter.import_files(
        import_type=ECR,
        import_name="ECR",
        file_types=[".csv", ".json"],
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
