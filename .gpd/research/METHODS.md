# Methods Research

**Domain:** quantum information scrambling and benchmarked quantum-circuit echoes
**Researched:** 2026-03-17
**Confidence:** MEDIUM

## Recommended Methods

### Analytical Methods

| Method | Purpose | Why Recommended |
| ------ | ------- | --------------- |
| Fixed-observable OLE definition plus small-`delta` expansion | Defines the actual target observable and its commutator-controlled onset | It is the minimum rigorous bridge from the current `perturbed_echo` baseline to the user's requested OLE benchmark |
| Exact q14 reference evaluation with the same `U`, `U^\dagger`, `G`, and fixed `O` | Produces the decisive benchmark artifact before hardware work | The repo already has an exact-short q14 discipline; this keeps the first claim anchored to a tractable exact reference |
| Support-structure analysis for overlap and disjoint variants | Tests whether the measured observable is actually sensitive to perturbation locality | The user explicitly wants both variants in scope, and the existing q80 subset controls already show this matters |
| Anti-butterfly / recovery-control reasoning | Separates genuine scrambling-style sensitivity from decay caused by noise or protocol mismatch | `2110.12355v2` shows decay alone is not enough for a trustworthy benchmark |

### Numerical Methods

| Method | Purpose | When to Use |
| ------ | ------- | ----------- |
| Exact statevector evolution and direct trace evaluation | Generate q14 ground-truth OLE curves and compare against `perturbed_echo` | First deliverable, exact-short depths, small-`delta` onset checks |
| Shot-based Sampler evaluation on IBM Runtime | Produce hardware-ready measurement estimates under the existing runner architecture | q14 hardware follow-up and all large-system work |
| Local-tensored subset readout mitigation | Stabilize large-system subset observables without pretending full-system mitigation is scalable | q80 subset route where full readout mitigation is infeasible |
| Local randomized-measurement OTOC estimator | Provides a hardware-friendly fallback if mirror-circuit OLE becomes too fragile | Alternative branch if backward/reverse-evolution path proves operationally weak |

### Computational Tools

| Tool | Version | Purpose | Notes |
| ---- | ------- | ------- | ----- |
| Python | 3.9+ in current repo tooling | Main execution environment | Existing scripts and artifacts already use this stack |
| Qiskit | `1.4.5` in recorded hardware artifacts | Circuit generation, transpilation, statevector, Sampler interfaces | Version seen in current benchmark artifacts, so it is the safest planning baseline |
| `qiskit_ibm_runtime` | `0.40.0` in recorded hardware artifacts | Hardware Sampler execution and metadata capture | Needed for the q14/q80 hardware path |
| `qiskit_aer` | `0.17.0` in recorded hardware artifacts | Local noise-aware checks and simulator support | Useful for pre-hardware sanity checks, not as a substitute for hardware evidence |
| NumPy | repo dependency | Numerical post-processing, averaging, fitting | Already part of the current scripts |

## Software Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
| ---------- | ------- | ------- | --------------- |
| `qiskit_black_hole_scrambling.py` | current repo snapshot | Exact and noisy classical baseline generation | It already defines the active q14 task family and should host the first OLE bridge |
| `qiskit_black_hole_hardware_runner.py` | current repo snapshot | IBM Runtime hardware execution | It already supports the q80 subset and mitigation workflow the user wants to preserve |
| Frozen benchmark manifests | `q14_only_manifest.json` and related summaries | Task-definition lock and claim discipline | The project already depends on frozen task definitions; new OLE work should follow the same pattern |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
| ------- | ------- | ------- | ----------- |
| `qiskit_experiments` | `0.7.0` in recorded artifacts | calibration / experiment support if needed | Only if future mitigation or calibration workflows require it |
| `circuit_knitting_toolbox` | `0.7.2` in recorded artifacts | ancillary tooling present in the environment | Not central to the first OLE benchmark |
| `/usr/bin/time -v` | system tool | classical runtime capture | Needed whenever runtime claims are discussed against classical baselines |

### Symbolic Computation

| Tool | Version | Purpose | Notes |
| ---- | ------- | ------- | ----- |
| lightweight manual derivation or optional SymPy | not pinned in snapshot | small commutator expansion and normalization checks | Useful only for short derivations; the main project is numerical/benchmarking, not CAS-driven |

## Installation

