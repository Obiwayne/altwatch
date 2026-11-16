"""The daily check: what is listed now, what was listed before, and one message
only when something is new."""
from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass, field
from datetime import date
from typing import Callable

from . import sources
from .sources import Budget, FeedItem, FetchError

MAX_TOOLS = 10        # tools you can watch
MAX_FEEDS = 5         # extra feeds
MAX_SEARCHES = 5      # Miniflux keyword searches
MAX_DETAILS = 5       # project pages opened for facts in one run
MAX_FEED_LINES = 5    # feed items shown in one message
FAILS_BEFORE_TELLING = 3
SEEN_CAP = 500        # feed ids remembered per feed
DEFAULT_BASE = "https://repoquarry.dev"

Fetch = Callable[..., str]


class WatchError(ValueError):
    """The watch file is wrong in a way the user has to fix."""


# ---------------------------------------------------------------- watch file

@dataclass
class Watch:
    base: str = DEFAULT_BASE
    tools: list[tuple[str, str]] = field(default_factory=list)   # (slug, name as typed)
    feeds: list[dict] = field(default_factory=list)              # {name, url, keywords}
    miniflux: dict | None = None                                 # {url, token_env, keywords}


def load_watch(data: dict) -> Watch:
    if not isinstance(data, dict):
        raise WatchError("The watch file must be a JSON object.")
    base = str(data.get("base") or DEFAULT_BASE).rstrip("/")
    if not sources.safe_link(base):
        raise WatchError(f"'base' is not a web address: {base}")
    tools: list[tuple[str, str]] = []
    for raw in data.get("tools") or []:
        name = str(raw).strip()
        slug = sources.slugify(name)
        if not slug:
            raise WatchError(f"Can't read the tool name {raw!r}.")
        if slug not in [s for s, _ in tools]:
            tools.append((slug, name))
    if len(tools) > MAX_TOOLS:
        raise WatchError(f"Altwatch watches up to {MAX_TOOLS} tools. The file lists {len(tools)}.")
    feeds = []
    for f in data.get("feeds") or []:
        url = sources.safe_link(str(f.get("url", "")))
        kws = [str(k).strip() for k in f.get("keywords") or [] if str(k).strip()]
        if not url:
            raise WatchError(f"A feed has no usable address: {f.get('url')!r}")
        if not kws:
            raise WatchError(f"The feed {url} needs at least one keyword, or every post would be an alert.")
        feeds.append({"name": sources.clean(str(f.get("name") or ""), 60), "url": url, "keywords": kws})
    if len(feeds) > MAX_FEEDS:
        raise WatchError(f"Altwatch reads up to {MAX_FEEDS} extra feeds. The file lists {len(feeds)}.")
    mf = data.get("miniflux")
    miniflux = None
    if mf:
        url = sources.safe_link(str(mf.get("url", "")))
        kws = [str(k).strip() for k in mf.get("keywords") or [] if str(k).strip()]
        if not url or not kws:
            raise WatchError("'miniflux' needs a 'url' and at least one keyword.")
        if "token" in mf:
            raise WatchError("Don't put the Miniflux token in the file. Name an environment variable in 'token_env'.")
        if len(kws) > MAX_SEARCHES:
            raise WatchError(f"Miniflux takes up to {MAX_SEARCHES} keywords. The file lists {len(kws)}.")
        miniflux = {"url": url.rstrip("/"), "token_env": str(mf.get("token_env") or "MINIFLUX_TOKEN"), "keywords": kws}
    if not tools and not feeds and not miniflux:
        raise WatchError("Nothing to watch. Add at least one tool, feed or Miniflux keyword.")
    return Watch(base=base, tools=tools, feeds=feeds, miniflux=miniflux)


def request_cap(watch: Watch) -> int:
    """The most requests one run can make: one per source, plus the project pages."""
    searches = len(watch.miniflux["keywords"]) if watch.miniflux else 0
    return len(watch.tools) + len(watch.feeds) + searches + MAX_DETAILS


# ---------------------------------------------------------------- state

def new_state() -> dict:
    return {"version": 1, "tools": {}, "feeds": {}, "runs": []}


def load_state(path: str) -> dict:
    if not os.path.exists(path):
        return new_state()
    with open(path, encoding="utf-8") as f:
        state = json.load(f)
    if state.get("version") != 1:
        raise WatchError(f"{path} isn't an Altwatch state file this version can read.")
    return state


def save_state(path: str, state: dict) -> None:
    folder = os.path.dirname(os.path.abspath(path))
    os.makedirs(folder, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=folder, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=1, ensure_ascii=False)
    os.replace(tmp, path)


# ---------------------------------------------------------------- the run

