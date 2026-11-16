# Altwatch build log

Build 5 in RepoQuarry's queue. Built by a scheduled, unattended run on 16 November 2026 (Windows 11, Python 3.13.5). Times are from the PC's clock, UK time.

| Time | What |
|---|---|
| 08:35 | Start. Two builds (Prepnote, Subtrim) were waiting, so the stop rule didn't apply. Queue entry 5 picked: no Altwatch folder or review row yet. |
| 08:36 | Parts checked on `origin/main` at 9921dcb and on GitHub. Miniflux (`miniflux/v2`): Apache-2.0, not archived, last push 12 Nov 2026. RSSHub (`DIYgod/RSSHub`): AGPL-3.0, not archived, last push 16 Nov 2026. Both pass. Altwatch only reads from them and includes none of their code. |
| 08:37 | Live site read to learn its shape: `/feed.xml`, `/alternatives/<tool>.md`, `/projects/<id>.md`, the JSON API and the MCP tool list. The JSON API allows 10 requests a minute without a key, so Altwatch reads the Markdown pages instead. |
| 08:38-08:41 | Preview tool written: page and feed readers, the daily check, state file, message, command line. Stand-in website and sample week written. |
| 08:41 | 47 tests pass. Sample week gives the numbers below. |
| 08:42 | Live check against repoquarry.dev from a 9 Nov starting point. Numbers below. |
| 08:43 | Two wording faults fixed (see below). 48 tests pass. Live check run again with the same result. |
| 08:43-08:45 | One MCP lookup run against the live server. Skill, routine and README written. |
| 08:46-08:53 | Stills checked in both sizes, voiceover made (one ElevenLabs pass: 7 new lines, line 1 reused from the approved take), lines re-timed, 20 s video rendered in 16:9 and 9:16 at -14.1 LUFS. |
| 08:53-08:57 | Cover, two pictures, six slides, guide page and posts written. |

The end time and the guide's check results are in the last section.

## Numbers measured

### Sample week (stand-in website on this PC, dates 9 to 15 Nov 2026)

Watching Notion and Zapier, one made-up blog feed with two keywords, and a Miniflux stand-in with one keyword.

- 7 daily runs: 1 start-up note, 3 alerts, 3 silent.
- Mon: first run. Notion 9 listed, Zapier 6 listed. Start-up note, no alert.
- Tue: a blog post about a dog. Silent. Wed: nothing. Silent.
- Thu: Pagewell listed for Notion. Alert with licence, use at work, running cost and link.
- Fri: nothing. Silent.
- Sat: one matching blog post and one matching reader entry. One alert with both.
- Sun: Flowkiln listed for both Zapier and Notion. One alert, one entry naming both tools.
- 30 requests in the week. 4 on a quiet day, 5 on a day with a new project. The cap for this watch file is 9 a run.

The Notion and Zapier pages are real RepoQuarry pages saved on 16 Nov 2026. Pagewell, Flowkiln, the Maker Notes blog and the reader entries are made up.

### Live check (repoquarry.dev, 16 Nov 2026, 08:42)

- Starting point: every project listed for six tools in RepoQuarry's catalogue at commit 61183ab (9 Nov 2026), built with `tools/state_from_checkout.py`. Notion 8, Evernote 3, Adobe Creative Cloud 13, Claude Code 10, Slack 13, Asana 3.
- One check found 10 new alternatives: Logseq (Notion and Evernote), Memos and Notesnook (Evernote), LosslessCut, Shotcut and OpenShot (Adobe Creative Cloud), CLIProxyAPI and Qwen Code (Claude Code), Agentes-chat (Slack), Kanzo (Asana).
- Listed on the day: Notion 9, Evernote 6, Adobe Creative Cloud 16, Claude Code 12, Slack 14, Asana 4.
- All 10 in one message. Logseq, new for two tools, appeared once.
- 11 requests (6 tool pages and 5 facts pages, the cap), about 3 seconds by the clock.
- 4 of the 10 (CLIProxyAPI, Qwen Code, Agentes-chat, Kanzo) had "Not checked yet" for commercial use and paid services. The message called each a lead and gave no licence.
- The sixth project, OpenShot, was past the facts-page cap. Its line read "Licence: on the page below", with use at work and running cost taken from the tool's page.
- A second check straight after: no message, 6 requests.
- The message is in `sample/live-2026-11-16/message.txt`.

### Other live reads

- `https://repoquarry.dev/feed.xml`: 209 posts parsed on the first read, no alert.
- `https://repoquarry.dev/alternatives/not-a-real-tool.md`: 404, which Altwatch reports once as "no page".
- MCP `search_projects`, query "Notion", limit 20: `interpreted_as.paid_product` was "Notion", 9 results, the same 9 as the page. A limit of 25 was refused: the most is 20.

## Found and fixed during the build

- A fact with the status "partial" was printed as "GPL-3.0 (copyleft) (partial)". It now reads "(partly confirmed)".
- Draft projects printed "Use at work: Not checked yet" and "Running cost: Not checked yet". They now get one line: "RepoQuarry hasn't checked its licence or cost yet. Treat it as a lead, not a swap."
- A project past the facts-page cap showed no licence line at all. It now says "Licence: on the page below".
- The video's voice lines came back longer than planned and three ran into the next. They were re-timed, not re-voiced: line 2 now starts over the last problem word.
- The video's three cards first showed the made-up blog posts under the heading "New alternatives 10", which read as if they were the alternatives. They now show three of the real ten.

## Not tested, and why

- **Grok Bot.** No plan to test on. The skill and routine come from xAI's documentation.
- **A real Miniflux or RSSHub.** This PC has no Docker. Miniflux is tested against a stand-in that answers `GET /v1/entries` (with `status`, `search`, `limit` and the `X-Auth-Token` header) the way its API documentation describes. Feeds are tested with hand-written RSS and Atom and with RepoQuarry's real feed.
- **A real week of daily runs.** The sample week moves the date forward by hand.
- **Share of the Grok Bot weekly allowance.** Not measurable without a plan.

## Cost

- Plan: X Premium ($30/month) or higher for Grok Bot.
- Runs: 1 scheduled run a day, 7 a week.
- Cap: at most 1 request per tool (10 tools), 1 per feed (5 feeds), 1 per Miniflux keyword (5), and 5 facts pages in a run. Feeds skipped past 70% of the allowance. No retry loop, no Bot-to-Bot hand-offs.
- RepoQuarry's pages and MCP server: free, no account. Miniflux and RSSHub: free, but they need somewhere to run.
- Voiceover for the promo video: one ElevenLabs pass, 7 new lines, no re-runs.
