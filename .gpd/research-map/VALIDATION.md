# Validation and Cross-Checks

**Analysis Date:** 2026-03-17

## Analytic Cross-Checks

**Limiting Cases Verified:**

- Ideal echo sanity check: `U^\dagger U` should return the initial state, so `ideal_echo` stays near `1`
  - File: `files/quantum-math-lab/qiskit_black_hole_scrambling.py`
- Exact perturbed-echo reference for feasible sizes
  - Files: `files/quantum-math-lab/qiskit_black_hole_scrambling.py`, `files/quantum-math-lab/qiskit_black_hole_hardware_runner.py`
- q14 day-by-day MAE gate against exact reference
  - Files: `run_q14_only_exact_short_day.ps1`, `files/quantum-math-lab/results/hardware/benchmark_q14_raw_exact_short_day{1,2,3}.json`

**Limiting Cases NOT Verified:**

- Full 80-qubit global overlap or global-fidelity benchmark
- A second consecutive size runtime PASS under the clarified `quantum_seconds` metric
- Hardware-valid ZNE on real-device runs beyond the documented plan level

## Symmetry and Diagnostic Checks

- Locality control on subset `[10..19]`
  - Control with perturbation on qubit `0`: almost no gap
  - Signal with perturbation on qubit `10`: large reproducible gap
  - Files: `STATUS.md`, `files/quantum-math-lab/results/hardware/summary/levelb_evidence_report.md`

- Claim-language cross-check
  - The active q14-only claim is explicitly separated from full Level C in `STATUS.md` and `files/quantum-math-lab/results/hardware/summary/q14_only_campaign_plan_2026-03-16.md`

## Numerical Validation

**Reproduced Results:**

- q10 mitigation efficacy
  - Raw ideal abs error mean `0.205533` -> mitigated `0.006396`
  - File: `files/quantum-math-lab/results/hardware/summary/levelb_evidence_report.md`

- q14 three-day reproducibility
  - Day 1, day 2, and day 3 all pass `MAE <= 0.05` and `26 quantum_seconds < 51.05 s`
  - Files: `files/quantum-math-lab/results/hardware/summary/q14_only_day2_update_2026-03-16.md`, `files/quantum-math-lab/results/hardware/summary/q14_only_day3_update_2026-03-17.md`

- 80q subset reproducibility
  - Subset `[10..19]` perturb-qubit-10 rerun stays close (`delta gap = -0.001892`)
  - File: `files/quantum-math-lab/results/hardware/summary/levelb_evidence_report.md`

**Stability / Error Control:**

- `summary_by_depth` is emitted in all inspected hardware JSON artifacts
- Exact-short classical timing baselines are stored in `/usr/bin/time -v` sidecars under `files/quantum-math-lab/results/benchmark/classical/`
- IBM hardware JSON artifacts carry runtime metadata, backend metadata, and calibration metadata

## Comparison with Literature

**Current State:**

- Validation is benchmarked against internal manifests and prior run artifacts, not against external papers or datasets
- No bibliography or external paper references were found in the snapshot

**Discrepancy Status:**

- No in-snapshot external comparison layer exists yet, so “comparison with literature” is currently a missing validation dimension

## Internal Consistency

**Cross-Method Verification:**

- Same task family is encoded in both the protocol markdown and the manifests
- Classical and hardware tracks are compared on matching exact-short q14 tasks in the q14-only campaign

**Runtime-Metric Clarification:**

- `files/quantum-math-lab/results/hardware/summary/levelc_runtime_quantum_seconds_2026-03-16.md` explicitly resolves the ambiguity between local wall time and IBM `quantum_seconds`

## Test Suite

**Existing Tests:**

- No `pytest`, `unittest`, `tests/`, `requirements.txt`, or `pyproject.toml` files were found in the snapshot
- Validation is currently carried by benchmark artifacts, summary markdown, and campaign stop rules rather than an automated test harness

**Run Commands Present in Snapshot:**

```bash
bash files/quantum-math-lab/scripts/run-levelc-bundle.sh --stage plan
```

```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\Lenna\SynologyDrive\qlab\onderzoek_blackhole_echo_status_2026-03-05_131816\run_q14_only_exact_short_day.ps1 -DryRun
```

**Missing Tests:**

- JSON-schema validation for benchmark artifacts is proposed in `files/quantum-math-lab/hardware_advantage_protocol.md` but no dedicated checker script is present in the snapshot
- No automated regression test guards against claim drift or runtime-metric misuse

## Reproducibility

**Random Seeds:**

- Fixed seed family `424242` is part of both manifests

**Platform Dependence:**

- Hardware results depend on backend choice and calibration window; the q14-only plan explicitly says to restart the 3-day count if the backend changes

**Version Pinning:**

- Backend version and last properties update are embedded in hardware JSON artifacts
- No local dependency lockfile or package manifest is present in the snapshot

---

_Validation analysis: 2026-03-17_
