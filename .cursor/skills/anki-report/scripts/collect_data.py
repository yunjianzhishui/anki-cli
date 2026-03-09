#!/usr/bin/env python3
"""
Anki Report 数据收集脚本。

一次运行，调用多个 anki-cli 命令，聚合为单个 JSON 输出到 stdout。
供 anki-report skill 的 AI 解析后生成 Markdown 报告。

用法:
  python collect_data.py --scope daily --profile "操东瀚"
  python collect_data.py --scope weekly --profile "操东瀚"
  python collect_data.py --scope monthly --profile "操东瀚"
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
# When this script lives inside the anki-cli repo itself:
#   .cursor/skills/anki-report/scripts  -> up 4 levels = anki-cli repo root
ANKI_CLI_DIR = SKILL_DIR.parent.parent.parent  # .cursor/skills/anki-report -> anki-cli root
WORKSPACE_ROOT = ANKI_CLI_DIR  # same in standalone repo; override if needed
ANKI_CLI_PYTHON = ANKI_CLI_DIR / ".venv" / "Scripts" / "python.exe"

SCOPE_DAYS = {"daily": 1, "weekly": 7, "monthly": 30}


def _ensure_utf8():
    if sys.platform == "win32":
        try:
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8")
            if hasattr(sys.stderr, "reconfigure"):
                sys.stderr.reconfigure(encoding="utf-8")
        except (AttributeError, OSError, TypeError):
            pass


def _run_cli(profile: str, *args: str) -> dict | list | None:
    """Run an anki-cli command with --json and return parsed output."""
    cmd = [
        str(ANKI_CLI_PYTHON), "-m", "ankicli",
        "--profile", profile,
        "--json",
        *args,
    ]
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(ANKI_CLI_DIR),
            encoding="utf-8",
            env=env,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        _log_error(f"Command timed out: {' '.join(args)}")
        return None

    if result.returncode != 0:
        _log_error(f"Command failed ({' '.join(args)}): {result.stderr.strip()}")
        return None

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        _log_error(f"Invalid JSON from {' '.join(args)}: {result.stdout[:200]}")
        return None


_errors: list[str] = []


def _log_error(msg: str):
    _errors.append(msg)


def collect_stats_today(profile: str) -> dict:
    data = _run_cli(profile, "stats", "today")
    if not isinstance(data, dict):
        return {}
    raw = data.get("studied_today", "")
    if isinstance(raw, str):
        import re
        nums = re.findall(r"[\d.]+", raw.replace("\u2068", "").replace("\u2069", ""))
        data["studied_count"] = int(nums[0]) if nums else 0
    return data


def collect_stats_deck(profile: str) -> list:
    data = _run_cli(profile, "stats", "deck")
    return data if isinstance(data, list) else []


def collect_stats_overview(profile: str) -> dict:
    data = _run_cli(profile, "stats", "overview")
    return data if isinstance(data, dict) else {}


def collect_revlog_summary(profile: str, days: int) -> dict:
    data = _run_cli(profile, "revlog", "summary", "--days", str(days))
    return data if isinstance(data, dict) else {}


def collect_revlog_entries(profile: str, days: int, limit: int = 2000) -> list:
    data = _run_cli(profile, "revlog", "query", "--days", str(days), "--limit", str(limit))
    if isinstance(data, dict):
        return data.get("entries", [])
    return []


def collect_search_count(profile: str, query: str) -> int:
    """Run search cards and return total count (don't fetch full card details)."""
    data = _run_cli(profile, "search", "cards", query, "--limit", "1")
    if isinstance(data, dict):
        return data.get("total", 0)
    return 0


def compute_daily_breakdown(entries: list) -> list[dict]:
    """Group revlog entries by date, compute per-day stats."""
    by_date: dict[str, dict] = defaultdict(lambda: {
        "total": 0, "again": 0, "hard": 0, "good": 0, "easy": 0, "time_ms": 0
    })

    for entry in entries:
        date_str = entry.get("time", "")[:10]
        if not date_str:
            continue
        day = by_date[date_str]
        day["total"] += 1
        rating = entry.get("rating", "")
        if rating == "Again":
            day["again"] += 1
        elif rating == "Hard":
            day["hard"] += 1
        elif rating == "Good":
            day["good"] += 1
        elif rating == "Easy":
            day["easy"] += 1
        day["time_ms"] += entry.get("taken_ms", 0)

    result = []
    for date_str in sorted(by_date.keys()):
        day = by_date[date_str]
        result.append({
            "date": date_str,
            "total": day["total"],
            "again": day["again"],
            "hard": day["hard"],
            "good": day["good"],
            "easy": day["easy"],
            "time_min": round(day["time_ms"] / 60000, 1),
        })
    return result


def compute_difficulty_hotspots(entries: list, threshold: int = 2) -> list[dict]:
    """Find cards with Again >= threshold in the period."""
    again_counts: dict[int, int] = defaultdict(int)
    card_decks: dict[int, str] = {}

    for entry in entries:
        if entry.get("rating") == "Again":
            cid = entry.get("card_id", 0)
            again_counts[cid] += 1

    hotspots = []
    for cid, count in sorted(again_counts.items(), key=lambda x: -x[1]):
        if count >= threshold:
            hotspots.append({"card_id": cid, "again_count": count})

    return hotspots


def compute_time_hotspots(entries: list, threshold_ms: int = 60000, top_n: int = 10) -> list[dict]:
    """Find cards with high average review time."""
    card_times: dict[int, list[int]] = defaultdict(list)

    for entry in entries:
        cid = entry.get("card_id", 0)
        taken = entry.get("taken_ms", 0)
        if taken > 0:
            card_times[cid].append(taken)

    hotspots = []
    for cid, times in card_times.items():
        avg = sum(times) / len(times)
        if avg >= threshold_ms:
            hotspots.append({
                "card_id": cid,
                "avg_time_sec": round(avg / 1000, 1),
                "reviews": len(times),
            })

    hotspots.sort(key=lambda x: -x["avg_time_sec"])
    return hotspots[:top_n]


def compute_retention_rate(summary: dict) -> float:
    """(Good + Easy) / Total, returns 0-1."""
    total = summary.get("total_reviews", 0)
    if total == 0:
        return 0.0
    good = summary.get("good", 0)
    easy = summary.get("easy", 0)
    return round((good + easy) / total, 4)


def compute_avg_time(entries: list) -> float:
    """Average time per card in seconds."""
    times = [e.get("taken_ms", 0) for e in entries if e.get("taken_ms", 0) > 0]
    if not times:
        return 0.0
    return round(sum(times) / len(times) / 1000, 1)


def compute_study_streak(entries: list, scope_days: int) -> int:
    """Count consecutive days with at least 1 review, ending today."""
    dates_with_reviews: set[str] = set()
    for entry in entries:
        date_str = entry.get("time", "")[:10]
        if date_str:
            dates_with_reviews.add(date_str)

    today = datetime.now().date()
    streak = 0
    for i in range(scope_days + 30):
        day = (today - timedelta(days=i)).isoformat()
        if day in dates_with_reviews:
            streak += 1
        else:
            if i == 0:
                continue
            break

    return streak


def compute_volume_variance(daily_breakdown: list[dict]) -> dict:
    """Compute mean, std dev, and coefficient of variation of daily review counts."""
    counts = [d["total"] for d in daily_breakdown if d["total"] > 0]
    if len(counts) < 2:
        return {"mean": counts[0] if counts else 0, "stddev": 0, "cv": 0}

    mean = sum(counts) / len(counts)
    variance = sum((c - mean) ** 2 for c in counts) / len(counts)
    stddev = variance ** 0.5
    cv = round(stddev / mean, 2) if mean > 0 else 0
    return {"mean": round(mean, 1), "stddev": round(stddev, 1), "cv": cv}


def _extract_attributions(file_path: Path) -> list[dict]:
    """Extract ERR-A/B/C/D attribution codes from a practice record file."""
    import re
    try:
        content = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []

    attributions = []
    in_attribution_section = False
    for line in content.splitlines():
        if "归因分析" in line or "归因维度" in line:
            in_attribution_section = True
            continue
        if in_attribution_section:
            if line.startswith("#") or (line.startswith("---") and attributions):
                break
            match = re.search(r"(ERR-[A-D])", line)
            if match:
                err_code = match.group(1)
                cols = [c.strip() for c in line.split("|") if c.strip()]
                detail = cols[1] if len(cols) > 1 else ""
                note = cols[2] if len(cols) > 2 else ""
                attributions.append({
                    "code": err_code,
                    "detail": detail,
                    "note": note,
                })
    return attributions


def _extract_score(file_path: Path) -> str | None:
    """Extract the final score from a practice record file."""
    import re
    try:
        content = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    for line in content.splitlines():
        if "最终评分" in line or "评分" in line:
            match = re.search(r"([\d.]+)\s*/\s*(\d+)", line)
            if match:
                return f"{match.group(1)}/{match.group(2)}"
    return None


def collect_practice_records(scope_days: int) -> list[dict]:
    """Scan practice record files from 学习资料/ for cross-subject analysis."""
    records_dir = WORKSPACE_ROOT / "学习资料"
    if not records_dir.exists():
        return []

    cutoff = datetime.now() - timedelta(days=scope_days + 1)
    records = []

    for md_file in records_dir.rglob("练习记录-*.md"):
        name = md_file.stem
        parts = name.split("-")
        if len(parts) < 4:
            continue
        try:
            date_str = f"{parts[1]}-{parts[2]}-{parts[3]}"
            file_date = datetime.strptime(date_str, "%Y-%m-%d")
        except (ValueError, IndexError):
            continue

        if file_date < cutoff:
            continue

        subject = "未知"
        for parent in md_file.parents:
            if parent.name in ("语文", "英语", "数学", "物理", "化学", "生物", "历史", "政治", "地理"):
                subject = parent.name
                break
            if parent == records_dir:
                break

        record_type = "未知"
        if "文言翻译" in name:
            record_type = "文言翻译"
        elif "段落概括" in name:
            record_type = "段落概括"
        elif "英语翻译" in name or "高考翻译" in name:
            record_type = "英语翻译"

        topic = "-".join(parts[4:]) if len(parts) > 4 else ""

        record = {
            "file": str(md_file.relative_to(WORKSPACE_ROOT)),
            "date": date_str,
            "subject": subject,
            "type": record_type,
            "topic": topic,
        }

        attributions = _extract_attributions(md_file)
        if attributions:
            record["attributions"] = attributions
            record["attribution_summary"] = {}
            for a in attributions:
                code = a["code"]
                record["attribution_summary"][code] = record["attribution_summary"].get(code, 0) + 1

        score = _extract_score(md_file)
        if score:
            record["score"] = score

        records.append(record)

    records.sort(key=lambda x: x["date"])
    return records


def main():
    _ensure_utf8()

    parser = argparse.ArgumentParser(description="Anki Report data collector")
    parser.add_argument("--scope", choices=["daily", "weekly", "monthly"], default="daily")
    parser.add_argument("--profile", default="User 1")
    args = parser.parse_args()

    days = SCOPE_DAYS[args.scope]
    streak_query_days = max(days, 30)

    today = collect_stats_today(args.profile)
    deck_overview = collect_stats_deck(args.profile)
    global_overview = collect_stats_overview(args.profile)
    revlog_summary = collect_revlog_summary(args.profile, days)

    entries = collect_revlog_entries(args.profile, days)

    streak_entries = entries
    if days < 30:
        streak_entries = collect_revlog_entries(args.profile, streak_query_days, limit=5000)

    overdue_count = collect_search_count(args.profile, "is:due")
    new_count = collect_search_count(args.profile, "is:new")
    suspended_count = collect_search_count(args.profile, "is:suspended")

    daily_breakdown = compute_daily_breakdown(entries)
    difficulty_hotspots = compute_difficulty_hotspots(entries, threshold=2 if days <= 7 else 3)
    time_hotspots = compute_time_hotspots(entries)
    retention_rate = compute_retention_rate(revlog_summary)
    avg_time = compute_avg_time(entries)
    streak = compute_study_streak(streak_entries, streak_query_days)
    volume_stats = compute_volume_variance(daily_breakdown)

    practice_records = []
    attribution_totals: dict[str, int] = {}
    if args.scope in ("weekly", "monthly"):
        practice_records = collect_practice_records(days)
        for rec in practice_records:
            for code, count in rec.get("attribution_summary", {}).items():
                attribution_totals[code] = attribution_totals.get(code, 0) + count

    report_data = {
        "scope": args.scope,
        "days": days,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "profile": args.profile,
        "today": today,
        "global_overview": global_overview,
        "deck_overview": deck_overview,
        "revlog_summary": revlog_summary,
        "daily_breakdown": daily_breakdown,
        "retention_rate": retention_rate,
        "avg_time_per_card_sec": avg_time,
        "study_streak_days": streak,
        "volume_stats": volume_stats,
        "difficulty_hotspots": difficulty_hotspots,
        "time_hotspots": time_hotspots,
        "queue_depth": {
            "overdue": overdue_count,
            "new": new_count,
            "suspended": suspended_count,
        },
        "practice_records": practice_records,
        "attribution_totals": attribution_totals,
        "errors": _errors,
    }

    print(json.dumps(report_data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
