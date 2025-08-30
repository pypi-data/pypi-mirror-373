#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""standard python imports"""
import glob
import logging
from datetime import date, datetime
from typing import Literal, Optional

import click
from dateutil.relativedelta import relativedelta

from regscale.core.app.utils.regscale_utils import check_module_id
from regscale.models import regscale_id, regscale_module

logger = logging.getLogger("regscale")


@click.group()
def fedramp():
    """Performs bulk processing of FedRAMP files (Upload trusted data only)."""


# FedRAMP Docx Support
@fedramp.command(context_settings={"show_default": True})
@click.option(
    "--file_path",
    "-f",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    required=True,
    prompt="Enter the full file path of the FedRAMP (.docx) document to ingest to RegScale.",
    help="RegScale will process and load the FedRAMP document.",
)
@click.option(
    "--base_fedramp_profile",
    "-pn",
    type=click.STRING,
    required=False,
    help="Enter the name of the RegScale FedRAMP profile to use.",
    default="FedRAMP - High",
)
@click.option(
    "--base_fedramp_profile_id",
    "-p",
    type=click.INT,
    required=False,
    help="Enter the ID of the RegScale FedRAMP profile to use.",
)
@click.option(
    "--appendix_a_file_path",
    "-a",
    type=click.Path(exists=True),
    required=False,
    prompt="Enter the full file path of the FedRAMP Appendix A (.docx) document to ingest to RegScale.",
    help="RegScale will process and load the FedRAMP Appendix A document, used during Rev5 version import.",
)
@click.option(
    "--save_data",
    type=click.BOOL,
    default=False,
    required=False,
    help="Whether to save the data as a JSON file.",
)
@click.option(
    "--add_missing",
    type=click.BOOL,
    default=False,
    required=False,
    help="Whether to create missing controls from profile in the SSP.",
)
@click.option(
    "--version",
    "-rev",
    type=click.Choice(["rev4", "rev5", "4", "5"], case_sensitive=False),
    help="FedRAMP revision version.",
    prompt="Rev4 or Rev5",
    required=True,
)
def load_fedramp_docx(
    file_path: click.Path,
    base_fedramp_profile: click.STRING,
    base_fedramp_profile_id: Optional[click.STRING],
    save_data: click.BOOL,
    add_missing: click.BOOL,
    appendix_a_file_path: click.Path,
    version: Literal["rev4", "rev5", "4", "5"],
):
    """
    Convert a FedRAMP docx file to a RegScale SSP.
    """
    if "4" in version:
        from regscale.integrations.public.fedramp.fedramp_docx import process_fedramp_docx

        logger.info(f"Processing FedRAMP document {file_path}.")
        process_fedramp_docx(file_path, base_fedramp_profile, base_fedramp_profile_id, save_data, add_missing)
    elif "5" in version:
        from regscale.integrations.public.fedramp.fedramp_five import process_fedramp_docx_v5

        if not base_fedramp_profile_id:
            from regscale.integrations.public.fedramp.fedramp_common import find_profile_by_name

            profile = find_profile_by_name(base_fedramp_profile) or {}
            base_fedramp_profile_id = profile.get("id")
            if not base_fedramp_profile_id:
                from regscale.core.app.utils.app_utils import error_and_exit

                error_and_exit(
                    f"Unable to find profile with name {base_fedramp_profile}. Please provide a profile ID "
                    "by using the -p flag."
                )

        process_fedramp_docx_v5(file_path, base_fedramp_profile_id, save_data, add_missing, appendix_a_file_path)  # type: ignore


@fedramp.command()
@click.option(
    "--file_path",
    "-f",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    required=True,
    prompt="Enter the file name of the FedRAMP JSON document to process.",
    help="RegScale will process and load the FedRAMP document.",
)
@click.option(
    "--submission_date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=str(date.today()),
    required=True,
    prompt="Enter the submission date of this FedRAMP document.",
    help=f"Submission date, default is today: {date.today()}.",
)
@click.option(
    "--expiration_date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=str((datetime.now() + relativedelta(years=3)).date()),
    required=True,
    prompt="Enter the expiration date of this FedRAMP document.",
    help=f"Expiration date, default is {str((datetime.now() + relativedelta(years=3)).date())}.",
)
def load_fedramp_oscal(file_path, submission_date, expiration_date):
    """
    [BETA] Convert a FedRAMP OSCAL SSP json file to a RegScale SSP.
    """
    from regscale.integrations.public.fedramp.fedramp_common import process_fedramp_oscal_ssp

    if not expiration_date:
        today_dt = date.today()
        expiration_date = date(today_dt.year + 3, today_dt.month, today_dt.day)

    process_fedramp_oscal_ssp(file_path, submission_date, expiration_date)


