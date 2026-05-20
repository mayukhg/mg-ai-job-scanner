# Hybrid System Design — Option 3 (GHA + Python Engine)

## Overview

The **Hybrid Architecture** is designed to provide 100% reliable, zero-maintenance weekly execution in the cloud while retaining the modularity and protocol-driven simplicity of advanced agent frameworks, completely negating the critical drawbacks of both Custom Python (Option 1) and local-first OpenClaw (Option 2).

```
┌─────────────────────────────────────────────────────────────────┐
│              Weekly GitHub Actions Cron (Monday 8AM)            │
│                 (100% Uptime Cloud Runner)                      │
└─────────────────────────┬───────────────────────────────────────┘
                          │
          ┌───────────────▼───────────────┐
          │     Modular Python Engine     │
          │   (Config-driven main.py)     │
          └───────────────┬───────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌───────▼──────┐  ┌───────▼──────┐  ┌──────▼───────┐
│ Apify Scraper│  │  LLM Router  │  │ python-docx  │
│  (Managed)   │  │(Claude/Gemini│  │ (In-place)   │
└───────┬──────┘  └───────┬──────┘  └──────┬───────┘
        │                 │                │
┌───────▼──────┐  ┌───────▼──────┐  ┌──────▼───────┐
│ Raw JDs JSON │  │ SQLite DB /  │  │ Polished     │
│  (Artifact)  │  │ Theme JSON   │  │ Resume.docx  │
└──────────────┘  └──────────────┘  └──────┬───────┘
                                           │
                              ┌────────────┼────────────┐
                              │                         │
                     ┌────────▼───────┐      ┌─────────▼──────┐
                     │ Dropbox Upload │      │  Email Sender  │
                     │  (Auto-Refresh)│      │  (Gmail SMTP)  │
                     └────────────────┘      └────────────────┘
```

---

## How It Negates the Cons of Existing Options

| Con of Option 1 (Custom Python SDK) | Con of Option 2 (OpenClaw local-first) | **Negated by Option 3 (Hybrid)** |
|---|---|---|
| **Boilerplate Overload**: Hundreds of lines of glue-code for integrations, MIMEs, and custom clients. | **Uptime & Cron Vulnerability**: Local proactive cron fails if the personal machine is off/sleep at 8 AM. | **GitHub Actions Cloud Run**: 100% serverless cloud uptime. Highly modular python sub-packages replace boilerplate with single-responsibility imports. |
| **Model Lock-In**: Deep dependency on Anthropic SDK specifically. | **Scraping Anti-Bot Blocks**: Headless Playwright is blocked instantly by advanced boards like Naukri.com. | **Apify Scraping + LLM Router**: Offloads scraping to managed anti-bot services, and uses a model-agnostic wrapper (LiteLLM or direct config) to swap LLMs instantly. |
| **Silent Credential Expiration**: Refresh token persistence can break silently in serverless. | **Resume XML / Style Corruption**: General text-generation/Markdown conversion breaks document fonts and layouts. | **XML Bullet In-Place Edit + Auto-Refresh**: Edits the XML runs *directly* inside the `.docx` (preserving original layout) and auto-refreshes OAuth keys on each GHA run. |
| **Complex Local Dev**: Heavy mocking required to run the pipeline. | **MCP Server Fragility**: Community MCP packages suffer from unmaintained repos and OAuth bugs. | **Local Execution / Mock Run**: Run the engine locally by swapping APIs with local mocks, bypassing MCP bugs altogether. |

---

## Component Specifications

### 1. Ingestion Layer (Apify Scraper Integration)
* **Strategy**: Use an HTTP client calling a managed Apify Actor (specifically optimized for LinkedIn India and Naukri.com).
* **Bypass Mechanics**: Apify handles residential proxy rotation, request headers, dynamic DOM parsing, and bypasses Cloudflare walls.
* **Fallback**: Standard Python beautifulsoup scraper for static XML feeds, completely isolated in `src/scraper/`.

### 2. Multi-Model Router (LiteLLM / Lightweight Wrapper)
* **Strategy**: Standardized interface supporting both Anthropic (Claude 3.5 Sonnet) and Google Gemini (2.0 Pro) using simple environment variable flags:
```python
# config.py
LLM_PROVIDER = "gemini"  # or "anthropic"
MODEL_NAME = "gemini-2.0-pro-exp"  # or "claude-3-5-sonnet"
```
* Allows you to use Gemini's huge context window for digesting dozens of raw job descriptions cheaply, while retaining the option to use Claude's writing style for the final resume update.

