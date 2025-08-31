from __future__ import annotations

import json
from pathlib import Path

import pytest

from filevisualization.core import visualize_data

SAMPLE = {"a": 1, "b": [1, 2, {"c": True}]}


def test_export_dot(tmp_path: Path):
    out = tmp_path / "g.dot"
    visualize_data(SAMPLE, format="graphviz", export_dot=out)
    text = out.read_text(encoding="utf-8")
    # minimal golden assertions
    assert text.startswith("digraph")
    assert "n1" in text and "shape" in text


def test_export_json_graph(tmp_path: Path):
    out = tmp_path / "g.json"
    visualize_data(SAMPLE, format="graphviz", export_json_graph=out)
    obj = json.loads(out.read_text(encoding="utf-8"))
    assert "nodes" in obj and "links" in obj
    assert any(n.get("label") == "dict" for n in obj["nodes"])  # root node