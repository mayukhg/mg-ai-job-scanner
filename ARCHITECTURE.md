# Architecture — Visual Design

## 1. High-Level System Flow

```mermaid
flowchart TD
    CRON([🕗 Weekly Cron\nEvery Monday 8AM]):::trigger

    CRON --> ORCH

    subgraph ORCH["🤖 Orchestrator Agent (Claude Sonnet)"]
        direction LR
        S1[1 · Scrape] --> S2[2 · Analyze] --> S3[3 · Write] --> S4[4 · Store] --> S5[5 · Notify]
    end

    subgraph SCRAPE["Job Scraper Module"]
        LI[LinkedIn]
        NA[Naukri.com]
        IN[Indeed]
        GL[Glassdoor]
    end

    subgraph ANALYZE["Theme Analyzer Module"]
        EX[Claude\nTheme Extraction]
        DB[(Theme DB\nSQLite)]
    end

    subgraph RESUME["Resume Writer Module"]
        BR[/base_resume.docx/]
        RW[Claude\nResume Rewrite]
        OUT[/Resume_WeekOf_DATE.docx/]
    end

    subgraph DELIVER["Delivery"]
        DP[Dropbox\n/Resumes/Weekly/]
        EM[Gmail\nw/ Attachment]
    end

    S1 --> SCRAPE
    SCRAPE --> S2
    S2 --> ANALYZE
    ANALYZE --> S3
    BR --> S3
    S3 --> RESUME
    RESUME --> S4
    S4 --> DP
    S4 --> S5
    S5 --> EM

    classDef trigger fill:#f5a623,color:#000,font-weight:bold
    classDef module fill:#4a90d9,color:#fff
    classDef store fill:#7ed321,color:#000
```

---

## 2. Job Scraper — Search Parameters

```mermaid
flowchart LR
    subgraph TITLES["Target Job Titles"]
        T1[AI Product Manager]
        T2[Agentic AI Product Manager]
        T3[Director of Product Management]
        T4[Senior Director of Product Management]
        T5[VP of Product Management]
    end

    subgraph SOURCES["Job Boards"]
        S1[🔵 LinkedIn]
        S2[🟠 Naukri.com]
        S3[🔴 Indeed]
        S4[🟢 Glassdoor]
    end

    LOC["📍 Location: Pune, India\n🗓 Posted: Last 7 Days"]

    TITLES --> QUERY
    LOC --> QUERY
    QUERY[Search Query Builder] --> SOURCES
    SOURCES --> DEDUP[Deduplication\nby JD fingerprint]
    DEDUP --> RAW[("📁 Raw Postings\nJSON Store")]
```

---

## 3. Theme Extraction Pipeline

```mermaid
flowchart TD
    RAW[("📁 Raw JDs\nN postings this week")]

    RAW --> CLAUDE["🤖 Claude\nTheme Extraction Prompt"]

    CLAUDE --> E1["Skills & Tools\n(LLM, RAG, Agents, Python...)"]
    CLAUDE --> E2["Responsibilities\n(roadmap, GTM, stakeholders...)"]
    CLAUDE --> E3["Qualifications\n(years exp, domain, MBA...)"]
    CLAUDE --> E4["Buzzwords\n(GenAI, Agentic, Copilot...)"]

    E1 & E2 & E3 & E4 --> AGG["Frequency Aggregator\n(count across all JDs)"]

    AGG --> RANK["Ranked Theme Map\n(top N per category)"]

    RANK --> DB[("🗄 Theme DB\nweekly snapshot")]
    RANK --> JSON[("📄 themes_YYYY-MM-DD.json\n→ Dropbox /Themes/")]
```

---

## 4. Resume Generation

