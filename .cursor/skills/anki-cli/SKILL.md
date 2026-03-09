---
name: anki-cli
description: >-
  Anki CLI operations expert. Knows how to query decks, search cards, review, import/export, stats via anki-cli.
  Callable by other skills for Anki data operations. Suggests new commands when existing ones are insufficient.
  Use this when user writes in English. Triggers: anki-cli, query cards, deck list, Anki operations, review stats.
---

# Anki CLI Operations Expert

anki-cli is this repo's Anki command-line tool, sharing the same Rust core as Anki GUI.
This skill knows all its capabilities and helps users or other skills perform Anki data operations.

> **First use**: Read [INSTALL.md](INSTALL.md) to enable this skill in your IDE.

## Environment

| Item | Value |
|------|-------|
| Tool path | Repo root (skill and anki-cli same repo) |
| Execution | `anki-cli <cmd>` or `python -m ankicli <cmd>` (after `pip install -e .`) |
| Virtual env | `.venv/` (if used) |
| Global options | `--profile <name>` · `--json` · `--path <db>` · `--verbose` · `--lang zh|en` |
| Profile | Default `User 1`; use `deck list` to confirm, then `--profile "<name>"` if needed |

## Connection Modes

| Mode | Condition | Command prefix |
|------|-----------|----------------|
| Direct | Anki GUI **closed** | `anki-cli <cmd>` |
| AnkiConnect | Anki GUI **running** + plugin 2055492159 | `anki-cli ac <cmd>` |

CLI will prompt to switch to ac mode when direct mode fails.

## Standard Steps

1. Determine profile: default `User 1`; use `--profile "<name>"` for multiple profiles
2. Determine mode: GUI closed → direct; GUI running → ac
3. Add `--json` when structured output is needed (for scripts or skills)

### Command template

```bash
anki-cli --profile "User 1" --json <subcommand> [args]
```

## Core Commands

Full list in [reference.md](reference.md).
Common recipes (10 cross-discipline scenarios): [recipes.md](recipes.md).

| Scenario | Command |
|----------|---------|
| List decks | `deck list` / `deck tree` |
| Search cards | `search cards "<query>"` |
| View due | `review due --deck "<deck>"` |
| Get next card | `review next --deck "<deck>"` |
| Submit rating | `review answer <card_id> --ease <1-4>` |
| Batch rating | `review answer-batch --data '[{"card_id":N,"ease":M}]'` |
| Today stats | `stats today` |
| Deck stats | `stats deck` |
| Card details | `card info <card_id>` |
| Review log | `card revlog <card_id>` |
| Add note | `note add --deck "<deck>" --type "<notetype>" --fields '{"Front":"x","Back":"y"}'` |
| Batch add | `note add-batch --file data.json` |
| FSRS memory | `stats memory <card_id>` |
| Export | `export apkg --deck "<deck>" --output out.apkg` |
| Sync | `sync collection` |

### Anki Search Syntax

`search cards` uses Anki native search:

| Filter | Syntax |
|--------|--------|
| Deck | `"deck:DeckName"` |
| Tag | `tag:TagName` |
| Due | `is:due` |
| New | `is:new` |
| Suspended | `is:suspended` |
| Field | `"front:keyword"` |
| Combine | space = AND; `OR` for OR |
| Negate | `-is:suspended` |

## Building-Block Philosophy

**Principle**: Each anki-cli command is a building block, not a complete solution.
New needs should try **combining existing blocks**; when that fails, identify **which block is missing**

Known gaps in [known-gaps.md](known-gaps.md).

### Flow

1. **Can combine?** Use existing commands (reference.md) → execute
2. **Missing block?** Where does the chain break? What atomic capability is missing?
3. **Check gaps**: Is it in known-gaps.md?
4. **Suggest block**: Propose minimal command design

### Anti-patterns

- **Don't** design one-purpose commands for specific scenarios
- **Do** design generic blocks for user/AI to combine freely

## Companion Teaching Skills

anki-cli ships with ready-to-use Skills that demonstrate how to build Anki-driven practice workflows:

| Skill | Path | Description |
|-------|------|-------------|
| **anki-report** | `../anki-report/SKILL.md` | Learning analytics: daily/weekly/monthly reports, 7-dimension insight engine |
| **wenyan-translator** | `../wenyan-translator/SKILL.md` | Classical Chinese translation (scaffolding pedagogy + Anki) |
| **shanghai-english-translator** | `../shanghai-english-translator/SKILL.md` | Shanghai Gaokao English translation (examiner perspective + Anki) |

Full guide: [companion-skills.md](companion-skills.md)

## For Other Skills

When other skills need Anki operations:

1. Read this SKILL.md for command format
2. Use Shell tool to run anki-cli (add `--json` for structured output)
3. Parse JSON result

### Common Integration Scenarios

| Scenario | Recommended |
|----------|-------------|
| Fetch due cards | `review due --deck "<deck>" --limit N --json` or `review next --deck "<deck>" --json` |
| Write back rating | `review answer <card_id> --ease <1-4>` or `review answer-batch` |
| Get card fields | `card info <card_id> --json` |
| Add supplement card | `note add --deck ... --type ... --fields '{...}'` |
| Today study count | `stats today --profile "<name>"` |
