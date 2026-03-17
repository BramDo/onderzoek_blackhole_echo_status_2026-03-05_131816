---
phase: "01"
plan: "02"
depth: standard
one-liner: "Phase 1 translated the q14 formalism lock into a fixed-picture small-delta bridge, a Phase 2 execution handoff, and explicit hardware/q80 guardrails centered on F_delta(Z_0)."
subsystem:
  - formalism
  - derivation
  - analysis
tags:
  - operator-loschmidt-echo
  - q14
  - small-delta
  - handoff
requires: []
provides:
  - "Fixed-picture small-delta bridge for the q14 Pauli-specialized OLE benchmark"
  - "Phase 2 execution handoff tied to the active q14 exact-short manifest and classical baseline artifact"
  - "Explicit carry-forward wording for hardware readiness and the q80 subset/full scope split"
affects:
  - "Phase 2 q14 exact benchmark"
  - "Phase 3 hardware mapping and q80 scope"
methods:
  added:
    - "Fixed-picture commutator bridge in A_P(U) = U P U^dagger form"
    - "Execution-facing baseline overlay and fit-window discipline"
  patterns:
    - "Keep the plotted Pauli-specialized quantity and the normalized OLE translation explicit"
    - "Treat the existing state-return echo as a same-family baseline, not as the benchmark quantity itself"
key-files:
  created:
    - ".gpd/phases/01/ole_small_delta_bridge.md"
    - ".gpd/phases/01/q14_phase2_handoff.md"
  modified:
    - ".gpd/NOTATION_GLOSSARY.md"
    - ".gpd/ROADMAP.md"
key-decisions:
  - "Carry the derivation in the fixed picture A_P(U) = U P U^dagger and rotate G as well if an alternate U^dagger O U picture is used."
  - "Treat F_delta(Z_0) as the Phase 2 plotted quantity and f_delta(O) = 2^-14 F_delta(Z_0) as the normalized translation."
  - "Use the current perturbed_echo artifact only as a labeled baseline comparison, with the full X kick interpreted as the V_{pi/2} endpoint of the same perturbation family."
patterns-established:
  - "A benchmark handoff is not complete until the fit-window test, baseline overlay discipline, and q80 scope guardrail live in one note."
  - "Hardware readiness can be preserved at the scoping level without claiming that the hardware estimator is already solved."
conventions:
  - "operator_picture = primary bridge written in A_P(U) = U P U^dagger form"
  - "observable_normalization = plot F_delta(P) first, then report f_delta(O) = 2^-n F_delta(P) explicitly when needed"
  - "commutation_convention = [A,B]=AB-BA with [X,Z]=-2iY and [Z,X]=2iY"