```mermaid
flowchart LR
    BASE[/📄 base_resume.docx\nimmutable source/]
    THEMES["📊 Top Themes\nthis week"]

    BASE --> CLAUDE
    THEMES --> CLAUDE

    subgraph CLAUDE["🤖 Claude — Resume Writer"]
        direction TB
        P1["Rewrite Summary\nto highlight GenAI / Agentic"]
        P2["Enhance Skills section\nwith ranked keywords"]
        P3["Strengthen Experience bullets\nusing JD language"]
    end

    CLAUDE --> NEW[/"✅ Resume_Mayukh_Ghosh_PM\n_WeekOf_YYYY-MM-DD.docx"/]

    NEW --> DB["📁 Dropbox\n/Resumes/Weekly/"]
    NEW --> EMAIL["📧 Gmail\nw/ attachment"]
```

---

## 5. Weekly Execution Sequence

```mermaid
sequenceDiagram
    participant CRON as 🕗 Cron
    participant ORCH as 🤖 Orchestrator
    participant SCRAPER as 🕷 Scraper
    participant CLAUDE as 🧠 Claude API
    participant DROPBOX as ☁️ Dropbox
    participant GMAIL as 📧 Gmail

    CRON->>ORCH: trigger(week_date)

    ORCH->>SCRAPER: scrape_jobs(titles, Pune, last_7_days)
    SCRAPER-->>ORCH: raw_postings[]

    ORCH->>CLAUDE: extract_themes(raw_postings)
    CLAUDE-->>ORCH: theme_map{category: [{text, frequency}]}

    ORCH->>DROPBOX: get_file(base_resume.docx)
    DROPBOX-->>ORCH: base_resume

    ORCH->>CLAUDE: rewrite_resume(base_resume, theme_map)
    CLAUDE-->>ORCH: updated_resume.docx

    ORCH->>DROPBOX: upload(Resume_WeekOf_YYYY-MM-DD.docx)
    DROPBOX-->>ORCH: shared_link

    ORCH->>GMAIL: send_email(subject, theme_summary, attachment)
    GMAIL-->>ORCH: sent ✓
```

---

## 6. Data Model

```mermaid
erDiagram
    WEEKLY_RUN {
        string week_date PK
        int postings_scraped
        int themes_extracted
        string resume_filename
        string dropbox_link
        string email_sent_at
    }

    RAW_POSTING {
        string id PK
        string week_date FK
        string title
        string company
        string source
        string url
        text   jd_text
        string scraped_at
    }

    THEME {
        string id PK
        string week_date FK
        string category
        string theme_text
        int    frequency
        float  pct_of_postings
    }

    WEEKLY_RUN ||--o{ RAW_POSTING : "contains"
    WEEKLY_RUN ||--o{ THEME : "produces"
```

---

## 7. Folder Structure

```
mg-ai-job-scanner/
│
├── .github/workflows/
│   └── weekly_scan.yml          ← Cron trigger (Monday 8AM IST)
│
├── src/
│   ├── main.py                  ← Orchestrator entry point
│   ├── scraper/
│   │   ├── linkedin.py
│   │   ├── naukri.py
│   │   └── indeed.py
│   ├── analyzer/
│   │   └── theme_extractor.py   ← Claude theme extraction
│   ├── resume/
│   │   └── writer.py            ← Claude resume rewriter
│   └── integrations/
│       ├── dropbox_client.py
│       └── email_client.py
│
├── data/
│   ├── base_resume/             ← Your immutable base resume
│   ├── raw_postings/            ← Weekly JD JSON dumps
│   └── themes/                  ← Weekly theme snapshots
│
├── DESIGN.md
├── ARCHITECTURE.md              ← This file
├── README.md
└── requirements.txt
```

---

## 8. Credentials & Environment Variables

```mermaid
flowchart LR
    subgraph ENV[".env / GitHub Secrets"]
        A[ANTHROPIC_API_KEY]
        B[SCRAPER_API_KEY\nApify or SerpAPI]
        C[DROPBOX_APP_KEY\nDROPBOX_APP_SECRET\nDROPBOX_REFRESH_TOKEN]
        D[GMAIL_CLIENT_ID\nGMAIL_CLIENT_SECRET\nGMAIL_REFRESH_TOKEN]
    end

    A --> CLAUDE_API[Claude API]
    B --> JOB_BOARDS[Job Boards]
    C --> DROPBOX[Dropbox]
    D --> GMAIL[Gmail]
```
