# Research State

## Project Reference

See: .gpd/PROJECT.md (updated 2026-03-17)

**Core research question:** Can the existing q14/q80 perturbed_echo pipeline be turned into a fixed-observable OLE workflow that yields a decisive q14 small-delta benchmark and a credible hardware-ready path without overclaiming the meaning of q80 subset observables?
**Current focus:** Phase 1 - Formal OLE Bridge

## Current Position

**Current Phase:** 01
**Current Phase Name:** Formal OLE Bridge
**Total Phases:** 3
**Current Plan:** 0
**Total Plans in Phase:** 2
**Status:** Ready to execute
**Last Activity:** 2026-03-17
**Last Activity Description:** Phase 1 research and plan files created

**Progress:** [░░░░░░░░░░] 0%

## Active Calculations

None yet.

## Intermediate Results

None yet.

## Open Questions

- Which fixed observable placement should be the default first implementation for the q14 benchmark?
- Whether full-q80 OLE will admit a feasible meaningful proxy or remain a longer-horizon target
- Whether later phases should use explicit PLE terminology for a Pauli-specialized fixed-observable OLE path

## Performance Metrics

| Label | Duration | Tasks | Files |
| ----- | -------- | ----- | ----- |
| -     | -        | -     | -     |

## Accumulated Context

### Decisions

None yet.

### Active Approximations

None yet.

**Convention Lock:**

- Metric signature: euclidean
- Fourier convention: physics
- Natural units: natural
- State normalization: non-relativistic

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

**Last session:** 2026-03-17
**Stopped at:** Ready to execute Phase 1
**Resume file:** —
