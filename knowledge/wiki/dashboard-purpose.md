# Dashboard Purpose & Panel Guide

## What the Dashboard Does

Answers three questions in sequence, matching the descriptive → diagnostic → actionable framework from the project requirements:

1. **What is the current state of the LA CRE market?** (Descriptive)
2. **Why did office and industrial diverge?** (Diagnostic)
3. **What is the credit backdrop and where is the market headed?** (Context + Outlook)

All charts read live from Snowflake — REIT prices update daily via yfinance, macro indicators and employment update monthly via FRED and BLS.

---

## Section 1: Current State — Descriptive

### Financial Signals KPI Cards

**Question:** How are commercial real estate sectors priced today, and what does the current rate and lending environment look like?

| Card | What it shows | Source |
|---|---|---|
| Office REIT Avg Price | Sector valuation snapshot — daily close averaged across office REITs | `FACT_DAILY_PRICES` (yfinance, daily) |
| Industrial REIT Avg Price | Same for industrial | `FACT_DAILY_PRICES` (yfinance, daily) |
| Fed Funds Rate | The rate environment shaping CRE valuations and deal volume | `FACT_MACRO_QUARTERLY` (FRED FEDFUNDS) |
| CRE Loan Delinquency | Health of CRE lending | `FACT_MACRO_QUARTERLY` (FRED DRCRELEXFACBS) |

### Space Market KPI Cards

**Question:** How much space is vacant across property types, and are tenants taking on more or less space?

| Card | What it shows |
|---|---|
| Office Vacancy | 23.6% Q1 2026 — rising YOY. Move-outs still outpacing leasing. |
| Industrial Vacancy | 5.4% Q1 2026 — tight relative to 7.5% national avg. |
| Office YTD Absorption | Negative — confirming continued structural decline. |
| Industrial YTD Absorption | +934K SF Q1 2026 — first positive quarter since 2022. |

Source: Cushman & Wakefield Q1 2026 (Office), CBRE Q1 2026 (Industrial) seeded into `FACT_LA_MARKET_SNAPSHOT`. Static seed — does not auto-update; must be manually updated each quarter when new MarketBeat reports are published.

### Submarket Breakdown (Expander)

**Question:** Which LA submarkets are performing differently, and where is the market tightest or most stressed?

Drills into vacancy, absorption, and asking rent by submarket for the most recent period per property type. The key insight: LA West — the lone office bright spot through Q2 2025 — turned sharply negative in Q1 2026 at -545K SF, signaling the office decline has broadened to the Westside.

---

## Section 2: Market Performance — Descriptive

### Office vs. Industrial REIT Price Performance

**Question:** How have investors priced different property types over time, and which sectors are they most confident in?

Industrial REITs up ~160% from the 2018 baseline; office down ~36%. The divergence began before COVID and has not reversed despite rate easing. This is the headline descriptive chart — it shows *what happened* to prices without yet explaining why.

Fixed at 2018 to show the full pre/post-COVID arc. Updates daily from `FACT_DAILY_PRICES`.

---

## Section 3: The Drivers — Diagnostic

### E-Commerce Share of Retail Sales vs. Industrial REIT Performance

**Question:** What has driven demand for industrial real estate, and is that demand durable or cyclical?

E-commerce share of retail jumped from ~11% to ~16% post-COVID and held — a permanent shift in how goods move. This created durable warehouse demand that absorbed a temporary spec oversupply correction (2022–2024). The dual-axis chart shows industrial REIT prices tracked the e-commerce structural shift, not just a cyclical build wave.

Data: FRED ECOMPCTNSA (4Q rolling avg) + `FACT_DAILY_PRICES` (quarterly). Both live from Snowflake.

### Fed Rate Hike Cycle and Office REIT Valuations

**Question:** How did the interest rate cycle affect office valuations, and did office recover when rates came down?

The 2022–2023 rate hike cycle hit CRE valuations broadly. But when rates eased in 2024–2025, industrial recovered and office did not. That divergence — rates down, office still down — is the diagnostic signal: office faces structural demand loss from hybrid work, not a rate cycle that will self-correct when the Fed cuts.

Fixed at 2020 baseline to preserve the pre-hike index point. Annotations ("Fed begins hiking", "Rate peak: 5.33%", "Rates ease — office stays down") are hardcoded to the 2022–2024 rate cycle — accurate for this project period. Data: FRED FEDFUNDS + `FACT_DAILY_PRICES` (quarterly).

---

## Section 4: Credit Environment — Context

### CRE Loan Delinquency Rate

**Question:** How does current CRE loan stress compare to historical downturns, and does it signal a systemic problem?

Delinquency is rising but remains well below the 2010 GFC peak. This chart contextualizes the stress: elevated, not systemic. It is *not* a driver of the office/industrial divergence — it is background context for investors evaluating credit risk in the current market. The sidebar slider lets viewers zoom in on recent quarters or pull back to benchmark against prior downturns.

The GFC peak annotation and current-level annotation locate the actual max and latest values dynamically — they update as new FRED data comes in. Data: FRED DRCRELEXFACBS via `FACT_MACRO_QUARTERLY`, updated monthly.

---

## Section 5: Outlook — Forward-Looking

### Office-Using Sector Employment: LA vs. Peer Cities

**Question:** How is employment in office-using industries growing in LA compared to other major markets, and what does that imply for future leasing demand?

Employment in Financial Activities + Professional & Business Services is the most reliable leading indicator for office leasing. LA's office-using employment has been flat since 2020 while Dallas is up ~20%. When LA's line turns upward, leasing demand typically follows in 6–18 months.

The interactive multiselect lets viewers benchmark LA against any metro in the BLS dataset. This is the most forward-looking panel in the dashboard — it tells you what to watch, not just what happened.

Data: BLS Metro Employment via `FACT_METRO_EMPLOYMENT`, updated monthly.

---

## Project Requirements Mapping

| Requirement | Panel |
|---|---|
| Descriptive analytics (what happened?) | KPI cards, Space Market snapshot, REIT Price Trend |
| Diagnostic analytics (why did it happen?) | E-Commerce chart, Rate Hike chart |
| Interactive element | Sidebar slider (delinquency start year), Metro multiselect (employment) |
| Deployed public URL | https://commercial-real-estate-analytics.streamlit.app/ |

---

## What Updates Automatically vs. What Requires Manual Refresh

| Panel | Updates | How |
|---|---|---|
| Financial Signals KPI cards | Daily (REIT) / Monthly (macro) | Automated pipeline |
| Space Market KPIs + submarket breakdown | Manual — each new quarter | Re-run `dbt seed` with updated `la_marketbeat.csv` |
| REIT Price Trend | Daily | Automated pipeline |
| E-Commerce chart | Monthly | Automated pipeline (FRED) |
| Rate Hike chart | Monthly | Automated pipeline (FRED) |
| Delinquency chart | Monthly | Automated pipeline (FRED) |
| Employment chart | Monthly | Automated pipeline (BLS) |
