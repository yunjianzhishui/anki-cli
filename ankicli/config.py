"""anki-cli configuration: language and other user preferences."""

from __future__ import annotations

import json
import os
import platform
from pathlib import Path
from typing import Any


def get_config_path() -> Path:
    """Return the path to anki-cli config file."""
    if platform.system() == "Windows":
        base = os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming"))
        return Path(base) / "anki-cli" / "config.json"
    data_home = os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))
    return Path(data_home) / "anki-cli" / "config.json"


def load_config() -> dict[str, Any]:
    """Load config from disk. Returns empty dict if not found."""
    path = get_config_path()
    if not path.exists():
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_config(data: dict[str, Any]) -> None:
    """Save config to disk."""
    path = get_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_lang() -> str:
    """Return current language: 'zh' or 'en'. Defaults to 'en'."""
    cfg = load_config()
    lang = cfg.get("lang", "en")
    return "zh" if lang == "zh" else "en"


def set_lang(lang: str) -> None:
    """Set and persist language. lang must be 'zh' or 'en'."""
    if lang not in ("zh", "en"):
        raise ValueError("lang must be 'zh' or 'en'")
    cfg = load_config()
    cfg["lang"] = lang
    save_config(cfg)


def config_exists() -> bool:
    """Return True if config file exists."""
    return get_config_path().exists()
