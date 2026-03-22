# Phase 3: Hardware Mapping and q80 Scope - Research

**Researched:** 2026-03-18
**Domain:** quantum information scrambling, fixed-observable operator Loschmidt echo, circuit benchmarking
**Confidence:** MEDIUM

## User Constraints

No phase-local `03-CONTEXT.md` exists yet, so constraints are inherited from `ROADMAP.md`, `PROJECT.md`, `.gpd/STATE.md`, and the active artifact chain (`q14-only` bridge + subset/q80 evidence).

### Locked decisions (must preserve)

- Stay centered on the existing `q14/q80` flow; do not branch to a new OLE project.
- Keep both classical and hardware-ready continuations in scope.
- Use fixed-observable OLE first; do not re-scope to an observable-family search.
- Do not relabel `perturbed_echo` as OLE. It is the same-family state-return baseline only.
- Report the q14 fixed-observable benchmark as `F_delta(P)` and always carry `f_delta(O) = 2^-14 F_delta(P)` with `O = Z_0/sqrt(2^14)`.
- Keep `perturbed_qubit=0` overlap and `perturb_qubit=10` disjoint control as the default immediate control pair.
- Keep q80 extension explicitly subset-scoped; full-q80 global OLE remains unresolved and must stay visible as a forward question.
- Use the active manifest values from `files/quantum-math-lab/benchmarks/q14_only_manifest.json` (14q, depths 1-4, trials=3, seed=424242) for Phase 3 handoff compatibility.

### Agent-discretion areas (PLAN to choose)

- Whether phase 3 hardware planning starts with a pure documentation-first mapping note or adds a thin `qiskit_black_hole_ole_hardware.py` implementation at once.
- Whether randomized-measurement OTOC is kept as hard fallback or implemented as a parity benchmark in parallel to direct circuit-family mapping.
- Exact choice of local subset sizes / exact subset labels to carry in q80 scope note (`subset-qubits` ranges, number of fixed sets).

### Deferred ideas (out of scope for this phase)

- Restoring full Level-C legacy claim in this phase.
- Declaring any q80 subset signal as a full global OLE proxy.
- Broad OLE observable-family search beyond the fixed q14 first bridge.

## Active Anchor References

| Anchor / Artifact | Type | Why It Matters Here | Required Action | Where It Must Reappear |
| ----------------- | ---- | ------------------- | --------------- | ---------------------- |
| `ref-algorithmiq-ole` | contract | fixes fixed-observable OLE definition and small-delta bridge | read, enforce in notation | Mathematical framework, methods, validation |
| `ref-status` | contract | constrains claim language and scope | enforce wording and milestone boundaries | Summary, validation, q80 scope |
| `ref-levelb-evidence` | evidence | gives prior q80 locality/subset support structure | carry forward support labels and locality checks | q80 scope note, pitfalls, validation |
| `files/quantum-math-lab/benchmarks/q14_only_manifest.json` | manifest | defines frozen depth/trials/seed/task family | preserve exactly in phase-3 hardware and analysis runs | Commands, mapping note, checks |
| `files/quantum-math-lab/results/hardware/summary/levelb_evidence_report.md` | evidence | records q80 subset interpretation and limitations | reuse unresolved/full language and local controls | Validation, caveats, open questions |
| `files/quantum-math-lab/results/hardware/summary/ibm_runs_raw_vs_mitigated_summary.md` | evidence | quantifies mitigation utility/limitations | reuse raw-vs-mitigated discipline in phase-3 evidence | Computational plan, validation |

## Summary

Phase 3 is primarily an execution-discipline phase, not a new physics-derivation phase. The core methods are already set in phase 1/2: fixed observable, fixed generator support, and small-delta perturbation theory. The new demand is to preserve that contract while re-using the existing hardware path and making explicit what is and is not being measured at large scale.

**Primary recommendation:** plan phase 3 around one canonical mapping pattern: (i) keep the exact q14 fixed-observable OLE definition and dataset as the non-negotiable target, (ii) add a hardware-ready note and matching-run discipline that preserves circuit-family continuity (`U` family, seeds, depths), and (iii) define q80 scope as labeled subset-observable work with overlap/disjoint locality controls and explicit “no full-q80 claim” guards.

## Mathematical Framework and Physical Principles

### Fixed-observable OLE definitions to preserve for planning

Use the contract-consistent AP-picture:

```text
A_P(U) = U P U^dagger
F_delta(P; U, X_q) = 2^-n Tr(A_P V_delta^dagger A_P V_delta)
V_delta = exp(-i delta X_q)
f_delta(O) = 2^-n F_delta(P), with O = P / sqrt(2^n)
```

Interpretation rules:

