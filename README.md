# Career Intelligence Engine

A serverless multi-agent ecosystem that automatically monitors job markets, scrapes stealth opportunities, tunes professional resumes, conducts interactive upskilling and mock interview loops, and scaffolds proof-of-work project repositories.

## Original Requirements

> On a weekly basis scan through all the job postings with location Pune and title ai product manager agentic ai product manager director / senior director of product management and vp of product manager and create me a database of the common themes across these postings, the idea is to use these common themes to write my resume, a base resume will be provided, please create an updated resume based on the scan results for that week and save it in a dropbox location using naming convention to clearly indicate the date of creation, once that is done send me an email with the Subject Update resume for week of <<date placeholder>> with the newly created resume attached.

## What it does (Unified Multi-Agent System)

1. **Job Scraper & Resume Tuner (Agent 1)**: Scans regional job boards for target roles, extracts frequency-weighted technical themes, and edits experience bullets *in-place* to target high-probability keywords without corrupting document layouts, integrating a **Reverse Loop** that analyzes the user's public GitHub profile footprint to highlight unstated expertise.
2. **Agent Opportunity Watchdog (Agent 2)**: Directly queries corporate Greenhouse and Lever ATS endpoints of top-tier AI organizations, identifying and alerting stealth job postings immediately upon publication.
3. **Agent Tutor (Agent 3)**: Crawls scholarly engines (arXiv API) and developer codebases (GitHub APIs) for weekly trends. Compiles engineering blogs, architectures, and threat landscapes into a hyper-dense, pre-anchored markdown brief (`notebook_ingest_source.md`) optimized for Google NotebookLM's context-retrieval recall, sending out structured weekly upskilling resources.
4. **Agent Mock Interviewer (Agent 4)**: Generates highly custom, difficulty-graded technical architecture and behavioral interview questions based on SQLite's weekly scanned themes and candidate resume bullets, evaluates performance, and logs evaluation scorecards.
5. **Agent Portfolio Architect (Agent 5)**: Translates weekly trending technology stacks into a full **Test-Driven Development (TDD) workspace** containing a suite of failing unit, integration, and security `pytest` templates. The developer must make the tests pass, creating a robust, verifiable proof-of-work project published to their GitHub.

---

## ⚡ The 5 Strategic Pillars (Architecture Upgrades)

CIE is engineered around five critical enterprise-ready technical principles:

### Pillar 1: Stateless-Native Memory (Git-as-a-Database)
Running 100% serverlessly in cron-based environments requires a stateless state-retention strategy. CIE implements a **Git-as-a-Database** model:
- At startup, the orchestrator pulls the `state_history.json` index from an isolated, secure Git branch (`state-store`).
- Runs relational SQLite synchronization, updating matching pipelines and ensuring zero context-drift between scheduled actions.
- At exit, the orchestrator packages scanned matches, resume edits, and interview scores back to `state_history.json` and pushes commits securely to `state-store`.

### Pillar 2: Proof-of-Work Scaffolding (TDD Workspaces)
Instead of basic template scaffolding, Agent 5 analyzes target requirements to build complete, functional TDD environments. The generated repositories include complete testing configs (`pytest.ini`, `requirements.txt`) and failing test suites (`tests/test_*.py`) that challenge the developer to implement functional code to prove their expertise.

### Pillar 3: NotebookLM Ingestion Compiler
To address Google NotebookLM's lack of a public API, Agent 3 aggregates scientific papers, blog specs, and system architectures into a pre-structured, clean markdown file `notebook_ingest_source.md` featuring retrieval anchors (e.g. `[EXECUTIVE SUMMARY]`, `[SYSTEM DESIGN SCENARIOS]`). Users can drop this single file into their NotebookLM workspace for high-fidelity QA retrieval.

### Pillar 4: LLMOps Observability & Tracing
Eliminates "black box" agent executions by providing comprehensive observability tracing. The engine compiles execution stages, inputs, confidence scores, and tokens into a structured `gha_run_summary.md` that is written directly into the **GitHub Actions Run Summary** interface.

### Pillar 5: Rebranding & Optimization
Standardizes CIE for modern AI discovery with standard metadata specifications (`llms.txt` and `llms-full.txt` at the root) which enable seamless context loading for agentic coding tools like Claude Code, Cursor, and Copilot.

---

## End-to-End System Workflow

To visualize the interactions between the 5 specialized agents, the Git-as-a-Database memory layer, relational triggers, and deployment targets, refer to our comprehensive workflow diagram:

