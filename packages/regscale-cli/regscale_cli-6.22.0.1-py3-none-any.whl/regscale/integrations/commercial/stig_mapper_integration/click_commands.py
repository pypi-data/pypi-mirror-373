"""STIG Mapper commands."""

import logging

import click

from regscale.models import regscale_id, regscale_module, Asset

logger = logging.getLogger(__name__)


@click.group(name="stig_mapper")
def stig_mapper():
    """Map data from STIGs to RegScale."""


@stig_mapper.command(name="run")
@click.option(
    "--json-file", help="Path to the JSON file with mapping rules", required=True, type=click.Path(exists=True)
)
@regscale_id()
@regscale_module()
def run(json_file: str, regscale_id: int, regscale_module: str):
    """
    Map STIGs from a .json file to assets in RegScale.
    """
    from regscale.integrations.commercial.stig_mapper_integration.mapping_engine import StigMappingEngine as STIGMapper
    from os import path

    if not path.exists(json_file):
        logger.error(f"File {json_file} does not exist.")
        return
    stig_mapper = STIGMapper(json_file)
    assets = Asset.get_all_by_parent(parent_id=regscale_id, parent_module=regscale_module)
    asset_mappings = []
    for asset in assets:
        asset_mappings.append(stig_mapper.map_associated_stigs_to_asset(asset=asset, ssp_id=regscale_id))
    logger.info(f"Created {len(asset_mappings)} new asset mappings")
