from __future__ import annotations

from typing import Any


def _clamp(n: int) -> int:
    return max(0, min(255, n))


def lighten(hex_color: str, amount: float = 0.2) -> str:
    """Lighten a #RRGGBB color by mixing with white.
    amount in [0,1]."""
    h = hex_color.lstrip('#')
    if len(h) != 6:
        return hex_color
    r = int(h[0:2], 16)
    g = int(h[2:4], 16)
    b = int(h[4:6], 16)
    r = _clamp(int(r + (255 - r) * amount))
    g = _clamp(int(g + (255 - g) * amount))
    b = _clamp(int(b + (255 - b) * amount))
    return f"#{r:02X}{g:02X}{b:02X}"


def kind_of(value: Any) -> str:
    if isinstance(value, dict):
        return "dict"
    if isinstance(value, list):
        return "list"
    if isinstance(value, tuple):
        return "tuple"
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, str):
        return "string"
    return "other"


def icon_for(kind: str) -> str:
    return {
        "dict": "🗂️",
        "list": "📚",
        "tuple": "📦",
        "string": "🔤",
        "number": "🔢",
        "bool": "🔘",
        "null": "∅",
    }.get(kind, "🔹")


def graphviz_shape_for(kind: str) -> str:
    return {
        "dict": "box",
        "list": "ellipse",
        "tuple": "ellipse",
        "string": "oval",
        "number": "circle",
        "bool": "diamond",
        "null": "oval",
    }.get(kind, "oval")


def plotly_symbol_for(kind: str) -> str:
    return {
        "dict": "square",
        "list": "triangle-up",
        "tuple": "triangle-up",
        "string": "circle",
        "number": "circle",
        "bool": "diamond",
        "null": "circle-open",
    }.get(kind, "circle")


def pyvis_shape_for(kind: str) -> str:
    return {
        "dict": "box",
        "list": "ellipse",
        "tuple": "ellipse",
        "string": "ellipse",
        "number": "dot",
        "bool": "diamond",
        "null": "dot",
    }.get(kind, "ellipse")
