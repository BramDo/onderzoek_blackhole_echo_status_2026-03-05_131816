---
phase: "03"
plan: "01"
depth: standard
one-liner: "Phase 3 established a contract-safe q14 hardware mapping note, executed the locked q14 branch pair on hardware, and kept corrected checkpoint ZNE admissible while blocking OLE relabeling and PE-LiNN support."
subsystem:
  - hardware
  - validation
  - guardrail
tags:
  - operator-loschmidt-echo
  - q14
  - hardware
  - zne
  - guardrail
requires:
  - "files/quantum-math-lab/benchmarks/q14_only_manifest.json"
  - "files/quantum-math-lab/results/hardware/phase3_q14_zne_xsup_s8000_f135_localfold.json"
provides:
  - "Completed q14 hardware-ready mapping note with fixed-observable bridge and command/output matrix"
  - "Phase-3 hardware wording boundary that separates baseline-compatible runner outputs from any future explicit OLE estimator"
  - "Admissible q14 checkpoint verdict anchored to corrected local-fold ZNE and explicit exclusion of PE-LiNN support"
affects:
  - "Phase 3 q80 scope wording"
  - "Hardware estimator claim discipline"
  - "Mitigation-method admissibility"
methods:
  added:
    - "Hardware-ready command/output mapping against the existing q14 runner schema"
    - "Local-tensor full-register readout mitigation path for the 14-qubit hardware branch pair"
    - "Corrected local-fold checkpoint ZNE on transpiled two-qubit gates with DD and twirling still enabled"
  patterns:
    - "Baseline-compatible hardware outputs are continuity evidence, not estimator identity"
    - "Checkpoint ZNE becomes admissible only after the folding construction is hardware-valid"
key-files:
  created:
    - ".gpd/research/OLE_HARDWARE_PATH.md"
  modified:
    - "files/quantum-math-lab/qiskit_black_hole_hardware_runner.py"
key-decisions:
  - "Keep the q14 note explicit: current hardware outputs remain baseline-compatible only and must not be relabeled as final fixed-observable OLE estimators."
  - "Treat corrected local-fold checkpoint ZNE as the strongest admissible q14 hardware checkpoint evidence."
  - "Reject PE-LiNN outputs as claim support on the current q14 hardware dataset."
patterns-established:
  - "A hardware mapping phase is not closed until it says both what is executable now and what circuit-level estimator work remains unresolved."
  - "Admissible mitigation evidence and inadmissible learned-mitigation branches must be separated explicitly in the phase note."
conventions:
  - "fixed-observable bridge: P = Z_0, O = Z_0 / sqrt(2^14)"
  - "branch labels: q = 0 overlap, q = 10 disjoint"
  - "runner outputs: perturbed_echo and perturbed_subset_echo stay baseline-only"
