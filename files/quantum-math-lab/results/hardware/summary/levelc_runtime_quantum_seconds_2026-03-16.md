# Level C runtime interpretation on IBM quantum_seconds

Date: 2026-03-16

## Runtime metric clarification

- For the current Level-C discussion, the intended hardware runtime metric is `IBM quantum_seconds`.
- This is different from local end-to-end wall time, which can include queueing, orchestration, result fetch, and wrapper overhead.

## Classical baselines

| size | classical exact-short wall time |
|---|---:|
| q12 | `21.33 s` |
| q14 | `51.05 s` |

## Hardware runtime from IBM job metadata

| run | hardware job id | quantum_seconds | result |
|---|---|---:|---|
| q12 day 1 | `d6rcd94u243c73a192m0` | `26` | runtime FAIL vs q12 classical |
| q14 day 1 | `d6rcjrbopkic73fj1a10` | `26` | runtime PASS vs q14 classical |
| q12 day 2 | `d6rv3ef90okc73erlkb0` | `26` | runtime FAIL vs q12 classical |

## Interpretation

- q12 is currently the blocker for a Level-C runtime claim under the `quantum_seconds` metric.
- q14 looks promising on runtime under the same metric, but that alone is not enough because the claim requires two consecutive sizes.
- Day-2 q12 did strengthen accuracy reproducibility, but it did not change the runtime verdict because the IBM usage stayed at `26 quantum_seconds`.

## Practical consequence

- If the benchmark definition is now fixed on `quantum_seconds`, future gating should compare:
  - q12 hardware `quantum_seconds` versus q12 classical wall time
  - q14 hardware `quantum_seconds` versus q14 classical wall time
- Under that definition, there is no need to treat queue-heavy local wall time as the primary runtime gate.
