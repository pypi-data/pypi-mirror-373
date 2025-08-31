from __future__ import annotations

from typing import Any

import plotly.graph_objects as go

from ..style_utils import kind_of, plotly_symbol_for
from ..styles import get_theme


def _flatten_edges(
    data: Any,
    parent: str | None,
    edges: list[tuple[str, str]],
    labels: dict[str, str],
    counter: dict[str, int],
) -> str:
    counter["i"] += 1
    node_id = f"n{counter['i']}"
    labels[node_id] = _node_label(data)
    if parent:
        edges.append((parent, node_id))

    if isinstance(data, dict):
        for k, v in data.items():
            child_id = _flatten_edges(v, node_id, edges, labels, counter)
            labels[child_id] = f"{k}: {labels[child_id]}"
    elif isinstance(data, (list, tuple)):
        for idx, v in enumerate(data):
            child_id = _flatten_edges(v, node_id, edges, labels, counter)
            labels[child_id] = f"[{idx}]: {labels[child_id]}"
    return node_id


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


def build_plotly_figure(data: Any, *, theme: str | None = None) -> go.Figure:
    th = get_theme(theme)
    # Build a simple tree layout using networkx-like layering (manual)
    edges: list[tuple[str, str]] = []
    labels: dict[str, str] = {}
    counter = {"i": 0}
    root_id = _flatten_edges(data, None, edges, labels, counter)

    # Simple layered positions by BFS
    from collections import defaultdict, deque
    children: dict[str, list[str]] = defaultdict(list)
    indeg: dict[str, int] = defaultdict(int)
    nodes: set[str] = set(labels.keys())
    for u, v in edges:
        children[u].append(v)
        indeg[v] += 1
    nodes.add(u)
    nodes.add(v)
    levels = {root_id: 0}
    q = deque([root_id])
    while q:
        u = q.popleft()
        for v in children[u]:
            levels[v] = levels[u] + 1
            q.append(v)

    by_level = defaultdict(list)
    for n, lv in levels.items():
        by_level[lv].append(n)

    pos = {}
    max_w = 0
    for lv, ns in by_level.items():
        w = len(ns)
        max_w = max(max_w, w)
        for i, n in enumerate(ns):
            # center horizontally per level
            x = i - (w - 1) / 2
            y = -lv
            pos[n] = (x, y)

    xs, ys, texts = [], [], []
    symbols = []
    for n in nodes:
        x, y = pos.get(n, (0, 0))
        xs.append(x)
        ys.append(y)
        texts.append(labels[n])
        # infer symbol by simple heuristic: look up original label suffix
        lbl = labels[n]
        if ":" in lbl:
            val = lbl.split(":", 1)[1].strip()
        else:
            val = lbl
        symbols.append(plotly_symbol_for(kind_of(val)))

    # Scatter for nodes
    node_trace = go.Scatter(
        x=xs, y=ys, mode='markers+text', text=texts, textposition='top center',
    marker=dict(size=16, color=th.node_fill, opacity=0.95, line=dict(color=th.node_border, width=2), symbol=symbols),
        hoverinfo='text',
        textfont=dict(color=th.node_font)
    )

    # Edges as line segments
    exs, eys = [], []
    for u, v in edges:
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        exs += [x0, x1, None]
        eys += [y0, y1, None]
    edge_trace = go.Scatter(x=exs, y=eys, mode='lines', line=dict(color=th.edge_color, width=1.5))

    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor=th.background or 'white',
        paper_bgcolor=th.background or 'white',
        font=dict(family=th.font, color=th.node_font),
        margin=dict(l=20, r=20, t=20, b=20),
    )
    return fig
