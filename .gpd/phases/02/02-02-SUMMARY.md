---
phase: "02"
plan: "02"
depth: standard
one-liner: "Phase 2 turned the exact q14 OLE artifact into a decisive delta^2 benchmark report that keeps the overlap/disjoint OLE onset explicit while presenting perturbed_echo only as a labeled state-return baseline."
subsystem:
  - benchmark
  - analysis
  - reporting
tags:
  - operator-loschmidt-echo
  - q14
  - benchmark
  - delta-squared
requires:
  - "files/quantum-math-lab/results/ole/black_hole_ole_q14_exact_small_delta.json"
  - "files/quantum-math-lab/results/benchmark/classical/black_hole_scrambling_q14_exact_short.json"
provides:
  - "Reproducible q14 delta^2 benchmark report for the exact OLE onset"
  - "Machine-readable comparison table aligned to the report labels"
  - "Explicit baseline wording that preserves the gap between OLE and perturbed_echo semantics"
affects:
  - "Phase 2 small-delta validation"
  - "Phase 3 hardware/q80 carry-forward wording"
methods:
  added:
    - "Manifest-checked benchmark report generator"
    - "CSV export spanning both OLE onset points and baseline rows"
    - "Juxtaposed baseline presentation instead of a collapsed same-axis overlay"
  patterns:
    - "Keep the baseline visible while refusing to rename it as OLE"
    - "Treat wide-scale baseline differences as a reporting problem, not as permission to blur observable semantics"
key-files:
  created:
    - "files/quantum-math-lab/analyze_q14_ole_benchmark.py"
    - "files/quantum-math-lab/results/ole/q14_ole_vs_delta2_benchmark.md"
    - "files/quantum-math-lab/results/ole/q14_ole_vs_delta2_benchmark.csv"
  modified: []
key-decisions:
  - "Render the q14 benchmark as a markdown report plus CSV instead of forcing an image workflow."
  - "List perturbed_echo in a separate baseline table rather than squeezing it onto the narrow delta^2 onset axis."
  - "Carry the normalized translation f_delta(O) = 2^-14 F_delta(P) explicitly in the report header and manifest table."
patterns-established:
  - "For mixed-semantics comparisons, juxtaposition is preferable to an over-compressed overlay if it preserves interpretability."
  - "Benchmark reports should export a machine-readable table at the same time as the narrative artifact."
conventions:
  - "benchmark_x_axis = delta^2 for the OLE onset panels"
  - "observable_lock = P = Z_0 with normalized translation O = Z_0 / sqrt(2^14)"
  - "baseline_label = perturbed_echo is a state-return baseline, not OLE"
