---
phase: "02"
plan: "03"
depth: standard
one-liner: "Phase 2 validated the q14 small-delta interpretation with shrinking-window fits and wrote a Phase 3 handoff that keeps the hardware-ready path local-Pauli and the q80 subset/full split explicit."
subsystem:
  - validation
  - analysis
  - handoff
tags:
  - operator-loschmidt-echo
  - q14
  - validation
  - q80-guardrail
requires:
  - "files/quantum-math-lab/results/ole/black_hole_ole_q14_exact_small_delta.json"
  - "files/quantum-math-lab/results/ole/q14_ole_vs_delta2_benchmark.md"
provides:
  - "Fit-window validation note for the exact q14 OLE benchmark"
  - "Execution-facing Phase 3 handoff with hardware/q80 guardrails"
  - "Explicit pass/fail wording for overlap stability and disjoint flatness"
affects:
  - "Phase 2 verification"
  - "Phase 3 planning"
methods:
  added:
    - "Nested least-squares fits in x = delta^2 on three shrinking windows"
    - "Contract-level distinction between exact benchmark validation and hardware-estimator design"
    - "Guardrail handoff keyed to STATUS.md and the existing hardware evidence trail"
  patterns:
    - "Keep the baseline outside the small-delta fit even when it is useful for context"
    - "Treat exact locality controls as implementation gates, not soft trends"
key-files:
  created:
    - ".gpd/phases/02/q14_small_delta_validation.md"
    - ".gpd/phases/02/q14_phase3_handoff.md"
  modified: []
key-decisions:
  - "Accept all three declared fit windows for the active q14 overlap branch, while preferring delta <= 0.10 for quoted coefficient statements."
  - "Treat the disjoint X_10 branch as an exact flat control whose failure would indicate a bug, not new physics."
  - "Carry the hardware-ready story forward only as a next-step measurement-design problem, not as an already-solved estimator."
patterns-established:
  - "A benchmark phase is not closed until it says both what was validated and what remains explicitly unresolved."
  - "q80 subset/full distinctions must survive handoff documents as first-class scope guards."
conventions:
  - "fit_variable = x = delta^2"
  - "fit_quantity = F_delta(Z_0)"
  - "baseline_exclusion = perturbed_echo stays outside the quadratic fit"
