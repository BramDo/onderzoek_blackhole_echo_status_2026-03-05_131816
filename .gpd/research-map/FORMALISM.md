# Theoretical Frameworks

**Analysis Date:** 2026-03-17

## Physical System

**Subject:** Quantum-information black-hole scrambling toy model built from random brickwork circuits, evaluated with Loschmidt-echo-style observables and benchmarked on IBM hardware.

**Scales:**

- Qubit counts: `6` for the README toy demo, `8/10/12` for classical and pilot benchmarking, `14` for the active exact-short campaign, and `80` for subset-observable utility studies.
- Circuit depth: `1,2,3,4,5,6,8,10,12` in the broader benchmark plan, narrowed to `1,2,3,4` for the active exact-short q14 campaign.
- Sampling: `3` trials per pilot/day in the frozen benchmark artifacts, with `10` trials named as the publication-quality target in `files/quantum-math-lab/hardware_advantage_protocol.md`.
- Runtime metrics: local wall-clock seconds from `/usr/bin/time -v` for classical runs, and `IBM quantum_seconds` for the active hardware runtime gate.

**Degrees of Freedom:**

- Qubit register initialized in `|0...0>` in `files/quantum-math-lab/qiskit_black_hole_scrambling.py`.
- Random brickwork scrambling unitary `U` with single-qubit `Rx/Rz` layers and staggered `CZ` couplings in `files/quantum-math-lab/qiskit_black_hole_scrambling.py`.
- Local perturbation `X_q`, usually at qubit `0`, with locality controls using perturbation on qubit `10` for subset `[10..19]` in the 80q evidence trail described in `STATUS.md` and `files/quantum-math-lab/results/hardware/summary/levelb_evidence_report.md`.

## Theoretical Framework

**Primary Framework:**

- Gate-model quantum circuit toy model for scrambling and echo recovery.
- Formulation: exact statevector evolution for feasible sizes plus sampled measurement histograms for noisy/hardware tracks.
- Files: `files/quantum-math-lab/qiskit_black_hole_scrambling.py`, `files/quantum-math-lab/qiskit_black_hole_hardware_runner.py`

**Secondary/Supporting Frameworks:**

- Finite-shot noisy simulator with depolarizing noise, readout flips, optional readout mitigation, and optional ZNE in `files/quantum-math-lab/qiskit_black_hole_scrambling.py`.
- IBM Runtime Sampler workflow with optional readout mitigation, subset observables, job reuse, and extra suppression options in `files/quantum-math-lab/qiskit_black_hole_hardware_runner.py`.
- Claim-governance framework for Level A / B / C and the later q14-only narrowing in `files/quantum-math-lab/hardware_advantage_protocol.md`, `files/quantum-math-lab/benchmarks/levelc_manifest.json`, and `files/quantum-math-lab/benchmarks/q14_only_manifest.json`.

## Fundamental Equations

**Governing Equations:**

| Equation | Type | Location | Status |
| -------- | ---- | -------- | ------ |
| Ideal Loschmidt echo `|<psi0|U^\dagger U|psi0>|^2` | sanity observable | `files/quantum-math-lab/qiskit_black_hole_scrambling.py` | Derived / implemented |
| Perturbed echo `|<psi0|U^\dagger X_q U|psi0>|^2` | benchmark observable | `files/quantum-math-lab/qiskit_black_hole_scrambling.py` | Derived / implemented |
| Renyi-2 entropy `S2 = -log Tr(rho_A^2)` | entanglement diagnostic | `files/quantum-math-lab/qiskit_black_hole_scrambling.py` | Derived / implemented |
| OTOC proxy `F` and commutator proxy `C=(1-Re(F))/2` | scrambling diagnostic | `files/quantum-math-lab/qiskit_black_hole_scrambling.py` | Derived / implemented |
| Local-tensored readout assignment inversion | estimator correction | `files/quantum-math-lab/qiskit_black_hole_hardware_runner.py` | Implemented |

**Constraints:**

