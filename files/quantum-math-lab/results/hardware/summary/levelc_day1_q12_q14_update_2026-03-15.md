# Level C day-1 update: q12/q14 exact-short qualification

Date: 2026-03-15

## What was completed

- q12 raw exact-short hardware qualification on `ibm_fez`
  - artifact: `results/hardware/benchmark_q12_raw_exact_short_day1.json`
  - job id: `d6rcd94u243c73a192m0`
- q14 raw exact-short hardware qualification on `ibm_fez`
  - artifact: `results/hardware/benchmark_q14_raw_exact_short_day1.json`
  - job id: `d6rcjrbopkic73fj1a10`
- q12 exact-short classical baseline
  - artifact: `results/benchmark/classical/black_hole_scrambling_q12_exact_short.json`
  - wall time: `0:21.33`
- q14 exact-short classical baseline
  - artifact: `results/benchmark/classical/black_hole_scrambling_q14_exact_short.json`
  - wall time: `0:51.05`

## Qualification result

- Frozen observable for this route: `perturbed_echo`
- Fixed accuracy target used for qualification: `MAE <= 0.05` versus exact reference

| size | backend | raw perturbed_echo MAE | qualification |
|---|---|---:|---|
| q12 | ibm_fez | 0.037174 | PASS |
| q14 | ibm_fez | 0.032857 | PASS |

## Interpretation

- Day-1 accuracy qualification passes for both q12 and q14.
- Level C is still **NOT YET** because the manifest-level claim also requires:
  - matched runtime victory versus best classical on two consecutive sizes
  - reproduction on three independent calendar days
- The classical timing artifacts are now much faster than the older pre-fix q12 baseline, because the exact OTOC path was rewritten to avoid dense `2^n x 2^n` operator construction.
- As a result, any earlier runtime-advantage intuition based on the old q12 classical timing should be treated as obsolete until the hardware-vs-classical runtime comparison is recomputed against these updated baselines.

## Immediate next step

- Produce an explicit runtime comparison note for q12 and q14 using the updated classical baselines and the matching hardware job metadata, then decide whether a 3-day Level-C campaign is still justified.
