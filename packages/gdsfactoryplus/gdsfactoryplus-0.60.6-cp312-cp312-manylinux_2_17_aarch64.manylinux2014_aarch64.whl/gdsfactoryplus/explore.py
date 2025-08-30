"""PDK exploration utilities."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from contextlib import suppress
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import gdsfactory as gf
    import gdsfactory.typings as gft
    import matplotlib.pyplot as plt
    import networkx as nx
    from natsort import natsorted
    from tqdm import tqdm

    import gdsfactoryplus.core.shared as gfp_shared

    _CellDict = dict[str, gft.ComponentFactory]
else:
    from gdsfactoryplus.lazy import lazy_import

    gf = lazy_import("gdsfactory")
    gft = lazy_import("gdsfactory.typings")
    plt = lazy_import("matplotlib.pyplot")
    nx = lazy_import("networkx")
    natsorted = lazy_import("natsort", "natsorted")
    tqdm = lazy_import("tqdm", "tqdm")
    gfp_shared = lazy_import("gdsfactoryplus.core.shared")
    _CellDict = Any

__all__ = [
    "classify_cells",
    "get_pdk_graph",
    "get_top_level_cells",
    "plot_pdk_relations",
]


def get_pdk_graph() -> nx.DiGraph:
    """Get a graph of all cells and their dependencies in the PDK."""
    g = nx.DiGraph()
    pdk = gf.get_active_pdk()
    _range = tqdm(list(pdk.cells))
    for name in _range:
        c = _get_maybe_c(name)
        if c is None:
            continue
        net = _get_net(name)
        insts = net.get("instances", {})
        comp_set = set()
        for inst in insts.values():
            if isinstance(inst, str):
                comp_set.add(inst)
            else:
                comp_set.add(inst.get("component", ""))
        comps = [c for c in natsorted(comp_set) if c]
        if comps:
            g.add_node(name, ports=_get_port_names(name), is_fixed=_is_fixed(name))
            for cname in comps:
                g.add_node(
                    cname, ports=_get_port_names(cname), is_fixed=_is_fixed(cname)
                )
                g.add_edge(name, cname)
        else:
            g.add_node(name, ports=_get_port_names(name), is_fixed=_is_fixed(name))
    return g


def _find_without_ports(g: nx.DiGraph) -> list[str]:
    """Find cells without ports in the pdk graph."""
    return natsorted(
        [n for n, attr in g.nodes(data=True) if len(attr.get("ports", [])) < 2]
    )


def _find_unconnected(g: nx.DiGraph) -> list[str]:
    """Find cells without any other dependencies in the pdk."""
    return natsorted(nx.isolates(g))


def _find_sinks(g: nx.DiGraph) -> list[str]:
    """Find top level cells in the pdk."""
    return natsorted([n for n in g.nodes() if g.out_degree(n) == 0])


def _find_fixed(g: nx.DiGraph) -> list[str]:
    """Find fixed cells in the pdk."""
    return natsorted([n for n, attr in g.nodes(data=True) if attr.get("is_fixed")])


def _find_composite(g: nx.DiGraph) -> list[str]:
    """Find composite cells in the pdk."""
    return natsorted([n for n in g.nodes() if g.out_degree(n) != 0])


def _find_good_sinks(g: nx.DiGraph) -> list[str]:
    """Find top level cells with enough ports in the pdk."""
    g = g.copy()
    without_ports = _find_without_ports(g)
    g.remove_nodes_from(without_ports)
    return _find_sinks(g)


def _get_node_colors(
    g: nx.DiGraph,
    good_color: str = "#00ff0033",
    composite_color: str = "#0000ff33",
    no_ports_color: str = "#ff000033",
    is_fixed_color: str = "#ffff0033",
    *,
    reverse: bool = False,
) -> list[str]:
    """Color the nodes in the pdk graph."""
    if reverse:
        _g = g.copy().reverse()
        without_ports = _find_without_ports(_g)
        sinks = _find_good_sinks(_g)
        is_fixed = _find_fixed(_g)
    else:
        without_ports = _find_without_ports(g)
        sinks = _find_good_sinks(g)
        is_fixed = _find_fixed(g)

    return [
        (
            no_ports_color
            if label in without_ports
            else (
                (is_fixed_color if label in is_fixed else good_color)
                if label in sinks
                else (composite_color)
            )
        )
        for label in g.nodes
    ]


def get_top_level_cells(
    g: nx.DiGraph, *, no_fixed: bool = True, reverse: bool = False
) -> list[str]:
    """Get top level cells in th epdk graph with possibility to filer out some."""
    colors = _get_node_colors(
        g,
        reverse=reverse,
        good_color="green",
        composite_color="red",
        no_ports_color="red",
        is_fixed_color=("red" if no_fixed else "green"),
    )
    return [n for n, c in zip(g.nodes, colors, strict=False) if c == "green"]


def plot_pdk_relations() -> None:
    """Plot PDK releationships with matplotlib."""
    g = get_pdk_graph()
    # g.remove_nodes_from(_find_fixed(g))
    # g.remove_nodes_from(_find_without_ports(g))
    # g.remove_nodes_from(_find_composite(g))
    node_colors = _get_node_colors(g)
    pos = nx.nx_agraph.graphviz_layout(g, prog="circo")  # 'dot', 'neato', 'circo', ...
    plt.figure(figsize=(10, 10))
    nx.draw(
        g,
        pos,
        with_labels=True,
        node_color=node_colors,
        node_size=1000,
        font_size=6,
        arrows=True,
    )


def classify_cells(pdk: gf.Pdk) -> tuple[_CellDict, _CellDict, _CellDict]:
    """Classify cells."""
    pcells: _CellDict = {}  # Parametric Cells
    fcells: _CellDict = {}  # Fixed Cells
    ocells: _CellDict = {}  # Other Cells
    for name, f in pdk.cells.items():
        if _num_args(f) > 0:
            try:
                c = f()
                ps = [p.name for p in c.ports]
            except Exception:  # noqa: BLE001
                ocells[name] = f
                continue
            if len(ps) > 1:
                pcells[name] = f
            else:
                ocells[name] = f
        else:
            try:
                c = f()
                ps = [p.name for p in c.ports]
            except Exception:  # noqa: BLE001
                ocells[name] = f
                continue
            if len(ps) > 1:
                fcells[name] = f
            else:
                ocells[name] = f
    return pcells, fcells, ocells


def _num_args(f: Callable) -> int:
    return len(inspect.signature(f).parameters)


def _get_maybe_f(name: str) -> gf.typings.ComponentFactory | None:
    pdk = gf.get_active_pdk()
    return pdk.cells.get(name, None)


def _get_maybe_c(name: str) -> gf.Component | None:
    with suppress(Exception):
        return gfp_shared.build_component_with_inserted_defaults(name)
    return None


def _get_net(name: str) -> dict:
    c = _get_maybe_c(name)
    if c is None:
        return {}
    try:
        return c.get_netlist()
    except Exception:  # noqa: BLE001
        return {}


def _get_port_names(name: str) -> tuple[str, ...]:
    c = _get_maybe_c(name)
    if not c:
        return ()
    return tuple((p.name or "") for p in c.ports)


def _is_fixed(name: str) -> bool:
    c = _get_maybe_c(name)
    if not c:
        return True
    f = _get_maybe_f(name)
    if not f:
        return True
    return _num_args(f) < 2
