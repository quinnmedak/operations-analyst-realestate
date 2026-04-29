# dbt Star Schema & Streamlit Dashboard Design

**Date:** 2026-04-29
**Project:** BI Analytics Pipeline — Commercial Real Estate
**Target role:** JLL Business Intelligence Analyst (Rosemead, CA)
**Milestone:** 02 — Transform, Present & Polish (due May 4)

---

## Stakeholder & Purpose

**Direct user:** Internal JLL deal teams — capital markets brokers, leasing teams, research teams.
**How they use it:** To pitch clients, win business, and back up recommendations with data.
**End clients served:** PE funds, institutional investors, corporate occupiers, lenders.

The dashboard answers "how much" and "what happened" using structured data. The knowledge base wiki handles qualitative narrative (what analysts are saying). The two are complementary, not redundant.

---

## Data Sources Feeding the Dashboard

Five sources landing in Snowflake `RAW`:

| Source | Raw table(s) | Grain | Notes |
|---|---|---|---|
| yfinance (prices) | `RAW.REIT_DAILY_PRICES` | Daily per REIT | 9 REITs, ~11,300 rows, 5 years |
| yfinance (financials) | `RAW.REIT_QUARTERLY_FINANCIALS` | Quarterly per REIT | ~55 rows |
| FRED REST API | `RAW.FRED_OBSERVATIONS` | Mixed (daily/monthly/quarterly) | Long format, 9 series, 36,904 rows |
| BLS CES API | `RAW.BLS_METRO_EMPLOYMENT` | Monthly per metro + supersector | 8 metros × 2 sectors, 1,184 rows |
| JLL PDF marketbeats | `RAW.JLL_MARKET_STATS` | Quarterly per market | Scraped via Firecrawl + Claude API extraction |

---

## JLL Market Stats Source

**Why it exists:** Absorption and vacancy are the most important real estate metrics — they measure what tenants are actually doing with space, not what investors feel about it. The REIT and FRED sources answer the financial story. JLL market stats answer the physical occupancy story. Leasing teams specifically live by absorption data.

**Why JLL only:** Single source, consistent quarterly format, publicly accessible PDF marketbeats, same metrics reported the same way each quarter. Avoids cross-source formatting inconsistencies.

**Four markets tracked:**
- LA Office
- LA Industrial
- US Office
- US Industrial

**Extraction flow:**
1. GitHub Actions runs quarterly (or manual trigger near quarter-end)
2. Firecrawl targets JLL PDF marketbeat URLs for each market
3. Python extraction script uses Claude API to parse scraped markdown → structured JSON: `{market, property_type, data_quarter, vacancy_rate_pct, net_absorption_sf, asking_rent_psf, leasing_volume_sf, source_url}`
4. Load to `RAW.JLL_MARKET_STATS` (truncate-and-reload)

**Known risk:** JLL's market dynamics pages are JavaScript-rendered — past scrapes returned stubs. PDF marketbeats are more reliably scrapeable. If PDF URLs don't follow a predictable pattern each quarter, the extractor needs updating. Build the panel with hardcoded current-quarter values first, automate second. Do not let this block dashboard deployment.

**Raw schema:**
```
RAW.JLL_MARKET_STATS
  market              VARCHAR    -- 'LA Office', 'LA Industrial', 'US Office', 'US Industrial'
  property_type       VARCHAR    -- 'Office', 'Industrial'
  geography           VARCHAR    -- 'Los Angeles', 'National'
  data_quarter        VARCHAR    -- 'Q1 2026', 'Q4 2025', etc.
  vacancy_rate_pct    FLOAT
  net_absorption_sf   FLOAT      -- negative = net move-out
  asking_rent_psf     FLOAT
  leasing_volume_sf   FLOAT
  source_url          VARCHAR
  scraped_at          TIMESTAMP
```

---

## dbt Layer Design

### Schemas

```
SNOWFLAKE_DATABASE.RAW        -- raw tables (populated by extractors)
SNOWFLAKE_DATABASE.ANALYTICS  -- all dbt output: staging/ and marts/
```

### Staging Layer — views, rename and cast only, no business logic

