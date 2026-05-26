# Career Intelligence Engine (CIE) — Architecture & Mermaid Diagrams

This document outlines the visual system engineering layout, relational tables, and pipeline sequences defining the **Career Intelligence Engine (CIE)**.

---

## 1. High-Level Multi-Agent Architecture

The Orchestrator agent boots inside GitHub Actions, pulls remote memory states, coordinates specialized agents via SQLite persistence, and writes back outputs to Git branches and GHA Summaries.

```mermaid
flowchart TD
    CRON([🕗 Weekly Cron / Manual Dispatch]):::trigger
    CRON --> ORCH

    subgraph ORCH["🤖 CIE Orchestrator Loop (main.py)"]
        direction TB
        GitPull[1 · Pull State from state-store branch] --> AgentRun[2 · Execute 5-Agent Ecosystem]
        AgentRun --> Observability[3 · Generate gha_run_summary.md]
        Observability --> GitPush[4 · Push updated state_history.json to state-store branch]
    end

    subgraph MEMORY["Stateless Memory Layer"]
        GitDB[("📁 Git-as-a-Database\nstate-store branch")]
        SQLiteDB[("🗄 SQLite db\nthemes.db")]
    end

    subgraph AGENTS["Specialized Agents"]
        A1[Agent 1: Scraper & Tuner]
        A2[Agent 2: Watchdog]
        A3[Agent 3: Agent Tutor]
        A4[Agent 4: Mock Interviewer]
        A5[Agent 5: Portfolio Architect]
    end

    GitPull <--> GitDB
    AgentRun <--> SQLiteDB
    A1 & A2 & A3 & A4 & A5 <--> AgentRun

    classDef trigger fill:#f5a623,color:#000,font-weight:bold
    classDef module fill:#4a90d9,color:#fff
```

---

## 2. Ingestion & Resume In-Place Rewrite Pipeline (Agent 1)

Swaps experience bullets using programmatic python-docx XML manipulation while analyzing the candidate's GitHub footprint.

```mermaid
flowchart LR
    BASE[/📄 base_resume.docx\nCanonical Template/]
    THEMES["📊 Scraped Weekly JDs\n+ GitHub Footprint"]
    
    BASE --> WRITER
    THEMES --> WRITER

    subgraph WRITER["🤖 Agent 1 — Resume Writer"]
        P1["Parse user public GitHub repos"]
        P2["Verify frequency keywords"]
        P3["XML In-Place Bullet Swaps"]
    end

    WRITER --> NEW[/"✅ Resume_WeekOf_YYYY-MM-DD.docx"/]
```

---

## 3. Git-as-a-Database State Synchronization Sequence

```mermaid
sequenceDiagram
    participant GHA as 🕗 GHA Cron Runner
    participant ORCH as 🤖 CIE Orchestrator
    participant GIT as 📁 Remote Git (state-store Branch)
    participant SQL as 🗄 SQLite local (themes.db)

    GHA->>ORCH: Execute pipeline main.py
    ORCH->>GIT: git fetch origin state-store
    GIT-->>ORCH: state_history.json payload
    ORCH->>SQL: Sync and seed trends into SQLite
    ORCH->>ORCH: Run Agent executions (Tuner, Watchdog, Tutor, Interviewer, Architect)
    ORCH->>SQL: Extract updated run parameters
    ORCH->>GIT: git checkout state-store && git commit state_history.json && git push origin
    GIT-->>ORCH: Pushed successfully ✓
    ORCH->>GHA: Output Step Summary markdown
```

---

## 4. TDD Project Scaffolding Structure (Agent 5)

Rather than plain boilerplate, CIE scaffolds fully functional, failing Pytest TDD repositories.

```mermaid
flowchart TD
    subgraph TDD_Scaffold ["Generated Portfolio Repository"]
        direction TB
        R1[README.md - explaining the TDD challenge]
        C1[pytest.ini - configuration parameters]
        R2[requirements.txt - installs pytest, pytest-mock]
        S1["src/main.py - main class raising NotImplementedError"]
        T1["tests/test_core.py - 3 failing pytest unit / security specs"]
        CI[".github/workflows/ci.yml - runs pytest on pushes"]
    end

    A5[Agent 5: Portfolio Architect] -->|Generates| TDD_Scaffold
```

---

## 5. Folder Architecture

```
mg-ai-job-scanner/
│
├── llms.txt                     ← Standard discovery profile for LLMs
├── llms-full.txt                ← Detailed specification sheet for LLMs
│
├── .github/workflows/
│   └── weekly_scan.yml          ← GHA with contents:write permission
│
├── config/
│   └── settings.yaml            ← Swappable model parameters
│
├── data/
│   ├── base_resume/             ← Immutable master resume
│   ├── store/
│   │   ├── themes.db            ← Relational database
│   │   └── state_history.json   ← Versioned state file
│   ├── tutor/
│   │   └── briefs/
│   │       └── brief_*.md       ← Pre-anchored NotebookLM briefs
│   └── portfolio/
│       └── scaffolds/           ← Local directories of scaffolded TDD labs
│
├── src/
│   ├── main.py                  ← Orchestrator Loop
│   ├── onboard.py               ← Onboarding Wizard
│   │
│   ├── analyzer/
│   │   ├── trending.py          ← SQLite Persistence
│   │   ├── git_database.py      ← Git-as-a-Database
│   │   └── observability.py     ← LLMOps Trace Observability
│   │
│   ├── tutor/
│   │   ├── agent_tutor.py       ← Upskilling brief compiler
│   │   ├── source_extractor.py  ← arXiv & GitHub crawler
│   │   └── notebooklm_client.py  ← Mock NotebookLM integrations
│   │
│   └── portfolio/
│       └── portfolio_architect.py ← failing pytest scaffold builder
```
