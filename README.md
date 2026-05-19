# mg-ai-job-scanner

A weekly AI agent that scans PM/AI product job postings in Pune, extracts common themes, and generates a tailored resume — automatically saved to Dropbox and emailed every Monday.

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
