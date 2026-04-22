# Data Sources

This project uses three data sources across two pipelines: a structured data pipeline that feeds the Snowflake star schema and Streamlit dashboard, and a knowledge base pipeline that feeds qualitative market intelligence.

---

## Project Requirement: API Source

The project requires:

> "An API (REST, GraphQL, or a **Python client wrapping one**). Feeds your structured data pipeline (dbt → dashboard)."

This project satisfies that requirement with two API integrations:

**Primary: yfinance (Python client)**
`yfinance` is an open-source Python library that wraps Yahoo Finance's data API. It fits the explicit requirement category — "a Python client wrapping one" — pulling from Yahoo Finance's REST endpoints under the hood. Data flows directly into the structured pipeline:

`yfinance` → `RAW.REIT_DAILY_PRICES` / `RAW.REIT_QUARTERLY_FINANCIALS` → dbt staging → dbt mart → Streamlit dashboard

**Secondary: FRED REST API (authenticated)**
`fred_extract.py` calls the FRED REST API directly at `https://api.stlouisfed.org/fred/series/observations`. It requires a registered API key (`FRED_API_KEY`) stored as an environment variable — demonstrating authenticated REST API integration. FRED data loads to `RAW.FRED_OBSERVATIONS` and flows into the same structured pipeline as supplementary macroeconomic context.

Between yfinance (Python client wrapping an API) and FRED (direct authenticated REST API), this project satisfies the API requirement twice over.

---

## Source 1: REIT Financial Data (yfinance)

**What it is:** Publicly traded Real Estate Investment Trusts (REITs) are companies that own and operate commercial properties. Because they are publicly traded, their financial statements and stock prices are public. This source pulls daily stock prices and quarterly financial results for 9 major CRE REITs using the `yfinance` Python library.

**Companies covered:**

| Ticker | Company | Property Type | Market |
|---|---|---|---|
| BXP | Boston Properties | Office | Boston / NYC / DC |
| SLG | SL Green Realty | Office | New York City |
| VNO | Vornado Realty Trust | Office | New York City |
| PLD | Prologis | Industrial | National |
| STAG | STAG Industrial | Industrial | National |
| SPG | Simon Property Group | Retail | National |
| EQR | Equity Residential | Multifamily | National |
| AVB | AvalonBay Communities | Multifamily | National |
| ARE | Alexandria Real Estate | Life Science | National |

**Raw tables loaded:**
- `RAW.REIT_DAILY_PRICES` — one row per company per trading day: open, high, low, close price, volume, dividends
- `RAW.REIT_QUARTERLY_FINANCIALS` — one row per company per quarter: total revenue, net income, EBITDA, operating income, total assets, total debt, net debt, long-term debt

**Why this source:** REIT financial data is the closest publicly available proxy for commercial real estate market health. When office tenants leave buildings, office REIT revenue falls. When industrial demand grows from e-commerce, industrial REIT revenue grows. This data lets us answer real questions that a JLL Capital Markets advisor or institutional investor would ask — by property type, over time, and with actual dollar figures.

---

### Descriptive Questions (what happened?)

**"How have office REIT stock prices trended over the last 5 years?"**
Pull `close` from `fact_daily_prices`, filter `dim_reit.property_type = 'Office'`, group by quarter using `dim_date`. Shows the timeline of the office market decline since 2021.

**"Which property type generates the most revenue?"**
Sum `total_revenue` from `fact_quarterly_financials`, group by `dim_reit.property_type`. Ranks office, industrial, retail, and multifamily by revenue scale.

**"Which companies pay the highest dividends?"**
Sum `dividends` from `fact_daily_prices`, group by `dim_reit.company`. Dividend yield is a core metric for CRE investors.

**"How has total debt changed for office REITs since 2022?"**
Pull `total_debt` and `net_debt` from `fact_quarterly_financials`, filter to Office, group by quarter. Shows whether office companies took on more debt as revenues softened.

---

### Diagnostic Questions (why did it happen?)

**"Why did office REIT valuations drop 30–40% since 2021?"**
Compare `close` prices in `fact_daily_prices` for Office vs. Industrial from 2021–2024. Then layer in FRED mortgage rate data (Source 2) to show the rate spike that compressed valuations. The answer: remote work reduced tenant demand AND rising rates increased borrowing costs simultaneously.

**"Is office revenue actually declining, or just the stock price?"**
Stock prices can fall due to investor sentiment without revenue changing. Compare `total_revenue` trend in `fact_quarterly_financials` for Office REITs against their `close` price trend from `fact_daily_prices`. If both are falling, the business is genuinely declining — not just out of favor with investors.

**"Why is industrial outperforming office?"**
Compare `total_revenue` and EBITDA growth for Industrial vs. Office REITs from 2020–2024. Industrial growth tracks e-commerce expansion; office decline tracks remote work adoption. Two property types, opposite trajectories, same macro environment.

**"Which property types are most exposed to rising rates?"**
Higher debt means higher interest payments when rates rise. Compare `total_debt / total_assets` (leverage ratio) across property types using `fact_quarterly_financials` joined to `dim_reit`. The property type with highest leverage suffers most when rates spike.

---

## Source 2: FRED Macroeconomic Data (FRED API)

