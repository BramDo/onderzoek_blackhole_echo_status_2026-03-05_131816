# Research State

## Project Reference

See: .gpd/PROJECT.md (updated 2026-03-17)

**Core research question:** Can the existing q14/q80 perturbed_echo pipeline be turned into a fixed-observable OLE workflow that yields a decisive q14 small-delta benchmark and a credible hardware-ready path without overclaiming the meaning of q80 subset observables?
**Current focus:** Phase 3 - Hardware Mapping and q80 Scope

## Current Position

**Current Phase:** 03
**Current Phase Name:** Hardware Mapping and q80 Scope
**Total Phases:** 3
**Current Plan:** 0
**Total Plans in Phase:** 2
**Status:** Ready to plan
**Last Activity:** 2026-03-18
**Last Activity Description:** Phase 2 executed; q14 exact benchmark, validation note, and Phase 3 handoff completed with verifier follow-up checks recorded

**Progress:** [██████████] 100%

## Active Calculations

- Exact q14 OLE artifact now exists on the active manifest with mean term counts `3, 12, 39, 195` across depths `1..4`.
- The overlap branch `G = X_0` has validated small-`delta` fits; the preferred quoted coefficient window is `delta <= 0.10`.
- The disjoint branch `G = X_10` is now locked as an exact flat control on the active q14 manifest.

## Intermediate Results

- `qiskit_black_hole_ole_exact.py` produces exact q14 `F_delta(Z_0)` and `f_delta(O)` artifacts without dense 14-qubit operators.
- `q14_ole_vs_delta2_benchmark.md` and the matching CSV now provide the decisive q14 benchmark artifact against the existing `perturbed_echo` baseline.
- `q14_small_delta_validation.md` records passing shrinking-window fits and explicit baseline exclusion from the quadratic regression.

## Open Questions

- Which fixed-observable hardware estimator is the cleanest Phase 3 continuation of the local-Pauli q14 benchmark
- How q80 subset observables should be mapped onto an OLE-compatible fixed-observable correlator without relabeling existing subset-return outputs
- Whether full-q80 OLE will admit a meaningful justified proxy or remain a longer-horizon target

## Performance Metrics

| Label | Duration | Tasks | Files |
| ----- | -------- | ----- | ----- |
| Phase 01 | 2 plans + verification | 2 plan summaries, 1 verification report | 7 primary docs |
| Phase 02 | 3 plans + verification | 3 plan summaries, 1 verification report | exact runner, benchmark report, validation + handoff docs |

## Accumulated Context

### Decisions

- Report the first q14 benchmark as `F_delta(P)` and carry `f_delta(O) = 2^-14 F_delta(P)` as the normalized translation.
- Keep the primary bridge in the fixed picture `A_P(U) = U P U^dagger`; rotate `G` as well if an alternate `U^dagger O U` picture is used.
- Treat `perturbed_echo` only as a labeled same-family baseline and not as the OLE quantity itself.
- Prefer `delta <= 0.10` for quoted overlap coefficients while allowing `delta <= 0.20` as a broader presentation window.
- Keep q80 immediate work subset-scoped until a later phase justifies any fuller proxy explicitly.

### Active Approximations

- Small-`delta` expansion: use only shrinking `delta^2` windows where the intercept and quadratic coefficient remain stable.
- Depth-0 locality control: overlap and disjoint branches are exact sanity checks before nontrivial scrambling depth is introduced.
- Hardware-ready continuity: Phase 2 preserves only the local-Pauli measurement direction, not a solved hardware estimator.

**Convention Lock:**

- Metric signature: euclidean
- Fourier convention: physics
- Natural units: natural
- Gauge choice: not applicable (no gauge field in gate-model circuit benchmark)
- Regularization scheme: not applicable (finite-dimensional Hilbert space; no UV regulator)
- Renormalization scheme: not applicable (no renormalized continuum coupling in current scope)
- Coordinate system: Qiskit qubit index ordering 0..n-1
- Spin basis: computational basis with Pauli operators X,Y,Z in the standard qubit basis
- State normalization: non-relativistic
- Coupling convention: brickwork gate angles are used directly; no separate continuum coupling convention
- Index positioning: qubit and operator labels are positional only; no covariant/contravariant distinction
- Time ordering: circuit gates are ordered by layer depth from left to right in circuit time
- Commutation convention: [A,B]=AB-BA; Pauli commutators use [X,Z]=-2iY and [Z,X]=2iY
- Levi-Civita sign: epsilon_xyz = +1 for Pauli-axis orientation when used
- Generator normalization: single-qubit Pauli generators square to identity; use X_q, Y_q, Z_q without 1/2 factors unless stated
- Covariant derivative sign: not applicable (no covariant derivative in the circuit benchmark)
- Gamma matrix convention: not applicable (no gamma matrices in the circuit benchmark)
- Creation/annihilation order: not applicable (no creation/annihilation ordering is used in the current scope)

*Custom conventions:*
- Observable Normalization: Tr(O^2)=1
- Operator Picture: Use f_delta(O)=2^{-n} Tr(U O U^dagger V_delta^dagger U O U^dagger V_delta) as the defining expression and translate the small-delta commutator form consistently from that choice.
- Qubit Indexing: Qubits are indexed 0..n-1 as in Qiskit; subset observables must report their support S explicitly.
- Perturbed Echo Baseline: perturbed_echo denotes the state-return benchmark |<psi0|U^dagger X U|psi0>|^2 for psi0=|0...0>; it is a baseline and must not be labeled as OLE.

### Propagated Uncertainties

None yet.

### Pending Todos

None yet.

### Blockers/Concerns

None

## Session Continuity

**Last session:** 2026-03-18
**Stopped at:** Ready to plan Phase 3
**Resume file:** —
