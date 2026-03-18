# Requirements: Operator Loschmidt Echo Extension of q14/q80 Scrambling Benchmarks

**Defined:** 2026-03-17
**Core Research Question:** Can the existing q14/q80 `perturbed_echo` pipeline be turned into a fixed-observable OLE workflow that yields a decisive q14 small-`delta` benchmark and a credible hardware-ready path without overclaiming the meaning of q80 subset observables?

## Primary Requirements

### Formalism

- [ ] **FORM-01**: Freeze the first q14 fixed observable `O`, perturbation generator `G`, support placement, normalization `Tr(O^2)=1`, and operator-picture convention in a way that is compatible with the current echo-circuit workflow.
- [ ] **FORM-02**: Derive the project-specific small-`delta` OLE expression for the chosen convention and state explicitly how it differs from the existing `perturbed_echo` observable while remaining comparable on the same q14 task family.

### Numerical Benchmarks

- [ ] **NUMR-01**: Implement exact q14 fixed-observable OLE evaluation on the active exact-short manifest over a controlled small-`delta` sweep.
- [ ] **NUMR-02**: Produce the decisive q14 benchmark artifact: `F_delta(P)` versus `delta^2`, with explicit normalized translation `f_delta(O) = 2^-14 F_delta(P)`, overlaid or juxtaposed with the current q14 `perturbed_echo` baseline and labeled with the explicit observable definition.
- [ ] **NUMR-03**: Evaluate both overlap-support and disjoint-support variants for the first q14 benchmark so the locality sensitivity of the fixed-observable construction is visible.

### Hardware Translation

- [ ] **PROT-01**: Specify a hardware-ready fixed-observable measurement protocol that maps the q14 OLE benchmark onto the existing `qiskit_black_hole_hardware_runner.py` path without relabeling current outputs as OLE.
- [ ] **PROT-02**: Define the immediate q80 extension as subset-observable OLE-compatible measurements using fixed subsets, explicit support labels, and locality controls consistent with the current Level-B evidence trail.

### Validation and Scope Guards

- [ ] **VALD-01**: Demonstrate that the q14 OLE onset is genuinely in the small-`delta` regime by checking fit-window stability, intercept behavior, and observable normalization in the exact regime.
- [ ] **VALD-02**: Preserve scope discipline by documenting why classical-only curves, proxy-only `perturbed_echo` reuse, and q80 subset-to-global overclaims do not satisfy the approved project contract.

## Follow-up Requirements

### Extensions

- **EXTD-01**: Assess whether a randomized-measurement OTOC implementation should be added as a hardware fallback if the echo-style OLE route proves too fragile.
- **EXTD-02**: Determine whether a meaningful full-q80 proxy exists or whether the project should remain explicitly subset-observable at large size.
- **EXTD-03**: Decide whether explicit PLE terminology clarifies the Pauli-specialized branch after the first OLE benchmark is established.

## Out of Scope

| Topic | Reason |
| ----- | ------ |
| Restoring the legacy full Level-C two-size claim during initialization | The approved contract explicitly keeps the project centered on the narrow q14/q80 bridge rather than reopening the blocked q12/q14 runtime narrative |
| Presenting q80 subset observables as full-system global OLE | The current evidence and contract both forbid this overclaim |
| Fresh observable-family search | The user explicitly asked for fixed observables first |
| Teleportation-based or other ancilla-heavy scrambling verification as the first deliverable | Useful literature context, but too heavy for the initial q14 benchmark gate |

## Accuracy and Validation Criteria

