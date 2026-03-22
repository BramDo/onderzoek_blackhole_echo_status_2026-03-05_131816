# Q14-only campaign plan

Date: 2026-03-16

## Scope

The active campaign target is no longer the legacy q12/q14 Level-C route.
It is now a narrower q14-only claim on the same exact-short task.

This q14-only claim is:

- same observable: `perturbed_echo`
- same accuracy target: `MAE <= 0.05` versus exact reference
- same runtime metric: `IBM quantum_seconds`
- same classical comparator: q14 exact-short wall time
- same reproducibility rule: three independent calendar days

It is **not** the same thing as the older two-consecutive-size Level-C hardware-advantage claim.

## Frozen q14-only claim

Recommended wording:

- "On q14 exact-short perturbed-echo benchmarking, raw hardware reaches `MAE <= 0.05` versus exact reference and does so faster than the matching classical baseline, reproduced on three independent calendar days."

Communication-safe broader wording:

- "We observe a narrow, task-specific quantum runtime advantage at q14, together with reproducible subset-level utility at 80 qubits. This is not yet full hardware advantage, but it is consistent with a plausible path toward broader advantage if noise can be reduced further."

Communication rule:

- The first sentence is supported by current evidence once the 3-day q14-only campaign closes.
- The phrase "plausible path toward broader advantage" is an inference and should be presented as such, not as an achieved result.

## Frozen configuration

- qubits: `14`
- backend: `ibm_fez` when available
- depths: `1,2,3,4`
- trials: `3`
- shots: `4000`
- seed family: existing exact-short benchmark seed rule
- runtime verdict: `IBM quantum_seconds < 51.05 s`

## Current evidence

- Day 1 on 2026-03-15 passes:
  - q14 perturbed-echo MAE: `0.032857`
  - q14 runtime: `26 quantum_seconds`
  - q14 classical comparator: `51.05 s`
- Day 2 on 2026-03-16 also passes:
  - q14 perturbed-echo MAE: `0.033684`
  - q14 runtime: `26 quantum_seconds`
  - q14 classical comparator: `51.05 s`

## Remaining campaign days

- Day 3: 2026-03-17

Run the same q14 raw exact-short bundle on the remaining day with no change to:

- observable
- target
- backend when possible
- depths
- trials
- shots

## Stop rules

Stop the q14-only campaign if any of the following happen:

1. q14 misses `MAE <= 0.05`.
2. q14 no longer beats the q14 classical baseline under `IBM quantum_seconds`.
3. Backend changes and you do not want to restart the 3-day count.
4. You feel tempted to change the task definition after seeing the result.

## Entry point

Use the q14-only day runner:

```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\Lenna\SynologyDrive\qlab\onderzoek_blackhole_echo_status_2026-03-05_131816\run_q14_only_exact_short_day.ps1
```

For a dry check first:

```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\Lenna\SynologyDrive\qlab\onderzoek_blackhole_echo_status_2026-03-05_131816\run_q14_only_exact_short_day.ps1 -DryRun
```