plan_contract_ref: ".gpd/phases/03/03-01-PLAN.md#/contract"
contract_results:
  claims:
    claim-q14-ole-bridge:
      status: passed
      summary: "The q14 hardware mapping note now freezes the manifest lock, command/output contract, anti-overclaim gate, and the admissible q14 checkpoint evidence boundary without silently relabeling existing runner outputs as OLE."
      linked_ids:
        - deliv-hardware-ready-note
        - test-hardware-ready
        - ref-algorithmiq-ole
        - ref-status
        - ref-q14-manifest
        - manifest-levelc-v1
        - protocol-levelc-v1
        - ibm-raw-vs-mit
      evidence: []
  deliverables:
    deliv-hardware-ready-note:
      status: passed
      path: ".gpd/research/OLE_HARDWARE_PATH.md"
      summary: "Completed hardware-ready mapping note with manifest lock, branch table, command/output matrix, unresolved-estimator gate, q14 execution evidence, corrected local-fold checkpoint ZNE update, and PE-LiNN exclusion."
      linked_ids:
        - claim-q14-ole-bridge
        - test-hardware-ready
  acceptance_tests:
    test-hardware-ready:
      status: passed
      summary: "The note exists, preserves the locked q14 control fields, resolves runner command arguments into output fields, and keeps the baseline-only versus explicit-estimator boundary visible."
      linked_ids:
        - claim-q14-ole-bridge
        - deliv-hardware-ready-note
        - ref-q14-manifest
        - ref-status
        - manifest-levelc-v1
        - protocol-levelc-v1
        - ibm-raw-vs-mit
  references:
    ref-algorithmiq-ole:
      status: completed
      completed_actions:
        - read
        - compare
        - use
      missing_actions: []
      summary: "Used to keep the fixed-observable bridge definition explicit and to block any silent state-return relabeling."
    ref-status:
      status: completed
      completed_actions:
        - read
        - use
        - avoid
      missing_actions: []
      summary: "Used as the binding anti-overclaim source for q14 hardware language and later q80 carry-forward wording."
    ref-q14-manifest:
      status: completed
      completed_actions:
        - read
        - use
        - compare
      missing_actions: []
      summary: "Used to freeze the q14 manifest lock and verify that the note did not drift on qubits, depths, trials, seed, or shots."
    manifest-levelc-v1:
      status: completed
      completed_actions:
        - use
        - compare
      missing_actions: []
      summary: "Used to keep the q14 hardware-ready path aligned with level-C continuity rather than a new claim family."
    protocol-levelc-v1:
      status: completed
      completed_actions:
        - read
        - compare
        - use
      missing_actions: []
      summary: "Used to preserve the anti-overclaim and raw-versus-mitigated reporting discipline in the hardware note."
    ibm-raw-vs-mit:
      status: completed
      completed_actions:
        - read
        - compare
        - use
      missing_actions: []
      summary: "Used to phrase the q14 hardware evidence as a raw-versus-mitigated benchmark with explicit spread rather than a hidden estimator claim."
  forbidden_proxies:
    fp-03-01-proxy:
      status: rejected
      notes: "The note says explicitly that reproducing perturbed_echo behavior is not enough to count as a completed fixed-observable OLE estimator."
  uncertainty_markers:
    weakest_anchors:
      - "An explicit fixed-observable hardware estimator remains unimplemented beyond the current baseline-compatible runner outputs."
    unvalidated_assumptions: []
    competing_explanations: []
    disconfirming_observations: []
comparison_verdicts:
  - subject_id: test-hardware-ready
    subject_kind: acceptance_test
    subject_role: decisive
    reference_id: ref-q14-manifest
    comparison_kind: benchmark
    metric: "manifest lock fidelity"
    threshold: "qubits=14, depths=1,2,3,4, trials=3, seed=424242, shots=4000 remain unchanged in the note"
    verdict: pass
    recommended_action: "Keep later hardware writing pinned to the same q14 manifest values unless a new manifest is explicitly versioned."
    notes: "The mapping note preserves the locked q14 parameter block exactly."
  - subject_id: test-hardware-ready
    subject_kind: acceptance_test
    subject_role: decisive
    reference_id: ref-status
    comparison_kind: benchmark
    metric: "claim-discipline continuity"
    threshold: "baseline-compatible runner outputs are not presented as final OLE estimators"
    verdict: pass
    recommended_action: "Carry the same anti-overclaim sentence into every downstream hardware note and summary."
    notes: "The note blocks silent relabeling and keeps the unresolved-estimator gate explicit."
  - subject_id: test-hardware-ready
    subject_kind: acceptance_test
    subject_role: supporting
    reference_id: ibm-raw-vs-mit
    comparison_kind: experiment
    metric: "admissible checkpoint evidence"
    threshold: "corrected local-fold checkpoint ZNE remains stronger than the earlier mixed whole-grid mitigation result"
    verdict: pass
    recommended_action: "Use corrected local-fold checkpoint ZNE as the admissible q14 hardware anchor and leave PE-LiNN outside the support chain."
    notes: "Depth 2 is cleanest, depth 3 remains noisier, and the note records that boundary instead of overstating closure."