- `perturbed_echo` is a state-return quantity `|<0...0| U^dagger X_q U |0...0>|^2` and stays a same-family baseline.
- OLE is an operator-space correlator and is only meaningful if `P` and `V_delta` are explicit and fixed.
- For this phase, keep overlap and disjoint branches explicit:
  - overlap: `q=0`, controls commutator sensitivity
  - disjoint: `q=10`, acts as locality control

### Small-delta physics that must be kept in the planner

For local-kick branch from phase 2, exact sparse-Pauli derivations in this repo use

```text
F_delta(P) = 1 - (delta^2 / 2) kappa + O(delta^4)
kappa = 4 w_anti(q)
```
where `w_anti(q)` is the squared Pauli-weight on support that anticommutes with local generator `X_q`.

Planner-level rule of thumb:
- Treat `delta <= 0.10` as the default quoted onset window.
- Use `delta <= 0.20` only as broader diagnostic sweep; require shrink-window stability before claiming onset constants.

### Dimensional and scaling checks

- All observables are dimensionless probabilities/overlaps.
- The only dimensional scale for execution planning is circuit depth and system size (14 vs 80).
- Runtime contracts use `IBM quantum_seconds` for reproducibility with the active `q14_only` campaign.

## Exact Known Results and Hard Limits for Phase 3 Planning

### What already exists and should not be reopened

- Fixed-observable q14 OLE exact evaluator already exists and was used: `files/quantum-math-lab/qiskit_black_hole_ole_exact.py`.
- Exact-to-baseline analyzer exists: `files/quantum-math-lab/analyze_q14_ole_benchmark.py`.
- q14 exact-small-delta benchmark artifacts exist with overlap and disjoint branches, and were validated against manifest.
- Hardware runner already supports:
  - `--subset-qubits`
  - readout mitigation subset
  - exact vs hardware mode (`--skip-exact`)
  - raw vs mitigated statistics
  - reproducible metadata collection (`output-json`, backend usage)
- q80 evidence currently exists as subset-locality evidence, not global overlap OLE evidence.

### Mandatory interpretation constraints for q80

- Global 80q state-overlap observables lose contrast and are not scalable under current mitigation structure.
- Existing q80 path is subset-observable only and must remain labeled as such in every artifact.
- Keep a visible unresolved item for full-q80 proxy feasibility; do not close it in phase 3.

## Methods and Approaches

### Recommended primary approach for this phase

| Step | What to do | Why this is best here |
| ---- | ---------- | --------------------- |
| 1 | Re-use `qiskit_black_hole_hardware_runner.py` as the execution substrate. | It already captures raw/mittigated subset observables and exact q14 reference behavior; minimizing divergence preserves claim continuity. |
| 2 | Add a **phase-3 mapping note first**: exact map from current fixed-observable q14 definitions to hardware-callable outputs (depths, qubits, perturb positions, subset labels). | Protects against overclaiming and enforces explicit scope before any code-level expansion. |
| 3 | Add optional `q14`-specific hardware-friendly OLE output fields that are linked to overlap/disjoint support labels and explicitly marked as provisional until validated against explicit construction. | Makes Phase 3 hardware note concrete while respecting the contract that OLE is not just a renamed perturb-return. |
| 4 | Extend `q80` execution docs to require at least two disjoint subset runs and both overlap/disjoint control points. | This preserves locality reasoning already established in `levelb_evidence_report.md`. |

### Alternative approach if direct OLE mapping becomes unstable

| Alternative | What it gives | When to switch |
| ----------- | ------------- | -------------- |
| Randomized-measurement OTOC route (`Vermersch et al.` family) | Avoids direct backward-state reverse-evolution dependence. | If extra circuit-level control or inversion cost dominates and signals become too brittle in the direct-path continuation. |

### What not to do

- Do not infer OLE from only `perturbed_echo` runs; this is explicitly forbidden by the phase contract.
- Do not propose full-q80 global OLE until explicit full-scale proxy is derived and validated.
- Do not add non-manifest changes to depths, seeds, trial count, or metric definition without a handoff update in `CONTEXT`/PLAN.

## Computational Toolchain for this phase

### Core execution tools

| Tool | Role | Status |
| ---- | ---- | ------ |
| `qiskit_black_hole_ole_exact.py` | Exact fixed-observable q14 OLE dataset generator | Already implemented; primary source for mathematical ground truth |
| `analyze_q14_ole_benchmark.py` | Exact/report bridge against baseline | Already implemented |
| `qiskit_black_hole_hardware_runner.py` | Hardware run orchestration and JSON schema |
| `qiskit_black_hole_scrambling.py` | Baseline task generation and manifest-aligned circuit family | Reuse for continuity |
| `qiskit`, `qiskit_ibm_runtime`, `qiskit_aer` | Simulator + hardware execution | Existing stack in artifacts |
| `numpy`, `json`, plotting stack (matplotlib) | Postprocessing and fit checks | Needed for scope note and q80/phase summaries |

