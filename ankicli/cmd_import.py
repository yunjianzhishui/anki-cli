"""Import commands."""

from __future__ import annotations

import typer

from ankicli.connection import open_collection
from ankicli.output import print_error, print_single, print_success, print_table

app = typer.Typer(no_args_is_help=True)


def _get_state():
    from ankicli.main import state
    return state


@app.command()
def apkg(
    path: str = typer.Argument(..., help="Path to .apkg file"),
) -> None:
    """Import an Anki package (.apkg)."""
    s = _get_state()
    from pathlib import Path as P
    if not P(path).exists():
        print_error(f"File not found: {path}")
        raise typer.Exit(1)

    with open_collection(s.profile, s.path) as col:
        from anki.collection import ImportAnkiPackageRequest, ImportAnkiPackageOptions
        request = ImportAnkiPackageRequest(
            package_path=path,
            options=ImportAnkiPackageOptions(
                merge_notetypes=True,
                update_notes=True,
                update_notetypes=True,
                with_scheduling=True,
                with_deck_configs=True,
            ),
        )
        result = col.import_anki_package(request)
        data = {
            "new_notes": result.log.new_notes_count if hasattr(result.log, "new_notes_count") else "?",
            "updated_notes": result.log.updated_notes_count if hasattr(result.log, "updated_notes_count") else "?",
            "duplicate_notes": result.log.duplicate_notes_count if hasattr(result.log, "duplicate_notes_count") else "?",
        }
        print_single(data, title=f"Imported: {path}")


@app.command()
def colpkg(
    path: str = typer.Argument(..., help="Path to .colpkg file"),
) -> None:
    """Import a collection package (.colpkg) — replaces current collection!"""
    s = _get_state()
    from pathlib import Path as P
    if not P(path).exists():
        print_error(f"File not found: {path}")
        raise typer.Exit(1)

    typer.confirm("This will REPLACE your entire collection. Continue?", abort=True)

    with open_collection(s.profile, s.path) as col:
        from anki.collection import ImportAnkiPackageRequest, ImportAnkiPackageOptions
        request = ImportAnkiPackageRequest(
            package_path=path,
            options=ImportAnkiPackageOptions(
                merge_notetypes=True,
                update_notes=True,
                update_notetypes=True,
                with_scheduling=True,
                with_deck_configs=True,
            ),
        )
        col.import_anki_package(request)
        print_success(f"Imported collection from {path}")


@app.command()
def csv(
    path: str = typer.Argument(..., help="Path to CSV file"),
    deck: str = typer.Option(None, "--deck", "-d", help="Target deck name"),
    notetype: str = typer.Option(None, "--type", "-t", help="Note type name"),
) -> None:
    """Import a CSV file."""
    s = _get_state()
    from pathlib import Path as P
    if not P(path).exists():
        print_error(f"File not found: {path}")
        raise typer.Exit(1)

    with open_collection(s.profile, s.path) as col:
        metadata = col.get_csv_metadata(path, delimiter=None)
        if deck:
            did = col.decks.id_for_name(deck)
            if did:
                metadata.deck_id = did
        if notetype:
            mid = col.models.id_for_name(notetype)
            if mid:
                metadata.notetype_id = mid

        from anki.collection import ImportCsvRequest
        request = ImportCsvRequest(path=path, metadata=metadata)
        result = col.import_csv(request)
        print_success(f"Imported CSV from {path}")


@app.command("json")
def import_json(
    path: str = typer.Argument(..., help="Path to JSON file"),
) -> None:
    """Import an Anki JSON file."""
    s = _get_state()
    from pathlib import Path as P
    if not P(path).exists():
        print_error(f"File not found: {path}")
        raise typer.Exit(1)

    with open_collection(s.profile, s.path) as col:
        col.import_json_file(path)
        print_success(f"Imported JSON from {path}")


@app.command("csv-preview")
def csv_preview(
    path: str = typer.Argument(..., help="Path to CSV file"),
) -> None:
    """Preview CSV metadata (delimiter, columns, mapping)."""
    s = _get_state()
    from pathlib import Path as P
    if not P(path).exists():
        print_error(f"File not found: {path}")
        raise typer.Exit(1)

    with open_collection(s.profile, s.path) as col:
        metadata = col.get_csv_metadata(path, delimiter=None)
        data = {
            "delimiter": metadata.delimiter,
            "is_html": metadata.is_html,
            "notetype_id": metadata.notetype_id,
            "deck_id": metadata.deck_id,
            "columns": len(metadata.column_labels) if hasattr(metadata, "column_labels") else "?",
            "preview_rows": len(metadata.preview) if hasattr(metadata, "preview") else "?",
        }
        print_single(data, title=f"CSV Preview: {path}")
