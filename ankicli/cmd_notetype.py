"""Note type management commands."""

from __future__ import annotations

import typer

from ankicli.connection import open_collection
from ankicli.output import print_error, print_single, print_success, print_table

app = typer.Typer(no_args_is_help=True)


def _get_state():
    from ankicli.main import state
    return state


@app.command("list")
def notetype_list() -> None:
    """List all note types with usage counts."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        use_counts = col.models.all_use_counts()
        rows = []
        for entry in use_counts:
            rows.append({
                "id": entry.id,
                "name": entry.name,
                "use_count": entry.use_count,
            })
        print_table(rows, title="Note Types")


@app.command()
def info(name: str = typer.Argument(..., help="Note type name")) -> None:
    """Show note type details (fields, templates)."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        model = col.models.by_name(name)
        if not model:
            print_error(f"Note type '{name}' not found")
            raise typer.Exit(1)

        field_names = col.models.field_names(model)
        templates = [t["name"] for t in model.get("tmpls", [])]
        data = {
            "id": model["id"],
            "name": model["name"],
            "fields": ", ".join(field_names),
            "templates": ", ".join(templates),
            "css_length": len(model.get("css", "")),
            "sort_field": field_names[model.get("sortf", 0)] if field_names else "?",
        }
        print_single(data, title=f"Note Type: {name}")


@app.command()
def create(name: str = typer.Argument(..., help="New note type name")) -> None:
    """Create a new note type (with Front/Back fields)."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        model = col.models.new(name)
        front = col.models.new_field("Front")
        col.models.add_field(model, front)
        back = col.models.new_field("Back")
        col.models.add_field(model, back)
        tmpl = col.models.new_template("Card 1")
        tmpl["qfmt"] = "{{Front}}"
        tmpl["afmt"] = "{{FrontSide}}<hr id=answer>{{Back}}"
        col.models.add_template(model, tmpl)
        col.models.add(model)
        print_success(f"Created note type '{name}' with Front/Back fields")


@app.command()
def copy(
    name: str = typer.Argument(..., help="Source note type name"),
    new_name: str = typer.Argument(..., help="New copy name"),
) -> None:
    """Copy a note type."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        model = col.models.by_name(name)
        if not model:
            print_error(f"Note type '{name}' not found")
            raise typer.Exit(1)
        new_model = col.models.copy(model)
        new_model["name"] = new_name
        col.models.update_dict(new_model)
        print_success(f"Copied '{name}' as '{new_name}'")


@app.command()
def delete(name: str = typer.Argument(..., help="Note type to delete")) -> None:
    """Delete a note type (and all its notes!)."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        mid = col.models.id_for_name(name)
        if not mid:
            print_error(f"Note type '{name}' not found")
            raise typer.Exit(1)
        count = col.models.use_count(col.models.get(mid))
        if count > 0:
            typer.confirm(f"This will delete {count} note(s). Continue?", abort=True)
        col.models.remove(mid)
        print_success(f"Deleted note type '{name}'")


@app.command("add-field")
def add_field(
    notetype_name: str = typer.Argument(..., help="Note type name"),
    field_name: str = typer.Argument(..., help="New field name"),
) -> None:
    """Add a field to a note type."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        model = col.models.by_name(notetype_name)
        if not model:
            print_error(f"Note type '{notetype_name}' not found")
            raise typer.Exit(1)
        field = col.models.new_field(field_name)
        col.models.add_field(model, field)
        col.models.save(model)
        print_success(f"Added field '{field_name}' to '{notetype_name}'")


@app.command("remove-field")
def remove_field(
    notetype_name: str = typer.Argument(..., help="Note type name"),
    field_name: str = typer.Argument(..., help="Field name to remove"),
) -> None:
    """Remove a field from a note type."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        model = col.models.by_name(notetype_name)
        if not model:
            print_error(f"Note type '{notetype_name}' not found")
            raise typer.Exit(1)
        fmap = col.models.field_map(model)
        if field_name not in fmap:
            print_error(f"Field '{field_name}' not found")
            raise typer.Exit(1)
        field = model["flds"][fmap[field_name][0]]
        col.models.remove_field(model, field)
        col.models.save(model)
        print_success(f"Removed field '{field_name}' from '{notetype_name}'")


@app.command("rename-field")
def rename_field(
    notetype_name: str = typer.Argument(..., help="Note type name"),
    old_name: str = typer.Argument(..., help="Current field name"),
    new_name: str = typer.Argument(..., help="New field name"),
) -> None:
    """Rename a field in a note type."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        model = col.models.by_name(notetype_name)
        if not model:
            print_error(f"Note type '{notetype_name}' not found")
            raise typer.Exit(1)
        fmap = col.models.field_map(model)
        if old_name not in fmap:
            print_error(f"Field '{old_name}' not found")
            raise typer.Exit(1)
        field = model["flds"][fmap[old_name][0]]
        col.models.rename_field(model, field, new_name)
        col.models.save(model)
        print_success(f"Renamed field '{old_name}' -> '{new_name}'")


@app.command("add-template")
def add_template(
    notetype_name: str = typer.Argument(..., help="Note type name"),
    template_name: str = typer.Argument(..., help="New template name"),
) -> None:
    """Add a card template to a note type."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        model = col.models.by_name(notetype_name)
        if not model:
            print_error(f"Note type '{notetype_name}' not found")
            raise typer.Exit(1)
        tmpl = col.models.new_template(template_name)
        col.models.add_template(model, tmpl)
        col.models.save(model)
        print_success(f"Added template '{template_name}' to '{notetype_name}'")


@app.command("remove-template")
def remove_template(
    notetype_name: str = typer.Argument(..., help="Note type name"),
    template_name: str = typer.Argument(..., help="Template name to remove"),
) -> None:
    """Remove a card template from a note type."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        model = col.models.by_name(notetype_name)
        if not model:
            print_error(f"Note type '{notetype_name}' not found")
            raise typer.Exit(1)
        tmpl = None
        for t in model.get("tmpls", []):
            if t["name"] == template_name:
                tmpl = t
                break
        if not tmpl:
            print_error(f"Template '{template_name}' not found")
            raise typer.Exit(1)
        col.models.remove_template(model, tmpl)
        col.models.save(model)
        print_success(f"Removed template '{template_name}' from '{notetype_name}'")


@app.command()
def restore(name: str = typer.Argument(..., help="Note type name to restore")) -> None:
    """Restore a note type to its built-in/stock version."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        mid = col.models.id_for_name(name)
        if not mid:
            print_error(f"Note type '{name}' not found")
            raise typer.Exit(1)
        col.models.restore_notetype_to_stock(mid)
        print_success(f"Restored '{name}' to stock version")


@app.command("fields")
def notetype_fields(name: str = typer.Argument(..., help="Note type name")) -> None:
    """List fields of a note type."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        model = col.models.by_name(name)
        if not model:
            print_error(f"Note type '{name}' not found")
            raise typer.Exit(1)
        field_names = col.models.field_names(model)
        sort_idx = col.models.sort_idx(model)
        rows = [
            {"index": i, "name": f, "is_sort": i == sort_idx}
            for i, f in enumerate(field_names)
        ]
        print_table(rows, title=f"Fields: {name}")