plan_contract_ref: ".gpd/phases/02/02-03-PLAN.md#/contract"
contract_results:
  claims:
    claim-q14-small-delta-validity:
      status: passed
      summary: "The exact q14 benchmark now has explicit shrinking-window validation, exact disjoint-control wording, and a Phase 3 handoff that preserves the hardware/q80 guardrails without relabeling old outputs as OLE."
      linked_ids:
        - deliv-small-delta-validation-note
        - deliv-phase3-handoff-note
        - test-fit-window-stability
        - test-control-flatness
        - test-phase3-guardrails
        - ref-exact-ole-data
        - ref-q14-benchmark-report
        - ref-small-delta-bridge
        - ref-phase2-handoff
        - ref-status
        - ref-hardware-protocol
        - ref-levelb-evidence
      evidence: []
  deliverables:
    deliv-small-delta-validation-note:
      status: passed
      path: ".gpd/phases/02/q14_small_delta_validation.md"
      summary: "Validation note that records the three fit windows, branch-by-branch intercept and slope tables, and explicit pass/fail wording for the small-delta interpretation."
      linked_ids:
        - claim-q14-small-delta-validity
        - test-fit-window-stability
        - test-control-flatness
    deliv-phase3-handoff-note:
      status: passed
      path: ".gpd/phases/02/q14_phase3_handoff.md"
      summary: "Execution-facing handoff that separates what Phase 2 settled from what Phase 3 still has to design, while preserving hardware and q80 scope guardrails."
      linked_ids:
        - claim-q14-small-delta-validity
        - test-phase3-guardrails
  acceptance_tests:
    test-fit-window-stability:
      status: passed
      summary: "The overlap branch keeps intercept 1 and converges toward slope -kappa/2 as the fit window shrinks, while the disjoint branch stays at intercept 1 and slope 0."
      linked_ids:
        - claim-q14-small-delta-validity
        - deliv-small-delta-validation-note
        - ref-exact-ole-data
        - ref-small-delta-bridge
    test-control-flatness:
      status: passed
      summary: "The validation note treats the q10 disjoint branch as an exact flat control and states that any material non-flatness would be an implementation failure."
      linked_ids:
        - claim-q14-small-delta-validity
        - deliv-small-delta-validation-note
        - ref-exact-ole-data
        - ref-phase2-handoff
    test-phase3-guardrails:
      status: passed
      summary: "The Phase 3 handoff keeps the hardware-ready local-Pauli direction, the q80 subset/full split, and the warning against relabeling existing hardware outputs as OLE."
      linked_ids:
        - deliv-phase3-handoff-note
        - ref-status
        - ref-hardware-protocol
        - ref-levelb-evidence
  references:
    ref-exact-ole-data:
      status: completed
      completed_actions:
        - read
        - use
      missing_actions: []
      summary: "Used as the source of the shrinking-window fit inputs and the exact branch-control statements."
    ref-q14-benchmark-report:
      status: completed
      completed_actions:
        - read
        - use
      missing_actions: []
      summary: "Used as the report-level artifact whose small-delta interpretation is now being certified."
    ref-small-delta-bridge:
      status: completed
      completed_actions:
        - read
        - compare
        - use
      missing_actions: []
      summary: "Compared the fitted intercepts and slopes directly against the Phase 1 small-delta target b0 -> 1 and b2 -> -kappa/2."
    ref-phase2-handoff:
      status: completed
      completed_actions:
        - read
        - compare
        - use
      missing_actions: []
      summary: "Used to preserve the declared fit windows, the baseline exclusion rule, and the disjoint-control expectation."
    ref-status:
      status: completed
      completed_actions:
        - read
        - use
        - avoid
      missing_actions: []
      summary: "Used as the binding guardrail against overclaiming beyond the current q14-only claim and subset-scoped 80q evidence."
    ref-hardware-protocol:
      status: completed
      completed_actions:
        - read
        - compare
        - use
      missing_actions: []
      summary: "Used to constrain the Phase 3 handoff so hardware-ready means protocol continuity, not a premature hardware-advantage claim."
    ref-levelb-evidence:
      status: completed
      completed_actions:
        - read
        - use
        - avoid
      missing_actions: []
      summary: "Used to keep the q80 route subset-scoped and to block any silent slide into a full-q80 claim."
  forbidden_proxies:
    fp-fit-everything:
      status: rejected
      notes: "The validation fit uses only the exact OLE onset data on the three declared windows and excludes the perturbed_echo baseline entirely."
    fp-hardware-ready-means-done:
      status: rejected
      notes: "The handoff says explicitly that the hardware path is a next-step measurement-design problem rather than a solved estimator."
  uncertainty_markers:
    weakest_anchors:
      - "Phase 2 validates exact small-delta behavior, but the concrete hardware estimator choice still belongs to Phase 3."
    unvalidated_assumptions: []
    competing_explanations: []
    disconfirming_observations: []
