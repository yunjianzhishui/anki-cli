"""Language selection subcommand."""

from __future__ import annotations

import typer

from ankicli import i18n
from ankicli.config import config_exists, get_lang, set_lang

app = typer.Typer(no_args_is_help=True)


@app.command("set")
def lang_set(lang: str = typer.Argument(..., help="Language: zh or en")) -> None:
    """Set and persist interface language."""
    if lang not in ("zh", "en"):
        typer.echo("Language must be 'zh' or 'en'.", err=True)
        raise typer.Exit(1)
    set_lang(lang)
    i18n.set_lang_override(lang)
    msg = i18n._("lang_set_zh") if lang == "zh" else i18n._("lang_set_en")
    typer.echo(msg)


@app.command("show")
def lang_show() -> None:
    """Show current language."""
    lang = get_lang()
    label = i18n._("lang_zh") if lang == "zh" else i18n._("lang_en")
    typer.echo(i18n._("lang_current", lang=label))