### 3. XML In-Place Resume Editor (`python-docx` Engine)
* **Strategy**: The rewriter **never** generates a `.docx` file from scratch.
* **Mechanism**:
  1. Parse `base_resume.docx` into paragraph and table cell nodes.
  2. Map paragraph elements matching career experience bullets.
  3. Send specific text strings to the LLM: *"Enhance this resume bullet point to reflect these weekly themes, but keep all metrics and factual dates identical."*
  4. Inject the LLM's returned plain text back into the **exact same run nodes**, preserving the original document's fonts, colors, margins, and page layouts.

### 4. Resilient Delivery Layer (Auto-Refresh OAuth Manager)
* **Strategy**: Native Python packages for Dropbox and Google APIs, wrapped in an auto-refreshing authentication utility class.
* **Mechanism**:
  1. Store the long-lived client IDs and `REFRESH_TOKEN`s in **GitHub Repository Secrets**.
  2. At the start of the GitHub Actions run, the Python script sends an OAuth token-refresh request.
  3. The API client obtains a fresh, short-lived `access_token` valid for 3600 seconds.
  4. Executed completely headlessly without the risk of community MCP version crashes.

---

## Tech Stack

| Layer | Selection | Advantage |
|---|---|---|
| **Runtime & Runner** | GitHub Actions (Ubuntu VM) | 100% free cloud scheduling, zero local infra maintenance. |
| **Language** | Python 3.11+ | The premier ecosystem for natural language parsing and docx editing. |
| **Scraper** | Apify Python SDK / HTTP Client | Eliminates anti-bot IP blocks and selector updates on Indian boards. |
| **Docx Editor** | `python-docx` (XML run mapping) | Bullet-by-bullet replacement, ensuring styling is completely unbroken. |
| **Model Router** | LiteLLM or Direct API Wrappers | Swap between Google Gemini and Anthropic Claude via a single `.env` line. |
| **Data Storage** | SQLite + JSON Weekly Snapshots | Portable DB easily uploaded to Dropbox and saved as GHA artifacts. |

---

## Operational Folder Structure

The Hybrid design implements a clean, modular structure where scripts, prompts, databases, and environments are clearly separated:

```
mg-ai-job-scanner/
│
├── .github/workflows/
│   └── weekly_scan.yml          ← GHA Cron runner (Monday 8AM IST, handles secrets)
│
├── config/
│   └── settings.yaml            ← Target locations, titles, and model selections
│
├── src/
│   ├── main.py                  ← Central orchestrator entry point
│   ├── scraper/
│   │   ├── __init__.py
│   │   └── apify_client.py      ← Managed scraper interface (LinkedIn/Naukri)
│   ├── analyzer/
│   │   ├── __init__.py
│   │   └── extraction.py        ← Structured weekly theme aggregator
│   ├── resume/
│   │   ├── __init__.py
│   │   └── inplace_editor.py    ← python-docx text node injector
│   └── delivery/
│       ├── __init__.py
│       ├── oauth_helper.py      ← Secure OAuth2 refresh token exchanger
│       ├── dropbox_helper.py    ← Dropbox upload manager
│       └── email_helper.py      ← Gmail SMTP MIME client
│
├── data/
│   ├── base_resume/             ← Your immutable base template (Resume_Base.docx)
│   └── store/                   ← Local SQLite / weekly cache (ignored in Git)
│
├── DESIGN_HYBRID.md             ← This document
├── ARCHITECTURE_HYBRID.md       ← Diagrams for Hybrid flow
└── requirements.txt
```

---

## Secret Configuration (GitHub Secrets Setup)

All secure keys are stored in your GitHub Repository under **Settings > Secrets and Variables > Actions**:

| Secret Key | Source Platform | Purpose |
|---|---|---|
| `APIFY_API_KEY` | Apify Console | Bypassing bot blocks on LinkedIn & Naukri |
| `GEMINI_API_KEY` / `ANTHROPIC_API_KEY` | Google AI Studio / Console | Orchestrating resume refinement and theme extraction |
| `DROPBOX_REFRESH_TOKEN` | Dropbox App Console | Headless upload of generated resumes |
| `DROPBOX_APP_KEY` / `DROPBOX_APP_SECRET` | Dropbox App Console | Auto-refreshing Dropbox credentials |
| `GMAIL_REFRESH_TOKEN` | Google Developer Console | Headless SMTP delivery to your inbox |
| `GMAIL_CLIENT_ID` / `GMAIL_CLIENT_SECRET` | Google Developer Console | Auto-refreshing Gmail credentials |
