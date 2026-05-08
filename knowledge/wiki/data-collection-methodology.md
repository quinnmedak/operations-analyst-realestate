# Data Collection Methodology

**Last updated:** May 2026
**Scope:** How the 27 raw sources in `knowledge/raw/` were collected — which tool was used for each group and why.

---

## Two Collection Methods

This knowledge base was built using two distinct tools: a Python extraction script (`extractors/scrape_extract.py`) calling the Firecrawl API, and the Firecrawl MCP server used interactively inside Claude Code. The choice between them followed a consistent rule: automation for recurring, predictable collection; MCP for exploration and one-off targeted pulls.

---

## Python Pipeline (`scrape_extract.py`)

**Files:** `04` through `23`, `25`, `26` (21 files)

The Python script calls Firecrawl with a mix of hardcoded direct URLs (C&W quarterly PDF paths, resolved dynamically to the current quarter) and search queries (e.g. "JLL US industrial market dynamics 2025 2026"). Results are written to `knowledge/raw/` with a `YYYY-MM-DD_HH-MM-SS_url-slug.md` filename format and a YAML frontmatter block (`title`, `url`, `scraped_at`). Files were later renamed to the `NN-slug.md` convention during portfolio cleanup.

Three runs produced the bulk of the corpus:

| Run date | How triggered | Files produced |
|---|---|---|
| Apr 22 | Local (two batches) | 04–12 |
| Apr 26 | Local | 13–18 |
| Apr 28 | Local (search queries surfaced Bisnow + JLL global articles) | 19–23 |
| May 4 | GitHub Actions (scheduled) | 25–26 |

**Why Python:** These sources are recurring report types (C&W quarterly PDFs, CBRE outlook pages, JLL market dynamics) that benefit from a reproducible, version-controlled script. The May 4 run was triggered automatically by GitHub Actions with no manual intervention — the correct end state for any source you expect to update on a schedule.

---

## MCP In-Session (Firecrawl MCP in Claude Code)

**Files:** `explore-01`, `explore-02`, `explore-03`, `manual-24`, `manual-27` (5 files)

These files were scraped interactively using the Firecrawl MCP server inside a Claude Code session — one tool call per URL, no code written. They have hand-authored headers and no `scraped_at` YAML frontmatter. The filename prefix reflects the reason each was collected outside the automated pipeline:

### `explore-` prefix (files 01–03)

Collected before `scrape_extract.py` existed, while mapping the domain to understand which sources were worth automating. These were not targeted research pulls — they were orientation: read a JLL national report, a CBRE outlook, and a C&W hub page to understand what firms publish, what format the data takes, and which recurring report types deserved a pipeline entry.

| File | What it is |
|---|---|
| `explore-01-jll-us-office-market-dynamics-q1-2026.md` | JLL US Office Q1 2026 |
| `explore-02-cbre-us-real-estate-market-outlook-2026.md` | CBRE US Outlook 2026 |
| `explore-03-cushman-wakefield-greater-los-angeles-marketbeats.md` | C&W Greater LA hub page |

### `manual-` prefix (files 24 and 27)

PDFs that could not be retrieved by the Python scraper — either gated behind a form, not publicly crawlable, or delivered directly. The MCP server was the only viable collection method for these files.

| File | What it is | Why manual |
|---|---|---|
| `manual-24-jll-la-retail-market-dynamics-q2-2025.md` | JLL LA Retail Q2 2025 (PDF) | PDF not accessible to automated scraper; provided directly |
| `manual-27-cbre-la-industrial-marketbeat-q1-2026.md` | CBRE LA Industrial Q1 2026 (full report) | PDF not accessible to automated scraper; provided directly |

---

## Decision Framework

| Situation | Tool | Why |
|---|---|---|
| Scheduled, automated production pipeline | Python | Fixed response schema, deterministic parameters, easy to version and test |
| Exploring an unfamiliar domain before committing to a pipeline | MCP | One prompt beats 30 lines of code when you do not yet know what to collect |
| Adding known sources you found manually | MCP | Fast, no code to maintain for a handful of URLs |
| Reproducible collection that must run the same way every day | Python | Deterministic, version-controlled, testable |

---

## Automation Design Decisions

These decisions were made implicitly as the pipeline was built rather than planned upfront. Documented here as the reasoning behind what the workflow does.

**Run cadence — quarterly, not monthly**
The scrape workflow runs on the 1st of January, April, July, and October at 7am UTC. That matches the CRE industry publication cycle — C&W, CBRE, and JLL all release their MarketBeat and outlook reports quarterly. Running monthly would mostly pull duplicates. Contrast with FRED and BLS, which run monthly because macro indicators update on a monthly release schedule.

**Manual vs. scheduled triggers**
Both `schedule` and `workflow_dispatch` are enabled. The scheduled run handles routine quarterly corpus refresh. `workflow_dispatch` exists for mid-quarter pulls — a significant Bisnow deal article drops in February, you want it ingested before the next quarterly run. In practice, the bulk of the 27 raw sources were collected via local runs during the build phase; the scheduled trigger is the maintenance mechanism for keeping the corpus current going forward.

**What counts as a successful run**
The git commit step is the implicit success signal: `git diff --cached --quiet || git commit` — it only commits if new files were actually written to `knowledge/raw/`. If Firecrawl returned the same URLs as last quarter and nothing new was scraped, no commit fires. That no-op case is technically not a failure but it is silent — there is no alert if the run completes and produces zero new files.

**What to do on failure**
No explicit handling beyond GitHub Actions' default: if the Python script exits non-zero, the run turns red in the Actions tab. No retry, no notification, no fallback. The `WARNING: no markdown` log messages printed by the extractor do not fail the run — they are informational stdout only. For a portfolio project, manual inspection of the Actions tab after each quarterly run is sufficient.

**Where credentials live**
GitHub Actions secrets injected as environment variables at runtime (`${{ secrets.FIRECRAWL_API_KEY }}` etc.) — never in the workflow YAML or anywhere in the repo. Local development uses a `.env` file listed in `.gitignore`. This pattern is consistent across all four extractors.

---

## How to Identify Which Tool Produced a File

- **Python-generated (`NN-slug`):** YAML frontmatter with `title`, `url`, `scraped_at` fields; no filename prefix
- **`explore-NN-slug`:** MCP-collected during initial domain exploration, before the pipeline existed; hand-authored header, no `scraped_at`
- **`manual-NN-slug`:** MCP-collected as a targeted one-off addition after the pipeline was built; hand-authored header, no `scraped_at`

The original Python filenames (before portfolio cleanup) also carried a `YYYY-MM-DD_HH-MM-SS_` timestamp prefix, which made provenance unambiguous before the rename.
