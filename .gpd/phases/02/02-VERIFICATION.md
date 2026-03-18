---
phase: "02"
verified: "2026-03-18T07:54:18Z"
status: gaps_found
score: "15/15 contract targets verified; 2 follow-up checks suggested"
plan_contract_ref: ".gpd/phases/02/02-03-PLAN.md#/contract"
contract_results:
  claims:
    claim-q14-small-delta-validity:
      status: passed
      summary: "The phase goal is verified: the q14 exact benchmark has exact OLE data, a report-level benchmark artifact, stable shrinking-window fits, an exact disjoint control, and a Phase 3 handoff that preserves the hardware/q80 guardrails."
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
      evidence:
        - verifier: codex
          method: exact artifact self-checks, shrinking-window regression, and artifact audit
          confidence: high
          claim_id: claim-q14-small-delta-validity
          deliverable_id: deliv-small-delta-validation-note
          acceptance_test_id: test-fit-window-stability
          reference_id: ref-exact-ole-data
          evidence_path: ".gpd/phases/02/02-VERIFICATION.md"
  deliverables:
    deliv-small-delta-validation-note:
      status: passed
      path: ".gpd/phases/02/q14_small_delta_validation.md"
      summary: "Artifact exists, records three shrinking fit windows for both branches, and states explicit pass/fail wording plus the baseline exclusion rule."
      linked_ids:
        - claim-q14-small-delta-validity
        - test-fit-window-stability
        - test-control-flatness
    deliv-phase3-handoff-note:
      status: passed
      path: ".gpd/phases/02/q14_phase3_handoff.md"
      summary: "Artifact exists and preserves the hardware-ready local-Pauli continuity rule, the q80 subset/full split, and the warning against relabeling existing hardware outputs as OLE."
      linked_ids:
        - claim-q14-small-delta-validity
        - test-phase3-guardrails
  acceptance_tests:
    test-fit-window-stability:
      status: passed
      summary: "Independent least-squares fits on the exact q14 overlap/disjoint curves confirm that overlap keeps b0 near 1 and slope near -kappa/2 under shrinking windows, while disjoint stays flat."
      linked_ids:
        - claim-q14-small-delta-validity
        - deliv-small-delta-validation-note
        - ref-exact-ole-data
        - ref-small-delta-bridge
    test-control-flatness:
      status: passed
      summary: "The validation note treats the disjoint X_10 branch as an exact flat control and makes any non-flat result an implementation failure."
      linked_ids:
        - claim-q14-small-delta-validity
        - deliv-small-delta-validation-note
        - ref-exact-ole-data
        - ref-phase2-handoff
    test-phase3-guardrails:
      status: passed
      summary: "The Phase 3 handoff note preserves the local-Pauli hardware-ready direction, the subset/full-q80 split, and explicit anti-overclaim wording."
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
      summary: "Verified as the source of the exact overlap/disjoint curves, self-check metadata, and fit inputs."
    ref-q14-benchmark-report:
      status: completed
      completed_actions:
        - read
        - use
      missing_actions: []
      summary: "Verified as the benchmark artifact whose interpretation is locked by the validation note."
    ref-small-delta-bridge:
      status: completed
      completed_actions:
        - read
        - compare
        - use
      missing_actions: []
      summary: "Verified as the source of the target intercept and target slope relation b2 -> -kappa/2."
    ref-phase2-handoff:
      status: completed
      completed_actions:
        - read
        - compare
        - use
      missing_actions: []
      summary: "Verified as the source of the required fit windows, baseline exclusion, and disjoint-control expectation."
    ref-status:
      status: completed
      completed_actions:
        - read
        - use
        - avoid
      missing_actions: []
      summary: "Verified as the binding scope guard for the q14-only claim and the subset-scoped 80q evidence."
    ref-hardware-protocol:
      status: completed
      completed_actions:
        - read
        - compare
        - use
      missing_actions: []
      summary: "Verified as the method anchor constraining how hardware-ready language can be carried forward without overstating current evidence."
    ref-levelb-evidence:
      status: completed
      completed_actions:
        - read
        - use
        - avoid
      missing_actions: []
      summary: "Verified as the current subset-observable 80q evidence anchor whose scope must not be inflated."
  forbidden_proxies:
    fp-fit-everything:
      status: rejected
      notes: "The fit uses only the exact OLE onset windows and excludes the full-kick perturbed_echo baseline entirely."
    fp-hardware-ready-means-done:
      status: rejected
      notes: "The handoff preserves hardware-ready continuity while stating explicitly that the estimator still belongs to Phase 3."
  uncertainty_markers:
    weakest_anchors:
      - "The concrete hardware estimator remains unverified and belongs to the next phase."
    unvalidated_assumptions: []
    competing_explanations: []
    disconfirming_observations: []