plan_contract_ref: ".gpd/phases/02/02-02-PLAN.md#/contract"
contract_results:
  claims:
    claim-q14-benchmark-figure:
      status: passed
      summary: "The q14 exact OLE artifact is now packaged as a decisive delta^2 benchmark report with both support variants visible and the existing perturbed_echo baseline kept explicit and separate."
      linked_ids:
        - deliv-q14-benchmark-script
        - deliv-q14-benchmark-figure
        - test-benchmark-artifact
        - test-baseline-label-discipline
        - test-support-variant-visibility
        - ref-exact-ole-data
        - ref-q14-baseline-artifact
        - ref-q14-manifest
        - ref-small-delta-bridge
        - ref-phase2-handoff
      evidence: []
  deliverables:
    deliv-q14-benchmark-script:
      status: passed
      path: "files/quantum-math-lab/analyze_q14_ole_benchmark.py"
      summary: "Analysis script that validates manifest continuity, emits a machine-readable comparison table, and writes a markdown report with explicit OLE and baseline labels."
      linked_ids:
        - claim-q14-benchmark-figure
        - test-benchmark-artifact
    deliv-q14-benchmark-figure:
      status: passed
      path: "files/quantum-math-lab/results/ole/q14_ole_vs_delta2_benchmark.md"
      summary: "Report artifact that presents the q14 overlap/disjoint OLE onset panels on a delta^2 axis and lists perturbed_echo in a separate baseline table."
      linked_ids:
        - claim-q14-benchmark-figure
        - test-benchmark-artifact
        - test-baseline-label-discipline
        - test-support-variant-visibility
  acceptance_tests:
    test-benchmark-artifact:
      status: passed
      summary: "The generated report is manifest-tied, uses delta^2 onset tables, defines P = Z_0 explicitly, and includes the q14 perturbed_echo baseline as a labeled comparison reference."
      linked_ids:
        - claim-q14-benchmark-figure
        - deliv-q14-benchmark-script
        - deliv-q14-benchmark-figure
        - ref-exact-ole-data
        - ref-q14-baseline-artifact
    test-baseline-label-discipline:
      status: passed
      summary: "The report consistently describes perturbed_echo as a state-return baseline and never renames the baseline itself as OLE or as F_delta(Z_0)."
      linked_ids:
        - claim-q14-benchmark-figure
        - deliv-q14-benchmark-figure
        - ref-q14-baseline-artifact
        - ref-small-delta-bridge
    test-support-variant-visibility:
      status: passed
      summary: "Each active depth section contains both overlap G = X_0 and disjoint G = X_10 rows, so the benchmark keeps the signal and the locality control visible together."
      linked_ids:
        - claim-q14-benchmark-figure
        - deliv-q14-benchmark-figure
        - ref-exact-ole-data
  references:
    ref-exact-ole-data:
      status: completed
      completed_actions:
        - read
        - use
      missing_actions: []
      summary: "Used the exact q14 OLE artifact as the source of the overlap/disjoint onset curves and operator-statistics overview."
    ref-q14-baseline-artifact:
      status: completed
      completed_actions:
        - read
        - use
        - compare
      missing_actions: []
      summary: "Used the current q14 exact-short state-return artifact as the explicit baseline table and as the comparison anchor for report wording."
    ref-q14-manifest:
      status: completed
      completed_actions:
        - read
        - use
      missing_actions: []
      summary: "Used the active q14 manifest to keep qubits, depths, trials, seed, and shots visible in the report."
    ref-small-delta-bridge:
      status: completed
      completed_actions:
        - read
        - use
      missing_actions: []
      summary: "Used the Phase 1 bridge to keep F_delta(P), f_delta(O), and the onset interpretation consistent in the report wording."
    ref-phase2-handoff:
      status: completed
      completed_actions:
        - read
        - use
      missing_actions: []
      summary: "Used the handoff note to preserve the branch choices, baseline comparison rules, and guardrail against relabeling."
  forbidden_proxies:
    fp-baseline-renaming:
      status: rejected
      notes: "The report labels perturbed_echo as a state-return baseline and explicitly says it is not the OLE curve."
    fp-axis-collapse:
      status: rejected
      notes: "The baseline is juxtaposed in its own table instead of being forced onto the narrow delta^2 onset axis."
  uncertainty_markers:
    weakest_anchors:
      - "The benchmark report is decisive at the presentation layer, but the actual fit-window stability verdict still belongs to Wave 3."
    unvalidated_assumptions: []
    competing_explanations: []
    disconfirming_observations: []
