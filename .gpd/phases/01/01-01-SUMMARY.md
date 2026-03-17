---
phase: "01"
plan: "01"
depth: standard
one-liner: "Phase 1 froze the first q14 OLE benchmark as P = Z_0 with overlap G = X_0, disjoint control G = X_10, and a unit-intercept report-level curve F_delta(P) with explicit normalized-operator translation."
subsystem:
  - formalism
  - derivation
tags:
  - operator-loschmidt-echo
  - pauli-observable
  - q14
  - conventions
requires: []
provides:
  - "Explicit q14 observable/generator/support lock for the first OLE benchmark"
  - "Resolved intercept convention: plot F_delta(P) with f_delta(O)=2^-n F_delta(P) as the normalized translation"
  - "Repo-facing wording that keeps perturbed_echo as a baseline only"
affects:
  - "Phase 2 q14 exact benchmark"
  - "Phase 3 hardware mapping"
methods:
  added:
    - "Pauli-specialized OLE formalism lock"
    - "Explicit unit-intercept versus Hilbert-Schmidt-normalized translation"
  patterns:
    - "Freeze benchmark observable and generator before any delta sweep"
    - "Surface contract anchors directly in the formalism artifact"
key-files:
  created:
    - ".gpd/phases/01/ole_formalism_lock.md"
  modified:
    - ".gpd/CONVENTIONS.md"
    - ".gpd/PROJECT.md"
    - ".gpd/STATE.md"
    - ".gpd/state.json"
    - "files/quantum-math-lab/README.md"
key-decisions:
  - "Use P = Z_0 as the first q14 fixed observable."
  - "Use G = X_0 for the overlap benchmark and G = X_10 for the disjoint control."
  - "Report the first benchmark as F_delta(P) with F_0 = 1, while keeping f_delta(O) = 2^-n F_delta(P) available for normalized notation."
patterns-established:
  - "For circuit-model phases, fill the canonical convention lock explicitly even when many continuum fields are bookkeeping-only."
  - "Resolve normalization/intercept ambiguity before writing any delta^2 benchmark plan."
conventions:
  - "natural_units = natural"
  - "metric_signature = euclidean"
  - "coordinate_system = Qiskit qubit index ordering 0..n-1"
  - "spin_basis = computational basis with Pauli operators X,Y,Z in the standard qubit basis"
  - "commutation_convention = [A,B]=AB-BA with [X,Z]=-2iY and [Z,X]=2iY"
  - "generator_normalization = single-qubit Pauli generators square to identity"
