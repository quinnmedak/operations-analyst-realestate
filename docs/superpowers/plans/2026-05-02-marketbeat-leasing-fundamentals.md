# Leasing Fundamentals — MarketBeat Section Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Space Market KPI row and Market Fundamentals submarket expander to the dashboard, backed by a dbt seed → staging → mart pipeline so all leasing data is SQL-queryable via Snowflake.

**Architecture:** Static MarketBeat snapshot data (Office Q2 2025, Industrial Q3 2025) lives in a dbt seed CSV → staging view → mart table in the ANALYTICS schema. The dashboard queries `FACT_LA_MARKET_SNAPSHOT` the same way it queries all other mart tables. Submarket breakdown rows are hardcoded `pd.DataFrame` objects in `app.py` — static data that does not warrant a full pipeline.

**Tech Stack:** dbt (seed, view, table), Snowflake ANALYTICS schema, Streamlit, pandas

---

## Files

| Action | Path |
|---|---|
| Create | `dbt/cre_analytics/seeds/la_marketbeat.csv` |
| Create | `dbt/cre_analytics/models/staging/stg_la_marketbeat.sql` |
| Create | `dbt/cre_analytics/models/mart/fact_la_market_snapshot.sql` |
| Modify | `dbt/cre_analytics/models/mart/_mart.yml` |
| Modify | `dashboard/app.py` |

---

## Task 1: Create the seed CSV

**Files:**
- Create: `dbt/cre_analytics/seeds/la_marketbeat.csv`

Data sourced from `knowledge/raw/` MarketBeat PDFs already in the repo.
- Office: `knowledge/raw/2026-04-22_13-14-43_assets-cushmanwakefield-com...office-q2-2025...md`
- Industrial: `knowledge/raw/2026-04-22_13-26-54_assets-cushmanwakefield-com...industrial-q32025...md`

- [ ] **Step 1: Create the seed file**

Create `dbt/cre_analytics/seeds/la_marketbeat.csv` with this exact content:

```csv
property_type,period,period_date,source,vacancy_rate,vacancy_rate_bps_qoq,vacancy_rate_bps_yoy,ytd_net_absorption_sf,absorption_context,asking_rent_psf,asking_rent_type
Office,Q2 2025,2025-04-01,Cushman & Wakefield,24.1,10,100,-560688,12th consecutive negative quarter,3.64,Full Service
Industrial,Q3 2025,2025-07-01,Cushman & Wakefield,4.8,10,40,1616617,First positive YTD since 2022,1.34,NNN
```

- [ ] **Step 2: Verify the file parses correctly**

```bash
cd dbt/cre_analytics && dbt seed --select la_marketbeat --full-refresh
```

Expected output:
```
1 of 1 START seed file ANALYTICS.la_marketbeat ................................. [RUN]
1 of 1 OK loaded seed file ANALYTICS.la_marketbeat ............................ [INSERT 2 in Xs]
```

- [ ] **Step 3: Commit**

```bash
git add dbt/cre_analytics/seeds/la_marketbeat.csv
git commit -m "feat: add la_marketbeat seed with Office Q2 2025 and Industrial Q3 2025 data"
```

---

## Task 2: Create the staging model

**Files:**
- Create: `dbt/cre_analytics/models/staging/stg_la_marketbeat.sql`

Seeds are referenced with `{{ ref('seed_name') }}`, not `{{ source(...) }}`. Follow the same `{{ config(materialized='view') }}` pattern as other staging models.

- [ ] **Step 1: Create the staging model**

Create `dbt/cre_analytics/models/staging/stg_la_marketbeat.sql`:

```sql
{{ config(materialized='view') }}

WITH source AS (
    SELECT * FROM {{ ref('la_marketbeat') }}
)

SELECT
    property_type,
    period,
    CAST(period_date AS DATE)          AS period_date,
    source,
    CAST(vacancy_rate AS FLOAT)        AS vacancy_rate,
    CAST(vacancy_rate_bps_qoq AS INT)  AS vacancy_rate_bps_qoq,
    CAST(vacancy_rate_bps_yoy AS INT)  AS vacancy_rate_bps_yoy,
    CAST(ytd_net_absorption_sf AS INT) AS ytd_net_absorption_sf,
    absorption_context,
    CAST(asking_rent_psf AS FLOAT)     AS asking_rent_psf,
    asking_rent_type
FROM source
```

- [ ] **Step 2: Run the staging model**

```bash
cd dbt/cre_analytics && dbt run --select stg_la_marketbeat
```