- Exact statevector reference is disabled beyond `24` qubits in `files/quantum-math-lab/qiskit_black_hole_hardware_runner.py`.
- Readout mitigation is capped to subsets of at most `12` qubits in `files/quantum-math-lab/qiskit_black_hole_hardware_runner.py`.
- The active campaign observable is the raw `perturbed_echo` exact-short q14 task, not the full legacy Level-C multi-size claim, per `STATUS.md` and `files/quantum-math-lab/benchmarks/q14_only_manifest.json`.

## Symmetries and Conservation Laws

**Exact Symmetries:**

- Unitarity of the scrambling circuit is used operationally through explicit inversion `U.inverse()` in `files/quantum-math-lab/qiskit_black_hole_scrambling.py`.

**Approximate / Diagnostic Structure:**

- Locality is treated as an empirical diagnostic rather than a formal symmetry: subset `[10..19]` shows almost no gap for perturbation on qubit `0` but a large reproducible gap for perturbation on qubit `10`, documented in `STATUS.md` and `files/quantum-math-lab/results/hardware/summary/levelb_evidence_report.md`.

**Gauge Symmetries / Ward Identities / Topology:**

- No gauge structure, Ward identities, anomaly bookkeeping, or topological invariants are present in this snapshot. The project is a circuit-model benchmark, not a field-theory derivation stack.

## Parameters and Couplings

**Fundamental Parameters:**

- `qubits`: system size, defined in both main Python CLIs and manifests.
- `depths`: scrambling depth list, frozen in `files/quantum-math-lab/benchmarks/levelc_manifest.json` and narrowed in `files/quantum-math-lab/benchmarks/q14_only_manifest.json`.
- `trials`, `shots`, `seed`: benchmark sampling controls, present in manifests and both runner scripts.
- `perturb_qubit`: local perturbation location.
- `subset_qubits`: subset-observable specification for scalable 80q mitigation.
- `noise_dep`, `noise_readout`, `mitigation_p_ro`: simulator-noise and mitigation controls in `files/quantum-math-lab/qiskit_black_hole_scrambling.py`.

**Derived Quantities:**

- `ideal_echo`, `perturbed_echo`, `ideal_subset_echo`, `perturbed_subset_echo`
- `renyi2`, `otoc_real`, `commutator_sq`
- `perturbed_abs_error_vs_exact` and runtime verdict quantities in hardware JSON outputs under `files/quantum-math-lab/results/hardware/`

## Phase Structure / Regimes

**Regimes Studied:**

- Exact-feasible small/medium regime: `q <= 14`, exact statevector reference available.
- Legacy Level-C route: `q12/q14` exact-short raw benchmarking with two-consecutive-size runtime requirement.
- Active regime: q14-only exact-short campaign with three independent day reproductions and `MAE <= 0.05` against exact.
- Large-system utility regime: `q80` subset observables with `--skip-exact` and subset-level mitigation.

**Known Limiting Cases:**

- Ideal echo should stay near `1` after `U^\dagger U`.
- Classical exact-short baselines for q12 and q14 provide the current runtime comparison anchor.
- No full 80-qubit global-overlap limit is validated in this snapshot; only subset observables are tracked.

## Units and Conventions

**Unit System:**

- Echoes, entropies, OTOC proxies, and MAEs are dimensionless.
- Runtime values are in seconds, but the project explicitly distinguishes local wall-clock seconds from IBM-reported `quantum_seconds`.
- No spacetime metric signature or continuum-field convention is relevant in the current artifact set.

**Key Conventions:**

- The scientifically meaningful claim is phrased around `perturbed_echo`, not `ideal_echo`, per `files/quantum-math-lab/results/hardware/summary/levelb_strengthening_and_levelc_plan_2026-03-15.md`.
- The active claim is narrower than legacy Level C and should not be described as full hardware advantage, per `STATUS.md` and `files/quantum-math-lab/results/hardware/summary/q14_only_campaign_plan_2026-03-16.md`.

---

_Framework analysis: 2026-03-17_