```bash
# Existing project stack is already embedded in the repo workflow.
# Use the current qiskit environment and scripts rather than creating a new stack.

# Typical execution entry points in this snapshot:
scripts/run-in-qiskit-venv.sh python qiskit_black_hole_scrambling.py ...
scripts/run-in-qiskit-venv.sh python qiskit_black_hole_hardware_runner.py ...
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
| ----------- | ----------- | ----------------------- |
| Exact q14 OLE trace evaluation | Purely perturbative symbolic treatment | Only for a short derivation note; not sufficient for the first success gate |
| Mirror-circuit / existing echo architecture | Full randomized-measurement workflow | Use if backward-evolution OLE mapping becomes too brittle or too hardware-expensive |
| q80 subset observable path | Attempted global 80q overlap or full-system OLE | Only if a genuinely scalable proxy is derived and validated; not for the current snapshot |
| Same-task comparison against existing `perturbed_echo` baseline | Fresh standalone OLE campaign | Use only later; the user explicitly wants continuity with the current q14/q80 program |

## What NOT to Use

| Avoid | Why | Use Instead |
| ----- | --- | ----------- |
| Renaming existing `perturbed_echo` outputs as OLE | It would fake progress and break the fixed-observable requirement | Implement explicit `O`, `G`, and `delta` handling with its own observable label |
| Global 80q overlap as the first large-system target | The repo already documents why this loses contrast and is not mitigation-scalable | Keep q80 work subset-observable unless a separate full-q80 proxy is justified |
| Comparing IBM `quantum_seconds` to unrelated wall-clock numbers | It breaks the repo's claim discipline | Use manifest-frozen same-task runtime comparisons only |
| Aer depolarizing scaling as "hardware ZNE" | The hardware protocol already warns this is not a valid hardware claim | Use raw or readout-mitigated hardware first; only add hardware-valid scaling later |

## Method Selection by Problem Type

**If the problem is the first q14 benchmark gate:**

- Use exact statevector evaluation of fixed-observable OLE across a small `delta` sweep.
- Because the deliverable is explicitly a q14 exact/classical benchmark against the current baseline.

**If the problem is hardware readiness on the same task family:**

- Use the existing hardware runner architecture, with explicit fixed observables and frozen subset definitions.
- Because this preserves continuity with the repo's existing evidence and reporting discipline.

**If the problem is a large-system exploratory extension:**

- Use subset observables with locality controls and mitigation.
- Because the current q80 evidence supports this path, while full-system fidelity does not scale.

**If the mirror-circuit OLE route becomes operationally fragile:**

- Use randomized-measurement OTOC estimation as a backup method.
- Because the literature provides a hardware-tested path that avoids backward evolution entirely.

## Validation Strategy by Method

| Method | Validation Approach | Key Benchmarks |
| ------ | ------------------- | -------------- |
| Fixed-observable OLE small-`delta` benchmark | Check intercept near `1`, quadratic onset in `delta^2`, and agreement with the commutator coefficient in the exact q14 regime | Algorithmiq small-`delta` formula; q14 exact reference |
| Bridge to current `perturbed_echo` workflow | Overlay OLE-vs-`delta^2` with the current q14 `perturbed_echo` baseline and make the distinction explicit | `q14_only_manifest.json` and current exact-short artifacts |
| Locality / support controls | Compare overlap-support and disjoint-support observables or perturbation placements | Existing q80 subset locality controls in `levelb_evidence_report.md` |
| Hardware-readiness checks | Freeze backend, shots, mitigation mode, and observable subset definitions; compare raw vs mitigated on the same task | Existing q14/q80 hardware reporting pattern |

## Version Compatibility

| Tool A | Compatible With | Notes |
| ------ | --------------- | ----- |
| `qiskit_ibm_runtime-0.40.0` | `qiskit-1.4.5` | Seen together in current benchmark artifacts |
| `qiskit_aer-0.17.0` | `qiskit-1.4.5` | Current local simulation stack in recorded artifacts |

## Sources

- `STATUS.md` -- active q14-only claim discipline and q80 subset guardrails.
- `files/quantum-math-lab/benchmarks/q14_only_manifest.json` -- frozen task definition for the first benchmark gate.
- `files/quantum-math-lab/hardware_advantage_protocol.md` -- current hardware benchmarking logic and what not to overclaim.
- `files/quantum-math-lab/results/hardware/summary/levelb_evidence_report.md` -- q80 subset locality evidence.
- Yan, Cincio, Zurek (`1903.02651v4`) -- LE/OTOC bridge.
- Vermersch et al. (`1807.09087v2`) and Joshi et al. (`2001.02176v2`) -- randomized-measurement scrambling methods.
- Harris, Yan, Sinitsyn (`2110.12355v2`) -- anti-butterfly benchmark logic.
- Kastner, Osterholz, Gross (`2403.08670v1`) -- ancilla-free backward-evolution route.
