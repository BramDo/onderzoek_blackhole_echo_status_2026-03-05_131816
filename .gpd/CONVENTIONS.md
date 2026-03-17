# Conventions Ledger

**Project:** Operator Loschmidt Echo extension of q14/q80 scrambling benchmarks
**Created:** 2026-03-17
**Last updated:** 2026-03-17 (Initialization)

> This file records the conventions locked at project initialization. For this circuit-model project,
> several generic physics fields are bookkeeping defaults rather than active continuum assumptions.

---

## Core Lock

### Unit System

| Field | Value |
| ----- | ----- |
| **Convention** | `natural_units = natural` |
| **Introduced** | Initialization |
| **Rationale** | GPD expects a unit convention lock. In practice this project uses dimensionless circuit observables and reports runtime metrics in seconds. |
| **Dependencies** | benchmark labeling, glossary entries, later derivation headers |

### Metric Signature

| Field | Value |
| ----- | ----- |
| **Convention** | `metric_signature = euclidean` |
| **Introduced** | Initialization |
| **Rationale** | No spacetime metric is active in the present circuit-model benchmark; `euclidean` is a bookkeeping default rather than a physical input to current calculations. |
| **Dependencies** | only relevant if later continuum or field-theory notation is introduced |

### Fourier Convention

| Field | Value |
| ----- | ----- |
| **Convention** | `fourier_convention = physics` |
| **Introduced** | Initialization |
| **Rationale** | Dormant default for any future transform notation. No active Fourier-transform calculation is central to the current benchmark. |
| **Dependencies** | later analytical notes if momentum/frequency-space expressions are introduced |

### State Normalization

| Field | Value |
| ----- | ----- |
| **Convention** | `state_normalization = non-relativistic` |
| **Introduced** | Initialization |
| **Rationale** | Computational-basis and statevector objects use the standard quantum-information inner product with `<psi|psi> = 1`. |
| **Dependencies** | state overlaps, exact return probabilities, hardware baseline interpretation |
| **Test value** | `|0...0>` has norm `1` |

---

## Project-Specific Custom Conventions

### Observable Normalization

| Field | Value |
| ----- | ----- |
| **Convention** | `Tr(O^2) = 1` for fixed-observable OLE |
| **Introduced** | Initialization |
| **Rationale** | This matches the OLE definition adopted in the project contract and prevents normalization drift when moving from Pauli strings to subset observables. |
| **Dependencies** | OLE magnitude, small-`delta` coefficient, q14 benchmark comparability |
| **Test value** | If `P` is an `n`-qubit Pauli string, use `O = P / sqrt(2^n)` when the benchmark requires `Tr(O^2)=1` |

### Operator Picture

| Field | Value |
| ----- | ----- |
| **Convention** | Use `f_delta(O) = 2^{-n} Tr(U O U^dagger V_delta^dagger U O U^dagger V_delta)` as the defining expression; translate the small-`delta` commutator form consistently from that choice. |
| **Introduced** | Initialization |
| **Rationale** | The literature mixes `U O U^dagger` and `U^dagger O U` conventions. This project freezes one defining expression and requires any equivalent rewriting to be explicit. |
| **Dependencies** | derivations, code comments, benchmark notes, OTOC bridge statements |

### Qubit Indexing and Subset Support

| Field | Value |
| ----- | ----- |
| **Convention** | Qubits are indexed `0..n-1` as in Qiskit; subset observables must state their support set `S` explicitly. |
| **Introduced** | Initialization |
| **Rationale** | The q80 route depends on subset observables and locality controls, so support labels must never remain implicit. |
| **Dependencies** | filenames, plots, hardware notes, overlap/disjoint support comparisons |
| **Test value** | CLI interval `0-9` denotes subset support `{0,1,...,9}` |

### Perturbation Convention

| Field | Value |
| ----- | ----- |
| **Convention** | `V_delta = exp(-i delta G)` with an explicit generator `G`; support overlap with `O` must be stated when relevant. |
| **Introduced** | Initialization |
| **Rationale** | The user explicitly wants both overlap-support and disjoint-support variants kept visible. |
| **Dependencies** | small-`delta` expansion, locality tests, q14 and q80 benchmark definitions |

### Baseline Naming Guardrail

| Field | Value |
| ----- | ----- |
| **Convention** | `perturbed_echo` denotes the state-return benchmark `|<psi0|U^dagger X U|psi0>|^2` for `psi0 = |0...0>`; it is a baseline and must not be labeled as OLE. |
| **Introduced** | Initialization |
| **Rationale** | This is the main semantic guardrail of the project. The whole roadmap depends on a real bridge from the current baseline to OLE, not a rename. |
| **Dependencies** | PROJECT.md wording, roadmap success criteria, future figure captions, hardware notes |

---

## Convention Update Rule

If a later phase changes any of these conventions, append a new entry and mark the prior one as superseded. Do not silently overwrite the original initialization choice.
