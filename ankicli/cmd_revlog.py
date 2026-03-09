"""Review log query commands — the revlog building block."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

import typer

from ankicli.connection import open_collection
from ankicli.output import print_error, print_json, print_table, is_json_mode

app = typer.Typer(no_args_is_help=True)


def _get_state():
    from ankicli.main import state
    return state


REVIEW_TYPE_NAMES = {0: "learn", 1: "review", 2: "relearn", 3: "cram", 4: "resched"}
EASE_NAMES = {1: "Again", 2: "Hard", 3: "Good", 4: "Easy"}


def _parse_date(s: str) -> datetime:
    """Parse YYYY-MM-DD string to datetime at midnight."""
    return datetime.strptime(s, "%Y-%m-%d")


def _resolve_time_range(
    days: Optional[int],
    since: Optional[str],
    until: Optional[str],
    day_cutoff: int,
) -> tuple[int, int]:
    """Return (start_ms, end_ms) for the revlog id filter.

    day_cutoff is Anki's next-day boundary in epoch seconds.
    """
    if days is not None:
        end_ms = day_cutoff * 1000
        start_ms = (day_cutoff - 86400 * (days + 1)) * 1000
        return start_ms, end_ms

    now = datetime.now()
    if since:
        start = _parse_date(since)
    else:
        start = now - timedelta(days=1)

    if until:
        end = _parse_date(until) + timedelta(days=1)
    else:
        end = now + timedelta(days=1)

    return int(start.timestamp()) * 1000, int(end.timestamp()) * 1000


@app.command()
def query(
    days: Optional[int] = typer.Option(None, "--days", "-d", help="Past N days (uses Anki day boundary)"),
    since: Optional[str] = typer.Option(None, "--since", "-s", help="Start date YYYY-MM-DD"),
    until: Optional[str] = typer.Option(None, "--until", "-u", help="End date YYYY-MM-DD (inclusive)"),
    limit: int = typer.Option(200, "--limit", "-n", help="Max rows"),
    unique: bool = typer.Option(False, "--unique", help="Deduplicate by card_id (keep first review)"),
) -> None:
    """Query review log entries by date range."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        try:
            start_ms, end_ms = _resolve_time_range(days, since, until, col.sched.day_cutoff)
        except ValueError as e:
            print_error(f"Invalid date format: {e}")
            raise typer.Exit(1)

        results = col.db.all(
            """
            SELECT r.id, r.cid, r.ease, r.ivl, r.lastIvl, r.factor, r.time, r.type
            FROM revlog r
            WHERE r.id >= ? AND r.id < ?
            ORDER BY r.id
            LIMIT ?
            """,
            start_ms,
            end_ms,
            limit,
        )

        seen = set()
        rows = []
        for rid, cid, ease, ivl, last_ivl, factor, time_ms, rtype in results:
            if unique:
                if cid in seen:
                    continue
                seen.add(cid)

            ts = datetime.fromtimestamp(rid / 1000)
            row = {
                "review_id": rid,
                "card_id": cid,
                "time": ts.strftime("%Y-%m-%d %H:%M:%S"),
                "type": REVIEW_TYPE_NAMES.get(rtype, str(rtype)),
                "rating": EASE_NAMES.get(ease, str(ease)),
                "interval": ivl,
                "last_interval": last_ivl,
                "ease_factor": factor,
                "taken_ms": time_ms,
            }
            rows.append(row)

        if is_json_mode():
            print_json({"total": len(results), "showing": len(rows), "entries": rows})
        else:
            print_table(rows, title=f"Review Log ({len(rows)} entries)")


@app.command()
def summary(
    days: Optional[int] = typer.Option(None, "--days", "-d", help="Past N days"),
    since: Optional[str] = typer.Option(None, "--since", "-s", help="Start date YYYY-MM-DD"),
    until: Optional[str] = typer.Option(None, "--until", "-u", help="End date YYYY-MM-DD (inclusive)"),
    group_by: Optional[str] = typer.Option(None, "--group-by", "-g", help="Group results: 'day' or 'card'"),
    limit: int = typer.Option(50, "--limit", "-n", help="Max rows (for --group-by)"),
) -> None:
    """Summarize review activity in a date range (counts by type and rating)."""
    s = _get_state()
    with open_collection(s.profile, s.path) as col:
        try:
            start_ms, end_ms = _resolve_time_range(days, since, until, col.sched.day_cutoff)
        except ValueError as e:
            print_error(f"Invalid date format: {e}")
            raise typer.Exit(1)

        if group_by == "day":
            _summary_by_day(col, start_ms, end_ms, limit)
        elif group_by == "card":
            _summary_by_card(col, start_ms, end_ms, limit)
        elif group_by is not None:
            print_error(f"Invalid --group-by value: '{group_by}'. Use 'day' or 'card'.")
            raise typer.Exit(1)
        else:
            _summary_total(col, start_ms, end_ms)


