# Architecture — OpenClaw Visual Design

## 1. OpenClaw Runtime Overview

```mermaid
flowchart TD
    CRON([🕗 Proactive Engine\nEvery Monday 8AM IST]):::trigger

    CRON --> GW

    subgraph GW["🦞 OpenClaw Gateway (Control Plane)"]
        direction LR
        ROUTER[Message Router]
        SESSION[Session Manager]
        TASKFLOW[TaskFlow Engine]
        ROUTER <--> SESSION
        SESSION <--> TASKFLOW
    end

    subgraph LOBSTER["Lobster Workflow: weekly_job_scan.yaml"]
        S1[Step 1\nscrape_jobs]
        S2[Step 2\nextract_themes]
        S3[Step 3\nsave_themes]
        S4[Step 4\nwrite_resume]
        S5[Step 5\nupload_dropbox]
        S6[Step 6\nsend_email]
        S1 --> S2 --> S3
        S2 --> S4 --> S5 --> S6
    end

    subgraph MCPORTER["MCPorter (MCP Bridge)"]
        MCP1[playwright-mcp\nJob Scraping]
        MCP2[dropbox-mcp\nFile Storage]
        MCP3[gmail-mcp\nEmail Delivery]
    end

    subgraph MEMORY["Memory Store\n~/.openclaw/memory/"]
        M1[themes/\nweekly snapshots .md]
        M2[resumes/\nindex.md]
    end

    subgraph LLM["LLM Layer"]
        C1[Claude claude-sonnet-4-6\nTheme Extraction]
        C2[Claude claude-sonnet-4-6\nResume Writing]
    end

    TASKFLOW --> LOBSTER
    S1 --> MCP1
    S3 --> MEMORY
    S2 --> C1
    S4 --> C2
    S5 --> MCP2
    S6 --> MCP3

    classDef trigger fill:#f5a623,color:#000,font-weight:bold
```

---

## 2. Lobster Workflow — Step-by-Step

```mermaid
flowchart LR
    START([Monday\n8AM]):::trigger

    START --> A

    A["🕷 scrape_jobs\nskill: web_scraper\nmcp: playwright\n\nLinkedIn · Naukri\nIndeed · Glassdoor\nPune · last 7 days"]:::step

    A --> B["🧠 extract_themes\nskill: llm_analyze\nmodel: claude-sonnet-4-6\n\nSkills · Responsibilities\nQualifications · Keywords"]:::step

    B --> C["💾 save_themes\nskill: memory_write\n\nthemes/themes_DATE.md\nvector-indexed"]:::step

    B --> D["✍️ write_resume\nskill: llm_generate\nmodel: claude-sonnet-4-6\n\nbase_resume + themes\n→ Resume_WeekOf_DATE.docx"]:::step

    D --> E["☁️ upload_dropbox\nmcp: dropbox-mcp\n\n/Resumes/Weekly/\nResume_WeekOf_DATE.docx"]:::step

    E --> F["📧 send_email\nmcp: gmail-mcp\n\nSubject: Updated resume\nfor week of DATE\n+ attachment"]:::step

    classDef trigger fill:#f5a623,color:#000,font-weight:bold
    classDef step fill:#4a90d9,color:#fff,text-align:left
```

---

## 3. MCPorter Integration Map

```mermaid
flowchart TB
    subgraph MCPORTER["MCPorter — OpenClaw MCP Bridge"]
        direction TB

        subgraph SCRAPE["Scraping"]
            PW["playwright-mcp\nnpx @playwright/mcp"]
        end

        subgraph STORE["Storage"]
            DB["dropbox-mcp\nnpx dropbox-mcp"]
        end

        subgraph COMM["Communication"]
            GM["gmail-mcp\nnpx gmail-mcp"]
        end
    end

    PW --> LI[LinkedIn]
    PW --> NA[Naukri.com]
    PW --> IN[Indeed]
    PW --> GL[Glassdoor]

    DB --> DPX["☁️ Dropbox\n/Resumes/Weekly/"]

    GM --> EMAIL["📧 mayukhg@gmail.com"]
```

---

## 4. Memory Architecture

