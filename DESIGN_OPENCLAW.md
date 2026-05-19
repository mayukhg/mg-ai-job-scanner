# Alternate Design — OpenClaw Implementation

> This is an alternate implementation design using [OpenClaw](https://openclaw.ai),
> an open-source local-first AI agent framework. Compare with [DESIGN.md](DESIGN.md)
> which uses the Anthropic Agents SDK directly.

---

## Why OpenClaw?

| Concern | Anthropic SDK Approach | OpenClaw Approach |
|---|---|---|
| Orchestration | Custom Python orchestrator | Built-in **Gateway + TaskFlow** |
| Scheduling | GitHub Actions / external cron | Built-in **Proactive Engine** |
| Workflows | Imperative Python code | Declarative **Lobster YAML** |
| Tool integrations | Manual API clients | **MCPorter** (100+ MCP connectors) |
| Memory / Theme DB | SQLite + JSON | Built-in **local markdown + vector store** |
| LLM | Claude API (cloud) | Claude, Gemini, or local Ollama — your choice |
| Data privacy | Data leaves your machine | **Local-first** — nothing sent to third parties |

---

## OpenClaw Runtime Components Used

| Component | Role in This Agent |
|---|---|
| **Gateway** | Central control plane — routes all messages, sessions, and agent calls |
| **TaskFlow** | Durable 5-step pipeline: scrape → analyze → write → store → notify |
| **Lobster Engine** | YAML-defined weekly workflow definition |
| **Proactive Engine** | Monday 8AM cron trigger — no external scheduler needed |
| **MCPorter** | Bridges to Playwright (scraping), Dropbox MCP, Gmail MCP, GitHub MCP |
| **Memory Store** | `~/.openclaw/memory/` — persists weekly theme snapshots as markdown + vectors |
| **AgentSkills** | Shell, file system, and web automation primitives used by scraper skill |

---

## Lobster Workflow Definition

The entire weekly pipeline is defined in a single YAML file processed by OpenClaw's
Lobster orchestration engine:

```yaml
# workflows/weekly_job_scan.yaml

name: weekly_job_scan
description: Scan Pune PM/AI job postings, extract themes, update resume, deliver

schedule:
  cron: "0 8 * * MON"   # Every Monday 8:00 AM (Proactive Engine)
  timezone: Asia/Kolkata

variables:
  location: "Pune, India"
  job_titles:
    - "AI Product Manager"
    - "Agentic AI Product Manager"
    - "Director of Product Management"
    - "Senior Director of Product Management"
    - "VP of Product Management"
  dropbox_folder: "/Resumes/Weekly"
  email_to: "mayukhg@gmail.com"

steps:

  - id: scrape_jobs
    name: Scrape job postings
    skill: web_scraper
    mcp: playwright
    input:
      sources: [linkedin, naukri, indeed, glassdoor]
      titles: ${{ variables.job_titles }}
      location: ${{ variables.location }}
      posted_within_days: 7
    output: raw_postings

  - id: extract_themes
    name: Analyze themes with LLM
    skill: llm_analyze
    model: claude-sonnet-4-6          # swap for ollama/llama3 for fully local
    depends_on: [scrape_jobs]
    input:
      postings: ${{ steps.scrape_jobs.output }}
      prompt_template: prompts/theme_extraction.md
    output: theme_map

  - id: save_themes
    name: Persist themes to memory
    skill: memory_write
    depends_on: [extract_themes]
    input:
      content: ${{ steps.extract_themes.output }}
      path: "themes/themes_{{ date }}.md"
      tags: [themes, weekly]

  - id: write_resume
    name: Rewrite resume with Claude
    skill: llm_generate
    model: claude-sonnet-4-6
    depends_on: [extract_themes]
    input:
      base_file: workspace/base_resume.docx
      themes: ${{ steps.extract_themes.output }}
      prompt_template: prompts/resume_writer.md
      output_filename: "Resume_Mayukh_Ghosh_PM_WeekOf_{{ date }}.docx"
    output: resume_file

  - id: upload_dropbox
    name: Upload resume to Dropbox
    skill: file_upload
    mcp: dropbox
    depends_on: [write_resume]
    input:
      file: ${{ steps.write_resume.output }}
      destination: "${{ variables.dropbox_folder }}/Resume_Mayukh_Ghosh_PM_WeekOf_{{ date }}.docx"
    output: dropbox_link

  - id: send_email
    name: Email resume
    skill: send_email
    mcp: gmail
    depends_on: [upload_dropbox]
    input:
      to: ${{ variables.email_to }}
      subject: "Updated resume for week of {{ date }}"
      body_template: prompts/email_body.md
      body_vars:
        themes: ${{ steps.extract_themes.output }}
        dropbox_link: ${{ steps.upload_dropbox.output }}
      attachment: ${{ steps.write_resume.output }}
```

---

## Memory Architecture

OpenClaw stores all persistent data as local markdown files with vector embeddings,
eliminating the need for a separate SQLite database.

```
~/.openclaw/
├── workspace/
│   └── base_resume.docx          ← your immutable base resume
└── memory/
    ├── themes/
    │   ├── themes_2026-05-19.md   ← weekly theme snapshots (auto-indexed)
    │   ├── themes_2026-05-26.md
    │   └── ...
    └── resumes/
        └── index.md               ← log of generated resume filenames + links
```

Themes are stored as structured markdown so the agent can query them across weeks:
```markdown
---
tags: [themes, weekly]
week: 2026-05-19
postings_analyzed: 34
---

## Skills (by frequency)
- LLM product development (28/34)
- Agentic workflow design (25/34)
- RAG architecture (22/34)
...
```

---

## MCP Integrations via MCPorter

> **MCP package selection is based on a live GitHub issue tracker audit (May 2026).**
> Not all MCP packages are equal — see findings below before swapping packages.

```
MCPorter (OpenClaw MCP bridge)
├── playwright-mcp              → job board scraping (LinkedIn, Naukri, Indeed)
├── amgadabdelhafez/dbx-mcp-server  → file upload + shared link generation  ✅ recommended
├── shinzo-labs/gmail-mcp       → send email with attachment                 ✅ recommended
└── github-mcp                  → (optional) commit theme reports to repo
```

### MCP Package Audit Results

| MCP | Package | Status | Finding |
|---|---|---|---|
| Dropbox | `amgadabdelhafez/dbx-mcp-server` | ✅ Use this | Only 4 issues ever; no OAuth problems; bugs closed |
| Gmail | `GongRzhe/Gmail-MCP-Server` | ❌ Avoid | Flagged unmaintained Mar 2026; `send_email` broken from SDK; OAuth server issue open |
| Gmail | `shinzo-labs/gmail-mcp` | ✅ Use this | Actively maintained; cleaner codebase; no OAuth token refresh issues |
| Gmail (alt) | `j3k0/mcp-google-workspace` | ✅ Fallback | Covers Gmail + Calendar together; good alternative |

Each MCP is configured in `~/.openclaw/config.yaml`:

```yaml
mcp_servers:
  playwright:
    command: npx
    args: ["@playwright/mcp@latest"]

  # Dropbox: use amgadabdelhafez/dbx-mcp-server (audited May 2026 — no OAuth issues)
  dropbox:
    command: npx
    args: ["dbx-mcp-server"]
    env:
      DROPBOX_APP_KEY: ${{ secrets.DROPBOX_APP_KEY }}
      DROPBOX_APP_SECRET: ${{ secrets.DROPBOX_APP_SECRET }}
      DROPBOX_REDIRECT_URI: ${{ secrets.DROPBOX_REDIRECT_URI }}
      TOKEN_ENCRYPTION_KEY: ${{ secrets.TOKEN_ENCRYPTION_KEY }}

  # Gmail: use shinzo-labs/gmail-mcp (NOT GongRzhe/Gmail-MCP-Server — unmaintained)
  gmail:
    command: npx
    args: ["@shinzolabs/gmail-mcp"]
    env:
      GMAIL_CLIENT_ID: ${{ secrets.GMAIL_CLIENT_ID }}
      GMAIL_CLIENT_SECRET: ${{ secrets.GMAIL_CLIENT_SECRET }}
      GMAIL_REFRESH_TOKEN: ${{ secrets.GMAIL_REFRESH_TOKEN }}
```

---

## Prompt Templates

### `prompts/theme_extraction.md`
```
You are analyzing {{ n }} job descriptions for AI/PM roles in Pune.

Extract and rank themes by frequency across ALL postings in these categories:
1. Required skills & tools
2. Core responsibilities
3. Preferred qualifications
4. Emerging buzzwords (GenAI, Agentic, Copilot, etc.)

Return structured JSON: { category: [ { theme, frequency, pct_of_postings } ] }
```

### `prompts/resume_writer.md`
```
You are rewriting a Product Manager resume to match this week's job market.

BASE RESUME: (attached)
TOP THEMES THIS WEEK: {{ themes }}

Rules:
- Preserve ALL factual content (companies, titles, dates, metrics)
- Rewrite Summary to highlight the top 3 themes
- Augment Skills section with ranked keywords from themes
- Strengthen 2-3 experience bullets per role using JD language
- Do NOT invent experience or credentials
```

---

## Project Structure

```
mg-ai-job-scanner/
│
├── workflows/
│   └── weekly_job_scan.yaml      ← Lobster workflow (main entry point)
│
├── prompts/
│   ├── theme_extraction.md
│   ├── resume_writer.md
│   └── email_body.md
│
├── skills/                        ← custom AgentSkills (if needed)
│   └── naukri_scraper.py          ← Naukri.com needs custom skill (no MCP yet)
│
├── config/
│   └── openclaw.yaml              ← Gateway + MCP + model config
│
├── workspace/
│   └── base_resume.docx           ← your base resume (immutable)
│
├── DESIGN.md                      ← Anthropic SDK design
├── DESIGN_OPENCLAW.md             ← this document
├── ARCHITECTURE.md                ← visual diagrams (SDK approach)
├── ARCHITECTURE_OPENCLAW.md       ← visual diagrams (OpenClaw approach)
└── README.md
```

---

## Credentials Needed

| Secret | Used By | How to Set |
|---|---|---|
| `ANTHROPIC_API_KEY` | LLM calls (Claude) | `openclaw secrets set ANTHROPIC_API_KEY` |
| `DROPBOX_APP_KEY` | `dbx-mcp-server` | `openclaw secrets set DROPBOX_APP_KEY` |
| `DROPBOX_APP_SECRET` | `dbx-mcp-server` | `openclaw secrets set DROPBOX_APP_SECRET` |
| `DROPBOX_REDIRECT_URI` | `dbx-mcp-server` | `openclaw secrets set DROPBOX_REDIRECT_URI` |
| `TOKEN_ENCRYPTION_KEY` | `dbx-mcp-server` | `openclaw secrets set TOKEN_ENCRYPTION_KEY` |
| `GMAIL_CLIENT_ID` | `@shinzolabs/gmail-mcp` | `openclaw secrets set GMAIL_CLIENT_ID` |
| `GMAIL_CLIENT_SECRET` | `@shinzolabs/gmail-mcp` | `openclaw secrets set GMAIL_CLIENT_SECRET` |
| `GMAIL_REFRESH_TOKEN` | `@shinzolabs/gmail-mcp` | `openclaw secrets set GMAIL_REFRESH_TOKEN` |

> All secrets are stored locally in OpenClaw's encrypted secret store —
> never committed to git or sent to a cloud service.

---

## Comparison: SDK vs OpenClaw

| Capability | Anthropic SDK | OpenClaw |
|---|---|---|
| Lines of Python code | ~600 | ~50 (YAML) |
| External scheduler | GitHub Actions | Built-in Proactive Engine |
| Tool integrations | Manual SDK clients | MCPorter one-liners |
| Observability | Custom logging | Built-in Gateway session logs |
| LLM flexibility | Claude only | Claude, Gemini, Ollama, any OpenAI-compatible |
| Local/private | No | Yes — fully local option |
| Setup complexity | Medium | Low (`npm install openclaw`) |
| Customization | Full | Constrained to OpenClaw model |
