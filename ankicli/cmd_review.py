"""Review and study commands."""

from __future__ import annotations

from typing import Optional

import typer

from ankicli.connection import open_collection
from ankicli.output import print_error, print_json, print_single, print_success, print_table, is_json_mode

app = typer.Typer(no_args_is_help=True)


def _get_state():
    from ankicli.main import state
    return state


def _strip_html(text: str) -> str:
    """Minimal HTML tag stripping for terminal display."""
    import re
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&")
    text = text.replace("&lt;", "<").replace("&gt;", ">")
    return text.strip()


@app.command()
def start(
    deck: str = typer.Option(None, "--deck", "-d", help="Deck to review"),
) -> None:
    """Interactive review session in the terminal."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        if deck:
            did = col.decks.id_for_name(deck)
            if not did:
                print_error(f"Deck '{deck}' not found")
                raise typer.Exit(1)
            d = col.decks.get(did)
            col.decks.set_current(d)

        try:
            from rich.console import Console
            from rich.panel import Panel
            from rich.text import Text
            console = Console()
            _rich_review_loop(col, console, deck)
        except ImportError:
            _plain_review_loop(col, deck)


def _rich_review_loop(col, console, deck_name: str | None) -> None:
    """Review loop with rich formatting."""
    from rich.panel import Panel
    from rich.text import Text

    reviewed = 0
    while True:
        counts = col.sched.counts()
        new_count, learn_count, review_count = counts
        total = new_count + learn_count + review_count
        if total == 0:
            console.print(Panel("[bold green]Congratulations![/bold green] No more cards to review.", title="Done"))
            break

        header = f"New: {new_count}  Learn: {learn_count}  Review: {review_count}  |  Reviewed: {reviewed}"
        if deck_name:
            header = f"[bold]{deck_name}[/bold]  |  " + header
        console.print(f"\n{header}")

        card = col.sched.getCard()
        if card is None:
            console.print(Panel("[bold green]Congratulations![/bold green] No more cards.", title="Done"))
            break

        note = card.note()
        front = _strip_html(card.question())
        console.print(Panel(front, title="Question", border_style="cyan"))

        try:
            input("  Press Enter to show answer...")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Review ended.[/dim]")
            break

        back = _strip_html(card.answer())
        console.print(Panel(back, title="Answer", border_style="yellow"))

        while True:
            try:
                choice = input("  [1] Again  [2] Hard  [3] Good  [4] Easy  [u] Undo  [q] Quit: ").strip()
            except (KeyboardInterrupt, EOFError):
                console.print("\n[dim]Review ended.[/dim]")
                return

            if choice == "q":
                console.print(f"[dim]Reviewed {reviewed} card(s).[/dim]")
                return
            if choice == "u" and reviewed > 0:
                col.undo()
                reviewed -= 1
                console.print("[dim]Undone.[/dim]")
                break
            if choice in ("1", "2", "3", "4"):
                ease = int(choice)
                col.sched.answerCard(card, ease)
                reviewed += 1
                ease_labels = {1: "Again", 2: "Hard", 3: "Good", 4: "Easy"}
                console.print(f"  [green]{ease_labels[ease]}[/green]")
                break
            console.print("  [red]Invalid input[/red]")


def _plain_review_loop(col, deck_name: str | None) -> None:
    """Fallback review loop without rich."""
    reviewed = 0
    while True:
        counts = col.sched.counts()
        new_count, learn_count, review_count = counts
        total = new_count + learn_count + review_count
        if total == 0:
            print("Congratulations! No more cards to review.")
            break

        print(f"\n--- New: {new_count} | Learn: {learn_count} | Review: {review_count} | Reviewed: {reviewed} ---")

        card = col.sched.getCard()
        if card is None:
            print("No more cards.")
            break

        front = _strip_html(card.question())
        print(f"\n[Question]\n{front}")

        try:
            input("\n  Press Enter to show answer...")
        except (KeyboardInterrupt, EOFError):
            print("\nReview ended.")
            break

        back = _strip_html(card.answer())
        print(f"\n[Answer]\n{back}")

        while True:
            try:
                choice = input("\n  [1] Again  [2] Hard  [3] Good  [4] Easy  [q] Quit: ").strip()
            except (KeyboardInterrupt, EOFError):
                print(f"\nReviewed {reviewed} card(s).")
                return

            if choice == "q":
                print(f"Reviewed {reviewed} card(s).")
                return
            if choice in ("1", "2", "3", "4"):
                ease = int(choice)
                col.sched.answerCard(card, ease)
                reviewed += 1
                break
            print("  Invalid input")


@app.command("next")
def next_card(
    deck: str = typer.Option(None, "--deck", "-d", help="Deck name"),
) -> None:
    """Get the next card to review (non-interactive, for scripting)."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        if deck:
            did = col.decks.id_for_name(deck)
            if not did:
                print_error(f"Deck '{deck}' not found")
                raise typer.Exit(1)
            d = col.decks.get(did)
            col.decks.set_current(d)

        queued = col.sched.get_queued_cards(fetch_limit=1)
        if not queued.cards:
            print_error("No cards to review")
            raise typer.Exit(1)

        qc = queued.cards[0]
        card_data = {
            "card_id": qc.card.id,
            "note_id": qc.card.nid,
            "deck_id": qc.card.did,
            "queue": qc.card.queue,
            "new_count": queued.new_count,
            "learn_count": queued.learning_count,
            "review_count": queued.review_count,
        }
        if is_json_mode():
            note = col.get_note(qc.card.nid)
            card_data["fields"] = dict(note.items())
            card_data["tags"] = note.tags
        print_single(card_data, title="Next Card")


