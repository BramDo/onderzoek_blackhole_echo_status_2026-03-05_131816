# Hardware Advantage Protocol (Qlab)

Date: 2026-03-04
Scope: black-hole scrambling / Loschmidt echo workflow in `qiskit_black_hole_scrambling.py`

## Active campaign note (2026-03-16)

The active day-to-day benchmark target has been narrowed to a q14-only exact-short claim.
That active claim should be described as a single-size reproducible runtime-positive result, not as full Level C hardware advantage.
This protocol still defines the broader Level A / B / C framework for historical comparison.
It is acceptable to describe the broader picture as a plausible path toward wider advantage under lower noise, but that forward-looking statement should be marked as an inference rather than a demonstrated result.

## 1. Goal and claim levels

This protocol separates three claims. Do not call something "hardware advantage" unless level C is met.

- Level A: Mitigation efficacy
  - Show that mitigation reduces error vs exact reference.
- Level B: Hardware utility
  - Show that real hardware reaches useful accuracy on non-trivial sizes where raw hardware is not sufficient.
- Level C: Hardware advantage
  - Show that hardware reaches target accuracy faster than best known classical method for the same task definition.

## 2. Why current results are not yet advantage

Current q10 runs are simulator-noise (Aer) runs, not real-device runs.
They are valid for method development, but not for an advantage claim.

## 3. Task definition (must stay fixed)

Fix this task family before benchmarking:

- State preparation: `|0...0>`
- Circuit family: random brickwork scrambler + `U† X U` perturbed echo
- Outputs:
  - `ideal_echo`
  - `perturbed_echo`
- Accuracy metric:
  - absolute error vs exact statevector reference for each depth
- Aggregation:
  - mean and std over fixed seeds

## 4. Required benchmarking matrix

Use the same matrix for classical and quantum tracks.

- qubits: `8, 10, 12` first; extend to `14` if feasible
- depths: `1,2,3,4,5,6,8,10,12`
- seeds/trials: at least `10` per depth for publication-quality; `3` for pilot
- shots: `5000` and `10000`

## 5. Classical baseline track

Track both runtime and memory with `/usr/bin/time -v`.

- Baseline 1: exact statevector (current script)
- Baseline 2: best practical classical approximation available in your stack (if added later)

For every `(qubits, depth)` record:

- wall-clock runtime
- max RSS memory
- error vs exact (where exact is feasible)

## 6. Hardware track (real IBM backend)

Run the same circuits on hardware via runtime sampler.
Do not reuse Aer depolarizing scaling as "hardware ZNE"; for real hardware ZNE, use gate-folding/noise-scaling methods that are valid on hardware.

Required per run:

- backend name and calibration timestamp
- transpiled depth and 2q count
- shots
- raw counts
- mitigated estimate
- uncertainty (bootstrap or repeated jobs)

## 7. Mitigation stack to test

Each config must be run separately and logged.

- raw (no mitigation)
- readout mitigation only
- readout mitigation + ZNE (hardware-valid scaling)
- optional: dynamical decoupling / twirling if supported by backend workflow

## 8. Decision criteria

## Level A (mitigation efficacy)

Pass if all hold:

- median absolute error improves vs raw on at least `70%` of `(qubits, depth)` points
- no catastrophic degradation on more than `10%` of points

## Level B (hardware utility)

Pass if all hold:

- for at least one non-trivial size (`>=10 qubits`), mitigated hardware reaches a predeclared accuracy target
- repeated jobs show stable confidence intervals

## Level C (hardware advantage)

Pass only if all hold:

- same task, same accuracy target, same confidence level on both tracks
- hardware runtime beats best classical runtime for at least two consecutive sizes
- result is reproducible across at least `3` independent days / calibration windows

## 9. Minimal implementation plan

1. Add a hardware runner for black-hole scrambling echoes using runtime sampler (new script).
2. Log schema in JSON for raw + mitigated + metadata.
3. Add one orchestrator script to run full matrix and emit one summary table.
4. Add CI-like local check that validates JSON schema and required fields.

## 10. Immediate next experiment (pragmatic)

Run a pilot to establish Level A/B readiness:

- qubits: `8,10`
- depths: `1,2,3,4,5,6,8,10`
- trials: `3`
- shots: `5000`
- configs: raw, readout-mitigated

If pilot is stable, increase to trials `10` and add hardware-valid ZNE.

## 11. What to report to avoid over-claiming

Use wording like:

- "mitigation improves noisy estimates in simulator and is being validated on hardware"

Avoid wording like:

- "we demonstrated hardware advantage"

unless Level C criteria are actually met.

## 12. 80-qubit scalable mitigation path

At `80` qubits, global `P(0...0)` is very sensitive to readout/SPAM and quickly loses contrast.
Use a fixed small subset observable plus subset readout mitigation.

Rules:

- always use `--skip-exact` for large `n` (exact statevector is not feasible)
- keep `--subset-qubits` at `8-12` qubits
- run both raw and mitigated configs on the same backend/day window
- repeat with at least two disjoint subsets (for robustness)

Concrete commands (runner supports this now):

1) Raw baseline (no mitigation):

```bash
scripts/run-in-qiskit-venv.sh python qiskit_black_hole_hardware_runner.py \
  --qubits 80 \
  --depths 1,2,3,4 \
  --trials 3 \
  --shots 4000 \
  --skip-exact \
  --output-json results/hardware/black_hole_hardware_q80_raw.json
```

2) Scalable readout mitigation on subset `0-9`:

```bash
scripts/run-in-qiskit-venv.sh python qiskit_black_hole_hardware_runner.py \
  --qubits 80 \
  --depths 1,2,3,4 \
  --trials 3 \
  --shots 4000 \
  --readout-mitigation \
  --cal-shots 6000 \
  --subset-qubits 0-9 \
  --skip-exact \
  --output-json results/hardware/black_hole_hardware_q80_subset01_mit.json
```

3) Same run with disjoint subset `10-19`:

```bash
scripts/run-in-qiskit-venv.sh python qiskit_black_hole_hardware_runner.py \
  --qubits 80 \
  --depths 1,2,3,4 \
  --trials 3 \
  --shots 4000 \
  --readout-mitigation \
  --cal-shots 6000 \
  --subset-qubits 10-19 \
  --skip-exact \
  --output-json results/hardware/black_hole_hardware_q80_subset02_mit.json
```

Compare raw vs mitigated on:

- `raw.ideal_subset_echo` vs `readout_mitigated.ideal_subset_echo`
- `raw.perturbed_subset_echo` vs `readout_mitigated.perturbed_subset_echo`
- stability (std across trials and subset-to-subset agreement)
