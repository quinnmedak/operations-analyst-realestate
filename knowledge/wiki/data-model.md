# Data Model: Star Schema & dbt

## What dbt Is

dbt (data build tool) is a transformation layer that sits between raw Snowflake tables and the analytical tables the dashboard reads from. The core idea: you write SELECT statements, and dbt handles everything else — creating the tables and views in Snowflake, tracking which models depend on which, enforcing data quality tests, and compiling a dependency graph so models always run in the right order.

Without dbt you would write `CREATE OR REPLACE TABLE` statements manually, manage execution order yourself, and have no built-in testing. With dbt, the entire transformation layer is version-controlled SQL with a test suite attached.

**Two things dbt does that matter most for this project:**

`{{ ref('model_name') }}` — instead of hardcoding a table name, you reference another model by name. dbt reads all those references, builds a dependency graph, and runs models in the correct order automatically. `fact_daily_prices` references `stg_reit_daily_prices` and `dim_reit` — dbt ensures both exist before building the fact table.

Materialization — staging models are materialized as **views** (no storage cost, always reflect the latest raw data), mart models are materialized as **tables** (pre-computed, fast for the dashboard to query). This is set in `dbt_project.yml` and can be overridden per model.

**Testing** is declared in `_mart.yml`. Tests like `unique`, `not_null`, and `relationships` run with `dbt test` and fail the pipeline if data quality breaks — e.g., if a REIT ticker in `fact_daily_prices` has no matching row in `dim_reit`, the relationships test catches it.

---

## What a Star Schema Is

A star schema organizes data into two types of tables: **fact tables** that hold measurements (prices, employment, vacancy rates) and **dimension tables** that hold descriptive attributes used to filter and group those measurements. The name comes from the shape: fact table at the center, dimension tables radiating outward like points of a star.

The reason to use this pattern: analytical queries almost always follow the same shape — "give me [fact metric] grouped by or filtered on [dimension attribute]." In this project: "give me average close price grouped by property type" requires joining `fact_daily_prices` to `dim_reit` on `ticker`. The star schema makes that join simple and consistent, and Snowflake's columnar storage engine is specifically optimized for this query pattern.

---

## The Dimensions

**`dim_reit`** — one row per REIT ticker. Four columns: `ticker`, `company_name`, `property_type`, `primary_market`. Seeded from `reit_companies.csv` — this is static reference data, not pulled from an API. The key column for the dashboard is `property_type` (Office, Industrial, Retail, Multifamily, Life Science), which is what lets the REIT price chart split by sector. Because this dimension is defined once and referenced by multiple fact tables, REIT metadata never has to be repeated.

**`dim_date`** — a date spine. One row per calendar day, with derived columns: `year`, `quarter`, `month`, `month_name`, `year_quarter`. Provides a consistent time axis that multiple fact tables can join to. This is a standard dimensional modeling pattern — instead of storing date math in every fact table, you compute it once in the dimension.

---

## The Fact Tables

**`fact_daily_prices`** — daily REIT price data. Grain: one row per ticker per day. Columns: `ticker` (FK → `dim_reit`), `date_day` (FK → `dim_date`), `open`, `high`, `low`, `close`, `volume`, `dividends`. Source: yfinance via `stg_reit_daily_prices`. This is the highest-volume table — 9 tickers × years of daily history. The FK join to `dim_reit` is what lets the dashboard filter by `property_type` without that column living in the fact table itself.

**`fact_quarterly_financials`** — REIT financial metrics by quarter. Grain: one row per ticker per reporting period. Columns: `ticker` (FK → `dim_reit`), `period_date` (FK → `dim_date`), plus revenue, net income, EBITDA, operating income, total assets, total debt, net debt, long-term debt. Source: yfinance quarterly financials via `stg_reit_quarterly_financials`.

**`fact_macro_quarterly`** — FRED macro indicators, one row per quarter. This table is notable because it is a **pivot**: the FRED raw data comes in as a tall/narrow format (one row per series per date), and dbt transforms it into a wide format (one row per quarter, one column per series). The nine FRED series — FEDFUNDS, DGS10, MORTGAGE30US, T10Y2Y, UNRATE, PAYEMS, ECOMPCTNSA, DRCRELEXFACBS, CREACBW027SBOG — each become their own column. This makes dashboard queries simple: `SELECT fedfunds, ecompctnsa FROM FACT_MACRO_QUARTERLY WHERE year = 2024` rather than filtering by series ID every time. This table has no FK to `dim_reit` (macro data is not REIT-specific) and no FK to `dim_date` (quarterly grain doesn't map cleanly to a single date).

**`fact_metro_employment`** — BLS metro employment by sector and month. Grain: one row per metro per supersector per month. Columns: `series_id`, `metro`, `supersector`, `year`, `month`, `date_day` (FK → `dim_date`), `employment_thousands`. No FK to `dim_reit` — employment is market-level data, not REIT-level. The dashboard filters this table to `Financial Activities` and `Professional & Business Services` to isolate office-using employment as a leading indicator for office leasing recovery.

**`fact_la_market_snapshot`** — LA submarket vacancy, absorption, and asking rent. Grain: one row per property type per submarket per period. This table is seeded from `la_marketbeat.csv` — static data manually compiled from Cushman & Wakefield and CBRE quarterly MarketBeat reports. It does not auto-update. No FK to `dim_reit` or `dim_date` — it uses its own `period` and `period_date` columns because the grain is a CRE reporting quarter, not a financial reporting date. This is the table that powers the space market KPI cards and submarket breakdown expander in the dashboard.

---

## Why Some Fact Tables Don't Join to the Dimensions

Three of the five fact tables (`fact_macro_quarterly`, `fact_la_market_snapshot`, `fact_metro_employment` for metro) don't have FKs back to `dim_reit`. This is intentional: those tables describe market-level conditions, not individual REIT behavior. Forcing a join to `dim_reit` would be meaningless — FEDFUNDS isn't a property of Prologis, it's a property of the economy. The star schema only requires FKs where the relationship is real.

---

## The Staging Layer

Before data reaches the mart, it passes through staging views (`stg_*`). Staging models do three things: rename columns to a consistent convention (e.g., `DATE` → `date_day`), cast types, and document the source table. They are materialized as views — no storage cost, and the mart tables that reference them always see fresh raw data. The staging layer is what makes the mart models readable: by the time `fact_daily_prices` runs, all the column names and types are already clean.

---

## The Schema Override Macro

By default, dbt concatenates your target name and schema name — a `+schema: ANALYTICS` config would produce `dev__ANALYTICS` in development. The `generate_schema_name` macro in `dbt/cre_analytics/macros/` overrides this so all models write directly to `ANALYTICS` regardless of target. This matters for the dashboard: `streamlit run dashboard/app.py` connects to `ANALYTICS`, and the Snowflake credentials in `.env` point to the same place whether the models were built locally or via GitHub Actions.
