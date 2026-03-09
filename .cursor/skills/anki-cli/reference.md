# anki-cli Command Reference

> Prefix: `anki-cli [global options] <subcommand>` (run `pip install -e .` first)

## Global Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--profile TEXT` | `-p` | Anki profile name | `User 1` |
| `--path TEXT` | — | collection.anki2 path | auto-detect |
| `--json` | `-j` | JSON output | off |
| `--lang zh|en` | `-l` | Interface language | config |
| `--verbose` | `-v` | Verbose logging | off |
| `--version` | — | Version | — |

---

## deck — Deck management

| Command | Description | Key params |
|---------|--------------|------------|
| `deck list` | List all decks | — |
| `deck tree` | Tree view | — |
| `deck create "<name>"` | Create deck (`::` for nesting) | — |
| `deck rename "<old>" "<new>"` | Rename | — |
| `deck delete "<name>"` | Delete | — |
| `deck move "<name>" --parent "<parent>"` | Move | — |
| `deck info "<name>"` | Details & config | — |
| `deck select "<name>"` | Set current deck | — |
| `deck current` | Show current deck | — |
| `deck count "<name>"` | Card count | — |
| `deck create-filtered "<name>" --query "<q>"` | Create filtered deck | `--limit` |
| `deck rebuild-filtered "<name>"` | Rebuild filtered deck | — |

## card — Card operations

| Command | Description | Key params |
|---------|--------------|------------|
| `card info <id>` | Fields, state, scheduling | — |
| `card info-batch "<ids>"` | Batch card details | comma-sep IDs |
| `card stats <id>` | Stats (avg/total time) | — |
| `card revlog <id>` | Review log | — |
| `card move "<ids>" --deck "<deck>"` | Move cards | comma-sep IDs |
| `card suspend "<ids>"` | Suspend | — |
| `card unsuspend "<ids>"` | Unsuspend | — |
| `card bury "<ids>"` | Bury until tomorrow | — |
| `card unbury "<ids>"` | Unbury | — |
| `card flag "<ids>" --flag <0-7>` | Set flag | 0=none,1=red,2=orange... |
| `card forget "<ids>"` | Reset to new | — |
| `card set-due "<ids>" --days <N>` | Set due date | 0=today |
| `card reposition "<ids>" --start <N>` | Reposition new cards | `--step`, `--randomize` |
| `card delete "<ids>"` | Delete | — |

## note — Note operations

| Command | Description | Key params |
|---------|--------------|------------|
| `note add --deck "<d>" --type "<t>" --fields '<json>'` | Add note | `--tags` |
| `note add-batch --file <f>` | Batch add from JSON | `--deck`, `--type` |
| `note info <id>` | Note details | — |
| `note edit <id> --field "<name>" --value "<val>"` | Edit field | — |
| `note delete "<ids>"` | Delete notes | — |
| `note find-replace --field "<f>" --find "<s>" --replace "<r>"` | Find & replace | `--query` |
| `note duplicates --field "<f>"` | Find duplicates | `--query` |
| `note fields <id>` | Show field names & values | — |
| `note cards <id>` | Linked cards | — |

## review — Review flow

| Command | Description | Key params |
|---------|--------------|------------|
| `review start` | Interactive terminal review | `--deck` |
| `review next` | Get next card (for scripts) | `--deck` |
| `review answer <card_id> --ease <1-4>` | Submit rating | 1=Again,2=Hard,3=Good,4=Easy |
| `review answer-batch --data '<json>'` | Batch rating | JSON array |
| `review counts` | New/learn/review counts | `--deck` |
| `review due` | List due cards (incl. `overdue_days`) | `--deck`, `--limit` |
| `review undo` | Undo | — |

## search — Search

| Command | Description | Key params |
|---------|--------------|------------|
| `search cards "<query>"` | Search cards | `--limit`, `--order` |
| `search notes "<query>"` | Search notes | `--limit` |
| `search empty-cards` | Find empty cards | — |
| `search build "<parts>"` | Build search string | `--joiner` |

## tag — Tag management