comparison_verdicts:
  - subject_id: test-fit-window-stability
    subject_kind: acceptance_test
    subject_role: decisive
    reference_id: ref-exact-ole-data
    comparison_kind: benchmark
    metric: "fit-window stability"
    threshold: "overlap branch keeps b0 near 1 and slope near -kappa/2 while disjoint stays flat"
    verdict: pass
    recommended_action: "Use delta <= 0.10 for quoted overlap coefficients and keep the wider windows as contextual support."
    notes: "All three declared windows pass on the active q14 benchmark family."
  - subject_id: test-fit-window-stability
    subject_kind: acceptance_test
    subject_role: decisive
    reference_id: ref-small-delta-bridge
    comparison_kind: cross_method
    metric: "agreement with Phase 1 small-delta target"
    threshold: "fitted intercepts and slopes converge toward the bridge expectation"
    verdict: pass
    recommended_action: "Carry the same bridge equations forward unchanged into Phase 3."
    notes: "Worst overlap slope error falls from 2.76% at delta <= 0.30 to 0.33% at delta <= 0.10."
  - subject_id: test-control-flatness
    subject_kind: acceptance_test
    subject_role: decisive
    reference_id: ref-phase2-handoff
    comparison_kind: benchmark
    metric: "control-branch flatness"
    threshold: "disjoint X_10 branch remains an exact flat control"
    verdict: pass
    recommended_action: "Retain the implementation-failure wording for any future non-flat disjoint result."
    notes: "The validation note records intercept 1 and slope 0 on every declared window."
  - subject_id: test-phase3-guardrails
    subject_kind: acceptance_test
    subject_role: decisive
    reference_id: ref-status
    comparison_kind: benchmark
    metric: "claim-discipline continuity"
    threshold: "handoff does not exceed the q14-only and subset-scoped evidence base"
    verdict: pass
    recommended_action: "Keep the q14-only and subset/full wording intact in future planning documents."
    notes: "The handoff explicitly separates current evidence from later extensions."
  - subject_id: test-phase3-guardrails
    subject_kind: acceptance_test
    subject_role: decisive
    reference_id: ref-hardware-protocol
    comparison_kind: cross_method
    metric: "hardware-ready continuity"
    threshold: "next-step hardware path stays local-Pauli and bookkeeping-compatible"
    verdict: pass
    recommended_action: "Use the local Pauli family as the Phase 3 starting point for hardware estimator design."
    notes: "The handoff keeps hardware-ready continuity without claiming that the estimator already exists."
  - subject_id: test-phase3-guardrails
    subject_kind: acceptance_test
    subject_role: decisive
    reference_id: ref-levelb-evidence
    comparison_kind: experiment
    metric: "q80 subset/full honesty"
    threshold: "subset evidence remains subset evidence"
    verdict: pass
    recommended_action: "Preserve the subset/full split when Phase 3 discusses 80q observables."
    notes: "The handoff keeps the immediate q80 route subset-scoped and leaves full-q80 as a later extension."
  - subject_id: ref-exact-ole-data
    subject_kind: reference
    subject_role: decisive
    reference_id: ref-exact-ole-data
    comparison_kind: benchmark
    metric: "source-artifact coverage"
    threshold: "validation note is tied directly to the exact OLE artifact"
    verdict: pass
    recommended_action: "Keep the exact JSON as the only fit input source."
    notes: "All fit tables are derived from the exact q14 OLE artifact."
  - subject_id: ref-q14-benchmark-report
    subject_kind: reference
    subject_role: decisive
    reference_id: ref-q14-benchmark-report
    comparison_kind: benchmark
    metric: "report-interpretation coverage"
    threshold: "the report artifact's meaning is explicitly certified"
    verdict: pass
    recommended_action: "Use the benchmark report as the narrative artifact and the validation note as the interpretation lock."
    notes: "The validation note now states exactly what the benchmark report does and does not establish."
  - subject_id: ref-small-delta-bridge
    subject_kind: reference
    subject_role: decisive
    reference_id: ref-small-delta-bridge
    comparison_kind: cross_method
    metric: "bridge-equation continuity"
    threshold: "Phase 2 validation stays aligned with the Phase 1 small-delta equations"
    verdict: pass
    recommended_action: "Do not reopen the bridge equations in Phase 3."
    notes: "The validation note uses the bridge target b0 -> 1 and b2 -> -kappa/2 directly."
  - subject_id: ref-phase2-handoff
    subject_kind: reference
    subject_role: decisive
    reference_id: ref-phase2-handoff
    comparison_kind: benchmark
    metric: "handoff-rule coverage"
    threshold: "declared windows and baseline exclusion survive into the validation note"
    verdict: pass
    recommended_action: "Keep the same windows and exclusion rule unless a later phase explicitly supersedes them."
    notes: "The validation note uses the exact three declared windows and excludes perturbed_echo from the fit."
  - subject_id: ref-status
    subject_kind: reference
    subject_role: decisive
    reference_id: ref-status
    comparison_kind: benchmark
    metric: "scope-guard coverage"
    threshold: "handoff remains inside current defensible claim language"
    verdict: pass
    recommended_action: "Use STATUS.md wording whenever a Phase 3 document risks overclaiming."
    notes: "The handoff keeps the current q14-only and 80q subset boundaries visible."
  - subject_id: ref-hardware-protocol
    subject_kind: reference
    subject_role: decisive
    reference_id: ref-hardware-protocol
    comparison_kind: cross_method
    metric: "protocol continuity coverage"
    threshold: "hardware-ready path stays compatible with the existing protocol's bookkeeping and caution level"
    verdict: pass
    recommended_action: "Keep the protocol continuity paragraph intact when Phase 3 starts."
    notes: "The handoff maps future OLE work onto the existing hardware workflow without claiming Level C-style closure."
  - subject_id: ref-levelb-evidence
    subject_kind: reference
    subject_role: decisive
    reference_id: ref-levelb-evidence
    comparison_kind: experiment
    metric: "subset-evidence coverage"
    threshold: "handoff honors the current 80q subset evidence rather than inflating it"
    verdict: pass
    recommended_action: "Retain subset-scoped language until a full-q80 proxy is justified explicitly."
    notes: "The handoff preserves the exact subset/full split reflected in the existing Level B evidence."
