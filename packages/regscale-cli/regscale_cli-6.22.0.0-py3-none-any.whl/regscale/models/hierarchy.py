"""Demonstrate the hierarchy via ClickGroup."""

from regscale.regscale import cli
from regscale.models.click_models import ClickGroup


REGSCALE_CLI = ClickGroup.from_group(cli, prefix="regscale")
REGSCALE_CLI_FLAT = REGSCALE_CLI.flatten()
