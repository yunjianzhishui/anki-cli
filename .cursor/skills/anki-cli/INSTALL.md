# anki-cli Skill Installation & Registration

This skill lets AI assistants (e.g. Cursor) use anki-cli directly in conversation. Choose the method for your IDE.

---

## Cursor (recommended)

### Method 1: Open repo directly (recommended)

1. Open **anki-cli repo root** in Cursor (File → Open Folder → select anki-cli)
2. No extra steps; skill auto-loads at `.cursor/skills/anki-cli/`
3. In chat, say "list decks", "query cards", "review stats", etc.; AI will call anki-cli

### Method 2: anki-cli as subfolder

If your workspace is a parent folder (e.g. `my-project/`) with anki-cli at `my-project/anki-cli/`:

1. Copy `anki-cli/.cursor/skills/anki-cli/` to `my-project/.cursor/skills/anki-cli/`
2. Ensure `my-project/.cursor/skills/` exists
3. Reopen Cursor or refresh workspace

### Verify

In Cursor chat: `list my decks` or `anki-cli deck list`; AI should run and return results.

---

## Other IDEs (VS Code, JetBrains, etc.)

This skill format is **Cursor-specific**. Other IDEs with AI assistants (Copilot, Codeium, etc.) can try:

1. **Copy SKILL.md content**: Paste `.cursor/skills/anki-cli/SKILL.md` into your AI's custom instructions / rules / system prompt
2. **As reference**: Use `SKILL.md` and `reference.md` as project docs; reference manually when needed

Each IDE varies; check its docs for AI integration.

---

## Language Switching

- **CLI**: First run prompts for language (中文/English). Later: `anki-cli lang set zh` or `anki-cli lang set en`
- **Skill**: AI picks SKILL.md (English) or SKILL_zh.md (Chinese) based on user message language.

---

## Prerequisites

- `pip install -e .` to install anki-cli
- Anki desktop installed (for daily review)
- Direct mode: Anki GUI closed; AnkiConnect mode: GUI running + AnkiConnect plugin (2055492159)