@fedramp.command()
@click.option(
    "--file-path",
    "-f",
    type=click.Path(exists=True),
    help="File to upload to RegScale.",
    required=True,
)
@click.option(
    "--catalogue_id",
    "-c",
    type=click.INT,
    help="The RegScale ID # of the catalogue to use for controls in the profile.",
    required=True,
)
def import_fedramp_ssp_xml(file_path: click.Path, catalogue_id: click.INT):
    """
    Import FedRAMP Revision 4/5 SSP XML into RegScale
    """
    from collections import deque

    from regscale.integrations.public.fedramp.import_fedramp_r4_ssp import parse_and_load_xml_rev4
    from regscale.integrations.public.fedramp.ssp_logger import SSPLogger

    logger = SSPLogger()
    logger.info(event_msg="Importing FedRAMP SSP XML into RegScale")
    parse_generator = parse_and_load_xml_rev4(None, str(file_path), catalogue_id)
    deque(parse_generator, maxlen=1)


@fedramp.command(context_settings={"show_default": True})
@click.option(
    "--appendix_a_file_path",
    "-a",
    type=click.Path(exists=True),
    required=False,
    prompt="Enter the full file path of the FedRAMP Appendix A (.docx) document to ingest to RegScale.",
    help="RegScale will process and load the FedRAMP Appendix A document.",
)
@click.option(
    "--base_fedramp_profile_id",
    "-p",
    type=click.INT,
    required=True,
    help="The RegScale FedRAMP profile ID to use.",
)
@click.option(
    "--add_missing",
    type=click.BOOL,
    default=False,
    required=False,
    help="Whether to create missing controls from profile in the SSP.",
)
@click.option("--regscale_id", "-i", help="Regscale id to push inventory to in RegScale.", required=True)
def load_fedramp_appendix_a(
    appendix_a_file_path: str, base_fedramp_profile_id: int, add_missing: click.BOOL, regscale_id: int  # noqa
):
    """
    Convert a FedRAMP Appendix A docx file to a RegScale SSP.
    """
    from regscale.integrations.public.fedramp.fedramp_five import load_appendix_a as _load_appendix_a

    _load_appendix_a(
        appendix_a_file_name=appendix_a_file_path,
        parent_id=regscale_id,
        profile_id=base_fedramp_profile_id,
        add_missing=add_missing,
    )


@fedramp.command(name="import_fedramp_inventory")
@click.option(
    "--path",
    "-f",
    type=click.Path(exists=True, dir_okay=True),
    help="The File OR Folder Path to the inventory .xlsx files.",
    prompt="Inventory .xlsx folder location",
    required=True,
)
@click.option(
    "--sheet_name",
    "-s",
    type=click.STRING,
    help="Sheet name in the inventory .xlsx file to parse.",
    default="Inventory",
    required=False,
)
@click.option(
    "--regscale_id",
    "-i",
    type=click.INT,
    help="RegScale Record ID to update.",
    prompt="RegScale Record ID",
    required=True,
)
@click.option(
    "--regscale_module",
    "-m",
    type=click.STRING,
    help="RegScale Module for the provided ID.",
    prompt="RegScale Record Module",
    required=True,
)
@click.option(
    "--version",
    "-rev",
    type=click.Choice(["rev4", "rev5", "4", "5"], case_sensitive=False),
    help="FedRAMP revision version.",
    prompt="Rev4 or Rev5",
    required=True,
)
def import_fedramp_inventory(
    path: click.Path,
    sheet_name: str,
    regscale_id: int,
    regscale_module: str,
    version: Literal["rev4", "rev5", "4", "5"],
):  # noqa
    """
    Import FedRAMP rev4 or rev5 Inventory Workbook into RegScale
    """
    import os
    from pathlib import Path

    from regscale.integrations.public.fedramp.import_workbook import upload

    link_path = Path(path)
    if link_path.is_dir():
        files = glob.glob(str(link_path) + os.sep + "*.xlsx")
        if not files:
            logger.warning("No files found in the folder.")
            return
        for file in files:
            try:
                upload(
                    inventory=file,
                    sheet_name=sheet_name,
                    record_id=regscale_id,
                    module=regscale_module,
                    version=version,
                )
            except Exception as e:
                logger.error(f"Failed to parse inventory from {file}: {e}")
                continue
    elif link_path.is_file():
        try:
            upload(
                inventory=str(link_path),
                sheet_name=sheet_name,
                record_id=regscale_id,
                module=regscale_module,
                version=version,
            )
        except Exception as e:
            logger.error(f"Failed to parse inventory from {link_path}: {e}")


