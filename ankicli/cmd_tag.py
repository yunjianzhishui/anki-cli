"""Tag management commands."""

from __future__ import annotations

import typer

from ankicli.connection import open_collection
from ankicli.output import print_error, print_success, print_table, print_tree, is_json_mode, print_json

app = typer.Typer(no_args_is_help=True)


def _get_state():
    from ankicli.main import state
    return state


@app.command("list")
def tag_list() -> None:
    """List all tags."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        tags = col.tags.all()
        rows = [{"tag": t} for t in tags]
        print_table(rows, title=f"Tags ({len(tags)} total)")


@app.command("tree")
def tag_tree() -> None:
    """Show tags as a hierarchy tree."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        tree = col.tags.tree()

        def node_to_dict(node) -> dict:
            result = {"name": node.name}
            if node.children:
                result["children"] = [node_to_dict(c) for c in node.children]
            return result

        data = [node_to_dict(c) for c in tree.children]
        if is_json_mode():
            print_json(data)
        else:
            print_tree(data, title="Tag Tree")


@app.command()
def add(
    note_ids: str = typer.Argument(..., help="Comma-separated note IDs"),
    tags: str = typer.Option(..., "--tags", "-t", help="Space-separated tags to add"),
) -> None:
    """Add tags to notes."""
    s = _get_state()
    nids = [int(x.strip()) for x in note_ids.split(",") if x.strip()]
    with open_collection(s.profile, s.path) as col:
        col.tags.bulk_add(nids, tags)
        print_success(f"Added tags '{tags}' to {len(nids)} note(s)")


@app.command()
def remove(
    note_ids: str = typer.Argument(..., help="Comma-separated note IDs"),
    tags: str = typer.Option(..., "--tags", "-t", help="Space-separated tags to remove"),
) -> None:
    """Remove tags from notes."""
    s = _get_state()
    nids = [int(x.strip()) for x in note_ids.split(",") if x.strip()]
    with open_collection(s.profile, s.path) as col:
        col.tags.bulk_remove(nids, tags)
        print_success(f"Removed tags '{tags}' from {len(nids)} note(s)")


@app.command()
def rename(
    old: str = typer.Argument(..., help="Current tag name"),
    new: str = typer.Argument(..., help="New tag name"),
) -> None:
    """Rename a tag."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        col.tags.rename(old, new)
        print_success(f"Renamed tag '{old}' -> '{new}'")


@app.command()
def delete(tag: str = typer.Argument(..., help="Tag to delete")) -> None:
    """Delete a tag from all notes."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        col.tags.remove(tag)
        print_success(f"Deleted tag '{tag}'")


@app.command("clear-unused")
def clear_unused() -> None:
    """Remove tags that are not used by any notes."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        col.tags.clear_unused_tags()
        print_success("Cleared unused tags")
