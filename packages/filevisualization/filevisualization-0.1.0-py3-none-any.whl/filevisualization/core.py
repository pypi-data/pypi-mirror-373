from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Optional

try:
    from defusedxml import ElementTree as ET
except Exception:  # pragma: no cover
    import xml.etree.ElementTree as ET

yaml: Any
try:  # pragma: no cover
    import yaml as _yaml  # type: ignore
    yaml = _yaml
except Exception:  # pragma: no cover
    yaml = None

try:
    import tomllib as tomli  # Python 3.11+
except Exception:  # pragma: no cover
    try:
        import tomli
    except Exception:  # pragma: no cover
        tomli = None

from rich import print as rprint
from rich.console import Console
from rich.tree import Tree

from .renderers.mindmap_renderer import build_graphviz_digraph
from .renderers.tree_renderer import build_rich_tree

# Optional backends with explicit Optional typing
_build_plotly_figure: Optional[Callable[..., Any]]
try:  # pragma: no cover - optional dep
    from .renderers.plotly_renderer import build_plotly_figure as _build_plotly_figure
except Exception:  # pragma: no cover
    _build_plotly_figure = None

_build_pyvis_network: Optional[Callable[..., Any]]
try:  # pragma: no cover - optional dep
    from .renderers.pyvis_renderer import build_pyvis_network as _build_pyvis_network
except Exception:  # pragma: no cover
    _build_pyvis_network = None


@dataclass
class VisualizationResult:
    format: str  # tree | mindmap | graphviz
    output: str | None  # output path if written