@dataclass
class NewProject:
    id: str
    name: str
    url: str
    tools: list[str]
    jobs: str = ""
    use_instead: str = ""
    commercial_use: str = ""
    paid_services: str = ""
    licence: str = ""
    licence_checked: str = ""
    setup: str = ""


@dataclass
class Run:
    day: str
    started: list[str] = field(default_factory=list)       # sources seen for the first time
    projects: list[NewProject] = field(default_factory=list)
    items: list[tuple[FeedItem, str, str]] = field(default_factory=list)   # item, feed name, keyword
    tell: list[str] = field(default_factory=list)          # problems worth one line
    log: list[str] = field(default_factory=list)
    requests: int = 0

    @property
    def is_alert(self) -> bool:
        return bool(self.projects or self.items)


def _fail(entry: dict, label: str, err: Exception, run: Run) -> None:
    entry["fails"] = entry.get("fails", 0) + 1
    run.log.append(f"could not read {label}: {err}")
    if entry["fails"] == FAILS_BEFORE_TELLING:
        run.tell.append(f"Altwatch couldn't read {label} {FAILS_BEFORE_TELLING} days running. It will keep trying.")


def check(watch: Watch, state: dict, today: date, fetch: Fetch = sources.http_get) -> Run:
    """One check. Changes `state` in place and returns what there is to say."""
    day = today.isoformat()
    run = Run(day=day)
    budget = Budget(request_cap(watch))
    found: dict[str, NewProject] = {}

    for slug, typed in watch.tools:
        entry = state["tools"].setdefault(slug, {"name": typed, "since": None, "seen": {}, "fails": 0})
        url = f"{watch.base}/alternatives/{slug}.md"
        try:
            name, listed = sources.parse_alternatives_md(fetch(url, budget))
        except FetchError as e:
            if e.status == 404:
                if not entry.get("missing"):
                    entry["missing"] = True
                    run.tell.append(f"RepoQuarry has no page for \"{typed}\" yet, so there is nothing to compare. "
                                    f"Check the spelling against {watch.base}/alternatives.")
                run.log.append(f"{slug}: no page (404)")
            else:
                _fail(entry, f"the page for {entry['name']}", e, run)
            continue
        if not listed and entry["seen"]:
            _fail(entry, f"the page for {entry['name']}", ValueError("no project table on the page"), run)
            continue
        entry["fails"] = 0
        entry.pop("missing", None)
        if name:
            entry["name"] = name
        if entry["since"] is None:
            entry["since"] = day
            entry["seen"] = {p.id: day for p in listed}
            run.started.append(f"{entry['name']}: {len(listed)} listed so far")
            run.log.append(f"{slug}: first look, {len(listed)} listed")
            continue
        now_ids = {p.id for p in listed}
        gone = sorted(set(entry["seen"]) - now_ids)
        if gone:
            run.log.append(f"{slug}: no longer listed: {', '.join(gone)}")
        fresh = [p for p in listed if p.id not in entry["seen"]]
        for p in fresh:
            entry["seen"][p.id] = day
            hit = found.get(p.id)
            if hit:
                hit.tools.append(entry["name"])
            else:
                found[p.id] = NewProject(id=p.id, name=p.name, url=p.url, tools=[entry["name"]], jobs=p.jobs,
                                         use_instead=p.use_instead, commercial_use=p.commercial_use,
                                         paid_services=p.paid_services)
        run.log.append(f"{slug}: {len(listed)} listed, {len(fresh)} new")

    run.projects = list(found.values())
    for proj in run.projects[:MAX_DETAILS]:
        try:
            facts = sources.parse_project_md(fetch(f"{watch.base}/projects/{proj.id}.md", budget))
        except FetchError as e:
            run.log.append(f"{proj.id}: facts page not read: {e}")
            continue
        proj.licence = facts.get("licence", "")
        proj.licence_checked = facts.get("licence_checked", "")
        proj.setup = facts.get("setup", "")
        proj.commercial_use = facts.get("commercial_use") or proj.commercial_use
        proj.paid_services = facts.get("paid_services") or proj.paid_services

    for feed in watch.feeds:
        entry = state["feeds"].setdefault(feed["url"], {"since": None, "seen": [], "fails": 0})
        label = feed["name"] or feed["url"]
        try:
            title, items = sources.parse_feed(fetch(feed["url"], budget))
        except (FetchError, ValueError, SyntaxError) as e:
            _fail(entry, f"the feed {label}", e, run)
            continue
        entry["fails"] = 0
        _take_items(entry, items, feed["name"] or title or feed["url"], feed["keywords"], day, run)

    if watch.miniflux:
        mf = watch.miniflux
        entry = state["feeds"].setdefault("miniflux", {"since": None, "seen": [], "fails": 0})
        token = os.environ.get(mf["token_env"], "")
        if not token:
            run.log.append(f"Miniflux skipped: the environment variable {mf['token_env']} is not set")
        else:
            items: list[FeedItem] = []
            tagged: dict[str, str] = {}
            failed = None
            for kw in mf["keywords"]:
                try:
                    for it in sources.miniflux_entries(mf["url"], token, kw, budget):
                        if it.id not in tagged:
                            tagged[it.id] = kw
                            items.append(it)
                except FetchError as e:
                    failed = e
                    break
            if failed:
                _fail(entry, "Miniflux", failed, run)
            else:
                entry["fails"] = 0
                _take_items(entry, items, "Miniflux", None, day, run, tagged)

    run.requests = budget.used
    state["runs"] = (state.get("runs") or [])[-59:] + [{
        "date": day, "new_projects": len(run.projects), "new_items": len(run.items),
        "message": bool(compose(run)), "requests": run.requests}]
    return run


