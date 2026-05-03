# Design: API Pipeline GitHub Actions Workflows

**Date:** 2026-05-02  
**Scope:** Automate `reit_extract.py` and `bls_extract.py` with scheduled GitHub Actions workflows  
**Status:** Approved — ready for implementation

---

## Context

The project already has one automated pipeline: `fred_extract.yml` runs `fred_extract.py` on the 1st of every month. Two API extractors are not yet automated:

- `extractors/reit_extract.py` — pulls REIT daily prices and quarterly financials via yfinance; writes to `RAW.REIT_DAILY_PRICES` and `RAW.REIT_QUARTERLY_FINANCIALS`
- `extractors/bls_extract.py` — pulls metro employment data from the BLS public API; writes to `RAW.BLS_METRO_EMPLOYMENT`

Both scripts already use `os.getenv()` for all credentials — no hardcoded-key refactor is needed.

---

## Design

### Two separate workflow files

Matches the existing `fred_extract.yml` pattern. Each pipeline is independently visible in the GitHub Actions tab, independently retriggerable, and independently debuggable.

**`.github/workflows/reit_extract.yml`**

**`.github/workflows/bls_extract.yml`**

### Triggers

Both workflows use the same trigger pattern:

```yaml
on:
  schedule:
    - cron: "..."   # see cadence below
  workflow_dispatch:   # manual trigger always included
```

`workflow_dispatch` is included on both so the workflow can be run manually from the GitHub Actions tab before trusting the schedule. The tutorial principle: run manually first, verify green, then trust the schedule.

### Cadence

| Workflow | Cron | Rationale |
|---|---|---|
| `reit_extract.yml` | `0 7 * * 1` (Monday 7am UTC) | REIT prices update daily, but weekly is sufficient for a portfolio dashboard. Daily would burn GitHub Actions minutes for marginal freshness gain. Monday captures the full prior week of trading. |
| `bls_extract.yml` | `0 7 1 * *` (1st of month, 7am UTC) | BLS publishes metro employment on the 3rd Friday of the following month. By the 1st, prior month data is already available. Running on the 1st keeps all three macro pipelines (FRED, BLS, REIT monthly) on a predictable same-day cadence. |

### Steps (both workflows follow this shape)

1. `actions/checkout@v4`
2. `actions/setup-python@v5` — Python 3.11
3. Install dependencies via `pip install`
4. Run extractor script with Snowflake secrets injected as environment variables

### Dependencies

| Workflow | pip install |
|---|---|
| `reit_extract.yml` | `yfinance pandas snowflake-connector-python python-dotenv pyarrow` |
| `bls_extract.yml` | `requests pandas snowflake-connector-python python-dotenv pyarrow` |

### Secrets

Both workflows need the same five Snowflake secrets. These already exist in the repo's GitHub Actions secrets from `fred_extract.yml` — no new secrets need to be added.

| Secret name | Used by |
|---|---|
| `SNOWFLAKE_ACCOUNT` | both |
| `SNOWFLAKE_USER` | both |
| `SNOWFLAKE_PASSWORD` | both |
| `SNOWFLAKE_DATABASE` | both |
| `SNOWFLAKE_WAREHOUSE` | both |

No API keys are required. yfinance is free with no authentication. The BLS public API does not require a key for the series used in this project.

### Failure handling

GitHub's built-in Actions failure emails handle notification — no extra workflow steps needed. Ensure GitHub notification settings have Actions failures enabled (repo → Settings → Notifications, or personal account notification preferences).

### Scope boundary

These workflows extract and load to Snowflake RAW only. The mp04 tutorial covers no dbt automation — dbt runs manually when mart tables need refreshing.

---

## Verification steps (post-implementation)

Follow this order exactly — manual green first, then trust the schedule.

1. Push both workflow files to `main`
2. Go to GitHub → **Actions** tab → find `REIT Extract & Load`
3. Click **Run workflow** → wait for green check
4. Check run logs — confirm row count matches a local run
5. Repeat steps 2–4 for `BLS Extract & Load`
6. On each workflow page confirm GitHub shows "This workflow has a schedule"
7. Both green manually → schedules are trusted

---

## Out of scope

- Scrape pipeline automation (Step 10, separate brainstorm)
- dbt automation (not in mp04 tutorial, not required by rubric)
- Slack or webhook failure alerts
