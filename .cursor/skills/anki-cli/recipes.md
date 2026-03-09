# anki-cli Common Recipes

> 10 cross-discipline recipes with complete command sequences.
> Copy-paste ready — no need for AI to derive from scratch each time.
>
> Atomic command reference: [reference.md](reference.md) · Known gaps: [known-gaps.md](known-gaps.md)

---

## RCP-01: Daily Dashboard

**User says**: "How many cards do I need to review today? Will I have time?"

```bash
anki-cli stats today --json
```

**Key fields**:

| Field | Meaning |
|-------|---------|
| `studied_today` | Cards studied so far |
| `remaining_new` | New cards left |
| `remaining_learning` | Learning cards left |
| `remaining_review` | Review cards left |
| `remaining_total` | Total remaining |

**Advanced**: Per-deck breakdown

```bash
anki-cli stats deck --json
# → [{deck, new, learn, review, total_due}, ...]
```

---

## RCP-02: Backlog Triage

**User says**: "I haven't studied for days. Help me see which cards are most urgent."

```bash
anki-cli review due --json
# → [{card_id, front, deck, due, interval, overdue_days}, ...]
```

**Key fields**:

| Field | Meaning |
|-------|---------|
| `overdue_days` | Days overdue (positive = overdue, 0 = due today) |
| `interval` | Current interval (days) |

Sort by `overdue_days` descending to find the most urgent cards.

**Advanced**: Triage a specific deck

```bash
anki-cli review due --deck "Organic Chemistry" --json
```

---

## RCP-03: Time ROI / Leech Hunt

**User says**: "Was my study time worth it this month? Which cards are wasting my time?"

**Step 1**: Monthly overview

```bash
anki-cli revlog summary --days 30 --json
# → {total_reviews, unique_cards, total_time, again, hard, good, easy, learn, review, relearn}
```

**Step 2**: Find leech cards (Anki auto-tags repeatedly failed cards as `leech`)

```bash
anki-cli search cards "tag:leech -is:suspended" --json
# → {total, showing, cards: [{card_id, fields, lapses, reps, ...}]}
```

**Step 3**: Find most time-consuming cards (Top 10)

```bash
anki-cli revlog summary --days 30 --group-by card --limit 10 --json
# → [{card_id, total_time_ms, review_count, again_count}, ...]
```

**Key fields**:

| Field | Meaning |
|-------|---------|
| `card_id` | Card ID |
| `total_time_ms` | Total time spent (milliseconds) |
| `review_count` | Number of reviews |
| `again_count` | Number of Again ratings |

**Step 4 (optional)**: View content of time-consuming cards

```bash
anki-cli card info-batch "111,222,333" --json
```

---

## RCP-04: Batch Card Creation from Notes

**User says**: "I just finished Chapter 3. Help me turn these knowledge points into cards."

**Step 1**: Check available note types and fields

```bash
anki-cli notetype list --json
anki-cli notetype fields "Basic" --json
```

**Step 2**: Add individually

```bash
anki-cli note add --deck "Calculus" --type "Basic" \
  --fields '{"Front":"What is Taylor expansion?","Back":"A method to represent functions as power series around a point."}' \
  --tags "chapter3,calculus"
```

**Step 3 (batch)**: AI generates JSON file, then imports

```bash
anki-cli note add-batch --file cards.json --deck "Calculus" --type "Basic"
```

`cards.json` format:

```json
[
  {"fields": {"Front": "...", "Back": "..."}, "tags": ["chapter3"]},
  {"fields": {"Front": "...", "Back": "..."}, "tags": ["chapter3"]}
]
```

---

## RCP-05: Progress Check by Tag

**User says**: "Show me which cards under the 'Civil Law' tag are still new."

```bash
# New (unlearned) cards under the tag
anki-cli search cards "tag:CivilLaw is:new" --json
# → {total: 42, cards: [...]}

# All cards under the tag (for comparison)
anki-cli search cards "tag:CivilLaw" --json
# → {total: 150, cards: [...]}
```

**Key fields (search cards entry)**:

| Field | Meaning |
|-------|---------|
| `card_id` | Card ID |
| `fields` | Field name → content |
| `tags` | Tag list |
| `type` | Card type (0=new, 1=learning, 2=review) |
| `reps` | Review count |
| `lapses` | Lapse count |

**Advanced**: Check suspended cards

```bash
anki-cli search cards "tag:CivilLaw is:suspended" --json
```

---

## RCP-06: Batch Suspend / Unsuspend

**User says**: "Suspend the Pharmacology cards. I'll resume them after finals."

**Suspend**:

```bash
# Search for card IDs
anki-cli search cards "deck:Pharmacology -is:suspended" --json
# → Extract card_id list after user confirms

# Batch suspend
anki-cli card suspend "111,222,333,444"
```

**Unsuspend** (after exams):

```bash
anki-cli search cards "deck:Pharmacology is:suspended" --json
anki-cli card unsuspend "111,222,333,444"
```

**Advanced**: Suspend only a specific tag within a deck

```bash
anki-cli search cards "deck:Pharmacology tag:chapter5 -is:suspended" --json
```

---

## RCP-07: Fix Misrated Cards

**User says**: "Yesterday I accidentally rated some cards Easy when I didn't know them. Can I undo?"

**Step 1**: View recent review log

```bash
anki-cli revlog query --days 1 --json
# → {entries: [{card_id, time, rating, ...}]}
# AI filters rating=="Easy" entries, presents to user for confirmation
```

For a specific date range:

```bash
anki-cli revlog query --since 2026-03-09 --until 2026-03-09 --json
```

**Step 2**: Fix after user confirms

```bash
# Option A: Set due today for re-review
anki-cli card set-due "111,222" --days 0

# Option B: Reset to new card entirely
anki-cli card forget "111,222"
```

**Key fields (revlog query entry)**:

| Field | Meaning |
|-------|---------|
| `card_id` | Card ID |
| `time` | Review timestamp |
| `rating` | Again / Hard / Good / Easy |
| `interval` | New interval |
| `last_interval` | Previous interval |

---

## RCP-08: Cross-Deck Deduplication

**User says**: "I have two English vocabulary decks with overlapping content. Find the duplicates."

**Step 1**: Find duplicates

```bash
anki-cli note duplicates --field "Front" --query "deck:EnglishA OR deck:EnglishB" --json
```

**Step 2**: Clean up after user confirms

```bash
# Delete duplicate notes
anki-cli note delete "111,222"

# Or merge into one deck
anki-cli card move "111,222" --deck "EnglishA"
```

---

## RCP-09: Accuracy Trend

**User says**: "Show me my review accuracy trend for the past week. Am I improving?"

```bash
anki-cli revlog summary --days 7 --group-by day --json
# → [{date, total, time_secs, again, hard, good, easy}, ...]
```

**Key fields**:

| Field | Meaning |
|-------|---------|
| `date` | Date (YYYY-MM-DD) |
| `total` | Total reviews that day |
| `again` / `hard` / `good` / `easy` | Rating counts |
| `time_secs` | Time spent (seconds) |

AI computes daily `correct_rate = (good + easy) / total` to show the trend.

---

## RCP-10: Postpone Easy Cards

**User says**: "These cards are too easy. I want longer intervals so they stop showing up."

**Step 1**: Find "too easy" cards

```bash
# Rated Easy in last 7 days AND interval still short (<30 days)
anki-cli search cards "rated:7:4 prop:ivl<30" --json
# → {cards: [{card_id, fields, interval, ease_factor, reps, ...}]}
```

**Step 2**: Postpone due date

```bash
anki-cli card set-due "111,222,333" --days 60
```

**Alternative**: Suspend entirely

```bash
anki-cli card suspend "111,222,333"
```

**Useful search syntax reference**:

| Syntax | Meaning |
|--------|---------|
| `rated:N:E` | Rated with ease E in last N days (1=Again, 4=Easy) |
| `prop:ivl<30` | Interval less than 30 days |
| `prop:ease<2.0` | Ease factor below 2.0 ("Ease Hell") |
| `prop:lapses>5` | More than 5 lapses |
