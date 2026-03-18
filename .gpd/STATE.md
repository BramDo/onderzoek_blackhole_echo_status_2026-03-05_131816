# Research State

## Project Reference

See: .gpd/PROJECT.md (updated 2026-03-17)

**Core research question:** Can the existing q14/q80 perturbed_echo pipeline be turned into a fixed-observable OLE workflow that yields a decisive q14 small-delta benchmark and a credible hardware-ready path without overclaiming the meaning of q80 subset observables?
**Current focus:** Phase 2 - q14 Exact Benchmark

## Current Position

**Current Phase:** 02
**Current Phase Name:** q14 Exact Benchmark
**Total Phases:** 3
**Current Plan:** 0
**Total Plans in Phase:** 3
**Status:** Ready to execute
**Last Activity:** 2026-03-18
**Last Activity Description:** Phase 2 research, experiment design, and plan files created

**Progress:** [███░░░░░░░] 33%

## Active Calculations

- Phase 1 lock fixed the first benchmark to `P = Z_0`, overlap `G = X_0`, disjoint control `G = X_10`.
- Phase 1 bridge fixed the plotted quantity to `F_delta(P)` with `f_delta(O) = 2^-14 F_delta(P)` as the normalized translation.
- Phase 1 verification confirmed the depth-0 limits `kappa_overlap = 4`, `kappa_disjoint = 0`, and `F_delta(Z_0; I, X_0) = cos(2 delta)`.

## Intermediate Results

None yet.

## Open Questions

- Whether full-q80 OLE will admit a feasible meaningful proxy or remain a longer-horizon target
- How small the accepted q14 fit window must be before the overlap coefficient stabilizes numerically at nonzero scrambling depth
- Whether later phases should use explicit PLE terminology for a Pauli-specialized fixed-observable OLE path

## Performance Metrics

| Label | Duration | Tasks | Files |
| ----- | -------- | ----- | ----- |
| Phase 01 | 2 plans + verification | 2 plan summaries, 1 verification report | 7 primary docs |

## Accumulated Context

### Decisions

- Report the first q14 benchmark as `F_delta(P)` and carry `f_delta(O) = 2^-14 F_delta(P)` as the normalized translation.
- Keep the primary bridge in the fixed picture `A_P(U) = U P U^dagger`; rotate `G` as well if an alternate `U^dagger O U` picture is used.
- Treat `perturbed_echo` only as a labeled same-family baseline and not as the OLE quantity itself.

### Active Approximations

- Small-`delta` expansion: use only shrinking `delta^2` windows where the intercept and quadratic coefficient remain stable.
- Depth-0 locality control: overlap and disjoint branches are exact sanity checks before nontrivial scrambling depth is introduced.

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
**Stopped at:** Ready to execute Phase 2
**Resume file:** —
