"""Scheduler management commands."""

from __future__ import annotations

import typer

from ankicli.connection import open_collection
from ankicli.output import print_error, print_single, print_success

app = typer.Typer(no_args_is_help=True)


def _get_state():
    from ankicli.main import state
    return state


@app.command()
def version() -> None:
    """Show current scheduler version."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        ver = col.sched_ver()
        v3 = col.v3_scheduler()
        print_single({
            "scheduler_version": ver,
            "v3_enabled": v3,
            "display": f"v{ver}" + (" with v3/FSRS" if v3 else ""),
        }, title="Scheduler")


@app.command()
def upgrade() -> None:
    """Upgrade to v2 scheduler."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        if col.sched_ver() >= 2:
            print_success("Already on v2 scheduler")
            return
        col.upgrade_to_v2_scheduler()
        print_success("Upgraded to v2 scheduler")


@app.command("set-v3")
def set_v3(
    enabled: bool = typer.Argument(..., help="true/false to enable/disable v3 scheduler"),
) -> None:
    """Enable or disable v3 scheduler."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        col.set_v3_scheduler(enabled)
        state_str = "enabled" if enabled else "disabled"
        print_success(f"V3 scheduler {state_str}")


@app.command("unbury-deck")
def unbury_deck(
    deck_name: str = typer.Argument(..., help="Deck name"),
) -> None:
    """Unbury all cards in a deck."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        did = col.decks.id_for_name(deck_name)
        if not did:
            print_error(f"Deck '{deck_name}' not found")
            raise typer.Exit(1)
        from anki.scheduler import UnburyDeck
        col.sched.unbury_deck(did, mode=UnburyDeck.ALL)
        print_success(f"Unburied all cards in '{deck_name}'")


@app.command("custom-study")
def custom_study(
    deck_name: str = typer.Argument(..., help="Deck name"),
    extend_new: int = typer.Option(0, "--extend-new", help="Extra new cards"),
    extend_review: int = typer.Option(0, "--extend-review", help="Extra review cards"),
) -> None:
    """Extend daily limits for custom study."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        did = col.decks.id_for_name(deck_name)
        if not did:
            print_error(f"Deck '{deck_name}' not found")
            raise typer.Exit(1)
        d = col.decks.get(did)
        col.decks.set_current(d)
        if extend_new > 0 or extend_review > 0:
            col.sched.extend_limits(extend_new, extend_review)
            print_success(f"Extended limits: +{extend_new} new, +{extend_review} review")
        else:
            defaults = col.sched.custom_study_defaults(did)
            print_single({
                "available_new": defaults.available_new,
                "available_review": defaults.available_review,
            }, title=f"Custom Study Defaults: {deck_name}")
