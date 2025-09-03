"""
This module contains the Click command group for SAP.
"""

import logging

import click

from regscale.integrations.commercial.sap.click import tenable
from regscale.models.app_models.click import regscale_ssp_id

logger = logging.getLogger("regscale")


@tenable.command(name="sync_vulns")
@regscale_ssp_id()
@click.option(
    "--path",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    help="Path to the CSV file containing the SAP Concur data.",
    required=True,
)
def sync_vulns(regscale_ssp_id: int, path: str):
    """
    Synchronize vulnerabilities from SAP Concur Tenable data.
    """
    from .scanner import SAPConcurScanner

    SAPConcurScanner(plan_id=regscale_ssp_id).sync_findings(plan_id=regscale_ssp_id, path=path)


@tenable.command(name="sync_assets")
@regscale_ssp_id()
@click.option(
    "--path",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    help="Path to the CSV file containing the SAP Concur data.",
    required=True,
)
def sync_assets(regscale_ssp_id: int, path: str):
    """
    Synchronize assets from SAP Concur Tenable data.

    :param int regscale_ssp_id: RegScale System Security Plan ID
    :param str path: Path to the CSV file containing the SAP Concur data
    """
    from .scanner import SAPConcurScanner

    SAPConcurScanner(plan_id=regscale_ssp_id).sync_assets(plan_id=regscale_ssp_id, path=path)
