---
phase: "03"
plan: "02"
depth: standard
one-liner: "Phase 3 fixed the q80 subset-locality wording, adopted seeded far-disjoint controls, and recorded a successful first q80 pilot on S_A = 0..9 without weakening the full-q80 unresolved block."
subsystem:
  - hardware
  - analysis
  - guardrail
tags:
  - q80
  - subset-locality
  - hardware
  - scale-up
  - guardrail
requires:
  - "files/quantum-math-lab/results/hardware/phase3_q20_SA_q0_raw_vs_mit.json"
  - "files/quantum-math-lab/results/hardware/phase3_q20_SA_q19_raw_vs_mit.json"
  - "files/quantum-math-lab/results/hardware/phase3_q32_SA_q0_raw_vs_mit.json"
  - "files/quantum-math-lab/results/hardware/phase3_q32_SA_q31_raw_vs_mit.json"
  - "files/quantum-math-lab/results/hardware/phase3_q80pilot_SA_q0_raw_vs_mit.json"
  - "files/quantum-math-lab/results/hardware/phase3_q80pilot_SA_q79_raw_vs_mit.json"
provides:
  - "Completed q80 scope note with explicit subset labels, branch controls, raw-versus-mitigated pilot table, and unresolved full-q80 block"
  - "Seeded far-disjoint control rule for S_A and S_B carry-forward language"
  - "Successful first q80 subset-proxy pilot recorded as a scale-up milestone"
affects:
  - "Phase 3 milestone closure"
  - "q80 claim discipline"
  - "Follow-on symmetric second-subset pilot planning"
methods:
  added:
    - "Seeded far-disjoint control selection for subset-locality comparisons"
    - "Shallow-depth q32 pilot before the q80 jump"
    - "Raw-versus-mitigated pilot comparison with fixed subset labels and spread gate"
  patterns:
    - "Promote far-disjoint controls over near-boundary diagnostics when the two disagree"
    - "Treat a clean first q80 subset pilot as a scale-up milestone, not as full closure"
key-files:
  created:
    - ".gpd/research/Q80_SCOPE.md"
  modified:
    - ".gpd/phases/03/03-RESEARCH.md"
    - ".gpd/phases/03/03-02-PLAN.md"
    - "files/quantum-math-lab/scripts/run-q32-q80-pilot-scaleup.sh"
key-decisions:
  - "Use the seeded far-disjoint controls as the primary subset-locality references: S_A uses q=19 at q20 scale and q=79 in the q80 pilot; S_B uses q=0."
  - "Demote the earlier near-boundary S_A q=10 comparison to diagnostic-only status."
  - "Record the q80 S_A pilot (q=0 versus q=79) as a successful scale-up milestone."
  - "Keep the symmetric second-subset q80 pilot as valuable follow-up, but not a blocker for the current milestone."
patterns-established:
  - "A width jump is admissible when the same shallow-depth overlap-versus-far-disjoint structure survives at each intermediate width."
  - "Subset-locality evidence remains subset-locality evidence even when the width reaches 80 qubits."
conventions:
  - "primary q20 seeded controls: S_A q=0 vs q=19, S_B q=10 vs q=0"
  - "q80 pilot subset: S_A = 0..9"
  - "q80 pilot branches: q=0 overlap, q=79 far-disjoint"
