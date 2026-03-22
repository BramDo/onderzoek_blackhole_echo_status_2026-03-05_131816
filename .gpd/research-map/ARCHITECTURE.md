# Computational Architecture

**Analysis Date:** 2026-03-17

## Mathematical Setting

**Spaces:**

- `n`-qubit Hilbert space of dimension `2^n` for exact statevector evolution
  - Files: `files/quantum-math-lab/qiskit_black_hole_scrambling.py`, `files/quantum-math-lab/qiskit_black_hole_hardware_runner.py`
- Measurement histogram space over bitstrings of length `n`
  - Files: `files/quantum-math-lab/qiskit_black_hole_scrambling.py`, `files/quantum-math-lab/qiskit_black_hole_hardware_runner.py`
- Subset histogram space over selected qubit subsets for scalable mitigation at 80 qubits
  - File: `files/quantum-math-lab/qiskit_black_hole_hardware_runner.py`

**Key Mathematical Objects:**

| Object | Type | Symbol / Name | Defined In |
| ------ | ---- | ------------- | ---------- |
| Scrambling circuit | `QuantumCircuit` | `U` | `files/quantum-math-lab/qiskit_black_hole_scrambling.py` |
| Trial result container | dataclass | `RunResult` | `files/quantum-math-lab/qiskit_black_hole_scrambling.py` |
| Hardware pair metadata | dataclass | `PairMeta` | `files/quantum-math-lab/qiskit_black_hole_hardware_runner.py` |
| Readout assignment matrix | dense matrix | `A` | both Python runners |
| Frozen benchmark task | JSON manifest | `benchmark_id` | `files/quantum-math-lab/benchmarks/*.json` |

## Computational Pipeline

1. Freeze the task definition and claim language
   - Inputs: `files/quantum-math-lab/hardware_advantage_protocol.md`, `files/quantum-math-lab/benchmarks/levelc_manifest.json`, `files/quantum-math-lab/benchmarks/q14_only_manifest.json`
   - Outputs: reproducible benchmark parameters and pass/fail criteria

2. Generate exact or noisy classical reference curves
   - Script: `files/quantum-math-lab/qiskit_black_hole_scrambling.py`
   - Outputs: JSON summaries under `files/quantum-math-lab/results/benchmark/classical/` plus `/usr/bin/time -v` logs

3. Build hardware circuits, transpile, and execute via IBM Runtime Sampler
   - Script: `files/quantum-math-lab/qiskit_black_hole_hardware_runner.py`
   - Outputs: hardware JSON artifacts under `files/quantum-math-lab/results/hardware/`

4. Optionally run calibration circuits and local-tensored readout mitigation
   - Script: `files/quantum-math-lab/qiskit_black_hole_hardware_runner.py`
   - Outputs: `calibration` sections and `readout_mitigated` summaries in the hardware JSON files

5. Apply campaign-level gates
   - Scripts: `run_q14_only_exact_short_day.ps1`, `run_levelc_exact_short_day.ps1`
   - Outputs: timing sidecars, stdout logs, and pass/fail exit codes for daily campaign operation

6. Curate status and evidence summaries
   - Inputs: hardware JSON, classical timing files, summary markdowns
   - Outputs: `STATUS.md` and files under `files/quantum-math-lab/results/hardware/summary/`

## Key Algorithms

- Random brickwork scrambler
  - Alternating single-qubit `Rx/Rz` layers plus staggered `CZ` couplings
  - Implementation: `files/quantum-math-lab/qiskit_black_hole_scrambling.py`

- Exact echo / OTOC evaluation
  - Uses `Statevector` evolution and direct overlap calculations
  - Implementation: `files/quantum-math-lab/qiskit_black_hole_scrambling.py`

- Noisy classical fallback
  - Uses `qiskit-aer` when available, otherwise probability mixing plus sampled readout flips
  - Implementation: `files/quantum-math-lab/qiskit_black_hole_scrambling.py`

- Hardware histogram extraction
  - Supports SamplerV1 and SamplerV2 result shapes and optional job reuse
  - Implementation: `files/quantum-math-lab/qiskit_black_hole_hardware_runner.py`

- Local-tensored readout mitigation
  - Estimates per-qubit `p01/p10`, builds tensor-product assignment matrices, and applies a pseudoinverse
  - Implementation: `files/quantum-math-lab/qiskit_black_hole_hardware_runner.py`

- Extra hardware suppression
  - Optional dynamical decoupling plus gate twirling
  - Implementation: `files/quantum-math-lab/qiskit_black_hole_hardware_runner.py`

## Numerical Methods

- Mean/std aggregation over fixed random seeds per depth in `files/quantum-math-lab/qiskit_black_hole_scrambling.py`
- Hardware `runs` plus `summary_by_depth` aggregation in `files/quantum-math-lab/qiskit_black_hole_hardware_runner.py`
- Exact references skipped above `24` qubits and replaced by subset-only observables at `80` qubits

## Computational Architecture

**Directory Layout:**

```
[project-root]/
+-- STATUS.md
+-- run_q14_only_exact_short_day.ps1
+-- run_levelc_exact_short_day.ps1
+-- files/quantum-math-lab/
    +-- qiskit_black_hole_scrambling.py
    +-- qiskit_black_hole_hardware_runner.py
    +-- hardware_advantage_protocol.md
    +-- benchmarks/
    +-- results/
    +-- scripts/run-levelc-bundle.sh
```

## Boundary and Initial Conditions

**Initial Conditions:**

- State preparation is fixed to `|0...0>` in both manifests and both Python runners.
- The default perturbation is qubit `0`; locality-control artifacts also use perturbation on qubit `10`.
- Randomness is frozen with seed family `424242` at the manifest level.

**Operational Boundaries:**

- `run_levelc_exact_short_day.ps1` no longer performs a distinct legacy flow; it forwards to the active q14-only runner.
- The snapshot now contains the helper launcher `scripts/run-in-qiskit-venv.sh`, so the README and shell-bundle commands are again runnable from the packed repo.

---

_Architecture analysis: 2026-03-17_
