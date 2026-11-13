# Algorithm provenance and public adaptations

The numerical method follows an existing AI-assisted research study. Original
archives remain unchanged. The following archive-relative identifiers and hashes
identify the source without exposing private machine paths.

| Source artifact | SHA-256 |
| --- | --- |
| `recency_weighted_36_models/experiment.py` | `2318b229f61356f45c1ee7484596c218660279c4cca6c04209cb854c8fe4dec0` |
| `recency_weighted_36_models/calendar_rules.py` | `ca869ec056f29e16647139ab2c5dc3d3b8372ca3d2b203bbc8197e0e896954fe` |
| `recency_weighted_36_models/legacy_engine.py` | `1681459299dff1eb481a16d0e67b954139f8da2d2976cf410e8185d56f999554` |
| `recency_weighted_36_models/protocol.json` | `14ede608320c1c9c4820116a0599df002fc19880da034f42e88c6f3c2224c783` |
| `recency_weighted_36_models/training/models/A_H24_k05.json` | `90f53f1de14008482992948c9faef465d211761276e2a4a4253f7b92a9133b7b` |

## Preserved mathematics

The calendar's holiday rules are retained, including the 2025 exceptional closure
and the Saturday New Year's convention. The fitting code retains common
40-session warm-up, mature six-session labels, simple-return definitions,
intercept, calendar-day recency weights, centred sums, fixed validation
coefficients, unchanged-price and matching-mean controls. The A/B/C periods and
native/common evaluation boundaries are retained.

## Adaptations

The public code separates calendar, engine, generator and CLI modules. It replaces
machine-specific archive orchestration and cross-project hash pins with explicit
local input/output arguments. The original runner reused four already checked
A-OLS models; the demonstration fits its own synthetic A-OLS models directly.
The selected official saved coefficients are published separately and never
substituted into synthetic training. The public engine does not import private
archive modules or retrieve live prices.

Synthetic generation is new demonstration code, not an original research result.
Private reproduction is an explicit command, with outputs forbidden inside the
public repository. Generated outputs have their own notices and receipt; they do
not overwrite historical research receipts or imply original approval timestamps.

The official point application uses exact rational arithmetic and final-only
half-up rounding. Historical fitting uses standard-library double precision and
`math.fsum`, matching the original implementation. Last-digit differences across
Python/platform versions should be assessed with declared numerical tolerances,
not by altering saved coefficients or loosening the historical claim.

