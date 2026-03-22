# Level C day-2 update: q12 ran, q14 stopped by gate

Date: 2026-03-16

## What happened

- q12 raw exact-short hardware run executed on `ibm_fez`
  - artifact: `results/hardware/benchmark_q12_raw_exact_short_day2.json`
  - hardware job id: `d6rv3ef90okc73erlkb0`
- q14 raw exact-short was **not** started on day 2.

## q12 result

- perturbed-echo MAE versus exact reference: `0.035924`
- MAE gate (`<= 0.05`): PASS

## Runtime gate

- q12 classical exact-short baseline: `21.33 s`
- q12 hardware day-2 elapsed time: approximately `349 s` (`00:05:49`)
- IBM runtime metadata for the same job reports:
  - `quantum_seconds = 26`
  - `billed_seconds = 26`
  - timestamps: `created=2026-03-16T12:04:09.4919Z`, `running=2026-03-16T12:07:35.100809Z`, `finished=2026-03-16T12:09:19.297156Z`

Important note:

- the PowerShell day-run wrapper crashed after q12 because of a MAE parser bug, so it did not write a timing artifact for q12 day 2
- the elapsed hardware time above is therefore derived from the local file timestamps of the q12 day-2 log/output pair, not from a clean stopwatch record
- the IBM `quantum_seconds` figure is much smaller than the local end-to-end wall time and is consistent with queueing / orchestration overhead dominating the gap
- under the clarified runtime definition on `quantum_seconds`, the runtime gate still fails because `26 > 21.33`

## Consequence

- The day-2 run strengthens confidence that q12 can repeatedly hit the accuracy target on `perturbed_echo`.
- It does **not** strengthen the current Level-C runtime claim, because the IBM usage stays above the q12 classical baseline.
- Because q12 did not clear the runtime gate, q14 was not run on day 2 under the frozen stop rule.

## Operational note

- `run_levelc_exact_short_day.ps1` has been patched so future day runs no longer fail on the post-run MAE averaging step.
