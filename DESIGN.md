# mg-ai-job-scanner — System Design

## Overview

A weekly automated AI agent that scans job postings for AI/Product Management roles in Pune,
extracts common themes, rewrites a base resume to match, saves it to Dropbox, and emails it.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Weekly Cron Trigger (Monday 8AM)             │
└─────────────────────────┬───────────────────────────────────────┘
                          │
          ┌───────────────▼───────────────┐
          │      Orchestrator Agent        │
          │   (Claude claude-sonnet-4-6)   │
          └───────────────┬───────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌───────▼──────┐  ┌───────▼──────┐  ┌──────▼───────┐
│  Job Scraper │  │Theme Analyzer│  │Resume Writer │
│    Module    │  │   Module     │  │   Module     │
└───────┬──────┘  └───────┬──────┘  └──────┬───────┘
        │                 │                │
┌───────▼──────┐  ┌───────▼──────┐  ┌──────▼───────┐
│  Raw Postings│  │ Theme DB     │  │ Final Resume │
│  (JSON store)│  │ (SQLite/JSON)│  │  (.docx)     │
└──────────────┘  └──────────────┘  └──────┬───────┘
                                           │
                              ┌────────────┼────────────┐
                              │                         │
                     ┌────────▼───────┐      ┌─────────▼──────┐
                     │ Dropbox Upload │      │  Email Sender  │
                     │    Module      │      │   (Gmail API)  │
                     └────────────────┘      └────────────────┘
```

---

## Components

### 1. Job Scraper Module

**Sources (in priority order):**
- LinkedIn Jobs API / LinkedIn scraper
- Indeed API
- Naukri.com (major Indian job board, critical for Pune postings)
- Glassdoor
- Instahyre / iimjobs (India-specific)

**Search Parameters:**
```json
{
  "location": "Pune, India",
  "titles": [
    "AI Product Manager",
    "Agentic AI Product Manager",
    "Director of Product Management",
    "Senior Director of Product Management",
    "VP of Product Management",
    "Vice President of Product"
  ],
  "date_posted": "last_7_days",
  "deduplicate": true
}
```

**Output:** Raw JSON store of postings — title, company, JD full text, source URL, date scraped.

---

### 2. Theme Analyzer Module (Claude-powered)

**Process:**
1. Ingest all raw JDs for the week
2. Extract structured signals per posting:
   - Required skills & tools
   - Responsibilities
   - Preferred qualifications
   - Keywords/buzzwords
   - Years of experience
   - Domain focus (GenAI, LLM, Agentic, Platform, etc.)
3. Aggregate across all postings → frequency-weighted theme map
4. Persist to theme database (weekly snapshot)

**Theme Database Schema:**
```
themes_weekly
├── week_of         (date)
├── theme_category  (skills | responsibilities | qualifications | tools)
├── theme_text      (e.g., "LLM product development")
├── frequency       (count across postings)
├── sample_sources  (list of JD URLs)
└── raw_postings_count
```

---

### 3. Resume Writer Module (Claude-powered)

**Inputs:**
- `base_resume.docx` — canonical resume (stored in Dropbox or local)
- Weekly theme map from Theme Analyzer
- Previous week's resume (for diff/continuity)

**Process:**
1. Load base resume structure
2. For each section (Summary, Skills, Experience bullets), Claude rewrites/augments using top themes
3. Preserves all factual content — only enhances language and adds relevant keywords
4. Produces `resume_YYYY-MM-DD.docx`

**Naming Convention:**
```
Resume_Mayukh_Ghosh_PM_WeekOf_YYYY-MM-DD.docx
```

---

### 4. Dropbox Integration

- Auth via Dropbox OAuth2 / App token
- Target folder: `/Resumes/Weekly/`
- Uploads the `.docx` resume file
- Also saves weekly theme JSON: `/Themes/themes_YYYY-MM-DD.json`

---

### 5. Email Module

- Auth via Gmail API (OAuth2) or SMTP
- **To:** mayukhg@gmail.com
- **Subject:** `Updated resume for week of YYYY-MM-DD`
- **Body:** Summary of top 10 themes found this week
- **Attachment:** The newly created `.docx` resume

---

## Tech Stack

| Layer | Choice | Reason |
|---|---|---|
| Orchestration | Claude claude-sonnet-4-6 (Agents SDK) | Native tool use, multi-step reasoning |
| Scheduling | Cron (GitHub Actions / Cloud Scheduler) | Simple weekly trigger |
| Job Scraping | `apify` scrapers or `serpapi` | Managed, handles anti-bot |
| Theme DB | SQLite + JSON flat files | Portable, no infra needed |
| Resume Generation | `python-docx` + Claude | Programmatic Word editing |
| Dropbox | Dropbox Python SDK | Official SDK |
| Email | Gmail API + `google-auth` | Reliable, attachment support |
| Language | Python 3.11+ | Best ecosystem for all above |

---

## Agent Flow

```
every Monday at 8:00 AM:
  week_date = today()

  # Step 1: Scrape
  postings = scrape_jobs(titles, location="Pune", since=7_days_ago)
  save_raw(postings, week_date)

  # Step 2: Analyze
  themes = analyze_themes(postings)   # Claude call
  save_themes(themes, week_date)

  # Step 3: Write resume
  base_resume = load_from_dropbox("base_resume.docx")
  new_resume = rewrite_resume(base_resume, themes)  # Claude call
  filename = f"Resume_Mayukh_Ghosh_PM_WeekOf_{week_date}.docx"

  # Step 4: Upload
  upload_to_dropbox(new_resume, f"/Resumes/Weekly/{filename}")
  dropbox_link = get_shared_link(filename)

  # Step 5: Email
  send_email(
    to="mayukhg@gmail.com",
    subject=f"Updated resume for week of {week_date}",
    body=format_theme_summary(themes),
    attachment=new_resume
  )
