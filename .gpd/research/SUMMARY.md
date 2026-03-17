# Research Summary

**Project:** Operator Loschmidt Echo extension of the q14/q80 scrambling benchmark workflow
**Domain:** quantum information scrambling / benchmarked quantum-circuit echoes
**Researched:** 2026-03-17
**Confidence:** MEDIUM

## Executive Summary

This project is not starting from scratch. The repo already has a narrowly defended q14 exact-short `perturbed_echo` benchmark, hardware-ready execution scripts, and explicit q80 subset-observable evidence. The literature supports a careful bridge from that workflow to fixed-observable OLE, but it does not justify skipping the bridge itself: the first decisive deliverable still has to be an explicit q14 small-`delta` `f_delta(O)` versus `delta^2` benchmark with a frozen observable and perturbation generator.

The research landscape suggests two viable methodological paths. The closest path to the current repo is an echo-style, backward-evolution-compatible route informed by the Loschmidt-echo/OTOC bridge and anti-butterfly benchmarking logic. The strongest alternative, if reversal becomes too fragile on hardware, is randomized-measurement OTOC estimation, which is experimentally established and avoids time reversal. The main risk is interpretive rather than computational: decays can be faked by noise, subset observables can be overstated as full-system evidence, and the project can accidentally relabel `perturbed_echo` rather than implementing OLE.

## Key Findings

### Computational Approaches

The recommended core approach is to reuse the existing Qiskit workflow and add the smallest possible OLE layer. Exact q14 evaluation is already the natural first benchmark regime because the manifest, baseline artifacts, and task definition are frozen there. Large-system work should remain subset-observable and hardware-oriented; full 80q global OLE is not computationally credible in the current snapshot.

**Core approach:**

- Fixed-observable OLE with explicit `O`, `G`, and `delta` -- required to make the bridge real rather than semantic.
- Exact q14 reference plus `delta^2` onset fit -- first success gate and strongest validation anchor.
- Existing hardware runner with subset observables and mitigation -- immediate route for hardware readiness and q80 continuity.

### Prior Work Landscape

The prior-work picture is favorable but disciplined. Yan, Cincio, and Zurek provide the conceptual LE/OTOC bridge. Vermersch et al. and Joshi et al. show that practical scrambling diagnostics can be measured on hardware without ideal time reversal. Harris, Yan, and Sinitsyn show why decay alone is not enough and why a benchmark/control mentality matters. Zanardi supplies a fixed-observable/subalgebra language that helps justify subset observables when they are stated honestly.

**Must reproduce (benchmarks):**

- q14 small-`delta` quadratic OLE onset with an explicit fixed observable.
- locality-sensitive distinction between overlap and disjoint support, at least in exact or subset-controlled form.

**Novel contributions (for this project):**

- clean bridge from the repo's current `perturbed_echo` campaign to fixed-observable OLE without changing the task family.
- hardware-ready OLE framing that keeps q80 subset and possible full-q80 directions distinct.

**Defer (future work):**

- any claim about full 80q global OLE or full-system fidelity.
- heavier verification protocols such as teleportation-based scrambling tests.

### Methods and Tools

The best immediate method is exact q14 OLE evaluation inside the current `qiskit_black_hole_scrambling.py` pipeline, followed by a hardware mapping in the existing runner. Randomized-measurement OTOC methods should remain available as a fallback if the echo-style hardware route becomes operationally weak. The practical software stack is already present in the artifacts: Qiskit `1.4.5`, `qiskit_ibm_runtime` `0.40.0`, `qiskit_aer` `0.17.0`, and the current manifest-driven benchmark scripts.

**Major components:**

1. Fixed-observable formalism lock -- freeze `O`, `G`, normalization, and picture conventions.
2. Exact q14 benchmark implementation -- generate `f_delta(O)` and compare it to the active baseline.
3. Hardware/subset mapping -- preserve the existing q80 runner semantics and claim discipline.

### Critical Pitfalls

1. **Relabeling `perturbed_echo` as OLE** -- avoid by requiring explicit `O`, `G`, `delta`, and separate artifact labels.
2. **Reading noise-induced decay as scrambling** -- avoid by carrying locality controls and recovery-style benchmark logic.
3. **Overclaiming q80 subset evidence** -- avoid by keeping subset support explicit in every artifact and summary.
4. **Leaving the small-`delta` regime unnoticed** -- avoid by fit-window stability checks before claiming quadratic agreement.