plan_contract_ref: ".gpd/phases/01/01-01-PLAN.md#/contract"
contract_results:
  claims:
    claim-q14-ole-bridge:
      status: passed
      summary: "The first q14 OLE bridge is now anchored to P = Z_0, overlap G = X_0, disjoint control G = X_10, and an explicit report-level intercept convention."
      linked_ids:
        - deliv-formalism-lock-note
        - deliv-convention-ledger-update
        - test-formalism-lock
        - test-normalization-intercept
        - ref-algorithmiq-ole
        - ref-status
        - ref-q14-manifest
        - ref-scrambling-script
      evidence: []
  deliverables:
    deliv-formalism-lock-note:
      status: passed
      path: ".gpd/phases/01/ole_formalism_lock.md"
      summary: "Formal note created and anchored to the q14 manifest, baseline script, and OLE theory note."
      linked_ids:
        - claim-q14-ole-bridge
        - test-formalism-lock
        - test-normalization-intercept
    deliv-convention-ledger-update:
      status: passed
      path: ".gpd/CONVENTIONS.md"
      summary: "Convention ledger now records the benchmark observable/generator lock, the report-level OLE quantity, and the completed bookkeeping convention lock."
      linked_ids:
        - claim-q14-ole-bridge
        - test-normalization-intercept
  acceptance_tests:
    test-formalism-lock:
      status: passed
      summary: "The formalism note names P = Z_0, overlap G = X_0, disjoint G = X_10, and support labels consistent with q14 qubit indices and the existing X-kick machinery."
      linked_ids:
        - claim-q14-ole-bridge
        - deliv-formalism-lock-note
        - ref-q14-manifest
        - ref-scrambling-script
    test-normalization-intercept:
      status: passed
      summary: "The deliverables now state both F_0(P) = 1 and f_0(O) = 2^-n, plus the exact translation f_delta(O) = 2^-n F_delta(P)."
      linked_ids:
        - claim-q14-ole-bridge
        - deliv-formalism-lock-note
        - deliv-convention-ledger-update
        - ref-algorithmiq-ole
  references:
    ref-algorithmiq-ole:
      status: completed
      completed_actions:
        - read
        - compare
        - cite
      missing_actions: []
      summary: "Surfaced in the formalism note as the definition and small-delta interpretation anchor."
    ref-status:
      status: completed
      completed_actions:
        - read
        - use
        - avoid
      missing_actions: []
      summary: "Used to preserve the q14-only claim boundary and prevent relabeling the current baseline as OLE."
    ref-q14-manifest:
      status: completed
      completed_actions:
        - read
        - use
        - compare
      missing_actions: []
      summary: "Used to freeze q14 qubit labels and benchmark continuity."
    ref-scrambling-script:
      status: completed
      completed_actions:
        - read
        - compare
      missing_actions: []
      summary: "Used to align the OLE bridge with the repo's existing local X-kick semantics."
  forbidden_proxies:
    fp-rename-baseline:
      status: rejected
      notes: "The new note and project wording explicitly distinguish perturbed_echo from the fixed-observable operator correlator."
    fp-unfixed-intercept:
      status: rejected
      notes: "The report-level benchmark quantity and the normalized translation are both fixed in writing before Phase 2."
  uncertainty_markers:
    weakest_anchors:
      - "The hardware-ready measurement route is still only carried forward at the scope level; Phase 3 will still need to finalize protocol details."
    unvalidated_assumptions:
      - "Nonzero scrambling-depth overlap and disjoint coefficients are not yet benchmarked numerically; only the formalism and depth-0 controls are fixed here."
    competing_explanations:
      - "A later q14 curve could still look good while being only a dressed-up proxy unless Phase 2 follows the frozen F_delta(P) definition exactly."
    disconfirming_observations:
      - "If Phase 2 cannot evaluate or plot F_delta(P) without redefining the observable or normalization, the present formalism lock would be insufficient."
comparison_verdicts:
  - subject_id: claim-q14-ole-bridge
    subject_kind: claim
    subject_role: decisive
    reference_id: ref-algorithmiq-ole
    comparison_kind: prior_work
    metric: "definition alignment"
    threshold: "explicit fixed observable, generator, and small-delta role must match the OLE framing"
    verdict: pass
    recommended_action: "Carry the same F_delta(P) definition into Phase 2."
    notes: "The formalism lock keeps the operator-correlator definition and the small-delta interpretation explicit."
  - subject_id: claim-q14-ole-bridge
    subject_kind: claim
    subject_role: decisive
    reference_id: ref-q14-manifest
    comparison_kind: benchmark
    metric: "task-family alignment"
    threshold: "same q14 benchmark family and qubit-label range preserved"
    verdict: pass
    recommended_action: "Use the active q14 manifest unchanged for the first delta sweep."
    notes: "The lock uses q14 qubits 0..13 and preserves the exact-short campaign scope."
  - subject_id: claim-q14-ole-bridge
    subject_kind: claim
    subject_role: decisive
    reference_id: ref-scrambling-script
    comparison_kind: baseline
    metric: "generator-family alignment"
    threshold: "reuse the repo's local X-kick semantics without relabeling the baseline observable"
    verdict: pass
    recommended_action: "Keep the baseline overlay separate from the fixed-observable OLE quantity."
    notes: "The overlap and disjoint generators stay in the same local Pauli-X family as the existing script."
duration: "34min"
completed: "2026-03-17"
---

# Phase 1 Plan 01 Summary

**Phase 1 froze the first q14 OLE benchmark as `P = Z_0` with overlap `G = X_0`, disjoint control `G = X_10`, and a unit-intercept report-level curve `F_delta(P)` with explicit normalized translation.**

## Performance

