# Design: FRED API Pipeline — Milestone 01

## Overview

Extract macroeconomic data from the FRED API, load to Snowflake raw, transform through dbt staging and mart layers. Scheduled via GitHub Actions.

## Data Source

**API:** FRED (Federal Reserve Economic Data) — Federal Reserve Bank of St. Louis
**Base URL:** `https://api.stlouisfed.org/fred`
**Auth:** API key via `FRED_API_KEY` environment variable (free, no rate limit issues at this volume)

**Series:**

| Series ID | Metric | Frequency | ~Rows |
|---|---|---|---|
| `COMREAINTUSQ159N` | Commercial RE Price Index | Quarterly | ~100 |
| `MORTGAGE30US` | 30-Year Mortgage Rate | Weekly | ~2,700 |
| `UNRATE` | Unemployment Rate | Monthly | ~900 |
| `HOUST` | Housing Starts | Monthly | ~780 |
| `CPIAUCSL` | CPI (Inflation) | Monthly | ~920 |

Total: ~5,400 rows

## Extractor (`extractors/fred_extract.py`)

Follows the mp03 tutorial pattern: request → parse → loop → DataFrame → save.

1. Load `FRED_API_KEY` from `.env`
2. Loop over series IDs
3. Call `/fred/series/observations` → parse `data["observations"]`
4. Call `/fred/series` → parse metadata (name, units, frequency)
5. Append observations to results list with `series_id` column
6. Convert to DataFrame
7. Write to Snowflake `RAW.FRED_OBSERVATIONS` table (replace CSV with Snowflake connector)

## dbt Models

**Staging:**
- `stg_fred_observations` — cast types, rename columns, filter null values

**Mart (star schema):**
- `dim_series` — one row per series (series_id, name, units, frequency, category)
- `fact_observations` — one row per series per date (series_id, date, value)

At least one dbt test on each model (not_null, unique).

## GitHub Actions

Scheduled workflow (weekly cron):
- Runs `fred_extract.py`
- Then `dbt run && dbt test`
- Secrets: `FRED_API_KEY` + Snowflake credentials (`SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_PASSWORD`, `SNOWFLAKE_DATABASE`, `SNOWFLAKE_WAREHOUSE`, `SNOWFLAKE_SCHEMA`)

## Pipeline Diagram

Mermaid flowchart in README:
`FRED API → GitHub Actions → Snowflake RAW → dbt Staging → dbt Mart → Streamlit Dashboard`

## Insights

**Descriptive:** CRE price trends, mortgage rate history, unemployment over time

**Diagnostic:** Rate spike (2022-23) correlated with CRE price stall; CRE price growth vs. inflation (CPI); unemployment as leading indicator of CRE demand
