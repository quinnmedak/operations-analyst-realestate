# API Pipeline Workflows Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add GitHub Actions workflows to automate `reit_extract.py` (weekly) and `bls_extract.py` (monthly), matching the shape of the existing `fred_extract.yml`.

**Architecture:** Two separate YAML workflow files under `.github/workflows/`, each with `workflow_dispatch` for manual runs and a `cron` schedule. Both inject the same five Snowflake secrets already present in the repo. No new secrets required.

**Tech Stack:** GitHub Actions, Python 3.11, yfinance, BLS public API, snowflake-connector-python

---

## File Structure

| Action | File |
|---|---|
| Create | `.github/workflows/reit_extract.yml` |
| Create | `.github/workflows/bls_extract.yml` |
| Reference (do not modify) | `.github/workflows/fred_extract.yml` |

---

### Task 1: Create `reit_extract.yml`

**Files:**
- Create: `.github/workflows/reit_extract.yml`

> Note: GitHub Actions workflows are YAML infrastructure files, not Python. There are no unit tests to write. The verification step is the manual GitHub Actions run in Task 3.

- [ ] **Step 1: Create the workflow file**

Create `.github/workflows/reit_extract.yml` with this exact content:

```yaml
name: REIT Extract & Load

on:
  schedule:
    - cron: "0 7 * * 1"  # Every Monday at 7am UTC
  workflow_dispatch:

jobs:
  extract:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install yfinance pandas snowflake-connector-python python-dotenv pyarrow

      - name: Run REIT extractor
        env:
          SNOWFLAKE_ACCOUNT: ${{ secrets.SNOWFLAKE_ACCOUNT }}
          SNOWFLAKE_USER: ${{ secrets.SNOWFLAKE_USER }}
          SNOWFLAKE_PASSWORD: ${{ secrets.SNOWFLAKE_PASSWORD }}
          SNOWFLAKE_DATABASE: ${{ secrets.SNOWFLAKE_DATABASE }}
          SNOWFLAKE_WAREHOUSE: ${{ secrets.SNOWFLAKE_WAREHOUSE }}
        run: python extractors/reit_extract.py
```

- [ ] **Step 2: Confirm the file is in the right place**

```bash
ls .github/workflows/
```

Expected output includes: `fred_extract.yml  reit_extract.yml`

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/reit_extract.yml
git commit -m "feat: add REIT extract GitHub Actions workflow (weekly Monday)"
```

---

### Task 2: Create `bls_extract.yml`

**Files:**
- Create: `.github/workflows/bls_extract.yml`

- [ ] **Step 1: Create the workflow file**

Create `.github/workflows/bls_extract.yml` with this exact content:

```yaml
name: BLS Extract & Load

on:
  schedule:
    - cron: "0 7 1 * *"  # 1st of every month at 7am UTC
  workflow_dispatch:

jobs:
  extract:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install requests pandas snowflake-connector-python python-dotenv pyarrow

      - name: Run BLS extractor
        env:
          SNOWFLAKE_ACCOUNT: ${{ secrets.SNOWFLAKE_ACCOUNT }}
          SNOWFLAKE_USER: ${{ secrets.SNOWFLAKE_USER }}
          SNOWFLAKE_PASSWORD: ${{ secrets.SNOWFLAKE_PASSWORD }}
          SNOWFLAKE_DATABASE: ${{ secrets.SNOWFLAKE_DATABASE }}
          SNOWFLAKE_WAREHOUSE: ${{ secrets.SNOWFLAKE_WAREHOUSE }}
        run: python extractors/bls_extract.py
```

- [ ] **Step 2: Confirm the file is in the right place**

```bash
ls .github/workflows/
```

Expected output includes: `bls_extract.yml  fred_extract.yml  reit_extract.yml`

- [ ] **Step 3: Commit and push**

```bash
git add .github/workflows/bls_extract.yml
git commit -m "feat: add BLS extract GitHub Actions workflow (monthly 1st)"
git push
```

---

### Task 3: Verify REIT workflow manually on GitHub

- [ ] **Step 1: Open GitHub Actions tab**

Go to your repo on GitHub → click **Actions** tab → find **REIT Extract & Load** in the left sidebar.

- [ ] **Step 2: Run manually**

Click **Run workflow** → **Run workflow** (green button). Wait for the run to complete (2–4 minutes — yfinance pulls full price history for 9 tickers).

- [ ] **Step 3: Check the logs**

Click into the completed run → click the `extract` job → expand **Run REIT extractor**.

Expected log lines:
```
=== REIT Daily Prices ===
  BXP: fetching price history
  ...
Total rows: [some number > 10000]
Loaded [N] rows to RAW.REIT_DAILY_PRICES

=== REIT Quarterly Financials ===
  BXP: fetching quarterly financials
  ...
Loaded [N] rows to RAW.REIT_QUARTERLY_FINANCIALS
```

Run must finish with a green check. If it fails, read the error in the logs — most common causes: missing secret name (must match exactly), import error (missing pip package).

- [ ] **Step 4: Confirm schedule is registered**

On the **REIT Extract & Load** workflow page, confirm GitHub shows: **"This workflow has a schedule."**

---

### Task 4: Verify BLS workflow manually on GitHub

- [ ] **Step 1: Find the workflow**

GitHub → **Actions** tab → find **BLS Extract & Load** in the left sidebar.

- [ ] **Step 2: Run manually**

Click **Run workflow** → **Run workflow**. Wait for completion (under 1 minute — BLS API is fast).

- [ ] **Step 3: Check the logs**

Click into the run → `extract` job → expand **Run BLS extractor**.

Expected log lines:
```
Fetching 16 BLS CES series (2020–2026)
  Batch 1: [...]
  Got [N] data points
  ...
Total rows: [some number, typically 800–1200]
Loading to Snowflake...
Loaded [N] rows to Snowflake RAW.BLS_METRO_EMPLOYMENT
```

Run must finish with green check.

- [ ] **Step 4: Confirm schedule is registered**

On the **BLS Extract & Load** workflow page, confirm GitHub shows: **"This workflow has a schedule."**

- [ ] **Step 5: Both green — schedules trusted**

Both workflows show green on manual run and display a schedule. Pipeline automation for API sources is complete.