| Model | Source | Key transformations |
|---|---|---|
| `stg_reit_daily_prices` | `RAW.REIT_DAILY_PRICES` | Cast date to DATE, float cast price columns |
| `stg_reit_quarterly_financials` | `RAW.REIT_QUARTERLY_FINANCIALS` | Cast quarter columns, standardize ticker |
| `stg_fred_observations` | `RAW.FRED_OBSERVATIONS` | Cast date to DATE, cast value to FLOAT |
| `stg_bls_metro_employment` | `RAW.BLS_METRO_EMPLOYMENT` | Parse year + period into DATE, cast employment to FLOAT |
| `stg_jll_market_stats` | `RAW.JLL_MARKET_STATS` | Parse data_quarter to DATE (quarter start), cast numeric columns |

### Mart Layer — tables, business logic, star schema

#### Dimensions

**`dim_reit`** — seed file, 9 rows, never changes
```
reit_key        INT (surrogate PK)
reit_ticker     VARCHAR   -- BXP, SLG, VNO, PLD, STAG, SPG, EQR, AVB, ARE
company_name    VARCHAR
property_type   VARCHAR   -- Office, Industrial, Retail, Multifamily, Life Sciences
primary_market  VARCHAR
```

**`dim_date`** — standard date spine
```
date_key        INT (YYYYMMDD)
date            DATE
year            INT
quarter         INT
year_quarter    VARCHAR   -- 'Q1 2026'
month_number    INT
month_name      VARCHAR
is_trading_day  BOOLEAN
```

**`dim_metro`** — seed file, 8 rows
```
metro_key       INT (surrogate PK)
metro           VARCHAR   -- 'Los Angeles', 'New York', etc.
cbsa_code       VARCHAR
state           VARCHAR
why_included    VARCHAR   -- context note
```

**`dim_market`** — seed file, 4 rows
```
market_key      INT (surrogate PK)
market          VARCHAR   -- 'LA Office', 'LA Industrial', 'US Office', 'US Industrial'
property_type   VARCHAR
geography       VARCHAR
```

#### Facts

**`fact_daily_prices`** — one row per REIT per trading day
```
price_key       INT (surrogate PK)
reit_key        INT (FK → dim_reit)
date_key        INT (FK → dim_date)
open            FLOAT
high            FLOAT
low             FLOAT
close           FLOAT
volume          FLOAT
dividends       FLOAT
```

**`fact_quarterly_financials`** — one row per REIT per quarter
```
financial_key       INT (surrogate PK)
reit_key            INT (FK → dim_reit)
date_key            INT (FK → dim_date, quarter-start)
year_quarter        VARCHAR
total_revenue       FLOAT
net_income          FLOAT
ebitda              FLOAT
operating_income    FLOAT
total_assets        FLOAT
total_debt          FLOAT
net_debt            FLOAT
long_term_debt      FLOAT
```

**`fact_macro_quarterly`** — FRED series pivoted wide, one row per quarter
```
macro_key       INT (surrogate PK)
date_key        INT (FK → dim_date, quarter-start)
year_quarter    VARCHAR
MORTGAGE30US    FLOAT   -- 30-yr mortgage rate, quarterly avg
DGS10           FLOAT   -- 10-yr Treasury yield, quarterly avg
FEDFUNDS        FLOAT   -- Fed Funds Rate, quarterly avg
T10Y2Y          FLOAT   -- yield curve spread, quarterly avg
UNRATE          FLOAT   -- unemployment rate, quarter-end
PAYEMS          FLOAT   -- nonfarm payrolls (thousands), quarter-end
ECOMPCTNSA      FLOAT   -- e-commerce % of retail sales, quarterly direct
DRCRELEXFACBS   FLOAT   -- CRE loan delinquency rate, quarterly direct
CREACBW027SBOG  FLOAT   -- CRE loans outstanding, quarterly avg
```
Built with CASE WHEN pivot aggregation in dbt. Daily/monthly series averaged to quarter.

**`fact_metro_employment`** — one row per metro per supersector per month
```
employment_key          INT (surrogate PK)
metro_key               INT (FK → dim_metro)
date_key                INT (FK → dim_date)
supersector             VARCHAR   -- 'Financial Activities', 'Professional & Business Services'
employment_thousands    FLOAT
```

**`fact_market_stats`** — JLL vacancy and absorption, one row per market per quarter
```
market_stat_key     INT (surrogate PK)
market_key          INT (FK → dim_market)
date_key            INT (FK → dim_date, quarter-start)
year_quarter        VARCHAR
vacancy_rate_pct    FLOAT
net_absorption_sf   FLOAT
asking_rent_psf     FLOAT
leasing_volume_sf   FLOAT
```

