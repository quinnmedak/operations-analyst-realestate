# Dashboard Final Design
**Date:** 2026-05-01
**Stakeholder:** JLL Research/Analytics Manager supporting capital markets and leasing teams

---

## The Story

The market split in two. Office fell — rates crushed valuations and tenants genuinely left. Industrial rose — e-commerce created durable demand. The question now is when office recovers, and employment is the earliest signal available.

---

## Descriptive — what is happening

- **KPI Row** — where the market stands right now
- **Chart 1** — how valuations have moved by sector over 5 years; the gap between office and industrial opening up visibly
- **Chart 6** — whether that same gap shows up in actual revenue, not just investor prices

*Story so far: office and industrial have moved in opposite directions, and it shows up in both prices and fundamentals.*

---

## Diagnostic — why it's happening

- **Chart 2** — why office specifically crashed: interest rates went from 0% to 5%, debt got expensive, real estate values fell
- **Chart 3** — whether office's problems are real or fear-driven: did revenue fall with the price, or did investors just panic?
- **Chart 5** — why industrial held up: e-commerce permanently raised demand for warehouse and logistics space

*Story so far: office fell because of rates and genuine occupancy loss. Industrial held because the underlying demand driver — online shopping — didn't go away.*

---

## Actionable — what comes next

- **Chart 4** — employment in office-using sectors tells you whether office demand is recovering before it shows up in leasing numbers. If LA employment is picking up relative to peer cities, the office market will follow.

*Story so far: watch employment to know when office turns.*

---

## Chart Details

| # | Title | Question | Data source | Interactive element |
|---|---|---|---|---|
| KPI Row | Current State | Where does the market stand right now? | FACT_DAILY_PRICES, FACT_MACRO_QUARTERLY | — |
| Chart 1 | REIT Price Trend by Sector | Which property types do investors believe will keep generating income, and which have they lost confidence in? | FACT_DAILY_PRICES, DIM_REIT | Sector selector, date range |
| Chart 2 | Why Did Office Crash? | How did rising interest rates cause office valuations to fall? | FACT_MACRO_QUARTERLY, FACT_DAILY_PRICES | Date range |
| Chart 3 | Real Decline or Investor Fear? | Did office revenue actually fall, or did investors just panic? | FACT_QUARTERLY_FINANCIALS, FACT_DAILY_PRICES | Office / Industrial toggle |
| Chart 4 | LA Employment vs. Peers | Is LA's office demand recovering relative to other cities? | FACT_METRO_EMPLOYMENT | Metro selector |
| Chart 5 | Why Industrial Held Up | How did e-commerce permanently change demand for industrial space? | FACT_MACRO_QUARTERLY, FACT_QUARTERLY_FINANCIALS | Date range |
| Chart 6 | Revenue by Property Type | Does the gap between office and industrial show up in actual business performance, not just stock prices? | FACT_QUARTERLY_FINANCIALS, DIM_REIT | Date range |

---

## Layout

```
Sidebar: date range + sector selector

─── DESCRIPTIVE ──────────────────────────────
KPI Row   (4 metric cards, live from Snowflake)
Chart 1   REIT price trend by sector
Chart 6   Revenue by property type

─── DIAGNOSTIC ───────────────────────────────
Chart 2   Rate hike story
Chart 3   Revenue vs. stock price
Chart 5   E-commerce vs. industrial revenue

─── ACTIONABLE ───────────────────────────────
Chart 4   LA employment vs. peer cities
```

---

## Rubric Check

| Requirement | Status |
|---|---|
| Connected to Snowflake mart tables | KPI row + all charts |
| At least one descriptive view | KPI row, Chart 1, Chart 6 |
| At least one diagnostic view | Charts 2, 3, 5 |
| At least one interactive element | Sector selector, date range, metro selector, toggle |
| Deployed to Streamlit Community Cloud | TBD |
