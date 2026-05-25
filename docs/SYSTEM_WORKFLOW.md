# Career Intelligence Engine — End-to-End System Workflow

This document provides a highly detailed, technical blueprint of the **Career Intelligence Engine's** architecture, highlighting the relationships, data loops, and triggers between all five specialized AI agents, the central SQLite database state layer, and the outer deployment endpoints.

---

## 1. End-to-End System Workflow Diagram

The following Mermaid.js diagram illustrates the complete execution pipeline, from interactive setup to automated code publishing:

```mermaid
graph TB
    %% Styling Classes
    classDef frontend fill:#4a148c,stroke:#333,stroke-width:2px,color:#fff;
    classDef agent fill:#6a1b9a,stroke:#333,stroke-width:2px,color:#fff;
    classDef database fill:#1565c0,stroke:#333,stroke-width:2px,color:#fff;
    classDef api fill:#2e7d32,stroke:#333,stroke-width:1px,color:#fff;
    classDef deliverable fill:#e65100,stroke:#333,stroke-width:2px,color:#fff;

    %% Subgraph: Front-End & Input Layer
    subgraph Input_Layer ["1. Configuration & Security Gateway"]
        UI["Onboarding Webpage / CLI Portal<br/>(onboard.py)"]:::frontend
        YAML["System Preferences<br/>(config/settings.yaml)"]:::frontend
        ENV["Secure Credentials Vault<br/>(.env / Repo Secrets)"]:::frontend
        ResumeBase["Master Candidate Resume<br/>(Resume_Base.docx)"]:::frontend
    end

    %% Subgraph: Relational State Controller
    subgraph Database_State ["2. Central Relational Store (SQLite: themes.db)"]
        DB_Trends["trending_topics<br/>(week_id, topic, key, score)"]:::database
        DB_Notebooks["generated_notebooks<br/>(topic, notebook_id, urls)"]:::database
        DB_Stealth["stealth_opportunities<br/>(company, title, url, alerted)"]:::database
        DB_Interviews["mock_interviews<br/>(week_id, type, score, scorecard_path)"]:::database
        DB_Portfolio["portfolio_projects<br/>(name, stack, local_path, github_url)"]:::database
    end

    %% Subgraph: Ingestion & Market Agents
    subgraph Market_Ingestion ["3. Market Intelligence & Stealth Hunting"]
        Agent1["Agent 1: Job Scanner & Resume Tuner<br/>(src/resume/)"]:::agent
        Agent2["Agent 2: Opportunity Watchdog<br/>(src/scraper/)"]:::agent
        Apify["Apify Scraper Crawler<br/>(Regional Boards)"]:::api
        ATS["ATS Direct Scrapers<br/>(Greenhouse & Lever)"]:::api
    end

    %% Subgraph: Continuous Upskilling (Tutor)
    subgraph Upskilling_Loop ["4. Closed-Loop Upskilling (Agent Tutor)"]
        Agent3["Agent 3: Agent Tutor<br/>(src/tutor/)"]:::agent
        ArXiv["arXiv Search API<br/>(Academic Papers)"]:::api
        GitHubAPI["GitHub Search API<br/>(Code Specifications)"]:::api
        NotebookLM["Google NotebookLM Client<br/>(Gemini Context Cache fallback)"]:::api
    end

    %% Subgraph: Continuous Evaluation (Interviewer)
    subgraph Evaluation_Loop ["5. Career Readiness Coach (Agent Mock Interviewer)"]
        Agent4["Agent 4: Agent Mock Interviewer<br/>(src/interviewer/)"]:::agent
    end

    %% Subgraph: Practical Scaffolding (Portfolio Architect)
    subgraph Practical_Scaffolding ["6. Practical Proof-of-Work (Agent Portfolio Architect)"]
        Agent5["Agent 5: Agent Portfolio Architect<br/>(src/portfolio/)"]:::agent
    end

    %% Subgraph: Outer Deliverables
    subgraph Deliverables ["7. Sync, Notifications & Portfolios"]
        ResumeOutput["Tailored Resume<br/>(Resume_YYYYMMDD.docx)"]:::deliverable
        DropboxSync["Dropbox Cloud Sync<br/>(/Resumes/Weekly/)"]:::deliverable
        StealthAlert["Alert Notifications<br/>(Stealth Openings Detected)"]:::deliverable
        StudyEmail["Weekly Study Plan Email<br/>(Podcasts, Mindmaps, Notebook Links)"]:::deliverable
        ScorecardMD["Markdown Scorecard Log<br/>(Interview Readiness Stats)"]:::deliverable
        GitRepo["Active GitHub Repository<br/>(Published Lab Proof-of-Work)"]:::deliverable
    end

    %% Dynamic Data Flow and Interaction Connections

    %% Setup & Ingestion Triggers
    UI -->|1. Interactive Setup| YAML
    UI -->|2. Write Secrets| ENV
    YAML -->|Load Configurations| Agent1 & Agent2 & Agent3 & Agent4 & Agent5

    %% Agent 1 Flow (Scan & Resume Tune)
    Agent1 -->|Trigger Crawl| Apify
    Apify -->|Raw JD Ingestion| Agent1
    Agent1 -->|Extract & Weight Themes| DB_Trends
    DB_Trends -->|3. Feed Scanned Keywords| Agent1
    ResumeBase -->|4. Input Base Bullets| Agent1
    Agent1 -->|5. XML In-Place Copywriting| ResumeOutput
    ResumeOutput -->|6. Auto-Sync Backup| DropboxSync

    %% Agent 2 Flow (Stealth Opportunities Watchdog)
    Agent2 -->|Trigger Direct Scrapes| ATS
    ATS -->|Stealth Postings Payload| Agent2
    Agent2 -->|7. Relational Deduplication| DB_Stealth
    DB_Stealth -->|Write New Unique Openings| DB_Stealth
    Agent2 -->|8. Alert Dispatch| StealthAlert

    %% Agent 3 Flow (Agent Tutor Upskilling)
    DB_Trends -->|9. Extract Unmapped Topics| Agent3
    Agent3 -->|Query Scientific Knowledge| ArXiv
    Agent3 -->|Query Standard Code Specs| GitHubAPI
    ArXiv & GitHubAPI -->|Unified Grounding Payload| Agent3
    Agent3 -->|10. Instantiate Workspace| NotebookLM
    NotebookLM -->|11. Synthesize Podcasts, Mindmaps & Scripts| Agent3
    Agent3 -->|12. Persistence Logging| DB_Notebooks
    Agent3 -->|13. Deliver Weekly Study Plan| StudyEmail

    %% Agent 4 Flow (Agent Mock Interviewer Coach)
    DB_Trends -->|14. Fetch Target Skill Themes| Agent4
    ResumeOutput -->|15. Import Custom Experience Bullets| Agent4
    Agent4 -->|16. Dynamic Difficulty Questionnaire| Agent4
    Agent4 -->|17. Local Markdown Grading| ScorecardMD
    Agent4 -->|18. Log Performance Scorecards| DB_Interviews

    %% Agent 5 Flow (Agent Portfolio Architect Scaffolder)
    DB_Trends -->|19. Identify Trending Technology Combinations| Agent5
    Agent5 -->|20. Generate Boilerplate Template| Agent5
    Agent5 -->|21. Scaffold Directories & GHA CI YAMLs| GitRepo
    Agent5 -->|22. Version Proof-of-Work Metas| DB_Portfolio
```

