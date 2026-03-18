---
phase: "02"
plan: "01"
depth: standard
one-liner: "Phase 2 established an exact q14 OLE artifact on the active exact-short manifest by propagating P = Z_0 as a sparse Pauli expansion and extracting overlap/disjoint branch weights without dense full-system operators."
subsystem:
  - exact-benchmark
  - operator-propagation
  - analysis
tags:
  - operator-loschmidt-echo
  - q14
  - sparse-pauli
  - exact
requires:
  - ".gpd/phases/01/ole_formalism_lock.md"
  - ".gpd/phases/01/ole_small_delta_bridge.md"
provides:
  - "Exact q14 F_delta(Z_0) data on the active depth-1..4 exact-short manifest"
  - "Manifest-tied overlap and disjoint branch data with explicit F_delta and f_delta translations"
  - "An exact implementation check showing the disjoint X_10 branch stays flat on the active manifest"
affects:
  - "Phase 2 benchmark overlay and delta^2 analysis"
  - "Phase 3 hardware/q80 handoff"
methods:
  added:
    - "Sparse Pauli propagation through the RX/RZ/CZ brickwork circuit"
    - "Branch-resolved anti-commuting weight extraction for X_0 and X_10"
    - "Dense small-system cross-check for the exact F_delta evaluator"
  patterns:
    - "Keep the q14 benchmark tied to the existing manifest instead of introducing a fresh task family"
    - "Use disjoint-support flatness as an implementation bug trap, not just as a sanity note"
key-files:
  created:
    - "files/quantum-math-lab/qiskit_black_hole_ole_exact.py"
    - "files/quantum-math-lab/results/ole/black_hole_ole_q14_exact_small_delta.json"
  modified: []
key-decisions:
  - "Add a dedicated exact OLE script instead of overloading the existing perturbed_echo runner."
  - "Compute F_delta(P) from exact Pauli-basis coefficients and carry f_delta(O)=2^-14 F_delta(P) explicitly in the JSON."
  - "Treat the q10 disjoint branch as an exact light-cone control that must remain flat across depths 1..4."
patterns-established:
  - "For this brickwork family, q14 exact OLE is practical because the evolved Pauli support remains light-cone limited."
  - "Manifest continuity matters more than matching the baseline observable semantics."
conventions:
  - "operator_picture = propagate A_P(U) = U P U^dagger exactly in the Pauli basis"
  - "observable_normalization = report F_delta(P) first and store f_delta(O)=2^-14 F_delta(P) alongside it"
  - "generator_lock = overlap X_0, disjoint X_10"