#### Helper model

**`fct_reit_quarterly_prices`** — daily prices aggregated to quarterly grain
```
reit_key              INT (FK → dim_reit)
date_key              INT (FK → dim_date, quarter-start)
year_quarter          VARCHAR
quarter_end_close     FLOAT   -- close price on last trading day of quarter
quarterly_avg_close   FLOAT   -- avg close across all trading days in quarter
```
Required for any chart that joins REIT prices against quarterly macro or financial data.

---

## Dashboard Design

**Layout:** Wide mode. Sidebar: global date range filter + sector selector. Content top to bottom.

---

### Panel 1 — Market Fundamentals

Two rows of metric cards. Always shows the most recent data point.

**Row 1 — Real estate occupancy (from `fact_market_stats`)**

| Card | Metric | Who uses it |
|---|---|---|
| LA Office Vacancy | Latest vacancy_rate_pct, market = 'LA Office' | Leasing teams briefing office tenants |
| LA Industrial Vacancy | Latest vacancy_rate_pct, market = 'LA Industrial' | Leasing teams briefing industrial users |
| LA Office Net Absorption | Latest net_absorption_sf, market = 'LA Office' | Leasing + capital markets: is demand recovering? |
| LA Industrial Net Absorption | Latest net_absorption_sf, market = 'LA Industrial' | Same — positive = tenants moving in |

**Row 2 — Financial and macro (from `fact_daily_prices`, `fact_macro_quarterly`)**

| Card | Metric | Who uses it |
|---|---|---|
| Office REIT Price | Avg close, BXP + SLG + VNO | Capital markets brokers: public market signal |
| Industrial REIT Price | Avg close, PLD + STAG | Capital markets brokers: sector comparison |
| 10-Year Treasury | Latest DGS10 | Everyone: the rate environment |
| CRE Delinquency | Latest DRCRELEXFACBS | Capital markets: loan stress context |

**Row 3 — Deal volume callout (hardcoded from Bisnow data)**

A simple three-number trend bar: LA CRE sales volume 2023 ($35B) → 2024 ($33B) → 2025 ($37.3B), with note that 2019 peak was $51.4B.
Capital markets brokers use this to tell clients: "the market is recovering but still 27% below peak — still a window to buy before full recovery."
Source: MSCI via Bisnow. Hardcoded — no automated source exists for this without CoStar.

---

### Panel 2 — Absorption & Vacancy Trend

**Chart:** Line chart — net absorption by market over time, one line per market (LA Office, LA Industrial, US Office, US Industrial). Second chart in same panel: vacancy rate trend.

**Source:** `fact_market_stats` JOIN `dim_market` JOIN `dim_date`

**Filters:** Market multi-select, date range

**Business question:** *Is the market recovering? Absorption turning positive is the earliest real demand signal — it moves before rents do, before REIT prices react. Leasing teams use this to tell a tenant whether they have negotiating leverage.*

---

### Panel 3 — REIT Price Trend by Property Type

**Chart:** Line chart — avg close price by property_type over time.

**Source:** `fact_daily_prices` JOIN `dim_reit` JOIN `dim_date`

**Filters:** Sector selector, date range

**Business question:** *How have CRE valuations moved by sector across 5 years? Office peak, crash, partial recovery vs. industrial consistent outperformance. Capital markets brokers use this as public-market context before any private-market pricing conversation.*

---

### Panel 4 — The Rate Hike Story

**Chart:** Dual-axis line — Fed Funds Rate (left axis) vs. avg Office REIT close price (right axis). 2020–present.

**Source:** `fact_macro_quarterly` + `fct_reit_quarterly_prices` JOIN `dim_reit` (Office) JOIN `dim_date`

**Business question:** *Why did office valuations crash 35–40% from 2021–2024? The mechanism is visible: Fed Funds 0% → 5.3% compressed cap rates and froze debt markets. This is the chart a capital markets broker shows a client to explain why their building is worth less today than it was in 2021, and why the reset is structural rather than temporary.*

---

### Panel 5 — Revenue vs. Stock Price

**Chart:** Two lines — avg quarterly revenue (left axis) + avg quarterly close price (right axis) for selected property type. Sector toggle: Office / Industrial.

**Source:** `fact_quarterly_financials` + `fct_reit_quarterly_prices` JOIN `dim_reit` JOIN `dim_date`

