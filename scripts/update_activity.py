#!/usr/bin/env python3
import json, os, urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from xml.sax.saxutils import escape

org = os.environ.get("GITHUB_ORG", "VSQ-Studio")
token = os.environ.get("GITHUB_TOKEN", "")
headers = {"Accept": "application/vnd.github+json", "User-Agent": "VSQ-Studio-Activity-Bot"}
if token:
    headers["Authorization"] = f"Bearer {token}"
request = urllib.request.Request(f"https://api.github.com/orgs/{org}/events?per_page=100", headers=headers)
with urllib.request.urlopen(request, timeout=30) as response:
    events = json.load(response)

today = datetime.now(timezone.utc).date()
days = [today - timedelta(days=i) for i in range(13, -1, -1)]
counts = Counter()
for event in events:
    stamp = event.get("created_at")
    if stamp:
        try:
            day = datetime.fromisoformat(stamp.replace("Z", "+00:00")).date()
            if day in days:
                counts[day] += 1
        except ValueError:
            pass

palette = ["#102B45", "#075078", "#087EB7", "#16BBD8", "#56F0F5"]
max_count = max(counts.values(), default=0)
parts = []
for i, day in enumerate(days):
    value = counts[day]
    level = 0 if value == 0 else min(4, 1 + int((value / max(max_count, 1)) * 3))
    x = 28 + i * 68
    parts.append(f'<rect x="{x}" y="76" width="42" height="42" rx="3" fill="{palette[level]}"/>')
    parts.append(f'<text x="{x+21}" y="143" text-anchor="middle" fill="#9ACDE8" font-family="monospace" font-size="11">{day:%m/%d}</text>')
    parts.append(f'<text x="{x+21}" y="103" text-anchor="middle" fill="#F2F8FF" font-family="monospace" font-size="13">{value}</text>')

total = sum(counts.values())
updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="178" viewBox="0 0 1000 178">
<rect width="1000" height="178" rx="8" fill="#071A30"/>
<text x="28" y="34" fill="#2CE3F3" font-family="monospace" font-size="18" font-weight="bold">VSQ-STUDIO / PUBLIC ACTIVITY</text>
<text x="972" y="34" text-anchor="end" fill="#9ACDE8" font-family="monospace" font-size="12">{total} events / last 14 days</text>
{''.join(parts)}
<text x="28" y="166" fill="#7CAFCB" font-family="monospace" font-size="11">Daily public organization events / Updated {escape(updated)}</text>
<text x="972" y="166" text-anchor="end" fill="#7CAFCB" font-family="monospace" font-size="11">GITHUB EVENTS API</text>
</svg>'''
Path("assets/activity.svg").write_text(svg, encoding="utf-8")
