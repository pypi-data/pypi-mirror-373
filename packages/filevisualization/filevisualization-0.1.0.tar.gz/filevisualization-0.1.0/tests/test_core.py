from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from filevisualization.core import load_file, visualize_data


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


def test_load_json(tmp_path: Path):
    p = _write(tmp_path, "a.json", json.dumps({"a": 1, "b": [1, 2]}))
    data = load_file(p)
    assert isinstance(data, dict)
    assert data["a"] == 1


def test_load_yaml(tmp_path: Path):
    p = _write(tmp_path, "a.yaml", "a: 1\nb:\n  - 1\n  - 2\n")
    data = load_file(p)
    assert data["a"] == 1


def test_load_toml(tmp_path: Path):
    p = _write(tmp_path, "a.toml", "a=1\n[b]\nc=2\n")
    data = load_file(p)
    assert data["a"] == 1
    assert data["b"]["c"] == 2


def test_load_xml(tmp_path: Path):
    root = ET.Element("root")
    ch = ET.SubElement(root, "child", {"x": "1"})
    ch.text = "hello"
    path = tmp_path / "a.xml"
    ET.ElementTree(root).write(path, encoding="utf-8")
    data = load_file(path)
    assert data["_tag"] == "root"
    assert data["_children"][0]["_attributes"]["x"] == "1"


def test_visualize_tree_prints(capsys):
    data = {"a": 1, "b": [1, 2, {"c": True}]}
    visualize_data(data, format="tree")
    out = capsys.readouterr().out
    assert "a: 1" in out or out  # ensure printed something


def test_visualize_mindmap_dot(capsys):
    data = {"a": 1, "b": [1, 2, {"c": True}]}
    visualize_data(data, format="mindmap")
    out = capsys.readouterr().out
    assert "digraph" in out


def test_graphviz_layouts_print_dot(capsys):
    data = {"a": 1, "b": [1]}
    # hierarchical TB
    visualize_data(data, format="graphviz", layout="hierarchical")
    assert "digraph" in capsys.readouterr().out
    # radial (twopi)
    visualize_data(data, format="graphviz", layout="radial")
    assert "digraph" in capsys.readouterr().out


def test_plotly_if_installed(tmp_path):
    data = {"a": 1, "b": [1]}
    try:
        from filevisualization.core import visualize_data as _viz
        _viz(data, format="plotly", output=str(tmp_path/"p.html"))
    except RuntimeError as e:
        # plotly not installed
        assert "Plotly is not installed" in str(e)


def test_pyvis_if_installed(tmp_path):
    data = {"a": 1, "b": [1]}
    try:
        from filevisualization.core import visualize_data as _viz
        _viz(data, format="pyvis", output=str(tmp_path/"p.html"))
    except RuntimeError as e:
        assert "pyvis is not installed" in str(e)
