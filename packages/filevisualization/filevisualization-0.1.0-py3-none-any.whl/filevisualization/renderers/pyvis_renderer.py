from __future__ import annotations

import json
from typing import Any

from ..style_utils import icon_for, kind_of, pyvis_shape_for
from ..styles import get_theme

try:
    from pyvis.network import Network
except Exception:  # pragma: no cover
    Network = None


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


def build_pyvis_network(data: Any, *, theme: str | None = None) -> Any:
    if Network is None:  # fall back case
        raise RuntimeError("pyvis is not installed. Install with filevisualization[pyvis]")
    th = get_theme(theme)
    net = Network(height="800px", width="100%", directed=True, bgcolor=th.background or "#ffffff")
    # Apply themed options
    options = {
        "nodes": {
            "shape": "box",
            "color": {
                "background": th.node_fill,
                "border": th.node_border,
            },
            "font": {"color": th.node_font, "face": th.font},
            "borderWidth": 1,
        },
        "edges": {
            "color": {"color": th.edge_color},
            "smooth": True,
        },
        "layout": {"improvedLayout": True},
        "physics": {"stabilization": True},
    }
    net.set_options(json.dumps(options))

    counter = {"i": 0}

    def add_node(value: Any, parent: str | None, key: str | None = None) -> str:
        counter["i"] += 1
        node_id = f"n{counter['i']}"
        k = kind_of(value)
        label_prefix = f"{key}: " if key is not None else ""
        net.add_node(node_id, label=f"{label_prefix}{icon_for(k)} {_node_label(value)}", shape=pyvis_shape_for(k))
        if parent is not None:
            net.add_edge(parent, node_id)
        if isinstance(value, dict):
            for k, v in value.items():
                add_node(v, node_id, str(k))
        elif isinstance(value, (list, tuple)):
            for idx, v in enumerate(value):
                add_node(v, node_id, f"[{idx}]")
        return node_id

    add_node(data, None, None)
    return net
