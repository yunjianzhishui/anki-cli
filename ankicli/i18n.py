"""Internationalization: translated strings for CLI output."""

from __future__ import annotations

# Override for current run (e.g. from --lang). None = use config.
_lang_override: str | None = None


def set_lang_override(lang: str | None) -> None:
    """Set language override for current process. None to use config."""
    global _lang_override
    _lang_override = lang


def get_current_lang() -> str:
    """Return effective language for this run: 'zh' or 'en'."""
    if _lang_override is not None:
        return _lang_override
    from ankicli.config import get_lang
    return get_lang()

# Keys are used in code; values are per-language.
STRINGS: dict[str, dict[str, str]] = {
    # output.py
    "ok": {"en": "OK", "zh": "成功"},
    "error": {"en": "Error", "zh": "错误"},
    # connection.py
    "collection_not_found": {"en": "collection not found at {path}", "zh": "未找到集合: {path}"},
    "available_profiles": {"en": "Available profiles", "zh": "可用 profiles"},
    "hint_gui_running": {
        "en": "Hint: Anki GUI is running. Use 'anki-cli ac' commands for AnkiConnect mode,\n      or close Anki GUI to use direct mode.",
        "zh": "提示：Anki GUI 正在运行。请使用 'anki-cli ac' 命令（AnkiConnect 模式），\n      或关闭 Anki GUI 后使用直接模式。",
    },
    "error_gui_locked": {
        "en": "Error: Anki GUI has the database locked.\n  Option 1: Close Anki GUI, then retry.\n  Option 2: Install AnkiConnect plugin (code: 2055492159),\n            then use 'anki-cli ac' commands.",
        "zh": "错误：Anki GUI 已锁定数据库。\n  选项 1：关闭 Anki GUI 后重试。\n  选项 2：安装 AnkiConnect 插件（代码: 2055492159），然后使用 'anki-cli ac' 命令。",
    },
    "error_ankiconnect_unavailable": {
        "en": "Error: AnkiConnect not available.\nMake sure Anki is running and AnkiConnect plugin is installed (code: 2055492159).",
        "zh": "错误：AnkiConnect 不可用。\n请确保 Anki 正在运行且已安装 AnkiConnect 插件（代码: 2055492159）。",
    },
    # first-run prompt
    "choose_language": {
        "en": "Choose language / 选择语言:",
        "zh": "Choose language / 选择语言:",
    },
    "opt_zh": {"en": "[1] 中文", "zh": "[1] 中文"},
    "opt_en": {"en": "[2] English (default)", "zh": "[2] English (default)"},
    "lang_set_zh": {"en": "Language set to 中文.", "zh": "已切换为中文。"},
    "lang_set_en": {"en": "Language set to English.", "zh": "已切换为 English。"},
    "lang_current": {"en": "Current language: {lang}", "zh": "当前语言: {lang}"},
    "lang_zh": {"en": "Chinese", "zh": "中文"},
    "lang_en": {"en": "English", "zh": "English"},
}


def _(key: str, **kwargs: str) -> str:
    """Return translated string for key. Falls back to English if key missing."""
    lang = get_current_lang()
    tbl = STRINGS.get(key, {})
    s = tbl.get(lang) or tbl.get("en") or key
    return s.format(**kwargs) if kwargs else s
