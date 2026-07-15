# Event-Model Benchmark Report — README

## Total Token Usage
Total token usage: 130k ~ 141k
Total token cost: $10 ~ $15

## What this is
`benchmark_report.html` is a self-contained, offline-viewable dashboard comparing three models — **claude-opus-4.5**, **gpt-5.3-codex**, and **gemini-3.1-pro** — on an evidence-backed event-analysis task. Open the file in any browser; no server or install needed.

## Source data
`comparison_analysis/results_cache.csv` — 96 rows: **3 models × 8 events × 4 evaluation years (2021–2024)**.

Each row is one model's graded run on one historical/current event, scored by an automated rubric into:
- `total_score` — the headline number (sum of scored evidence snippets)
- `evidence_count`, `avg/max/min_snippet_score` — how much evidence was found and how strong it was
- `positive_points_total` / `negative_points_total` — points earned vs. deducted by the rubric
- `holistic_analyisis_lenght` — length (characters) of the model's written analysis
- `latency_second` — response time, where logged

## Headline findings
1. **claude-opus-4.5 leads overall** — mean score 18.66 vs. gpt-5.3-codex's 15.28 and gemini-3.1-pro's 8.41 (out of a 31-point max observed in the data).
2. **gemini-3.1-pro's gap is mostly penalties, not missing evidence** — it lost −81 points to rubric deductions across its 32 runs, vs. only −5 (gpt) and −7 (claude). Its `negative_points_total` per row is far more negative on average than the other two models.
3. **All three models dip after 2023** — every model's mean score falls from its 2023 peak into 2024, driven largely by declining `COVID_19_Pandemic` scores across the board.
4. **Israel–Hamas Conflict is a near-blackout event** — claude-opus-4.5 only scores on it from 2023 onward (score 20 in both 2023 and 2024); gpt-5.3-codex and gemini-3.1-pro score exactly 0 in **all four** evaluation years.
5. **2021 is a clean zero for two events, across all models** — `Russia_Ukraine_Conflict` and `US_China_Chip_Export_Controls` score 0 for every model specifically in 2021, then recover from 2022 onward. This lines up with those events not yet having happened as of a 2021 evaluation frame — consistent with correct evidence-withholding rather than a scoring bug.
6. **gpt-5.3-codex's latency is unmeasured** — `latency_second` is 0 for all 32 of its runs, which reads as "not logged" rather than an actual 0-second response, so it's excluded from the latency comparison chart.
7. **gemini-3.1-pro has one clear outlier** — its 2021 `US_China_Chip_Export_Controls` run logs 912 seconds of latency, ~40–90× its other runs; excluded from its "clean" latency average as a likely logging artifact.

## How to read the report
- **Section 01 — Scoreboard**: per-model summary cards (mean score, consistency, latency, penalty totals, zero-score run count).
- **Section 02 — Trajectory**: line chart of mean score per model across the four evaluation years.
- **Section 03 — Breakdown**: heatmap of mean score per event × model, ordered hardest → easiest.
- **Section 04 — Zero-score runs**: where models produced no scorable evidence at all, isolating the Israel–Hamas pattern and the 2021-only zeroes.
- **Section 05 — Operational**: latency and analysis-length comparisons, with the measurement caveats above called out inline.

## Caveats / things to watch if this data gets reused
- `gpt-5.3-codex` latency should be treated as **missing**, not zero, in any further analysis.
- The `gemini-3.1-pro` 912s latency value should be checked against raw logs before being used in any latency-based decision — it's very likely not a genuine response time.
- `total_score` scale differs slightly by row depending on `evidence_count` (3–5 snippets per run), so raw score comparisons implicitly reward runs where a model found more evidence, not just higher-quality evidence. `avg_snippet_score` is the more apples-to-apples quality metric if you need one.

## Files
- `model_benchmark_report.html` — the interactive report (open in browser)
- `README.md` — this file
