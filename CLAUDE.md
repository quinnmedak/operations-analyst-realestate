# CLAUDE.md — Project Context

## Project Overview

This is a portfolio analytics project built to demonstrate skills required for the JLL Business Intelligence Analyst role. It pulls commercial real estate market data through two sources, transforms it in Snowflake via dbt, and surfaces insights through a Streamlit dashboard and a Claude Code-queryable knowledge base.

**Target role:** Business Intelligence Analyst — JLL  
**GitHub repo:** https://github.com/quinnmedak/operations-analyst-realestate

## Tech Stack

| Layer | Tool |
|---|---|
| Data Warehouse | Snowflake (AWS US East 1) |
| Transformation | dbt (staging + mart layers) |
| Orchestration | GitHub Actions (scheduled) |
| Dashboard | Streamlit (deployed to Streamlit Community Cloud) |
| Knowledge Base | Claude Code (scrape → summarize → query) |
| Version Control | Git + GitHub (public repo) |

## Directory Structure

```
extractors/         # Python scripts to pull from API and web scrape sources
dbt/
  models/
    staging/        # Cleaning, renaming, type casting per source
    mart/           # Star schema: fact + dimension tables
dashboard/          # Streamlit app connected to Snowflake mart tables
knowledge/
  raw/              # 15+ scraped sources (market reports, press releases, etc.)
  wiki/             # Claude Code-generated synthesis pages
  index.md          # Index of all wiki pages with one-line summaries
.github/
  workflows/        # GitHub Actions pipelines (scheduled extraction + load)
docs/
  job-posting.pdf
  proposal.pdf
  proposal.md
```

## Data Sources

- **Source 1 (API):** Commercial real estate market data (candidates: FRED, HUD, RentCast, Census Bureau)
- **Source 2 (Web scrape):** Industry research and market reports (candidates: JLL Research, CBRE, Bisnow, GlobeSt)

Sources are finalized during Milestone 01.

## Credentials & Secrets

Never commit credentials to this repo. All secrets (Snowflake credentials, API keys) are stored as environment variables and GitHub Actions secrets.

Required environment variables:
- `SNOWFLAKE_ACCOUNT`
- `SNOWFLAKE_USER`
- `SNOWFLAKE_PASSWORD`
- `SNOWFLAKE_DATABASE`
- `SNOWFLAKE_WAREHOUSE`
- `SNOWFLAKE_SCHEMA`

## Querying the Knowledge Base

The `knowledge/` folder is the project's knowledge base. To query it:

1. Open Claude Code in this repo
2. Ask questions like: "What does my knowledge base say about commercial real estate vacancy trends?" or "Summarize what the wiki says about JLL's market positioning"
3. Claude Code will read `knowledge/wiki/` pages and `knowledge/raw/` sources to answer

Wiki pages are synthesized from multiple raw sources — not just individual summaries. The `knowledge/index.md` lists all wiki pages with one-line descriptions.

**Conventions Claude Code should follow when answering knowledge base questions:**
- Always cite which wiki page or raw source the answer draws from
- If the question spans multiple wiki pages, synthesize across them rather than answering from one alone
- If the answer isn't in the knowledge base, say so explicitly rather than inferring from general knowledge
