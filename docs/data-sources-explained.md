# Data Sources

This project uses four data sources across two pipelines: a structured data pipeline that feeds the Snowflake star schema and Streamlit dashboard, and a knowledge base pipeline that feeds qualitative market intelligence.

---

## Project Requirement: API Source

The project requires:

> "An API (REST, GraphQL, or a **Python client wrapping one**). Feeds your structured data pipeline (dbt → dashboard)."

This project satisfies that requirement with three API integrations:

**Primary: yfinance (Python client)**
`yfinance` is an open-source Python library that wraps Yahoo Finance's data API. It fits the explicit requirement category — "a Python client wrapping one" — pulling from Yahoo Finance's REST endpoints under the hood. Data flows directly into the structured pipeline:

`yfinance` → `RAW.REIT_DAILY_PRICES` / `RAW.REIT_QUARTERLY_FINANCIALS` → dbt staging → dbt mart → Streamlit dashboard

**Secondary: FRED REST API (authenticated)**
`fred_extract.py` calls the FRED REST API directly at `https://api.stlouisfed.org/fred/series/observations`. Requires a registered API key (`FRED_API_KEY`) stored as an environment variable. Loads 9 macroeconomic series to `RAW.FRED_OBSERVATIONS`.

**Tertiary: BLS CES REST API (unauthenticated)**
`bls_extract.py` calls the BLS Current Employment Statistics API at `https://api.bls.gov/publicAPI/v2/timeseries/data/`. No key required. Loads metro employment data for 8 cities to `RAW.BLS_METRO_EMPLOYMENT`.

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
- `RAW.REIT_DAILY_PRICES` — one row per company per trading day: open, high, low, close price, volume, dividends. ~11,300 rows, 5 years of history.
- `RAW.REIT_QUARTERLY_FINANCIALS` — one row per company per quarter: total revenue, net income, EBITDA, operating income, total assets, total debt, net debt, long-term debt. ~55 rows.

**Why this source:** Commercial real estate is almost entirely a private market — lease terms, sale prices, vacancy rates, and rental income are not publicly disclosed. Accessing this data normally requires paid subscriptions like CoStar or MSCI Real Capital Analytics. REITs are the exception: because they are publicly traded companies, they are required by the SEC to report their financials every quarter. This makes REIT data the only freely available window into real CRE financial performance.

The data maps directly to market conditions by property type: BXP, SLG, and VNO own Manhattan and Boston office towers, so their declining revenue is a direct signal of falling office demand — not just investor sentiment. Prologis and STAG own industrial warehouses, so their growing revenue reflects real e-commerce-driven demand. This distinction matters analytically: if office REIT *stock prices* fall but *revenue* holds steady, that is a sentiment problem. If both fall together, that is genuine business deterioration. REIT quarterly financials are the data that answers that question — a real question a JLL analyst would ask.

---

### Relevance to the JLL BI Analyst Role

**Stock prices** are a leading indicator of private market sentiment. JLL advises clients on buying, selling, and financing commercial properties. When REIT stock prices fall, public market investors are signaling that CRE values are declining — and that directly affects what buyers will pay in private transactions, which is JLL's core business. A BI analyst supporting JLL's capital markets team would track REIT performance to anticipate where deal activity and pricing are heading.

**Total debt** is the most directly actionable metric for JLL. When interest rates rise, companies carrying heavy debt can't afford to refinance. That creates distressed assets — properties owners are forced to sell below market value. JLL gets hired to broker those sales. Tracking which sectors carry the highest leverage ratios tells you where distressed activity is most likely to emerge — and where JLL should be focusing business development.

The metrics that most directly connect to the JLL BI Analyst job are: stock price trends as a market health signal, debt leverage as a refinancing risk indicator, and revenue decline as evidence of real occupancy deterioration. These three together tell the story a JLL analyst would need to tell a client.

---

### Descriptive Questions (what happened?)

**"How have office REIT stock prices trended over the last 5 years?"**
Pull `close` from `fact_daily_prices`, filter `dim_reit.property_type = 'Office'`, group by quarter using `dim_date`. Shows the timeline of the office market decline since 2021.

**"Which property type generates the most revenue?"**
Sum `total_revenue` from `fact_quarterly_financials`, group by `dim_reit.property_type`. Ranks office, industrial, retail, and multifamily by revenue scale.

**"How has total debt changed for office REITs since 2022?"**
Pull `total_debt` and `net_debt` from `fact_quarterly_financials`, filter to Office, group by quarter. Shows whether office companies took on more debt as revenues softened.

---

### Diagnostic Questions (why did it happen?)

**"Why did office REIT valuations drop 30–40% since 2021?"**
Compare `close` prices for Office vs. Industrial from 2021–2024. Layer in FRED rate data (Source 2) to show the rate spike. The answer: remote work reduced tenant demand AND rising rates increased borrowing costs simultaneously.