comparison_verdicts:
  - subject_id: claim-q14-small-delta-validity
    subject_kind: claim
    subject_role: decisive
    reference_id: ref-exact-ole-data
    comparison_kind: benchmark
    metric: "exact q14 fit-input continuity"
    threshold: "verification is tied directly to the exact overlap/disjoint artifact"
    verdict: pass
    recommended_action: "Keep the exact q14 JSON as the only source of small-delta fit inputs."
    notes: "The fit tables and control checks all come directly from the exact OLE artifact."
  - subject_id: claim-q14-small-delta-validity
    subject_kind: claim
    subject_role: decisive
    reference_id: ref-q14-benchmark-report
    comparison_kind: benchmark
    metric: "report-level continuity"
    threshold: "the benchmark report remains the validated narrative artifact for Phase 2"
    verdict: pass
    recommended_action: "Use the report and validation note together in later writeups."
    notes: "The verification locks the report's interpretation rather than rewriting it."
  - subject_id: claim-q14-small-delta-validity
    subject_kind: claim
    subject_role: decisive
    reference_id: ref-small-delta-bridge
    comparison_kind: cross_method
    metric: "agreement with the Phase 1 bridge"
    threshold: "intercept and slope behavior match the bridge expectation b0 -> 1 and b2 -> -kappa/2"
    verdict: pass
    recommended_action: "Carry the same small-delta bridge forward into Phase 3."
    notes: "The fitted overlap curves converge exactly in the direction required by the bridge note."
  - subject_id: claim-q14-small-delta-validity
    subject_kind: claim
    subject_role: decisive
    reference_id: ref-phase2-handoff
    comparison_kind: benchmark
    metric: "fit-window and baseline-exclusion continuity"
    threshold: "the declared windows and the baseline exclusion rule survive intact"
    verdict: pass
    recommended_action: "Keep the same windows and exclusion rule unless a later phase supersedes them explicitly."
    notes: "The verification uses the exact 0.30/0.20/0.10 windows and excludes perturbed_echo from the fit."
  - subject_id: claim-q14-small-delta-validity
    subject_kind: claim
    subject_role: decisive
    reference_id: ref-status
    comparison_kind: benchmark
    metric: "scope discipline"
    threshold: "Phase 2 closeout stays inside the current q14-only and subset-scoped evidence base"
    verdict: pass
    recommended_action: "Preserve the same scope wording in Phase 3 artifacts."
    notes: "The handoff keeps the current claim boundaries explicit."
  - subject_id: claim-q14-small-delta-validity
    subject_kind: claim
    subject_role: decisive
    reference_id: ref-hardware-protocol
    comparison_kind: cross_method
    metric: "hardware-ready continuity"
    threshold: "future path stays local-Pauli and bookkeeping-compatible"
    verdict: pass
    recommended_action: "Use the local Pauli family as the Phase 3 estimator-design anchor."
    notes: "The handoff preserves protocol continuity without claiming a solved estimator."
  - subject_id: claim-q14-small-delta-validity
    subject_kind: claim
    subject_role: supporting
    reference_id: ref-levelb-evidence
    comparison_kind: experiment
    metric: "subset/full q80 scope honesty"
    threshold: "subset evidence remains subset evidence"
    verdict: pass
    recommended_action: "Retain subset-scoped language until fuller evidence exists."
    notes: "The handoff keeps the subset/full split explicit."
  - subject_id: test-fit-window-stability
    subject_kind: acceptance_test
    subject_role: decisive
    reference_id: ref-exact-ole-data
    comparison_kind: benchmark
    metric: "fit-window stability"
    threshold: "overlap branch keeps b0 near 1 and slope near -kappa/2 while disjoint stays flat"
    verdict: pass
    recommended_action: "Quote overlap coefficients from delta <= 0.10 and keep the wider windows as context."
    notes: "Worst overlap slope error falls from 2.76% at delta <= 0.30 to 0.33% at delta <= 0.10."
  - subject_id: test-fit-window-stability
    subject_kind: acceptance_test
    subject_role: decisive
    reference_id: ref-small-delta-bridge
    comparison_kind: cross_method
    metric: "agreement with Phase 1 small-delta target"
    threshold: "fitted intercepts and slopes converge toward the bridge expectation"
    verdict: pass
    recommended_action: "Carry the Phase 1 bridge equations forward unchanged."
    notes: "The exact q14 fits satisfy the expected b0 -> 1 and b2 -> -kappa/2 trend."
  - subject_id: test-control-flatness
    subject_kind: acceptance_test
    subject_role: decisive
    reference_id: ref-phase2-handoff
    comparison_kind: benchmark
    metric: "control-branch flatness"
    threshold: "disjoint X_10 branch remains an exact flat control"
    verdict: pass
    recommended_action: "Treat any future non-flat disjoint result as an implementation bug until proven otherwise."
    notes: "The disjoint branch stays at intercept 1 and slope 0 on every declared window."
  - subject_id: test-phase3-guardrails
    subject_kind: acceptance_test
    subject_role: decisive
    reference_id: ref-status
    comparison_kind: benchmark
    metric: "claim-discipline continuity"
    threshold: "Phase 3 handoff stays inside the q14-only and subset-scoped evidence base"
    verdict: pass
    recommended_action: "Retain the same scope wording in future planning and writing artifacts."
    notes: "The handoff keeps the current q14-only and 80q subset claim boundaries explicit."
  - subject_id: test-phase3-guardrails
    subject_kind: acceptance_test
    subject_role: decisive
    reference_id: ref-hardware-protocol
    comparison_kind: cross_method
    metric: "hardware-ready continuity"
    threshold: "Phase 3 path stays local-Pauli and bookkeeping-compatible"
    verdict: pass
    recommended_action: "Use the local Pauli family as the Phase 3 estimator-design anchor."
    notes: "The handoff preserves compatibility with the existing hardware workflow without claiming completion."
  - subject_id: test-phase3-guardrails
    subject_kind: acceptance_test
    subject_role: decisive
    reference_id: ref-levelb-evidence
    comparison_kind: experiment
    metric: "q80 subset/full honesty"
    threshold: "subset evidence remains subset evidence"
    verdict: pass
    recommended_action: "Keep 80q work subset-scoped unless a later phase justifies a fuller proxy explicitly."
    notes: "The handoff preserves the subset/full split reflected in the current Level B evidence."
  - subject_id: ref-exact-ole-data
    subject_kind: reference
    subject_role: decisive
    reference_id: ref-exact-ole-data
    comparison_kind: benchmark
    metric: "source-artifact coverage"
    threshold: "exact q14 OLE artifact is fully represented in the validation"
    verdict: pass
    recommended_action: "Keep the exact JSON as the only fit input source."
    notes: "The verification reuses the exact self-checks and the exact fit inputs."
  - subject_id: ref-q14-benchmark-report
    subject_kind: reference
    subject_role: decisive
    reference_id: ref-q14-benchmark-report
    comparison_kind: benchmark
    metric: "report-interpretation coverage"
    threshold: "benchmark report meaning is explicitly certified"
    verdict: pass
    recommended_action: "Use the report and validation note together in later writeups."
    notes: "The benchmark report is now explicitly tied to the validated small-delta reading."
  - subject_id: ref-small-delta-bridge
    subject_kind: reference
    subject_role: decisive
    reference_id: ref-small-delta-bridge
    comparison_kind: cross_method
    metric: "bridge-equation continuity"
    threshold: "Phase 2 verification stays aligned with the Phase 1 equations"
    verdict: pass
    recommended_action: "Do not reopen the bridge equations during Phase 3 planning."
    notes: "The verification uses the same target intercept and slope relation defined in Phase 1."
  - subject_id: ref-phase2-handoff
    subject_kind: reference
    subject_role: decisive
    reference_id: ref-phase2-handoff
    comparison_kind: benchmark
    metric: "handoff-rule coverage"
    threshold: "declared windows and baseline exclusion survive into validation"
    verdict: pass
    recommended_action: "Keep the declared windows and exclusion rule unless later work explicitly supersedes them."
    notes: "The verification follows the exact fit-window contract from the handoff note."
  - subject_id: ref-status
    subject_kind: reference
    subject_role: decisive
    reference_id: ref-status
    comparison_kind: benchmark
    metric: "scope-guard coverage"
    threshold: "handoff remains inside current defensible claim language"
    verdict: pass
    recommended_action: "Use STATUS.md wording whenever a Phase 3 artifact risks overclaiming."
    notes: "The verification confirms that q14-only and subset/full boundaries remain explicit."
  - subject_id: ref-hardware-protocol
    subject_kind: reference
    subject_role: decisive
    reference_id: ref-hardware-protocol
    comparison_kind: cross_method
    metric: "protocol continuity coverage"
    threshold: "hardware-ready path stays compatible with the existing protocol"
    verdict: pass
    recommended_action: "Keep the local-Pauli, bookkeeping-compatible path as the next-step design constraint."
    notes: "The handoff adopts protocol continuity without claiming a solved estimator."
  - subject_id: ref-levelb-evidence
    subject_kind: reference
    subject_role: decisive
    reference_id: ref-levelb-evidence
    comparison_kind: experiment
    metric: "subset-evidence coverage"
    threshold: "handoff honors the current 80q subset evidence scope"
    verdict: pass
    recommended_action: "Retain subset-scoped language until fuller evidence exists."
    notes: "The verification confirms that the handoff does not inflate subset evidence into a full-q80 claim."
