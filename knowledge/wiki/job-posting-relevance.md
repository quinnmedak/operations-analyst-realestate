# Job Posting Relevance

**Role:** Business Intelligence Analyst — JLL (Rosemead, CA)
**Salary range:** $65,300 – $94,700

This document maps what the project builds to what the job actually requires, and explains who the internal stakeholders are and what they use the data for.

---

## Who the Stakeholders Are

The BI Analyst's immediate "customers" are internal JLL deal teams:

- **Capital markets brokers** — pitch clients on buying, selling, and financing CRE assets. Need market data to explain pricing, defend valuations, and identify opportunities. The broker is the intermediary — they translate data insights into client conversations.
- **Leasing teams** — pitch tenants and landlords on space. Need vacancy and absorption data to tell clients whether they have negotiating leverage.
- **Research teams** — produce market reports and thought leadership. Need cross-sector trends and benchmarks.

The end clients those brokers serve include:

- **Private equity funds** — the dominant buyer in LA CRE right now (61.4% of 2025 deal volume). Hold mixed portfolios, move on conviction before institutional capital, and need data to justify allocation decisions to LPs.
- **Institutional investors** (pension funds, REITs, insurance) — currently on the sidelines at 23.8% of SoCal industrial deals. Re-entry is projected by CBRE in 2026.
- **Corporate occupiers** — tenants making long-term space decisions based on market conditions.
- **Lenders** — evaluating credit risk against CRE loan delinquency trends.

---

## Selected Stakeholder: PE Fund (Slide Deck Target)

For the presentation slides, a **LA-focused private equity fund** was selected as the target stakeholder. This is the client a JLL capital markets broker is most likely sitting across from right now, and it is the stakeholder our data most directly serves.

**Why this stakeholder:**
Private capital drove 61.4% of all LA CRE deals in 2025 — the highest share in a decade. These funds hold mixed portfolios (including office) and face two questions our data answers directly: what to do with underperforming office positions, and where to redeploy capital.

**How the project demonstrates insight delivery to this stakeholder:**

The slide deck (`docs/slides-stakeholder-brief.md`) follows a descriptive → diagnostic → action framework:

1. **Descriptive** — Dashboard data (REIT prices from `FACT_DAILY_PRICES`, vacancy/absorption from `FACT_LA_MARKET_SNAPSHOT`) establishes the office/industrial divergence. Verified stats: industrial REITs up ~160% since 2018, office down ~36%; industrial vacancy 5.4% vs. office 23.6%.

2. **Diagnostic** — API data (`FACT_MACRO_QUARTERLY` FRED series) and wiki sources (CBRE, JLL, Cushman & Wakefield) together explain why: e-commerce permanently shifted industrial demand (+4pp share in 2020, held); rate hikes accelerated office decline but hybrid work is the structural driver (office REIT prices −21% YoY Q1 2026 even as rates eased — verified from `FACT_DAILY_PRICES`).

3. **Action** — A specific, sourced recommendation: rotate ~$150M from office into SoCal industrial. The income upside (44%, $6.97M → $10.02M/year) is grounded in CBRE rent data and a verified calculation chain, not a macro forecast.

---

## How the Dashboard Serves Each Stakeholder

**Capital markets brokers use:**
- REIT price trend by property type → public market comparables before any private-market pricing conversation
- The rate hike story (Panel 4) → explains to clients why their building is worth less today than in 2021, and whether the reset is structural
- Revenue vs. stock price (Panel 5) → backs up buy/hold recommendations with fundamental data, not just price charts
- Deal volume callout ($33B → $37.3B, still below $51.4B 2019 peak) → "the market is recovering but still 27% below peak — a window to buy before full rebound"

**Leasing teams use:**
- LA Office and Industrial vacancy/absorption (Panel 1 + Panel 2) → tells a tenant whether they have leverage or not before entering negotiations
- Absorption trend → the earliest real demand signal; moves before rents or REIT prices react
- LA employment vs. peer cities (Panel 6) → forecasts whether leasing pipeline will convert

**Research teams use:**
- All of the above for market reports
- National vs. LA benchmarks (Panel 3, Panel 6) → cross-market context for reports
- E-commerce vs. industrial (Panel 7) → structural demand driver narrative

---

## How the Project Maps to Job Requirements

### Core requirements

| Requirement | What the project demonstrates |
|---|---|
| Strong SQL skills | All mart queries, FRED pivot, cross-source grain alignment |
| Data warehousing and ETL | Snowflake + dbt staging + mart layers |
| Reports, dashboards, visualizations | Streamlit app, deployed public URL |
| Extract, transform, analyze from multiple sources | yfinance + FRED + BLS + JLL scrape, all in one pipeline |
| Identify trends, patterns, correlations | Rate hike → valuation crash; e-commerce → industrial outperformance |
| Automated reporting systems | GitHub Actions scheduled pipelines |
| Data quality and governance | dbt tests on every fact table PK and FK |
| Metrics definitions and data models | Star schema documented in spec; metrics defined in dbt model descriptions |
| Communicate to technical and non-technical audiences | Dashboard + presentation slides; knowledge base for qualitative layer |

### Preferred qualifications

| Preferred qualification | Status |
|---|---|
| Python | All extractors (yfinance, FRED, BLS, Firecrawl) + Streamlit app |
| Cloud platforms (AWS, Azure, GCP) | Snowflake on AWS |
| Industry-specific knowledge | CRE domain; prior CBRE research internship |
| Data governance and quality | dbt tests, documented metrics, no credentials in repo |

---

## The One Tool Gap

The posting lists Power BI, Tableau, Looker, and QlikView as the expected BI tools. This project uses Streamlit.

**How to frame it:** Streamlit demonstrates Python proficiency (a preferred qualification) and end-to-end pipeline ownership — from raw API data to a deployed web app. The underlying SQL and star schema are tool-agnostic: the same `fact_quarterly_financials` and `dim_reit` tables power any BI tool. In the interview, note this explicitly: "I built the dashboard in Streamlit to keep the full stack in Python, but the mart layer connects directly to Power BI or Tableau — same tables, different query layer."



---

## What This Project Does Not Cover (and Why)

| Gap | Why it's acceptable |
|---|---|
| Submarket-level vacancy (DTLA vs. Westside) | Requires CoStar ($15K+/yr). Acknowledged in README. Knowledge base wiki has submarket narrative from Cushman Q2 2025. |
| Individual deal/transaction data | Not publicly available in structured form. |
| Retail and multifamily deep-dives | Appear in aggregate charts. Wiki pages cover the narrative layer. |
| CoStar-style market analytics | Industry standard is paywalled. This project uses all available free structured sources and is transparent about the limitation. |
