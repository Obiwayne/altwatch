# Altwatch

One message when a new open-source alternative to a tool you pay for appears. Silence the rest of the time.

Altwatch watches [RepoQuarry](https://repoquarry.dev), a catalogue of open-source alternatives with a source and a date for every fact. You name the tools you pay for. Once a day it compares what is listed with what it has already seen. If something is new, you get its licence, whether you can use it at work, what it costs to run, and a link. If nothing is new, you get nothing.

Altwatch is two things:

1. **A Grok Bot skill and routine** (`grok-bot/`). The Bot runs the check once a day and messages you only when there is something new. **Not yet tested on Grok Bot.**
2. **A preview tool** (`altwatch/`). The same check on your own computer. Python 3.10 or later, nothing to install. It only reads web pages; it sends nothing. This part is tested.

## Try it in a minute

```
copy watch.example.json watch.json
python -m altwatch check
```

The first run replies with what is listed so far. That is your starting point. Run it again tomorrow, or put it in Task Scheduler or cron. A quiet day prints nothing.

To see a week of messages without waiting a week:

```
python sample/run_week.py
```

This runs seven daily checks against a stand-in website on your own computer. The Notion and Zapier pages in it are real RepoQuarry pages saved on 16 November 2026. The two "new" projects (Pagewell and Flowkiln), the blog and the reader entries are made up.

## The watch file

```json
{
  "tools": ["Notion", "Zapier"],
  "feeds": [
    {"name": "RepoQuarry new and trending", "url": "https://repoquarry.dev/feed.xml", "keywords": ["note-taking", "automation"]}
  ],
  "miniflux": {"url": "http://localhost:8080", "token_env": "MINIFLUX_TOKEN", "keywords": ["notion alternative"]}
}
```

- `tools`: up to 10. Names as on RepoQuarry (`https://repoquarry.dev/alternatives`). If a tool has no page, Altwatch tells you once.
- `feeds` (optional): up to 5 RSS or Atom feeds. A post counts only when it is new and its title or summary contains one of your keywords as whole words. [RSSHub](https://github.com/DIYgod/RSSHub) routes are ordinary feeds, so they go here.
- `miniflux` (optional): searches the unread entries in your own [Miniflux](https://github.com/miniflux/v2) for up to 5 keywords. The API key is read from the environment variable you name. Altwatch refuses a watch file with the key written in it. It never marks anything as read.

## What you get

- `message-<date>.txt` in `altwatch-out/` on days with something to say, and the same text on screen.
- `altwatch.log`: one entry per run, including quiet ones.
- `altwatch-state.json`: what has been seen. Delete it to start again.
- `python -m altwatch status` shows what is watched and how many runs were silent.

## How it behaves

- **First look at a tool or feed is never an alert.** It records what is there.
- **Each new project is reported once**, even if it is new for two of your tools.
- **A page that fails is not "everything is new".** Altwatch keeps what it knew and tries again next day. After 3 failed days in a row it says so, once.
- **Unchecked projects are called leads.** If RepoQuarry hasn't checked a project's licence or cost yet, the message says that instead of guessing.
- **A run has a request cap**: one per tool, one per feed, one per Miniflux keyword, and at most 5 project pages. With everything at its limit that is 25.
- **Text from feeds is cleaned**: tags stripped, cut short, and only plain web links kept.

## What we tested (16 November 2026, Windows 11, Python 3.13.5)

- 48 automated tests pass (`python -m unittest discover -s tests`). They run against a stand-in website on the same computer, over real HTTP.
- **The sample week:** 7 daily runs gave 1 start-up note, 3 alerts and 3 silent days. The alerts were one new project for Notion, two posts on watched topics (one from a feed, one from the Miniflux stand-in), and one project new for both Zapier and Notion, reported once. The 7 runs made 30 requests, never more than 5 in a run.
- **The live site:** we built a starting point from RepoQuarry's catalogue as it stood on 9 November 2026 for six tools (Notion, Evernote, Adobe Creative Cloud, Claude Code, Slack, Asana), then ran one check against repoquarry.dev on 16 November. It reported 10 new alternatives in one message, with 11 requests in about 3 seconds. Four of the ten were drafts RepoQuarry hadn't checked yet, and the message said so. A second run straight after was silent, with 6 requests. The message is in `sample/live-2026-11-16/`.
- **The live feed:** `https://repoquarry.dev/feed.xml` parsed as 209 posts on its first read, with no alert, as intended.
- **The MCP server:** one `search_projects` call for "Notion" with `limit` 20 returned the same 9 projects as the page. The most it returns is 20, so the skill reads the page when a list is longer.

## What we haven't tested

- The skill and routine on a real Grok Bot plan, or how much of the weekly allowance a daily run uses.
- A real Miniflux or RSSHub. This computer has no Docker, so the Miniflux tests use a stand-in that answers `GET /v1/entries` the way Miniflux's API documentation describes, and the feed tests use hand-written RSS and Atom.
- A real week of daily runs. The sample week moves the date forward by hand.
- Feeds in unusual formats, or bigger than 2 MB (refused).

## Licences

Altwatch is MIT. The two saved pages in `sample/site/` and the message in `sample/live-2026-11-16/` are RepoQuarry data, CC BY 4.0. Miniflux is Apache-2.0 and RSSHub is AGPL-3.0; Altwatch only reads from them and includes none of their code.
