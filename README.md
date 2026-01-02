# Two Sides of the Same Coin: How LLMs Reveal Dual Narratives in Annual Reports

This repository is a **reproducibility-oriented codebase scaffold** for the ICAIF’25 paper:

> **Two Sides of the Same Coin: How LLMs Reveal Dual Narratives in Annual Reports**  
> Xiao Li*, Changhong Jin*, Yingjie Niu, Ruihai Dong (ICAIF 2025)  
> DOI: 10.1145/3768292.3770435  
> (*equal contribution)

The paper proposes a **Dual Narrative Analysis (DNA)** framework that uses an LLM with a **two-step Chain-of-Thought (CoT) prompting** process and **micro-scorecards** to quantify two complementary narratives in Form 10‑K filings:

- **Impact Score** (Item 1A: Risk Factors): how severe the event’s impact is described.
- **Response Score** (Item 7: MD&A): how proactive / mitigating the managerial response narrative is.

The framework produces **auditable, structured JSON outputs** and then aggregates scores programmatically for transparency and reproducibility.

## What’s in this repo

- ✅ A clean repo layout for: 10‑K section extraction → prompt assembly → LLM JSON outputs → deterministic aggregation → portfolio backtests.
- ✅ Prompt templates & output schema (Pydantic).
- ✅ Scripts you can extend to reproduce the end‑to‑end pipeline.
- 🚫 No large datasets are committed (EDGAR filings, GDELT dumps, etc.). Scripts write to `data/`.

<!-- ## Paper PDF

- Local copy: [`paper/ICAIF_2025.pdf`](paper/ICAIF_2025.pdf) -->

<!-- ## Quickstart

### 0) Make `src/` importable
You can either:

- **Option A (quick):**
  ```bash
  export PYTHONPATH=$PWD/src
  ```
- **Option B (clean):** install as an editable package:
  ```bash
  pip install -e .
  ```


### 1) Create environment
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Configure secrets (LLM API)
This scaffold uses OpenAI's **JSON mode / Structured Outputs**. If you use another provider, just replace `src/dna/client.py`.

Create a `.env` file (not committed) like:
```bash
OPENAI_API_KEY=...
```

### 3) Run pipeline (skeleton)
```bash
# 1) (optional) download filings (you will likely customize tickers / dates)
python scripts/download_edgar.py --config configs/default.yaml

# 2) run DNA scoring (LLM → structured JSON)
python scripts/run_dna.py --config configs/default.yaml

# 3) aggregate micro-scorecards → firm-year Impact/Response scores
python scripts/aggregate_scores.py --config configs/default.yaml

# 4) portfolio backtest
python scripts/backtest.py --config configs/default.yaml
``` -->

## Repository structure

```
.
├── prompts/               # CoT prompt templates + few-shot examples
├── configs/               # YAML configs (paths + parameters)
├── data/
│   ├── raw/               # downloaded filings / event data
│   └── processed/         # parsed Item 1A/7 texts etc.
├── outputs/
│   ├── scores/            # JSON outputs + aggregated tables
│   └── plots/             # figures generated from analysis
├── presentation/          # Oral presentation .pptx
└── notebooks/             # optional exploration
```

## How the pipeline maps to the paper

The repo mirrors the core components described in the paper:

1. **Data & corpus**: S&P 500 10‑K filings (2021–2024), global event source (GDELT), and market data (Yahoo Finance).  
2. **DNA framework**: prompt template with event info + metadata + full Item texts + few-shot + time-decay constraints, then:
   - Step 1: *Holistic analysis*  
   - Step 2: *Evidence extraction + micro-scorecard*  
3. **Deterministic aggregation**: programmatic computation of higher-level metrics from the LLM’s reason-level scores.  
4. **Backtesting**: annual rebalancing (July 1) and evaluation via cumulative return, Sharpe, max drawdown.

(See `prompts/` and `src/dna/`.)

## Citation

If you build upon this work, please cite:

- `CITATION.cff` (GitHub will render it automatically)
- or the DOI: **10.1145/3768292.3770435**

## License

- Code: MIT (see `LICENSE`)
- Paper: © authors, licensed under CC BY 4.0 as stated in the paper PDF.

---

<!-- ### Notes for you (repo owner)

This repo is designed as a *clean public scaffold*. When you’re ready, you’ll typically add:
- a short “Results” section with your key plots in `outputs/plots/`
- a `release/` tag for the camera-ready artifact
- minimal sample JSON in `outputs/scores/example/` for quick inspection -->
