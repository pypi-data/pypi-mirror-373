"""Generate a click group object."""

import matplotlib.pyplot as plt
import networkx as nx

from regscale.models.click_models import ClickGroup, ClickCommand


def plot_click_group(group: ClickGroup):
    G = nx.DiGraph()

    def add_node(cmd, parent=None):
        G.add_node(cmd.name)
        if parent is not None:
            G.add_edge(parent.name, cmd.name)
        if isinstance(cmd, ClickCommand):
            for param in cmd.params:
                G.add_node(param.name)
                G.add_edge(cmd.name, param.name)
        elif isinstance(cmd, ClickGroup):
            for subcmd in cmd.commands:
                add_node(subcmd, cmd)

    add_node(group)
    nx.draw(G, with_labels=True)
    plt.show()


if __name__ == "__main__":
    from regscale.regscale import cli

    click_group = ClickGroup.from_group(cli, include_callback=True)
    print(click_group.json())
    plot_click_group(click_group)