**"Is office revenue actually declining, or just the stock price?"**
Compare `total_revenue` trend in `fact_quarterly_financials` for Office REITs against their `close` price trend. If both are falling, the business is genuinely declining — not just out of favor with investors.

**"Why is industrial outperforming office?"**
Compare `total_revenue` and EBITDA growth for Industrial vs. Office REITs from 2020–2024. Industrial growth tracks e-commerce expansion (`ECOMPCTNSA` from FRED); office decline tracks remote work adoption.

**"Which property types are most exposed to rising rates?"**
Compare `total_debt / total_assets` across property types. The property type with highest leverage suffers most when rates spike.

---

## Source 2: FRED Macroeconomic Data (FRED REST API)

**What it is:** The Federal Reserve Bank of St. Louis publishes economic data through its FRED API. This source pulls 9 macroeconomic series directly relevant to commercial real estate valuation and demand.

**Raw table loaded:**
- `RAW.FRED_OBSERVATIONS` — one row per series per date: series_id, date, value. 36,904 rows total. Stored in long format; pivoted to one column per series at quarterly grain in the dbt mart layer (`fact_macro_quarterly`).

**Series pulled:**

| Series ID | Metric | Frequency | Why it matters |
|---|---|---|---|
| `MORTGAGE30US` | 30-Year Fixed Mortgage Rate | Weekly | Rising rates increase borrowing costs for CRE, directly compressing valuations |
| `DGS10` | 10-Year Treasury Yield | Daily | The benchmark cap rates are priced against — REIT valuations move inversely with this |
| `FEDFUNDS` | Federal Funds Rate | Monthly | The Fed policy rate that drove the 2022–23 rate hike cycle |
| `T10Y2Y` | 10yr minus 2yr Treasury Spread | Daily | Yield curve inversion (negative = recession signal → office demand slowdown) |
| `UNRATE` | Unemployment Rate | Monthly | Fewer employed people = less office space demanded |
| `PAYEMS` | Total Nonfarm Payrolls | Monthly | Overall job growth → demand for office and industrial space |
| `ECOMPCTNSA` | E-Commerce as % of Retail Sales | Quarterly | Directly explains industrial REIT outperformance — the e-commerce demand story |
| `DRCRELEXFACBS` | CRE Loan Delinquency Rate at Banks | Quarterly | Shows actual financial stress in the CRE sector, not just stock price sentiment |
| `CREACBW027SBOG` | CRE Loans Outstanding at Banks | Weekly | Credit availability — tightens when rates rise, limiting new CRE activity |

**Why this source:** REIT data shows *what* happened to valuations. FRED data shows *why*. The 2022–23 rate hike cycle — `FEDFUNDS` climbing from 0.08% to 5.33% in 18 months, `DGS10` rising from 1.5% to 4.5%, `MORTGAGE30US` jumping from 3% to 7% — is the direct cause of the REIT price drops visible in `fact_daily_prices`. Overlaying these on a single chart is the project's core diagnostic insight.

---

### How FRED Supports Diagnostic Analysis

**"Why did REIT prices crash in 2022?"**
Overlay `FEDFUNDS` and `DGS10` against average Office REIT `close` price. The rate spike from near-zero to 5%+ is the direct cause of valuation compression.

**"Is the CRE sector financially stressed beyond just falling prices?"**
`DRCRELEXFACBS` shows CRE loan delinquency at banks rising from 0.63% in 2022 Q3 to 1.58% by 2025 Q1 — real loan defaults, not just stock sentiment.

**"What drove industrial REIT outperformance?"**
`ECOMPCTNSA` held at 13–18% of all retail sales post-COVID (vs. ~11% pre-COVID) — elevated e-commerce sustaining industrial warehouse demand even as office suffered.

---

## Source 3: BLS Metro Employment (BLS CES API)

**What it is:** The Bureau of Labor Statistics Current Employment Statistics (CES) program publishes monthly employment data for U.S. metropolitan areas by industry supersector. This source pulls two office-using industry groups for 8 major metros that correspond to the markets where the covered REITs operate.

**Raw table loaded:**
- `RAW.BLS_METRO_EMPLOYMENT` — one row per metro per supersector per month: series_id, metro, supersector, year, period, employment_thousands. 1,184 rows, January 2020–present.

**Metros and industry groups covered:**

| Metro | CBSA | Why included |
|---|---|---|
| New York | 35620 | BXP, SLG, VNO (office); EQR (multifamily) |
| Los Angeles | 31080 | Primary market for the JLL role |
| Boston | 14460 | BXP headquarters market |
| Washington DC | 47900 | BXP major market |
| San Francisco | 41860 | ARE (Alexandria Real Estate) primary market |
| Chicago | 16980 | VNO and national office market |
| Dallas | 19100 | National industrial and office coverage |
| Seattle | 42660 | STAG industrial coverage |

