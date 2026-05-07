# Slides Stakeholder Brief
## Investment Recommendation — SoCal Industrial

---

## Who the Stakeholder Is

**A private equity fund with LA commercial real estate exposure.**

Private capital is the dominant buyer in the LA CRE market right now — 61.4% of all LA deals in 2025, the highest share in a decade, and net buying (only 51.2% of sellers are private capital). In SoCal industrial specifically, private buyers accelerated from 46.1% to 63.8% of acquisitions between 2024 and Q4 2025 alone. These funds move on conviction before institutional investors catch up.

This is the client a JLL capital markets broker is most likely sitting across from right now.

Source: `knowledge/wiki/capital-markets.md` — Bisnow LA capital markets, CBRE via Bisnow Q4 2025

---

## Why They Benefit From Our Insights

This fund already holds a mix of LA real estate — likely including office. They are asking two questions:

**1. What do we do with our office positions?**

Slide 4 answers this directly: office REIT prices fell -21% YoY in Q1 2026 *even as interest rates eased*. If the problem were just rates, a Fed cut would have fixed it. It didn't. The problem is structural — hybrid work permanently reduced office demand. Holding office and waiting for a rate-driven recovery is the wrong thesis.

Source: `knowledge/wiki/la-office-market.md`, FRED (FEDFUNDS) via Snowflake

**2. Where do we redeploy that capital?**

Slides 2 and 3 answer this: industrial has structurally outperformed (+160% REIT price since 2018) because e-commerce permanently shifted from ~11% to ~16% of retail sales in 2020 and held there. This is not a cycle — it is a permanent change in how goods move. Industrial demand is durable.

Source: `knowledge/wiki/la-industrial-market.md`, `knowledge/wiki/macro-environment.md`, FRED (ECOMPCTNSA) via Snowflake

---

## The Trend — Backed by the Data

LA industrial is in a post-pandemic oversupply correction that is now clearing:

**What happened:** During 2020–2022, developers built aggressively to meet e-commerce demand. That spec supply flooded the market faster than tenants could absorb it — vacancy climbed from under 1% at the trough to 5.4% today, and landlords cut rents to fill buildings. Rents fell from a Q1 2023 peak of $1.74/SF to $1.21/SF today — a 30.5% decline.

Source: CBRE LA Industrial Q1 2026 — `knowledge/wiki/la-industrial-market.md`

**Why it is clearing now:**

| Signal | Data | What it means |
|---|---|---|
| Absorption | +934K SF Q1 2026 — first positive since 2022 | Tenants are taking more space than they're vacating |
| Pipeline | 4.53M SF under construction, down **34.5% YOY** for four consecutive quarters | Developers stopped building — less new supply coming |
| Leasing velocity | 14.6M SF in Q1 2026 — highest quarterly level in three years | Tenant demand is back |
| Vacancy vs. national | LA at 5.4% vs. national 7.5% | LA industrial structurally tighter than most markets |

Source: CBRE LA Industrial Q1 2026 — `knowledge/wiki/la-industrial-market.md`; JLL US Industrial Q1 2026 — `knowledge/wiki/national-cre-trends.md`

**The causal chain:** Less supply being built + more space being absorbed = vacancy tightens = landlords regain pricing power = rents recover toward peak.

---

## The Number — Justifiable From the Data

**The recommendation:** Acquire SoCal industrial now at $1.21/SF to capture the rent recovery before the supply contraction closes the window.

**The math:**

| | Value | Source |
|---|---|---|
| Current asking rent | $1.21/SF NNN | CBRE Q1 2026 |
| 2023 peak rent | $1.74/SF NNN | CBRE Q1 2026 |
| Discount to peak | **−30.5%** | CBRE Q1 2026 |
| Income upside at normalization | **+44%** on current-rate acquisitions | ($1.74 − $1.21) / $1.21 |

A fund acquiring a 200,000 SF SoCal industrial asset today at $1.21/SF NNN generates $2.42M/year in rental income. If rents recover to the prior peak of $1.74/SF, that same asset generates $3.48M/year — **$1.06M in additional annual income** with no change in occupancy or capital structure.

**Why the window is closing:** The pipeline has contracted for four consecutive quarters (-34.5% YOY). As new supply dries up and absorption continues, vacancy tightens. When vacancy tightens, landlords raise rents. Every quarter of delay is a quarter closer to paying full-price for the same assets.

**Interview caveat:** The Q1 2026 positive absorption figure (+934K SF) includes a single Trader Joe's 1M SF distribution center. Without it, Q1 would have been slightly negative. The pipeline contraction is the more reliable leading indicator — four straight quarters of developers pulling back is structural, not a one-deal event.

Source: CBRE LA Industrial Q1 2026 — `knowledge/wiki/la-industrial-market.md`

---

## One-Line Slide Recommendation

> **Increase SoCal industrial exposure now — buy at $1.21/SF (30% below 2023 peak) before the four-quarter pipeline contraction closes the rent recovery window → 44% income upside if rents normalize to prior peak**

---

## Sources

- `knowledge/wiki/la-industrial-market.md` — primary market data
- `knowledge/wiki/capital-markets.md` — buyer composition, private capital dominance
- `knowledge/wiki/macro-environment.md` — e-commerce structural shift
- `knowledge/wiki/la-office-market.md` — office structural weakness
- `knowledge/wiki/national-cre-trends.md` — national industrial context
- Snowflake: `FACT_DAILY_PRICES`, `FACT_MACRO_QUARTERLY` — REIT prices, FRED e-commerce series
