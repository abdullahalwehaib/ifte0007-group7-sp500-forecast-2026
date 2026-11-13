# Fixed-model S&P 500 forecasting evidence

This repository publishes genuine calculation code, saved model coefficients,
permitted aggregate research evidence and an artificial-data demonstration.
**It does not publish the genuine historical price series or individual genuine
historical forecasts.** The official point record is in
[`evidence/model_selection.json`](evidence/model_selection.json).

The university assignment asks for one S&P 500 **price-index** closing-level
forecast with a clear information boundary, economic rationale, benchmark
validation, sensitivity, agent evidence and reproducible calculations. The
approved official point is **7,607.23 index points**, targeting **20 November
2026, 16:00 New York EST / 21:00 UTC**, with information cutoff **13 November
2026, 12:00 noon London GMT / UTC**. This official record is separate from every
synthetic demonstration result.

Historical modelling inputs were FRED SP500, originally supplied by S&P Dow
Jones Indices LLC. Only the approved 12 November origin used Yahoo Finance
^GSPC daily Close as a fallback. Its dated Close was observed at
**2026-11-12T21:19:08.818Z**, before cutoff. That receipt bounds availability by
observation; the exact first-publication instant and original historical CSV
download timestamps remain unknown. No genuine price sequence is published here.

Every generated demonstration file carries:

> SYNTHETIC DEMONSTRATION — NOT THE OFFICIAL SUBMITTED FORECAST

Artificial observations exercise the research method. They do not reproduce the
reported historical accuracy, establish financial predictability or replace the
restricted genuine-data evidence. See [DATA_RIGHTS.md](DATA_RIGHTS.md).

## Run the public demonstration

Python **3.12.14** and its standard library are sufficient. There is no pip
dependency, API key, AI account or live download. From the repository directory:

```sh
python3 -B run.py generate-synthetic --output data/synthetic_prices.csv
python3 -B run.py demo --output reproduced_runs/synthetic_demo
python3 -B -m unittest discover -s tests -v
```

The seed and generator are fixed. Repeating generation recreates the same input
bytes. Use a fresh output directory: completed results are never overwritten.
`outputs/synthetic_demo/` contains the saved demonstration run for comparison.
All its prices, training rows, forecasts, errors and metrics are synthetic.

The workflow fits four lookbacks (5/10/20/40 sessions), three historical windows
and OLS/24-month/six-month estimation schemes. It includes unchanged-price and
matching weighted-mean controls, 705 native A origins, and 37 common origins.
Those counts follow the original calendar and sample design; synthetic scores
are unrelated to the genuine scores in `evidence/aggregate_validation.csv`.

## Apply saved coefficients to an authorised private CSV

Keep the input and output **outside this repository**. The CLI enforces that
boundary. Required private CSV header: `observation_date,SP500`; dates are ISO
US equity-session dates and values are positive closing price-index levels.
No real example price rows are included here.

```sh
python3 -B run.py forecast-saved --input /private/path/authorised.csv --output /private/path/new_forecast_output
```

This command requires six consecutive completed sessions through the approved
12 November 2026 origin. It applies the original saved alpha and beta using exact
`Fraction` arithmetic, rounds the final level once with `ROUND_HALF_UP`, and
performs **no fitting**. It makes no network request. A private input is the
user's responsibility; repository access does not confer data redistribution rights.

To reproduce the original historical fitting and evaluation algorithm using
authorised private history covering 2020 through the approved origin:

```sh
python3 -B run.py private-reproduce --input /private/path/authorised_history.csv --output /private/path/new_historical_reproduction
```

This explicitly requested reproduction estimates the previously specified fixed
historical models; it does not update the official model, change its specification
or optimise against validation outcomes. Its outputs remain private.

## Mathematical and chronological rules

For a verified session position `t`, momentum is `P_t/P_(t-k)-1`, the label is
`P_(t+6)/P_t-1`, and the level forecast is `P_t*(1+alpha+beta*X_t)`.
Training requires all 40 warm-up sessions and the six-session outcome inside each
window, including for shorter lookbacks. H24 uses 730.5 **calendar days** and H6
182.625, based on training-origin age relative to its original cutoff.
An intercept is fitted with centred weighted sums; validation coefficients are
fixed. Recency preferences are not inverse-error-variance estimates.

Validation prediction receives only a completed origin prefix. Targets are exactly
six subsequent equity sessions; outcomes are attached after predictions are made.
The full retrospective file is available to the orchestration process, so this
mechanical restriction is not evidence of a pristine blind experiment. Missing
sessions, malformed values and future prediction inputs fail rather than being
filled, sorted or clipped silently.

## Genuine aggregate findings and limits

The saved official model is `ABD_A_H24_k05`. Its coefficients remain fixed from
2020–2023 training, with 960 common eligible origins. Genuine native-705 MAPE is
1.5567763811%, against 1.6030643296% unchanged and 1.5609709837% matching H24 mean.
The original **primary common-37** MAPE is 1.0523226095%, against 1.0512776736%
unchanged: the selected regression narrowly loses. This unfavourable result is
retained. Moderate weighting improved seven of twelve matched common-period
regressions; six-month weighting improved two. The mean control's competitiveness
limits claims about incremental momentum information.

The eventual model choice followed exploratory screening of 51 frozen fits by
predicted movement. Fifth-place proximity is not an accuracy or confidence rank.
Overlapping horizons, previously inspected periods, correlated variants, stale
coefficients and unverified historical vintages limit inference. Different native
and common samples must not be pooled or ranked as identical evidence.

## Evidence and provenance

- [Evidence map](EVIDENCE_MAP.md): links and original-artifact identifiers.
- [Source provenance and adaptations](PROVENANCE.md): original code hashes.
- [Saved coefficients](evidence/official_coefficients.csv): genuine parameters only.
- [Genuine aggregates](evidence/aggregate_validation.csv): no row-level forecasts.
- [Curated agent evidence](evidence/agent_workflow.md): authentic short instructions
  and redacted historical tool execution records, distinct from this demonstration.
- [Genuine-data verification receipt](evidence/public_verification_receipt.json):
  post-cutoff replay of unchanged saved inputs and specifications, with 45 model/control
  JSON files and 731 deterministic CSV files reproduced byte for byte. This verifies
  arithmetic and integrity, not predictive skill or independent statistical observations.

The numerical code does not depend on document-authoring tools. No full private
transcripts, personal machine paths, student identifiers, source screenshots or
genuine price observations belong in this public package.