plan_contract_ref: ".gpd/phases/01/01-02-PLAN.md#/contract"
contract_results:
  claims:
    claim-q14-ole-bridge:
      status: passed
      summary: "The frozen q14 benchmark now has an explicit small-delta bridge, a fixed-picture quadratic coefficient, and a concrete Phase 2 handoff that keeps the hardware-ready and q80 scope constraints visible."
      linked_ids:
        - deliv-small-delta-bridge-note
        - deliv-phase2-handoff-note
        - test-small-delta-bridge
        - test-phase2-handoff
        - ref-algorithmiq-ole
        - ref-formalism-lock
        - ref-q14-manifest
        - ref-q14-baseline-artifact
        - ref-status
        - ref-levelb-evidence
        - ref-hardware-protocol
      evidence: []
  deliverables:
    deliv-small-delta-bridge-note:
      status: passed
      path: ".gpd/phases/01/ole_small_delta_bridge.md"
      summary: "Bridge note created with one fixed operator picture, explicit normalized translation, quadratic coefficient kappa_G(P;U), and depth-0 overlap/disjoint control limits."
      linked_ids:
        - claim-q14-ole-bridge
        - test-small-delta-bridge
    deliv-phase2-handoff-note:
      status: passed
      path: ".gpd/phases/01/q14_phase2_handoff.md"
      summary: "Execution-facing handoff note created with the q14 manifest, the existing exact baseline artifact, nested fit-window checks, and hardware/q80 guardrails."
      linked_ids:
        - claim-q14-ole-bridge
        - test-phase2-handoff
  acceptance_tests:
    test-small-delta-bridge:
      status: passed
      summary: "The bridge note now states the fixed-picture defining expression, the exact intercept, the O(delta^2) coefficient structure, and the depth-0 overlap/disjoint limits with kappa_overlap = 4 and kappa_disjoint = 0."
      linked_ids:
        - claim-q14-ole-bridge
        - deliv-small-delta-bridge-note
        - ref-algorithmiq-ole
        - ref-formalism-lock
    test-phase2-handoff:
      status: passed
      summary: "The handoff note names the active q14 manifest, the current exact baseline artifact, the required overlap/disjoint branches, the fit-window/intercept checks, and the hardware-ready plus q80 subset/full guardrail in one place."
      linked_ids:
        - claim-q14-ole-bridge
        - deliv-phase2-handoff-note
        - ref-q14-manifest
        - ref-q14-baseline-artifact
        - ref-status
        - ref-levelb-evidence
        - ref-hardware-protocol
  references:
    ref-algorithmiq-ole:
      status: completed
      completed_actions:
        - read
        - compare
        - cite
      missing_actions: []
      summary: "Used as the small-delta operator-correlator anchor and to keep the bridge tied to an explicit commutator norm."
    ref-formalism-lock:
      status: completed
      completed_actions:
        - read
        - use
      missing_actions: []
      summary: "Used to inherit the frozen q14 observable, generator, support, and intercept conventions from 01-01."
    ref-q14-manifest:
      status: completed
      completed_actions:
        - read
        - use
        - compare
      missing_actions: []
      summary: "Used to keep Phase 2 attached to the active q14 exact-short task family rather than inventing a new benchmark family."
    ref-q14-baseline-artifact:
      status: completed
      completed_actions:
        - read
        - use
        - compare
      missing_actions: []
      summary: "Used to define exactly which perturbed_echo artifact Phase 2 may overlay or juxtapose as the current baseline reference."
    ref-status:
      status: completed
      completed_actions:
        - read
        - use
        - avoid
      missing_actions: []
      summary: "Used to preserve the q14-only claim language and to keep q80 subset/full wording honest."
    ref-levelb-evidence:
      status: completed
      completed_actions:
        - read
        - use
        - avoid
      missing_actions: []
      summary: "Used to keep the q80 path framed as subset-observable evidence rather than as solved full-q80 OLE."
    ref-hardware-protocol:
      status: completed
      completed_actions:
        - read
        - compare
        - use
      missing_actions: []
      summary: "Used to keep the hardware-ready paragraph compatible with the current runner and claim-level discipline."
  forbidden_proxies:
    fp-underdetermined-bridge:
      status: rejected
      notes: "The bridge note now fixes the picture, the intercept convention, the quadratic coefficient, and the overlap/disjoint limits explicitly."
    fp-equate-baseline-and-ole:
      status: rejected
      notes: "The handoff note treats perturbed_echo only as a labeled comparison baseline and explicitly forbids fitting it as if it were the small-delta OLE curve."
  uncertainty_markers:
    weakest_anchors:
      - "The hardware-ready story is still scoped rather than implemented; Phase 3 must still choose and verify the concrete measurement protocol."
    unvalidated_assumptions:
      - "The eventual q14 exact data may require a tighter small-delta window than currently anticipated before the quadratic coefficient stabilizes."
    competing_explanations:
      - "A later OLE curve could still look approximately quadratic over too broad a range if Phase 2 skips the shrinking-window check."
    disconfirming_observations:
      - "If nonzero-depth overlap and disjoint branches cannot be separated without redefining P or G, the present bridge would not be sufficient for the benchmark."
