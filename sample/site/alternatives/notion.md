# Open-source alternatives to Notion

> Open-source alternatives to Notion that run locally, allow commercial use and need nothing paid include Logseq (notes; AGPL-3.0-only) and Trilium Notes (notes and wikis and docs; AGPL-3.0; runs on CPU). Macro and SiYuan are also allowed at work, but have a paid option or don't fully run on your own computer; see below. AFFiNE and Anytype cover all 4 Notion jobs.

Notion: Paid cloud workspace for notes, wikis and docs, and databases shown as tables and boards, synced across devices. Pricing: Free plan; Plus £8.50 and Business £16.50 per member/month billed yearly (GBP as shown); Enterprise custom (checked 2026-10-15). Facts checked 2026-11-14.

## Projects

| Project | Use it instead? | Jobs | Runs locally | Commercial use | Paid services | Hardware |
|---|---|---|---|---|---|---|
| [AppFlowy](https://repoquarry.dev/projects/appflowy) | Personal use: Yes. Business: Partly (Commercial use with conditions: AGPL client usable commercially; team server is commercial, free tier 1 seat). | notes, wiki-docs, sync | Desktop app; self-hosted server uses a closed-source commercial image | AGPL client usable commercially; team server is commercial, free tier 1 seat | None for personal use; Pro cloud and paid self-hosted tiers for teams | Android app needs Android 10 or newer (ARMv7 not supported); no desktop or server hardware figures published |
| [AFFiNE](https://repoquarry.dev/projects/affine) | Personal use: Yes. Business: Partly (Commercial use with conditions: MIT client; EE-only backend parts need an AFFiNE subscription in production). | notes, wiki-docs, databases, sync, real-time-collaboration | Local-first desktop app; server self-hosted with Docker | MIT client; EE-only backend parts need an AFFiNE subscription in production | None required; AFFiNE Cloud Pro/Team and Self-Hosted Team are optional | Self-hosted server: 2 GB RAM for basic use (4 GB for docs over 10k words), at least 4 CPU cores recommended, about 1.5 GB free disk plus data |
| [Joplin](https://repoquarry.dev/projects/joplin) | Personal use: Yes. Business: Partly (Commercial use with conditions: AGPL apps OK; Joplin Server is personal-use only (Business tier is paid)). | notes, sync | Desktop and mobile apps; notes stored locally, sync optional | AGPL apps OK; Joplin Server is personal-use only (Business tier is paid) | None required; Joplin Cloud and Joplin Server Business are optional | Android app needs Android 7.0 or newer (minSdk 24); no desktop hardware figures published |
| [SiYuan](https://repoquarry.dev/projects/siyuan) | Personal use: Yes. Business: Yes. | notes, wiki-docs, databases | Desktop app with local storage; Docker server option (browser only) | Yes; AGPL-3.0, and most features free for commercial use | Free locally; any sync (S3/WebDAV or official cloud) is paid | Android 8.0 or newer (minSdk 26) |
| [Logseq](https://repoquarry.dev/projects/logseq) | Personal use: Yes. Business: Yes. | notes | Yes; a desktop app (also a browser app and an iOS beta) that keeps your notes on your device; sync is optional | Allowed under AGPL-3.0; if you change it and run it as a network service, you must share your changed source | None required; the app is free. Optional paid Logseq Sync and Publish come with OpenCollective backing ($5/month backer, $15/month sponsor), or you can self-host them | No desktop minimum figures published (checked README, DB version docs, 2.0.2 release notes); the iOS beta needs a recent iOS version |
| [Outline](https://repoquarry.dev/projects/outline) | Personal use: Yes. Business: Partly (Commercial use with conditions: Production use allowed, except offering a commercial Document Service). | wiki-docs, notes | Self-hosted server (Docker) or hosted; no desktop app documented | Production use allowed, except offering a commercial Document Service | None required to self-host; hosted getoutline.com is optional | 512 MB RAM minimum, 1 GB+ recommended; low-powered CPU fine |
| [Trilium Notes](https://repoquarry.dev/projects/trilium) | Personal use: Yes. Business: Yes. | notes, wiki-docs, sync | Desktop app, plus self-hosted sync server with web UI | Yes under AGPL-3.0 (share source of modified network versions) | None; sync uses your own server (third-party hosts exist) | x64 and ARM64 supported on Windows, Linux and macOS (no ARMv7); Docker server image for AMD64 and ARM; no RAM or disk figures documented |
| [Anytype](https://repoquarry.dev/projects/anytype) | Personal use: Yes. Business: Partly (Commercial use with conditions: Commercial use only on networks authorised by Any Association). | notes, wiki-docs, databases, sync | Offline-first desktop app; optional self-hosted sync network | Commercial use only on networks authorised by Any Association | Free tier; paid memberships add storage, shared channels, ANY ID | Self-hosted sync network needs Docker and ~1 GB RAM; client needs not documented |
| [Macro](https://repoquarry.dev/projects/macro) | Personal use: Partly (Runs locally only in part: Self-hosting is allowed under the AGPL but is not a focus yet; the only documented route…). Business: Partly. | notes, wiki-docs, channels-and-dms, threaded-replies, huddles-and-calls, message-search, contacts-companies, deal-pipeline, email-calendar-sync, task-management, kanban-boards | Self-hosting is allowed under the AGPL but is not a focus yet; the only documented route is a developer Docker stack (Postgres, Redis, LocalStack, OpenSearch, Kafka, FusionAuth) with stubbed integrations. Hosted Macro is the main product | Commercial use allowed under AGPL-3.0; if you build on Macro or offer a modified version over a network you must share that source under the AGPL, or buy a different licence from Macro | Self-hosting needs no Macro plan, but the FAQ says you must hold your own licences for LiveKit (calls), FusionAuth (sign-in) and PostHog (analytics) or turn them off; Gmail, agents and GitHub need your own Google/GitHub OAuth apps. Hosted plans: Free, Pro $40 and Max $200 per seat a month | Not documented (checked README and docs/development/running-locally.md) |

## Common questions

### Is there a free, open-source alternative to Notion?

Yes. Anytype, AFFiNE, Macro, Joplin and Trilium Notes are free to download and run on your own computer without paid API keys. Anytype and AFFiNE cover every job we list for Notion; the others cover only part of it, so check which job you need.

### Is Anytype open source?

Not under the OSI definition. Anytype's apps use the Any Source Available License 1.0, which lets you use, change and share the code for non-commercial use, or for commercial use on networks that Any Association authorises. (source: https://github.com/anyproto/anytype-ts/blob/develop/LICENSE.md)

### Is Outline open source?

Its licence says it is not. Outline uses the Business Source License 1.1, which allows production use except offering a commercial document service to others; each version later converts to Apache-2.0. (source: https://github.com/outline/outline/blob/main/LICENSE)

### Can I self-host a Notion alternative?

Yes. 8 of the 9 can run on your own server: AFFiNE, Anytype, AppFlowy, Joplin, Logseq and Outline (and 2 more). AFFiNE, Anytype, AppFlowy and Outline (and 2 more) document a Docker setup. Setup is rated easy for AFFiNE, Anytype and AppFlowy (and 4 more).

### What hardware do I need to run a Notion alternative?

Memory stated in their docs: 512 MB for Outline and 1 GB for Anytype. The others give no single figure. Each project page quotes the source and says whether a figure is a minimum or a recommendation.

### Which Notion alternatives run on Windows, macOS or Linux?

Windows: AFFiNE, Anytype, AppFlowy, Joplin and Logseq (and 2 more). macOS: AFFiNE, Anytype, AppFlowy, Joplin and Logseq (and 3 more). Linux: AFFiNE, Anytype, AppFlowy, Joplin and Logseq (and 4 more). The rest are web apps or servers, or their docs don't say which systems they support.

### Which Notion alternatives can I use commercially?

Confirmed: Logseq, Macro, SiYuan and Trilium Notes. With conditions: AFFiNE, Anytype, AppFlowy, Joplin and Outline. This is not legal advice; read each licence.

### Does any open-source project replace all of Notion?

AFFiNE and Anytype cover every job we list for Notion.

---
Source: RepoQuarry (https://repoquarry.dev/alternatives/notion). Data licence: CC BY 4.0. Quotes are from project documentation and belong to their authors.