suggested_contract_checks:
  - check: "Re-verify any future graphical rewrite of the q14 benchmark report against the exact CSV/JSON artifacts"
    reason: "The decisive benchmark artifact is currently markdown-plus-table based; a later figure rewrite must preserve the same delta^2 panels, branch visibility, and baseline exclusion rules."
    suggested_subject_kind: reference
    suggested_subject_id: "ref-q14-benchmark-report"
    evidence_path: "files/quantum-math-lab/results/ole/q14_ole_vs_delta2_benchmark.md"
  - check: "Close the hardware-ready continuity claim with a concrete estimator artifact in Phase 3"
    reason: "Phase 2 verified semantic continuity to the hardware protocol, but the actual fixed-observable hardware estimator is intentionally deferred to the next phase."
    suggested_subject_kind: reference
    suggested_subject_id: "ref-hardware-protocol"
    evidence_path: "files/quantum-math-lab/hardware_advantage_protocol.md"
---

# Phase 2 Verification Report

## Verification Verdict

Phase 2's execution artifacts are internally consistent and the contract targets are substantively verified, but the verifier still requires two structured follow-up checks to keep the benchmark-report and hardware-continuity story explicit in future work.

## Evidence Summary

- Wave 1 exact artifact executed successfully and wrote `black_hole_ole_q14_exact_small_delta.json`.
- The exact script's built-in checks passed:
  - gate-rule self-check max absolute error: `1.11e-16`
  - dense 3-qubit end-to-end cross-check max absolute error: `4.44e-16`