comparison_verdicts:
  - subject_id: claim-q14-ole-bridge
    subject_kind: claim
    subject_role: decisive
    reference_id: ref-algorithmiq-ole
    comparison_kind: prior_work
    metric: "small-delta form in a fixed operator picture"
    threshold: "explicit defining expression, explicit picture translation, and explicit commutator-norm coefficient"
    verdict: pass
    recommended_action: "Carry the same F_delta(P) to Phase 2 without changing picture conventions."
    notes: "The bridge note now makes the picture choice explicit and states how to rotate the generator if the alternate U^dagger O U picture is used."
  - subject_id: claim-q14-ole-bridge
    subject_kind: claim
    subject_role: decisive
    reference_id: ref-q14-manifest
    comparison_kind: benchmark
    metric: "task-family continuity"
    threshold: "same q14 exact-short family, same qubit count, same depth set, and same local perturbation language preserved"
    verdict: pass
    recommended_action: "Use the manifest unchanged when Phase 2 builds the q14 delta sweep."
    notes: "The handoff note anchors the benchmark to qubits 14 and depths 1-4 instead of opening a new task definition."
  - subject_id: claim-q14-ole-bridge
    subject_kind: claim
    subject_role: decisive
    reference_id: ref-q14-baseline-artifact
    comparison_kind: baseline
    metric: "baseline overlay discipline"
    threshold: "baseline stays explicit, same-family, and outside the small-delta quadratic fit"
    verdict: pass
    recommended_action: "Show perturbed_echo only as a labeled reference or comparison marker."
    notes: "The handoff note explicitly interprets the current full X kick as the V_{pi/2} endpoint of the same kick family without identifying the two observables."
  - subject_id: claim-q14-ole-bridge
    subject_kind: claim
    subject_role: decisive
    reference_id: ref-hardware-protocol
    comparison_kind: cross_method
    metric: "hardware-ready continuity"
    threshold: "future estimator phrased as a fixed-observable correlator while preserving the existing runner's bookkeeping discipline"
    verdict: pass
    recommended_action: "Defer the concrete hardware estimator to Phase 3, but keep the local Pauli perturbation and measurement language aligned now."
    notes: "The handoff note preserves compatibility with the existing hardware path without claiming that the hardware OLE estimator is already implemented."
  - subject_id: claim-q14-ole-bridge
    subject_kind: claim
    subject_role: supporting
    reference_id: ref-levelb-evidence
    comparison_kind: experiment
    metric: "q80 scope honesty"
    threshold: "subset evidence stays labeled as subset evidence and does not collapse into a full-q80 claim"
    verdict: pass
    recommended_action: "Carry the subset/full split forward unchanged into Phase 3."
    notes: "The handoff note keeps the immediate q80 route as subset observables and leaves full-q80 as an unresolved later extension."
duration: "9min"
completed: "2026-03-17"
---

# Phase 1 Plan 02 Summary

**Phase 1 translated the q14 formalism lock into a fixed-picture small-`delta` bridge, a Phase 2 execution handoff, and explicit hardware/q80 guardrails centered on `F_delta(Z_0)`.**

## Performance

- **Duration:** 9 min
- **Started:** 2026-03-17T21:22:10Z
- **Completed:** 2026-03-17T21:31:21Z
- **Tasks:** 3
- **Files modified:** 4

## Key Results

- The benchmark bridge is now written in the fixed picture `A_P(U) = U P U^dagger`, with explicit warning not to mix that definition with an unrotated `[G, U^dagger O U]` commutator.
- The small-`delta` onset is now stated as `F_delta(P;U,G) = 1 - (delta^2 / 2) kappa_G(P;U) + O(delta^4)` with `kappa_G(P;U) = 2^-n Tr([G,A_P][G,A_P]^dagger)`.
- The Phase 2 handoff now names one manifest, one classical baseline artifact, the overlap/disjoint branches, the nested fit-window checks, and the hardware/q80 guardrails in one execution note.

## Task Commits

1. **Task 1: Derive the Phase 2 bridge in one fixed operator picture** - `75ad72e`
2. **Task 2: Write the Phase 2 benchmark handoff note** - `3650828`
3. **Task 3: Carry the hardware-ready and q80 scope guardrails forward** - `3650828`

## Files Created/Modified

- `.gpd/phases/01/ole_small_delta_bridge.md` - fixed-picture small-`delta` bridge and depth-0 control limits
- `.gpd/phases/01/q14_phase2_handoff.md` - execution-facing q14 benchmark handoff note
- `.gpd/NOTATION_GLOSSARY.md` - benchmark notation for `P`, `F_delta(P)`, `A_P(U)`, and `kappa_G(P;U)`
- `.gpd/ROADMAP.md` - Phase 2 wording aligned to the plotted `F_delta(P)` quantity and normalized translation

