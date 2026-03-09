"""Collection connection management: locate, open, and close Anki databases.

Two modes:
  - Direct mode: opens collection.anki2 via Anki's Rust backend (GUI must be closed)
  - AnkiConnect mode: proxies requests to the running Anki GUI via HTTP (GUI must be open)

The open_collection() context manager automatically picks the right mode.
"""

from __future__ import annotations

import json
import os
import platform
import sys
import urllib.request
import urllib.error
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator

from anki.collection import Collection

from ankicli import i18n

ANKICONNECT_URL = "http://127.0.0.1:8765"


def detect_anki_base() -> Path:
    """Return the Anki base directory for the current platform."""
    system = platform.system()
    if system == "Windows":
        base = os.environ.get("APPDATA")
        if base:
            return Path(base) / "Anki2"
        return Path.home() / "AppData" / "Roaming" / "Anki2"
    elif system == "Darwin":
        return Path.home() / "Library" / "Application Support" / "Anki2"
    else:
        data_home = os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share"))
        return Path(data_home) / "Anki2"


def detect_collection_path(profile: str = "User 1") -> str:
    """Return the full path to collection.anki2 for the given profile."""
    col_path = detect_anki_base() / profile / "collection.anki2"
    if not col_path.exists():
        profiles = list_profiles()
        msg = i18n._("collection_not_found", path=str(col_path))
        print(f"{i18n._('error')}: {msg}\n{i18n._('available_profiles')}: {profiles}", file=sys.stderr)
        raise SystemExit(1)
    return str(col_path)


def list_profiles() -> list[str]:
    """List available Anki profile names."""
    base = detect_anki_base()
    if not base.exists():
        return []
    return [
        d.name
        for d in base.iterdir()
        if d.is_dir() and (d / "collection.anki2").exists()
    ]


# ── AnkiConnect proxy ────────────────────────────────────────────────────────

def ankiconnect_available() -> bool:
    """Check if AnkiConnect is responding."""
    try:
        result = ankiconnect_invoke("version")
        return result is not None
    except Exception:
        return False


def ankiconnect_invoke(action: str, params: dict | None = None) -> Any:
    """Call an AnkiConnect action. Raises on failure."""
    payload = json.dumps({
        "action": action,
        "version": 6,
        "params": params or {},
    }).encode("utf-8")
    req = urllib.request.Request(
        ANKICONNECT_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    if result.get("error"):
        raise RuntimeError(f"AnkiConnect: {result['error']}")
    return result.get("result")


class AnkiConnectProxy:
    """Lightweight proxy that mimics a subset of Collection API via AnkiConnect.

    When the Anki GUI is running (and has the DB locked), CLI commands
    can use this proxy instead of opening the Collection directly.
    """

    def __init__(self) -> None:
        self._is_proxy = True

    def invoke(self, action: str, **params: Any) -> Any:
        return ankiconnect_invoke(action, params if params else None)

    # ── Deck operations ──

    def deck_names_and_ids(self) -> dict[str, int]:
        return self.invoke("deckNamesAndIds")

    def deck_names(self) -> list[str]:
        return self.invoke("deckNames")

    def create_deck(self, name: str) -> int:
        return self.invoke("createDeck", deck=name)

    def delete_decks(self, names: list[str]) -> None:
        self.invoke("deleteDecks", decks=names, cardsToo=True)

    # ── Card operations ──

    def find_cards(self, query: str) -> list[int]:
        return self.invoke("findCards", query=query)

    def cards_info(self, card_ids: list[int]) -> list[dict]:
        return self.invoke("cardsInfo", cards=card_ids)

    def answer_cards(self, answers: list[dict]) -> list[bool]:
        return self.invoke("answerCards", answers=answers)

    def suspend_cards(self, card_ids: list[int]) -> bool:
        return self.invoke("suspend", cards=card_ids)

    def unsuspend_cards(self, card_ids: list[int]) -> bool:
        return self.invoke("unsuspend", cards=card_ids)

    # ── Note operations ──

    def find_notes(self, query: str) -> list[int]:
        return self.invoke("findNotes", query=query)

    def notes_info(self, note_ids: list[int]) -> list[dict]:
        return self.invoke("notesInfo", notes=note_ids)

    def add_note(self, note: dict) -> int:
        return self.invoke("addNote", note=note)

    def delete_notes(self, note_ids: list[int]) -> None:
        self.invoke("deleteNotes", notes=note_ids)

    def update_note_fields(self, note_id: int, fields: dict) -> None:
        self.invoke("updateNoteFields", note={"id": note_id, "fields": fields})

    # ── Tag operations ──

    def get_tags(self) -> list[str]:
        return self.invoke("getTags")

    def add_tags(self, note_ids: list[int], tags: str) -> None:
        self.invoke("addTags", notes=note_ids, tags=tags)

    def remove_tags(self, note_ids: list[int], tags: str) -> None:
        self.invoke("removeTags", notes=note_ids, tags=tags)

    # ── Stats ──

    def get_num_cards_reviewed_today(self) -> int:
        return self.invoke("getNumCardsReviewedToday")

    def get_collection_stats_html(self) -> str:
        return self.invoke("getCollectionStatsHTML")

    # ── Model (notetype) ──

    def model_names(self) -> list[str]:
        return self.invoke("modelNames")

    def model_field_names(self, model_name: str) -> list[str]:
        return self.invoke("modelFieldNames", modelName=model_name)

    # ── Sync ──

    def sync(self) -> None:
        self.invoke("sync")

    def close(self) -> None:
        pass  # nothing to close


# ── Main connection logic ─────────────────────────────────────────────────────

@contextmanager
def open_collection(
    profile: str = "User 1",
    path: str | None = None,
) -> Generator[Collection, None, None]:
    """Context manager that opens a Collection, or raises with guidance."""
    col_path = path or detect_collection_path(profile)

    try:
        col = Collection(col_path)
    except Exception as e:
        err_msg = str(e)
        if "already open" in err_msg.lower() or "locked" in err_msg.lower():
            if ankiconnect_available():
                print(i18n._("hint_gui_running"), file=sys.stderr)
            else:
                print(i18n._("error_gui_locked"), file=sys.stderr)
            raise SystemExit(1)
        raise

    try:
        yield col
    finally:
        col.close()


@contextmanager
def open_ankiconnect() -> Generator[AnkiConnectProxy, None, None]:
    """Context manager for AnkiConnect proxy (when GUI is running)."""
    if not ankiconnect_available():
        print(i18n._("error_ankiconnect_unavailable"), file=sys.stderr)
        raise SystemExit(1)
    proxy = AnkiConnectProxy()
    try:
        yield proxy
    finally:
        proxy.close()
