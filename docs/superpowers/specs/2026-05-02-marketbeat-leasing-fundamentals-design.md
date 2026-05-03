# Leasing Fundamentals — MarketBeat Section Design
**Date:** 2026-05-02
**Feature:** Add Space Market KPI row and LA Market Fundamentals section to the Streamlit dashboard

---

## Context

The existing dashboard serves a capital markets story (REIT prices, fed funds rate, delinquency). The target role — JLL Business Intelligence Analyst — primarily serves leasing teams, who think in vacancy rates, net absorption, and asking rents. These metrics do not exist in any public API and cannot be pulled from FRED or yfinance. They come from industry MarketBeat reports (Cushman & Wakefield format, same as JLL's own reports).

The goal is to add ground-truth leasing fundamentals to the dashboard so it is useful to both leasing and capital markets stakeholders — without replacing or competing with the existing charts.

---

## Page Layout

The Current State block at the top becomes two labeled rows:

```
─── CURRENT STATE ────────────────────────────────────────────
  Space Market       (Cushman & Wakefield MarketBeat)
  Office Vacancy   Industrial Vacancy   Office Absorption   Industrial Absorption
  24.1% ▲+100bps   4.8% ▲+40bps        -561K SF YTD        +1.6M SF YTD
  YoY              YoY                 12 consec. negative  First positive since 2022

  Financial Signals  (yfinance · FRED via Snowflake)
  Office REIT Price  Industrial REIT Price  Fed Funds Rate  CRE Delinquency

─── MARKET FUNDAMENTALS ──────────────────────────────────────
  └─ Expander: submarket breakdown table (Office Q2 2025 / Industrial Q3 2025)

─── INVESTOR SIGNALS ─────────────────────────────────────────
  Chart 1   REIT price trend by sector
  Chart 6   CRE loan delinquency rate
  Chart 2   Rate hike story (office price vs. fed funds)
  Chart 5   E-commerce vs. industrial

─── OUTLOOK ──────────────────────────────────────────────────
  Chart 4   LA employment vs. peer cities
```

**Why two labeled rows instead of one KPI row:**
The Space Market row (physical market reality) and the Financial Signals row (investor/debt reaction) are two lenses on the same market — cause and effect. A capital markets broker needs vacancy to underwrite NOI; a leasing broker needs REIT prices to understand how motivated sellers are. Neither row is for a separate audience — both are overall market health, just measured differently.

---

## dbt Data Model

### Seed: `seeds/la_marketbeat.csv`

One row per property type (Office, Industrial). Static snapshot data from MarketBeat PDFs already in `knowledge/raw/`.

| column | type | description |
|---|---|---|
| `property_type` | string | `Office` or `Industrial` |
| `period` | string | Display label, e.g. `Q2 2025` |
| `period_date` | date | First day of quarter, e.g. `2025-04-01` |
| `source` | string | `Cushman & Wakefield` |
| `vacancy_rate` | float | Overall vacancy rate (%) |
| `vacancy_rate_bps_qoq` | int | QoQ change in basis points |
| `vacancy_rate_bps_yoy` | int | YoY change in basis points |
| `ytd_net_absorption_sf` | int | YTD net absorption in square feet |
| `absorption_context` | string | Short streak note, e.g. `12th consecutive negative quarter` |
| `asking_rent_psf` | float | Overall avg asking rent ($/SF/month) |
| `asking_rent_type` | string | `Full Service` or `NNN` |

### Staging: `models/staging/stg_la_marketbeat.sql`

- Materialized as view in ANALYTICS schema
- Casts types, passes through all columns
- No joins required

### Mart: `models/mart/fact_la_market_snapshot.sql`

- Materialized as table in ANALYTICS schema
- Selects from `stg_la_marketbeat`
- No joins required — standalone reference table

### Tests (`_mart.yml` additions)

- `not_null` on `property_type`, `period_date`, `vacancy_rate`, `ytd_net_absorption_sf`
- `unique` on `property_type` (one row per sector)

---

## Dashboard Display

### Space Market KPI Row (top of page, above Financial Signals)

Query: `SELECT * FROM ANALYTICS.FACT_LA_MARKET_SNAPSHOT`

4 cards in a single `st.columns(4)` row:
- **Office Vacancy** — `vacancy_rate`% with `▲/▼ +N bps YoY` delta
- **Industrial Vacancy** — same pattern
- **Office Absorption** — `ytd_net_absorption_sf` formatted as SF with `absorption_context` as caption
- **Industrial Absorption** — same pattern

Asking rent is not shown as a top-level card — more useful by submarket in the expander.

### Market Fundamentals Section

Section header only — no repeated cards. Immediately contains:

```python
with st.expander("Submarket breakdown — Office Q2 2025 / Industrial Q3 2025"):
    st.dataframe(office_submarket_df)
    st.dataframe(industrial_submarket_df)
```

Submarket tables are hardcoded `pd.DataFrame` objects (not from Snowflake) — the submarket rows are static and do not warrant their own seed. The totals row in each table matches the seed values exactly.

### Source caption
`"Source: Cushman & Wakefield MarketBeat · Office Q2 2025 · Industrial Q3 2025"`

---

## Submarket Data (hardcoded)

### Office Q2 2025 — key columns to show
Submarket, Vacancy Rate, QTR Net Absorption (SF), YTD Net Absorption (SF), Avg Asking Rent ($/SF/mo)

Rows: Downtown CBD, Downtown Non-CBD, Mid-Wilshire, LA West, LA North, LA South, Tri-Cities, San Gabriel Valley, **LOS ANGELES TOTALS**

### Industrial Q3 2025 — key columns to show
Submarket, Vacancy Rate, QTR Net Absorption (SF), YTD Net Absorption (SF), Avg Asking Rent ($/SF/mo)

Rows: LA North, San Gabriel Valley, Mid-Counties, LA Central, LA West, LA South, **LOS ANGELES TOTALS**

---

## What Is Not In Scope

- Multi-quarter trend charts — the YoY delta and streak context in the seed provide sufficient trend signal without requiring additional data scraping
- Submarket rows in the seed — submarket data is static and does not need to be queryable; only the market totals live in Snowflake
- Chart 3 (Revenue vs. stock price) — separate feature, not part of this spec