**Industry supersectors tracked:**
- **Financial Activities** (BLS code 55) — finance and real estate employment combined
- **Professional & Business Services** (BLS code 60) — the largest office-using sector; legal, consulting, accounting, tech services

**Why this source:** REIT revenue and stock price data tells you what happened nationally. BLS metro employment adds the geographic dimension: which specific cities are losing or gaining office-using jobs, and does that track with the REIT performance for companies concentrated in those markets? LA office employment declining year-over-year → LA-focused REIT revenue falling → a story you can tell with data specific to the market where the JLL role is located.

---

### Questions BLS Metro Employment Answers

**"Is LA office employment actually declining, or is it a national story?"**
Compare Financial Activities and Professional & Business Services employment trends for Los Angeles vs. NYC vs. national REIT averages. LA-specific decline = local structural problem; national decline = macro story.

**"Which metros are recovering fastest in office-using employment?"**
Rank metros by employment growth rate from 2023–2025. Shows where office demand recovery is leading vs. lagging.

**"Does metro employment growth predict REIT revenue performance?"**
Join BLS metro employment trends against `fact_quarterly_financials` revenue for REITs concentrated in those markets. Employment leads revenue — it's the leading indicator.

---

## Source 4: Web Scraped Market Research (Firecrawl)

**What it is:** Qualitative market intelligence scraped from four commercial real estate research firms and trade publications using the Firecrawl API. Content includes quarterly market reports, sector outlooks, capital markets analyses, and industry news — with a focus on the Greater Los Angeles market where this JLL role is based.

**Sites scraped (4 sources):**
- JLL Research (jll.com) — national office dynamics, LA retail market
- CBRE Insights (cbre.com) — 2026 sector forecasts, capital markets outlook
- Cushman & Wakefield (cushmanwakefield.com) — LA office and industrial marketbeats
- Bisnow (bisnow.com) — LA capital markets news, SoCal industrial investment activity

**Where it lives:**
- `knowledge/raw/` — 20 markdown files, one per article, with title, URL, and full text
- `RAW.SCRAPE_ARTICLES` — same content loaded to Snowflake for pipeline completeness
- `knowledge/wiki/` — Claude Code-synthesized pages that compound insights across sources *(coming Milestone 02)*

**Highlight sources:**

| File | Content | Why it matters |
|---|---|---|
| JLL US Office Market Dynamics Q1 2026 | National office leasing, absorption, delinquency | JLL's own research on the market they operate in |
| CBRE US Real Estate Market Outlook 2026 | Sector-by-sector forecasts for all property types | Cross-sector view matching REIT data coverage |
| Cushman LA Office Marketbeat Q2 2025 | Submarket vacancy, key deals, rent data for Greater LA | Directly covers the market where the JLL role is located |
| Cushman LA Industrial Marketbeat Q1–Q3 2025 | Three consecutive quarters of LA industrial data | Matches Prologis/STAG industrial REIT data |
| Bisnow: LA Commercial Sales Bounce Back 2025 | Capital markets recovery story in LA | Local market narrative layer |
| Bisnow: SoCal Industrial $1.2B in Sales Q4 2025 | Deal volume, investor sentiment for LA industrial | Corroborates industrial REIT outperformance |

**Why this source:** The structured sources answer quantitative questions. The scraped research answers qualitative ones: What are analysts saying about the LA market? What is JLL advising clients? What sectors are recovering and why? This content is not reducible to numbers — it requires reading and synthesis. Claude Code acts as the query engine against this knowledge base in the interview demo.

---

### Questions the Knowledge Base Answers

- What is JLL's current outlook on office leasing and absorption in the US?
- What is the state of the Greater Los Angeles office market — vacancy, net absorption, key deals?
- How has the LA industrial market performed across Q1–Q3 2025?
- What are CBRE's sector-by-sector forecasts for office, industrial, retail, and multifamily in 2026?
- How are analysts characterizing the capital markets recovery in LA?

---

## How the Sources Work Together

| Insight Type | Source | Example |
|---|---|---|
| Descriptive | REIT daily prices | Office REIT prices are down 35% since Jan 2022 |
| Descriptive | REIT quarterly financials | Industrial REIT revenue grew 28% from 2020–2024 |
| Diagnostic | REIT + FRED | Fed Funds Rate 0% → 5.3% (FRED) correlates with 35% REIT price drop (yfinance) |
| Diagnostic | REIT financials | Office revenue declining alongside stock price — real business deterioration, not sentiment |
| Geographic | BLS metro employment | LA Financial Activities employment down YoY → local office demand weakness |
| Qualitative | Scraped research | JLL and CBRE both project continued office market softness through 2026 |
