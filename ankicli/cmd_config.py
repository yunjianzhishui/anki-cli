"""Configuration and preferences commands."""

from __future__ import annotations

import json

import typer

from ankicli.connection import open_collection
from ankicli.output import print_error, print_json, print_single, print_success, is_json_mode

app = typer.Typer(no_args_is_help=True)


def _get_state():
    from ankicli.main import state
    return state


@app.command()
def get(key: str = typer.Argument(..., help="Configuration key")) -> None:
    """Get a configuration value."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        value = col.get_config(key)
        if value is None:
            print_error(f"Key '{key}' not found")
            raise typer.Exit(1)
        if is_json_mode():
            print_json({"key": key, "value": value})
        else:
            print_single({"key": key, "value": str(value)})


@app.command()
def set(
    key: str = typer.Argument(..., help="Configuration key"),
    value: str = typer.Argument(..., help="Value (JSON-encoded for complex types)"),
) -> None:
    """Set a configuration value."""
    s = _get_state()
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        parsed = value

    with open_collection(s.profile, s.path) as col:
        col.set_config(key, parsed)
        print_success(f"Set '{key}' = {parsed}")


@app.command("list")
def config_list() -> None:
    """List all configuration key-value pairs."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        all_conf = col.all_config()
        if is_json_mode():
            print_json(all_conf)
        else:
            from ankicli.output import print_table
            rows = []
            for k, v in sorted(all_conf.items()):
                val_str = str(v)
                if len(val_str) > 80:
                    val_str = val_str[:77] + "..."
                rows.append({"key": k, "value": val_str})
            print_table(rows, title="Configuration")


@app.command()
def preferences() -> None:
    """Show Anki preferences."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        prefs = col.get_preferences()
        sched = prefs.scheduling
        reviewing = prefs.reviewing
        editing = prefs.editing
        data = {
            "learn_ahead_secs": sched.learn_ahead_secs,
            "new_timezone": sched.new_timezone,
            "day_learn_first": sched.day_learn_first,
            "timebox_secs": reviewing.time_limit_secs,
            "show_remaining_due_counts": reviewing.show_remaining_due_counts,
            "show_intervals_on_buttons": reviewing.show_intervals_on_buttons,
            "adding_defaults_to_current_deck": editing.adding_defaults_to_current_deck,
            "paste_strips_formatting": editing.paste_strips_formatting,
        }
        print_single(data, title="Preferences")


@app.command("set-preferences")
def set_preferences(
    key: str = typer.Option(..., "--key", "-k", help="Preference key (e.g. 'learn_ahead_secs')"),
    value: str = typer.Option(..., "--value", "-v", help="New value"),
) -> None:
    """Modify a specific preference."""
    s = _get_state()
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        parsed = value

    with open_collection(s.profile, s.path) as col:
        prefs = col.get_preferences()
        sections = {
            "learn_ahead_secs": ("scheduling", "learn_ahead_secs"),
            "new_timezone": ("scheduling", "new_timezone"),
            "day_learn_first": ("scheduling", "day_learn_first"),
            "time_limit_secs": ("reviewing", "time_limit_secs"),
            "show_remaining_due_counts": ("reviewing", "show_remaining_due_counts"),
            "show_intervals_on_buttons": ("reviewing", "show_intervals_on_buttons"),
            "adding_defaults_to_current_deck": ("editing", "adding_defaults_to_current_deck"),
            "paste_strips_formatting": ("editing", "paste_strips_formatting"),
        }
        if key not in sections:
            print_error(f"Unknown preference key '{key}'. Available: {list(sections.keys())}")
            raise typer.Exit(1)

        section_name, attr = sections[key]
        section = getattr(prefs, section_name)
        setattr(section, attr, parsed)
        col.set_preferences(prefs)
        print_success(f"Set preference '{key}' = {parsed}")
