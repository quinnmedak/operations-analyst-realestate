# BI Analytics Pipeline — Commercial Real Estate

An end-to-end data pipeline and analytics project built to demonstrate Business Intelligence Analyst skills for a role at JLL. Pulls commercial real estate market data from public sources, transforms it through a Snowflake star schema via dbt, and surfaces insights through an interactive Streamlit dashboard and a Claude Code-queryable knowledge base.

**Target role:** Business Intelligence Analyst — JLL (Rosemead, CA)
**GitHub repo:** https://github.com/quinnmedak/operations-analyst-realestate

---

## Tech Stack

| Layer | Tool |
|---|---|
| Data Warehouse | Snowflake (AWS US East 1) |
| Transformation | dbt (staging + mart layers) |
| Orchestration | GitHub Actions (scheduled) |
| Dashboard | Streamlit (Streamlit Community Cloud) |
| Knowledge Base | Claude Code (scrape → synthesize → query) |
| Version Control | Git + GitHub |

---

## Data Sources

### Source 1: REIT Financial Data (yfinance)
Daily stock prices and quarterly financial statements for 9 major commercial real estate REITs across office, industrial, retail, multifamily, and life science property types.

**Raw tables:** `RAW.REIT_DAILY_PRICES`, `RAW.REIT_QUARTERLY_FINANCIALS`

| Ticker | Company | Property Type |
|---|---|---|
| BXP | Boston Properties | Office |
| SLG | SL Green Realty | Office |
| VNO | Vornado Realty Trust | Office |
| PLD | Prologis | Industrial |
| STAG | STAG Industrial | Industrial |
| SPG | Simon Property Group | Retail |
| EQR | Equity Residential | Multifamily |
| AVB | AvalonBay Communities | Multifamily |
| ARE | Alexandria Real Estate | Life Science |

### Source 2 (Supplementary): FRED Macroeconomic Data
30-year fixed mortgage rate (`MORTGAGE30US`) from the Federal Reserve Bank of St. Louis. Used as macro context to explain REIT valuation changes — the 2022–23 rate hike cycle overlaid against REIT price drops is the project's core diagnostic insight.

**Raw table:** `RAW.FRED_OBSERVATIONS`

### Source 3: Web Scraped Market Research (Firecrawl)
Qualitative market intelligence from JLL, CBRE, Cushman & Wakefield, and Bisnow. 20 raw sources covering national office market dynamics, Greater Los Angeles office and industrial market reports, 2026 sector forecasts, and LA capital markets activity.

**Raw table:** `RAW.SCRAPE_ARTICLES` | **Knowledge base:** `knowledge/raw/` (20 files)

See [docs/data-sources.md](docs/data-sources.md) for full source documentation, stakeholder questions, and analytical use cases.

---

## Pipeline Setup

### Prerequisites
- Python 3.11+
- Snowflake trial account (AWS US East 1)
- FRED API key (free at fred.stlouisfed.org)
- Firecrawl API key (free tier at firecrawl.dev)

### Environment Variables
Create a `.env` file in the project root:
```
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_WAREHOUSE=your_warehouse
FRED_API_KEY=your_fred_key
FIRECRAWL_API_KEY=your_firecrawl_key
```

### Install Dependencies
```bash
pip install yfinance pandas snowflake-connector-python snowflake-connector-python[pandas] python-dotenv requests
```

### Run Extractors
```bash
# REIT financial data (daily prices + quarterly financials)
python extractors/reit_extract.py

# FRED mortgage rate data
python extractors/fred_extract.py

# Web scrape to knowledge base + Snowflake
python extractors/scrape_extract.py
```

---

## Star Schema (dbt Mart)

*ERD coming in Milestone 02*

**Fact tables:**
- `fact_daily_prices` — one row per REIT per trading day (price, volume, dividends)
- `fact_quarterly_financials` — one row per REIT per quarter (revenue, net income, EBITDA, debt)
- `fact_macro_quarterly` — MORTGAGE30US aggregated to quarterly grain for diagnostic joins

**Dimension tables:**
- `dim_reit` — company name, property type, primary market
- `dim_date` — year, quarter, month, month name

---

## Dashboard

*Deployed URL coming in Milestone 02*

**Descriptive views:**
- REIT price trends by property type over time
- Revenue and EBITDA comparison across sectors
- Dividend yield by company

**Diagnostic views:**
- Office REIT price vs. mortgage rate overlay (2020–2025)
- Revenue trend vs. stock price for office REITs (sentiment vs. fundamentals)
- Debt-to-assets ratio by property type in rising rate environment

---

## Knowledge Base

20 raw sources in `knowledge/raw/` from 4 sites: JLL, CBRE, Cushman & Wakefield, Bisnow. Sources cover national office market dynamics, Greater Los Angeles office and industrial market reports (Q1–Q3 2025), 2026 sector forecasts, and LA capital markets activity.

Wiki pages synthesized by Claude Code in `knowledge/wiki/` *(coming Milestone 02)*

**To query the knowledge base:**
1. Open Claude Code in this repo
2. Ask questions like:
   - "What does my knowledge base say about LA office vacancy?"
   - "What are analysts forecasting for industrial CRE in 2026?"
   - "How is the LA market performing compared to national trends?"

---

## Insights Summary

*Coming in Milestone 02 after dbt models and dashboard are built*

---

## Pipeline Diagram

*Coming in Milestone 02*
