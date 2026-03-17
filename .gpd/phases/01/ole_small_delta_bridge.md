# Phase 1 Small-Delta Bridge: q14 Pauli-Specialized OLE

**Written:** 2026-03-17
**Scope:** Phase 1 handoff from the formalism lock to the q14 exact benchmark

## Purpose

This note turns the Phase 1 lock into the exact small-`delta` bridge that Phase 2 should implement. The primary benchmark quantity stays in one fixed operator picture so the quadratic coefficient, the `delta = 0` intercept, and the overlap/disjoint controls all refer to the same object.

## Fixed Benchmark Picture

Use the frozen q14 choices from `ole_formalism_lock.md`:

- `n = 14`
- `P = Z_0`
- `G_overlap = X_0`
- `G_disjoint = X_10`
- `V_delta(G) = exp(-i delta G)`

Define the evolved Pauli observable

$$
A_P(U) = U P U^\dagger.
$$

The report-level q14 benchmark quantity is

$$
F_\delta(P;U,G)
= 2^{-n}\operatorname{Tr}\!\left(A_P(U)\,V_\delta(G)^\dagger\,A_P(U)\,V_\delta(G)\right)
= 2^{-n}\operatorname{Tr}\!\left(A_P(U)\,e^{i\delta G}\,A_P(U)\,e^{-i\delta G}\right).
$$

For the locked Pauli observable `P = Z_0`, `P^2 = I`, so `A_P(U)^2 = I` and therefore

$$
F_0(P;U,G) = 2^{-n}\operatorname{Tr}(I) = 1.
$$

This is the quantity that Phase 2 should plot against `delta^2`.

## Translation To Normalized OLE Notation

The Hilbert-Schmidt-normalized operator is

$$
O = \frac{P}{\sqrt{2^n}} = \frac{Z_0}{\sqrt{2^{14}}}.
$$

With `A_O(U) = U O U^\dagger = A_P(U) / \sqrt{2^n}`, the normalized OLE is

$$
f_\delta(O;U,G)
= 2^{-n}\operatorname{Tr}\!\left(A_O(U)\,V_\delta(G)^\dagger\,A_O(U)\,V_\delta(G)\right)
= 2^{-n} F_\delta(P;U,G).
$$

Hence

$$
f_0(O;U,G) = 2^{-n}.
$$

The project should report `F_delta(P)` in figures and carry `f_delta(O) = 2^{-14} F_delta(P)` as the normalized translation in text and verification.

## Translation To The Alternate `U^\dagger O U` Picture

Some literature writes the evolved observable as

$$
\widetilde{A}_O(U) = U^\dagger O U.
$$

That is a different picture choice. To keep the quantity unchanged, the perturbation generator must be rotated with it:

$$
\widetilde{G}(U) = U^\dagger G U,
\qquad
\widetilde{V}_\delta(U,G) = U^\dagger V_\delta(G) U = e^{-i\delta \widetilde{G}(U)}.
$$

Then the same normalized OLE can be written as

$$
f_\delta(O;U,G)
= 2^{-n}\operatorname{Tr}\!\left(\widetilde{A}_O(U)\,\widetilde{V}_\delta(U,G)^\dagger\,\widetilde{A}_O(U)\,\widetilde{V}_\delta(U,G)\right).
$$

The practical rule for this project is simple:

- Primary picture: `A_P(U) = U P U^\dagger`
- Primary generator: the fixed lab-frame Pauli `G = X_0` or `G = X_10`
- Do not mix the `U O U^\dagger` defining expression with a commutator written as `[G, U^\dagger O U]` unless `G` has also been rotated to `U^\dagger G U`

## Small-`delta` Expansion In The Fixed Picture

Using

$$
e^{i\delta G} A_P e^{-i\delta G}
= A_P + i\delta [G,A_P] - \frac{\delta^2}{2}[G,[G,A_P]] + O(\delta^3),
$$

the benchmark curve becomes

$$
F_\delta(P;U,G)
= 2^{-n}\operatorname{Tr}(A_P^2)
+ i\delta\,2^{-n}\operatorname{Tr}\!\left(A_P [G,A_P]\right)
- \frac{\delta^2}{2}\,2^{-n}\operatorname{Tr}\!\left(A_P [G,[G,A_P]]\right)
+ O(\delta^3).
$$

