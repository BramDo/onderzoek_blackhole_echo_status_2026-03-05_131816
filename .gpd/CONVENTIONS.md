# Conventions Ledger

**Project:** Operator Loschmidt Echo extension of q14/q80 scrambling benchmarks
**Created:** 2026-03-17
**Last updated:** 2026-03-17 (Phase 1 formalism lock)

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

## Phase 1 Formalism Lock

### Benchmark Observable and Generator Lock

| Field | Value |
| ----- | ----- |
| **Convention** | First q14 benchmark uses `P = Z_0`, overlap `G = X_0`, and disjoint control `G = X_10`. |
| **Introduced** | Phase 1 |
| **Rationale** | This keeps the fixed-observable OLE benchmark aligned with the existing local-X kick baseline and the repo's current locality language. |
| **Dependencies** | q14 benchmark figure, overlap/disjoint control study, Phase 2 handoff |
| **Test value** | `supp(P) = {0}`, `supp(G_overlap) = {0}`, `supp(G_disjoint) = {10}` |

### Report-Level OLE Convention

| Field | Value |
| ----- | ----- |
| **Convention** | Report the first q14 curve as `F_delta(P) = 2^{-n} Tr(U P U^dagger V_delta^dagger U P U^dagger V_delta)` with `P^2 = I`, so `F_0(P) = 1`. |
| **Introduced** | Phase 1 |
| **Rationale** | The initialization wording mixed a Hilbert-Schmidt-normalized `O` with a unit-intercept-style onset narrative. Reporting `F_delta(P)` resolves the intercept ambiguity while preserving the normalized translation. |
| **Dependencies** | fit-window tests, figure captions, Phase 2 bridge derivation |
| **Test value** | For `P = Z_0`, `F_0(P) = 2^{-14} Tr(I) = 1` |

### Normalized-Operator Translation

| Field | Value |
| ----- | ----- |
| **Convention** | Keep `O = P / sqrt(2^n)` as the Hilbert-Schmidt-normalized observable, with `f_delta(O) = 2^{-n} F_delta(P)` and `f_0(O) = 2^{-n}`. |
| **Introduced** | Phase 1 |
| **Rationale** | This preserves compatibility with the user's normalized-operator notation while keeping the benchmark plot interpretable. |
| **Dependencies** | theory notes, glossary entries, later manuscript notation |
| **Test value** | For `n = 14`, `f_0(O) = 2^{-14}` |

### Canonical Bookkeeping Lock Completion

These canonical fields are now explicitly set in `state.json.convention_lock` so formalism and derivation phases pass the GPD convention gate. For this circuit-model project they are bookkeeping guardrails, not active continuum assumptions.

| Field | Value |
| ----- | ----- |
| `gauge_choice` | not applicable (no gauge field in gate-model circuit benchmark) |
| `regularization_scheme` | not applicable (finite-dimensional Hilbert space; no UV regulator) |
| `renormalization_scheme` | not applicable (no renormalized continuum coupling in current scope) |
| `coordinate_system` | Qiskit qubit index ordering `0..n-1` |
| `spin_basis` | computational basis with Pauli operators `X,Y,Z` in the standard qubit basis |
| `coupling_convention` | brickwork gate angles are used directly; no separate continuum coupling convention |
| `index_positioning` | qubit and operator labels are positional only; no covariant/contravariant distinction |
| `time_ordering` | circuit gates are ordered by layer depth from left to right in circuit time |
| `commutation_convention` | `[A,B]=AB-BA`; Pauli commutators use `[X,Z]=-2iY` and `[Z,X]=2iY` |
| `levi_civita_sign` | `epsilon_xyz = +1` for Pauli-axis orientation when used |
| `generator_normalization` | single-qubit Pauli generators square to identity; no `1/2` factor unless stated |
| `covariant_derivative_sign` | not applicable (no covariant derivative in the circuit benchmark) |
| `gamma_matrix_convention` | not applicable (no gamma matrices in the circuit benchmark) |
| `creation_annihilation_order` | not applicable (no creation/annihilation ordering is used in the current scope) |

---

## Convention Update Rule

If a later phase changes any of these conventions, append a new entry and mark the prior one as superseded. Do not silently overwrite the original initialization choice.
