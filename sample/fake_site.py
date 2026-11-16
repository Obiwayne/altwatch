"""A stand-in website for testing Altwatch on your own computer.

It serves three things from memory, on 127.0.0.1:
- RepoQuarry-style Markdown pages (/alternatives/<tool>.md, /projects/<id>.md)
- an RSS feed (/blog/feed.xml)
- a stand-in for Miniflux's API (/v1/entries), which wants the right X-Auth-Token

Nothing here talks to the internet.
"""
from __future__ import annotations

import json
import os
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
TOKEN = "test-token-not-a-real-one"

ROW = ("| [{name}](https://repoquarry.dev/projects/{id}) | Personal use: Yes. Business: Yes. | {jobs} | "
       "{local} | {commercial} | {paid} | No figures published |")

PROJECT_PAGE = """# {name}

> {name} is a made-up project used to test Altwatch. It does not exist.

- Repository: https://github.com/example/{id}
- Checked: {checked}

## What it replaces
- {tool}: {jobs} (partial).

## Facts, with sources

| Question | Status | Answer | Source | Checked |
|---|---|---|---|---|
| Runs on my machine? | Confirmed | {local} | https://example.com/{id}/readme | {checked} |
| Code licence | Confirmed | {licence} | https://example.com/{id}/LICENSE | {checked} |
| Commercial use | Confirmed | {commercial} | https://example.com/{id}/LICENSE | {checked} |
| Paid services needed? | Confirmed | {paid} | https://example.com/{id}/pricing | {checked} |
| Setup effort | Confirmed | {setup} | https://example.com/{id}/install | {checked} |
"""

MADE_UP = {
    "pagewell": dict(id="pagewell", name="Pagewell", tool="Notion", jobs="notes, wiki-docs",
                     local="Yes; a desktop app that keeps notes in a local folder",
                     licence="AGPL-3.0", commercial="Allowed under AGPL-3.0; share your changes if you run it for others",
                     paid="None required; sync between devices is an optional paid plan",
                     setup="Easy; download the installer", checked="2026-11-12"),
    "flowkiln": dict(id="flowkiln", name="Flowkiln", tool="Zapier", jobs="app-workflows, databases",
                     local="Self-hosted with Docker",
                     licence="Apache-2.0", commercial="Yes; Apache-2.0 allows commercial use",
                     paid="None; you need a server to run it on",
                     setup="Medium; Docker Compose and a database", checked="2026-11-15"),
}


def rss(items: list[dict]) -> str:
    body = "\n".join(
        f"<item><title>{i['title']}</title><link>{i['link']}</link><guid>{i['link']}</guid>"
        f"<description>{i.get('summary', '')}</description></item>" for i in items)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>'
            f"<title>Maker Notes</title><link>https://makernotes.example</link>\n{body}\n</channel></rss>\n")


def add_row(page: str, proj: dict) -> str:
    """Adds one project row to the end of a page's Projects table."""
    lines = page.splitlines()
    start = next(i for i, l in enumerate(lines) if l.strip() == "## Projects")
    last = max(i for i, l in enumerate(lines[start:], start) if l.startswith("| [")
               and not any(x.startswith("## ") for x in lines[start + 1:i]))
    lines.insert(last + 1, ROW.format(**proj))
    return "\n".join(lines) + "\n"


class FakeSite:
    """`pages` maps a path to (status, content type, text). Change it between runs."""

    def __init__(self):
        self.pages: dict[str, tuple[int, str, str]] = {}
        self.entries: list[dict] = []      # Miniflux entries
        self.hits: list[str] = []
        site = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):  # keep test output quiet
                pass

            def do_GET(self):
                parts = urllib.parse.urlsplit(self.path)
                site.hits.append(parts.path)
                if parts.path == "/v1/entries":
                    if self.headers.get("X-Auth-Token") != TOKEN:
                        return self._send(401, "application/json", '{"error_message":"Access Unauthorized"}')
                    q = urllib.parse.parse_qs(parts.query)
                    term = (q.get("search") or [""])[0].lower()
                    hits = [e for e in site.entries if e.get("status", "unread") in q.get("status", ["unread"])
                            and term in (e["title"] + " " + e.get("content", "")).lower()]
                    return self._send(200, "application/json", json.dumps({"total": len(hits), "entries": hits}))
                status, ctype, text = site.pages.get(parts.path, (404, "text/html", "<h1>Not found</h1>"))
                self._send(status, ctype, text)

            def _send(self, status, ctype, text):
                data = text.encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", ctype + "; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.server.server_port}"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def close(self):
        self.server.shutdown()
        self.server.server_close()

    # helpers for the tests and the sample week
    def page(self, path: str, text: str, ctype: str = "text/markdown", status: int = 200):
        self.pages[path] = (status, ctype, text)

    def load_snapshot(self, tool: str) -> str:
        """A real RepoQuarry page saved on 16 Nov 2026 (data CC BY 4.0)."""
        with open(os.path.join(HERE, "site", "alternatives", tool + ".md"), encoding="utf-8") as f:
            text = f.read()
        self.page(f"/alternatives/{tool}.md", text)
        return text

    def list_project(self, tool: str, key: str):
        """Lists a made-up project on a tool's page and gives it a facts page."""
        proj = MADE_UP[key]
        self.page(f"/alternatives/{tool}.md", add_row(self.pages[f"/alternatives/{tool}.md"][2], proj))
        self.page(f"/projects/{proj['id']}.md", PROJECT_PAGE.format(**proj))
