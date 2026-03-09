"""Media management commands."""

from __future__ import annotations

import typer

from ankicli.connection import open_collection
from ankicli.output import print_error, print_single, print_success, print_table

app = typer.Typer(no_args_is_help=True)


def _get_state():
    from ankicli.main import state
    return state


@app.command()
def check() -> None:
    """Check media integrity (find missing/unused files)."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        output = col.media.check()
        data = {
            "missing": len(output.missing),
            "unused": len(output.unused),
            "renamed": len(output.renamed) if hasattr(output, "renamed") else 0,
            "dirs_exist": len(output.dirs_exist) if hasattr(output, "dirs_exist") else 0,
            "oversize": len(output.oversize) if hasattr(output, "oversize") else 0,
        }
        print_single(data, title="Media Check")
        if output.missing:
            print_table(
                [{"file": f} for f in output.missing[:20]],
                title=f"Missing files (showing {min(20, len(output.missing))} of {len(output.missing)})",
            )
        if output.unused:
            print_table(
                [{"file": f} for f in output.unused[:20]],
                title=f"Unused files (showing {min(20, len(output.unused))} of {len(output.unused)})",
            )


@app.command()
def add(file: str = typer.Argument(..., help="File path to add to media collection")) -> None:
    """Add a file to the media collection."""
    s = _get_state()
    from pathlib import Path
    if not Path(file).exists():
        print_error(f"File not found: {file}")
        raise typer.Exit(1)

    with open_collection(s.profile, s.path) as col:
        fname = col.media.add_file(file)
        print_success(f"Added media file as '{fname}'")


@app.command()
def trash(files: str = typer.Argument(..., help="Comma-separated file names to trash")) -> None:
    """Move media files to trash."""
    s = _get_state()
    fnames = [f.strip() for f in files.split(",") if f.strip()]
    with open_collection(s.profile, s.path) as col:
        col.media.trash_files(fnames)
        print_success(f"Trashed {len(fnames)} file(s)")


@app.command("empty-trash")
def empty_trash() -> None:
    """Permanently delete trashed media files."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        col.media.empty_trash()
        print_success("Media trash emptied")


@app.command("restore-trash")
def restore_trash() -> None:
    """Restore trashed media files."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        col.media.restore_trash()
        print_success("Media trash restored")
