# Phase 2 Handoff: q14 Exact OLE Benchmark

**Written:** 2026-03-17
**Phase:** 01 -> 02
**Purpose:** give Phase 2 one execution-facing note that fixes the benchmark quantity, anchors, fit checks, and hardware/q80 guardrails

## Benchmark Anchor Set

Phase 2 should stay attached to exactly these repo anchors:

- q14 manifest: `files/quantum-math-lab/benchmarks/q14_only_manifest.json`
- q14 exact classical baseline artifact: `files/quantum-math-lab/results/benchmark/classical/black_hole_scrambling_q14_exact_short.json`
- q14/q80 scope boundary: `STATUS.md`
- hardware continuity note: `files/quantum-math-lab/hardware_advantage_protocol.md`
- current q80 subset evidence: `files/quantum-math-lab/results/hardware/summary/levelb_evidence_report.md`

The manifest and classical baseline define the active exact-short task family. The status and hardware artifacts keep the project from drifting into overclaiming.

## Primary Quantity Phase 2 Must Compute

Phase 2 should benchmark

$$
F_\delta(Z_0;U,G)
= 2^{-14}\operatorname{Tr}\!\left(U Z_0 U^\dagger\,V_\delta(G)^\dagger\,U Z_0 U^\dagger\,V_\delta(G)\right),
$$

with

- overlap branch: `G = X_0`
- disjoint branch: `G = X_10`

and with the normalized translation

$$
f_\delta\!\left(\frac{Z_0}{\sqrt{2^{14}}};U,G\right) = 2^{-14} F_\delta(Z_0;U,G).
$$

Phase 2 figures should plot `F_delta(Z_0)` versus `delta^2` because the unit intercept is easier to audit. Text and verification may additionally report the normalized `f_delta(O)` translation.

## Execution Contract For The First Exact Benchmark

Use the active q14 exact-short family from the manifest unchanged:

- qubits: `14`
- depths: `1, 2, 3, 4`
- trials/seeds: inherit the manifest/default exact-short setup
- keep the same brickwork scrambler family and q14 qubit indexing

For each depth, compute two OLE onset branches:

1. overlap branch with `P = Z_0`, `G = X_0`
2. disjoint control with `P = Z_0`, `G = X_10`

The deliverable is not "some delta-decay curve." It is the pair of fixed-observable onset curves tied to the frozen Phase 1 semantics.

## Required `delta^2` Fit-Window Checks

Phase 2 must explicitly record the small-`delta` acceptance checks, not just the final fit:

- nested fit windows: fit the same data on at least three shrinking `delta^2` ranges near zero
- intercept stability: the fitted intercept for `F_delta(Z_0)` must stay close to `1` as the window shrinks
- coefficient stability: the quadratic coefficient for the overlap branch must not move materially under the shrinking-window check
- control separation: the disjoint branch must remain much flatter near `delta = 0` than the overlap branch, with the depth-0 coefficient reducing to zero exactly

The handoff point is to make Phase 2 prove that it is seeing the promised small-`delta` OLE onset rather than a generic finite-kick decay.

## How To Compare Against The Existing `perturbed_echo` Baseline

The existing q14 baseline artifact is still useful, but it must stay explicitly labeled as a different observable family.

Use it this way:

- keep the exact-short `perturbed_echo` curves from `black_hole_scrambling_q14_exact_short.json` as the current repo benchmark reference
- compare at matching depths, seeds, and perturbation-support language
- if a single shared kick-family marker is helpful, note that the baseline uses a full `X_q` kick, corresponding to `V_{\pi/2}(X_q) = -i X_q`
- do not fit the `perturbed_echo` point into the small-`delta` quadratic model
- do not rename the baseline curve as OLE or as `F_delta(Z_0)`

The clean wording is: Phase 2 overlays or juxtaposes the q14 OLE onset curve with the existing state-return baseline from the same task family.

## Minimum Figure / Table Expectations

The first exact benchmark artifact should include, for each depth or for a representative depth panel:

- `F_delta(Z_0)` versus `delta^2` for overlap `G = X_0`
- `F_delta(Z_0)` versus `delta^2` for disjoint control `G = X_10`
- fitted intercept and quadratic coefficient over the accepted fit window
- a labeled `perturbed_echo` baseline reference from the current exact-short artifact
- one sentence that maps `F_delta(Z_0)` back to the normalized `f_delta(O)` convention

## Hardware-Ready Carry-Forward Paragraph

Phase 2 stays classical/exact, but it should preserve compatibility with the existing hardware path:

- keep the perturbation family local and Pauli-based so it remains close to the current hardware runner semantics
- phrase the future measurement task as a fixed-observable or fixed-parity correlator, not as global state-return overlap
- preserve the same depth/seed/backend bookkeeping discipline already used by the q14 and q80 hardware artifacts
- treat the hardware protocol as "compatible and to be finalized in Phase 3," not as already solved by the present note

This is enough to keep the benchmark hardware-ready without pretending that the hardware estimator is already implemented.

## q80 Scope Guardrail

Keep both q80 directions explicit:

- immediate scalable route: fixed subset observables on declared supports, analogous to the current 80q subset evidence
- longer-horizon route: a separate full-q80 global OLE definition or proxy, only if a later phase justifies it explicitly

Phase 2 must not write as though a successful q14 OLE benchmark automatically resolves the full 80q question.

## Ready-State Checklist For Phase 2

Phase 2 can start once the execution note does all of the following in one place:

- names the q14 manifest
- names the current exact classical baseline artifact
- names the primary plotted quantity `F_delta(Z_0)`
- names the normalized translation `f_delta(O) = 2^{-14} F_delta(Z_0)`
- names both support variants `G = X_0` and `G = X_10`
- names the nested fit-window and intercept-stability checks
- carries forward the hardware-ready paragraph
- keeps the q80 subset/full split explicit

If any of those items is missing, Phase 2 would be forced to reopen Phase 1 semantics instead of executing the benchmark.

## Phase 1 Deliverable Checklist

- q14 manifest anchor and current exact baseline artifact
- Required overlap-support and disjoint-support variants
- delta^2 fit-window and intercept-stability checks
- Hardware-ready carry-forward paragraph and q80 subset/full guardrail