plan_contract_ref: ".gpd/phases/02/02-01-PLAN.md#/contract"
contract_results:
  claims:
    claim-q14-exact-ole-data:
      status: passed
      summary: "The active q14 exact-short family now has an exact fixed-observable OLE artifact computed via sparse Pauli propagation, with overlap and disjoint branches resolved without state proxies or dense 14-qubit operators."
      linked_ids:
        - deliv-exact-ole-script
        - deliv-exact-ole-data
        - test-sparse-pauli-exactness
        - test-active-manifest-disjoint-control
        - test-manifest-compatibility
        - ref-formalism-lock
        - ref-small-delta-bridge
        - ref-phase2-handoff
        - ref-q14-manifest
        - ref-scrambling-script
        - ref-q14-baseline-artifact
      evidence: []
  deliverables:
    deliv-exact-ole-script:
      status: passed
      path: "files/quantum-math-lab/qiskit_black_hole_ole_exact.py"
      summary: "Dedicated exact q14 OLE runner that reuses the repo's brickwork scrambler, performs exact Pauli-basis propagation, self-checks the local gate rules, and writes branch-resolved F_delta/f_delta data."
      linked_ids:
        - claim-q14-exact-ole-data
        - test-sparse-pauli-exactness
        - test-manifest-compatibility
    deliv-exact-ole-data:
      status: passed
      path: "files/quantum-math-lab/results/ole/black_hole_ole_q14_exact_small_delta.json"
      summary: "Exact q14 depth-1..4 artifact with manifest snapshot, self-checks, depth-0 sanity checks, operator statistics, and overlap/disjoint branch curves on the locked delta grid."
      linked_ids:
        - claim-q14-exact-ole-data
        - test-sparse-pauli-exactness
        - test-active-manifest-disjoint-control
        - test-manifest-compatibility
  acceptance_tests:
    test-sparse-pauli-exactness:
      status: passed
      summary: "The exact script propagates the evolved observable in a Pauli basis, preserves Hilbert-Schmidt norm at 1 within tolerance, and passes both local gate-rule checks and a dense 3-qubit F_delta cross-check."
      linked_ids:
        - claim-q14-exact-ole-data
        - deliv-exact-ole-script
        - deliv-exact-ole-data
        - ref-small-delta-bridge
    test-active-manifest-disjoint-control:
      status: passed
      summary: "The disjoint control branch G = X_10 is exactly flat on the active q14 depths 1..4, with kappa = 0 and F_delta = 1 across the stored delta grid."
      linked_ids:
        - claim-q14-exact-ole-data
        - deliv-exact-ole-data
        - ref-formalism-lock
        - ref-phase2-handoff
    test-manifest-compatibility:
      status: passed
      summary: "The artifact records the active q14 exact-short settings directly: qubits = 14, depths = [1,2,3,4], trials = 3, seed = 424242, and the same scrambler family and seed discipline as the existing benchmark path."
      linked_ids:
        - claim-q14-exact-ole-data
        - deliv-exact-ole-data
        - ref-q14-manifest
        - ref-scrambling-script
  references:
    ref-formalism-lock:
      status: completed
      completed_actions:
        - read
        - use
      missing_actions: []
      summary: "Used the Phase 1 lock to keep P = Z_0, overlap X_0, disjoint X_10, and the report-level normalization fixed."
    ref-small-delta-bridge:
      status: completed
      completed_actions:
        - read
        - use
        - compare
      missing_actions: []
      summary: "Used the small-delta bridge to align the exact data schema with F_delta(P), f_delta(O), and the branch-resolved kappa interpretation."
    ref-phase2-handoff:
      status: completed
      completed_actions:
        - read
        - use
      missing_actions: []
      summary: "Used the handoff note to preserve the active manifest, branch choices, and the disjoint-control expectation."
    ref-q14-manifest:
      status: completed
      completed_actions:
        - read
        - use
        - compare
      missing_actions: []
      summary: "Compared the exact artifact against the active q14 exact-short manifest and embedded the matching manifest snapshot in the JSON."
    ref-scrambling-script:
      status: completed
      completed_actions:
        - read
        - compare
        - use
      missing_actions: []
      summary: "Reused the existing brickwork scrambler and parse-depth handling to keep Phase 2 on the same circuit family and seed discipline as the baseline path."
    ref-q14-baseline-artifact:
      status: completed
      completed_actions:
        - read
        - use
      missing_actions: []
      summary: "Kept the new exact OLE artifact anchored to the existing q14 exact-short comparison family via the baseline reference and shared manifest settings."
  forbidden_proxies:
    fp-pure-state-proxy:
      status: rejected
      notes: "The script computes infinite-temperature operator traces from Pauli-basis coefficients and never substitutes a |0...0> return probability."
    fp-dense-operator-detour:
      status: rejected
      notes: "The q14 benchmark is computed by sparse Pauli propagation; dense operators only appear inside a 3-qubit self-check rather than the production path."
  uncertainty_markers:
    weakest_anchors:
      - "The exact sparse-Pauli route is validated only for the active q14 depth-1..4 light cone; deeper or larger systems may need a different representation."
    unvalidated_assumptions: []
    competing_explanations: []
    disconfirming_observations: []
comparison_verdicts:
  - subject_id: claim-q14-exact-ole-data
    subject_kind: claim
    subject_role: decisive
    reference_id: ref-small-delta-bridge
    comparison_kind: cross_method
    metric: "F_delta/f_delta/kappa schema continuity"
    threshold: "artifact structure stays aligned with the Phase 1 small-delta bridge"
    verdict: pass
    recommended_action: "Use the stored branch curves directly in the delta^2 benchmark report."
    notes: "The JSON stores F_delta(P), f_delta(O), and branch-resolved kappa values in the fixed-picture convention."
  - subject_id: claim-q14-exact-ole-data
    subject_kind: claim
    subject_role: supporting
    reference_id: ref-phase2-handoff
    comparison_kind: benchmark
    metric: "branch/control continuity"
    threshold: "active overlap and disjoint controls match the handoff note"
    verdict: pass
    recommended_action: "Keep X_0 as the signal branch and X_10 as the exact flat control in all Wave 2 plots."
    notes: "The executed artifact preserves the locked branches and the disjoint-control expectation from the handoff."
  - subject_id: test-manifest-compatibility
    subject_kind: acceptance_test
    subject_role: decisive
    reference_id: ref-q14-manifest
    comparison_kind: benchmark
    metric: "qubit/depth/trial/seed continuity"
    threshold: "exact match to the active q14 exact-short manifest"
    verdict: pass
    recommended_action: "Use this JSON as the Phase 2 source artifact for all later q14 OLE analysis."
    notes: "The artifact stores qubits = 14, depths = [1,2,3,4], trials = 3, seed = 424242, and a manifest snapshot."
  - subject_id: test-sparse-pauli-exactness
    subject_kind: acceptance_test
    subject_role: supporting
    reference_id: ref-scrambling-script
    comparison_kind: cross_method
    metric: "scrambler-family reuse"
    threshold: "reuse the existing RX/RZ/CZ brickwork generator and seed discipline"
    verdict: pass
    recommended_action: "Treat the exact OLE script as a companion runner for the same circuit family rather than a forked benchmark path."
    notes: "The new script imports and reuses the existing scrambler and depth parsing helpers."
  - subject_id: test-sparse-pauli-exactness
    subject_kind: acceptance_test
    subject_role: supporting
    reference_id: ref-small-delta-bridge
    comparison_kind: cross_method
    metric: "exactness checks"
    threshold: "Hilbert-Schmidt norm preserved at 1 and dense 3-qubit F_delta cross-check max abs error <= 1e-10"
    verdict: pass
    recommended_action: "Carry the exact branch curves forward into the delta^2 fits without reopening the estimator."
    notes: "The script self-checks both local gate conjugation rules and a full dense-trace benchmark on a smaller system."
  - subject_id: deliv-exact-ole-data
    subject_kind: deliverable
    subject_role: supporting
    reference_id: ref-q14-baseline-artifact
    comparison_kind: baseline
    metric: "benchmark-family continuity"
    threshold: "same q14 exact-short family while keeping the OLE observable semantics explicit"
    verdict: pass
    recommended_action: "Overlay the new OLE curves with the perturbed_echo baseline in Wave 2 without relabeling the baseline as OLE."
    notes: "The new artifact shares the manifest family and stores a baseline reference, but the observable semantics remain distinct by design."
