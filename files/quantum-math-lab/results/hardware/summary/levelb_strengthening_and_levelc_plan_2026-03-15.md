# Level B strengthened and concrete route to Level C

Date: 2026-03-15

## 1. Why Level B is now stronger

The account check added one extra subset01 run that was not called out in the earlier Level-B summary:

- `q80_subset01_light`
  - hardware: `d6k9f4cgmsgc73c027fg`
  - calibration: `d6k9fdsmmeis739sfvk0`
  - backend: `ibm_fez`
  - setup: 80 qubits, subset `[0..9]`, depths `1-2`, trials `2`, shots `3000`

This matters because subset01 now has three independent positive-direction runs:

| Run | Backend | Raw gap | Mitigated gap | Gap increase | Ideal shift | Perturbed shift |
|---|---|---:|---:|---:|---:|---:|
| `q80_subset01_light` | `ibm_fez` | 0.760167 | 0.879629 | +0.119462 | +0.112000 | -0.007462 |
| `q80_subset01_mit` | `ibm_fez` | 0.696104 | 0.802921 | +0.106817 | +0.102253 | -0.004564 |
| `q80_subset01_mit_xsup` | `ibm_torino` | 0.643729 | 0.831016 | +0.187287 | +0.161870 | -0.025416 |

Directional consistency is now:

- `3/3` runs increase the ideal-minus-perturbed subset gap after mitigation.
- `3/3` runs push the ideal subset echo upward.
- `3/3` runs leave the perturbed subset echo flat-to-lower.
- The effect survives both backend variation (`ibm_fez`, `ibm_torino`) and option variation (with and without extra suppression).

Taken together with the existing locality control and rerun on subset `[10..19]`, this makes the Level-B statement more defensible:

> We do not just have one favorable 80q subset result. We now have a repeated pattern of subset-level mitigation benefit, plus a locality control, plus a close rerun, all pointing in the same direction.

## 2. What does not move Level C yet

The new account evidence does not close the Level-C gap:

- There is still no genuine multi-day research replication. The substantive campaign jobs are all from `2026-03-04`.
- The only later account job (`2026-03-07`) is unrelated Composer activity.
- The current q10 runtime comparison is not a winning Level-C point:
  - raw hardware / classical wall-time ratio: `1.3836`
  - mitigated hardware / classical wall-time ratio: `1.3451`
- The current q10 runtime comparison also mixes backends (`ibm_marrakesh` raw vs `ibm_fez` mitigated), so it is not a final claim artifact.

## 3. The cleanest route to Level C

### Recommendation

Do **not** spend more time trying to force Level C through q8/q10 or through 80q subset runs.

Instead, pivot the Level-C claim to the **exact-short track** on `q12` and `q14`, with a fixed observable:

- observable: `perturbed_echo`
- depths: `1,2,3,4`
- trials: `3` for qualification, `10` for final claim
- same seed family and same aggregation rule as the current benchmark
- same backend across claim runs if possible (`ibm_fez` is the current best anchor)

### Why this route is more realistic

- `q10` is already bad for a runtime win because classical exact-short is only `26.02 s`, while hardware is `32-36 s`.
- `q12` classical exact-short already costs `19:42.63`, so hardware has a real chance to win on runtime if it meets the accuracy target.
- `q14` hardware exact-short already exists and shows usable perturbed-error scale, but we still need a clean classical timing baseline for a fair runtime comparison.

## 4. Freeze the Level-C claim before running anything else

Level C is only coherent if the claim is frozen on a readout-meaningful observable.

Recommended fixed claim:

- "Hardware reaches perturbed-echo MAE <= 0.05 versus exact reference, and does so faster than classical exact-short on q12 and q14, reproduced on three independent days."

Do **not** define Level C on `ideal_echo` in the current workflow:

- q14 raw ideal error is about `0.288`, which is dominated by readout bias and will force you into a slower mitigation-heavy path.
- The scientifically interesting signal is in the perturbed echo / locality behavior, not the trivial all-zero return probability by itself.

## 5. Qualification phase

Goal: determine whether Level C is realistically attainable before spending 3-day campaign budget.

### Step Q1: complete the missing classical exact-short timing for q14

