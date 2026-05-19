# mg-ai-job-scanner

A weekly AI agent that scans PM/AI product job postings in Pune, extracts common themes, and generates a tailored resume — automatically saved to Dropbox and emailed every Monday.

## Original Requirements

> I want to create an AI agent with the described functionality, first create me a system design for this, here are my requirement - On a weekly basis scan through all the job postings with location Pune and title ai product manager agentic ai product manager director / senior director of product management and vp of product manager and create me a data base of the common themes across these postings, the idea is to use these common themes to write my resume, a base resume will be provided, please create an updated resume based on the scan results for that week and save it in a dropbox location using naming convention to clearly indicate the data of creation, once that is done send me an email with the Subject Update resume for week of <<date placeholder>> with the newly created resume attached

## What it does

1. **Scans** LinkedIn, Naukri, Indeed, and Glassdoor for AI PM / Director / VP of Product roles in Pune
2. **Analyzes** job descriptions with Claude to extract frequency-weighted themes (skills, responsibilities, keywords)
3. **Rewrites** a base resume to reflect the week's most in-demand themes
4. **Saves** the updated resume to Dropbox as `Resume_Mayukh_Ghosh_PM_WeekOf_YYYY-MM-DD.docx`
5. **Emails** the resume to you with a summary of the top themes

## Documentation

- [System Design](DESIGN.md) — architecture, components, tech stack, agent flow

## Status

> Under construction — see [DESIGN.md](DESIGN.md) for the full plan.
