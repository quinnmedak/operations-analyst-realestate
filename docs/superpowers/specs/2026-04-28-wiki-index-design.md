# Wiki & Knowledge Base Design Spec

**Date:** 2026-04-28
**Project:** BI Analytics Pipeline — Commercial Real Estate
**Target role:** JLL Operations Analyst (Rosemead, CA)

---

## Purpose

A Claude Code-queryable knowledge base synthesizing scraped CRE market research. Primary use case: a JLL Operations Analyst prepares market briefings for their director before client meetings. The knowledge base answers general CRE market intelligence questions — not pre-packaged for one client type, but structured so any query from any direction (PE investor, occupier, lender) can be answered.

---

## Stakeholder

**Direct:** JLL Operations Analyst → their director (internal)
**End beneficiary:** JLL clients — PE funds, institutional investors, corporate occupiers, lenders

Demo scenario: "I'm a JLL Operations Analyst. My director needs to brief a client on LA CRE market conditions. I'm going to use the knowledge base to pull the key points."

---

## Source Inventory

27 raw files in `knowledge/raw/` from 4+ sources:

- **JLL** — US Office Q1 2026, US Industrial Q1 2026, LA Office Q1 2026 (stub), LA Industrial Q1 2026 (stub), LA Retail Q2 2025, Life Sciences Outlook, Lab Market Newsroom, Industrial Tenant Demand Study, US Retail Q4 2025, Global Real Estate Perspective Feb 2026
- **CBRE** — US Market Outlook 2026, Capital Markets Outlook 2026, Cap Rate Survey H1 2025, Cap Rate Survey H2 2025, Multifamily Outlook 2026, Retail Outlook 2026
- **Cushman & Wakefield** — LA Office Q2 2025 (full submarket table), LA Industrial Q1/Q2/Q3 2025, national office/industrial/retail context
- **Bisnow** — LA Capital Markets rebound, SoCal Industrial Q4 2025, Canvas Worldwide El Segundo, Sunset Media Center Hollywood, Reframe Studios adaptive reuse

---

## Wiki Structure

**Organization:** Sector-first. One page per topic, each synthesizing across multiple sources. LA-specific data and national context are integrated within each page, not separated.

**9 total pages** built in two rounds:

### Round 1 — This session (7 pages)


| Page                               | Slug                       | Primary sources                                                                                                    | Key questions answered                                                                                                      |
| ---------------------------------- | -------------------------- | ------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------- |
| LA Office Market                   | `la-office-market.md`      | Cushman LA Q2 2025, JLL LA Office Q1 2026 stub, Bisnow Sunset Media Center                                         | Vacancy by submarket, absorption, rent, key deals, DTLA vs Westside bifurcation, 14M SF 2025 leasing high                   |
| LA Industrial Market               | `la-industrial-market.md`  | Cushman LA Industrial Q1–Q3 2025, JLL LA Industrial Q1 2026 stub, Bisnow SoCal Industrial                          | Three-quarter submarket trend, South Bay aerospace/logistics, Central LA (Amazon), rent trajectory                          |
| LA Retail & Multifamily            | `la-retail-multifamily.md` | JLL LA Retail Q2 2025, JLL US Retail Q4 2025, CBRE Retail 2026, CBRE Multifamily 2026                              | Retail evolution in LA, grocery/discount demand, national multifamily supply glut (LA multifamily data noted as thin)       |
| National CRE Trends                | `national-cre-trends.md`   | JLL US Office Q1 2026, JLL US Industrial Q1 2026, JLL Global Perspective Feb 2026, C&W national, CBRE 2026 Outlook | How LA fits the national picture, which sectors are leading vs lagging recovery, global benchmarks                          |
| Capital Markets & Investment       | `capital-markets.md`       | CBRE Cap Rate H1/H2 2025, CBRE 2026 Capital Markets Outlook, Bisnow LA capital markets, JLL Global Perspective     | Cap rate trends, deal volume, LA recovery ($37B in 2025), investor types, value-add thesis                                  |
| Macro Environment & Demand Drivers | `macro-environment.md`     | CBRE 2026 Outlook, Bisnow LA capital markets, JLL Global Perspective, C&W national                                 | Rate hike cycle and REIT valuations, e-commerce as industrial driver, employment → office demand, 2026 outlook              |
| Life Sciences                      | `life-sciences.md`         | JLL Life Sciences Outlook, JLL Lab Market Newsroom                                                                 | Lab/R&D market nationally, 61M SF available, AI reshaping space requirements, LA ranked 3rd in AI life sciences integration |


### Round 2 — Next session (2 pages)


| Page                   | Slug                     | Primary sources                                                                                  | Key questions answered                                                                                                                  |
| ---------------------- | ------------------------ | ------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------- |
| Overview: JLL & LA CRE | `overview.md`            | JLL Global Perspective (company profile), CBRE 2026 Outlook, JLL US Office/Industrial            | What is JLL, what does it do, what is this knowledge base, LA market in context, JLL Property Clock positioning                         |
| LA Tenant Landscape    | `la-tenant-landscape.md` | Bisnow El Segundo, Bisnow Sunset Media Center, Bisnow Reframe Studios, Cushman LA Office Q2 2025 | Who is leasing LA office/industrial, entertainment/media in Hollywood & El Segundo, financial/legal in DTLA, 3PL/aerospace in South Bay |


---

## index.md Structure

Lists all wiki pages with:

- One-line summary
- Key questions it answers
- Primary sources used

Updated in both rounds as pages are added. Living document — update whenever a page is added, renamed, or significantly revised.

---

## Relationship to Dashboard

Wiki and dashboard tell the same story from different angles:

- **Wiki:** What analysts are saying, qualitative context, industry narrative
- **Dashboard:** REIT stock/financials, FRED macro series, BLS metro employment — quantitative

Wiki pages can reference dashboard themes (e.g., "see dashboard for rate vs. REIT price correlation") but do not replicate quantitative data. API sources (yfinance, FRED, BLS) are NOT in the wiki — they live in Snowflake and surface through Streamlit.

---

## Commit History Plan


| Round | Commit contents                                      | Message                                                 |
| ----- | ---------------------------------------------------- | ------------------------------------------------------- |
| 1a    | All 27 raw files                                     | `knowledge: add initial source set (27 scraped files)`  |
| 1b    | 7 wiki pages + index                                 | `knowledge: add wiki pages for core CRE sectors`        |
| 2     | overview.md + la-tenant-landscape.md + updated index | `knowledge: add overview and LA tenant landscape pages` |


---

## Demo Query Examples

These should be answerable from the wiki in the final interview:

- "What's the current state of the LA industrial market?"
- "Is the LA office market recovering or still declining?"
- "How do rising interest rates affect CRE valuations?"
- "What sectors are analysts most bullish on for 2026?"
- "What's driving investment activity in LA right now?"
- "How does LA's office market compare to other major cities?"
- "What industries are leasing the most space in LA?" *(Round 2)*
- "What does JLL do and what markets do they serve?" *(Round 2)`*

