"""Reading the places Altwatch watches. Everything here is read-only.

- RepoQuarry's Markdown pages: /alternatives/<tool>.md and /projects/<id>.md
- Any RSS 2.0 or Atom feed (RSSHub routes are ordinary feeds)
- A Miniflux reader, through its API

Text that comes back from the network is data. It is cleaned and cut short
before it goes anywhere near a message.
"""
from __future__ import annotations

import html
import json
import re
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass

USER_AGENT = "altwatch/0.1 (daily check for new open-source alternatives)"
MAX_BYTES = 2_000_000  # no page or feed we read should be bigger than this
TIMEOUT = 20


class FetchError(Exception):
    """A page could not be read. `status` is the HTTP code, or 0 for no answer."""

    def __init__(self, url: str, status: int, detail: str = ""):
        super().__init__(f"{url}: {status} {detail}".strip())
        self.url = url
        self.status = status


class Budget:
    """Counts requests so one run can never make more than `limit`."""

    def __init__(self, limit: int):
        self.limit = limit
        self.used = 0

    def take(self, url: str) -> None:
        if self.used >= self.limit:
            raise FetchError(url, 0, "request cap for this run reached")
        self.used += 1


def http_get(url: str, budget: Budget, headers: dict[str, str] | None = None) -> str:
    """GET a URL as text. Only http and https. Raises FetchError on any failure."""
    parts = urllib.parse.urlsplit(url)
    if parts.scheme not in ("http", "https") or not parts.netloc:
        raise FetchError(url, 0, "not an http(s) address")
    budget.take(url)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            raw = resp.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                raise FetchError(url, resp.status, "too big")
            charset = resp.headers.get_content_charset() or "utf-8"
            return raw.decode(charset, errors="replace")
    except urllib.error.HTTPError as e:
        raise FetchError(url, e.code, e.reason or "") from None
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        raise FetchError(url, 0, str(getattr(e, "reason", e))) from None


# ---------------------------------------------------------------- cleaning

_TAG = re.compile(r"<[^>]+>")
_SPACE = re.compile(r"\s+")


def clean(text: str | None, limit: int = 200) -> str:
    """Plain, single-line text cut to `limit` characters."""
    if not text:
        return ""
    text = html.unescape(_TAG.sub(" ", html.unescape(text)))
    text = _SPACE.sub(" ", text).strip()
    if len(text) > limit:
        text = text[: limit - 1].rstrip() + "…"
    return text


def safe_link(url: str | None) -> str:
    """The link if it is plain http(s), else nothing."""
    if not url:
        return ""
    url = url.strip()
    parts = urllib.parse.urlsplit(url)
    if parts.scheme in ("http", "https") and parts.netloc and not re.search(r"[\s<>\"']", url):
        return url
    return ""


def slugify(name: str) -> str:
    """'Adobe Creative Cloud' -> 'adobe-creative-cloud', the way RepoQuarry names pages."""
    s = re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")
    return s


# ---------------------------------------------------------------- RepoQuarry

@dataclass
class Listed:
    """One project on a tool's alternatives page."""
    id: str
    name: str
    url: str
    use_instead: str = ""
    jobs: str = ""
    runs_locally: str = ""
    commercial_use: str = ""
    paid_services: str = ""


_ROW_LINK = re.compile(r"^\[([^\]]+)\]\((https?://[^)\s]+/projects/([a-z0-9][a-z0-9._-]*))\)$")


def _cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def parse_alternatives_md(text: str) -> tuple[str, list[Listed]]:
    """Reads '# Open-source alternatives to X' and the table under '## Projects'."""
    m = re.search(r"^#\s+Open-source alternatives to\s+(.+?)\s*$", text, re.M)
    tool = clean(m.group(1), 80) if m else ""
    lines = text.splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if l.strip().lower() == "## projects")
    except StopIteration:
        return tool, []
    header: list[str] = []
    out: list[Listed] = []
    for line in lines[start + 1:]:
        if line.startswith("## "):
            break
        if not line.lstrip().startswith("|"):
            continue
        cells = _cells(line)
        if not header:
            header = [c.lower() for c in cells]
            continue
        if all(set(c) <= set("-: ") for c in cells):
            continue
        row = dict(zip(header, cells))
        link = _ROW_LINK.match(row.get("project", ""))
        if not link:
            continue
        out.append(Listed(
            id=link.group(3),
            name=clean(link.group(1), 80),
            url=link.group(2),
            use_instead=clean(row.get("use it instead?"), 220),
            jobs=clean(row.get("jobs"), 120),
            runs_locally=clean(row.get("runs locally"), 220),
            commercial_use=clean(row.get("commercial use"), 220),
            paid_services=clean(row.get("paid services"), 220),
        ))
    return tool, out