### Command-level starting points

- Hardware mapping note baseline command (existing family):

```bash
scripts/run-in-qiskit-venv.sh python files/quantum-math-lab/qiskit_black_hole_hardware_runner.py \
  --qubits 14 --depths 1,2,3,4 --trials 3 --seed 424242 --shots 4000 --perturb-qubit 0 \
  --output-json files/quantum-math-lab/results/hardware/.../q14_ole_ready_note.json
```

- q80 subset locality check pattern (existing semantics):

```bash
scripts/run-in-qiskit-venv.sh python files/quantum-math-lab/qiskit_black_hole_hardware_runner.py \
  --qubits 80 --depths 1,2,3,4 --trials 3 --shots 4000 --perturb-qubit 10 \
  --subset-qubits 10-19 --readout-mitigation --cal-shots 6000 --skip-exact \
  --output-json files/quantum-math-lab/results/hardware/.../q80_subsetXX.json
```

Keep these as templates; exact file names should be standardized in the phase-3 plan.

## Validation and Verification Strategy (for planner)

### Minimal validity checks to satisfy `VALD-02`

1. **No-proxy check:** output documents explicitly keep `perturbed_echo` as baseline and do not relabel it as OLE.
2. **Manifest continuity:** fixed 14q manifest params in every phase-3 artifact (`qubits`, `depths`, `trials`, `seed`, `shots`).
3. **Support control preserved:** both overlap/disjoint support points are explicit and interpreted consistently in text and plots.
4. **Classical-vs-hardware dual-path separation:** classical exact benchmark remains unchanged as reference; hardware section records limitations and run-specific caveats.
5. **q80 scope check:** full list of subset labels used in hardware runs appears in outputs (`subset_qubits`) and all q80 conclusions are local-scope statements.
6. **Hardware-runtime hygiene:** include runtime/metadata fields so hardware utility claims are comparable in the existing framework (or explicitly state cannot be compared at this stage).

### Falsifiers (stop/re-scope triggers)

- Noisy hardware signal that can be explained without explicit support control.
- Inability to produce fixed `P`,`G`, and branch labels in any hardware artifact.
- Overlapping evidence where “full-q80” is inferred from subset fields.

## Common Pitfalls to guard in planning

- **Pitfall 1:** Reusing old `q14` language for q80 hardware outputs without relabeling. 
  - Mitigation: require per-run fields `branch=overlap|disjoint`, `subset_qubits`, `source=state-return`/`ole_proxy`.
- **Pitfall 2:** Treating large subsets as global proxy.
  - Mitigation: every q80 note states “subset observable” and explicitly states what the statistic estimates.
- **Pitfall 3:** Claiming OLE onset from one delta point.
  - Mitigation: require small-window stability checks and branch-wise comparison with exact disjoint expectation (`flatness`).
- **Pitfall 4:** Conflating hardware-ready note with accomplished hardware mapping.
  - Mitigation: distinguish `mapping_plan`, `execution_plan`, `validated mapping` stages.

## Key Derivations and Not-for-Implementation Shortcuts

### Exact branch sanity constraints

- With `P = Z_0`, `q=0` at depth 0: `kappa ≈ 4`, expected `F_delta = cos(2 delta)` behavior.
- With `P = Z_0`, `q=10` at depth 0: `kappa = 0`, expected flat `F_delta = 1`.

### Hardware-side constraints from physics and architecture

- If exact OLE correlator terms are not directly measured on hardware, planner should never treat subset `p_zero` statistics as equivalent to OLE.
- Subset observables should be treated as locality probes and utility diagnostics, not as global operator-correlation measurements.

## Literature Landscape and External Anchors

### Primary reference set already available in this project

1. `ref-algorithmiq-ole` — fixed-observable OLE form and small-delta bridge.
2. `ref-status` — active claim language and scope boundaries.
3. `ref-levelb-evidence` — q80 locality and subset support record.
4. `hardware_advantage_protocol.md` — protocol hierarchy (Level A/B/C), mitigation and over-claim barriers.

### Additional published anchors used for cross-checking semantics

- Yan, Cincio, Zurek (`1903.02651v4`) — LE/OTOC bridge context.
- Harris, Yan, Sinitsyn (`2110.12355v2`) — anti-butterfly and false-positive controls.
- Zanardi (`2107.01102v3`) — observable-subspace viewpoint, useful for subset phrasing.
- Vermersch et al. (`1807.09087v2`) — randomized-measurement OTOC backup.
- Kastner, Osterholz, Gross (`2403.08670v1`) — ancilla-free backward-evolution measurement path.

