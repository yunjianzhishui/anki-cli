"""Database maintenance commands."""

from __future__ import annotations

import os

import typer

from ankicli.connection import open_collection, detect_collection_path, detect_anki_base
from ankicli.output import print_error, print_single, print_success

app = typer.Typer(no_args_is_help=True)


def _get_state():
    from ankicli.main import state
    return state


@app.command()
def check() -> None:
    """Run full database integrity check and repair."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        result, ok = col.fix_integrity()
        if ok:
            print_success(f"Database OK\n{result}")
        else:
            print_error(f"Issues found:\n{result}")


@app.command()
def optimize() -> None:
    """Optimize database (VACUUM + ANALYZE)."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        col.optimize()
        print_success("Database optimized")


@app.command()
def backup(
    dir: str = typer.Option(None, "--dir", "-d", help="Backup directory (default: Anki's backup folder)"),
    force: bool = typer.Option(True, "--force/--no-force", help="Force backup even if recent"),
) -> None:
    """Create a collection backup."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        backup_dir = dir
        if not backup_dir:
            col_path = s.path or detect_collection_path(s.profile)
            backup_dir = os.path.join(os.path.dirname(col_path), "backups")
            os.makedirs(backup_dir, exist_ok=True)

        created = col.create_backup(
            backup_folder=backup_dir,
            force=force,
            wait_for_completion=True,
        )
        if created:
            print_success(f"Backup created in {backup_dir}")
        else:
            print_success("No changes since last backup; skipped")


@app.command()
def info() -> None:
    """Show database information."""
    s = _get_state()
    col_path = s.path or detect_collection_path(s.profile)
    size_mb = os.path.getsize(col_path) / (1024 * 1024)

    with open_collection(s.profile, s.path) as col:
        data = {
            "path": col.path,
            "size": f"{size_mb:.2f} MB",
            "profile": s.profile,
            "scheduler": f"v{col.sched_ver()}" + (" (v3)" if col.v3_scheduler() else ""),
            "cards": col.card_count(),
            "notes": col.note_count(),
            "decks": col.decks.count(),
            "schema_changed": col.schema_changed(),
        }
        print_single(data, title="Database Info")
