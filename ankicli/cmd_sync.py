"""Sync commands."""

from __future__ import annotations

import typer

from ankicli.connection import open_collection
from ankicli.output import print_error, print_single, print_success

app = typer.Typer(no_args_is_help=True)


def _get_state():
    from ankicli.main import state
    return state


@app.command()
def login(
    user: str = typer.Option(..., "--user", "-u", help="AnkiWeb username/email"),
    password: str = typer.Option(..., "--pass", "-p", help="AnkiWeb password", prompt=True, hide_input=True),
    endpoint: str = typer.Option(None, "--endpoint", help="Custom sync endpoint"),
) -> None:
    """Login to AnkiWeb and display auth token."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        auth = col.sync_login(user, password, endpoint)
        print_single({
            "hkey": auth.hkey,
            "endpoint": auth.endpoint or "(default)",
        }, title="Sync Login")


@app.command()
def collection(
    user: str = typer.Option(..., "--user", "-u", help="AnkiWeb username"),
    password: str = typer.Option(..., "--pass", "-p", help="AnkiWeb password", prompt=True, hide_input=True),
    media: bool = typer.Option(True, "--media/--no-media", help="Also sync media"),
) -> None:
    """Sync collection with AnkiWeb."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        auth = col.sync_login(user, password, None)
        result = col.sync_collection(auth, sync_media=media)
        print_single({
            "required": str(result.required),
            "server_message": result.server_message or "(none)",
        }, title="Sync Result")


@app.command()
def media(
    user: str = typer.Option(..., "--user", "-u", help="AnkiWeb username"),
    password: str = typer.Option(..., "--pass", "-p", help="AnkiWeb password", prompt=True, hide_input=True),
) -> None:
    """Sync media files with AnkiWeb."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        auth = col.sync_login(user, password, None)
        col.sync_media(auth)
        print_success("Media sync complete")


@app.command()
def status(
    user: str = typer.Option(..., "--user", "-u", help="AnkiWeb username"),
    password: str = typer.Option(..., "--pass", "-p", help="AnkiWeb password", prompt=True, hide_input=True),
) -> None:
    """Check sync status."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        auth = col.sync_login(user, password, None)
        sync_status = col.sync_status(auth)
        print_single({
            "required": str(sync_status.required),
            "new_endpoint": sync_status.new_endpoint or "(none)",
        }, title="Sync Status")


@app.command("full-upload")
def full_upload(
    user: str = typer.Option(..., "--user", "-u", help="AnkiWeb username"),
    password: str = typer.Option(..., "--pass", "-p", help="AnkiWeb password", prompt=True, hide_input=True),
) -> None:
    """Full upload: replace AnkiWeb with local collection."""
    s = _get_state()
    typer.confirm("This will REPLACE your AnkiWeb collection with the local one. Continue?", abort=True)
    with open_collection(s.profile, s.path) as col:
        auth = col.sync_login(user, password, None)
        col.full_upload_or_download(auth=auth, server_usn=None, upload=True)
        print_success("Full upload complete")


@app.command("full-download")
def full_download(
    user: str = typer.Option(..., "--user", "-u", help="AnkiWeb username"),
    password: str = typer.Option(..., "--pass", "-p", help="AnkiWeb password", prompt=True, hide_input=True),
) -> None:
    """Full download: replace local collection with AnkiWeb's."""
    s = _get_state()
    typer.confirm("This will REPLACE your local collection with AnkiWeb's. Continue?", abort=True)
    with open_collection(s.profile, s.path) as col:
        auth = col.sync_login(user, password, None)
        col.full_upload_or_download(auth=auth, server_usn=None, upload=False)
        print_success("Full download complete")