- **Duration:** 34 min
- **Started:** 2026-03-17T20:48:00Z
- **Completed:** 2026-03-17T21:22:09Z
- **Tasks:** 3
- **Files modified:** 5

## Key Results

- The first q14 fixed observable is now locked to `P = Z_0`, with normalized translation `O = Z_0 / sqrt(2^14)`.
- The first generator pair is locked to overlap `G = X_0` and disjoint control `G = X_10`.
- The benchmark will plot `F_delta(P)` with `F_0(P) = 1`, while `f_delta(O) = 2^-14 F_delta(P)` remains available for normalized notation.

## Task Commits

1. **Task 1: Freeze the default observable and generator supports** - `99c8d3b`, refined by `7014205`
2. **Task 2: Resolve normalization and intercept semantics** - `6ace8cf`
3. **Task 3: Propagate the baseline-versus-OLE guardrail into repo docs** - `bb8413f`

## Files Created/Modified

- `.gpd/phases/01/ole_formalism_lock.md` - formal q14 observable/generator/support lock
- `.gpd/CONVENTIONS.md` - report-level OLE convention and completed bookkeeping lock
- `.gpd/PROJECT.md` - project-facing Phase 1 default lock wording
- `.gpd/STATE.md` - synchronized convention-lock summary
- `.gpd/state.json` - canonical convention lock completion
- `files/quantum-math-lab/README.md` - bridge wording for the black-hole scrambling path

## Next Phase Readiness

Phase 2 can now write the small-`delta` bridge and benchmark handoff without reopening the observable choice, generator choice, or intercept convention.

## Contract Coverage

- Claim IDs advanced: `claim-q14-ole-bridge -> passed`
- Deliverable IDs produced: `deliv-formalism-lock-note`, `deliv-convention-ledger-update`
- Acceptance test IDs run: `test-formalism-lock`, `test-normalization-intercept`
- Reference IDs surfaced: `ref-algorithmiq-ole`, `ref-status`, `ref-q14-manifest`, `ref-scrambling-script`
- Forbidden proxies rejected or violated: `fp-rename-baseline -> rejected`, `fp-unfixed-intercept -> rejected`

## Equations Derived

**Eq. (01.1):**

$$
F_\delta(P) = 2^{-n}\operatorname{Tr}\!\left(U P U^\dagger V_\delta^\dagger U P U^\dagger V_\delta\right)
$$

**Eq. (01.2):**

$$
f_\delta(O) = 2^{-n} F_\delta(P), \qquad O = \frac{P}{\sqrt{2^n}}
$$

**Eq. (01.3):**

$$
[X_0, Z_0] = -2 i Y_0, \qquad [X_{10}, Z_0] = 0
$$

## Validations Completed

- Checked q14 support labels against the manifest: qubit labels `0..13` make `Z_0`, `X_0`, and `X_10` all well-defined.
- Checked the report-level intercept: `F_0(P) = 1` for Pauli `P`, while `f_0(O) = 2^-n` for `O = P / sqrt(2^n)`.
- Checked the depth-0 locality controls: overlap is nontrivial and disjoint is exactly commuting before scrambling spreads support.

## Decisions & Deviations

The only substantive decision was to treat `F_delta(P)` as the plotted q14 benchmark quantity and to keep `f_delta(O)` as the explicit normalized translation. No deviation from the plan's intended formalism lock occurred.

## Open Questions

- Whether Phase 3 should keep the explicit `F_delta(P)` notation or introduce `PLE` as a lighter label for the Pauli-specialized branch.

```yaml
gpd_return:
  status: completed
  files_written:
    - ".gpd/phases/01/ole_formalism_lock.md"
    - ".gpd/CONVENTIONS.md"
    - ".gpd/PROJECT.md"
    - "files/quantum-math-lab/README.md"
    - ".gpd/phases/01/01-01-SUMMARY.md"
  issues: []
  next_actions:
    - "$gpd-execute-phase 1"
  phase: "01"
  plan: "01"
  tasks_completed: 3
  tasks_total: 3
  duration_seconds: 2040
  conventions_used:
    units: "natural"
    metric: "euclidean"
    coordinates: "Qiskit qubit index ordering 0..n-1"
```
