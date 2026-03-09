"""Card operations commands."""

from __future__ import annotations

from typing import List, Optional

import typer

from ankicli.connection import open_collection
from ankicli.output import print_error, print_single, print_success, print_table, is_json_mode, print_json

app = typer.Typer(no_args_is_help=True)


def _get_state():
    from ankicli.main import state
    return state


def _parse_ids(ids_str: str) -> list[int]:
    """Parse comma-separated card IDs."""
    return [int(x.strip()) for x in ids_str.split(",") if x.strip()]


@app.command()
def info(card_id: int = typer.Argument(..., help="Card ID")) -> None:
    """Show card details including fields, state, and scheduling info."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        card = col.get_card(card_id)
        note = card.note()
        data = {
            "card_id": card.id,
            "note_id": card.nid,
            "deck": col.decks.name(card.did),
            "notetype": note.note_type()["name"],
            "queue": card.queue,
            "type": card.type,
            "due": card.due,
            "interval": card.ivl,
            "ease_factor": card.factor / 10 if card.factor else 0,
            "reviews": card.reps,
            "lapses": card.lapses,
        }
        for key in note.keys():
            data[f"field:{key}"] = note[key]
        data["tags"] = " ".join(note.tags)
        print_single(data, title=f"Card {card_id}")


@app.command()
def stats(card_id: int = typer.Argument(..., help="Card ID")) -> None:
    """Show card statistics with review history."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        stat = col.card_stats_data(card_id)
        data = {
            "card_id": stat.card_id,
            "note_id": stat.note_id,
            "position": stat.position,
            "average_time": f"{stat.average_secs:.1f}s",
            "total_time": f"{stat.total_secs:.1f}s",
        }
        print_single(data, title=f"Stats: Card {card_id}")


@app.command()
def revlog(card_id: int = typer.Argument(..., help="Card ID")) -> None:
    """Show card review log."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        logs = col.get_review_logs(card_id)
        rows = []
        for log in logs:
            rows.append({
                "time": log.time,
                "type": log.review_kind,
                "rating": log.button_chosen,
                "interval": log.interval,
                "ease": log.ease,
                "taken_ms": log.taken_millis,
            })
        print_table(rows, title=f"Review Log: Card {card_id}")


@app.command()
def move(
    ids: str = typer.Argument(..., help="Comma-separated card IDs"),
    deck: str = typer.Option(..., "--deck", "-d", help="Target deck name"),
) -> None:
    """Move cards to a different deck."""
    s = _get_state()
    card_ids = _parse_ids(ids)
    with open_collection(s.profile, s.path) as col:
        did = col.decks.id_for_name(deck)
        if not did:
            print_error(f"Deck '{deck}' not found")
            raise typer.Exit(1)
        col.set_deck(card_ids, did)
        print_success(f"Moved {len(card_ids)} card(s) to '{deck}'")


@app.command()
def suspend(ids: str = typer.Argument(..., help="Comma-separated card IDs")) -> None:
    """Suspend cards."""
    s = _get_state()
    card_ids = _parse_ids(ids)
    with open_collection(s.profile, s.path) as col:
        col.sched.suspend_cards(card_ids)
        print_success(f"Suspended {len(card_ids)} card(s)")


@app.command()
def unsuspend(ids: str = typer.Argument(..., help="Comma-separated card IDs")) -> None:
    """Unsuspend cards."""
    s = _get_state()
    card_ids = _parse_ids(ids)
    with open_collection(s.profile, s.path) as col:
        col.sched.unsuspend_cards(card_ids)
        print_success(f"Unsuspended {len(card_ids)} card(s)")


@app.command()
def bury(ids: str = typer.Argument(..., help="Comma-separated card IDs")) -> None:
    """Bury cards (hide until tomorrow)."""
    s = _get_state()
    card_ids = _parse_ids(ids)
    with open_collection(s.profile, s.path) as col:
        col.sched.bury_cards(card_ids)
        print_success(f"Buried {len(card_ids)} card(s)")


@app.command()
def unbury(ids: str = typer.Argument(..., help="Comma-separated card IDs")) -> None:
    """Unbury cards."""
    s = _get_state()
    card_ids = _parse_ids(ids)
    with open_collection(s.profile, s.path) as col:
        col.sched.unbury_cards(card_ids)
        print_success(f"Unburied {len(card_ids)} card(s)")


@app.command()
def flag(
    ids: str = typer.Argument(..., help="Comma-separated card IDs"),
    flag_num: int = typer.Option(..., "--flag", "-f", help="Flag number (0=none, 1=red, 2=orange, 3=green, 4=blue, 5=pink, 6=cyan, 7=purple)"),
) -> None:
    """Set flag on cards."""
    s = _get_state()
    card_ids = _parse_ids(ids)
    with open_collection(s.profile, s.path) as col:
        col.set_user_flag_for_cards(flag_num, card_ids)
        flag_names = {0: "none", 1: "red", 2: "orange", 3: "green", 4: "blue", 5: "pink", 6: "cyan", 7: "purple"}
        print_success(f"Set flag '{flag_names.get(flag_num, flag_num)}' on {len(card_ids)} card(s)")


@app.command()
def forget(ids: str = typer.Argument(..., help="Comma-separated card IDs")) -> None:
    """Reset cards to new state."""
    s = _get_state()
    card_ids = _parse_ids(ids)
    with open_collection(s.profile, s.path) as col:
        defaults = col.sched.schedule_cards_as_new_defaults(0)
        col.sched.schedule_cards_as_new(
            card_ids,
            restore_position=defaults.restore_position,
            reset_counts=defaults.reset_counts,
            context=0,
        )
        print_success(f"Reset {len(card_ids)} card(s) to new")


@app.command("set-due")
def set_due(
    ids: str = typer.Argument(..., help="Comma-separated card IDs"),
    days: str = typer.Option(..., "--days", "-d", help="Days from today (e.g. '0' for today, '3' for 3 days)"),
) -> None:
    """Set due date for cards."""
    s = _get_state()
    card_ids = _parse_ids(ids)
    with open_collection(s.profile, s.path) as col:
        col.sched.set_due_date(card_ids, days)
        print_success(f"Set due date to +{days} day(s) for {len(card_ids)} card(s)")


@app.command()
def reposition(
    ids: str = typer.Argument(..., help="Comma-separated card IDs"),
    start: int = typer.Option(0, "--start", "-s", help="Starting position"),
    step: int = typer.Option(1, "--step", help="Step size"),
    randomize: bool = typer.Option(False, "--randomize", "-r", help="Randomize order"),
) -> None:
    """Reposition new cards in queue."""
    s = _get_state()
    card_ids = _parse_ids(ids)
    with open_collection(s.profile, s.path) as col:
        col.sched.reposition_new_cards(
            card_ids,
            starting_from=start,
            step_size=step,
            randomize=randomize,
            shift_existing=True,
        )
        print_success(f"Repositioned {len(card_ids)} card(s) starting at {start}")


@app.command()
def delete(ids: str = typer.Argument(..., help="Comma-separated card IDs")) -> None:
    """Delete cards and their orphaned notes."""
    s = _get_state()
    card_ids = _parse_ids(ids)
    with open_collection(s.profile, s.path) as col:
        col.remove_cards_and_orphaned_notes(card_ids)
        print_success(f"Deleted {len(card_ids)} card(s)")
