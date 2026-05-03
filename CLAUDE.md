# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Portfolio analytics project targeting the JLL Business Intelligence Analyst role. Pulls commercial real estate market data from four sources, transforms it in Snowflake via dbt, and surfaces insights through a Streamlit dashboard and a Claude Code-queryable knowledge base.

**Target role:** Business Intelligence Analyst — JLL  
**GitHub repo:** https://github.com/quinnmedak/operations-analyst-realestate

## Commands

### Extractors

Run from the project root. Each script truncates and reloads its Snowflake RAW table.

```bash
python extractors/reit_extract.py       # REIT daily prices + quarterly financials (yfinance)
python extractors/fred_extract.py       # FRED macro indicators (9 series)
python extractors/bls_extract.py        # BLS metro employment by sector
python extractors/scrape_extract.py     # Web scrape → knowledge/raw/ (Firecrawl)
```

Only `fred_extract.py` runs on a schedule (GitHub Actions, 1st of month). The others must be triggered manually or via `workflow_dispatch`.

### dbt

All dbt commands run from `dbt/cre_analytics/`. The `~/.dbt/profiles.yml` (not in repo) must have a `cre_analytics` profile pointing to Snowflake.

```bash
cd dbt/cre_analytics
dbt seed          # Load static CSVs: reit_companies.csv, la_marketbeat.csv
dbt run           # Build staging views + mart tables in ANALYTICS schema
dbt test          # Validate data quality (uniqueness, not-null, FK relationships)
dbt run -s stg_fred_observations   # Run a single model
dbt test -s fact_daily_prices      # Test a single model
```

### Dashboard

```bash
streamlit run dashboard/app.py
```

Reads from Snowflake `ANALYTICS` schema. Requires `.env` in project root with all `SNOWFLAKE_*` vars.

## Architecture

Two independent data paths run in parallel:

**Structured path:** `extractors/*.py` → Snowflake `RAW` schema → dbt staging (views) → dbt mart (tables) → `ANALYTICS` schema → Streamlit dashboard

**Unstructured path:** `scrape_extract.py` → `knowledge/raw/` → Claude Code synthesis → `knowledge/wiki/`

### Snowflake Schema Layout

| Schema | Owner | Contents |
|---|---|---|
| `RAW` | extractors | One table per source: `REIT_DAILY_PRICES`, `REIT_QUARTERLY_FINANCIALS`, `FRED_OBSERVATIONS`, `BLS_METRO_EMPLOYMENT` |
| `ANALYTICS` | dbt | Staging views (`stg_*`) and mart tables (`dim_*`, `fact_*`) |

The `generate_schema_name` macro in `dbt/cre_analytics/macros/` overrides dbt's default schema concatenation so `+schema: ANALYTICS` in `dbt_project.yml` writes directly to `ANALYTICS` (not `<target>__ANALYTICS`).

### Star Schema (mart layer)

- `dim_reit` — ticker, company name, property type, primary market (seeded from `reit_companies.csv`)
- `dim_date` — date spine
- `fact_daily_prices` — daily REIT close/volume, FK to `dim_reit` + `dim_date`
- `fact_quarterly_financials` — REIT revenue, net income, EBITDA, debt
- `fact_macro_quarterly` — FRED series pivoted to one row per quarter (fedfunds, delinquency, e-commerce %, Treasury yields)
- `fact_metro_employment` — BLS metro employment by supersector and month
- `fact_la_market_snapshot` — LA office/industrial vacancy, absorption, asking rent by submarket (seeded from `la_marketbeat.csv`)

`fact_la_market_snapshot` is static seed data from Cushman & Wakefield MarketBeat; it does not update automatically.

### SQL Style

Uppercase all SQL keywords in dbt models and queries (e.g. `SELECT`, `FROM`, `WHERE`, `JOIN`).

## Data Sources

- **yfinance** — REIT daily prices and quarterly financials
- **FRED API** — 9 macro series: FEDFUNDS, DGS10, MORTGAGE30US, T10Y2Y, UNRATE, PAYEMS, ECOMPCTNSA, DRCRELEXFACBS, CREACBW027SBOG
- **BLS API** — metro-level employment by supersector
- **Firecrawl** — CRE market reports (JLL, CBRE, Cushman & Wakefield, Bisnow) scraped to `knowledge/raw/`

## Credentials & Secrets

All secrets are in `.env` (local) and GitHub Actions secrets (CI). Never commit them.

Required environment variables:
- `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_PASSWORD`, `SNOWFLAKE_DATABASE`, `SNOWFLAKE_WAREHOUSE`
- `FRED_API_KEY` — free at fred.stlouisfed.org
- `FIRECRAWL_API_KEY` — free tier at firecrawl.dev

## Querying the Knowledge Base

The `knowledge/` folder is the project's knowledge base: 24 scraped reports in `knowledge/raw/`, synthesized into 7 wiki pages in `knowledge/wiki/`. `knowledge/index.md` is the entry point — it lists all wiki pages with one-line summaries and cross-references.

**Conventions when answering knowledge base questions:**
- Always cite which wiki page or raw source the answer draws from
- If the question spans multiple wiki pages, synthesize across them rather than answering from one alone
- If the answer isn't in the knowledge base, say so explicitly rather than inferring from general knowledge

## Knowledge Base Schema

Three operations define how the agent interacts with `knowledge/`.

### Ingest

Triggered when a new file lands in `knowledge/raw/`.

1. Read the new source in full.
2. Identify which wiki page(s) in `knowledge/wiki/` it is relevant to. If no page exists, create one.
3. Update those wiki pages to incorporate the new evidence — synthesize, don't just append.
4. Add or update the entry in `knowledge/index.md` with a one-line summary.
5. Commit with a message of the form: `knowledge: ingest <source-name> → update <wiki-page(s)>`.

### Query

Triggered when asked any domain question about commercial real estate, JLL, market trends, or this project's data.

1. Read `knowledge/index.md` first to identify which wiki pages are relevant.
2. Read those wiki pages in full.
3. Drill into `knowledge/raw/` only when direct evidence, quotes, or precise figures are needed to support the answer.
4. Always cite the specific wiki page or raw source used. If the answer spans multiple pages, synthesize across them. If the answer is not in the knowledge base, say so explicitly — do not infer from general knowledge.

### Lint

Run periodically (or when asked) to keep the wiki consistent as the corpus grows.

1. Scan all pages in `knowledge/wiki/` for contradictions — claims on one page that conflict with another.
2. Flag stale claims — figures, dates, or assertions that a newer raw source has superseded.
3. Identify orphan pages — wiki pages that no other wiki page or `index.md` links to.
4. Identify missing cross-references — topics mentioned on a page that have their own wiki page but are not linked.
5. Report findings as a list of issues with the file and section for each. Do not auto-fix — present for human review.
