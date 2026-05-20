# Visual Architecture — Option 3 Hybrid Design

## 1. High-Level Flow (Serverless Cloud Cron)

```mermaid
flowchart TD
    CRON([🕗 GitHub Actions Cron\nEvery Monday 8AM IST]):::trigger

    CRON --> GHA

    subgraph GHA["☁️ GitHub Actions Runner (Ubuntu VM)"]
        direction TB
        ORCH[main.py Orchestrator]
        
        subgraph MODULES["Modular Python Modules (src/)"]
            M_SCRAPE[scraper/apify_client.py]
            M_ANAL[analyzer/extraction.py]
            M_RES[resume/inplace_editor.py]
            M_DEL[delivery/oauth_helper.py]
        end
        
        ORCH --> M_SCRAPE & M_ANAL & M_RES & M_DEL
    end

    subgraph SERVICES["External Managed APIs"]
        APIFY[Apify Console\nLinkedIn & Naukri Actors]
        LLM[Claude 3.5 Sonnet /\nGemini 2.0 Pro]
        DROPBOX[Dropbox API\n/Resumes/Weekly/]
        GMAIL[Gmail SMTP Service\nHeader / Attachment]
    end

    M_SCRAPE --> APIFY
    M_ANAL --> LLM
    M_RES --> LLM
    M_DEL --> |Auto-Refresh OAuth| DROPBOX
    M_DEL --> |Auto-Refresh OAuth| GMAIL

    classDef trigger fill:#f5a623,color:#000,font-weight:bold
```

---

## 2. Ingestion & Scraping Pipeline

```mermaid
flowchart LR
    subgraph GHA["GitHub Actions"]
        ORCH[Python Orchestrator]
        JSON[("📁 raw_postings.json\n(Temp Cache)")]
    end

    subgraph APIFY["Apify Platform"]
        ACTOR[LinkedIn & Naukri Scraper Actor]
        PROXY[Residential Proxy Pool]
        CAPTCHA[Anti-CAPTCHA Solvers]
        
        ACTOR --> PROXY & CAPTCHA
    end

    ORCH -->|1 · Call API w/ APIFY_API_KEY| ACTOR
    ACTOR -->|2 · Dynamic Extraction| BOARDS[LinkedIn & Naukri India]
    BOARDS -->|3 · Clean JDs| ACTOR
    ACTOR -->|4 · JSON Response| ORCH
    ORCH -->|5 · Cache JDs| JSON
```

---

## 3. In-Place Resume Edit Pipeline

```mermaid
flowchart TD
    BASE[/📄 base_resume.docx\n(Dropbox Immutable Base)/]
    THEMES["📊 Top Weekly Themes\n(SQLite Summary)"]

    BASE --> EDIT[python-docx Parser]
    THEMES --> EDIT

    subgraph EDIT["python-docx Node Editing Engine"]
        direction TB
        P1[Read Paragraph Bullet Runs]
        MAP[Filter Experience & Summary Paragraphs]
        LLM["🤖 Call LLM Router\n(Gemini 2.0 / Claude 3.5)"]
        INJECT[Inject Polished Text directly into XML node runs]
        
        P1 --> MAP --> LLM --> INJECT
    end

    EDIT --> NEW[/"✅ Resume_WeekOf_DATE.docx\n(Preserves layout, colors, and fonts)"/]
```

---

## 4. Sequence Flow

```mermaid
sequenceDiagram
    participant GHA as ☁️ GitHub Actions Cron
    participant PY as 🐍 main.py Orchestrator
    participant AP as 🕷 Apify API
    participant LL as 🧠 LLM Router (Claude/Gemini)
    participant OATH as 🔑 OAuth Helper (Refresh Token)
    participant DB as ☁️ Dropbox SDK
    participant GM as 📧 Gmail SMTP

    GHA->>PY: Execute (Monday 8AM IST)
    
    PY->>AP: run_actor(pune_jobs_scraper)
    AP-->>PY: raw_job_descriptions[]

    PY->>LL: analyze_and_extract_themes(raw_descriptions)
    LL-->>PY: structured_theme_map{skills, responsibilities}

    PY->>OATH: refresh_access_tokens(secrets)
    OATH-->>PY: Dropbox & Gmail fresh_access_tokens

    PY->>DB: download(themes.db)
    DB-->>PY: themes.db (local SQLite cache)

    PY->>DB: download(base_resume.docx)
    DB-->>PY: base_resume.docx (binary)

    PY->>LL: rewrite_docx_paragraphs(base_resume, theme_map)
    LL-->>PY: updated_docx_binary

    PY->>DB: upload(Resume_WeekOf_DATE.docx, fresh_token)
    DB-->>PY: shared_link

    PY->>DB: upload(updated themes.db, fresh_token)
    DB-->>PY: upload completed ✓

    PY->>GM: send_smtp_email(to, subject, body_summary, attachment, fresh_token)
    GM-->>PY: email sent successfully
```

---

## 5. Unified Credentials & Secrets Layout

```mermaid
flowchart TB
    subgraph GHA_SECRETS["GitHub Repository Secrets (Encrypted)"]
        API_KEYS["APIFY_API_KEY\nGEMINI_API_KEY\nANTHROPIC_API_KEY"]
        DBX_SECRETS["DROPBOX_REFRESH_TOKEN\nDROPBOX_APP_KEY\nDROPBOX_APP_SECRET"]
        GML_SECRETS["GMAIL_REFRESH_TOKEN\nGMAIL_CLIENT_ID\nGMAIL_CLIENT_SECRET"]
    end

    subgraph INJECT["Script Injection (.env / environment)"]
        PY[Python Engine Client]
    end

    API_KEYS -->|Direct Access| PY
    DBX_SECRETS -->|OAuth2 Refresh Loop| PY
    GML_SECRETS -->|OAuth2 Refresh Loop| PY

    PY -->|Bypass Bot Blocks| APIFY[Apify Scrapers]
    PY -->|Cost-effective LLM calls| GOOGLE[Gemini API]
    PY -->|Secure File Uploads| DROPBOX[Dropbox Storage]
    PY -->|Headless SMTP Emails| GMAIL[Gmail Servers]
```