def detect_format(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".json":
        return "json"
    if ext in {".yaml", ".yml"}:
        return "yaml"
    if ext == ".toml":
        return "toml"
    if ext == ".xml":
        return "xml"
    raise ValueError(f"Unsupported file extension: {ext}. Supported: .json, .yaml/.yml, .toml, .xml")


def load_file(path: str | Path, *, stream_json: bool | None = False) -> Any:
    p = Path(path)
    kind = detect_format(p)
    if kind == "json":
        if stream_json:
            try:
                import ijson
            except Exception as e:  # pragma: no cover
                raise RuntimeError("Streaming JSON requires 'ijson'. Install extras: pip install .[stream]") from e
            with p.open("rb") as f:
                # parse whole doc as one item
                data = next(ijson.items(f, "$"))
        else:
            data = json.loads(p.read_text(encoding="utf-8"))
    elif kind == "yaml":
        if yaml is None:
            raise RuntimeError("PyYAML is not installed")
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
    elif kind == "toml":
        if tomli is None:
            raise RuntimeError("tomli/tomllib is not available")
        data = tomli.loads(p.read_text(encoding="utf-8"))
    elif kind == "xml":
        data = _xml_to_nested(ET.parse(p).getroot())
    else:
        raise AssertionError
    return data


def _xml_to_nested(elem: ET.Element) -> Any:
    children = list(elem)
    node: dict[str, Any] = {"_tag": elem.tag}
    if elem.attrib:
        node["_attributes"] = dict(elem.attrib)
    if elem.text and elem.text.strip():
        node["_text"] = elem.text.strip()
    if children:
        node["_children"] = [_xml_to_nested(ch) for ch in children]
    return node


def _apply_filters(
    data: Any,
    *,
    max_depth: int | None = None,
    include_keys: Iterable[str] | None = None,
    exclude_keys: Iterable[str] | None = None,
    prune_arrays: int | None = None,
) -> Any:
    inc = list(include_keys or [])
    exc = list(exclude_keys or [])

    def key_allowed(k: str) -> bool:
        if inc and not any(s in k for s in inc):
            return False
        if exc and any(s in k for s in exc):
            return False
        return True

    def visit(obj: Any, depth: int) -> Any:
        if max_depth is not None and depth > max_depth:
            return "…(max-depth exceeded)"
        if isinstance(obj, dict):
            out: dict[str, Any] = {}
            for k, v in obj.items():
                if not key_allowed(str(k)):
                    continue
                out[str(k)] = visit(v, depth + 1)
            return out
        if isinstance(obj, (list, tuple)):
            seq = list(obj)
            if prune_arrays is not None and len(seq) > prune_arrays:
                kept = [visit(x, depth + 1) for x in seq[:prune_arrays]]
                kept.append(f"…({len(seq) - prune_arrays} more items truncated)")
                return kept
            return [visit(x, depth + 1) for x in seq]
        return obj

    return visit(data, 0)


def _enforce_caps(data: Any, *, max_nodes: int | None = None, max_edges: int | None = None) -> Any:
    if max_nodes is None and max_edges is None:
        return data
    node_count = 0
    edge_count = 0
    truncated = False

    def visit(obj: Any) -> Any:
        nonlocal node_count, edge_count, truncated
        if truncated:
            return "…(truncated)"
        node_count += 1
        if max_nodes is not None and node_count > max_nodes:
            truncated = True
            return "…(node cap exceeded)"
        if isinstance(obj, dict):
            out: dict[str, Any] = {}
            for k, v in obj.items():
                edge_count += 1
                if max_edges is not None and edge_count > max_edges:
                    truncated = True
                    out[str(k)] = "…(edge cap exceeded)"
                    break
                out[str(k)] = visit(v)
            return out
        if isinstance(obj, (list, tuple)):
            out_list = []
            for v in obj:
                edge_count += 1
                if max_edges is not None and edge_count > max_edges:
                    truncated = True
                    out_list.append("…(edge cap exceeded)")
                    break
                out_list.append(visit(v))
            return out_list
        return obj

    out = visit(data)
    if truncated:
        rprint(
            f"[yellow]Warning:[/] graph truncated (nodes={node_count}, edges={edge_count}). "
            "Consider increasing caps or using filters."
        )
    return out


def _to_edges_nodes(data: Any) -> tuple[list[tuple[int, int, str | None]], list[tuple[int, str]]]:
    edges: list[tuple[int, int, str | None]] = []
    nodes: list[tuple[int, str]] = []
    counter = 0

    def add_node(label: str) -> int:
        nonlocal counter
        counter += 1
        nid = counter
        nodes.append((nid, label))
        return nid

    def walk(obj: Any, parent: int | None, key: str | None) -> None:
        nid: int
        if isinstance(obj, dict):
            nid = add_node("dict")
            if parent is not None:
                edges.append((parent, nid, key))
            for k, v in obj.items():
                walk(v, nid, str(k))
            return
        if isinstance(obj, (list, tuple)):
            nid = add_node("list")
            if parent is not None:
                edges.append((parent, nid, key))
            for i, v in enumerate(obj):
                walk(v, nid, f"[{i}]")
            return
        nid = add_node(str(obj))
        if parent is not None:
            edges.append((parent, nid, key))

    walk(data, None, None)
    return edges, nodes


def _export_graph_formats(
    data: Any,
    *,
    export_dot: Path | None = None,
    export_json_graph: Path | None = None,
    export_graphml: Path | None = None,
    export_csv_edges: Path | None = None,
    engine: str = "dot",
    rankdir: str | None = None,
    theme: str | None = None,
) -> None:
    dot = build_graphviz_digraph(data, engine=engine, rankdir=rankdir, theme=theme)
    if export_dot:
        Path(export_dot).write_text(dot.source, encoding="utf-8")
    if export_graphml:
        edges, nodes = _to_edges_nodes(data)
        from xml.sax.saxutils import escape
        lines = [
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
            "<graphml xmlns=\"http://graphml.graphdrawing.org/xmlns\">",
            "  <graph edgedefault=\"directed\">",
        ]
        for nid, label in nodes:
            lines.append(f"    <node id=\"n{nid}\"><data key=\"label\">{escape(label)}</data></node>")
        for s, t, lbl in edges:
            attr = f" label=\"{escape(lbl)}\"" if lbl is not None else ""
            lines.append(f"    <edge source=\"n{s}\" target=\"n{t}\"{attr}/>")
        lines.append("  </graph>")
        lines.append("</graphml>")
        Path(export_graphml).write_text("\n".join(lines), encoding="utf-8")
    if export_json_graph:
        edges, nodes = _to_edges_nodes(data)
        obj = {
            "nodes": [{"id": f"n{nid}", "label": label} for nid, label in nodes],
            "links": [{"source": f"n{s}", "target": f"n{t}", "label": lbl} for s, t, lbl in edges],
        }
        Path(export_json_graph).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    if export_csv_edges:
        edges, _ = _to_edges_nodes(data)
        with Path(export_csv_edges).open("w", encoding="utf-8", newline="") as f:
            f.write("source,target,label\n")
            for s, t, lbl in edges:
                lab = "" if lbl is None else str(lbl).replace("\n", " ")
                f.write(f"n{s},n{t},\"{lab}\"\n")


def _detect_graphviz() -> tuple[bool, str | None]:
    try:
        try:
            from graphviz import backend
            v = backend.version()
            return True, v
        except Exception:
            return True, None
    except Exception as e:  # pragma: no cover
        return False, str(e)


def run_diagnose() -> None:
    import sys
    print("filevisualization diagnostics")
    print(f"Python: {sys.version.split()[0]}")
    try:
        import graphviz as _gv  # noqa: F401
        gv = True
    except Exception:
        gv = False
    print(f"graphviz: {'installed' if gv else 'missing'}")
    print(f"plotly: {'available' if _build_plotly_figure is not None else 'missing'}")
    print(f"pyvis: {'available' if _build_pyvis_network is not None else 'missing'}")
    ok, ver = _detect_graphviz()
    if ok:
        print(f"Graphviz 'dot': detected{f' (version {ver})' if ver else ''}")
    else:
        print("Graphviz 'dot': NOT detected")
        print("Windows対処: Graphvizをインストール後、dot.exeのパスをPATHに追加。PowerShellで 'dot -V' を実行して確認してください。")


def visualize_data(
    data: Any,
    format: str = "tree",
    output: str | None = None,
    *,
    layout: str | None = None,
    engine: str | None = None,
    theme: str | None = None,
    max_depth: int | None = None,
    include_keys: Iterable[str] | None = None,
    exclude_keys: Iterable[str] | None = None,
    prune_arrays: int | None = None,
    export_dot: Path | None = None,
    export_json_graph: Path | None = None,
    export_graphml: Path | None = None,
    export_csv_edges: Path | None = None,
    max_nodes: int | None = None,
    max_edges: int | None = None,
) -> VisualizationResult:
    # shaping and caps
    data = _apply_filters(
        data,
        max_depth=max_depth,
        include_keys=include_keys,
        exclude_keys=exclude_keys,
        prune_arrays=prune_arrays,
    )
    data = _enforce_caps(data, max_nodes=max_nodes, max_edges=max_edges)

    if format == "tree":
        tree = Tree("root")
        build_rich_tree(tree, data, theme=theme)
        Console().print(tree)
        return VisualizationResult(format=format, output=None)
    elif format in {"mindmap", "graphviz"}:
        eng = engine
        rankdir = None
        if layout:
            if layout in {"hierarchical", "tree", "tb", "lr"}:
                eng = eng or "dot"
                rankdir = "LR" if layout in {"lr"} else "TB"
            elif layout in {"radial", "circle"}:
                eng = eng or "twopi"
            elif layout in {"force", "spring"}:
                eng = eng or "sfdp"
        eng = eng or "dot"
        # Optionally export multiple formats
        if any(x is not None for x in (export_dot, export_json_graph, export_graphml, export_csv_edges)):
            _export_graph_formats(
                data,
                export_dot=export_dot,
                export_json_graph=export_json_graph,
                export_graphml=export_graphml,
                export_csv_edges=export_csv_edges,
                engine=eng,
                rankdir=rankdir,
                theme=theme,
            )
        dot = build_graphviz_digraph(data, engine=eng, rankdir=rankdir, theme=theme)
        if output:
            out_path = Path(output)
            ext = out_path.suffix.lower().lstrip('.')
            if not ext:
                ext = 'svg'
                out_path = out_path.with_suffix('.svg')
            try:
                data_bytes = dot.pipe(format=ext)
            except Exception as e:
                raise RuntimeError(
                    "Graphviz 実行に失敗しました。Graphviz 本体がインストールされ、PATHに dot.exe が通っているか確認してください（PowerShell: 'dot -V'）。\n"
                    "また、拡張子は svg/png/pdf などGraphviz対応のものを指定してください。\n"
                    f"詳細: {e}"
                ) from e
            out_path.write_bytes(data_bytes)
            return VisualizationResult(format=format, output=str(out_path))
        else:
            print(dot.source)
            return VisualizationResult(format=format, output=None)
    elif format == "plotly":
        if _build_plotly_figure is None:
            raise RuntimeError("Plotly is not installed. Install extras: pip install filevisualization[plotly]")
        fig = _build_plotly_figure(data, theme=theme)
        if output:
            if not str(output).lower().endswith(".html"):
                output = f"{output}.html"
            fig.write_html(output, include_plotlyjs="inline", full_html=True)
            return VisualizationResult(format=format, output=output)
        else:
            print(fig.to_json())
            return VisualizationResult(format=format, output=None)
    elif format == "pyvis":
        if _build_pyvis_network is None:
            raise RuntimeError("pyvis is not installed. Install extras: pip install filevisualization[pyvis]")
        net = _build_pyvis_network(data, theme=theme)
        if output:
            if not str(output).lower().endswith(".html"):
                output = f"{output}.html"
            net.write_html(output, open_browser=False, notebook=False)
            return VisualizationResult(format=format, output=output)
        else:
            import tempfile
            tmp = tempfile.mktemp(suffix=".html", prefix="fileviz_")
            net.write_html(tmp, open_browser=False, notebook=False)
            print(tmp)
            return VisualizationResult(format=format, output=tmp)
    else:
        raise ValueError("format must be one of 'tree', 'mindmap', 'graphviz', 'plotly', 'pyvis'")


def visualize_path(
    path: str | Path,
    format: str = "tree",
    output: str | None = None,
    *,
    layout: str | None = None,
    engine: str | None = None,
    theme: str | None = None,
    max_depth: int | None = None,
    include_keys: Iterable[str] | None = None,
    exclude_keys: Iterable[str] | None = None,
    prune_arrays: int | None = None,
    export_dot: Path | None = None,
    export_json_graph: Path | None = None,
    export_graphml: Path | None = None,
    export_csv_edges: Path | None = None,
    max_nodes: int | None = None,
    max_edges: int | None = None,
    stream_json: bool | None = None,
) -> VisualizationResult:
    data = load_file(path, stream_json=bool(stream_json))
    return visualize_data(
        data,
        format=format,
        output=output,
        layout=layout,
        engine=engine,
        theme=theme,
        max_depth=max_depth,
        include_keys=include_keys,
        exclude_keys=exclude_keys,
        prune_arrays=prune_arrays,
        export_dot=export_dot,
        export_json_graph=export_json_graph,
        export_graphml=export_graphml,
        export_csv_edges=export_csv_edges,
        max_nodes=max_nodes,
        max_edges=max_edges,
    )
