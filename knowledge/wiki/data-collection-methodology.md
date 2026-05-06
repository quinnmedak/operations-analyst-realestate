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

**Files:** `01`, `02`, `03`, `24`, `27` (5 files)

These files were scraped interactively using the Firecrawl MCP server inside a Claude Code session — one tool call per URL, no code written. They have hand-authored headers and no `scraped_at` YAML frontmatter.

| File | What it is | Why MCP |
|---|---|---|
| `01-jll-us-office-market-dynamics-q1-2026.md` | JLL US Office Q1 2026 | Domain exploration before the Python pipeline existed |
| `02-cbre-us-real-estate-market-outlook-2026.md` | CBRE US Outlook 2026 | Same — initial corpus seeding |
| `03-cushman-wakefield-greater-los-angeles-marketbeats.md` | C&W Greater LA hub page | Same — initial corpus seeding |
| `24-jll-la-retail-market-dynamics-q2-2025.md` | JLL LA Retail Q2 2025 (PDF) | Specific report found after the pipeline ran; one-off pull, no code to maintain |
| `27-cbre-la-industrial-marketbeat-q1-2026.md` | CBRE LA Industrial Q1 2026 (full report) | Same — targeted addition of a newly published report |

**Why MCP:** Files 01–03 were collected before `scrape_extract.py` existed, while exploring which sources were worth automating. Files 24 and 27 were specific PDFs identified after the pipeline was already built — adding a URL to the Python script and running it would have been more work than a single MCP call, with no recurring benefit.

---

## Decision Framework

| Situation | Tool | Reason |
|---|---|---|
| Scheduled or recurring source | Python | Reproducible, testable, runs on GitHub Actions |
| Exploring a domain before committing to a pipeline | MCP | Faster than writing a script when you don't yet know what to collect |
| Specific known URL, one-off addition | MCP | No code to maintain for a handful of PDFs |
| Source that must update automatically | Python | MCP requires a human in the loop |

---

## How to Identify Which Tool Produced a File

- **Python-generated:** YAML frontmatter with `title`, `url`, `scraped_at` fields
- **MCP-generated:** No `scraped_at` frontmatter; hand-authored header or bare markdown

The original Python filenames (before portfolio cleanup) also carried a `YYYY-MM-DD_HH-MM-SS_` timestamp prefix, which made provenance unambiguous before the rename.
