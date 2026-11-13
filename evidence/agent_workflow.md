# Curated AI-agent evidence

This is a **retrospective curated excerpt**, prepared from retained research
records. It is not a complete transcript, and no missing message timestamp is
invented. No full private conversation, personal machine path or financial
observation is reproduced here.

## Authentic human instructions

The retained extended-study approval includes:

> Use a common eligible training sample for all four regressions.

The retained full-grid approval includes:

> Keep regression coefficients fixed throughout each validation period.

> Ordinary MAPE on identical forecast dates will be our primary ranking criterion.

Source locators: extended-study approval message and full-grid approval message
in the supplied development conversation; corresponding decisions are recorded
in `AI_AGENT_DECISION_LOG.md`, sections 6 and 7. Message timestamps are unavailable
in the public excerpt. These quotations are instructions, not numerical proof.

## Authentic historical tool execution records, redacted

The commands below are transcribed from saved execution receipts. The original
absolute interpreter path is normalised to `python3`; arguments, dates and exit
codes are retained. No command below was newly executed to fabricate history.

| Original receipt identifier | Normalised actual command | Recorded UTC interval | Exit |
| --- | --- | --- | ---: |
| `recency_weighted_36_models/verification/training_execution.json` | `python3 -B experiment.py train` | 2026-11-05 13:52:42.095698 to 13:52:42.325417 | 0 |
| `recency_weighted_36_models/verification/validation_execution.json` | `python3 -B experiment.py validate` | 2026-11-05 13:52:56.338479 to 13:52:57.148744 | 0 |

Saved tool outputs report 36 regression configurations, four A-OLS reuses,
32 new regression fits, nine matching means, 705 native A origins and 37 common
origins. The original independent arithmetic receipt records 447,018 checks and
no discrepancy; it is historical evidence, not the current synthetic test count.

## Decision and verification sequence — summary, not verbatim transcript

The human first approved a short fixed OLS experiment. The agent recommended
common training samples, a mean-return control and target-date reporting before
the extended study. For the weighting study, the agent recommended a smaller
five-session design; the human instead approved all four lookbacks and aligned
the B/C cutoffs. Unfavourable benchmark results were retained. A forecast-origin
guard was added before an early forecasting function was used for market
predictions. A later source correction identified the historical provider as
FRED, rather than the earlier incorrect Yahoo description.

The final choice followed an exploratory 51-fit proximity comparison and remained
a human decision. It was not validated by the earlier four-lookback selector.
Independent arithmetic checks support calculation correctness; they do not prove
predictive skill, pristine vintages or statistical independence.

## Current public demonstration

The repository now supplies executable code, fixed-seed synthetic data, meaningful
tests and labelled synthetic outputs. These demonstrate the calculation mechanics
without distributing the genuine price records. They are distinct from the
historical agent execution records above and from restricted genuine-data replay.