- The active-manifest disjoint branch stayed exactly flat with `kappa = 0` and `F_delta = 1`.
- Wave 2 report and CSV passed structural checks:
  - report contains `delta^2`, explicit `P = Z_0`, explicit `f_delta(O)`, and explicit `perturbed_echo` baseline wording
  - CSV contains `4` baseline rows and `80` OLE rows with both branches present at every depth
- Wave 3 shrinking-window fits confirm:
  - overlap intercept stays near `1`
  - overlap slope converges toward `-kappa/2`
  - disjoint stays flat to machine precision

## Artifact Verification

Validated summary artifacts:

- `.gpd/phases/02/02-01-SUMMARY.md` passed `frontmatter validate --schema summary` and `validate summary-contract`
- `.gpd/phases/02/02-02-SUMMARY.md` passed `frontmatter validate --schema summary` and `validate summary-contract`
- `.gpd/phases/02/02-03-SUMMARY.md` passed `frontmatter validate --schema summary` and `validate summary-contract`

Validated execution artifacts:

- `files/quantum-math-lab/qiskit_black_hole_ole_exact.py`
- `files/quantum-math-lab/results/ole/black_hole_ole_q14_exact_small_delta.json`
- `files/quantum-math-lab/analyze_q14_ole_benchmark.py`
- `files/quantum-math-lab/results/ole/q14_ole_vs_delta2_benchmark.md`
- `files/quantum-math-lab/results/ole/q14_ole_vs_delta2_benchmark.csv`
- `.gpd/phases/02/q14_small_delta_validation.md`
- `.gpd/phases/02/q14_phase3_handoff.md`

## Numerical Validation Highlights

### Overlap branch

- Worst intercept deviation from `1`:
  - `delta <= 0.30`: `4.14e-4`
  - `delta <= 0.20`: `9.94e-5`
  - `delta <= 0.10`: `6.33e-6`
- Worst relative slope error versus `-kappa/2`:
  - `delta <= 0.30`: `2.76%`
  - `delta <= 0.20`: `1.27%`
  - `delta <= 0.10`: `0.33%`

### Disjoint branch

- Intercept is `1` to machine precision on all three windows.
- Fitted slope is `0` to machine precision on all three windows.
- This remains an exact locality control, not just a weaker comparison curve.

## Forbidden Proxy Audit

| Forbidden Proxy ID | What Was Forbidden | Status | Notes |
| --- | --- | --- | --- |
| `fp-fit-everything` | include the full-kick baseline or too-large windows in the small-delta fit | rejected | Only the exact OLE onset windows were fit; `perturbed_echo` stayed outside the regression |
| `fp-hardware-ready-means-done` | describe the hardware path as already solved by the exact benchmark | rejected | The handoff treats hardware as a next-step measurement-design problem |

## Comparison Verdict Ledger

All decisive benchmark, bridge, protocol, and scope-guard comparisons in the plan contract are closed as `pass` in the frontmatter ledger above.

## Suggested Contract Checks

None. The decisive Phase 2 checks are explicit and closed.