```mermaid
graph TD
    UI[onboard.py Wizard] -->|Bootstrap| SQLite[(SQLite Storage)]
    UI -->|Setup| GHA[GitHub Actions Cron]
    
    subgraph Git_Memory [Stateless-Native Memory Layer]
        GitDB[(state-store Branch)] <-->|Git Database Sync| SQLite
    end
    
    GHA -->|Trigger Run| A1[Agent 1: Scraper & Tuner]
    GHA -->|Trigger Run| A2[Agent 2: Opportunity Watchdog]
    
    A1 -->|Log Scans| SQLite
    A1 -->|Tune XML w/ Reverse GitHub Loop| Resume[Tailored Resume]
    A2 -->|Direct ATS Scrapes| SQLite
    A2 -->|Alert User| Notify[Weekly Notifications]
    
    SQLite -->|Unmapped Trends| A3[Agent 3: Agent Tutor]
    A3 -->|arXiv & GitHub| Search[Research Scrapes]
    A3 -->|Workspace compiler| Brief[notebook_ingest_source.md]
    Brief -->|Ingest| NotebookLM[NotebookLM / Gemini Cache]
    NotebookLM -->|Deliver Study Plan| Mail[SMTP Email]
    A3 -->|Log notebooks| SQLite
    
    SQLite -->|Target Skills & Resume| A4[Agent 4: Mock Interviewer]
    A4 -->|System Design Questions| A4
    A4 -->|Evaluation Scorecards| SQLite
    
    SQLite -->|Trending Stacks| A5[Agent 5: Portfolio Architect]
    A5 -->|Scaffold TDD Workspace| Git[User GitHub Profile]
    A5 -->|Log Metadata| SQLite
```

For a comprehensive, high-fidelity mapping of all 8 core career preparation use cases, data models, and system pathways, check out the dedicated **[System Workflow Specification](docs/SYSTEM_WORKFLOW.md)**.

## Documentation

### System Design & Workflows
* **[System Workflow Specification](docs/SYSTEM_WORKFLOW.md)** — Detailed Mermaid.js diagram and documentation of the 8 production career preparation use cases.
* **[Product & Technical Pitch](PITCH.md)** — Establishes the vision, system engineering trade-offs, and product decisions (e.g., Build vs. Buy, Defensive UX, and State persistence) directly aligning with **Agentic AI Product Manager** competencies, alongside the future NotebookLM upskilling roadmap.

### Anthropic SDK Implementation
- [System Design](DESIGN.md) — architecture, components, tech stack, agent flow
- [Visual Architecture](ARCHITECTURE.md) — Mermaid diagrams: system flow, scraper, theme pipeline, resume generation, sequence diagram, data model

### OpenClaw Implementation (Alternate)
- [OpenClaw Design](DESIGN_OPENCLAW.md) — Lobster YAML workflow, MCPorter integrations, memory architecture, SDK vs OpenClaw comparison
- [OpenClaw Architecture](ARCHITECTURE_OPENCLAW.md) — Mermaid diagrams: Gateway/TaskFlow, Lobster steps, MCP map, memory layout, sequence diagram

### Hybrid GHA + Python Implementation (Option 3 — Recommended)
- [Hybrid Design](DESIGN_HYBRID.md) — GHA runtime, python-docx XML manipulation, Apify integration, secret auto-refresh
- [Hybrid Architecture](ARCHITECTURE_HYBRID.md) — Mermaid diagrams: cloud system flow, ingestion pipeline, docx in-place edits, sequence flow
- [Agent Tutor Upskilling Design](DESIGN_AGENT_TUTOR.md) — Relational SQLite schemas, Google NotebookLM Client & universal Gemini fallbacks, deduplication checks, arXiv/GitHub crawl pipelines

## Status

> **Fully Operational & Memory-Enabled** — The multi-agent engine is production-ready, running serverless weekly cron cycles via GitHub Actions, persisted dynamically via Git-as-a-Database and SQLite, and integrated with live learning and TDD evaluation loops. See [PITCH.md](PITCH.md) for the product vision and [DESIGN_HYBRID.md](DESIGN_HYBRID.md) for the architectural blueprint.

---

## Deployment & Usage Guide

Follow these steps to deploy and run the **Career Intelligence Engine** locally or in a serverless GitHub Actions environment:

### 1. Prerequisite Setup
Ensure Python 3.8+ is installed. Clone the repository and install all required modules:
```bash
git clone https://github.com/mayukhg/mg-ai-job-scanner.git
cd mg-ai-job-scanner
pip install -r requirements.txt
```

### 2. Run the Interactive Onboarding Flow
Configure your profile, set scan frequencies, select job boards, specify notification targets, and safely hook up credentials without leaking them:
```bash
python onboard.py
```
> [!IMPORTANT]
> **Defensive UX Security**: Sensitive access keys (e.g. Gemini API Key, GitHub PAT, Dropbox Token) are written directly to a secure, git-ignored local `.env` file at your project root, preventing accidental commits while maintaining seamless developer access.

### 3. Execute the Ecosystem Main Loop
To trigger a manual scan, resume updates, mock interviewer questions, upskilling packs, and TDD project scaffolding, run:
```bash
python src/main.py
```

### 4. Serverless Cloud Setup (GitHub Actions)
To run this multi-agent loop 100% serverless on a weekly or daily schedule:
1. Ensure your settings (`config/settings.yaml`) are committed and pushed to your remote repository.
2. In your GitHub repository homepage, navigate to **Settings > Secrets and variables > Actions**.
3. Define the following Actions Repository Secrets matching your local `.env`:
   * `GEMINI_API_KEY`: Your Gemini/Google AI Studio key for upskilling caching and mock coaching.
   * `GITHUB_PAT`: GitHub personal access token with `repo` scopes to permit Agent Portfolio Architect to push scaffolds to your account.
   * `DROPBOX_ACCESS_TOKEN`: API token to sync relaid resumes and sqlite persistence vaults.
4. Navigate to the **Actions** tab in your repository and enable the pre-configured workflow scheduler.



