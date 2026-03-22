# Q14-only day-3 update

Date: 2026-03-17

## Result

- q14 raw exact-short executed on `ibm_fez`
- artifact: `results/hardware/benchmark_q14_raw_exact_short_day3.json`
- hardware job id: `d6sj7jrbjfas73fohiig`

## Gates

- perturbed-echo MAE versus exact reference: `0.031142`
- MAE gate (`<= 0.05`): PASS
- q14 classical exact-short baseline: `51.05 s`
- IBM runtime metric used for verdict: `quantum_seconds = 26`
- runtime gate (`26 < 51.05`): PASS

## Timing note

- local wrapper wall time was about `94.42 s`
- IBM timestamps were:
  - created `2026-03-17T10:58:23.437025Z`
  - running `2026-03-17T10:58:24.797873Z`
  - finished `2026-03-17T10:59:04.24819Z`

## Campaign status

- q14-only day 1: PASS
- q14-only day 2: PASS
- q14-only day 3: PASS
- the frozen 3-day q14-only claim criteria are now satisfied
