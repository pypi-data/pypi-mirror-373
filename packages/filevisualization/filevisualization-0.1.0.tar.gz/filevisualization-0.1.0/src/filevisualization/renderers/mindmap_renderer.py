from __future__ import annotations

from typing import Any

from graphviz import Digraph

from ..style_utils import graphviz_shape_for, kind_of
from ..styles import get_theme


def _node_label(value: Any) -> str:
    if isinstance(value, dict):
        return "dict"
    if isinstance(value, list):
        return f"list[{len(value)}]"
    if isinstance(value, tuple):
        return f"tuple[{len(value)}]"
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def build_graphviz_digraph(data: Any, *, engine: str = "dot", rankdir: str | None = None, theme: str | None = None) -> Digraph:
    th = get_theme(theme)
    graph_attr = {
        "splines": "spline",
        "overlap": "false",
        **({"rankdir": rankdir} if rankdir else {}),
    }
    if th.background:
        graph_attr["bgcolor"] = th.background
    # Graphviz supports gradient via two fillcolors when style=filled and gradientangle set
    node_attr = {
        "shape": "box",
        "style": "rounded,filled",
        "color": th.node_border,
        "fontname": th.font,
        "fontsize": "10",
        "fontcolor": th.node_font,
        "fillcolor": th.node_fill,
    }
    if th.node_fill2:
        node_attr["fillcolor"] = f"{th.node_fill}:{th.node_fill2}"
        node_attr["gradientangle"] = str(th.gradientangle or 90)

    dot = Digraph("fileviz", engine=engine, graph_attr=graph_attr, node_attr=node_attr, edge_attr={
        "color": th.edge_color
    })

    counter = {"i": 0}

    def add_node(value: Any, parent_id: str | None, key: str | None = None) -> str:
        counter["i"] += 1
        node_id = f"n{counter['i']}"
        label_prefix = f"{key}: " if key is not None else ""
        k = kind_of(value)
        shape = graphviz_shape_for(k)
        dot.node(node_id, f"{label_prefix}{_node_label(value)}", shape=shape)
        if parent_id is not None:
            dot.edge(parent_id, node_id)

        if isinstance(value, dict):
            for k, v in value.items():
                add_node(v, node_id, str(k))
        elif isinstance(value, (list, tuple)):
            for idx, v in enumerate(value):
                add_node(v, node_id, f"[{idx}]")
        return node_id

    add_node(data, None, None)
    return dot
