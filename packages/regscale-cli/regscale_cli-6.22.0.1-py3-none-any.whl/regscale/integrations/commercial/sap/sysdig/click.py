"""
This module contains the Click command group for SAP.
"""

import logging

import click

from regscale.integrations.commercial.sap.click import sysdig
from regscale.models.app_models.click import regscale_ssp_id

logger = logging.getLogger("regscale")


@sysdig.command(name="sync_vulns")
@regscale_ssp_id()
@click.option(
    "--path",
    type=click.STRING,
    help="Path to the CSV file containing the SAP Concur data.",
    required=True,
)
@click.option(
    "--scan_date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="The scan date of the file.",
    required=False,
)
def sync_vulns(regscale_ssp_id: int, path: str, scan_date: click.DateTime = None):
    """
    Synchronize vulnerabilities from SAP Concur data.
    """
    from regscale.integrations.commercial.sap.sysdig.sysdig_scanner import SAPConcurSysDigScanner

    SAPConcurSysDigScanner(plan_id=regscale_ssp_id).sync_findings(
        plan_id=regscale_ssp_id, path=path, scan_date=scan_date
    )


@sysdig.command(name="sync_assets")
@regscale_ssp_id()
@click.option(
    "--path",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    help="Path to the CSV file containing the SAP Concur data.",
    required=True,
)
def sync_assets(regscale_ssp_id: int, path: str):
    """
    Synchronize assets from SAP Concur data.

    :param int regscale_ssp_id: RegScale System Security Plan ID
    :param str path: Path to the CSV file containing the SAP Concur data
    """
    from regscale.integrations.commercial.sap.sysdig.sysdig_scanner import SAPConcurSysDigScanner

    SAPConcurSysDigScanner(plan_id=regscale_ssp_id).sync_assets(plan_id=regscale_ssp_id, path=path)