### Reference gap warning

The snapshot still has limited DOI-backed literature coverage in primary docs; the project depends strongly on internal artifacts for practical validity gates. Planner should treat literature citations as reinforcing and not as replacements for `q14_only_manifest`, `status`, and benchmark schema constraints.

## Don't Re-derive

- Do not re-derive the fixed q14 contract; it is already locked in project/phase context.
- Do not re-derive gate-level benchmark semantics for `perturbed_echo` from first principles.
- Do not rebuild an exact `q14` OLE method from scratch; use `qiskit_black_hole_ole_exact.py` results and existing analyzer.
- Do not replace the subset-first q80 strategy with speculative full-overlap assumptions.

## Open questions

1. Which exact hardware artifact schema is best for phase 3: schema extension in `qiskit_black_hole_hardware_runner.py` or a dedicated `qiskit_black_hole_ole_hardware.py` wrapper? (both remain feasible; wrapper gives cleaner separation)
2. Can fixed-observable OLE be represented as a direct hardware observable with minimal extra circuits, or should phase 3 settle for explicit `hardware-ready mapping note + controlled subset proxy` in its first pass?
3. How much of full-q80 OLE should be left as unresolved in `deliv-q80-scope-note`, and when should it flip from explicit visibility to a formal blocked follow-up?

## Caveats and Alternatives

- If direct fixed-observable hardware construction is too invasive, prioritize preserving scientific integrity: keep current hardware runs as high-quality subset-locality evidence and clearly label full-q80 OLE as unresolved.
- If reverse-evolution noise dominates, pivot to randomized-measurement OTOC protocols as explicit fallback and document why the fallback was necessary.
- If subset support is unstable across calibrations, do not treat that instability as evidence of scrambling physics without additional support controls.

## Execution update: q14 hardware verdict boundary (2026-03-19)

Phase-3 execution now has a concrete q14 hardware boundary from the completed overlap/disjoint hardware runs, corrected local-fold checkpoint ZNE, and a narrow PE-LiNN mitigation branch.

Current allowed interpretation:

- q14 hardware mapping is operationally successful.
- Readout mitigation plus corrected checkpoint ZNE provide branch-controlled checkpoint evidence.
- The cleanest checkpoint is depth `2`, where overlap remains clearly above disjoint.
- Depth `3` remains noisier but still preserves overlap-above-disjoint ordering in the corrected checkpoint run.

Current blocked interpretation:

- No full q14 hardware closure.
- No decisive OLE-equivalent confirmation from the present hardware observables.
- No PE-LiNN-based mitigation claim for q14.

Planning consequence:

- Treat `files/quantum-math-lab/results/hardware/phase3_q14_zne_xsup_s8000_f135_localfold.json` as the checkpoint-level ZNE reference artifact.
- Treat `.gpd/research/OLE_HARDWARE_PATH.md` sections 11-12 as the authoritative execution verdict.
- Do not route phase-3 wording through PE-LiNN outputs, because the mitigated baseline remains materially better on held-out q14 splits.

## q20 subset-proxy seeded control update (2026-03-20)

The preferred shallow-depth control set is now frozen from the seeded q20 subset-proxy rerun with seed_transpiler 424242:
- S_A = 0..9: overlap q=0, far-disjoint q=19.
- S_B = 10..19: overlap q=10, far-disjoint q=0.
- S_A q=10 is retained only as a diagnostic near-boundary control.

Shallow-depth mitigated subset contrasts (far-disjoint minus overlap):
- S_A, depth 1: +0.98326.
- S_A, depth 2: +0.66936.
- S_B, depth 1: +0.89765.
- S_B, depth 2: +0.78241.

Carry-forward rule:
- Claim-bearing q20/q80 subset-locality discussion should use the seeded far-disjoint pair at depths 1 and 2.
- Near-boundary controls may be reported, but they are diagnostic-only when they disagree with the far-disjoint pair.

## q80 pilot execution update (2026-03-20)

The scale-up sequence has now reached a successful q80 subset-proxy pilot for the first subset.

Completed pilot:
- subset `S_A = 0..9`
- overlap `q=0`
- far-disjoint `q=79`
- seeded transpilation `424242`
- shallow depths `1,2`

Observed mitigated subset contrasts (`far-disjoint - overlap`):
- depth 1: `+0.98420`
- depth 2: `+0.89110`

Carry-forward interpretation:
- q80 subset-locality survives the width scale-up in the first subset pilot.
- This is sufficient to record a successful q80 scale-up milestone under the subset-proxy boundary.
- It is not sufficient for symmetric two-subset closure or any full-q80 OLE-equivalent claim.