@fedramp.command(name="import-poam")
@click.option(
    "--file_path",
    "-f",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    required=True,
    prompt="Enter the file path containing FedRAMP (.xlsx) POAM workbook to ingest to RegScale.",
    help="RegScale will process and load the FedRAMP POAMs as RegScale issues.",
)
@regscale_id()
@regscale_module()
@click.option(
    "--poam_id_column",
    "-pc",
    type=click.STRING,
    help="The column name containing the POAM ID.",
    required=False,
    default="POAM ID",
)
@click.option(
    "--resolve_empty_status_date",
    "-rs",
    type=click.Choice(["CURRENT_DATE", "USE_NEIGHBOR"], case_sensitive=False),
    default="CURRENT_DATE",
    help="Choose between 'CURRENT_DATE' (default) or 'USE_NEIGHBOR'.",
)
def import_fedramp_poam_template(
    file_path: click.Path, regscale_id: int, regscale_module: str, poam_id_column: str, resolve_empty_status_date: str
) -> None:
    """
    Import a FedRamp POA&M document to RegScale issues.
    """
    # suppress UserWarnings from openpyxl
    import warnings

    from regscale.integrations.public.fedramp.poam.scanner import FedrampPoamIntegration

    warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

    if not check_module_id(parent_id=regscale_id, parent_module=regscale_module):
        raise ValueError(f"RegScale ID {regscale_id} is not a valid member of {regscale_module}.")

    # Initialize the FedRAMP integration
    integration = FedrampPoamIntegration(plan_id=regscale_id, file_path=str(file_path))
    integration.poam_id_header = poam_id_column
    integration.file_path = str(file_path)

    # First sync assets
    integration.sync_assets(
        plan_id=regscale_id,
        file_path=str(file_path),
        poam_sheets=integration.poam_sheets,
        workbook=integration.workbook,
        validators=integration.validators,
    )

    # Then process the POAM findings
    integration.sync_findings(
        plan_id=regscale_id,
        file_path=str(file_path),
        poam_sheets=integration.poam_sheets,
        workbook=integration.workbook,
        validators=integration.validators,
        resolve_empty_status_date=resolve_empty_status_date,
        close_outdated_findings=False,
    )

    # Ensure workbook is closed
    if integration.workbook:
        integration.workbook.close()


@fedramp.command(name="import-drf")
@click.option(
    "--file_path",
    "-f",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    required=True,
    prompt="Enter the file path containing FedRAMP (.xlsx) POAM workbook to ingest to RegScale.",
    help="RegScale will process and load the FedRAMP POAMs as RegScale issues.",
)
@regscale_id()
@regscale_module()
def import_drf(file_path: click.Path, regscale_id: int, regscale_module: str) -> None:
    """
    Import a FedRamp DRF document to RegScale issues.
    """
    # suppress UserWarnings from openpyxl
    import warnings

    from regscale.models.integration_models.drf import DRF

    warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

    if not check_module_id(parent_id=regscale_id, parent_module=regscale_module):
        raise ValueError(f"RegScale ID {regscale_id} is not a valid member of {regscale_module}.")
    DRF(file_path=file_path, module_id=regscale_id, module=regscale_module)


@fedramp.command(name="import-cis-crm")
@click.option(
    "--file_path",
    "-f",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    help="The file path to the FedRAMP CIS CRM .xlsx file.",
    prompt="FedRAMP CIS CRM .xlsx file location",
    required=True,
)
@click.option(
    "--version",
    "-rev",
    type=click.Choice(["rev4", "rev5", "4", "5"], case_sensitive=False),
    help="FedRAMP revision version.",
    prompt="Rev4 or Rev5",
    required=True,
)
@click.option(
    "--cis_sheet_name",
    "-cis",
    type=click.STRING,
    help="CIS sheet name in the FedRAMP CIS CRM .xlsx to parse.",
    prompt="CIS Sheet Name",
    default="CIS Worksheet",
    required=True,
)
@click.option(
    "--profile_id",
    "-p",
    type=click.INT,
    help="The ID number from RegScale of the Profile.  (This will generate the control implementations for a new Security Plan)",
    prompt="Enter RegScale Profile ID",
    required=True,
)
@click.option(
    "--crm_sheet_name",
    "-crm",
    type=click.STRING,
    help="CRM sheet name in the FedRAMP CIS CRM .xlsx to parse.",
    required=False,
)
@click.option(
    "--leveraged_auth_id",
    "-l",
    type=click.INT,
    help="RegScale Leveraged Authorization ID #, if none provided, one will be created.",
    required=False,
    default=0,
)
def import_ciscrm(
    file_path: click.Path,
    version: str,
    cis_sheet_name: str,
    crm_sheet_name: Optional[click.STRING],
    profile_id: int,
    leveraged_auth_id: int = 0,
):
    """
    [BETA] Import FedRAMP Rev5 CIS/CRM Workbook into a new RegScale System Security Plan.
    """

    from regscale.integrations.public.fedramp.fedramp_cis_crm import parse_and_import_ciscrm

    version_literal: Literal["rev4", "rev5", "4", "5"] = version  # type: ignore
    parse_and_import_ciscrm(
        file_path=file_path,
        version=version_literal,  # type: ignore
        cis_sheet_name=cis_sheet_name,
        crm_sheet_name=crm_sheet_name,
        profile_id=profile_id,
        leveraged_auth_id=leveraged_auth_id,
    )