def parse_project_md(text: str) -> dict[str, str]:
    """Pulls the facts Altwatch quotes from a /projects/<id>.md page."""
    facts: dict[str, str] = {}
    wanted = {
        "code licence": "licence",
        "commercial use": "commercial_use",
        "paid services needed?": "paid_services",
        "setup effort": "setup",
    }
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = _cells(line)
        if len(cells) < 5:
            continue
        key = wanted.get(cells[0].lower())
        if key:
            status = cells[1].lower()
            answer = clean(cells[2], 220)
            if status == "confirmed" or not answer:
                facts[key] = answer or status
            else:
                note = {"partial": "partly confirmed"}.get(status, status)
                facts[key] = f"{answer} ({note})"
            facts[key + "_checked"] = cells[-1] if re.fullmatch(r"\d{4}-\d{2}-\d{2}", cells[-1]) else ""
    m = re.search(r"^- Repository:\s*(\S+)", text, re.M)
    if m:
        facts["repo"] = safe_link(m.group(1))
    return facts


# ---------------------------------------------------------------- feeds

@dataclass
class FeedItem:
    id: str
    title: str
    link: str
    summary: str
    source: str = ""


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def parse_feed(xml_text: str) -> tuple[str, list[FeedItem]]:
    """RSS 2.0 or Atom. Returns the feed's title and its items, newest as given."""
    if "<!ENTITY" in xml_text[:20000].upper():
        raise ValueError("feed declares XML entities; refused")
    root = ET.fromstring(xml_text)
    title = ""
    items: list[FeedItem] = []
    for el in root.iter():
        name = _local(el.tag)
        if name in ("channel", "feed") and not title:
            for child in el:
                if _local(child.tag) == "title":
                    title = clean(child.text, 80)
                    break
        if name not in ("item", "entry"):
            continue
        f = {"title": "", "link": "", "id": "", "summary": ""}
        for child in el:
            c = _local(child.tag)
            if c == "title":
                f["title"] = child.text or ""
            elif c == "link":
                href = child.attrib.get("href")
                if href and child.attrib.get("rel", "alternate") == "alternate":
                    f["link"] = href
                elif not href and child.text:
                    f["link"] = child.text
            elif c in ("guid", "id"):
                f["id"] = (child.text or "").strip()
            elif c in ("description", "summary", "content") and not f["summary"]:
                f["summary"] = child.text or ""
        link = safe_link(f["link"])
        ident = f["id"] or link or f["title"]
        if not ident:
            continue
        items.append(FeedItem(id=ident[:300], title=clean(f["title"], 140),
                              link=link, summary=clean(f["summary"], 200)))
    return title, items


def keyword_hit(item: FeedItem, keywords: list[str]) -> str:
    """The first keyword found as whole words in the title or summary, else ''."""
    hay = f"{item.title} {item.summary}".lower()
    for kw in keywords:
        k = kw.strip().lower()
        if k and re.search(r"(?<![a-z0-9])" + re.escape(k) + r"(?![a-z0-9])", hay):
            return kw.strip()
    return ""


def miniflux_entries(base: str, token: str, search: str, budget: Budget, limit: int = 20) -> list[FeedItem]:
    """Unread entries matching `search`, from Miniflux's API (GET /v1/entries)."""
    q = urllib.parse.urlencode({"status": "unread", "search": search, "limit": limit,
                                "order": "published_at", "direction": "desc"})
    text = http_get(base.rstrip("/") + "/v1/entries?" + q, budget, {"X-Auth-Token": token})
    try:
        data = json.loads(text)
        entries = data["entries"]
    except (ValueError, KeyError, TypeError):
        raise FetchError(base, 0, "Miniflux answered with something that isn't an entry list") from None
    out = []
    for e in entries:
        if not isinstance(e, dict) or "id" not in e:
            continue
        feed = e.get("feed") or {}
        out.append(FeedItem(id=f"miniflux-{e['id']}", title=clean(e.get("title"), 140),
                            link=safe_link(e.get("url")), summary=clean(e.get("content"), 200),
                            source=clean(feed.get("title"), 60)))
    return out
