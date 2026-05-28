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
            M_SCRAPE[scraper/watchdog.py]
            M_A2A[analyzer/a2a_messaging.py]
            M_RES[resume/inplace_editor.py]
            M_TUTOR[tutor/agent_tutor.py]
            M_INTER[interviewer/mock_interviewer.py]
            M_PORT[portfolio/portfolio_architect.py]
        end
        
        ORCH --> M_SCRAPE & M_A2A & M_RES & M_TUTOR & M_INTER & M_PORT
    end

    subgraph SERVICES["External Managed APIs"]
        APIFY[Apify Console\nLinkedIn & Naukri Actors]
        LLM[Claude 3.5 Sonnet /\nGemini 2.0 Pro]
        DROPBOX[Dropbox API\n/Resumes/Weekly/]
        GMAIL[Gmail SMTP Service\nHeader / Attachment]
    end

    M_SCRAPE --> APIFY
    M_A2A --> LLM
    M_RES --> LLM
    M_TUTOR --> LLM

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

## 4. Sequence Flow (Reactive Event Bus Cascade)

```mermaid
sequenceDiagram
    participant GHA as ☁️ GitHub Actions Cron
    participant PY as 🐍 main.py Orchestrator
    participant EB as 🎛️ AgentEventBus
    participant ATN as 🤖 Tuner Agent
    participant AMC as 🤖 Mock Interviewer Agent
    participant ATT as 🤖 Tutor Agent
    participant APA as 🤖 Portfolio Agent

    GHA->>PY: Execute (Monday 8AM IST)
    PY->>PY: Git-as-a-Database: Seed local SQLite from state_history.json
    PY->>EB: Instantiate AgentEventBus
    PY->>EB: Register Tuner, Watchdog, Tutor, Interviewer, Portfolio agents
    PY->>EB: Subscribe agents to target routing keys
    
    PY->>ATN: tune_resume() [Initial Trigger]
    Note over ATN: Tunes resume & commits trend keys to SQLite
    
    ATN->>EB: send_message("agent_mock_interviewer", "RESUME_TUNED_FOR_TARGET", payload)
    EB->>AMC: on_message(RESUME_TUNED_FOR_TARGET)
    
    Note over AMC: Simulates system-design interview session<br/>Scorecard readiness rating < 9.0/10.0
    AMC->>EB: send_message("agent_tutor", "UPSKILLING_REQUIRED", payload)
    EB->>ATT: on_message(UPSKILLING_REQUIRED)

    Note over ATT: Crawls arXiv papers & technical specs<br/>Compiles anchored NotebookLM brief
    ATT->>EB: send_message("agent_portfolio_architect", "UPSKILLING_BRIEF_COMPILED", payload)
    EB->>APA: on_message(UPSKILLING_BRIEF_COMPILED)

    Note over APA: Scaffolds complete Pytest TDD project workspace
    
    PY->>PY: Observability: Compile gha_run_summary.md
    PY->>PY: Git-as-a-Database: Serialize & commit state_history.json to state-store branch
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