comparison_verdicts:
  - subject_id: test-benchmark-artifact
    subject_kind: acceptance_test
    subject_role: decisive
    reference_id: ref-exact-ole-data
    comparison_kind: benchmark
    metric: "delta^2 OLE onset visibility"
    threshold: "report uses the exact q14 overlap/disjoint curves directly"
    verdict: pass
    recommended_action: "Use this report as the canonical Phase 2 benchmark artifact in later validation and write-up steps."
    notes: "Each active depth panel is built from the exact q14 OLE JSON without manual editing."
  - subject_id: test-benchmark-artifact
    subject_kind: acceptance_test
    subject_role: decisive
    reference_id: ref-q14-baseline-artifact
    comparison_kind: baseline
    metric: "baseline continuity"
    threshold: "baseline is present, labeled, and kept semantically distinct from OLE"
    verdict: pass
    recommended_action: "Carry the perturbed_echo table forward only as a comparison reference."
    notes: "The report juxtaposes the baseline rather than treating it as a point on the OLE curve."
  - subject_id: test-benchmark-artifact
    subject_kind: acceptance_test
    subject_role: decisive
    reference_id: ref-q14-manifest
    comparison_kind: benchmark
    metric: "manifest continuity"
    threshold: "report matches the active q14 benchmark family"
    verdict: pass
    recommended_action: "Keep all later q14 validation and hardware notes on this same manifest family."
    notes: "The report repeats benchmark_id, qubits, depths, trials, seed, shots, and the delta grid."
  - subject_id: test-baseline-label-discipline
    subject_kind: acceptance_test
    subject_role: supporting
    reference_id: ref-small-delta-bridge
    comparison_kind: cross_method
    metric: "quantity naming discipline"
    threshold: "F_delta(P) and perturbed_echo remain visibly distinct"
    verdict: pass
    recommended_action: "Preserve this naming discipline in Wave 3 and Phase 3."
    notes: "The report header carries both F_delta(P) and f_delta(O) while keeping the baseline wording separate."
  - subject_id: test-baseline-label-discipline
    subject_kind: acceptance_test
    subject_role: decisive
    reference_id: ref-phase2-handoff
    comparison_kind: benchmark
    metric: "comparison-rule continuity"
    threshold: "juxtaposition allowed, relabeling forbidden"
    verdict: pass
    recommended_action: "Retain the separate baseline table unless a future figure can preserve the same clarity."
    notes: "The benchmark artifact follows the handoff note's permission for overlay or juxtaposition and chooses juxtaposition."
  - subject_id: test-support-variant-visibility
    subject_kind: acceptance_test
    subject_role: decisive
    reference_id: ref-exact-ole-data
    comparison_kind: benchmark
    metric: "branch visibility"
    threshold: "both overlap G = X_0 and disjoint G = X_10 rows appear for every active depth"
    verdict: pass
    recommended_action: "Preserve both support variants in all later q14 benchmark summaries and figures."
    notes: "The markdown report shows both branches in every depth panel and the CSV exports both families per depth."
  - subject_id: ref-exact-ole-data
    subject_kind: reference
    subject_role: decisive
    reference_id: ref-exact-ole-data
    comparison_kind: benchmark
    metric: "source-artifact coverage"
    threshold: "the exact q14 OLE artifact is visibly represented in the benchmark report"
    verdict: pass
    recommended_action: "Keep this exact JSON as the sole source of the OLE onset tables."
    notes: "The benchmark report and CSV are generated directly from the exact OLE artifact."
  - subject_id: ref-q14-baseline-artifact
    subject_kind: reference
    subject_role: decisive
    reference_id: ref-q14-baseline-artifact
    comparison_kind: baseline
    metric: "baseline-source coverage"
    threshold: "the existing q14 perturbed_echo artifact appears as a labeled comparison reference"
    verdict: pass
    recommended_action: "Continue to cite this artifact only as a state-return baseline."
    notes: "The report's baseline table and CSV baseline rows come directly from the exact-short q14 baseline artifact."
  - subject_id: ref-q14-manifest
    subject_kind: reference
    subject_role: decisive
    reference_id: ref-q14-manifest
    comparison_kind: benchmark
    metric: "manifest-source coverage"
    threshold: "benchmark report stays tied to the active q14 manifest family"
    verdict: pass
    recommended_action: "Preserve the same benchmark_id and fixed parameters in later q14 artifacts."
    notes: "The report copies benchmark_id, qubits, depths, trials, seed, shots, and the delta grid from the active manifest family."
  - subject_id: ref-phase2-handoff
    subject_kind: reference
    subject_role: decisive
    reference_id: ref-phase2-handoff
    comparison_kind: benchmark
    metric: "handoff-rule coverage"
    threshold: "artifact preserves the allowed juxtaposition and naming guardrails"
    verdict: pass
    recommended_action: "Carry the same comparison-rule guardrails into Wave 3 and Phase 3."
    notes: "The benchmark artifact follows the handoff note by juxtaposing the baseline and preserving explicit branch labels."
