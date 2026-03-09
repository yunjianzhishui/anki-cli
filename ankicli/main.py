"""Anki CLI main entry point."""

from __future__ import annotations

import sys
import typer

from ankicli import output

app = typer.Typer(
    name="anki-cli",
    help="Anki CLI — full command-line interface for Anki, sharing the same core as the GUI.",
    no_args_is_help=True,
)


class GlobalState:
    profile: str = "User 1"
    path: str | None = None
    json_mode: bool = False
    verbose: bool = False

state = GlobalState()


@app.callback()
def main(
    profile: str = typer.Option("User 1", "--profile", "-p", help="Anki profile name"),
    path: str = typer.Option(None, "--path", help="Direct path to collection.anki2"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output JSON instead of tables"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose logging"),
    version: bool = typer.Option(False, "--version", help="Show version"),
) -> None:
    """Anki CLI — operate your Anki collection from the command line."""
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if sys.stderr and hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    if version:
        typer.echo("anki-cli 0.1.0")
        raise typer.Exit()

    state.profile = profile
    state.path = path or None
    state.json_mode = json_output
    state.verbose = verbose
    output.set_json_mode(json_output)


from ankicli.cmd_deck import app as deck_app
from ankicli.cmd_card import app as card_app
from ankicli.cmd_note import app as note_app
from ankicli.cmd_review import app as review_app
from ankicli.cmd_search import app as search_app
from ankicli.cmd_tag import app as tag_app
from ankicli.cmd_notetype import app as notetype_app
from ankicli.cmd_import import app as import_app
from ankicli.cmd_export import app as export_app
from ankicli.cmd_sync import app as sync_app
from ankicli.cmd_stats import app as stats_app
from ankicli.cmd_media import app as media_app
from ankicli.cmd_config import app as config_app
from ankicli.cmd_db import app as db_app
from ankicli.cmd_scheduler import app as scheduler_app
from ankicli.cmd_revlog import app as revlog_app
from ankicli.cmd_ac import app as ac_app

app.add_typer(deck_app, name="deck", help="Deck management")
app.add_typer(card_app, name="card", help="Card operations")
app.add_typer(note_app, name="note", help="Note operations")
app.add_typer(review_app, name="review", help="Review and study")
app.add_typer(search_app, name="search", help="Search cards and notes")
app.add_typer(tag_app, name="tag", help="Tag management")
app.add_typer(notetype_app, name="notetype", help="Note type management")
app.add_typer(import_app, name="import", help="Import data")
app.add_typer(export_app, name="export", help="Export data")
app.add_typer(sync_app, name="sync", help="Sync with AnkiWeb")
app.add_typer(stats_app, name="stats", help="Statistics")
app.add_typer(media_app, name="media", help="Media management")
app.add_typer(config_app, name="config", help="Configuration and preferences")
app.add_typer(db_app, name="db", help="Database maintenance")
app.add_typer(scheduler_app, name="scheduler", help="Scheduler management")
app.add_typer(revlog_app, name="revlog", help="Review log queries")
app.add_typer(ac_app, name="ac", help="AnkiConnect mode (use while GUI is running)")


def cli() -> None:
    """Entry point for console_scripts."""
    app()


if __name__ == "__main__":
    cli()
