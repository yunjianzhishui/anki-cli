"""Export commands."""

from __future__ import annotations

import typer

from ankicli.connection import open_collection
from ankicli.output import print_error, print_success

app = typer.Typer(no_args_is_help=True)


def _get_state():
    from ankicli.main import state
    return state


@app.command()
def apkg(
    output: str = typer.Option(..., "--output", "-o", help="Output .apkg file path"),
    deck: str = typer.Option(None, "--deck", "-d", help="Deck to export (all if omitted)"),
    include_scheduling: bool = typer.Option(True, "--scheduling/--no-scheduling", help="Include scheduling info"),
    include_media: bool = typer.Option(True, "--media/--no-media", help="Include media files"),
    legacy: bool = typer.Option(False, "--legacy", help="Legacy .apkg format"),
) -> None:
    """Export a deck as .apkg package."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        from anki.collection import ExportAnkiPackageOptions, DeckIdLimit

        limit = None
        if deck:
            did = col.decks.id_for_name(deck)
            if not did:
                print_error(f"Deck '{deck}' not found")
                raise typer.Exit(1)
            limit = DeckIdLimit(deck_id=did)

        options = ExportAnkiPackageOptions(
            with_scheduling=include_scheduling,
            with_media=include_media,
            legacy=legacy,
        )
        count = col.export_anki_package(out_path=output, options=options, limit=limit)
        print_success(f"Exported {count} card(s) to {output}")


@app.command()
def colpkg(
    output: str = typer.Option(..., "--output", "-o", help="Output .colpkg file path"),
    include_media: bool = typer.Option(True, "--media/--no-media", help="Include media"),
    legacy: bool = typer.Option(False, "--legacy", help="Legacy format"),
) -> None:
    """Export entire collection as .colpkg."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        col.export_collection_package(output, include_media=include_media, legacy=legacy)
        print_success(f"Exported collection to {output}")


@app.command("notes-csv")
def notes_csv(
    output: str = typer.Option(..., "--output", "-o", help="Output CSV file path"),
    deck: str = typer.Option(None, "--deck", "-d", help="Deck to export"),
    with_html: bool = typer.Option(False, "--html", help="Include HTML tags"),
    with_tags: bool = typer.Option(True, "--tags/--no-tags", help="Include tags column"),
    with_deck: bool = typer.Option(False, "--with-deck", help="Include deck column"),
    with_notetype: bool = typer.Option(False, "--with-notetype", help="Include notetype column"),
    with_guid: bool = typer.Option(False, "--with-guid", help="Include GUID column"),
) -> None:
    """Export notes as CSV."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        from anki.collection import DeckIdLimit

        limit = None
        if deck:
            did = col.decks.id_for_name(deck)
            if not did:
                print_error(f"Deck '{deck}' not found")
                raise typer.Exit(1)
            limit = DeckIdLimit(deck_id=did)

        count = col.export_note_csv(
            out_path=output,
            limit=limit,
            with_html=with_html,
            with_tags=with_tags,
            with_deck=with_deck,
            with_notetype=with_notetype,
            with_guid=with_guid,
        )
        print_success(f"Exported {count} note(s) to {output}")


@app.command("cards-csv")
def cards_csv(
    output: str = typer.Option(..., "--output", "-o", help="Output CSV file path"),
    deck: str = typer.Option(None, "--deck", "-d", help="Deck to export"),
    with_html: bool = typer.Option(False, "--html", help="Include HTML tags"),
) -> None:
    """Export cards as CSV."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        from anki.collection import DeckIdLimit

        limit = None
        if deck:
            did = col.decks.id_for_name(deck)
            if not did:
                print_error(f"Deck '{deck}' not found")
                raise typer.Exit(1)
            limit = DeckIdLimit(deck_id=did)

        count = col.export_card_csv(out_path=output, limit=limit, with_html=with_html)
        print_success(f"Exported {count} card(s) to {output}")


@app.command()
def dataset(
    output: str = typer.Option(..., "--output", "-o", help="Output path for research dataset"),
    min_entries: int = typer.Option(0, "--min-entries", help="Min review entries per card"),
) -> None:
    """Export dataset for research (FSRS training data)."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        col.export_dataset_for_research(output, min_entries=min_entries)
        print_success(f"Exported research dataset to {output}")