def _take_items(entry: dict, items: list[FeedItem], name: str, keywords: list[str] | None,
                day: str, run: Run, tagged: dict[str, str] | None = None) -> None:
    seen = set(entry["seen"])
    first = entry["since"] is None
    fresh = [it for it in items if it.id not in seen]
    if first:
        entry["since"] = day
        run.started.append(f"{name}: watching for new posts")
    else:
        for it in fresh:
            kw = tagged[it.id] if tagged is not None else sources.keyword_hit(it, keywords or [])
            if kw:
                run.items.append((it, it.source or name, kw))
    entry["seen"] = (entry["seen"] + [it.id for it in fresh])[-SEEN_CAP:]
    run.log.append(f"{name}: {len(items)} posts, {len(fresh)} not seen before")


# ---------------------------------------------------------------- the message

def _nice_day(day: str) -> str:
    d = date.fromisoformat(day)
    return f"{d.day} {d.strftime('%b %Y')}"


def compose(run: Run) -> str:
    """The one message for this run, or '' when there is nothing to say."""
    lines: list[str] = []
    if run.is_alert:
        n = len(run.projects)
        if n:
            head = f"{n} new open-source alternative{'s' if n != 1 else ''}"
        else:
            m = len(run.items)
            head = f"{m} new post{'s' if m != 1 else ''} on your topics"
        lines.append(f"Altwatch, {_nice_day(run.day)}: {head}")
        for p in run.projects:
            lines.append("")
            lines.append(f"{p.name}, for {_join(p.tools)}")
            unchecked = [v for v in (p.commercial_use, p.paid_services) if v.lower().startswith("not checked")]
            if not p.licence and (len(unchecked) == 2 or not (p.commercial_use or p.paid_services)):
                lines.append("  RepoQuarry hasn't checked its licence or cost yet. Treat it as a lead, not a swap.")
            else:
                if p.licence:
                    checked = f" (checked {p.licence_checked})" if p.licence_checked else ""
                    lines.append(f"  Licence: {p.licence}{checked}")
                else:
                    lines.append("  Licence: on the page below")
                if p.commercial_use:
                    lines.append(f"  Use at work: {p.commercial_use}")
                if p.paid_services:
                    lines.append(f"  Running cost: {p.paid_services}")
            if p.jobs:
                lines.append(f"  Covers: {p.jobs}")
            lines.append(f"  {p.url}")
        if run.items:
            shown = run.items[:MAX_FEED_LINES]
            lines.append("")
            lines.append("Also new in your feeds:" if run.projects else "New in your feeds:")
            for it, name, kw in shown:
                lines.append(f"- {it.title or '(no title)'} ({name}, matched \"{kw}\")")
                if it.link:
                    lines.append(f"  {it.link}")
            if len(run.items) > len(shown):
                lines.append(f"- and {len(run.items) - len(shown)} more")
        if run.projects:
            lines.append("")
            lines.append("Facts come from RepoQuarry, each with a source and a check date. "
                         "Licences change, so open the page before you switch.")
    elif run.started:
        lines.append(f"Altwatch, {_nice_day(run.day)}: now watching")
        lines.append("")
        lines += [f"- {s}" for s in run.started]
        lines.append("")
        lines.append("These are your starting point. You'll only hear from Altwatch when something new appears.")
    if run.is_alert and run.started:
        lines.append("")
        lines.append("Now also watching: " + "; ".join(run.started))
    if run.tell:
        if lines:
            lines.append("")
        lines += run.tell
    return "\n".join(lines)


def _join(names: list[str]) -> str:
    if len(names) <= 1:
        return "".join(names)
    return ", ".join(names[:-1]) + " and " + names[-1]
