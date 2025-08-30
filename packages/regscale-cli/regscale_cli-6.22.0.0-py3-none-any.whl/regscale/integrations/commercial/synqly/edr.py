# flake8: noqa E501
# pylint: disable=line-too-long

"""Edr connector commands for the RegScale CLI"""

import click
from regscale.models import regscale_ssp_id


@click.group()
def edr() -> None:
    """Edr connector commands for the RegScale CLI"""
    pass


@edr.command(name="sync_crowdstrike")
@regscale_ssp_id()
@click.option(
    "--url",
    type=click.STRING,
    help="Base URL for the CrowdStrike Falcon® API.",
    required=False,
)
def sync_crowdstrike(regscale_ssp_id: int, url: str) -> None:
    """Sync Edr from Crowdstrike to RegScale."""
    from regscale.models.integration_models.synqly_models.connectors import Edr

    edr_crowdstrike = Edr("crowdstrike")
    edr_crowdstrike.run_sync(regscale_ssp_id=regscale_ssp_id, url=url)


@edr.command(name="sync_defender")
@regscale_ssp_id()
def sync_defender(regscale_ssp_id: int) -> None:
    """Sync Edr from Defender to RegScale."""
    from regscale.models.integration_models.synqly_models.connectors import Edr

    edr_defender = Edr("defender")
    edr_defender.run_sync(regscale_ssp_id=regscale_ssp_id)


@edr.command(name="sync_malwarebytes")
@regscale_ssp_id()
@click.option(
    "--url",
    type=click.STRING,
    help="Base URL for the ThreatDown EDR API.",
    required=False,
)
def sync_malwarebytes(regscale_ssp_id: int, url: str) -> None:
    """Sync Edr from Malwarebytes to RegScale."""
    from regscale.models.integration_models.synqly_models.connectors import Edr

    edr_malwarebytes = Edr("malwarebytes")
    edr_malwarebytes.run_sync(regscale_ssp_id=regscale_ssp_id, url=url)


@edr.command(name="sync_sentinelone")
@regscale_ssp_id()
@click.option(
    "--edr_events_url",
    type=click.STRING,
    help="Base URL for the SentinelOne Singularity Data Lake API. This URL is required is required when querying EDR events.",
    required=False,
)
def sync_sentinelone(regscale_ssp_id: int, edr_events_url: str) -> None:
    """Sync Edr from Sentinelone to RegScale."""
    from regscale.models.integration_models.synqly_models.connectors import Edr

    edr_sentinelone = Edr("sentinelone")
    edr_sentinelone.run_sync(regscale_ssp_id=regscale_ssp_id, edr_events_url=edr_events_url)


@edr.command(name="sync_sophos")
@regscale_ssp_id()
@click.option(
    "--url",
    type=click.STRING,
    help="Base URL for the Sophos Endpoint API.",
    required=False,
)
def sync_sophos(regscale_ssp_id: int, url: str) -> None:
    """Sync Edr from Sophos to RegScale."""
    from regscale.models.integration_models.synqly_models.connectors import Edr

    edr_sophos = Edr("sophos")
    edr_sophos.run_sync(regscale_ssp_id=regscale_ssp_id, url=url)


@edr.command(name="sync_tanium")
@regscale_ssp_id()
def sync_tanium(regscale_ssp_id: int) -> None:
    """Sync Edr from Tanium to RegScale."""
    from regscale.models.integration_models.synqly_models.connectors import Edr

    edr_tanium = Edr("tanium")
    edr_tanium.run_sync(regscale_ssp_id=regscale_ssp_id)


# pylint: enable=line-too-long
