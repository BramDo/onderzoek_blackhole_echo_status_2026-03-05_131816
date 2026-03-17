# Reference and Anchor Map

**Analysis Date:** 2026-03-17

## Active Anchor Registry

| Anchor ID | Anchor | Type | Source / Locator | Why It Matters | Contract Subject IDs | Required Action | Carry Forward To |
| --------- | ------ | ---- | ---------------- | -------------- | -------------------- | --------------- | ---------------- |
| `status-2026-03-17` | Current project status snapshot | prior artifact | `STATUS.md` | Declares the active q14-only claim, the allowed wording, and the current Level A/B/C boundaries |  | read | planning, execution, verification, writing |
| `protocol-levelc-v1` | Legacy Level A/B/C protocol | benchmark | `files/quantum-math-lab/hardware_advantage_protocol.md` | Freezes the broader benchmark matrix, pass criteria, and anti-overclaim rules |  | read, compare | planning, verification, writing |
| `manifest-levelc-v1` | Frozen Level-C manifest | benchmark | `files/quantum-math-lab/benchmarks/levelc_manifest.json` | Defines the original task family, parameter grid, and multi-size runtime criteria |  | use, compare | planning, execution, verification |
| `manifest-q14-only-v1` | Active q14-only manifest | benchmark | `files/quantum-math-lab/benchmarks/q14_only_manifest.json` | Defines the current frozen claim, exact-short task, MAE target, and q14 classical runtime comparator |  | use, compare | planning, execution, verification, writing |
| `q14-day3-pass` | Frozen q14 day-3 evidence | prior artifact | `files/quantum-math-lab/results/hardware/benchmark_q14_raw_exact_short_day3.json` and `files/quantum-math-lab/results/hardware/summary/q14_only_day3_update_2026-03-17.md` | Records the closing day of the 3-day q14-only claim with MAE and runtime PASS |  | compare, cite | verification, writing |
| `levelb-evidence-report` | Level-B evidence synthesis | prior artifact | `files/quantum-math-lab/results/hardware/summary/levelb_evidence_report.md` | Summarizes q10 mitigation gains and 80q subset/locality evidence |  | read, cite | planning, verification, writing |
| `ibm-raw-vs-mit` | Raw-vs-mitigated summary | prior artifact | `files/quantum-math-lab/results/hardware/summary/ibm_runs_raw_vs_mitigated_summary.md` | Gives compact per-depth raw/mitigated comparisons for q10 and q80 subset runs |  | compare | planning, verification |
| `runtime-quantum-seconds` | Runtime-interpretation note | prior artifact | `files/quantum-math-lab/results/hardware/summary/levelc_runtime_quantum_seconds_2026-03-16.md` | Clarifies that `IBM quantum_seconds` is the intended runtime gate for the current campaign logic |  | read, compare | planning, verification, writing |

## Benchmarks and Comparison Targets

- q14 exact-short active benchmark
  - Source: `files/quantum-math-lab/benchmarks/q14_only_manifest.json`
  - Comparison artifacts: `files/quantum-math-lab/results/hardware/benchmark_q14_raw_exact_short_day1.json`, `files/quantum-math-lab/results/hardware/benchmark_q14_raw_exact_short_day2.json`, `files/quantum-math-lab/results/hardware/benchmark_q14_raw_exact_short_day3.json`
  - Status: matched and closed with three PASS days according to `files/quantum-math-lab/results/hardware/summary/q14_only_day3_update_2026-03-17.md`

- Legacy Level-C runtime gate
  - Source: `files/quantum-math-lab/benchmarks/levelc_manifest.json`
  - Comparison note: `files/quantum-math-lab/results/hardware/summary/levelc_runtime_quantum_seconds_2026-03-16.md`
  - Status: contested / currently blocked by q12 runtime FAIL under `quantum_seconds`

- 80q subset locality benchmark
  - Source: `files/quantum-math-lab/results/hardware/summary/levelb_evidence_report.md`
  - Compared in: `STATUS.md`, `files/quantum-math-lab/results/hardware/summary/account_runs_last3weeks_analysis_2026-03-15.md`
  - Status: supportive of Level B and locality, not a full global-fidelity or Level-C benchmark

## Prior Artifacts and Baselines

- `files/quantum-math-lab/results/benchmark/classical/black_hole_scrambling_q12_exact_short.json`: exact-short classical reference for q12
- `files/quantum-math-lab/results/benchmark/classical/black_hole_scrambling_q14_exact_short.json`: exact-short classical reference for q14
- `files/quantum-math-lab/results/benchmark/classical/time_black_hole_scrambling_q12_exact_short.txt`: q12 wall-time comparator (`21.33 s` in current summaries)
- `files/quantum-math-lab/results/benchmark/classical/time_black_hole_scrambling_q14_exact_short.txt`: q14 wall-time comparator (`51.05 s` in current summaries)
- `files/quantum-math-lab/results/hardware/black_hole_hardware_q10_pilot.json`: q10 exact-reference mitigation evidence
- `files/quantum-math-lab/results/hardware/black_hole_hardware_q80_subset01_mit.json`: 80q subset-mitigation baseline on subset `[0..9]`
- `files/quantum-math-lab/results/hardware/black_hole_hardware_q80_subset02_mit_xsup_pq10_rerun1.json`: rerun evidence for subset `[10..19]` with perturbation on qubit `10`

## Open Reference Questions

- No external literature citations, DOI links, or paper bibliography are present in the snapshot, so the project currently anchors itself almost entirely on internal manifests and result artifacts.
- The snapshot does not contain a paper draft or bibliography file connecting the toy scrambling experiment to the broader black-hole / information-scrambling literature.
- `STATUS.md` cites only in-repo artifacts; if manuscript writing is a goal, the missing external reference layer will need to be built explicitly.

## Background Reading

- `files/quantum-math-lab/README.md`: general repo overview, older toy-demo framing, and historical entry points
- `files/quantum-math-lab/results/hardware/summary/levelb_strengthening_and_levelc_plan_2026-03-15.md`: rationale for shifting the decisive observable toward `perturbed_echo`
- `files/quantum-math-lab/results/hardware/summary/levelc_plan_reassessment_quantum_seconds_2026-03-16.md`: explains why q12 blocks the strict Level-C path under the clarified runtime metric

---

_Reference map: 2026-03-17_
