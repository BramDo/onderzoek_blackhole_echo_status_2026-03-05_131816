# Phase 1 Formalism Lock: q14 Fixed-Observable OLE

**Locked:** 2026-03-17
**Scope:** first q14 exact benchmark in the existing q14/q80 scrambling workflow

## Purpose

This note freezes the first fixed-observable OLE benchmark so Phase 2 can execute a real q14 `delta^2` onset study without drifting back into the existing `perturbed_echo` state-return observable.

## Fixed Benchmark Objects

### System and support labels

- Qubit count: `n = 14`
- Qubit labels: `0,1,...,13` in Qiskit ordering
- Scrambling unitary: the existing brickwork `U` from `qiskit_black_hole_scrambling.py`

### Fixed observable

- Pauli benchmark observable: `P = Z_0`
- Hilbert-Schmidt-normalized observable:

  $$
  O = \frac{P}{\sqrt{2^n}} = \frac{Z_0}{\sqrt{2^{14}}}
  $$

- Support label: `supp(P) = {0}`

### Perturbation generators

- Overlap benchmark generator: `G_overlap = X_0`
- Disjoint control generator: `G_disjoint = X_10`
- Perturbation unitary:

  $$
  V_\delta(G) = e^{-i \delta G}
  $$

- Support labels:
  - `supp(G_overlap) = {0}`
  - `supp(G_disjoint) = {10}`

## Report-Level OLE Quantity

The default q14 benchmark curve will be reported in the Pauli-specialized unit-intercept form

$$
F_\delta(P) = 2^{-n}\operatorname{Tr}\!\left(U P U^\dagger V_\delta^\dagger U P U^\dagger V_\delta\right).
$$

For the frozen choice `P = Z_0`, this gives

$$
F_0(P) = 2^{-n}\operatorname{Tr}(P^2) = 1
$$

because `P^2 = I`.

The Hilbert-Schmidt-normalized operator form remains available and is related by

$$
f_\delta(O) = 2^{-n}\operatorname{Tr}\!\left(U O U^\dagger V_\delta^\dagger U O U^\dagger V_\delta\right)
           = 2^{-n} F_\delta(P),
$$

so

$$
f_0(O) = 2^{-n}.
$$

### Why the project will plot `F_delta(P)` first

- The first q14 benchmark is an onset plot against `delta^2`; a unit intercept is easier to inspect and fit.
- The existing project wording mixed `Tr(O^2)=1` with a near-`1` intercept narrative.
- Using `F_delta(P)` as the report-level quantity resolves that mismatch without losing the normalized-operator translation.

## Compatibility With The Existing Baseline

`perturbed_echo` remains the state-return baseline

$$
\left|\langle \psi_0 | U^\dagger X_q U | \psi_0 \rangle\right|^2
$$

for `|psi0> = |0...0>`. The bridge to OLE is continuity of local support and perturbation family, not equality of observables.

What is reused from the existing repo:

- the same q14 manifest and seed/depth family
- the same local Pauli-X kick semantics
- the same overlap/disjoint locality language (`q = 0` versus `q = 10`)

What is new:

- an explicit fixed observable `P = Z_0`
- an operator-space correlator instead of a state-return probability
- an explicit normalization translation between `F_delta(P)` and `f_delta(O)`

## Depth-0 Control Limits

Write

$$
A_P = U P U^\dagger.
$$

At depth `0`, `U = I`, so `A_P = P = Z_0`.

### Overlap control

For `G = X_0`,

$$
[G, P] = [X_0, Z_0] = -2 i Y_0 \neq 0.
$$

Hence the quadratic small-`delta` coefficient is nonzero at depth `0`.

### Disjoint control

For `G = X_10`,

$$
[G, P] = [X_{10}, Z_0] = 0,
$$

so the quadratic small-`delta` coefficient vanishes at depth `0`.

This is the control separation Phase 2 must preserve when it moves to nontrivial scrambling depth.

## Locked Interpretation

- `F_delta(P)` is the primary plotted q14 OLE curve for the first benchmark.
- `f_delta(O)` is the normalized translation that remains available for manuscript notation and cross-checks.
- `perturbed_echo` is only a baseline overlay. It is not to be relabeled as OLE.
- q80 remains subset-observable unless a later phase establishes a distinct full-system proxy.

## Carry-Forward Items For Phase 2

- Benchmark observable: `P = Z_0`
- Normalized operator translation: `O = Z_0 / sqrt(2^14)`
- Overlap generator: `G = X_0`
- Disjoint control generator: `G = X_10`
- Plot `F_delta(P)` against `delta^2`
- When normalized notation is required, report `f_delta(O) = 2^{-14} F_delta(P)` explicitly
