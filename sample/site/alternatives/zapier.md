# Open-source alternatives to Zapier

> The one open-source alternative to Zapier that runs locally, allows commercial use and needs nothing paid is Huginn (app-to-app workflows, scheduled automations and webhooks; MIT; runs on CPU). Activepieces and Langflow are also allowed at work, but have a paid option or don't fully run on your own computer; see below. Activepieces and n8n cover all 4 Zapier jobs.

Zapier: Paid hosted automation platform that connects web apps with multi-step workflows, schedules, webhooks and AI agents. Pricing: Free (100 tasks per month, two-step Zaps); Professional from $19.99/month; Team from $69/month (checked 2026-10-15). Facts checked 2026-11-14.

## Projects

| Project | Use it instead? | Jobs | Runs locally | Commercial use | Paid services | Hardware |
|---|---|---|---|---|---|---|
| [n8n](https://repoquarry.dev/projects/n8n) | Personal use: Yes. Business: Partly (Commercial use with conditions: Only for your own internal business use; no reselling or offering n8n to others for a fee). | app-workflows, scheduled-automations, ai-agent-workflows, webhooks | Self-hosted with Docker or npm; n8n Cloud also offered | Only for your own internal business use; no reselling or offering n8n to others for a fee | None required; Enterprise License and n8n Cloud are optional paid extras; AI nodes use your own model provider keys | Illustrative sizing from n8n Cloud: 320 MB to 2 GB memory, 512 MB to 4 GB SSD for the database; not CPU-intensive, so small instances suffice |
| [Dify](https://repoquarry.dev/projects/dify) | Personal use: Yes. Business: Partly (Commercial use with conditions: Commercial use allowed, but a multi-tenant service needs written permission and the web f…). | scheduled-automations, ai-agent-workflows, webhooks, document-chat | Self-hosted with Docker Compose on your machine or server; Dify Cloud also offered | Commercial use allowed, but a multi-tenant service needs written permission and the web frontend's logo and copyright may not be removed | Not required with local models via the Ollama plugin; cloud model APIs, Dify Cloud and Dify Enterprise are optional | Minimum 2 CPU cores and 4 GiB RAM; on macOS the docs ask for a Docker VM with 2 vCPUs and 8 GiB |
| [Langflow](https://repoquarry.dev/projects/langflow) | Personal use: Yes. Business: Yes. | ai-agent-workflows, webhooks, document-chat | Yes, as a desktop app, a local Python package or a Docker container you host | Allowed under MIT | Not required with local models via Ollama; cloud model API keys are optional | Python package: dual-core CPU and 2 GB RAM minimum; multi-core CPU and 4 GB RAM recommended |
| [Huginn](https://repoquarry.dev/projects/huginn) | Personal use: Yes. Business: Yes. | app-workflows, scheduled-automations, webhooks | Self-hosted on your own server (Docker or manual install) | Yes, MIT code | None required; AI agents use your own OpenAI-compatible API if you choose | 0.5 GB RAM + 0.5 GB swap minimum, 2 GB RAM recommended; dual core recommended |
| [Activepieces](https://repoquarry.dev/projects/activepieces) | Personal use: Yes. Business: Yes. | app-workflows, scheduled-automations, ai-agent-workflows, webhooks | Self-hosted with Docker; Activepieces Cloud also offered | Yes for the MIT Community Edition; enterprise features need a paid licence | None required; enterprise licence and Activepieces Cloud are optional | Production sizing: app 1 vCPU / 1 GB per ten workers; each worker 0.5 vCPU / 1 GB; Postgres 2 vCPU / 4 GB; Redis 1 vCPU / 1 GB |
| [Windmill](https://repoquarry.dev/projects/windmill) | Personal use: Yes. Business: Partly (Commercial use with conditions: Free for internal use; reselling, managed service or embedding in a product needs AGPL co…). | app-workflows, scheduled-automations, webhooks | Self-hosted with Docker Compose or Kubernetes; Windmill cloud also offered | Free for internal use; reselling, managed service or embedding in a product needs AGPL compliance or a commercial licence | None required; Enterprise Edition and Windmill cloud are optional | Rule of thumb 1 vCPU and 1-2 GB RAM per worker, plus Postgres |

## Common questions

### Is there a free, open-source alternative to Zapier?

Yes. n8n, Huginn, Activepieces, Dify and Windmill are free to download and run on your own computer without paid API keys. n8n and Activepieces cover every job we list for Zapier; the others cover only part of it, so check which job you need.

### Can I do app-to-app workflows locally without a Zapier subscription?

Yes, with Huginn (MIT), n8n (Custom licence) and Activepieces (MIT). Check the hardware notes and licence conditions on each page before you start.

### Can I do scheduled automations locally without a Zapier subscription?

Yes, with Huginn (MIT), n8n (Custom licence) and Dify (Custom licence). Check the hardware notes and licence conditions on each page before you start.

### Can I self-host a Zapier alternative?

Yes. All 6 can run on your own server: Activepieces, Dify, Huginn, Langflow, n8n and Windmill. All of them document a Docker setup. Setup is rated easy for Langflow.

### What hardware do I need to run a Zapier alternative?

Memory stated in their docs: 512 MB for Huginn, 1 GB for Windmill, 2 GB for Langflow and 4 GB for Dify. The others give no single figure. Each project page quotes the source and says whether a figure is a minimum or a recommendation.

### Which Zapier alternatives run on Windows, macOS or Linux?

Windows: Dify, Langflow, n8n and Windmill. macOS: Dify, Langflow, n8n and Windmill. Linux: Dify, Huginn, Langflow, n8n and Windmill. The rest are web apps or servers, or their docs don't say which systems they support.

### Which Zapier alternatives can I use commercially?

Confirmed: Activepieces, Huginn and Langflow. With conditions: Dify, n8n and Windmill. This is not legal advice; read each licence.

### Does any open-source project replace all of Zapier?

Activepieces and n8n cover every job we list for Zapier.

---
Source: RepoQuarry (https://repoquarry.dev/alternatives/zapier). Data licence: CC BY 4.0. Quotes are from project documentation and belong to their authors.
