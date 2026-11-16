# Altwatch routine for Grok Bot

Status: **not yet tested on Grok Bot.**

## The one scheduled run

Ask your Bot:

> Create a routine called "Altwatch daily". Every day at 07:30 in my time zone, run the Altwatch skill's daily check. If nothing is new, send me nothing. If something is new, send one message. Run it once. Don't retry more than once if it fails.

That is 7 runs a week. RepoQuarry adds most new projects in a nightly job, so checking more than once a day rarely finds anything extra.

## Tell it what to watch

> Altwatch: watch Notion, Zapier and Adobe Creative Cloud.

Up to 10 tools. The Bot replies once with how many alternatives each already has. After that it stays quiet until something new is listed.

## Extra feeds (optional)

RepoQuarry covers 90 paid products. For anything else, give the Bot a feed address and keywords:

> Altwatch: also watch https://repoquarry.dev/feed.xml for "note-taking" and "automation".

- Any RSS or Atom feed works.
- [RSSHub](https://repoquarry.dev/projects/rsshub) (AGPL-3.0) makes feeds for sites that have none. Run your own copy and give the Bot the route's address. The Bot can only read it if your RSSHub is reachable from the internet.
- [Miniflux](https://repoquarry.dev/projects/miniflux) (Apache-2.0) is a feed reader you host yourself. The preview tool in this repo can search it through its API. Don't paste a Miniflux API key into a chat with your Bot; use the preview tool for that instead.

## Connecting RepoQuarry

The skill reads plain Markdown pages, so nothing needs connecting. If you'd rather use the MCP server, ask your Bot to add `https://repoquarry.dev/mcp`. It is read-only and needs no key. Adding MCP servers through chat is described by Composio, not in xAI's own documentation, so it may not work on every plan.

## Cost

| | |
|---|---|
| Plan needed | X Premium ($30/month) or higher, which includes Grok Bot |
| Scheduled runs | 1 a day, 7 a week |
| Requests in a run | At most 1 per tool, 1 per feed, and 5 facts pages. With 10 tools and 5 feeds that is 20 |
| Share of the weekly allowance | Not measured. We have no Grok Bot plan to test on yet |
| RepoQuarry, Miniflux, RSSHub | Free. Miniflux and RSSHub need somewhere to run |

## Before the first run

Try the preview tool in this repo. It does the same check on your own computer, so you can see what the messages look like before giving a Bot the job.
