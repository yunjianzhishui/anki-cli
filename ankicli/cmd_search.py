"""Search commands."""

from __future__ import annotations

import typer

from ankicli.connection import open_collection
from ankicli.output import print_error, print_table, print_json, is_json_mode

app = typer.Typer(no_args_is_help=True)


def _get_state():
    from ankicli.main import state
    return state


def _strip_html(text: str) -> str:
    import re
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()


@app.command("cards")
def search_cards(
    query: str = typer.Argument(..., help="Anki search query (e.g. 'is:due deck:Default')"),
    limit: int = typer.Option(50, "--limit", "-n", help="Max results"),
    order: bool = typer.Option(False, "--order", "-o", help="Use collection sort order"),
) -> None:
    """Search for cards matching a query."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        cids = col.find_cards(query, order=order)
        rows = []
        for cid in cids[:limit]:
            card = col.get_card(cid)
            note = card.note()
            field_names = note.keys()
            front = _strip_html(note[field_names[0]]) if field_names else ""
            if is_json_mode():
                row = {
                    "card_id": cid,
                    "note_id": card.nid,
                    "deck": col.decks.name(card.did),
                    "notetype": note.note_type()["name"],
                    "fields": {k: _strip_html(note[k]) for k in field_names},
                    "tags": note.tags,
                    "queue": card.queue,
                    "type": card.type,
                    "due": card.due,
                    "interval": card.ivl,
                    "ease_factor": card.factor,
                    "reps": card.reps,
                    "lapses": card.lapses,
                }
            else:
                row = {
                    "card_id": cid,
                    "note_id": card.nid,
                    "front": front[:80],
                    "deck": col.decks.name(card.did),
                    "queue": card.queue,
                    "type": card.type,
                    "due": card.due,
                }
            rows.append(row)
        if is_json_mode():
            print_json({"total": len(cids), "showing": len(rows), "cards": rows})
        else:
            print_table(rows, title=f"Search: '{query}' ({len(cids)} total, showing {len(rows)})")


@app.command("notes")
def search_notes(
    query: str = typer.Argument(..., help="Anki search query"),
    limit: int = typer.Option(50, "--limit", "-n", help="Max results"),
) -> None:
    """Search for notes matching a query."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        nids = col.find_notes(query)
        rows = []
        for nid in nids[:limit]:
            note = col.get_note(nid)
            field_names = note.keys()
            front = _strip_html(note[field_names[0]]) if field_names else ""
            rows.append({
                "note_id": nid,
                "front": front[:80],
                "notetype": note.note_type()["name"],
                "tags": " ".join(note.tags),
            })
        print_table(rows, title=f"Notes: '{query}' ({len(nids)} total, showing {len(rows)})")


@app.command("empty-cards")
def empty_cards() -> None:
    """Find empty cards (cards with no content)."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        report = col.get_empty_cards()
        rows = []
        for ntype_report in report.report:
            for card_report in ntype_report.cards:
                rows.append({
                    "notetype": ntype_report.notetype_name,
                    "template": card_report.template_name,
                    "count": len(card_report.card_ids),
                })
        if rows:
            print_table(rows, title="Empty Cards")
        else:
            from ankicli.output import print_success
            print_success("No empty cards found")


@app.command()
def build(
    parts: list[str] = typer.Argument(..., help="Search components to combine"),
    joiner: str = typer.Option("AND", "--joiner", "-j", help="AND or OR"),
) -> None:
    """Build a search string from components (utility command)."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        from anki.collection import SearchNode
        nodes = []
        for part in parts:
            nodes.append(SearchNode(parsable_text=part))
        result = col.build_search_string(*nodes, joiner=joiner)
        if is_json_mode():
            print_json({"query": result})
        else:
            print(result)