plan_contract_ref: ".gpd/phases/03/03-02-PLAN.md#/contract"
contract_results:
  claims:
    claim-q80-visibility:
      status: passed
      summary: "The q80 scope note now fixes subset labels, seeded far-disjoint controls, a raw-versus-mitigated pilot table, and a successful first q80 pilot while preserving the explicit unresolved full-q80 block."
      linked_ids:
        - deliv-q80-scope-note
        - test-q80-scope-guard
        - ref-levelb-evidence
        - ref-status
        - manifest-levelc-v1
        - protocol-levelc-v1
        - ibm-raw-vs-mit
        - ref-q14-manifest
        - ref-algorithmiq-ole
      evidence: []
  deliverables:
    deliv-q80-scope-note:
      status: passed
      path: ".gpd/research/Q80_SCOPE.md"
      summary: "Completed q80 continuation note with subset labels, guardrails, seeded control updates, q80 pilot contrast values, raw-versus-mitigated pilot table, and the unresolved full-q80 block."
      linked_ids:
        - claim-q80-visibility
        - test-q80-scope-guard
  acceptance_tests:
    test-q80-scope-guard:
      status: passed
      summary: "Both subset families remain explicit in the note, at least one depth-wise contrast metric is reported, raw-versus-mitigated pilot fields are spelled out, and subset evidence is never presented as final full-q80 evidence."
      linked_ids:
        - claim-q80-visibility
        - deliv-q80-scope-note
        - ref-levelb-evidence
        - ref-status
  references:
    ref-levelb-evidence:
      status: completed
      completed_actions:
        - read
        - use
        - avoid
      missing_actions: []
      summary: "Used to keep the q80 route subset-scoped and to block any slide into full-q80 wording."
    ref-status:
      status: completed
      completed_actions:
        - read
        - use
        - avoid
      missing_actions: []
      summary: "Used as the binding anti-overclaim source for q80 scope and milestone language."
    manifest-levelc-v1:
      status: completed
      completed_actions:
        - use
        - compare
      missing_actions: []
      summary: "Used to preserve level-C continuity while widening the subset-locality hardware path."
    protocol-levelc-v1:
      status: completed
      completed_actions:
        - read
        - compare
        - use
      missing_actions: []
      summary: "Used to keep raw-versus-mitigated reporting and scope wording aligned with the hardware protocol discipline."
    ibm-raw-vs-mit:
      status: completed
      completed_actions:
        - read
        - compare
        - use
      missing_actions: []
      summary: "Used to express the q80 pilot as a raw-versus-mitigated subset-locality result with explicit spread rather than a hidden claim jump."
    ref-q14-manifest:
      status: completed
      completed_actions:
        - read
        - compare
      missing_actions: []
      summary: "Used as background continuity so the q80 language inherits the same q14 naming and control discipline."
    ref-algorithmiq-ole:
      status: completed
      completed_actions:
        - read
        - compare
      missing_actions: []
      summary: "Used only as a fixed-observable definition anchor so subset results are not mislabeled as full-q80 OLE."
  forbidden_proxies:
    fp-03-02-subset-as-full:
      status: rejected
      notes: "The scope note says explicitly that subset-locality evidence does not close the full-q80 fixed-observable question."
  uncertainty_markers:
    weakest_anchors:
      - "A symmetric second-subset q80 confirmation remains open and would strengthen the current milestone."
    unvalidated_assumptions: []
    competing_explanations: []
    disconfirming_observations: []
comparison_verdicts:
  - subject_id: test-q80-scope-guard
    subject_kind: acceptance_test
    subject_role: decisive
    reference_id: ref-levelb-evidence
    comparison_kind: experiment
    metric: "subset/full honesty"
    threshold: "subset evidence remains subset evidence even after the width jump"
    verdict: pass
    recommended_action: "Keep all q80 wording pinned to subset-locality and avoid full-q80 language until a new estimator exists."
    notes: "The note keeps the unresolved full-q80 block visible and uses the q80 pilot only as a subset-proxy milestone."
  - subject_id: test-q80-scope-guard
    subject_kind: acceptance_test
    subject_role: decisive
    reference_id: ibm-raw-vs-mit
    comparison_kind: benchmark
    metric: "raw-versus-mitigated reporting discipline"
    threshold: "pilot tables retain raw and mitigated values with explicit spread"
    verdict: pass
    recommended_action: "Quote mitigated contrasts for the main verdict, but keep the raw rows visible beside them."
    notes: "The completed note now carries a compact q80 pilot table with both raw and readout-mitigated fields."
  - subject_id: test-q80-scope-guard
    subject_kind: acceptance_test
    subject_role: supporting
    reference_id: manifest-levelc-v1
    comparison_kind: cross_method
    metric: "scale-up continuity"
    threshold: "shallow-depth overlap-versus-far-disjoint structure survives from seeded q20 controls through q32 into the first q80 pilot"
    verdict: pass
    recommended_action: "Treat the q80 S_A pilot as a valid scale-up milestone and only spend more hardware time when stronger symmetry is needed."
    notes: "The q80 pilot keeps strong shallow-depth separation: +0.98420 at depth 1 and +0.89110 at depth 2."

## Phase 3 milestone conclusion and follow-up

Phase 3 closes with a successful hardware scale-up milestone under the project's subset-locality interpretation boundary. The q14 hardware mapping path is now formalized with explicit anti-overclaim guardrails, corrected local-fold checkpoint ZNE remains the strongest admissible q14 hardware evidence, and the q80 continuation note records a successful first subset pilot on `S_A = 0..9` using the overlap-versus-far-disjoint control pair `q=0` versus `q=79`. At shallow depth, this pilot preserves strong subset-locality separation on hardware while remaining explicitly below any full-q80 or OLE-equivalent claim.

Follow-up research directions:
- Symmetric second-subset q80 validation: run the companion subset pilot to test whether the same shallow-depth overlap-versus-far-disjoint separation survives on the second fixed support.
- Full-q80 estimator program: move beyond subset-proxy state-return baselines toward an explicit, independently verifiable fixed-observable full-q80 construction.
