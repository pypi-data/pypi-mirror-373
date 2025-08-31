from __future__ import annotations

import argparse
from pathlib import Path

from .core import run_diagnose, visualize_path


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="fileviz",
        description="Visualize structure of XML/JSON/YAML/TOML files",
    )
    p.add_argument("path", type=Path, nargs="?", help="Path to file")
    p.add_argument("--format", choices=["tree", "mindmap", "graphviz", "plotly", "pyvis"], default="tree")
    p.add_argument("--layout", type=str, default=None, help="Layout hint for graphviz: hierarchical/tree/tb/lr, radial/circle, force/spring")
    p.add_argument("--engine", type=str, default=None, help="Graphviz engine override: dot, neato, fdp, sfdp, twopi, circo, osage, patchwork")
    p.add_argument("--output", type=str, default=None, help="Output path (e.g. out.svg or out.html). For graphviz/mindmap: if missing, prints DOT. For plotly: writes HTML if provided, else prints JSON.")
    p.add_argument("--theme", type=str, default=None, help="Theme name: pastel (default), light, dark, kawaii, chic, modern, business, caution")
    # Diagnostics and data shaping options
    p.add_argument("--diagnose", action="store_true", help="Print environment diagnostics and exit")
    p.add_argument("--max-depth", type=int, default=None, help="Limit traversal depth (0=root only). Deeper nodes are summarized")
    p.add_argument("--include-keys", type=str, default=None, help="Comma-separated key substrings to include (others pruned). Applies to dict keys")
    p.add_argument("--exclude-keys", type=str, default=None, help="Comma-separated key substrings to exclude")
    p.add_argument("--prune-arrays", type=int, default=None, help="If set, arrays longer than N are truncated to first N elements with a summary tail")
    # Export multi-formats
    p.add_argument("--export-dot", type=Path, default=None, help="Export raw DOT source to file")
    p.add_argument("--export-json-graph", type=Path, default=None, help="Export nodes/links JSON graph to file")
    p.add_argument("--export-graphml", type=Path, default=None, help="Export GraphML to file")
    p.add_argument("--export-csv-edges", type=Path, default=None, help="Export edges CSV (source,target,label)")
    # Limits & streaming
    p.add_argument("--max-nodes", type=int, default=None, help="Hard cap on node count; rendering stops and warns after this many")
    p.add_argument("--max-edges", type=int, default=None, help="Hard cap on edge count; rendering stops and warns after this many")
    p.add_argument("--stream-json", action="store_true", help="Use streaming parser for large JSON (requires ijson)")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.diagnose:
        run_diagnose()
        return 0
    if args.path is None:
        raise SystemExit("error: PATH is required unless --diagnose is given")
    include_keys = [s for s in (args.include_keys.split(",") if args.include_keys else []) if s]
    exclude_keys = [s for s in (args.exclude_keys.split(",") if args.exclude_keys else []) if s]
    visualize_path(
        args.path,
        format=args.format,
        output=args.output,
        layout=args.layout,
        engine=args.engine,
        theme=args.theme,
        max_depth=args.max_depth,
        include_keys=include_keys or None,
        exclude_keys=exclude_keys or None,
        prune_arrays=args.prune_arrays,
        export_dot=args.export_dot,
        export_json_graph=args.export_json_graph,
        export_graphml=args.export_graphml,
        export_csv_edges=args.export_csv_edges,
        max_nodes=args.max_nodes,
        max_edges=args.max_edges,
        stream_json=args.stream_json,
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
