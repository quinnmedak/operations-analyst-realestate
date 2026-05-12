# Component Drill-Down Q&A
**Session: May 2026**

---

## Component 1: dbt Mart Layer & Star Schema

**Q1 — What does it do?**

*Your answer:* The dbt mart layer creates the tables queried by app.py for the Streamlit dashboard. The mart organizes data into a star schema with two dimensions and five fact tables. The staging layer cleans up column names and removes rows with null primary keys, and this data then goes to the mart layer where tables are created. dbt ensures queries run in the right order, tests the data, and documents how the data is organized.

*Corrections:*
- Keep staging and mart as distinct layers — mart's job is building the star schema, not cleaning. Cleaning is staging's job.
- `_mart.yml` is almost entirely tests (uniqueness, not-null, FK relationships), not documentation. No `description:` fields exist. Don't say dbt documents your schema.

*Stronger version:* "The mart layer takes the clean staging views and builds a star schema — two dims and five facts, all materialized as tables in the ANALYTICS schema. dbt manages the dependency order between models and runs data quality tests on primary keys and foreign keys."

*Verified against:* `dbt/cre_analytics/models/mart/_mart.yml`, `dbt_project.yml`, `models/mart/`

---

**Q2 — Why a star schema instead of a flat denormalized table?**

*Your answer:* Star schema makes for fast querying and simplest joins. Many fact tables are joined through the ticker variable, and the ticker dimension table associates each ticker with its company name and property type — so those columns don't need to exist in each fact table repetitively.

*Corrections:*
- `dim_reit` enriches facts, it doesn't join facts to each other. Star schema = each fact joins outward to dims, not fact-to-fact.
- Name the alternative explicitly: a single flat denormalized table.

*Stronger version:* "Star schema avoids redundancy. The alternative is a single flat table, but then company name and property type repeat across every price row. With a dim, I update one place. Each fact joins outward to the dims — not fact-to-fact joins, fact-to-dim."

*Verified against:* `dim_reit.sql`, `fact_daily_prices.sql`

---

**Q3 — What's a realistic failure mode?**

*Your answer:* I don't know.

*Answer:* A new ticker appears in yfinance data that isn't in `reit_companies.csv`. `dim_reit` is built from the seed, so the row either gets dropped or returns null company name and property type. No error fires — dbt runs green, the dashboard silently shows incomplete data. The fix is a dbt test that checks no tickers in `REIT_DAILY_PRICES` are missing from the seed.

*Verified against:* `dim_reit.sql`, `dbt/cre_analytics/seeds/`

---

**Q4 — What would you change with more time?**

*Your answer:* Two things. First, continue experimenting with `fact_quarterly_financials` — I built charts but discarded them when they didn't offer clear insights. There's rich data there (revenue, EBITDA, debt) worth exploring further, e.g. debt-to-EBITDA by property type vs. Fed Funds Rate. Second, the API extractors use manual chunked INSERT loops while `scrape_extract.py` uses `write_pandas` — I'd standardize all extractors to `write_pandas` for cleaner, more consistent loading code.

*Verified against:* `fact_quarterly_financials` has no references in `dashboard/app.py`. `reit_extract.py` uses manual INSERT; `scrape_extract.py` uses `write_pandas`.

---

**Q5 — What does the output flow into downstream?**

*Your answer:* The Streamlit dashboard queries the ANALYTICS schema using environment credentials for Snowflake. If a mart table schema changed, app.py may query the data wrong — and if it doesn't throw an error, charts may silently display incorrect data.

*Corrections:*
- Dashboard queries five mart tables, not three: `FACT_DAILY_PRICES`, `FACT_MACRO_QUARTERLY`, `FACT_LA_MARKET_SNAPSHOT`, `FACT_METRO_EMPLOYMENT`, and `DIM_REIT` (via JOIN). Only `FACT_QUARTERLY_FINANCIALS` and `DIM_DATE` are unused.
- Two distinct failure modes: hard failure (column dropped → SQL error on load) vs. silent failure (column keeps name, meaning changes → wrong chart, no error).

*Stronger version:* "Streamlit connects via five Snowflake env vars and queries five mart tables. A column rename throws a hard error on load. The scarier failure is silent — a column keeps its name but its meaning changes, and the chart renders wrong data with no indication anything broke."

*Verified against:* `dashboard/app.py` lines 107–111, 155–794

---

## Architecture Tradeoff Questions

**Q1 — Why Snowflake instead of local Pandas dataframes?**

*Your answer:* Industry standard for data engineering. Data lives in the cloud and is accessible. Most importantly, the Streamlit dashboard connects to Snowflake rather than something on your machine — so anyone can see the dashboard live.

*Stronger version:* "Two reasons. It's the industry standard for analytics, which made the architecture realistic for a BI role. And everything runs in the cloud end to end — GitHub Actions writes to Snowflake, dbt transforms in Snowflake, Streamlit reads from Snowflake. Anyone can see the live dashboard and the pipeline runs whether my laptop is on or not."

---

**Q2 — Why dbt instead of writing SQL transformations directly in Python?**

*Your answer:* dbt handles testing (uniqueness, not-null on PKs), staging views ensure consistent column naming and clean data, and YAML files organize the star schema.

*Corrections:*
- Don't say dbt "documents" — `_mart.yml` has no `description:` fields, only tests.
- Missing the main reason: dependency management. dbt builds a DAG from `ref()` calls so models run in the right order automatically. Without dbt you'd manually manage execution order across seven models.
- Also: transformations execute inside Snowflake via SQL pushdown, not in Python memory.

*Stronger version:* "Three reasons. Dependency management — dbt builds a DAG from ref() calls so models run in the right order automatically. Transformations execute inside Snowflake rather than pulling data into Python. And the testing framework — uniqueness, not-null, and foreign key tests run automatically with dbt test."

---

**Q3 — Why truncate-and-reload instead of incremental loads?**

*Your answer:* Truncate-and-reload is the simplest method. The data and project size are small enough that it makes sense. On a larger project, time and unnecessary API calls are wasted. For this project I avoided complexity, but I understand the costs of full truncate-and-reload at larger scale.

*Note:* Keep separate from the write_pandas improvement — those are two distinct issues. write_pandas improves insertion code quality but doesn't change the truncate-and-reload pattern.

---

**Q4 — Why Streamlit instead of Tableau or Power BI?**

*Your answer:* Tableau and Power BI are drag-and-drop tools for building charts visually. Streamlit gives full control through Python — you write exact queries and layout in code, which fits the existing stack. It also deploys for free, which Tableau and Power BI don't. The tradeoff is it's more code-intensive. I know those tools are standard in enterprise BI teams and I'm building familiarity with them.

*No corrections — strong answer.*

---

## Components Not Yet Covered
- GitHub Actions schedule
- dbt staging models
- FRED / BLS extractors
- Firecrawl scrape pipeline
- Knowledge base wiki structure
