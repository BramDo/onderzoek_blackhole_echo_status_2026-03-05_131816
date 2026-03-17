# Convention and Methodology Map

**Analysis Date:** 2026-03-17

## Derivation / Estimator Inventory

**Exact scrambling observables:**

- Result: exact `ideal_echo`, `perturbed_echo`, `renyi2`, `otoc_real`, and `commutator_sq`
- File: `files/quantum-math-lab/qiskit_black_hole_scrambling.py`
- Method: exact statevector evolution
- Status: complete in code for feasible qubit counts

**Hardware estimators:**

- Result: raw and optionally readout-mitigated echo estimates, plus `summary_by_depth`
- File: `files/quantum-math-lab/qiskit_black_hole_hardware_runner.py`
- Method: IBM Runtime Sampler counts with optional local-tensored mitigation
- Status: complete in code

**Claim-gating layer:**

- Result: campaign-level pass/fail verdicts based on MAE and runtime gates
- Files: `run_q14_only_exact_short_day.ps1`, `run_levelc_exact_short_day.ps1`, `files/quantum-math-lab/benchmarks/*.json`
- Status: operational, but legacy naming remains in the wrapper

## Approximations Made

**Random brickwork toy model:**

- What is neglected: any first-principles derivation from a concrete black-hole Hamiltonian or gravity dual
- Justification given: toy-model scrambling benchmark language in `files/quantum-math-lab/README.md` and `files/quantum-math-lab/hardware_advantage_protocol.md`
- Justification quality: adequate for benchmarking, weak for literal black-hole claims
- File: `files/quantum-math-lab/qiskit_black_hole_scrambling.py`

**Subset-observable replacement at 80 qubits:**

- What is neglected: full 80-qubit string-overlap / global fidelity
- Justification given: global overlap is too fragile to readout/SPAM and full mitigation is not scalable
- Justification quality: explicitly documented and defensible, but still an observable restriction
- Files: `STATUS.md`, `files/quantum-math-lab/hardware_advantage_protocol.md`

**Exact-reference cutoff above 24 qubits:**

- What is neglected: exact full-state benchmark beyond `24` qubits
- Justification given: exact statevector reference is not feasible in the workflow
- File: `files/quantum-math-lab/qiskit_black_hole_hardware_runner.py`

## Assumptions Catalog

**Explicit Assumptions:**

- Fixed state preparation `|0...0>` for every benchmark track
- Fixed observable family centered on `perturbed_echo`
- Fixed seeds, depths, trials, and shots in the manifests
- Fixed runtime gate on `IBM quantum_seconds` for the active q14-only claim

**Implicit Assumptions:**

- Local-tensored readout mitigation is informative enough for subset observables
- `IBM quantum_seconds` is an acceptable comparator against classical wall-clock seconds for the frozen campaign claim
- Three trial seeds per day are sufficient for campaign-level stability in the current phase

## Mathematical Rigor Assessment

**Circuit definitions and estimators:**

- Rigor level: physicist-standard / implementation-rigorous
- Strength: the core observables are defined explicitly in code and tied to frozen benchmark manifests
- Weakness: the bridge from scrambling toy to broader black-hole language is heuristic, not derived in-project

## Dimensional Analysis

**Consistency Checks:**

- Echo probabilities, subset echoes, MAEs, and OTOC-derived quantities are dimensionless
- Runtime fields are in seconds, but the project correctly distinguishes local elapsed time from IBM usage metrics

**Dimensional Anomalies / Risks:**

- Communication risk arises if local wall time and `quantum_seconds` are mixed in prose; the summary notes explicitly warn against that

## Sign and Factor Conventions

**Sign Choices and Observable Definitions:**

- Perturbed echo is always `U^\dagger X U`, not `U X U^\dagger`
- OTOC proxy is reported through `Re(F)` and `C=(1-Re(F))/2`
- Subset ranges such as `0-9` and `10-19` are inclusive

**Bit and Index Conventions:**

- Qiskit count strings are interpreted as `c[n-1]..c[0]`; helper `_bit_from_qiskit_bitstring` compensates for that in `files/quantum-math-lab/qiskit_black_hole_hardware_runner.py`
- The older README states an MSB-to-LSB subsystem convention for tensor products

**Factor Tracking:**

- Readout mitigation uses per-qubit `p01/p10` parameters and clips negative mass after pseudoinverse correction

## Notation Consistency

**Consistent Usage:**

- `depth`, `trial`, `shots`, `perturb_qubit`, `subset_qubits`, `readout_mitigation`, and `summary_by_depth` are used consistently across the manifests and emitted JSON

**Conflicts / Drift:**

- `run_levelc_exact_short_day.ps1` still carries legacy Level-C naming even though it now only forwards to the active q14-only runner
- `STATUS.md` carefully distinguishes “narrow q14-only runtime advantage” from full Level C, but older filenames can still suggest the broader claim if read in isolation

---

_Methodology analysis: 2026-03-17_
