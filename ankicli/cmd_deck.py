"""Deck management commands."""

from __future__ import annotations

from typing import Optional

import typer

from ankicli.connection import open_collection
from ankicli.output import print_error, print_json, print_single, print_success, print_table, print_tree, is_json_mode

app = typer.Typer(no_args_is_help=True)


def _get_state():
    from ankicli.main import state
    return state


@app.command("list")
def deck_list() -> None:
    """List all decks with card counts."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        decks = col.decks.all_names_and_ids()
        rows = []
        for d in decks:
            count = col.decks.card_count([d.id], include_subdecks=False)
            rows.append({"id": d.id, "name": d.name, "cards": count})
        print_table(rows, title="Decks")


@app.command("tree")
def deck_tree() -> None:
    """Show deck hierarchy as a tree."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        tree = col.sched.deck_due_tree()

        def node_to_dict(node) -> dict:
            result = {
                "name": node.name,
                "new": node.new_count,
                "learn": node.learn_count,
                "review": node.review_count,
            }
            if node.children:
                result["children"] = [node_to_dict(c) for c in node.children]
            return result

        root_children = [node_to_dict(c) for c in tree.children]
        if is_json_mode():
            print_json(root_children)
        else:
            print_tree(root_children, title="Deck Tree")


@app.command()
def create(name: str = typer.Argument(..., help="Deck name (use :: for nesting)")) -> None:
    """Create a new deck."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        result = col.decks.add_normal_deck_with_name(name)
        print_success(f"Created deck '{name}' (ID: {result.id})")


@app.command()
def rename(
    name: str = typer.Argument(..., help="Current deck name"),
    new_name: str = typer.Argument(..., help="New deck name"),
) -> None:
    """Rename a deck."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        did = col.decks.id_for_name(name)
        if not did:
            print_error(f"Deck '{name}' not found")
            raise typer.Exit(1)
        deck = col.decks.get(did)
        col.decks.rename(deck, new_name)
        print_success(f"Renamed '{name}' -> '{new_name}'")


@app.command()
def delete(name: str = typer.Argument(..., help="Deck name to delete")) -> None:
    """Delete a deck."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        did = col.decks.id_for_name(name)
        if not did:
            print_error(f"Deck '{name}' not found")
            raise typer.Exit(1)
        col.decks.remove([did])
        print_success(f"Deleted deck '{name}'")


@app.command()
def move(
    name: str = typer.Argument(..., help="Deck name to move"),
    parent: str = typer.Option(..., "--parent", "-p", help="New parent deck name"),
) -> None:
    """Move a deck under a new parent."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        did = col.decks.id_for_name(name)
        parent_id = col.decks.id_for_name(parent)
        if not did:
            print_error(f"Deck '{name}' not found")
            raise typer.Exit(1)
        if not parent_id:
            print_error(f"Parent deck '{parent}' not found")
            raise typer.Exit(1)
        col.decks.reparent([did], parent_id)
        print_success(f"Moved '{name}' under '{parent}'")


@app.command("set-limits")
def set_limits(
    new_per_day: Optional[int] = typer.Option(None, "--new", "-n", help="Max new cards per day (0 to pause)"),
    review_per_day: Optional[int] = typer.Option(None, "--review", "-r", help="Max reviews per day"),
    deck_name: Optional[str] = typer.Option(None, "--deck", "-d", help="Deck name (omit to update all configs)"),
) -> None:
    """Set daily new/review limits. Use --new 0 to pause new cards."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        if deck_name:
            did = col.decks.id_for_name(deck_name)
            if not did:
                print_error(f"Deck '{deck_name}' not found")
                raise typer.Exit(1)
            configs = [col.decks.config_dict_for_deck_id(did)]
        else:
            configs = col.decks.all_config()

        updated = 0
        for conf in configs:
            changed = False
            if new_per_day is not None:
                if "new" not in conf:
                    conf["new"] = {}
                conf["new"]["perDay"] = new_per_day
                changed = True
            if review_per_day is not None:
                if "rev" not in conf:
                    conf["rev"] = {}
                conf["rev"]["perDay"] = review_per_day
                changed = True
            if changed:
                col.decks.update_config(conf)
                updated += 1

        if updated:
            msg = f"Updated {updated} config(s)"
            if new_per_day is not None:
                msg += f" · 新卡/天: {new_per_day}"
            if review_per_day is not None:
                msg += f" · 复习/天: {review_per_day}"
            print_success(msg)
        else:
            print_error("Specify at least one of --new or --review")


@app.command()
def info(name: str = typer.Argument(..., help="Deck name")) -> None:
    """Show deck details and configuration."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        did = col.decks.id_for_name(name)
        if not did:
            print_error(f"Deck '{name}' not found")
            raise typer.Exit(1)
        deck = col.decks.get(did)
        conf = col.decks.config_dict_for_deck_id(did)
        total = col.decks.card_count([did], include_subdecks=True)
        data = {
            "id": did,
            "name": deck["name"],
            "cards_total": total,
            "config_name": conf.get("name", "?"),
            "new_per_day": conf.get("new", {}).get("perDay", "?"),
            "review_per_day": conf.get("rev", {}).get("perDay", "?"),
            "is_filtered": deck.get("dyn", 0) == 1,
        }
        print_single(data, title=f"Deck: {name}")


@app.command()
def select(name: str = typer.Argument(..., help="Deck name")) -> None:
    """Set a deck as the current/active deck."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        did = col.decks.id_for_name(name)
        if not did:
            print_error(f"Deck '{name}' not found")
            raise typer.Exit(1)
        deck = col.decks.get(did)
        col.decks.set_current(deck)
        print_success(f"Current deck set to '{name}'")


@app.command()
def current() -> None:
    """Show the current active deck."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        deck = col.decks.current()
        print_single({"id": deck["id"], "name": deck["name"]}, title="Current Deck")


@app.command()
def count(name: str = typer.Argument(..., help="Deck name")) -> None:
    """Show card count for a deck."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        did = col.decks.id_for_name(name)
        if not did:
            print_error(f"Deck '{name}' not found")
            raise typer.Exit(1)
        own = col.decks.card_count([did], include_subdecks=False)
        total = col.decks.card_count([did], include_subdecks=True)
        print_single({"deck": name, "own_cards": own, "with_subdecks": total})


@app.command("create-filtered")
def create_filtered(
    name: str = typer.Argument(..., help="Filtered deck name"),
    search: str = typer.Option(..., "--search", "-s", help="Search query for filtered deck"),
) -> None:
    """Create a filtered/custom study deck."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        deck = col.sched.get_or_create_filtered_deck(deck_id=0)
        deck.name = name
        if deck.config.search_terms:
            deck.config.search_terms[0].search = search
        col.sched.add_or_update_filtered_deck(deck)
        print_success(f"Created filtered deck '{name}'")


@app.command("rebuild-filtered")
def rebuild_filtered(name: str = typer.Argument(..., help="Filtered deck name")) -> None:
    """Rebuild a filtered deck."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        did = col.decks.id_for_name(name)
        if not did:
            print_error(f"Deck '{name}' not found")
            raise typer.Exit(1)
        col.sched.rebuild_filtered_deck(did)
        print_success(f"Rebuilt filtered deck '{name}'")