| Command | Description |
|---------|-------------|
| `tag list` | List all tags |
| `tag tree` | Tree view |
| `tag add "<note_ids>" --tags "<tags>"` | Add tags |
| `tag remove "<note_ids>" --tags "<tags>"` | Remove tags |
| `tag rename "<old>" "<new>"` | Rename |
| `tag delete "<tag>"` | Delete |
| `tag clear-unused` | Clear unused |

## notetype — Note type management

| Command | Description |
|---------|-------------|
| `notetype list` | List (with usage count) |
| `notetype info "<name>"` | Details |
| `notetype create "<name>"` | Create |
| `notetype copy "<name>" "<new>"` | Copy |
| `notetype delete "<name>"` | Delete |
| `notetype add-field "<type>" "<field>"` | Add field |
| `notetype remove-field "<type>" "<field>"` | Remove field |
| `notetype rename-field "<type>" "<old>" "<new>"` | Rename field |
| `notetype fields "<name>"` | List fields |

## import — Import

| Command | Description |
|---------|-------------|
| `import apkg "<file>"` | Import .apkg |
| `import colpkg "<file>"` | Import .colpkg (replace collection) |
| `import csv "<file>" --deck "<d>" --type "<t>"` | Import CSV |
| `import json "<file>" --deck "<d>" --type "<t>"` | Import JSON |
| `import csv-preview "<file>"` | Preview CSV metadata |

## export — Export

| Command | Description |
|---------|-------------|
| `export apkg --deck "<d>" --output "<f>"` | Export .apkg |
| `export colpkg --output "<f>"` | Export .colpkg |
| `export notes-csv --output "<f>"` | Notes CSV |
| `export cards-csv --output "<f>"` | Cards CSV |
| `export dataset` | FSRS training dataset |

## sync — Sync

| Command | Description |
|---------|-------------|
| `sync login --user "<u>" --password "<p>"` | Login AnkiWeb |
| `sync collection` | Sync collection |
| `sync media` | Sync media |
| `sync status` | Sync status |
| `sync full-upload` | Full upload |
| `sync full-download` | Full download |

## stats — Statistics

| Command | Description |
|---------|-------------|
| `stats today` | Today stats (studied_today) |
| `stats card <id>` | Single card stats |
| `stats deck` | Deck due overview |
| `stats memory <id>` | FSRS memory state |
| `stats overview` | Global overview |

## media / config / db / scheduler

| Command | Description |
|---------|-------------|
| `media check` | Media integrity check |
| `media add "<file>"` | Add media |
| `config get "<key>"` | Get config |
| `config set "<key>" "<val>"` | Set config |
| `db check` | DB integrity check/repair |
| `db optimize` | VACUUM + ANALYZE |
| `db backup` | Create backup |
| `db info` | DB info |
| `scheduler version` | Scheduler version |
| `scheduler set-v3 --enable/--disable` | Enable/disable v3 |

## revlog — Review log query

| Command | Description | Key params |
|---------|--------------|------------|
| `revlog query` | Query by date range | `--days N`, `--since`, `--until`, `--unique`, `--limit` |
| `revlog summary` | Review activity summary | `--days N`, `--since`, `--until`, `--group-by day\|card`, `--limit` |

## lang — Language

| Command | Description |
|---------|-------------|
| `lang set zh` | Set interface to Chinese |
| `lang set en` | Set interface to English |
| `lang show` | Show current language |

## ac — AnkiConnect mode (GUI running)

| Command | Description |
|---------|-------------|
| `ac decks` | List decks |
| `ac due` | Due cards |
| `ac counts` | Today review count |
| `ac search "<query>"` | Search |
| `ac add --front "<f>" --back "<b>"` | Add note |
| `ac answer <card_id> --ease <1-4>` | Rate |
| `ac suspend/unsuspend "<ids>"` | Suspend/unsuspend |
| `ac tags` | List tags |
| `ac add-tags "<note_ids>" --tags "<t>"` | Add tags |
| `ac notetypes` | Note types |
| `ac sync` | Trigger sync |
| `ac delete-notes "<ids>"` | Delete notes |
