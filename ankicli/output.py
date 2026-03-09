"""Unified output formatting: human-readable tables or JSON."""

from __future__ import annotations

import json
import sys
from typing import Any, Sequence

from ankicli import i18n

_json_mode = False


def set_json_mode(enabled: bool) -> None:
    global _json_mode
    _json_mode = enabled


def is_json_mode() -> bool:
    return _json_mode


def print_json(data: Any) -> None:
    """Print data as JSON to stdout."""
    print(json.dumps(data, ensure_ascii=False, indent=2, default=str))


def print_table(
    rows: Sequence[dict[str, Any]],
    columns: Sequence[str] | None = None,
    title: str | None = None,
) -> None:
    """Print rows as a rich table, or as JSON if --json is active."""
    if _json_mode:
        print_json(rows)
        return

    from rich.console import Console
    from rich.table import Table

    console = Console()
    if not rows:
        console.print(f"[dim]{title + ': ' if title else ''}(empty)[/dim]")
        return

    cols = columns or list(rows[0].keys())
    table = Table(title=title, show_lines=False)
    for col in cols:
        table.add_column(col)
    for row in rows:
        table.add_row(*[str(row.get(c, "")) for c in cols])
    console.print(table)


def print_tree(data: Any, title: str | None = None) -> None:
    """Print a tree structure."""
    if _json_mode:
        print_json(data)
        return

    from rich.console import Console
    from rich.tree import Tree

    console = Console()
    tree = Tree(title or "Anki")
    _build_tree(tree, data)
    console.print(tree)


def _build_tree(parent: Any, nodes: Any) -> None:
    if isinstance(nodes, list):
        for node in nodes:
            _build_tree(parent, node)
    elif isinstance(nodes, dict):
        name = nodes.get("name", "?")
        info_parts = []
        for k, v in nodes.items():
            if k not in ("name", "children"):
                info_parts.append(f"{k}={v}")
        label = name
        if info_parts:
            label += f"  [dim]({', '.join(info_parts)})[/dim]"
        branch = parent.add(label)
        for child in nodes.get("children", []):
            _build_tree(branch, child)


def print_single(data: dict[str, Any], title: str | None = None) -> None:
    """Print a single record as key-value pairs, or JSON."""
    if _json_mode:
        print_json(data)
        return

    from rich.console import Console
    from rich.table import Table

    console = Console()
    table = Table(title=title, show_header=False)
    table.add_column("Key", style="bold")
    table.add_column("Value")
    for k, v in data.items():
        table.add_row(str(k), str(v))
    console.print(table)


def print_success(message: str) -> None:
    if _json_mode:
        print_json({"status": "ok", "message": message})
        return
    from rich.console import Console
    Console().print(f"[green]{i18n._('ok')}[/green] {message}")


def print_error(message: str) -> None:
    if _json_mode:
        print_json({"status": "error", "message": message})
    else:
        print(f"{i18n._('error')}: {message}", file=sys.stderr)
