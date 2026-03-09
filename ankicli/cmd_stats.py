"""Statistics commands."""

from __future__ import annotations

import typer

from ankicli.connection import open_collection
from ankicli.output import print_error, print_single, print_table, is_json_mode, print_json

app = typer.Typer(no_args_is_help=True)


def _get_state():
    from ankicli.main import state
    return state


@app.command()
def today() -> None:
    """Show today's study statistics."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        studied = col.studied_today()
        new_count, learn_count, review_count = col.sched.counts()
        data = {
            "studied_today": studied,
            "remaining_new": new_count,
            "remaining_learning": learn_count,
            "remaining_review": review_count,
            "remaining_total": new_count + learn_count + review_count,
        }
        print_single(data, title="Today's Statistics")


@app.command()
def card(card_id: int = typer.Argument(..., help="Card ID")) -> None:
    """Show statistics for a specific card."""
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
        print_single(data, title=f"Card Stats: {card_id}")


@app.command()
def deck(
    deck_name: str = typer.Option(None, "--deck", "-d", help="Deck name (all decks if omitted)"),
) -> None:
    """Show deck statistics overview (due tree)."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        tree = col.sched.deck_due_tree()
        rows = []

        def flatten(node, depth=0):
            prefix = "  " * depth
            rows.append({
                "deck": prefix + node.name,
                "new": node.new_count,
                "learn": node.learn_count,
                "review": node.review_count,
                "total_due": node.new_count + node.learn_count + node.review_count,
            })
            for child in node.children:
                flatten(child, depth + 1)

        for child in tree.children:
            flatten(child)

        if deck_name:
            rows = [r for r in rows if deck_name.lower() in r["deck"].strip().lower()]

        print_table(rows, title="Deck Statistics")


@app.command()
def memory(card_id: int = typer.Argument(..., help="Card ID")) -> None:
    """Show FSRS memory state for a card."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        mem = col.compute_memory_state(card_id)
        data = {
            "card_id": card_id,
            "desired_retention": f"{mem.desired_retention:.2%}",
            "stability": f"{mem.stability:.2f} days" if mem.stability is not None else "N/A",
            "difficulty": f"{mem.difficulty:.2f}" if mem.difficulty is not None else "N/A",
            "decay": f"{mem.decay:.4f}" if mem.decay is not None else "N/A",
        }
        print_single(data, title=f"FSRS Memory: Card {card_id}")


@app.command()
def overview() -> None:
    """Show global collection statistics."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        data = {
            "total_cards": col.card_count(),
            "total_notes": col.note_count(),
            "total_decks": col.decks.count(),
            "scheduler_version": f"v{col.sched_ver()}" + (" (v3)" if col.v3_scheduler() else ""),
            "collection_name": col.name(),
            "collection_path": col.path,
        }
        print_single(data, title="Collection Overview")
