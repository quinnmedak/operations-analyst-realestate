# Project–Role Alignment

**Role:** Business Intelligence Analyst — JLL (Rosemead, CA)
**Salary range:** $65,300 – $94,700

Maps what this project builds to what the job actually requires, explains who the internal stakeholders are, and frames the one tool gap.

---

## Who the Stakeholders Are

The BI Analyst's immediate "customers" are internal JLL deal teams:

- **Capital markets brokers** — pitch clients on buying, selling, and financing CRE assets. Need market data to explain pricing, defend valuations, and identify opportunities.
- **Leasing teams** — pitch tenants and landlords on space. Need vacancy and absorption data to tell clients whether they have negotiating leverage.
- **Research teams** — produce market reports and thought leadership. Need cross-sector trends and benchmarks.

In practice: you are serving JLL employees who then serve clients. The end clients are PE funds, institutional investors, corporate occupiers, and lenders.

---

## How the Dashboard Serves Each Stakeholder

**Capital markets brokers use:**
- REIT price trend by property type → public market comparables before any private-market pricing conversation
- The rate hike story → explains to clients why their building is worth less today than in 2021, and whether the reset is structural
- Revenue vs. stock price → backs up buy/hold recommendations with fundamental data, not just price charts
- Deal volume callout ($33B → $37.3B, still below $51.4B 2019 peak) → "the market is recovering but still 27% below peak — a window to buy before full rebound"

**Leasing teams use:**
- LA Office and Industrial vacancy/absorption → tells a tenant whether they have leverage or not before entering negotiations
- Absorption trend → the earliest real demand signal; moves before rents or REIT prices react
- LA employment vs. peer cities → forecasts whether leasing pipeline will convert

**Research teams use:**
- All of the above for market reports
- National vs. LA benchmarks → cross-market context for reports
- E-commerce vs. industrial → structural demand driver narrative

---

## How the Project Maps to Job Requirements

### Core requirements

| Requirement | What the project demonstrates |
|---|---|
| Strong SQL skills | All mart queries, FRED pivot, cross-source grain alignment |
| Data warehousing and ETL | Snowflake + dbt staging + mart layers |
| Reports, dashboards, visualizations | Streamlit app, deployed public URL |
| Extract, transform, analyze from multiple sources | yfinance + FRED + BLS + Firecrawl scrape, all in one pipeline |
| Identify trends, patterns, correlations | Rate hike → valuation crash; e-commerce → industrial outperformance |
| Automated reporting systems | GitHub Actions scheduled pipelines |
| Data quality and governance | dbt tests on every fact table PK and FK |
| Metrics definitions and data models | Star schema documented in spec; metrics defined in dbt model descriptions |
| Communicate to technical and non-technical audiences | Dashboard + knowledge base for qualitative layer |

### Preferred qualifications

| Preferred qualification | Status |
|---|---|
| Python | All extractors (yfinance, FRED, BLS, Firecrawl) + Streamlit app |
| Cloud platforms (AWS, Azure, GCP) | Snowflake on AWS |
| Industry-specific knowledge | CRE domain wiki across 10 pages, 27 scraped sources |
| Data governance and quality | dbt tests, documented metrics, no credentials in repo |

---

## The One Tool Gap

The posting lists Power BI, Tableau, Looker, and QlikView as the expected BI tools. This project uses Streamlit.

**How to frame it:** Streamlit demonstrates Python proficiency (a preferred qualification) and end-to-end pipeline ownership — from raw API data to a deployed web app. The underlying SQL and star schema are tool-agnostic: the same `fact_quarterly_financials` and `dim_reit` tables connect directly to Power BI or Tableau — same tables, different query layer.

---

## Most Important Metric Note

**Net absorption is the most important real estate metric on the dashboard**, not REIT stock price. Absorption measures what tenants are actually doing with space — moving in (positive) or moving out (negative). Stock price measures what investors feel. The two diverge frequently and for extended periods.

The vacancy/absorption panel sourced from JLL quarterly marketbeats is the panel most directly useful to leasing teams on a day-to-day basis — the panel that makes this dashboard genuinely useful to JLL employees, not just analytically interesting.

---

## What This Project Does Not Cover (and Why)

| Gap | Why it's acceptable |
|---|---|
| Submarket-level vacancy (DTLA vs. Westside) | Requires CoStar ($15K+/yr). Acknowledged in README. Knowledge base wiki has submarket narrative from Cushman Q2 2025. |
| Individual deal/transaction data | Not publicly available in structured form. |
| Retail and multifamily deep-dives | Appear in aggregate charts. Wiki pages cover the narrative layer. |
| CoStar-style market analytics | Industry standard is paywalled. This project uses all available free structured sources and is transparent about the limitation. |