## Implications for Research Plan

Based on the survey, suggested phase structure:

### Phase 1: Formal OLE Bridge

**Rationale:** The first failure mode is semantic drift, so the project must freeze the exact observable definition before any new benchmark is run.
**Delivers:** fixed `O`, `G`, normalization, picture conventions, and task-definition updates tied to the existing q14 manifest.
**Validates:** that OLE is distinct from the current `perturbed_echo` output.
**Avoids:** the "renaming as progress" pitfall.

### Phase 2: q14 Exact Benchmark

**Rationale:** The first decisive evidence should stay where exact references already exist.
**Delivers:** q14 `f_delta(O)` versus `delta^2`, small-`delta` coefficient checks, and overlay with the active `perturbed_echo` baseline.
**Uses:** exact statevector evaluation, manifest-frozen depths, and support-variant controls.
**Builds on:** Phase 1 conventions and task definition.

### Phase 3: Hardware-Ready Mapping and q80 Subset Extension

**Rationale:** Hardware readiness matters to the user, but it should follow only after the q14 bridge is exact and explicit.
**Delivers:** hardware-ready protocol for the same observable semantics, q80 subset feasibility path, and locality-control guidance.
**Uses:** current hardware runner, subset mitigation, and existing q80 evidence conventions.
**Builds on:** Phase 2 benchmark semantics.

### Phase 4: Full-q80 Proxy Assessment

**Rationale:** The full-q80 question should remain visible without infecting earlier claims.
**Delivers:** decision on whether a meaningful full-q80 proxy exists or whether the project remains subset-observable at large size.

### Phase Ordering Rationale

- The ordering follows dependency reality: definitions first, exact benchmark second, hardware translation third.
- This grouping keeps the project centered on the current q14/q80 repo rather than drifting into a separate OTOC platform.
- The plan explicitly blocks the main pitfalls: semantic relabeling, noise-overinterpretation, and q80 overclaiming.

### Phases Requiring Deep Investigation

- **Phase 1:** the observable-picture choice and exact definition of the first fixed `O` need careful locking because the literature mixes conventions.
- **Phase 3:** hardware OLE design may need extra exploration if the mirror-circuit route is less stable than expected.
- **Phase 4:** any full-q80 proxy is still speculative and should be treated as a genuine research question.

Phases with established methodology:

- **Phase 2:** exact q14 benchmarking is the most straightforward step because the repo already supports the same task family and exact references.

## Confidence Assessment

| Area | Confidence | Notes |
| ---- | ---------- | ----- |
| Computational Approaches | HIGH | grounded in the current repo and existing artifacts |
| Prior Work | HIGH | anchored in primary papers plus current local evidence |
| Methods | MEDIUM | the bridge to fixed-observable OLE is partly an inference from literature plus repo architecture |
| Pitfalls | HIGH | both literature and current repo state make the main failure modes clear |

**Overall confidence:** MEDIUM

### Gaps to Address

- first fixed-observable choice for the q14 benchmark still needs to be frozen explicitly.
- the preferred hardware route is not fully decided between a direct echo-style OLE mapping and a randomized-measurement fallback.
- full-q80 OLE remains an open feasibility question, not a promised outcome.

## Sources

### Primary (HIGH)

- Yan, Cincio, Zurek (`1903.02651v4`) -- LE/OTOC equivalence.
- Vermersch et al. (`1807.09087v2`) -- randomized-measurement OTOC protocol.
- Joshi et al. (`2001.02176v2`) -- hardware scrambling experiment.
- Harris, Yan, Sinitsyn (`2110.12355v2`) -- anti-butterfly benchmark logic.
- Zanardi (`2107.01102v3`) -- observable-algebra scrambling framework.
- Kastner, Osterholz, Gross (`2403.08670v1`) -- ancilla-free backward-evolution protocol.

### Secondary (MEDIUM)

- Algorithmiq OLE theory note -- fixed-observable OLE formula and small-`delta` benchmark target.
- `STATUS.md`, `q14_only_manifest.json`, `levelb_evidence_report.md`, `hardware_advantage_protocol.md` -- project-specific computational and claim constraints.

### Tertiary (LOW)

- none relied upon for key claims in this survey.

---

_Research analysis completed: 2026-03-17_
_Ready for research plan: yes_
