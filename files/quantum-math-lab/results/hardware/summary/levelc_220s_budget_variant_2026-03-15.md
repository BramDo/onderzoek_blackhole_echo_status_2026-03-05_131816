# Level C 220s budget variant

Date: 2026-03-15
Available hardware budget: 220 quantum_seconds

## Goal for today

Use the remaining hardware budget only for the smallest meaningful Level-C qualification test:

1. `q12 raw exact-short`
2. `q14 raw exact-short` only if `q12` qualifies

This keeps the plan aligned with the frozen Level-C route:

- observable: `perturbed_echo`
- depths: `1,2,3,4`
- trials: `3`
- shots: `4000`
- backend: `ibm_fez`

## Command 1

Run first:

```bash
scripts/run-in-qiskit-venv.sh python qiskit_black_hole_hardware_runner.py \
  --backend ibm_fez \
  --qubits 12 \
  --depths 1,2,3,4 \
  --trials 3 \
  --shots 4000 \
  --output-json results/hardware/benchmark_q12_raw_exact_short_day1.json
```

Expected budget use:

- target estimate: about `25-35` quantum_seconds
- conservative ceiling: about `40` quantum_seconds

## Stop rule after command 1

Only continue to command 2 if both conditions hold:

1. `q12` meets the fixed accuracy target: `MAE(perturbed_echo) <= 0.05` versus exact reference
2. `q12` is clearly faster than the matching classical exact-short baseline

If either condition fails:

- stop the hardware campaign for today
- do **not** spend budget on `q14`
- do **not** try extra 80q runs
- only consider one mitigated retry if the miss is small and you explicitly want to spend more budget on rescue

## Command 2

Run only if `q12` qualifies:

```bash
scripts/run-in-qiskit-venv.sh python qiskit_black_hole_hardware_runner.py \
  --backend ibm_fez \
  --qubits 14 \
  --depths 1,2,3,4 \
  --trials 3 \
  --shots 4000 \
  --output-json results/hardware/benchmark_q14_raw_exact_short_day1.json
```

Expected budget use:

- observed comparable run: about `26` quantum_seconds
- conservative ceiling: about `35` quantum_seconds

## Budget picture

Best practical estimate for today:

- `q12 raw` + `q14 raw`: about `50-70` quantum_seconds total

Conservative working allowance:

- hold back up to `80-90` quantum_seconds total for the two raw jobs together

That means the 220s budget is sufficient for:

- both raw qualification jobs
- plus one or two mitigated rescue attempts if they are narrowly needed

## What to run outside the hardware budget

The missing classical exact-short baseline for `q14` should still be completed, but it does not consume IBM hardware budget:

```bash
/usr/bin/time -v -o results/benchmark/classical/time_black_hole_scrambling_q14_exact_short.txt \
  scripts/run-in-qiskit-venv.sh python qiskit_black_hole_scrambling.py \
  --qubits 14 --depths 1,2,3,4 --trials 3 --seed 424242 \
  --json-out results/benchmark/classical/black_hole_scrambling_q14_exact_short.json
```

## Decision rule for tonight

- If `q12` fails: Level C is not ready under the current benchmark definition.
- If `q12` passes and `q14` fails: Level C is still not ready; the current claim is too ambitious or too unstable.
- If both pass: the remaining blocker is no longer budget, but the requirement for replication on three independent calendar days.
