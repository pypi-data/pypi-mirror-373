"""Use the click methods to generate an importable click hierarchy."""

from regscale.regscale import cli
from regscale.utils.click_utils import process_click_group

REGSCALE_CLI = process_click_group(group=cli, prefix="regscale")

REGSCALE_CLI_SERIALIZABLE = process_click_group(group=cli)

if __name__ == "__main__":
    from pprint import pprint

    pprint(REGSCALE_CLI)
