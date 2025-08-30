"""
This module contains the Click command group for SAP.
"""

import logging

import click

logger = logging.getLogger("regscale")


@click.group()
def sap():
    """
    SAP Integration
    """


@sap.group(help="SAP Concur")
def concur():
    """Performs actions on the SAP Concur API."""


@concur.group(help="SAP Sysdig")
def sysdig():
    """Performs actions on the SysDig Concur export."""


@concur.group(help="Synchronize data from Tenable.")
def tenable():
    """Performs actions on a Tenable Concur export."""