## Next Phase Readiness

Phase 2 can now execute the q14 exact benchmark without reopening the picture choice, intercept convention, baseline role, or q80 scope boundary.

## Contract Coverage

- Claim IDs advanced: `claim-q14-ole-bridge -> passed`
- Deliverable IDs produced: `deliv-small-delta-bridge-note`, `deliv-phase2-handoff-note`
- Acceptance test IDs run: `test-small-delta-bridge`, `test-phase2-handoff`
- Reference IDs surfaced: `ref-algorithmiq-ole`, `ref-formalism-lock`, `ref-q14-manifest`, `ref-q14-baseline-artifact`, `ref-status`, `ref-levelb-evidence`, `ref-hardware-protocol`
- Forbidden proxies rejected or violated: `fp-underdetermined-bridge -> rejected`, `fp-equate-baseline-and-ole -> rejected`
- Decisive comparison verdicts: `claim-q14-ole-bridge -> pass` versus `ref-algorithmiq-ole`, `ref-q14-manifest`, `ref-q14-baseline-artifact`, `ref-hardware-protocol`; supporting pass versus `ref-levelb-evidence`

## Equations Derived

**Eq. (01.4):**

$$
F_\delta(P;U,G)
= 2^{-n}\operatorname{Tr}\!\left(U P U^\dagger V_\delta(G)^\dagger U P U^\dagger V_\delta(G)\right)
$$

**Eq. (01.5):**

$$
F_\delta(P;U,G) = 1 - \frac{\delta^2}{2}\,\kappa_G(P;U) + O(\delta^4),
\qquad
\kappa_G(P;U) = 2^{-n}\operatorname{Tr}\!\left([G,A_P(U)][G,A_P(U)]^\dagger\right)
$$

**Eq. (01.6):**

$$
\kappa_{X_0}(Z_0;I) = 4,
\qquad
\kappa_{X_{10}}(Z_0;I) = 0,
\qquad
F_\delta(Z_0;I,X_0) = \cos(2\delta)
$$

## Validations Completed

- Checked the picture translation: the alternate `U^dagger O U` form is only equivalent when the perturbation generator is rotated to `U^dagger G U` as well.
- Checked the exact intercept and quadratic structure: `F_0(P) = 1` for Pauli `P`, and `f_delta(O) = 2^-14 F_delta(P)` for the normalized translation.
- Checked the depth-0 controls: overlap gives a nonzero coefficient `kappa = 4`, while the disjoint control remains exactly flat at depth `0`.
- Checked the execution handoff against the active repo anchors: one manifest, one baseline artifact, explicit fit-window checks, and explicit hardware/q80 scope wording are all present.

## Decisions & Deviations

The main decision was to phrase the current `perturbed_echo` artifact as the `V_{pi/2}` endpoint of the same local kick family while still keeping it outside the OLE fit. No deviation from the plan scope occurred.

## Open Questions

- How small the accepted q14 `delta` window must be before the overlap coefficient stabilizes numerically remains a Phase 2 execution question.
- Whether the later project should actually adopt the `PLE` label for the Pauli-specialized branch remains open; the glossary only reserves it as optional terminology.

```yaml
gpd_return:
  status: completed
  code: SUMMARY_READY
  message: "Plan 01-02 executed and summarized."
  duration_seconds: 551
  files_written:
    - ".gpd/phases/01/ole_small_delta_bridge.md"
    - ".gpd/phases/01/q14_phase2_handoff.md"
    - ".gpd/phases/01/01-02-SUMMARY.md"
    - ".gpd/NOTATION_GLOSSARY.md"
    - ".gpd/ROADMAP.md"
  issues: []
  next_actions:
    - "Run phase-level verification and state synchronization."
    - "Advance to Phase 2 planning/execution once Phase 1 is marked complete."
  data:
    summary_path: ".gpd/phases/01/01-02-SUMMARY.md"
    deliverables:
      - ".gpd/phases/01/ole_small_delta_bridge.md"
      - ".gpd/phases/01/q14_phase2_handoff.md"
    commits:
      - "75ad72e"
      - "3650828"
```
```