def _summary_total(col, start_ms: int, end_ms: int) -> None:
    """Default summary: single aggregate for the entire period."""
    stats = col.db.first(
        """
        SELECT
            count(*) as total,
            count(DISTINCT cid) as unique_cards,
            sum(time) / 1000 as total_secs,
            sum(case when ease = 1 then 1 else 0 end) as again_count,
            sum(case when ease = 2 then 1 else 0 end) as hard_count,
            sum(case when ease = 3 then 1 else 0 end) as good_count,
            sum(case when ease = 4 then 1 else 0 end) as easy_count,
            sum(case when type = 0 then 1 else 0 end) as learn_count,
            sum(case when type = 1 then 1 else 0 end) as review_count,
            sum(case when type = 2 then 1 else 0 end) as relearn_count
        FROM revlog
        WHERE id >= ? AND id < ? AND type != 4
        """,
        start_ms,
        end_ms,
    )

    total, unique_cards, total_secs, again, hard, good, easy, learn, review, relearn = stats
    total = total or 0
    unique_cards = unique_cards or 0
    total_secs = total_secs or 0

    from ankicli.output import print_single
    data = {
        "total_reviews": total,
        "unique_cards": unique_cards,
        "total_time": f"{total_secs // 60}m {total_secs % 60}s",
        "again": again or 0,
        "hard": hard or 0,
        "good": good or 0,
        "easy": easy or 0,
        "learn": learn or 0,
        "review": review or 0,
        "relearn": relearn or 0,
    }
    print_single(data, title="Review Summary")


def _summary_by_day(col, start_ms: int, end_ms: int, limit: int) -> None:
    """Group summary by Anki day (respects day boundary)."""
    day_cutoff = col.sched.day_cutoff
    results = col.db.all(
        """
        SELECT
            CAST((? - id/1000) / 86400 AS INT) as days_ago,
            count(*) as total,
            sum(time) as total_time_ms,
            sum(case when ease = 1 then 1 else 0 end) as again,
            sum(case when ease = 2 then 1 else 0 end) as hard,
            sum(case when ease = 3 then 1 else 0 end) as good,
            sum(case when ease = 4 then 1 else 0 end) as easy
        FROM revlog
        WHERE id >= ? AND id < ? AND type != 4
        GROUP BY days_ago
        ORDER BY days_ago ASC
        LIMIT ?
        """,
        day_cutoff,
        start_ms,
        end_ms,
        limit,
    )

    rows = []
    for days_ago, total, time_ms, again, hard, good, easy in results:
        date = datetime.fromtimestamp(day_cutoff - 86400 * (days_ago + 1))
        time_ms = time_ms or 0
        rows.append({
            "date": date.strftime("%Y-%m-%d"),
            "total": total or 0,
            "time_secs": time_ms // 1000,
            "again": again or 0,
            "hard": hard or 0,
            "good": good or 0,
            "easy": easy or 0,
        })

    if is_json_mode():
        print_json(rows)
    else:
        print_table(rows, title="Review Summary by Day")


def _summary_by_card(col, start_ms: int, end_ms: int, limit: int) -> None:
    """Group summary by card, sorted by total time descending."""
    results = col.db.all(
        """
        SELECT
            cid,
            sum(time) as total_time_ms,
            count(*) as review_count,
            sum(case when ease = 1 then 1 else 0 end) as again_count
        FROM revlog
        WHERE id >= ? AND id < ? AND type != 4
        GROUP BY cid
        ORDER BY total_time_ms DESC
        LIMIT ?
        """,
        start_ms,
        end_ms,
        limit,
    )

    rows = []
    for cid, time_ms, rev_count, again_count in results:
        rows.append({
            "card_id": cid,
            "total_time_ms": time_ms or 0,
            "review_count": rev_count or 0,
            "again_count": again_count or 0,
        })

    if is_json_mode():
        print_json(rows)
    else:
        print_table(rows, title=f"Review Summary by Card (top {limit})")