Run once:

```bash
/usr/bin/time -v -o results/benchmark/classical/time_black_hole_scrambling_q14_exact_short.txt \
  scripts/run-in-qiskit-venv.sh python qiskit_black_hole_scrambling.py \
  --qubits 14 --depths 1,2,3,4 --trials 3 --seed 424242 \
  --json-out results/benchmark/classical/black_hole_scrambling_q14_exact_short.json
```

### Step Q2: run q12 raw exact-short hardware on the same frozen task

Run once on the preferred backend:

```bash
scripts/run-in-qiskit-venv.sh python qiskit_black_hole_hardware_runner.py \
  --backend ibm_fez \
  --qubits 12 --depths 1,2,3,4 --trials 3 --shots 4000 \
  --output-json results/hardware/benchmark_q12_raw_exact_short_day1.json
```

### Step Q3: compare q12 raw against exact-short classical

Qualification target:

- `MAE(perturbed_echo) <= 0.05`
- hardware total runtime comfortably below classical wall time

Stop rule:

- If q12 raw misses the accuracy target by a large margin, do **not** continue the Level-C campaign unchanged.
- If q12 raw is accurate enough and already faster than classical, continue immediately to q14.

### Step Q4: re-run q14 in the same frozen style if needed

If you want a clean claim artifact, rerun q14 raw with the same naming and backend pinning:

```bash
scripts/run-in-qiskit-venv.sh python qiskit_black_hole_hardware_runner.py \
  --backend ibm_fez \
  --qubits 14 --depths 1,2,3,4 --trials 3 --shots 4000 \
  --output-json results/hardware/benchmark_q14_raw_exact_short_day1.json
```

Stop rule:

- If q14 raw is not faster than classical exact-short or fails the same accuracy target, stop the Level-C claim path and rewrite the benchmark definition instead of accumulating more 80q evidence.

## 6. Fallback only if raw misses target narrowly

If raw misses `MAE <= 0.05` only narrowly, try one mitigated fallback on the same day:

```bash
scripts/run-in-qiskit-venv.sh python qiskit_black_hole_hardware_runner.py \
  --backend ibm_fez \
  --qubits 12 --depths 1,2,3,4 --trials 3 --shots 4000 \
  --readout-mitigation --cal-shots 4000 \
  --output-json results/hardware/benchmark_q12_mit_exact_short_day1.json
```

```bash
scripts/run-in-qiskit-venv.sh python qiskit_black_hole_hardware_runner.py \
  --backend ibm_fez \
  --qubits 14 --depths 1,2,3,4 --trials 3 --shots 4000 \
  --readout-mitigation --cal-shots 4000 \
  --output-json results/hardware/benchmark_q14_mit_exact_short_day1.json
```

Use mitigation only if it actually improves the perturbed-echo MAE enough to clear the target without destroying the runtime advantage.

## 7. Claim phase: the minimum campaign that can honestly earn Level C

Only start this after the qualification phase passes on both q12 and q14.

### Day structure

Repeat the same frozen hardware configuration on **three independent calendar days**:

- Day 1: q12 + q14
- Day 2: q12 + q14
- Day 3: q12 + q14

For the final claim, use:

- same backend
- same shots
- same depths
- same trials count
- same observable
- same error target

If you want to align to the existing manifest more strictly, raise from `trials=3` to `trials=10` only after the day-1 qualification succeeds.

## 8. Practical stop rules

Stop the campaign and do not burn more runtime budget if any of the following happen:

1. q12 fails to beat classical exact-short runtime.
2. q12 or q14 cannot meet the frozen perturbed-echo target even with one mitigation fallback.
3. Backend availability forces a backend change mid-campaign; in that case restart the 3-day count.
4. You feel tempted to switch observable or target after seeing the results; that would invalidate the Level-C claim.

## 9. Bottom line

- Level B is stronger now because subset01 has become a repeated pattern rather than a one-off.
- Level C should now be pursued through **q12/q14 exact-short perturbed-echo benchmarking**, not through more 80q subset demonstrations.
- If q12 qualification fails, accept that Level C is not reachable under the current benchmark definition and revise the claim instead of collecting more heterogeneous runs.