---

## 2. Deep-Dive: The 8 Production-Grade Use Cases

The Career Intelligence Engine operates across **eight core career optimization use cases** represented in the diagram:

### Use Case 1: Interactive Onboarding & Bootstrapping
* **Actors**: User, `onboard.py` Onboarding Wizard.
* **Flow**: The user runs the wizard to set scan frequency (weekly/monthly/quarterly), toggle scraper backends (Apify/SerpApi), input the notification email, choose learning modes, and hook up target stealth companies.
* **Value**: Separates general preferences (saved in `settings.yaml`) from secure API keys (written to a local, git-ignored `.env` file), ensuring zero-leak security.

### Use Case 2: Dynamic In-Place Resume Keyword Injection
* **Actors**: Agent 1 (Resume Tuner), SQLite Database, Dropbox.
* **Flow**: Agent 1 extracts frequency-weighted keywords from Pune job openings and loads the base resume. It modifies XML text runs *in-place* to swap bullet points matching active keywords.
* **Value**: Preserves the original professional document layout and styling while optimizing the resume to bypass corporate ATS screens.

### Use Case 3: Stealth Opportunity Alerts
* **Actors**: Agent 2 (Opportunity Watchdog), Greenhouse/Lever ATS APIs, SQLite Database.
* **Flow**: Agent 2 directly scrapes target AI companies' public ATS pipelines. It runs unique-key database checks to deduplicate listings.
* **Value**: Discovers stealth opportunities immediately upon publication, bypassing job boards and allowing you to apply before general applicants.

### Use Case 4: Scholarly & Developer Ingestion
* **Actors**: Agent 3 (Agent Tutor), arXiv Search API, GitHub API.
* **Flow**: Agent 3 takes unmapped, high-priority weekly trend keywords and executes academic searches (arXiv papers) and code searches (popular GitHub templates).
* **Value**: Ground-truths the upskilling payload on academic whitepapers and real developer patterns instead of generic web content.

### Use Case 5: Workspace Orchestration & NotebookLM Creation
* **Actors**: Agent 3 (Agent Tutor), Google NotebookLM Client / Gemini Context Caches.
* **Flow**: The agent programmatically instantiates a Google Notebook named `<<TopicName-DateOfCreation>>` (or provisions a Gemini Context Cache) and loads the harvested arXiv/GitHub documents into memory.
* **Value**: Deploys a customized, grounded upskilling sandbox mapped exactly to the candidate's active skill gaps.

### Use Case 6: Continuous Upskilling & Study Plan Delivery
* **Actors**: Agent 3 (Agent Tutor), SMTP Email Server.
* **Flow**: Agent Tutor triggers generative models to synthesize study materials (multimodal audio WAV podcast, Mermaid.js mindmap diagram, and video storyboard script outline) and emails the package to the candidate.
* **Value**: Delivers an automated, highly personalized weekly study plan directly to your inbox.

### Use Case 7: Adaptive Behavioral & Technical Interview Coaching
* **Actors**: Agent 4 (Agent Mock Interviewer), Candidate, SQLite Database.
* **Flow**: Agent 4 retrieves target skills and the candidate's resume. It generates technical architecture and behavioral questionnaires calibrated to selected difficulties (`easy`/`medium`/`hard`/`executive`). It simulates responses and writes a rating scorecard (`scorecard_*.md`).
* **Value**: Conducts rigorous, tailored technical system-design interview sessions and registers historical readiness ratings in the database.

### Use Case 8: Programmatic Proof-of-Work Portfolio Scaffolding
* **Actors**: Agent 5 (Agent Portfolio Architect), GitHub Remote Repository.
* **Flow**: Agent 5 maps leading technical stack combinations and scaffolds a complete local project layout (folders, stubs, tests, requirements, and GitHub Actions CI pipelines). It publishes these ready-to-run repositories directly to your GitHub.
* **Value**: Automatically builds a credible, active GitHub portfolio containing real proof-of-expertise for hiring managers to review.
