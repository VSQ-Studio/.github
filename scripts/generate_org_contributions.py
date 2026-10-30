#!/usr/bin/env python3
"""Generate an organization-wide daily commit calendar for VSQ-Studio.

The calendar aggregates commits present on the default branch of each public,
non-fork repository owned by the organization. It is intentionally not based
on any maintainer's personal contribution graph.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any

ORG = os.getenv("ORG_NAME", "VSQ-Studio")
API_URL = os.getenv("GITHUB_API_URL", "https://api.github.com").rstrip("/")
TOKEN = os.getenv("ORG_READ_TOKEN", "").strip()
DAYS = int(os.getenv("CALENDAR_DAYS", "365"))
OUT_DIR = Path(os.getenv("OUTPUT_DIR", "dist"))

DARK = {
    "bg": "#171B22", "text": "#E6EDF3", "muted": "#9AA7B5",
    "empty": "#252D38", "levels": ["#18445A", "#216B8B", "#398EAE", "#5BCEFA", "#F5A9B8"],
    "border": "#384454",
}
LIGHT = {
    "bg": "#FFFFFF", "text": "#283342", "muted": "#637182",
    "empty": "#E8EDF2", "levels": ["#D5EFF8", "#A8E0F3", "#7BD0EE", "#5BCEFA", "#D98AA8"],
    "border": "#C9D2DC",
}


def api_get(path_or_url: str) -> tuple[Any, dict[str, str]]:
    url = path_or_url if path_or_url.startswith("https://") else f"{API_URL}{path_or_url}"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "VSQ-Studio-Org-Contribution-Calendar",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=40) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data, {k.lower(): v for k, v in resp.headers.items()}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:1000]
        if exc.code in (403, 429):
            remaining = exc.headers.get("X-RateLimit-Remaining", "unknown")
            reset = exc.headers.get("X-RateLimit-Reset", "unknown")
            raise RuntimeError(
                f"GitHub API rate/permission limit (HTTP {exc.code}, remaining={remaining}, reset={reset}). "
                f"Set ORG_READ_TOKEN with read access to the public repositories. Details: {detail}"
            ) from exc
        raise RuntimeError(f"GitHub API request failed ({exc.code}) for {url}: {detail}") from exc


def paged(path: str):
    page = 1
    while True:
        separator = "&" if "?" in path else "?"
        data, _ = api_get(f"{path}{separator}per_page=100&page={page}")
        if not isinstance(data, list):
            raise RuntimeError(f"Expected a list response from {path}")
        for item in data:
            yield item
        if len(data) < 100:
            break
        page += 1


def parse_commit_date(item: dict[str, Any]) -> date | None:
    commit = item.get("commit") or {}
    committer = commit.get("committer") or {}
    author = commit.get("author") or {}
    raw = committer.get("date") or author.get("date")
    if not raw:
        return None
    try:
        value = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).date()
    except ValueError:
        return None


def collect_daily_counts(start: date, end: date) -> tuple[Counter, int, int]:
    repo_path = f"/orgs/{urllib.parse.quote(ORG, safe='')}/repos?type=public&sort=created&direction=asc"
    repos = [r for r in paged(repo_path) if not r.get("fork", False)]
    daily: Counter = Counter()
    commits_seen = 0
    repos_checked = 0

    since = datetime.combine(start, time.min, tzinfo=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    until = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for repo in repos:
        name = repo.get("name")
        if not name:
            continue
        repos_checked += 1
        path = (
            f"/repos/{urllib.parse.quote(ORG, safe='')}/{urllib.parse.quote(name, safe='')}/commits"
            f"?since={urllib.parse.quote(since)}&until={urllib.parse.quote(until)}"
        )
        for item in paged(path):
            day = parse_commit_date(item)
            if day and start <= day <= end:
                daily[day] += 1
                commits_seen += 1
    return daily, commits_seen, repos_checked


def color_for(count: int, palette: dict[str, Any]) -> str:
    if count <= 0:
        return palette["empty"]
    # Fixed thresholds make the same activity level visually comparable day-to-day.
    if count == 1:
        idx = 0
    elif count <= 3:
        idx = 1
    elif count <= 6:
        idx = 2
    elif count <= 10:
        idx = 3
    else:
        idx = 4
    return palette["levels"][idx]


def esc(value: str) -> str:
    return (value.replace("&", "&amp;").replace("<", "&lt;")
                 .replace(">", "&gt;").replace('"', "&quot;"))


def render_svg(daily: Counter, start: date, end: date, total: int, repos: int,
               palette: dict[str, Any], filename: str) -> None:
    # GitHub-style grid: Sunday-first, one column per week.
    grid_start = start - timedelta(days=(start.weekday() + 1) % 7)
    grid_end = end + timedelta(days=(5 - end.weekday()) % 7)
    weeks = ((grid_end - grid_start).days // 7) + 1

    cell = 11
    gap = 4
    step = cell + gap
    left = 48
    top = 43
    width = max(900, left + weeks * step + 20)
    height = 180

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{esc(ORG)} organization contribution calendar</title>',
        f'<desc id="desc">{total} commits in the last {DAYS} days across {repos} public, non-fork repositories. Dates use UTC. Commits are counted on each repository default branch.</desc>',
        f'<text x="{left}" y="19" fill="{palette["text"]}" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="13" font-weight="700" letter-spacing="1.4">VSQ-STUDIO / ORGANIZATION ACTIVITY</text>',
        f'<text x="{width-20}" y="19" text-anchor="end" fill="{palette["muted"]}" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="11">{total:,} COMMITS · LAST {DAYS} DAYS</text>',
    ]

    # Weekday labels, aligned to Sunday-first rows.
    for label, row in (("Mon", 1), ("Wed", 3), ("Fri", 5)):
        y = top + row * step + 9
        parts.append(f'<text x="4" y="{y}" fill="{palette["muted"]}" font-family="ui-monospace, monospace" font-size="9">{label}</text>')

    # Month labels are positioned at the first visible week of each month.
    cursor = grid_start
    seen_months = set()
    while cursor <= grid_end:
        if cursor.day == 1 and (cursor.year, cursor.month) not in seen_months:
            col = (cursor - grid_start).days // 7
            x = left + col * step
            label = cursor.strftime("%b").upper()
            parts.append(f'<text x="{x}" y="35" fill="{palette["muted"]}" font-family="ui-monospace, monospace" font-size="9">{label}</text>')
            seen_months.add((cursor.year, cursor.month))
        cursor += timedelta(days=1)

    cursor = grid_start
    while cursor <= grid_end:
        if start <= cursor <= end:
            col = (cursor - grid_start).days // 7
            row = (cursor.weekday() + 1) % 7
            x = left + col * step
            y = top + row * step
            count = int(daily.get(cursor, 0))
            title = f"{cursor.isoformat()}: {count} commit" + ("s" if count != 1 else "")
            parts.append(
                f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="{color_for(count, palette)}" stroke="{palette["border"]}" stroke-width="0.35">'
                f'<title>{esc(title)}</title></rect>'
            )
        cursor += timedelta(days=1)

    # Compact legend at the bottom right.
    legend_y = top + 7 * step + 3
    legend_x = width - 172
    parts.append(f'<text x="{legend_x}" y="{legend_y+8}" fill="{palette["muted"]}" font-family="ui-monospace, monospace" font-size="9">LESS</text>')
    for idx, color in enumerate([palette["empty"], *palette["levels"]]):
        x = legend_x + 34 + idx * 15
        parts.append(f'<rect x="{x}" y="{legend_y}" width="10" height="10" fill="{color}" stroke="{palette["border"]}" stroke-width="0.35"/>')
    parts.append(f'<text x="{legend_x+128}" y="{legend_y+8}" fill="{palette["muted"]}" font-family="ui-monospace, monospace" font-size="9">MORE</text>')
    parts.append(f'<text x="{left}" y="{height-6}" fill="{palette["muted"]}" font-family="ui-monospace, monospace" font-size="9">PUBLIC REPOSITORIES · DEFAULT BRANCHES · UTC</text>')
    parts.append('</svg>')

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / filename).write_text("\n".join(parts), encoding="utf-8")


def main() -> int:
    if DAYS < 30 or DAYS > 730:
        raise RuntimeError("CALENDAR_DAYS must be between 30 and 730")
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=DAYS - 1)
    daily, total, repos = collect_daily_counts(start, end)
    render_svg(daily, start, end, total, repos, DARK, "org-contribution-calendar-dark.svg")
    render_svg(daily, start, end, total, repos, LIGHT, "org-contribution-calendar.svg")
    print(f"Generated organization calendar: {total} commits / {repos} public non-fork repos / {start}..{end} UTC")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"::error::{exc}", file=sys.stderr)
        raise