duration: "10min"
completed: "2026-03-18"
---

# Phase 2 Plan 01 Summary

**Phase 2 established an exact q14 OLE artifact on the active exact-short manifest by propagating `P = Z_0` as a sparse Pauli expansion and extracting overlap/disjoint branch weights without dense full-system operators.**

## Performance

- **Duration:** 10 min
- **Started:** 2026-03-18T07:31:00Z
- **Completed:** 2026-03-18T07:41:08Z
- **Tasks:** 2
- **Files modified:** 2

## Key Results

- The new exact q14 runner produced a manifest-tied JSON artifact for `F_delta(Z_0)` on depths `1..4` with delta grid `0.0..0.3`.
- The evolved observable stayed light-cone limited, with mean Pauli term counts `3, 12, 39, 195` and support maxima `1, 2, 3, 4` across depths `1..4`.
- The overlap branch remained nontrivial with mean `kappa_{X_0}` values `3.9627, 2.3433, 1.9120, 2.5778`, while the disjoint `X_10` branch stayed exactly flat with `kappa = 0` and `F_delta = 1`.

## Task Commits

1. **Task 1: Implement the exact q14 sparse-Pauli OLE runner and write the artifact** - `1653dda`

## Files Created/Modified

- `files/quantum-math-lab/qiskit_black_hole_ole_exact.py` - exact q14 OLE evaluator with gate-rule and dense cross-check self-tests
- `files/quantum-math-lab/results/ole/black_hole_ole_q14_exact_small_delta.json` - manifest-tied q14 artifact with branch curves, operator statistics, and sanity checks

## Next Phase Readiness

Wave 2 can now build the `delta^2` benchmark overlay directly from one exact q14 OLE artifact and the existing q14 `perturbed_echo` baseline without reopening the estimator or the manifest definition.

## Contract Coverage

- Claim IDs advanced: `claim-q14-exact-ole-data -> passed`
- Deliverable IDs produced: `deliv-exact-ole-script`, `deliv-exact-ole-data`
- Acceptance test IDs run: `test-sparse-pauli-exactness`, `test-active-manifest-disjoint-control`, `test-manifest-compatibility`
- Reference IDs surfaced: `ref-formalism-lock`, `ref-small-delta-bridge`, `ref-phase2-handoff`, `ref-q14-manifest`, `ref-scrambling-script`, `ref-q14-baseline-artifact`
- Forbidden proxies rejected or violated: `fp-pure-state-proxy -> rejected`, `fp-dense-operator-detour -> rejected`
- Decisive comparison verdicts: `test-manifest-compatibility -> pass`

## Equations Derived

**Eq. (02.1):**

$$
A_P(U) = U P U^\dagger, \qquad P = Z_0
$$

**Eq. (02.2):**

$$
F_\delta(P;U,G) = 1 - \left(1 - \cos(2\delta)\right) w_{\mathrm{anti}}(G; A_P(U))
$$

**Eq. (02.3):**

$$
\kappa_G(P;U) = 4\, w_{\mathrm{anti}}(G; A_P(U)), \qquad
f_\delta(O) = 2^{-14} F_\delta(P), \quad O = \frac{P}{\sqrt{2^{14}}}
$$

## Validations Completed

- The script passed local `RX`, `RZ`, and `CZ` conjugation-rule checks with maximum absolute error `1.11e-16`.
- The production evaluator passed a dense 3-qubit end-to-end trace benchmark with maximum absolute error `4.44e-16`.
- The q14 artifact preserved Hilbert-Schmidt norm `1` to numerical tolerance at every active depth.
- The disjoint `X_10` branch stayed exactly flat on the active manifest, so the intended light-cone control behaved as a bug trap rather than a qualitative expectation.

## Decisions & Deviations

The only real implementation choice was to add a dedicated exact OLE runner rather than overloading the state-return benchmark script. There was no contract deviation: the final artifact stayed on the active manifest, used the locked observable/generator choices, and kept the baseline semantics separate from the OLE quantity.

## Open Questions

- The exact sparse-Pauli representation is clearly adequate for the active q14 depth-1..4 family, but Phase 2 still needs to check how stable the overlap-branch quadratic fits remain across shrinking `delta` windows.
- Phase 3 still has to translate this exact classical artifact into a concrete hardware-ready estimator and decide how q80 subset observables will inherit the fixed-observable semantics.
