"""Note operations commands."""

from __future__ import annotations

import json
from typing import Optional

import typer

from ankicli.connection import open_collection
from ankicli.output import print_error, print_single, print_success, print_table, print_json, is_json_mode

app = typer.Typer(no_args_is_help=True)


def _get_state():
    from ankicli.main import state
    return state


@app.command()
def add(
    front: str = typer.Option(None, "--front", "-f", help="Front field (for Basic type)"),
    back: str = typer.Option(None, "--back", "-b", help="Back field (for Basic type)"),
    deck: str = typer.Option("Default", "--deck", "-d", help="Target deck name"),
    notetype: str = typer.Option("Basic", "--type", "-t", help="Note type name"),
    fields: str = typer.Option(None, "--fields", help="Fields as key=value pairs, comma-separated"),
    tags: str = typer.Option("", "--tags", help="Space-separated tags"),
) -> None:
    """Add a new note."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        model = col.models.by_name(notetype)
        if not model:
            print_error(f"Note type '{notetype}' not found")
            raise typer.Exit(1)

        did = col.decks.id_for_name(deck)
        if not did:
            print_error(f"Deck '{deck}' not found")
            raise typer.Exit(1)

        note = col.new_note(model)

        if front is not None and back is not None:
            field_names = col.models.field_names(model)
            if len(field_names) >= 2:
                note[field_names[0]] = front
                note[field_names[1]] = back
            else:
                print_error("Note type has fewer than 2 fields; use --fields instead")
                raise typer.Exit(1)
        elif fields:
            for pair in fields.split(","):
                key, _, value = pair.partition("=")
                key = key.strip()
                value = value.strip()
                if key in note.keys():
                    note[key] = value
                else:
                    print_error(f"Unknown field '{key}'. Available: {list(note.keys())}")
                    raise typer.Exit(1)
        else:
            print_error("Provide --front/--back or --fields")
            raise typer.Exit(1)

        if tags:
            note.set_tags_from_str(tags)

        changes = col.add_note(note, did)
        print_success(f"Added note (ID: {note.id}) to deck '{deck}'")


@app.command("add-batch")
def add_batch(
    file: str = typer.Option(..., "--file", "-f", help="JSON or CSV file with notes"),
    deck: str = typer.Option("Default", "--deck", "-d", help="Target deck"),
    notetype: str = typer.Option("Basic", "--type", "-t", help="Note type"),
) -> None:
    """Add multiple notes from a JSON file.

    JSON format: [{"front": "...", "back": "..."}, ...] or
    [{"fields": {"Field1": "val", ...}, "tags": "tag1 tag2"}, ...]
    """
    s = _get_state()
    import json as json_mod
    from pathlib import Path

    data = json_mod.loads(Path(file).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        print_error("File must contain a JSON array")
        raise typer.Exit(1)

    with open_collection(s.profile, s.path) as col:
        model = col.models.by_name(notetype)
        if not model:
            print_error(f"Note type '{notetype}' not found")
            raise typer.Exit(1)

        did = col.decks.id_for_name(deck)
        if not did:
            print_error(f"Deck '{deck}' not found")
            raise typer.Exit(1)

        field_names = col.models.field_names(model)
        count = 0
        for item in data:
            note = col.new_note(model)
            if "front" in item and "back" in item:
                note[field_names[0]] = item["front"]
                if len(field_names) >= 2:
                    note[field_names[1]] = item["back"]
            elif "fields" in item:
                for k, v in item["fields"].items():
                    if k in note.keys():
                        note[k] = v
            if "tags" in item:
                note.set_tags_from_str(item["tags"])
            col.add_note(note, did)
            count += 1

        print_success(f"Added {count} note(s) to deck '{deck}'")


@app.command()
def info(note_id: int = typer.Argument(..., help="Note ID")) -> None:
    """Show note details."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        note = col.get_note(note_id)
        data = {
            "note_id": note.id,
            "notetype": note.note_type()["name"],
            "tags": " ".join(note.tags),
        }
        for key in note.keys():
            data[f"field:{key}"] = note[key]
        print_single(data, title=f"Note {note_id}")


@app.command()
def edit(
    note_id: int = typer.Argument(..., help="Note ID"),
    field: str = typer.Option(..., "--field", "-f", help="Field name to edit"),
    value: str = typer.Option(..., "--value", "-v", help="New value"),
) -> None:
    """Edit a note field."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        note = col.get_note(note_id)
        if field not in note.keys():
            print_error(f"Unknown field '{field}'. Available: {list(note.keys())}")
            raise typer.Exit(1)
        note[field] = value
        col.update_note(note)
        print_success(f"Updated field '{field}' on note {note_id}")


@app.command()
def delete(ids: str = typer.Argument(..., help="Comma-separated note IDs")) -> None:
    """Delete notes."""
    s = _get_state()
    note_ids = [int(x.strip()) for x in ids.split(",") if x.strip()]
    with open_collection(s.profile, s.path) as col:
        col.remove_notes(note_ids)
        print_success(f"Deleted {len(note_ids)} note(s)")


@app.command("find-replace")
def find_replace(
    search: str = typer.Option(..., "--search", "-s", help="Text to find"),
    replace: str = typer.Option(..., "--replace", "-r", help="Replacement text"),
    query: str = typer.Option("", "--query", "-q", help="Limit to notes matching this search"),
    field_name: str = typer.Option(None, "--field", "-f", help="Limit to specific field"),
    regex: bool = typer.Option(False, "--regex", help="Use regular expressions"),
    match_case: bool = typer.Option(False, "--case", help="Case sensitive"),
) -> None:
    """Find and replace text in notes."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        if query:
            nids = col.find_notes(query)
        else:
            nids = col.find_notes("")
        changes = col.find_and_replace(
            note_ids=nids,
            search=search,
            replacement=replace,
            regex=regex,
            field_name=field_name,
            match_case=match_case,
        )
        print_success(f"Replaced in {changes.count} note(s)")


@app.command()
def duplicates(
    field: str = typer.Option(..., "--field", "-f", help="Field name to check"),
    search: str = typer.Option("", "--search", "-s", help="Limit search scope"),
) -> None:
    """Find duplicate notes by field content."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        dupes = col.find_dupes(field, search)
        rows = []
        for val, nids in dupes:
            rows.append({"value": val, "count": len(nids), "note_ids": ",".join(str(n) for n in nids)})
        print_table(rows, title=f"Duplicates in field '{field}'")


@app.command("fields")
def note_fields(note_id: int = typer.Argument(..., help="Note ID")) -> None:
    """Show note field names and values."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        note = col.get_note(note_id)
        rows = [{"field": k, "value": v} for k, v in note.items()]
        print_table(rows, title=f"Fields: Note {note_id}")


@app.command("cards")
def note_cards(note_id: int = typer.Argument(..., help="Note ID")) -> None:
    """Show cards associated with a note."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        cids = col.card_ids_of_note(note_id)
        rows = []
        for cid in cids:
            card = col.get_card(cid)
            rows.append({
                "card_id": cid,
                "deck": col.decks.name(card.did),
                "queue": card.queue,
                "type": card.type,
                "due": card.due,
            })
        print_table(rows, title=f"Cards for Note {note_id}")