| Requirement | Accuracy Target | Validation Method |
| ----------- | --------------- | ----------------- |
| FORM-01 | unambiguous observable and convention definition | cross-check against `PROJECT.md`, the approved contract, and the future conventions ledger |
| FORM-02 | exact symbolic consistency with the chosen operator picture | compare derived expression with the Algorithmiq small-`delta` formula and note any picture translation explicitly |
| NUMR-01 | exact q14 evaluation over a stable small-`delta` window | reproduce results in the exact regime using the active q14 manifest |
| NUMR-02 | benchmark artifact complete and readable | confirm explicit `delta^2` axis, baseline overlay, and fixed-observable labels |
| NUMR-03 | support-variant comparison is interpretable | require at least one overlap-support and one disjoint-support control in the exact regime |
| PROT-01 | protocol matches benchmark semantics | compare hardware-note steps against the exact q14 observable definition and existing runner interfaces |
| PROT-02 | subset extension preserves locality meaning | compare planned subset route against `levelb_evidence_report.md` controls and subset labeling rules |
| VALD-01 | small-`delta` coefficient stable under shrinking fit windows | fit-window stability and intercept checks in the exact q14 regime |
| VALD-02 | no forbidden proxy passes as success | review artifacts against the approved contract's forbidden proxies and stop/rethink conditions |

## Contract Coverage

| Requirement | Decisive Output / Deliverable | Anchor / Benchmark / Reference | Prior Inputs / Baselines | False Progress To Reject |
| ----------- | ----------------------------- | ------------------------------ | ------------------------ | ------------------------ |
| FORM-01 | q14 OLE benchmark setup | Algorithmiq OLE note; `STATUS.md` | current q14/q80 workflow definitions | vague "OLE-like" wording with no explicit `O` or `G` |
| FORM-02 | formal bridge note for q14 OLE | Algorithmiq OLE note; `1903.02651v4` | current `perturbed_echo` semantics | claiming equivalence by name instead of derivation |
| NUMR-01 | exact q14 OLE data | `q14_only_manifest.json` | q14 exact-short campaign settings | classical-only construction detached from the active task family |
| NUMR-02 | `deliv-q14-benchmark-figure` | `q14_only_manifest.json`; `STATUS.md` | current q14 `perturbed_echo` baseline | one clean curve without baseline overlay or explicit observable labels |
| NUMR-03 | locality-sensitive q14 comparison | `levelb_evidence_report.md`; randomized-measurement literature | existing overlap/disjoint q80 intuition | single-support result treated as decisive |
| PROT-01 | `deliv-hardware-ready-note` | Algorithmiq OLE note; `hardware_advantage_protocol.md` | existing hardware runner architecture | hardware story that is only a rename of current outputs |
| PROT-02 | q80 subset extension plan | `levelb_evidence_report.md`; `STATUS.md` | current q80 subset/locality evidence | subset route described as if it already solves full-q80 OLE |
| VALD-01 | q14 small-`delta` validation note | Algorithmiq OLE note | exact q14 regime | using too-large `delta` values and still claiming quadratic theory agreement |
| VALD-02 | scope-defense language across artifacts | approved project contract; `STATUS.md` | current claim discipline | polished summaries that hide proxy reuse or q80 overclaiming |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
| ----------- | ----- | ------ |
| FORM-01 | Phase 1: Formal OLE Bridge | Pending |
| FORM-02 | Phase 1: Formal OLE Bridge | Pending |
| NUMR-01 | Phase 2: q14 Exact Benchmark | Pending |
| NUMR-02 | Phase 2: q14 Exact Benchmark | Pending |
| NUMR-03 | Phase 2: q14 Exact Benchmark | Pending |
| PROT-01 | Phase 3: Hardware Mapping and q80 Scope | Pending |
| PROT-02 | Phase 3: Hardware Mapping and q80 Scope | Pending |
| VALD-01 | Phase 2: q14 Exact Benchmark | Pending |
| VALD-02 | Phase 3: Hardware Mapping and q80 Scope | Pending |

**Coverage:**

- Primary requirements: 9 total
- Mapped to phases: 9
- Unmapped: 0

---

_Requirements defined: 2026-03-17_
_Last updated: 2026-03-17 after roadmap drafting_
