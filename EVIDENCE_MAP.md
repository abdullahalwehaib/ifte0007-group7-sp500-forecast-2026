# Public evidence map

This map distinguishes reproducible synthetic mechanics, genuine saved aggregate
evidence and restricted genuine-data verification. It does not claim that the
public synthetic data recover the genuine training observations.

| ID | Public path | Evidence and limitation |
| --- | --- | --- |
| E1 Model | `evidence/official_model.json`; `evidence/official_coefficients.csv` | Saved genuine specifications, coefficients and aggregate diagnostics. No observation sequence. Original selected artifact: `recency_weighted_36_models/training/models/A_H24_k05.json`. |
| E2 Validation | `evidence/aggregate_validation.csv` | Saved genuine summary rows from `recency_weighted_36_models/validation/summary.csv`. Selected-model filters: `model_id=A_H24_k05`; native context `group=native_A` (705), primary comparison `group=common` (37). Match `UNCHANGED` and `A_H24_MEAN` using the same group. Annual views use target years. |
| E3 Agent history | `evidence/agent_workflow.md` | Curated authentic short instruction excerpts and redacted historical execution receipts. Original full private conversations and financial tool outputs are not public. |
| E4 Other comparisons | `evidence/partner_benchmark_aggregates.csv` | Saved S&P aggregate rows only, identifying `22_nearest_benchmark/summary.csv`, `23_recent_weighted_momentum/weighted_summary.csv` and `24_october_60pct_weights/comparison.csv`. Distinguish scenarios, ordinary/weighted scores and refit/rescore stages. A four-lookback selector does not validate the later 51-fit screen. |
| E5 Source timing | `evidence/source_receipts.json` | Provider definitions, observed availability, saved aggregate source-overlap checks and archive-relative source hashes. No screenshot, raw price file, personal path or invented original retrieval time. |
| E6 Selection | `evidence/model_selection.json`; `evidence/public_verification_receipt.json` | Official model/target/cutoff/point, exploratory selection context and aggregate receipt of genuine-data replay. The receipt records post-cutoff verification of unchanged saved inputs and specifications; it is not a new forecast publication, selection or retrieval. Synthetic output is not that receipt. |
| Demonstration | `data/synthetic_prices.csv`; `outputs/synthetic_demo/`; `src/sp500_forecast/` | Artificial fixed-seed inputs and actual executable method. Every generated result is labelled synthetic. |

The public source and aggregate rows permit inspection of equations, sample rules,
benchmark definitions and published claims. Exact genuine-data fitting and
row-level error reproduction additionally require authorised restricted inputs.
Retain those separately. Do not infer availability or historical source rights
from the presence of a public metadata hash.

