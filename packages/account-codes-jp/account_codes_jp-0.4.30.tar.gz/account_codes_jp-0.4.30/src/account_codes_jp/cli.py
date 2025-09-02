import warnings
from collections.abc import Mapping, Sequence
from logging import basicConfig
from pathlib import Path
from typing import Annotated, Any, Literal

import cyclopts
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from cyclopts import Parameter
from matplotlib import patheffects
from networkx.readwrite.text import generate_network_text
from rich import print
from rich.logging import RichHandler

from ._blue_return import get_blue_return_accounts
from ._edinet import Industry, get_edinet_accounts

app = cyclopts.App(name="account-codes-jp")
app.meta.group_parameters = cyclopts.Group("Session Parameters", sort_key=0)


@app.command
def list(
    type: Literal["edinet", "blue-return"] = "edinet",
    industry: Industry | None = "一般商工業",
) -> None:
    """List accounts."""
    if type == "edinet":
        G = get_edinet_accounts(industry, debug_unique=True)
    elif type == "blue-return":
        G = get_blue_return_accounts()
    else:
        raise ValueError(f"Unknown account type: {type}")
    for n, d in G.nodes(data=True):
        if d["abstract"]:
            G.nodes[n]["label"] = f"[red]{d['label']}[/red]"
        if d["title"]:
            G.nodes[n]["label"] = f"{d['label']}[タイトル]"
        if d["total"]:
            G.nodes[n]["label"] = f"[yellow]{d['label']}[/yellow][計]"
        if d["account_type"]:
            G.nodes[n]["label"] = f"{d['label']}/[orange1]{d['account_type']}[/orange1]"
        if type == "edinet":
            G.nodes[n]["label"] = (
                f"{d['label']}/[green]{d['label_etax']}[/green]/"
                f"[sky_blue3]{d['prefix']}:{d['element']}[/sky_blue3]"
            )
    for i, line in enumerate(generate_network_text(G, with_labels=True)):
        if i <= 0:
            continue
        print(line)


def draw_networkx_labels_rotated(
    pos: Mapping[Any, Sequence[float]],
    labels: Mapping[Any, str],
    natural: bool = True,
    **kwargs: Any,
) -> None:
    """
    Draw networkx labels rotated.

    Parameters
    ----------
    pos : dict[Any, Sequence[float]]
        The positions of the nodes
    labels : dict[Any, str]
        The labels of the nodes
    natural : bool
        Whether to rotate the labels
        from left to right
        as much as possible, by default True
    **kwargs : Any
        Additional keyword arguments
        to pass to `plt.text`

    """
    # see nx.rescale_layout_dict() for how networkx converts the graphviz layout
    # if nx.rescale_layout_dict() is already applied, center could be (0, 0)
    center = np.mean([[pos[0], pos[1]] for pos in pos.values()], axis=0)
    for node, label in labels.items():
        x, y = pos[node]
        r = np.atan2(y - center[1], x - center[0])
        if natural:
            if r > np.pi / 2:
                r -= np.pi
            elif r < -np.pi / 2:
                r += np.pi
        plt.text(
            x,
            y,
            label,
            rotation=r * 180 / np.pi,
            ha="center",
            va="center",
            **kwargs,
        )


@app.command
def export(
    path: Path | None = None,
    industry: Industry | None = "一般商工業",
    type: Literal["edinet", "blue-return"] = "edinet",
    graphviz_layout: str = "sfdp",
    graphviz_args: str = "",
) -> None:
    """Export accounts."""
    if path is None:
        path = Path(type)
    import japanize_matplotlib

    japanize_matplotlib.japanize()
    if type == "edinet":
        plt.figure(figsize=(40, 40))
    else:
        plt.figure(figsize=(6.5, 6.5))

    # remove margins
    plt.box(False)
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0, wspace=0, hspace=0)

    # get accounts
    if type == "edinet":
        G = get_edinet_accounts(industry)
    elif type == "blue-return":
        G = get_blue_return_accounts()
    else:
        raise ValueError(f"Unknown account type: {type}")

    print("Generating layout...")
    try:
        layout = nx.nx_agraph.graphviz_layout(
            G, prog=graphviz_layout, args=graphviz_args
        )
    except Exception as e:
        warnings.warn(f"Failed to use graphviz layout: {e}", stacklevel=2)
        layout = nx.spring_layout(G)

    print("Drawing graph...")
    nx.draw_networkx_edges(G, layout, edge_color="white", width=3, arrowsize=1)
    nx.draw_networkx(
        G,
        layout,
        with_labels=False,
        node_color=[
            "black"
            if d["abstract"] is None
            else "red"
            if d["abstract"]
            else "lightblue"
            for n, d in G.nodes(data=True)
        ],
    )
    path_effects = [
        patheffects.withStroke(linewidth=3, foreground="white", capstyle="round")
    ]
    draw_networkx_labels_rotated(
        layout,
        nx.get_node_attributes(G, "label"),
        path_effects=path_effects,
    )
    plt.title(
        f"{'EDINET' if type == 'edinet' else '青色申告'}の勘定科目",
        path_effects=path_effects,
    )
    plt.tight_layout()
    plt.savefig(path.with_suffix(".jpg"), dpi=150)
    plt.savefig(path.with_suffix(".png"), transparent=True, dpi=150)


@app.meta.default
def _app_launcher(
    *tokens: Annotated[str, Parameter(show=False, allow_leading_hyphen=True)],
    verbose: bool = False,
) -> None:
    basicConfig(level="DEBUG" if verbose else "INFO", handlers=[RichHandler()])
    app(tokens)
