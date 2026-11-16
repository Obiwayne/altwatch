"""Runs Altwatch once a day for a made-up week, 9 to 15 November 2026, against
the stand-in site in fake_site.py. Writes each day's message to sample/out/.

    python sample/run_week.py

The Notion and Zapier pages are real RepoQuarry pages saved on 16 Nov 2026.
Pagewell, Flowkiln, the Maker Notes blog and the Miniflux entries are made up.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

from altwatch import core  # noqa: E402
from fake_site import TOKEN, FakeSite, rss  # noqa: E402

POSTS = [
    {"title": "What we learned moving house", "link": "https://makernotes.example/moving-house",
     "summary": "Boxes, mostly."},
    {"title": "Our office dog has opinions", "link": "https://makernotes.example/office-dog",
     "summary": "Nothing about software this week."},
    {"title": "A week with a Zapier alternative on a spare laptop", "link": "https://makernotes.example/zapier-alternative-week",
     "summary": "We moved four automations off Zapier and kept notes on what broke."},
]
ENTRIES = [
    {"id": 101, "status": "unread", "title": "Ten desk plants that survive neglect", "url": "https://plants.example/ten",
     "content": "<p>None of them are software.</p>", "feed": {"title": "Desk Life"}},
    {"id": 102, "status": "unread", "title": "Self-hosted notes: what I run in 2026", "url": "https://homelab.example/notes-2026",
     "content": "<p>My <b>self-hosted notes</b> setup after a year.</p>", "feed": {"title": "Homelab Weekly"}},
]


def week(site: FakeSite):
    """Yields (day, what changed on the site that morning)."""
    day = date(2026, 11, 9)
    site.load_snapshot("notion")
    site.load_snapshot("zapier")
    site.page("/blog/feed.xml", rss(POSTS[:1]), "application/rss+xml")
    site.entries = ENTRIES[:1]
    yield day, "first run"
    site.page("/blog/feed.xml", rss(POSTS[:2]), "application/rss+xml")
    yield day + timedelta(1), "a blog post about a dog"
    yield day + timedelta(2), "nothing"
    site.list_project("notion", "pagewell")
    yield day + timedelta(3), "Pagewell listed for Notion"
    yield day + timedelta(4), "nothing"
    site.page("/blog/feed.xml", rss(POSTS), "application/rss+xml")
    site.entries = ENTRIES
    yield day + timedelta(5), "a blog post and a reader entry on watched topics"
    site.list_project("zapier", "flowkiln")
    site.list_project("notion", "flowkiln")
    yield day + timedelta(6), "Flowkiln listed for Zapier and Notion"


def main() -> int:
    out = os.path.join(HERE, "out")
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    site = FakeSite()
    os.environ["ALTWATCH_SAMPLE_TOKEN"] = TOKEN
    watch = core.load_watch({
        "base": site.url,
        "tools": ["Notion", "Zapier"],
        "feeds": [{"name": "Maker Notes", "url": site.url + "/blog/feed.xml",
                   "keywords": ["zapier alternative", "notion alternative"]}],
        "miniflux": {"url": site.url, "token_env": "ALTWATCH_SAMPLE_TOKEN", "keywords": ["self-hosted notes"]},
    })
    state = core.new_state()
    summary = []
    try:
        for day, change in week(site):
            run = core.check(watch, state, day)
            message = core.compose(run)
            kind = "alert" if run.is_alert else "setup note" if message else "silent"
            summary.append({"date": day.isoformat(), "site_change": change, "result": kind,
                            "new_projects": len(run.projects), "new_posts": len(run.items), "requests": run.requests})
            print(f"--- {day:%a %d %b}: {change} -> {kind} ({run.requests} requests)")
            if message:
                print(message)
                with open(os.path.join(out, f"message-{day.isoformat()}.txt"), "w", encoding="utf-8") as f:
                    f.write(message + "\n")
    finally:
        site.close()
    alerts = sum(1 for s in summary if s["result"] == "alert")
    silent = sum(1 for s in summary if s["result"] == "silent")
    total = {"runs": len(summary), "alerts": alerts, "setup_notes": len(summary) - alerts - silent, "silent": silent,
             "requests": sum(s["requests"] for s in summary), "most_requests_in_a_run": max(s["requests"] for s in summary),
             "request_cap_per_run": core.request_cap(watch)}
    with open(os.path.join(out, "week.json"), "w", encoding="utf-8") as f:
        json.dump({"days": summary, "total": total}, f, indent=1)
    print("---", json.dumps(total))
    return 0


if __name__ == "__main__":
    for s in (sys.stdout, sys.stderr):
        s.reconfigure(encoding="utf-8")
    sys.exit(main())
