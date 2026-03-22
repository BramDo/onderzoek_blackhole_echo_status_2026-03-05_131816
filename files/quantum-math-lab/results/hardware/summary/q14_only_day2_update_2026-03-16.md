# Q14-only day-2 update

Date: 2026-03-16

## Result

- q14 raw exact-short executed on `ibm_fez`
- artifact: `results/hardware/benchmark_q14_raw_exact_short_day2.json`
- hardware job id: `d6s2qnfgtkcc73cl1qvg`

## Gates

- perturbed-echo MAE versus exact reference: `0.033684`
- MAE gate (`<= 0.05`): PASS
- q14 classical exact-short baseline: `51.05 s`
- IBM runtime metric used for verdict: `quantum_seconds = 26`
- runtime gate (`26 < 51.05`): PASS

## Timing note

- local wrapper wall time was about `236.38 s`
- IBM timestamps were:
  - created `2026-03-16T16:18:37.300483Z`
  - running `2026-03-16T16:18:39.370557Z`
  - finished `2026-03-16T16:21:47.531588Z`

## Campaign status

- q14-only day 1: PASS
- q14-only day 2: PASS
- only day 3 remains before the frozen 3-day q14-only claim can be assessed
