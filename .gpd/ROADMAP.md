# Roadmap: Operator Loschmidt Echo Extension of q14/q80 Scrambling Benchmarks

## Overview

This roadmap keeps the project tightly centered on the existing q14/q80 scrambling repository. The sequence is deliberate: first lock the fixed-observable OLE formalism so the project does not drift into a renamed `perturbed_echo` proxy; then establish the decisive q14 exact benchmark against the active baseline; then translate that benchmark into a hardware-ready path that preserves the current q80 subset evidence while keeping the full-q80 question explicit rather than overstated.

Working wording for planning:

- `perturbed_echo` = state-return echo / return probability for the prepared input state after `U`, a local kick, and `U^dagger`.
- OLE = fixed-observable operator correlator for explicit `O` and `V_delta = exp(-i delta G)`.
- OLE is the broader target because it gives a larger design space and a more direct operator-growth interpretation; `perturbed_echo` stays in the roadmap as the narrower benchmark baseline already validated in this repo.
- Phase planning must treat the project as a bridge from the first object to the second, not as a relabeling of the first object.

## Contract Overview

| Contract Item | Advanced By Phase(s) | Status |
| ------------- | -------------------- | ------ |
| `claim-q14-ole-bridge` | Phase 1, Phase 2, Phase 3 | Advanced through Phase 2 |
| `deliv-q14-benchmark-figure` | Phase 2 | Completed |
| `deliv-hardware-ready-note` | Phase 3 | Planned |
| `claim-q80-visibility` | Phase 3 | Planned |
| `deliv-q80-scope-note` | Phase 3 | Planned |
| `ref-algorithmiq-ole` | Phase 1, Phase 2, Phase 3 | Surfaced |
| `ref-q14-manifest` | Phase 1, Phase 2 | Completed |
| `ref-levelb-evidence` | Phase 2, Phase 3 | Surfaced through Phase 2 |

## Phases

- [x] **Phase 1: Formal OLE Bridge** - Freeze the fixed observable, perturbation generator, and small-`delta` formalism so OLE is explicit and distinct from `perturbed_echo`. Completed 2026-03-17.
- [x] **Phase 2: q14 Exact Benchmark** - Produce the decisive exact q14 `F_delta(P)` versus `delta^2` benchmark, with explicit normalized translation to `f_delta(O)`, and compare it against the active q14 baseline. Executed 2026-03-18 with verifier follow-up checks recorded for future figure/hardware closure.
- [ ] **Phase 3: Hardware Mapping and q80 Scope** - Translate the benchmark into a hardware-ready path and define the q80 subset/full boundary without overclaiming.

## Phase Details

### Phase 1: Formal OLE Bridge

**Goal:** Establish an explicit, repo-compatible fixed-observable OLE definition for the first q14 benchmark.
**Depends on:** Nothing (first phase)
**Requirements:** `FORM-01`, `FORM-02`
**Contract Coverage:**
- Advances: `claim-q14-ole-bridge`
- Deliverables: formal OLE definition, convention lock inputs, explicit observable/generator choice
- Anchor coverage: `ref-algorithmiq-ole`, `ref-q14-manifest`, `ref-status`
- Forbidden proxies: relabeling a state-return echo as OLE; leaving `O` or `G` implicit
**Success Criteria** (what must be TRUE):

1. The first fixed observable `O`, perturbation generator `G`, and support layout are frozen and normalized.
2. The small-`delta` OLE expression is written in the project’s chosen operator picture with any picture translation made explicit.
3. The project writes down, in one place, that `perturbed_echo` is a state-return benchmark while OLE is a fixed-observable operator correlator, and that the former is only a baseline for the latter.

Plans:

- [x] 01-01: Freeze q14 observable/generator and normalization guardrails
- [x] 01-02: Derive small-`delta` bridge and q14 benchmark handoff

### Phase 2: q14 Exact Benchmark

**Goal:** Produce the decisive exact q14 benchmark artifact for the fixed-observable OLE bridge without reopening the Phase 1 picture or intercept choice.
**Depends on:** Phase 1
**Requirements:** `NUMR-01`, `NUMR-02`, `NUMR-03`, `VALD-01`
**Contract Coverage:**
- Advances: `claim-q14-ole-bridge`
- Deliverables: `deliv-q14-benchmark-figure`
- Anchor coverage: `ref-algorithmiq-ole`, `ref-q14-manifest`, `ref-status`, `ref-levelb-evidence`
- Forbidden proxies: classical-only curve with no explicit observable semantics; too-large-`delta` fit presented as small-`delta` theory
**Success Criteria** (what must be TRUE):

1. Exact q14 `F_delta(P)` data exist for a controlled small-`delta` sweep on the active exact-short task family, with `f_delta(O) = 2^-14 F_delta(P)` carried as the normalized translation.
2. The benchmark artifact overlays or juxtaposes the Pauli-specialized OLE onset curve with the current q14 `perturbed_echo` baseline on a clearly labeled `delta^2` comparison figure.
3. Overlap-support and disjoint-support variants are compared in the exact regime.
4. Fit-window stability and intercept behavior support the small-`delta` interpretation.

Plans:

- [x] 02-01: Implement exact q14 sparse-Pauli OLE evaluator
- [x] 02-02: Build q14 delta^2 benchmark artifact against perturbed_echo baseline
- [x] 02-03: Validate small-delta windows and write Phase 3 handoff

### Phase 3: Hardware Mapping and q80 Scope

**Goal:** Preserve the hardware-ready and large-system path without erasing the subset/full distinction.
**Depends on:** Phase 2
**Requirements:** `PROT-01`, `PROT-02`, `VALD-02`
**Contract Coverage:**
- Advances: `claim-q14-ole-bridge`, `claim-q80-visibility`
- Deliverables: `deliv-hardware-ready-note`, `deliv-q80-scope-note`
- Anchor coverage: `ref-algorithmiq-ole`, `ref-status`, `ref-levelb-evidence`
- Forbidden proxies: hardware story that is only a renamed existing output; q80 subset evidence described as full-q80 OLE
**Success Criteria** (what must be TRUE):

1. A hardware-ready note maps the fixed-observable q14 benchmark onto the existing measurement pipeline and names current limitations.
2. The q80 path is written explicitly as subset-observable immediate work with locality controls and fixed subset labels.
3. The full-q80 question remains visible as an unresolved extension rather than being silently dropped or prematurely claimed.

Plans:

- [ ] 03-01: TBD during future phase planning
- [ ] 03-02: TBD during future phase planning

## Progress

| Phase | Plans Complete | Status | Completed |
| ----- | -------------- | ------ | --------- |
| 1. Formal OLE Bridge | 2/2 | Verified | 2026-03-17 |
| 2. q14 Exact Benchmark | 3/3 | Executed; verification follow-ups recorded | 2026-03-18 |
| 3. Hardware Mapping and q80 Scope | 0/2 | Not started | - |
