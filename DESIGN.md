# Career Intelligence Engine (CIE) — System Design

## Overview

The **Career Intelligence Engine (CIE)** is a stateless-native, multi-agent serverless ecosystem designed to automate and optimize career preparation for high-intent technical roles (such as Agentic AI Product Managers, Platform Engineers, and System Architects). 

It operates serverlessly via GitHub Actions, persists structural state through Git-as-a-Database and SQLite, compiles source-grounded learning assets, builds active Test-Driven Development (TDD) proof-of-work project workspaces, and tracks LLMOps metrics in structured step logs.

---

## The 5 Strategic Pillars

### Pillar 1: Stateless-Native Memory (Git-as-a-Database)
CIE executes inside ephemeral runners (e.g. GitHub Actions virtual instances). To preserve learning state, interview scorecards, and scanning records without paid database servers, it synchronizes state:
1. **Pull Step**: Reads from origin branch `state-store` to load `state_history.json` and syncs it with local SQLite database `themes.db`.
2. **Push Step**: Compiles execution results into `state_history.json`, switches to `state-store` branch, commits, and pushes to remote.

### Pillar 2: Expanded Proof-of-Work Scaffolding
Agent 5 (Portfolio Architect) translates trending skill patterns into full **Test-Driven Development (TDD)** challenges. 
- Generated templates include a working `pytest` configuration and stubs.
- Populated with failing tests (`tests/test_*.py`) checking state, sync, and security validation structures.
- Candidate must write concrete code in `src/main.py` to make the suite turn green.

### Pillar 3: NotebookLM Ingestion Compiler
Agent 3 (Agent Tutor) scrapes corporate engineering blogs, architecture whitepapers, and scientific articles (arXiv). It compiles them into a pre-structured, hyper-dense markdown brief (`notebook_ingest_source.md`) formatted with structural retrieval anchors (e.g., `[EXECUTIVE SUMMARY]`, `[CORE TECH STACK DEEP DIVE]`). This maximizes Google NotebookLM's contextual recall accuracy.

### Pillar 4: LLMOps Observability & Tracing
Orchestration logs are transparently output into GHA Run Summaries via `gha_run_summary.md`, tracing execution status, confidence metrics, duration, token usage, and pipeline graph.

### Pillar 5: Rebranding & Discovery
Standardized root configuration files (`llms.txt` and `llms-full.txt`) allow agentic coding tools (Claude Code, Cursor, Copilot) to perfectly parse the codebase specs.

---

## Component Specifications

### 1. Job Scraper & In-Place Resume Tuner (Agent 1)
- **Managed Scrapers**: Apify Rotating Node crawlers.
- **In-Place DOCX Parser**: `python-docx` XML run paragraph editing to preserve template fonts and margins.
- **Reverse Loop Ingestion**: Analyzes the user's public GitHub footprint to inject undocumented strengths into the resume.

### 2. Stealth Opportunity Watchdog (Agent 2)
- **Direct ATS Parsing**: greenhouse.io and lever.co applicant endpoints.
- **Deduplication**: Relational unique key matches in SQLite.

### 3. Agent Tutor (Agent 3)
- **Extracs**: arXiv Search API and GitHub repositories.
- **Compiles**: Pre-structured markdown ingestion briefs, synthesizes podcaster voiceover scripts, and designs visual Mermaid mindmaps.

### 4. Agent Mock Interviewer (Agent 4)
- **Coaches**: Behavioral and system design interview simulator.
- **Saves**: Local markdown scorecards.

### 5. Agent Portfolio Architect (Agent 5)
- **Scaffolds**: Test-Driven Development (TDD) workspaces equipped with Pytest execution layers.

---

## Tech Stack & Service Interoperability

| Layer | Choice | Reason |
|---|---|---|
| **Orchestration** | Python 3.11+ / Gemini 2.0 Pro / Claude 3.5 Sonnet | Multi-agent pipelines, advanced professional copywriting |
| **Scheduling** | GitHub Actions Workflow (cron) | Stateless, 100% free serverless hosting |
| **Memory Sync** | Git branch (`state-store`) + `state_history.json` | Infinite state logging at $0 infra cost |
| **Relational Store**| SQLite (`themes.db`) | Local portable relational mapping |
| **Testing Engine** | Pytest / Pytest-Mock | Industry standard test automation runner |
| **Visual Mapping** | Mermaid.js | Dynamic, clean diagram parsing |
