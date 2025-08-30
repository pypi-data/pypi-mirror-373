"""
Public commands for the RegScale CLI
"""

import click
from regscale.core.lazy_group import LazyGroup


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "import_docx": "regscale.integrations.public.fedramp.click.load_fedramp_docx",
        "import_oscal": "regscale.integrations.public.fedramp.click.load_fedramp_oscal",
        "import_ssp_xml": "regscale.integrations.public.fedramp.click.import_fedramp_ssp_xml",
        "import_appendix_a": "regscale.integrations.public.fedramp.click.load_fedramp_appendix_a",
        "import_inventory": "regscale.integrations.public.fedramp.click.import_fedramp_inventory",
        "import_poam": "regscale.integrations.public.fedramp.click.import_fedramp_poam_template",
        "import_drf": "regscale.integrations.public.fedramp.click.import_drf",
        "import_cis_crm": "regscale.integrations.public.fedramp.click.import_ciscrm",
    },
    name="fedramp",
)
def fedramp():
    """Performs bulk processing of FedRAMP files (Upload trusted data only)."""
    pass


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "import_ssp": "regscale.integrations.public.csam.csam.import_ssp",
        "import_poam": "regscale.integrations.public.csam.csam.import_poam",
    },
    name="csam",
)
def csam():
    """[BETA] Integration with DoJ's CSAM GRC Tool."""
    pass


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "ingest_pulses": "regscale.integrations.public.otx.ingest_pulses",
    },
    name="alienvault",
)
def alienvault():
    """AlienVault OTX Integration to load pulses to RegScale."""
    pass


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "ingest_cisa_kev": "regscale.integrations.public.cisa.ingest_cisa_kev",
        "ingest_cisa_alerts": "regscale.integrations.public.cisa.ingest_cisa_alerts",
    },
    name="cisa",
)
def cisa():
    """Performs administrative actions on the RegScale platform."""
    pass


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "import": "regscale.integrations.public.criticality_updater.update_control_criticality",
    },
    name="criticality_updater",
)
def criticality_updater():
    """
    Update the criticality of security controls in the catalog.
    """


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "populate_controls": "regscale.integrations.public.emass.populate_workbook",
        "import_slcm": "regscale.integrations.public.emass.import_slcm",
    },
    name="emass",
)
def emass():
    """Performs bulk processing of eMASS files (Upload trusted data only)."""
    pass


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "sort_control_ids": "regscale.integrations.public.nist_catalog.sort_control_ids",
    },
    name="nist",
)
def nist():
    """Sort the controls of a catalog in RegScale."""
    pass


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "version": "regscale.integrations.public.oscal.version",
        "component": "regscale.integrations.public.oscal.upload_component",
        "profile": "regscale.integrations.public.oscal.profile",
        "catalog": "regscale.integrations.public.oscal.catalog",
    },
    name="oscal",
)
def oscal():
    """Performs bulk processing of OSCAL files."""
    pass
