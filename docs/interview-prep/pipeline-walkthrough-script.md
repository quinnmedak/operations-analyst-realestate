# Pipeline Walkthrough — Full Script
**Target: 7–8 minutes | Live verbal presentation**

Whiteboard cues are in [brackets]. Draw as you narrate — don't draw silently then explain.

---

## INTRO (~20 sec)

"I built two independent data pipelines for this project — a structured path and an unstructured path. Let me draw them both out."

[Draw two columns. Label left: **STRUCTURED** | Label right: **UNSTRUCTURED**]

---

## STRUCTURED PIPELINE (~4 min)

### Sources

[Draw **SOURCES** box top-left]

"I have three API sources.

yfinance — a Python wrapper around Yahoo Finance. I'm pulling two things from it: daily closing prices and volume for eight REIT tickers, and separately their quarterly financials — revenue, net income, EBITDA, total debt. Those come back as separate endpoints so they land in separate tables.

FRED API from the St. Louis Fed. Nine macro series: Fed Funds Rate, 10-year Treasury, 30-year mortgage rate, the 10-2 yield curve spread, unemployment, total nonfarm payrolls, e-commerce share of retail, CRE loan delinquency rate, and total CRE loans outstanding.

BLS API — Bureau of Labor Statistics. Metro-level employment by supersector. I'm querying it by CBSA code so I can filter down to specific metros."

### RAW Schema

[Draw arrow → **RAW schema** box. Label the four tables inside it.]

"Each source has a dedicated extractor script in extractors/ — reit_extract.py, fred_extract.py, bls_extract.py. Each one does a full truncate-and-reload on every run into Snowflake's RAW schema.

Four tables: REIT_DAILY_PRICES, REIT_QUARTERLY_FINANCIALS, FRED_OBSERVATIONS, BLS_METRO_EMPLOYMENT.

RAW is just a landing zone — column names and types come straight off the API response, no transformations."

### dbt Staging

[Draw arrow → **dbt staging** box. Label: views, ANALYTICS schema.]

"dbt picks it up from there. The staging layer has five models: stg_reit_daily_prices, stg_reit_quarterly_financials, stg_fred_observations, stg_bls_metro_employment, and stg_la_marketbeat.

These are materialized as views — no storage cost, they just run at query time. The staging models do three things: rename columns to snake_case, cast types explicitly, and drop rows with null primary keys. No aggregations, no joins at this layer.

I also have two dbt seeds — static CSVs that dbt loads as tables. reit_companies.csv maps tickers to company names and property types. la_marketbeat.csv is a Cushman & Wakefield LA submarket snapshot — vacancy, absorption, asking rent by submarket and quarter. That one doesn't update automatically, it's manually refreshed from the PDF.

One thing worth mentioning — I have a custom generate_schema_name macro in dbt that overrides dbt's default schema concatenation behavior. By default dbt would write to something like dev__ANALYTICS. The macro makes it write directly to ANALYTICS regardless of target, so dev and prod land in the same schema."

### dbt Mart

[Draw arrow → **dbt mart** box. Label the seven tables inside it.]

"The mart layer is a star schema. Two dims: dim_reit joins the REIT seed so property type and company name live alongside every fact row, and dim_date is a date spine generated from a dbt macro — it exists so I can join on date even when there's no fact row for a given day.

Five facts: fact_daily_prices, fact_quarterly_financials, fact_macro_quarterly, fact_metro_employment, and fact_la_market_snapshot.

fact_macro_quarterly is worth calling out — FRED comes in as a long table with one row per series per date. That model pivots it so you get one row per quarter with each of the nine series as its own column. That makes cross-series comparison much cleaner downstream.

Everything in the mart is materialized as a table, not a view, because the dashboard queries it on load and I don't want to recompute the joins every time.

dbt also runs tests — uniqueness and not-null on primary keys, referential integrity between facts and dims."

### Dashboard + Schedule

[Draw arrow → **Streamlit** box]

"The Streamlit app connects to Snowflake via environment variables and queries the ANALYTICS schema directly. dashboard/app.py.

The pipeline runs on GitHub Actions. reit_extract.py runs every Monday. fred_extract.py and bls_extract.py run on the first of every month. All three support workflow_dispatch for manual triggers. After each extractor runs, you'd run dbt seed, dbt run, dbt test to rebuild the mart."

---

## UNSTRUCTURED PIPELINE (~3 min)

### Sources

[Draw **SOURCES** box top-right]

"The unstructured pipeline is separate architecture entirely.

Sources are CRE research reports — JLL, CBRE, Cushman & Wakefield, Bisnow. PDFs and web pages, not APIs."

### knowledge/raw/

[Draw arrow → **knowledge/raw/** box]

"The extractor here is scrape_extract.py, which uses Firecrawl — a web scraping service with an API. You give it a URL, it returns the full page content as clean markdown. The script writes each report as a .md file into knowledge/raw/.

Right now there are 28 documents in there — JLL industrial tenant demand studies, CBRE US outlook reports, Cushman LA office and industrial marketbeats, Bisnow articles on LA submarkets. The script runs quarterly via GitHub Actions."

### knowledge/wiki/

[Draw arrow → **knowledge/wiki/** box]

"From knowledge/raw/, Claude Code synthesizes the raw documents into 15 structured wiki pages in knowledge/wiki/. Pages like la-office-market.md, la-industrial-market.md, macro-environment.md, capital-markets.md, national-cre-trends.md.

There's a knowledge/index.md that acts as the entry point — every wiki page has a one-line summary and cross-references. The synthesis process follows a defined schema: when a new file lands in raw/, the agent identifies which wiki pages it's relevant to, updates them to incorporate the new evidence, and commits with a structured message.

The knowledge base is queryable. The query flow reads index.md first to identify relevant pages, then reads those pages in full, then drills into raw/ only if it needs a specific figure or direct quote."

---

## CLOSING (~20 sec)

"So two pipelines — structured feeds the dashboard with quantitative data, unstructured builds the knowledge base from research reports. They run independently, on separate schedules, and write to separate outputs. The dashboard is where the structured data surfaces; the knowledge base is queryable directly through Claude Code."

---

*~880 words — approximately 7 minutes at a conversational pace.*
*Draw each box as you introduce it. Don't race through table names — say them clearly once.*
