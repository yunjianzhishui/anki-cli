"""AnkiConnect proxy commands — works while Anki GUI is running."""

from __future__ import annotations

import typer

from ankicli.connection import open_ankiconnect
from ankicli.output import print_error, print_json, print_single, print_success, print_table, is_json_mode

app = typer.Typer(no_args_is_help=True)


@app.command("decks")
def ac_decks() -> None:
    """List all decks (via AnkiConnect)."""
    with open_ankiconnect() as ac:
        mapping = ac.deck_names_and_ids()
        rows = [{"name": name, "id": did} for name, did in mapping.items()]
        print_table(rows, title="Decks (via AnkiConnect)")


@app.command("due")
def ac_due(
    deck: str = typer.Option(None, "--deck", "-d", help="Deck name"),
    limit: int = typer.Option(20, "--limit", "-n", help="Max cards"),
) -> None:
    """List due cards (via AnkiConnect)."""
    with open_ankiconnect() as ac:
        query = "is:due"
        if deck:
            query += f' "deck:{deck}"'
        cids = ac.find_cards(query)
        if not cids:
            print_success("No due cards")
            return
        infos = ac.cards_info(cids[:limit])
        rows = []
        for c in infos:
            rows.append({
                "card_id": c["cardId"],
                "deck": c["deckName"],
                "front": c.get("fields", {}).get(list(c.get("fields", {}).keys())[0] if c.get("fields") else "?", {}).get("value", "")[:60],
                "due": c.get("due", "?"),
                "interval": c.get("interval", "?"),
            })
        print_table(rows, title=f"Due Cards ({len(cids)} total, showing {len(rows)})")


@app.command("counts")
def ac_counts() -> None:
    """Show today's review count (via AnkiConnect)."""
    with open_ankiconnect() as ac:
        reviewed = ac.get_num_cards_reviewed_today()
        print_single({"reviewed_today": reviewed}, title="Review Counts")


@app.command("search")
def ac_search(
    query: str = typer.Argument(..., help="Anki search query"),
    limit: int = typer.Option(20, "--limit", "-n", help="Max results"),
) -> None:
    """Search cards (via AnkiConnect)."""
    with open_ankiconnect() as ac:
        cids = ac.find_cards(query)
        infos = ac.cards_info(cids[:limit])
        rows = []
        for c in infos:
            fields = c.get("fields", {})
            first_field = list(fields.values())[0]["value"] if fields else ""
            rows.append({
                "card_id": c["cardId"],
                "deck": c["deckName"],
                "front": first_field[:60],
                "type": c.get("type", "?"),
            })
        print_table(rows, title=f"Search: '{query}' ({len(cids)} total)")


@app.command("add")
def ac_add(
    front: str = typer.Option(..., "--front", "-f", help="Front field"),
    back: str = typer.Option(..., "--back", "-b", help="Back field"),
    deck: str = typer.Option("Default", "--deck", "-d", help="Deck name"),
    model: str = typer.Option("Basic", "--type", "-t", help="Note type"),
    tags: str = typer.Option("", "--tags", help="Space-separated tags"),
) -> None:
    """Add a note (via AnkiConnect)."""
    with open_ankiconnect() as ac:
        fields = ac.model_field_names(model)
        if len(fields) < 2:
            print_error(f"Model '{model}' has fewer than 2 fields")
            raise typer.Exit(1)

        note = {
            "deckName": deck,
            "modelName": model,
            "fields": {fields[0]: front, fields[1]: back},
            "tags": tags.split() if tags else [],
        }
        nid = ac.add_note(note)
        print_success(f"Added note (ID: {nid}) to deck '{deck}'")


@app.command("answer")
def ac_answer(
    card_id: int = typer.Argument(..., help="Card ID"),
    ease: int = typer.Option(..., "--ease", "-e", help="1=Again, 2=Hard, 3=Good, 4=Easy"),
) -> None:
    """Answer a card (via AnkiConnect)."""
    with open_ankiconnect() as ac:
        ac.answer_cards([{"cardId": card_id, "ease": ease}])
        labels = {1: "Again", 2: "Hard", 3: "Good", 4: "Easy"}
        print_success(f"Answered card {card_id}: {labels.get(ease, ease)}")


@app.command("suspend")
def ac_suspend(ids: str = typer.Argument(..., help="Comma-separated card IDs")) -> None:
    """Suspend cards (via AnkiConnect)."""
    with open_ankiconnect() as ac:
        card_ids = [int(x.strip()) for x in ids.split(",")]
        ac.suspend_cards(card_ids)
        print_success(f"Suspended {len(card_ids)} card(s)")


@app.command("unsuspend")
def ac_unsuspend(ids: str = typer.Argument(..., help="Comma-separated card IDs")) -> None:
    """Unsuspend cards (via AnkiConnect)."""
    with open_ankiconnect() as ac:
        card_ids = [int(x.strip()) for x in ids.split(",")]
        ac.unsuspend_cards(card_ids)
        print_success(f"Unsuspended {len(card_ids)} card(s)")


@app.command("tags")
def ac_tags() -> None:
    """List all tags (via AnkiConnect)."""
    with open_ankiconnect() as ac:
        tags = ac.get_tags()
        rows = [{"tag": t} for t in tags]
        print_table(rows, title=f"Tags ({len(tags)} total)")


@app.command("add-tags")
def ac_add_tags(
    note_ids: str = typer.Argument(..., help="Comma-separated note IDs"),
    tags: str = typer.Option(..., "--tags", "-t", help="Space-separated tags"),
) -> None:
    """Add tags to notes (via AnkiConnect)."""
    with open_ankiconnect() as ac:
        nids = [int(x.strip()) for x in note_ids.split(",")]
        ac.add_tags(nids, tags)
        print_success(f"Added tags '{tags}' to {len(nids)} note(s)")


@app.command("notetypes")
def ac_notetypes() -> None:
    """List note types (via AnkiConnect)."""
    with open_ankiconnect() as ac:
        names = ac.model_names()
        rows = [{"name": n} for n in names]
        print_table(rows, title="Note Types")


@app.command("sync")
def ac_sync() -> None:
    """Trigger sync (via AnkiConnect)."""
    with open_ankiconnect() as ac:
        ac.sync()
        print_success("Sync triggered")


@app.command("delete-notes")
def ac_delete_notes(ids: str = typer.Argument(..., help="Comma-separated note IDs")) -> None:
    """Delete notes (via AnkiConnect)."""
    with open_ankiconnect() as ac:
        nids = [int(x.strip()) for x in ids.split(",")]
        ac.delete_notes(nids)
        print_success(f"Deleted {len(nids)} note(s)")