```

---

## Key Design Decisions

| Decision | Rationale |
|---|---|
| **Claude for theme extraction AND resume writing** | Single model handles both NLP analysis and professional writing, consistent voice |
| **Base resume stays immutable** | Each week generates a new file; the original is never overwritten |
| **Theme DB persists week-over-week** | Enables trend analysis — track which themes are growing over time |
| **Dropbox as primary store** | Cross-device access, versioned history, easy sharing |
| **Email with attachment** | No extra login needed — resume is immediately actionable |

---

## Project Structure (Planned)

```
mg-ai-job-scanner/
├── DESIGN.md                  # This document
├── README.md
├── requirements.txt
├── .env.example               # Template for secrets
├── .github/
│   └── workflows/
│       └── weekly_scan.yml    # GitHub Actions cron trigger
├── src/
│   ├── main.py                # Orchestrator entry point
│   ├── scraper/
│   │   ├── __init__.py
│   │   ├── linkedin.py
│   │   ├── naukri.py
│   │   └── indeed.py
│   ├── analyzer/
│   │   ├── __init__.py
│   │   └── theme_extractor.py
│   ├── resume/
│   │   ├── __init__.py
│   │   └── writer.py
│   ├── integrations/
│   │   ├── __init__.py
│   │   ├── dropbox_client.py
│   │   └── email_client.py
│   └── db/
│       ├── __init__.py
│       └── theme_store.py
└── data/
    ├── base_resume/           # Base resume template
    ├── raw_postings/          # Weekly raw JD JSON files
    └── themes/                # Weekly theme snapshots
```

---

## Prerequisites / Credentials Needed

| Service | Credential | Purpose |
|---|---|---|
| Anthropic | `ANTHROPIC_API_KEY` | Claude API for theme analysis and resume writing |
| Apify / SerpAPI | `SCRAPER_API_KEY` | Job board scraping |
| Dropbox | `DROPBOX_APP_KEY`, `DROPBOX_APP_SECRET`, `DROPBOX_REFRESH_TOKEN` | File storage |
| Gmail | `GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET`, `GMAIL_REFRESH_TOKEN` | Sending email with attachment |
