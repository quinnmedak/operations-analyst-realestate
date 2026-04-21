# Project Progress Notes

---

## Session: Apr 21 — Milestone 01 Web Scrape Pipeline

### Done

- Scraped 3 initial sources manually via Claude Code + Firecrawl MCP, saved to `knowledge/raw/`:
  - `01-jll-us-office-market-dynamics-q1-2026.md` — JLL U.S. Office Q1 2026
  - `02-cbre-us-real-estate-market-outlook-2026.md` — CBRE 2026 Market Outlook (all sectors)
  - `03-cushman-wakefield-greater-los-angeles-marketbeats.md` — C&W Greater LA MarketBeats Q1 2026
- Built `extractors/scrape_extract.py` — runs 3 CRE Firecrawl queries, saves markdown to `knowledge/raw/`, loads rows to `RAW.SCRAPE_ARTICLES` in Snowflake
- Added all 7 GitHub Actions secrets (FRED_API_KEY, FIRECRAWL_API_KEY, all Snowflake creds)
- Created `.github/workflows/fred_extract.yml` — scheduled monthly on the 1st, also has manual trigger
- Pushed all of the above to GitHub

### Still Needed (Milestone 01 — due Apr 27)

- [ ] Test `scrape_extract.py` locally — verify Snowflake load works, check `RAW.SCRAPE_ARTICLES`
- [ ] GitHub Actions workflow for scrape extractor (`scrape_extract.yml`)
- [ ] Pipeline diagram in README

---

## Session: Apr 20 — Knowledge Base Strategy

### What the Knowledge Base Is For

The knowledge base answers qualitative questions that the dashboard can't. The dashboard shows the numbers (vacancy rates, mortgage rates, delinquencies). The knowledge base provides the industry narrative behind those numbers — queryable live via Claude Code during the final interview demo.

The two outputs together tell a complete analyst story:
- **Dashboard:** "vacancy rates rose 40% from 2021-2023" (the what)
- **Knowledge base:** "JLL Research attributes this to remote work permanently reducing office demand, especially in secondary markets" (the why/context)

### Questions the Knowledge Base Should Be Able to Answer

These map directly to the FRED diagnostic story (inflation → rate hikes → CRE lending tightened → delinquencies rose → vacancies increased):

1. Why did office vacancies spike specifically? (remote work, lease expirations, demand shifts)
2. Which CRE sectors are most stressed — office vs. industrial vs. retail?
3. What are analysts forecasting for 2024-2025?
4. How is JLL specifically positioning/advising clients in this environment?

### How to Know You Have Enough Data

Scrape with those questions in mind. A JLL Research report on office absorption and remote work → grab it. A report on logistics/industrial that your FRED data doesn't touch → lower priority.

You have enough when you can ask Claude Code one of those questions and get a substantive answer with citations from 2+ different sources. 15 focused on-topic sources beats 40 scattered ones.

**Good scrape targets:** JLL Research (jll.com/research), CBRE Insights, Bisnow, GlobeSt — market reports, press releases, research articles about CRE market conditions.

---

## Session: Apr 19 — FRED Pipeline

## Milestone 01: Extract & Load (due Apr 27)

### Done

**Source 1 — FRED API extractor (`extractors/fred_extract.py`)**
- Calls FRED API for 6 economic series, stores in `RAW.FRED_OBSERVATIONS` (5,183 rows x 3 cols: `SERIES_ID`, `DATE`, `VALUE`)

| Series ID | What it measures | Role in the story |
|---|---|---|
| `CPIAUCSL` | CPI inflation | Root cause — why rates spiked |
| `MORTGAGE30US` | 30-year mortgage rate | Financing cost driver |
| `CRLACBS` | CRE loans at banks | Lending activity |
| `DRCRELEXFACBS` | CRE loan delinquency rate | Market stress signal |
| `RRVRUSQ156N` | Rental vacancy rate | CRE market health outcome |
| `UNRATE` | Unemployment rate | Economic demand context |

**Diagnostic story:** Inflation spiked → Fed raised rates → mortgage rates surged → CRE lending tightened → delinquencies rose → vacancies increased

**Snowflake raw table**
- Database: `OPERATIONS_ANALYST`, Schema: `RAW`, Table: `FRED_OBSERVATIONS`

---

### Still Needed (Milestone 01)

- [ ] GitHub Actions pipeline for FRED extractor
- [ ] Source 2: web scrape extractor → `RAW.SCRAPE_ARTICLES`
- [ ] GitHub Actions pipeline for scrape extractor
- [ ] Pipeline diagram in README
- [ ] Submit repo URL to Brightspace

---

## Milestone 02: Transform, Present & Polish (due May 4)

### Still Needed

- [ ] dbt staging model: `stg_fred_observations`
- [ ] dbt staging model: `stg_scrape_articles`
- [ ] dbt mart: `dim_series` + `fact_observations` (star schema)
- [ ] dbt tests passing
- [ ] Streamlit dashboard (deployed to Streamlit Community Cloud)
- [ ] Knowledge base: 15+ raw sources in `knowledge/raw/`, 3+ wiki pages in `knowledge/wiki/`
- [ ] Presentation slides (PDF)
- [ ] README (pipeline diagram, ERD, insights summary)
- [ ] ERD generated from dbt models

---

## Star Schema Design (for Milestone 02 dbt)

**`fact_observations`** — one row per series per date
| series_id | observation_date | value |

**`dim_series`** — one row per series
| series_id | series_name | units | frequency | category |

Connect on `series_id`.