@app.command()
def answer(
    card_id: int = typer.Argument(..., help="Card ID"),
    ease: int = typer.Option(..., "--ease", "-e", help="Rating: 1=Again, 2=Hard, 3=Good, 4=Easy"),
) -> None:
    """Submit a review answer for a card."""
    s = _get_state()
    if ease not in (1, 2, 3, 4):
        print_error("Ease must be 1, 2, 3, or 4")
        raise typer.Exit(1)
    with open_collection(s.profile, s.path) as col:
        card = col.get_card(card_id)
        col.sched.answerCard(card, ease)
        ease_labels = {1: "Again", 2: "Hard", 3: "Good", 4: "Easy"}
        print_success(f"Answered card {card_id}: {ease_labels[ease]}")


@app.command("answer-batch")
def answer_batch(
    data: str = typer.Option(..., "--data", "-d", help='JSON array: [{"card_id": N, "ease": M}, ...]'),
) -> None:
    """Submit review answers for multiple cards."""
    s = _get_state()
    import json as json_mod
    items = json_mod.loads(data)
    with open_collection(s.profile, s.path) as col:
        for item in items:
            card = col.get_card(item["card_id"])
            col.sched.answerCard(card, item["ease"])
        print_success(f"Answered {len(items)} card(s)")


@app.command()
def counts(
    deck: str = typer.Option(None, "--deck", "-d", help="Deck name"),
) -> None:
    """Show new/learning/review counts."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        if deck:
            did = col.decks.id_for_name(deck)
            if not did:
                print_error(f"Deck '{deck}' not found")
                raise typer.Exit(1)
            d = col.decks.get(did)
            col.decks.set_current(d)

        new_count, learn_count, review_count = col.sched.counts()
        print_single({
            "new": new_count,
            "learning": learn_count,
            "review": review_count,
            "total": new_count + learn_count + review_count,
        }, title=f"Review Counts{f' ({deck})' if deck else ''}")


@app.command()
def due(
    deck: str = typer.Option(None, "--deck", "-d", help="Deck name"),
    limit: int = typer.Option(20, "--limit", "-n", help="Max cards to show"),
) -> None:
    """List due cards."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        query = "is:due"
        if deck:
            query += f' "deck:{deck}"'
        cids = col.find_cards(query)
        rows = []
        for cid in cids[:limit]:
            card = col.get_card(cid)
            note = card.note()
            field_names = note.keys()
            front = _strip_html(note[field_names[0]]) if field_names else ""
            rows.append({
                "card_id": cid,
                "front": front[:60],
                "deck": col.decks.name(card.did),
                "due": card.due,
                "interval": card.ivl,
            })
        print_table(rows, title=f"Due Cards ({len(cids)} total, showing {len(rows)})")


@app.command()
def undo() -> None:
    """Undo the last review action."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        status = col.undo_status()
        if not status.undo:
            print_error("Nothing to undo")
            raise typer.Exit(1)
        col.undo()
        print_success(f"Undone: {status.undo}")