```mermaid
flowchart LR
    subgraph LOCAL["~/.openclaw/"]
        subgraph WS["workspace/"]
            BASE[/base_resume.docx\nimmutable source/]
        end

        subgraph MEM["memory/"]
            subgraph TH["themes/"]
                T1["themes_2026-05-19.md\n(vector indexed)"]
                T2["themes_2026-05-26.md\n(vector indexed)"]
                TDOT["..."]
            end
            subgraph RE["resumes/"]
                RI["index.md\nfilenames + Dropbox links"]
            end
        end

        subgraph SEC["secrets/ (encrypted)"]
            S1[ANTHROPIC_API_KEY]
            S2[DROPBOX_*]
            S3[GMAIL_*]
        end
    end

    AGENT["OpenClaw Agent"] -- reads --> BASE
    AGENT -- writes --> TH
    AGENT -- writes --> RI
    AGENT -- reads --> SEC
```

---

## 5. Sequence Diagram

```mermaid
sequenceDiagram
    participant PE  as 🕗 Proactive Engine
    participant GW  as 🦀 Gateway
    participant LB  as 🦞 Lobster Engine
    participant PW  as 🌐 playwright-mcp
    participant CL  as 🧠 Claude API
    participant MEM as 💾 Memory Store
    participant DP  as ☁️ dropbox-mcp
    participant GM  as 📧 gmail-mcp

    PE->>GW: fire(weekly_job_scan, week_date)
    GW->>LB: load_workflow(weekly_job_scan.yaml)

    LB->>PW: scrape(titles, Pune, last_7_days)
    PW-->>LB: raw_postings[]

    LB->>CL: extract_themes(raw_postings, prompt)
    CL-->>LB: theme_map{category:[{theme,freq}]}

    LB->>MEM: write(themes/themes_DATE.md, theme_map)

    LB->>MEM: read(workspace/base_resume.docx)
    MEM-->>LB: base_resume

    LB->>CL: rewrite_resume(base_resume, theme_map, prompt)
    CL-->>LB: Resume_WeekOf_DATE.docx

    LB->>DP: upload(Resume_WeekOf_DATE.docx, /Resumes/Weekly/)
    DP-->>LB: dropbox_link

    LB->>GM: send(to, subject, body, attachment)
    GM-->>LB: sent ✓

    LB->>GW: workflow_complete(week_date)
```

---

## 6. Config File Structure

```mermaid
flowchart TD
    subgraph CONFIG["config/openclaw.yaml"]
        direction TB
        GW2["gateway:\n  port: 3000\n  log_level: info"]
        LLM2["models:\n  default: claude-sonnet-4-6\n  fallback: ollama/llama3"]
        MCP2["mcp_servers:\n  playwright: ...\n  dropbox: ...\n  gmail: ..."]
        MEM2["memory:\n  path: ~/.openclaw/memory\n  vector_backend: ollama"]
    end

    CONFIG --> RUNTIME["OpenClaw Runtime"]
```

---

## 7. SDK vs OpenClaw Side-by-Side

```mermaid
quadrantChart
    title Implementation Complexity vs Flexibility
    x-axis Low Complexity --> High Complexity
    y-axis Low Flexibility --> High Flexibility
    quadrant-1 Powerful but hard
    quadrant-2 Best of both
    quadrant-3 Simple but limited
    quadrant-4 Hard and limited

    Anthropic SDK: [0.75, 0.90]
    OpenClaw: [0.25, 0.70]
    LangChain: [0.65, 0.80]
    No-code tools: [0.10, 0.25]
```

---

## 8. Project File Map

```
mg-ai-job-scanner/
│
├── workflows/
│   └── weekly_job_scan.yaml     ← entire pipeline in ~80 lines of YAML
│
├── prompts/
│   ├── theme_extraction.md      ← LLM prompt for theme analysis
│   ├── resume_writer.md         ← LLM prompt for resume rewrite
│   └── email_body.md            ← email body template
│
├── skills/
│   └── naukri_scraper.py        ← custom AgentSkill for Naukri.com
│
├── config/
│   └── openclaw.yaml            ← gateway, models, MCP, memory config
│
└── workspace/
    └── base_resume.docx         ← your immutable base resume
```