duration: "6min"
completed: "2026-03-18"
---

# Phase 2 Plan 03 Summary

**Phase 2 validated the q14 small-`delta` interpretation with shrinking-window fits and wrote a Phase 3 handoff that keeps the hardware-ready path local-Pauli and the q80 subset/full split explicit.**

## Performance

- **Duration:** 6 min
- **Started:** 2026-03-18T07:48:19Z
- **Completed:** 2026-03-18T07:54:18Z
- **Tasks:** 2
- **Files modified:** 2

## Key Results

- The overlap branch passes all three declared fit windows, with worst slope error versus `-kappa/2` shrinking from `2.76%` at `delta <= 0.30` to `0.33%` at `delta <= 0.10`.
- The disjoint `X_10` branch is flat to machine precision on every declared window and is now explicitly locked as an implementation control rather than a qualitative comparison curve.
- The Phase 3 handoff now states clearly what Phase 2 validated, what it did not validate, and why existing hardware outputs must not be relabeled as OLE.

## Task Commits

1. **Task 1: Validate shrinking fit windows and control flatness** - pending user approval for commit
2. **Task 2: Write the Phase 3 hardware/q80 handoff** - pending user approval for commit

## Files Created/Modified

- `.gpd/phases/02/q14_small_delta_validation.md` - shrinking-window fit tables and explicit pass/fail wording
- `.gpd/phases/02/q14_phase3_handoff.md` - execution-facing carry-forward note for hardware continuity and q80 scope

## Next Phase Readiness

Phase 2 is ready for phase verification and state closeout. Phase 3 can start from a locked q14 exact benchmark, a validated small-`delta` interpretation, and an explicit hardware/q80 guardrail note.

## Contract Coverage

- Claim IDs advanced: `claim-q14-small-delta-validity -> passed`
- Deliverable IDs produced: `deliv-small-delta-validation-note`, `deliv-phase3-handoff-note`
- Acceptance test IDs run: `test-fit-window-stability`, `test-control-flatness`, `test-phase3-guardrails`
- Reference IDs surfaced: `ref-exact-ole-data`, `ref-q14-benchmark-report`, `ref-small-delta-bridge`, `ref-phase2-handoff`, `ref-status`, `ref-hardware-protocol`, `ref-levelb-evidence`
- Forbidden proxies rejected or violated: `fp-fit-everything -> rejected`, `fp-hardware-ready-means-done -> rejected`
- Decisive comparison verdicts: `test-fit-window-stability -> pass`, `test-phase3-guardrails -> pass`

## Equations Derived

**Eq. (02.7):**

$$
F_\delta(Z_0) = b_0 + b_2 \delta^2
$$

**Eq. (02.8):**

$$
b_0 \to 1,
\qquad
b_2 \to -\kappa/2
$$

## Validations Completed

- Fit `F_delta(Z_0)` on the three declared windows `delta <= 0.30`, `delta <= 0.20`, and `delta <= 0.10` for both overlap and disjoint branches.
- Verified that the overlap intercept remains near `1` and the overlap slope converges toward `-kappa/2` as the window shrinks.
- Verified that the disjoint branch remains exactly flat and documented that any material non-flatness would be an implementation failure.
- Verified that the handoff preserves the q14-only claim discipline, the hardware-ready limitation, and the q80 subset/full split.

## Decisions & Deviations

No phase-contract deviation was needed. The only substantive judgment call was to accept all three declared windows while preferring `delta <= 0.10` for quoted coefficient statements and `delta <= 0.20` for broader presentation language.

## Open Questions

- Phase 3 still has to decide the concrete hardware estimator for the fixed-observable correlator.
- The full-q80 global OLE question remains unresolved and must not be silently merged into the subset-observable route.
