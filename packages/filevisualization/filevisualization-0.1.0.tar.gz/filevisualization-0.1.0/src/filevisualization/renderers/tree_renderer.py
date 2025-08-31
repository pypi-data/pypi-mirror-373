from __future__ import annotations

from typing import Any

from rich.text import Text
from rich.tree import Tree

from ..style_utils import icon_for, kind_of
from ..styles import get_theme


def _label_for_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def build_rich_tree(tree: Tree, data: Any, *, key: str | None = None, theme: str | None = None) -> None:
    """Recursively append nodes to a rich Tree from Python nested data.

    Supports dict, list/tuple, and scalars. Optionally includes the key label.
    """
    if isinstance(data, dict):
        label = (key if key is not None else "object") + f" {icon_for('dict')}"
        th = get_theme(theme)
        node = tree.add(Text(f"{label} (dict)", style=f"bold {th.node_border}"))
        for k, v in data.items():
            build_rich_tree(node, v, key=str(k), theme=theme)
    elif isinstance(data, (list, tuple)):
        label = (key if key is not None else "array") + f" {icon_for('list')}"
        th = get_theme(theme)
        node = tree.add(Text(f"{label} (list[{len(data)}])", style=f"bold {th.node_border}"))
        for idx, v in enumerate(data):
            build_rich_tree(node, v, key=f"[{idx}]", theme=theme)
    else:
        # scalar
        k = kind_of(data)
        label = (key if key is not None else "value") + f" {icon_for(k)}"
        node_label = _label_for_scalar(data)
        th = get_theme(theme)
        tree.add(Text(f"{label}: ", style=f"bold {th.node_border}") + Text(str(node_label), style=th.node_font))