**What it is:** The Federal Reserve Bank of St. Louis publishes economic data through its FRED API. This source pulls the 30-year fixed mortgage rate — the single macro indicator most directly tied to commercial real estate valuations.

**Series pulled:**

| Series ID | Metric | Frequency | Why it matters |
|---|---|---|---|
| `MORTGAGE30US` | 30-Year Mortgage Rate | Weekly | Rising rates increase borrowing costs for CRE, directly compressing valuations |

**Raw table loaded:**
- `RAW.FRED_OBSERVATIONS` — one row per date: series_id, date, value

**Why this source:** REIT data shows *what* happened to valuations. Mortgage rate data shows *why*. The 2022–2023 rate hike cycle — rates climbing from 3% to 7% in 12 months — is the direct cause of the REIT price drops visible in `fact_daily_prices`. Overlaying both on a single chart is the clearest diagnostic insight in the project. FRED also uses a registered API key (`FRED_API_KEY`), demonstrating authenticated REST API integration alongside yfinance.

---

### How FRED Supports Diagnostic Analysis

**"Why did REIT prices crash in 2022?"**
Overlay `MORTGAGE30US` weekly rate data against average Office REIT `close` price from `fact_daily_prices`. The rate spike from 3% to 7% in 12 months is the direct cause of valuation compression. This is the project's core diagnostic insight — two lines on one chart tell the whole story.

---

## Source 3: Web Scraped Market Research (Firecrawl)

**What it is:** Qualitative market intelligence scraped from four commercial real estate research firms and trade publications using the Firecrawl API. Content includes quarterly market reports, sector outlooks, capital markets analyses, and industry news — with a focus on the Greater Los Angeles market where this JLL role is based.

**Sites scraped (4 sources):**
- JLL Research (jll.com) — national office dynamics, LA retail market
- CBRE Insights (cbre.com) — 2026 sector forecasts, capital markets outlook
- Cushman & Wakefield (cushmanwakefield.com) — LA office and industrial marketbeats (PDF reports)
- Bisnow (bisnow.com) — LA capital markets news, SoCal industrial investment activity

**Highlight sources:**

| File | Content | Why it matters |
|---|---|---|
| JLL US Office Market Dynamics Q1 2026 | National office leasing, absorption, delinquency | JLL's own research on the market they operate in |
| CBRE US Real Estate Market Outlook 2026 | Sector-by-sector forecasts for all property types | Cross-sector view matching REIT data coverage |
| Cushman LA Office Marketbeat Q2 2025 | Submarket vacancy table, key deals, rent data for Greater LA | Directly covers the market where the JLL role is located |
| Cushman LA Industrial Marketbeat Q1–Q3 2025 | Three consecutive quarters of LA industrial data — vacancy, absorption, port-driven demand | Matches Prologis/STAG industrial REIT data |
| Bisnow: LA Commercial Sales Bounce Back 2025 | Capital markets recovery story, office/retail/industrial sales volume | Local market narrative layer |
| Bisnow: SoCal Industrial $1.2B in Sales Q4 2025 | Specific deal volume, investor sentiment for LA industrial | Corroborates industrial REIT outperformance |
| JLL LA Retail Market Dynamics Q2 2025 | LA retail leasing, vacancy, market conditions | Adds retail sector coverage alongside Simon Property Group (SPG) REIT data |

**Total raw sources:** 20 files in `knowledge/raw/`

**Where it lives:**
- `knowledge/raw/` — markdown files, one per article, with title, URL, and full text
- `RAW.SCRAPE_ARTICLES` — same content loaded to Snowflake for pipeline completeness
- `knowledge/wiki/` — Claude Code-synthesized pages that compound insights across sources

**Why this source:** The structured REIT and FRED data answers quantitative questions. The scraped research answers qualitative ones: What are analysts saying about the LA market? What is JLL advising clients? What sectors are recovering and why? This content is not reducible to numbers — it requires reading and synthesis. Claude Code acts as the query engine against this knowledge base in the final interview demo.

---

### Questions the Knowledge Base Answers

- What is JLL's current outlook on office leasing and absorption in the US?
- What is the state of the Greater Los Angeles office market — vacancy, net absorption, key deals?
- How has the LA industrial market performed across Q1–Q3 2025, and what is driving demand?
- What are CBRE's sector-by-sector forecasts for office, industrial, retail, and multifamily in 2026?
- How are analysts characterizing the capital markets recovery in LA?
- What recommendations are analysts making to investors and occupiers in 2026?

These questions are answered by running Claude Code against `knowledge/wiki/` pages, which synthesize across all four sources rather than reflecting any single firm's view.

---

## How the Sources Work Together

The structured sources (REIT + FRED) power the dashboard's quantitative analysis. The scrape powers the qualitative knowledge base. Together they support both types of insight the project requires:

| Insight Type | Source | Example |
|---|---|---|
| Descriptive | REIT daily prices | Office REIT prices are down 35% since Jan 2022 |
| Descriptive | REIT quarterly financials | Industrial REIT revenue grew 28% from 2020–2024 |
| Diagnostic | REIT + FRED combined | Rate hike from 3% → 7% (FRED) correlates with 35% REIT price drop (yfinance) |
| Diagnostic | REIT financials | Office revenue declining alongside stock price — not just sentiment, real business deterioration |
| Qualitative | Scraped research | JLL and CBRE both project continued office market softness through 2025 |
