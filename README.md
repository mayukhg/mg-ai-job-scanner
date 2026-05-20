# Career Intelligence Engine

A serverless multi-agent ecosystem that automatically monitors job markets, scrapes stealth opportunities, tunes professional resumes, conducts interactive upskilling and mock interview loops, and scaffolds proof-of-work project repositories.

## Original Requirements

> On a weekly basis scan through all the job postings with location Pune and title ai product manager agentic ai product manager director / senior director of product management and vp of product manager and create me a database of the common themes across these postings, the idea is to use these common themes to write my resume, a base resume will be provided, please create an updated resume based on the scan results for that week and save it in a dropbox location using naming convention to clearly indicate the date of creation, once that is done send me an email with the Subject Update resume for week of <<date placeholder>> with the newly created resume attached.

## What it does (Unified Multi-Agent System)

1. **Job Scraper & Resume Tuner**: Scans regional job boards for AI PM / Director / VP of Product roles, extracts frequency-weighted technical themes, and edits experience bullets *in-place* to target high-probability keywords without corrupting document layouts.
2. **Agent Opportunity Watchdog**: Directly queries the Greenhouse and Lever ATS endpoints of top-tier AI organizations, identifying and alerts stealth job postings immediately upon publication.
3. **Agent Tutor**: Queries research repositories (arXiv API) and code libraries (GitHub APIs), programmatically deploys factual NotebookLM upskilling workspaces, generates voice-synthesis explainer podcasts, and emails a structured Weekly Study Plan.
4. **Agent Mock Interviewer**: Generates highly custom, difficulty-graded technical architecture and behavioral interview questions based on SQLite's weekly scanned themes and candidate resume bullets, evaluates performance, and logs evaluation scorecards.
5. **Agent Portfolio Architect**: Automatically translates trending technical stacks into fully structural open-source lab templates (source files, tests, requirements, and GitHub Actions CI pipelines) published directly to the user's GitHub account to display visible proof-of-expertise.


## Documentation

### Core Project Pitch
- [Product & Technical Pitch](PITCH.md) — Establishes the vision, system engineering trade-offs, and product decisions (e.g., Build vs. Buy, Defensive UX, and State persistence) directly aligning with **Agentic AI Product Manager** competencies, alongside the future NotebookLM upskilling roadmap.

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

> Under construction — see [DESIGN.md](DESIGN.md) for the full plan.
