# Pipeline Walkthrough — Bullet Outline
**Use this to practice and self-check. Each bullet = one beat to hit.**

---

## INTRO
- [ ] Name both pipelines: structured + unstructured
- [ ] Draw two columns, label them

---

## STRUCTURED PIPELINE

### Sources
- [ ] **yfinance**: daily prices + volume / quarterly financials (rev, NI, EBITDA, debt) / 8 REIT tickers / two separate endpoints → two tables
- [ ] **FRED API**: 9 macro series — name at least: Fed Funds, 10Y Treasury, CRE delinquency rate, yield curve spread
- [ ] **BLS API**: metro-level employment by supersector, queried by CBSA code

### RAW Schema (Snowflake)
- [ ] Three extractor scripts: reit_extract.py, fred_extract.py, bls_extract.py
- [ ] Truncate-and-reload on every run
- [ ] 4 tables: **REIT_DAILY_PRICES**, **REIT_QUARTERLY_FINANCIALS**, **FRED_OBSERVATIONS**, **BLS_METRO_EMPLOYMENT**
- [ ] RAW = landing zone only, no transformations

### dbt Staging (views → ANALYTICS schema)
- [ ] 5 staging views: **stg_reit_daily_prices**, **stg_reit_quarterly_financials**, **stg_fred_observations**, **stg_bls_metro_employment**, **stg_la_marketbeat**
- [ ] Materialized as **views** (no storage, recompute at query time)
- [ ] Staging work: rename to snake_case, cast types, drop null PKs — no joins or aggregations
- [ ] 2 seeds: **reit_companies.csv** (ticker → company/property type), **la_marketbeat.csv** (Cushman LA submarket snapshot — manual refresh)
- [ ] **generate_schema_name macro**: overrides default schema concatenation so all targets write directly to ANALYTICS (not dev__ANALYTICS)

### dbt Mart (tables → ANALYTICS schema)
- [ ] 2 dims: **dim_reit** (joins seed data), **dim_date** (date spine)
- [ ] 5 facts: **fact_daily_prices**, **fact_quarterly_financials**, **fact_macro_quarterly**, **fact_metro_employment**, **fact_la_market_snapshot**
- [ ] Call out **fact_macro_quarterly**: pivots FRED from long (one row/series/date) → wide (one row/quarter, each series as a column)
- [ ] Mart materialized as **tables** (not views) — dashboard queries on load, avoid recomputing joins
- [ ] dbt tests: uniqueness + not-null on PKs, FK referential integrity

### Dashboard + Schedule
- [ ] Streamlit app: **dashboard/app.py** → reads ANALYTICS schema via env vars
- [ ] GitHub Actions schedule: REIT = weekly (Monday), FRED + BLS = monthly (1st)
- [ ] All support **workflow_dispatch** for manual runs
- [ ] Post-extract steps: dbt seed → dbt run → dbt test

---

## UNSTRUCTURED PIPELINE

### Sources
- [ ] CRE research reports: **JLL, CBRE, Cushman & Wakefield, Bisnow**
- [ ] PDFs + web pages — not APIs

### knowledge/raw/
- [ ] Extractor: **scrape_extract.py** using **Firecrawl** (API that returns page content as clean markdown)
- [ ] 28 markdown files in knowledge/raw/
- [ ] Runs **quarterly** via GitHub Actions

### knowledge/wiki/
- [ ] **Claude Code** synthesizes 28 raw docs → **15 structured wiki pages** in knowledge/wiki/
- [ ] Name a few pages: **la-office-market.md**, **la-industrial-market.md**, **macro-environment.md**, **capital-markets.md**, **national-cre-trends.md**
- [ ] **knowledge/index.md**: entry point — one-line summary + cross-references per page
- [ ] Ingest schema: new file in raw/ → agent identifies relevant wiki pages → updates them → structured commit
- [ ] Query schema: read index.md → read relevant wiki pages → drill into raw/ only for specific figures/quotes

---

## CLOSING
- [ ] Two pipelines, separate schedules, separate outputs
- [ ] Structured → dashboard | Unstructured → knowledge base
- [ ] Knowledge base queryable directly through Claude Code