duration: "7min"
completed: "2026-03-18"
---

# Phase 2 Plan 02 Summary

**Phase 2 turned the exact q14 OLE artifact into a decisive `delta^2` benchmark report that keeps the overlap/disjoint OLE onset explicit while presenting `perturbed_echo` only as a labeled state-return baseline.**

## Performance

- **Duration:** 7 min
- **Started:** 2026-03-18T07:41:09Z
- **Completed:** 2026-03-18T07:48:18Z
- **Tasks:** 3
- **Files modified:** 3

## Key Results

- The benchmark report now presents the exact q14 OLE onset on a `delta^2` axis for both overlap `G = X_0` and disjoint `G = X_10` branches at every active depth.
- The report keeps `P = Z_0` and `f_delta(O) = 2^-14 F_delta(P)` explicit, so the plotted quantity and its normalized translation stay visible instead of implicit.
- The current q14 `perturbed_echo` artifact is included as a side baseline table and CSV rows, not as an OLE curve or as a collapsed same-axis overlay.

## Task Commits

1. **Task 1: Build the benchmark-report generator** - `e1a84eb`
2. **Task 2: Write the q14 delta^2 benchmark report** - `e1a84eb`
3. **Task 3: Emit a reproducible comparison table** - `e1a84eb`

## Files Created/Modified

- `files/quantum-math-lab/analyze_q14_ole_benchmark.py` - reproducible generator for the q14 benchmark markdown and CSV artifacts
- `files/quantum-math-lab/results/ole/q14_ole_vs_delta2_benchmark.md` - report artifact with manifest table, baseline table, and depth-by-depth onset panels
- `files/quantum-math-lab/results/ole/q14_ole_vs_delta2_benchmark.csv` - machine-readable benchmark table with 4 baseline rows and 80 OLE rows

## Next Phase Readiness

Wave 3 can now validate shrinking fit windows directly from a stable benchmark artifact rather than recomputing or reformatting the q14 OLE curves.

## Contract Coverage

- Claim IDs advanced: `claim-q14-benchmark-figure -> passed`
- Deliverable IDs produced: `deliv-q14-benchmark-script`, `deliv-q14-benchmark-figure`
- Acceptance test IDs run: `test-benchmark-artifact`, `test-baseline-label-discipline`, `test-support-variant-visibility`
- Reference IDs surfaced: `ref-exact-ole-data`, `ref-q14-baseline-artifact`, `ref-q14-manifest`, `ref-small-delta-bridge`, `ref-phase2-handoff`
- Forbidden proxies rejected or violated: `fp-baseline-renaming -> rejected`, `fp-axis-collapse -> rejected`
- Decisive comparison verdicts: `test-benchmark-artifact -> pass`

## Equations Derived

**Eq. (02.4):**

$$
x = \delta^2
$$

**Eq. (02.5):**

$$
f_\delta(O) = 2^{-14} F_\delta(P), \qquad O = \frac{Z_0}{\sqrt{2^{14}}}
$$

**Eq. (02.6):**

$$
\texttt{perturbed\_echo}
\neq
F_\delta(Z_0)
$$

## Validations Completed

- Checked that the report contains a `delta^2` axis, explicit `P = Z_0`, explicit `f_delta(O)` translation, and the required `perturbed_echo` wording.
- Checked that the CSV contains `4` baseline rows plus `80` OLE rows, with both overlap and disjoint branches present at every depth.
- Checked that the report keeps the baseline in a separate table rather than collapsing it onto the onset axis.

## Decisions & Deviations

The only substantive presentation choice was to generate a markdown report and a CSV table instead of forcing a graphical same-axis overlay. That is not a deviation from the plan; the plan explicitly allowed juxtaposition, and the baseline/state-return semantics are clearer in this layout than they would be on a compressed onset plot.

## Open Questions

- Wave 3 still needs to decide which fit windows are accepted for the overlap branch once intercept and slope stability are checked explicitly.
- The benchmark artifact is now fixed, but the hardware-ready estimator and the q80 subset/full carry-forward rules still belong to the next wave.