**Business question:** *Is the decline a real business problem or investor sentiment? If both revenue and price fall together, tenants are genuinely leaving. If price falls but revenue holds, the market overshot. For Industrial: revenue grew while prices briefly dipped — proof that the sell-off was sentiment, not fundamentals. Capital markets brokers use this to back up buy/hold recommendations.*

---

### Panel 6 — LA Employment in Office-Using Sectors

**Chart:** Multi-line — Professional & Business Services + Financial Activities employment for LA and peer metros over time.

**Source:** `fact_metro_employment` JOIN `dim_metro` JOIN `dim_date`

**Filters:** Metro multi-select (default: LA + NYC + SF + Dallas), supersector toggle, date range

**Business question:** *Is LA's office problem local or national? Employment in office-using industries leads absorption by one to two quarters — it's the earliest demand signal available. Leasing teams use this to forecast whether their pipeline will convert. Research teams use it for market reports.*

---

### Panel 7 — E-Commerce as Industrial Demand Driver

**Chart:** Dual-axis line — e-commerce as % of retail sales (`ECOMPCTNSA`) vs. avg Industrial REIT quarterly revenue.

**Source:** `fact_macro_quarterly` + `fact_quarterly_financials` JOIN `dim_reit` (Industrial) JOIN `dim_date`

**Business question:** *What is structurally driving industrial outperformance? E-commerce share held at 13–18% post-COVID vs. 11% pre-COVID — a permanent step-change that sustains warehouse and logistics demand. Capital markets brokers use this to explain industrial's investment thesis to clients considering a sector rotation out of office into industrial.*

---

## SQL Notes

**Grain alignment:** Never join daily-grain to quarterly-grain directly. Use `fct_reit_quarterly_prices` for all cross-source charts. All cross-source joins go through `dim_date.year_quarter`.

**FRED pivot:** `stg_fred_observations` is long format (series_id, date, value). `fact_macro_quarterly` pivots wide using CASE WHEN aggregation grouped by year_quarter. Built once; all charts reference columns by name (`m.FEDFUNDS`, `m.ECOMPCTNSA`).

**Example cross-source query (Panel 4):**
```sql
SELECT
  d.year_quarter,
  m.FEDFUNDS,
  AVG(q.quarterly_avg_close) AS avg_office_reit_price
FROM fct_reit_quarterly_prices q
JOIN dim_reit r       ON q.reit_key = r.reit_key
JOIN dim_date d       ON q.date_key = d.date_key
JOIN fact_macro_quarterly m ON d.year_quarter = m.year_quarter
WHERE r.property_type = 'Office'
GROUP BY 1, 2
ORDER BY 1
```

---

## dbt Tests

- `unique` + `not_null` on each fact table surrogate key
- `not_null` on all FK columns
- `accepted_values` on `dim_reit.property_type`
- `accepted_values` on `dim_metro.metro` (8 expected values)
- Row count assertion: `fact_daily_prices` should have ~11,300 rows

---

## Deployment

- dbt runs via GitHub Actions after extract + load steps complete
- Streamlit deployed to Streamlit Community Cloud, public URL
- All Snowflake credentials in `.env` locally; Streamlit Cloud secrets panel for deployment
- Cache all Snowflake queries: `@st.cache_data(ttl=3600)`
- Python version: snowflake-snowpark-python requires ≤ 3.11; Claude Code will install via pyenv if needed

---

## What Is NOT in This Dashboard

- Qualitative market narrative → knowledge base wiki, queryable via Claude Code in interview demo
- Submarket-level breakdowns (DTLA vs. Westside) → wiki pages; requires CoStar for structured data
- Individual deal/transaction data → not in any raw source
- Retail and multifamily deep-dives → appear in aggregate charts; dedicated sections not in scope for May 4

---

## Open Questions Before Implementation

1. **JLL PDF URL pattern** — confirm quarterly marketbeat PDFs follow a predictable URL pattern before writing the extractor. If not, scrape the market dynamics HTML pages directly. If that also fails, hardcode Panel 1 vacancy/absorption numbers from current wiki data and mark as static.
2. **FRED series grain decision** — `DGS10` and `T10Y2Y` are daily. Use quarterly average (smoother, better for trend charts) in `fact_macro_quarterly`.
3. **Deal volume callout** — hardcoded from Bisnow data in the knowledge base. Not automated. Document the source explicitly.