The linear term vanishes by cyclicity of the trace. For Hermitian `A_P` and `G`,

$$
\operatorname{Tr}\!\left(A_P [G,[G,A_P]]\right)
= \operatorname{Tr}\!\left([G,A_P][G,A_P]^\dagger\right),
$$

so the quadratic onset is

$$
F_\delta(P;U,G)
= 1 - \frac{\delta^2}{2}\,\kappa_G(P;U) + O(\delta^4),
$$

with

$$
\kappa_G(P;U)
= 2^{-n}\operatorname{Tr}\!\left([G,A_P(U)][G,A_P(U)]^\dagger\right)
\ge 0.
$$

Equivalently,

$$
f_\delta(O;U,G)
= 2^{-n}\left[1 - \frac{\delta^2}{2}\,\kappa_G(P;U) + O(\delta^4)\right].
$$

This is the exact coefficient structure that Phase 2 should fit near `delta = 0`.

## Depth-0 Control Limits

At depth `0`, `U = I`, so `A_P = P = Z_0`.

### Overlap control: `G = X_0`

$$
[X_0,Z_0] = -2 i Y_0,
$$

hence

$$
\kappa_{X_0}(Z_0;I)
= 2^{-14}\operatorname{Tr}\!\left(4 I\right)
= 4.
$$

Therefore

$$
F_\delta(Z_0;I,X_0) = 1 - 2\delta^2 + O(\delta^4).
$$

The exact one-qubit rotation check is

$$
F_\delta(Z_0;I,X_0) = \cos(2\delta),
$$

which matches the quadratic onset above.

### Disjoint control: `G = X_10`

$$
[X_{10},Z_0] = 0,
$$

so

$$
\kappa_{X_{10}}(Z_0;I) = 0
\qquad\text{and}\qquad
F_\delta(Z_0;I,X_{10}) = 1
$$

exactly at depth `0`.

These are the locality controls that Phase 2 must preserve at nonzero scrambling depth.

## Relation To The Existing `perturbed_echo` Baseline

The current repo baseline is the state-return quantity

$$
\mathrm{perturbed\_echo}(U,q)
= \left|\langle 0\cdots 0|U^\dagger X_q U|0\cdots 0\rangle\right|^2.
$$

It is not the same observable as `F_delta(P)`. The bridge is narrower and should be stated explicitly:

- both use the same q14 task family and the same local Pauli-`X` perturbation family
- the existing baseline corresponds to the large-kick endpoint `V_{\pi/2}(X_q) = -i X_q`
- the first OLE benchmark studies the small-`delta` onset of a fixed operator correlator, not the state-return probability at a full `X` kick

That makes `perturbed_echo` a comparison baseline, not an identity or a hidden special case of the plotted OLE curve.

## Phase 2 Carry-Forward Rules

- Plot `F_delta(Z_0)` against `delta^2` as the primary q14 benchmark quantity.
- Report `f_delta(Z_0 / sqrt(2^14)) = 2^{-14} F_delta(Z_0)` when normalized notation is needed.
- Fit only inside a shrinking small-`delta` window where both the intercept and quadratic coefficient remain stable.
- Run both support variants: overlap `G = X_0` and disjoint `G = X_10`.
- Keep `perturbed_echo` as a labeled baseline overlay or comparison marker only.
- Do not write `[G, U^\dagger O U]` unless the perturbation has also been rotated into the same picture.

## Phase 1 Deliverable Checklist

- Defining expression in one fixed operator picture
- Explicit translation to any alternate picture used in the literature
- delta=0 intercept and O(delta^2) coefficient structure
- Depth-0 overlap and disjoint control limits

## Anchors Used

- Algorithmiq OLE theory note: definition and small-`delta` commutator framing
- `.gpd/phases/01/ole_formalism_lock.md`: frozen q14 observable/generator/support choices
- `files/quantum-math-lab/benchmarks/q14_only_manifest.json`: q14 exact-short task family
- `files/quantum-math-lab/results/benchmark/classical/black_hole_scrambling_q14_exact_short.json`: current exact baseline artifact
- `STATUS.md`: q14-only claim boundary and q80 subset/full guardrail