Expected output:
```
1 of 1 START sql view model ANALYTICS.stg_la_marketbeat ........................ [RUN]
1 of 1 OK created sql view model ANALYTICS.stg_la_marketbeat .................. [CREATE VIEW in Xs]
```

- [ ] **Step 3: Commit**

```bash
git add dbt/cre_analytics/models/staging/stg_la_marketbeat.sql
git commit -m "feat: add stg_la_marketbeat staging view"
```

---

## Task 3: Create the mart model and add dbt tests

**Files:**
- Create: `dbt/cre_analytics/models/mart/fact_la_market_snapshot.sql`
- Modify: `dbt/cre_analytics/models/mart/_mart.yml`

- [ ] **Step 1: Create the mart model**

Create `dbt/cre_analytics/models/mart/fact_la_market_snapshot.sql`:

```sql
WITH stg AS (
    SELECT * FROM {{ ref('stg_la_marketbeat') }}
)

SELECT
    property_type,
    period,
    period_date,
    source,
    vacancy_rate,
    vacancy_rate_bps_qoq,
    vacancy_rate_bps_yoy,
    ytd_net_absorption_sf,
    absorption_context,
    asking_rent_psf,
    asking_rent_type
FROM stg
```

- [ ] **Step 2: Add tests to `_mart.yml`**

Append to the `models:` list in `dbt/cre_analytics/models/mart/_mart.yml`:

```yaml
  - name: fact_la_market_snapshot
    columns:
      - name: property_type
        tests:
          - not_null
          - unique
      - name: period_date
        tests:
          - not_null
      - name: vacancy_rate
        tests:
          - not_null
      - name: ytd_net_absorption_sf
        tests:
          - not_null
```

- [ ] **Step 3: Run the mart model**

```bash
cd dbt/cre_analytics && dbt run --select fact_la_market_snapshot
```

Expected output:
```
1 of 1 START sql table model ANALYTICS.fact_la_market_snapshot ................. [RUN]
1 of 1 OK created sql table model ANALYTICS.fact_la_market_snapshot ........... [CREATE TABLE in Xs]
```

- [ ] **Step 4: Run dbt tests**

```bash
cd dbt/cre_analytics && dbt test --select fact_la_market_snapshot
```

Expected output: 4 tests pass (not_null property_type, unique property_type, not_null period_date, not_null vacancy_rate, not_null ytd_net_absorption_sf).

- [ ] **Step 5: Commit**

```bash
git add dbt/cre_analytics/models/mart/fact_la_market_snapshot.sql dbt/cre_analytics/models/mart/_mart.yml
git commit -m "feat: add fact_la_market_snapshot mart model with dbt tests"
```

---

## Task 4: Add Space Market KPI row to app.py

**Files:**
- Modify: `dashboard/app.py`

The existing `app.py` has one KPI block under a `section-header "Current State"`. This task splits it into two labeled sub-rows: **Space Market** (new, from `FACT_LA_MARKET_SNAPSHOT`) and **Financial Signals** (existing, renamed).

- [ ] **Step 1: Add `.kpi-delta` and `.sub-header` CSS classes**

In the `<style>` block (around line 17), add after the `.kpi-card` rule:

```python
    .kpi-delta {
        font-size: 0.72rem;
        color: #6B7280;
        margin-top: 4px;
    }
    .sub-header {
        font-size: 0.8rem;
        font-weight: 600;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin: 20px 0 6px 0;
    }
```

- [ ] **Step 2: Add the Space Market KPI row**

After the existing `st.markdown('<div class="section-header">Current State</div>', ...)` line and before the existing `try:` block that loads office/industrial REIT prices, insert this block:

```python
st.markdown('<div class="sub-header">Space Market</div>', unsafe_allow_html=True)

try:
    snapshot = run_query("""
        SELECT
            property_type,
            vacancy_rate,
            vacancy_rate_bps_yoy,
            ytd_net_absorption_sf,
            absorption_context
        FROM ANALYTICS.FACT_LA_MARKET_SNAPSHOT
        ORDER BY property_type
    """)

    off = snapshot[snapshot["PROPERTY_TYPE"] == "Office"].iloc[0]
    ind = snapshot[snapshot["PROPERTY_TYPE"] == "Industrial"].iloc[0]

    def fmt_absorption(sf):
        sf = int(sf)
        sign = "+" if sf > 0 else ""
        if abs(sf) >= 1_000_000:
            return f"{sign}{sf / 1_000_000:.1f}M SF YTD"
        return f"{sign}{sf / 1_000:.0f}K SF YTD"

    def fmt_bps(bps):
        bps = int(bps)
        arrow = "▲" if bps > 0 else "▼"
        return f"{arrow} {abs(bps)} bps YoY"

    sm1, sm2, sm3, sm4 = st.columns(4)

    with sm1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Office Vacancy</div>
            <div class="kpi-value">{off['VACANCY_RATE']:.1f}%</div>
            <div class="kpi-delta">{fmt_bps(off['VACANCY_RATE_BPS_YOY'])}</div>
        </div>""", unsafe_allow_html=True)

    with sm2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Industrial Vacancy</div>
            <div class="kpi-value">{ind['VACANCY_RATE']:.1f}%</div>
            <div class="kpi-delta">{fmt_bps(ind['VACANCY_RATE_BPS_YOY'])}</div>
        </div>""", unsafe_allow_html=True)

    with sm3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Office YTD Absorption</div>
            <div class="kpi-value">{fmt_absorption(off['YTD_NET_ABSORPTION_SF'])}</div>
            <div class="kpi-delta">{off['ABSORPTION_CONTEXT']}</div>
        </div>""", unsafe_allow_html=True)

    with sm4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Industrial YTD Absorption</div>
            <div class="kpi-value">{fmt_absorption(ind['YTD_NET_ABSORPTION_SF'])}</div>
            <div class="kpi-delta">{ind['ABSORPTION_CONTEXT']}</div>
        </div>""", unsafe_allow_html=True)

    st.caption("Source: Cushman & Wakefield MarketBeat · Office Q2 2025 · Industrial Q3 2025")

except Exception as e:
    st.error(f"Could not load market snapshot: {e}")
```

- [ ] **Step 3: Add "Financial Signals" sub-label before existing KPI row**

Directly before the existing `try:` block that queries `FACT_DAILY_PRICES` for office/industrial REIT prices, add:

```python
st.markdown('<div class="sub-header">Financial Signals</div>', unsafe_allow_html=True)
```

- [ ] **Step 4: Verify the page loads without error**

```bash
cd dashboard && streamlit run app.py
```

Open `http://localhost:8501`. Confirm:
- "Current State" section header appears
- "Space Market" sub-header with 4 vacancy/absorption cards
- "Financial Signals" sub-header with existing 4 REIT/macro cards
- No errors in the Streamlit UI or terminal

- [ ] **Step 5: Commit**

```bash
git add dashboard/app.py
git commit -m "feat: add Space Market KPI row with vacancy and absorption from FACT_LA_MARKET_SNAPSHOT"
```

---

## Task 5: Add section headers and Market Fundamentals expander

**Files:**
- Modify: `dashboard/app.py`

This task restructures the chart sections with the new layout:
- **Market Fundamentals** — submarket expander (before REIT charts)
- **Investor Signals** — Charts 1, 6, 2, 5
- **Outlook** — Chart 4 (rename from "Actionable — What Comes Next")

- [ ] **Step 1: Add Market Fundamentals section header and submarket expander**

After the Financial Signals KPI row block (after its closing `except` block, before Chart 1), insert:

```python
st.markdown('<div class="section-header">Market Fundamentals</div>', unsafe_allow_html=True)

OFFICE_SUBMARKETS = pd.DataFrame([
    {"Submarket": "Downtown CBD",       "Vacancy": "32.1%", "QTR Absorption (SF)": "-159,430",   "YTD Absorption (SF)": "-289,651",   "Asking Rent ($/SF/mo)": "$3.93"},
    {"Submarket": "Downtown Non-CBD",   "Vacancy": "32.8%", "QTR Absorption (SF)": "-92,286",    "YTD Absorption (SF)": "-176,846",   "Asking Rent ($/SF/mo)": "$3.78"},
    {"Submarket": "Mid-Wilshire",       "Vacancy": "27.1%", "QTR Absorption (SF)": "-23,439",    "YTD Absorption (SF)": "-31,015",    "Asking Rent ($/SF/mo)": "$3.02"},
    {"Submarket": "LA West",            "Vacancy": "24.0%", "QTR Absorption (SF)": "+264,295",   "YTD Absorption (SF)": "+38,735",    "Asking Rent ($/SF/mo)": "$5.14"},
    {"Submarket": "LA North",           "Vacancy": "20.5%", "QTR Absorption (SF)": "+21,586",    "YTD Absorption (SF)": "-149,845",   "Asking Rent ($/SF/mo)": "$2.52"},
    {"Submarket": "LA South",           "Vacancy": "21.4%", "QTR Absorption (SF)": "-169,554",   "YTD Absorption (SF)": "+66,344",    "Asking Rent ($/SF/mo)": "$3.07"},
    {"Submarket": "Tri-Cities",         "Vacancy": "26.1%", "QTR Absorption (SF)": "+2,117",     "YTD Absorption (SF)": "-56,415",    "Asking Rent ($/SF/mo)": "$3.61"},
    {"Submarket": "San Gabriel Valley", "Vacancy": "7.1%",  "QTR Absorption (SF)": "+27,072",    "YTD Absorption (SF)": "+38,005",    "Asking Rent ($/SF/mo)": "$2.51"},
    {"Submarket": "LA TOTALS",          "Vacancy": "24.1%", "QTR Absorption (SF)": "-129,639",   "YTD Absorption (SF)": "-560,688",   "Asking Rent ($/SF/mo)": "$3.64"},
])

INDUSTRIAL_SUBMARKETS = pd.DataFrame([
    {"Submarket": "LA North",           "Vacancy": "4.4%",  "QTR Absorption (SF)": "-1,072,630", "YTD Absorption (SF)": "-959,690",   "Asking Rent ($/SF/mo)": "$1.42"},
    {"Submarket": "San Gabriel Valley", "Vacancy": "3.0%",  "QTR Absorption (SF)": "+778,875",   "YTD Absorption (SF)": "+2,197,197", "Asking Rent ($/SF/mo)": "$1.30"},
    {"Submarket": "Mid-Counties",       "Vacancy": "5.0%",  "QTR Absorption (SF)": "+1,053,460", "YTD Absorption (SF)": "+756,187",   "Asking Rent ($/SF/mo)": "$1.31"},
    {"Submarket": "LA Central",         "Vacancy": "5.1%",  "QTR Absorption (SF)": "+501,542",   "YTD Absorption (SF)": "+1,376,140", "Asking Rent ($/SF/mo)": "$1.15"},
    {"Submarket": "LA West",            "Vacancy": "2.7%",  "QTR Absorption (SF)": "-27,915",    "YTD Absorption (SF)": "+56,568",    "Asking Rent ($/SF/mo)": "$2.38"},
    {"Submarket": "LA South",           "Vacancy": "6.3%",  "QTR Absorption (SF)": "-758,590",   "YTD Absorption (SF)": "-1,809,785", "Asking Rent ($/SF/mo)": "$1.46"},
    {"Submarket": "LA TOTALS",          "Vacancy": "4.8%",  "QTR Absorption (SF)": "+474,742",   "YTD Absorption (SF)": "+1,616,617", "Asking Rent ($/SF/mo)": "$1.34"},
])

with st.expander("Submarket breakdown — Office Q2 2025 / Industrial Q3 2025"):
    st.markdown("**Office — Q2 2025**")
    st.dataframe(OFFICE_SUBMARKETS, hide_index=True, use_container_width=True)
    st.markdown("**Industrial — Q3 2025**")
    st.dataframe(INDUSTRIAL_SUBMARKETS, hide_index=True, use_container_width=True)
    st.caption("Source: Cushman & Wakefield MarketBeat")
```

Note: `import pandas as pd` must be added to the imports block at the top of `app.py` alongside the existing imports — it is not currently there.

- [ ] **Step 2: Add "Investor Signals" section header before Chart 1**

Directly before the Chart 1 `st.markdown("#### How has investor confidence...")` line, insert:

```python
st.markdown('<div class="section-header">Investor Signals</div>', unsafe_allow_html=True)
```

- [ ] **Step 3: Rename "Actionable" header to "Outlook"**

Find and replace this line:

```python
st.markdown('<div class="section-header">Actionable — What Comes Next</div>', unsafe_allow_html=True)
```

With:

```python
st.markdown('<div class="section-header">Outlook</div>', unsafe_allow_html=True)
```

- [ ] **Step 4: Verify full page layout**

```bash
cd dashboard && streamlit run app.py
```

Confirm the page flows as:
1. "Current State" header
2. "Space Market" sub-header → 4 cards (vacancy + absorption)
3. "Financial Signals" sub-header → 4 cards (REIT prices, fed funds, delinquency)
4. "Market Fundamentals" header → closed expander
5. Click expander → Office submarket table, Industrial submarket table
6. "Investor Signals" header → Charts 1, 6, 2, 5
7. "Outlook" header → Chart 4

No errors in UI or terminal.

- [ ] **Step 5: Commit**

```bash
git add dashboard/app.py
git commit -m "feat: add Market Fundamentals expander and restructure dashboard section headers"
```
