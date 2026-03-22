# Phase 3: Hardware Mapping and q80 Scope - Experiment Design

**Designed:** 2026-03-18
**Phase:** 03
**Mode:** `balanced` (from `.gpd/config.json`)
**Scope:** preserve `q14`-to-`q80` continuity without collapsing subset/global distinctions

## Objective

Design the numerical experiment and execution map for Phase 3 such that:

1. the first result is a hardware-ready mapping note connecting the fixed-observable q14 OLE contract to the existing hardware runner stack,
2. q80 continuation is explicitly scoped as fixed-support subset observables with locality controls,
3. the unresolved full-q80 global OLE question remains visible and is not converted into a completed claim.

## Locked Inputs and Non-Negotiables

| Field | Value / Rule |
| ----- | ------------ |
| q14 manifest | `files/quantum-math-lab/benchmarks/q14_only_manifest.json` |
| qubits | `14` for the bridge handoff, `80` for subset continuation |
| depths | `1,2,3,4` |
| trials | `3` |
| seed | `424242` |
| shots (default) | `4000` |
| overlap branch | `perturb-qubit = 0` |
| disjoint control | `perturb-qubit = 10` |
| observable lock | `P = Z_0`, `O = Z_0 / sqrt(2^14)` |
| q14 primary report quantity | `F_delta(P)` |
| normalized form | `f_delta(O)=2^-14 F_delta(P)` |
| forbidden rename | `perturbed_echo` is a baseline only and may not be labeled as OLE |
| q80 interpretation rule | subset evidence is locality/utility evidence, not full q80 OLE |

## Phase Success Criteria (for this phase)

1. A hardware-ready note exists that maps the fixed-observable q14 OLE contract onto the existing hardware execution pipeline and records all current limitations.
2. The q80 plan is explicitly subset-scoped with fixed support labels and overlap/disjoint control branches.
3. The full-q80 global-OLE question remains as a visible unresolved forward item in scope docs and summaries.

## Deliverables this phase

- `deliv-hardware-ready-note`
- `deliv-q80-scope-note`

The deliverables are tied to PROT-01, PROT-02, and VALD-02 in `.gpd/REQUIREMENTS.md`.

## Target Quantities

The experiment works with two classes of objects: exact benchmarks (already available from Phase 2) and hardware-observable proxies.

| Quantity | Formula / Definition | Primary Source |
| --- | --- | --- |
| q14 overlap OLE target | `F_delta(Z_0; U, X_0) = 2^-14 Tr(U Z_0 U^dagger V_delta(X_0)^dagger U Z_0 U^dagger V_delta(X_0))` | `files/quantum-math-lab/results/ole/q14_ole_vs_delta2_benchmark.csv` |
| q14 disjoint locality control | same with `G = X_10` | same |
| normalized equivalent | `f_delta(O)=2^-14 F_delta(P)` with `O=Z_0/sqrt(2^14)` | same |
| q14 bridge-to-hardware alignment metric | whether `q14` hardware artifacts preserve task family and branch labeling without relabeling | `qiskit_black_hole_hardware_runner.py` runs |
| q80 subset locality signal | difference between perturbation on overlapping and disjoint control for fixed subsets | q80 subset hardware results |

## Fixed Geometry and Delta Grid (q14 continuity)

- q14 bridge anchor deltas: `0.000,0.025,0.050,0.075,0.100,0.125,0.150,0.200,0.250,0.300` (from Phase 2 baseline).
- Primary quoted-on-paper delta window remains `delta <= 0.10`.
- Full hardware mapping must remain compatible with this same notation and the `F_delta(P)` contract.

## Plan 03-01: Hardware Mapping Protocol for the q14 Bridge (PROT-01)

### Inputs

- Qiskit script stack and artifacts in `files/quantum-math-lab`.
- Runner defaults from manifest.
- `qiskit_black_hole_hardware_runner.py` as execution substrate.
- Exact references from `files/quantum-math-lab/results/ole/q14_ole_vs_delta2_benchmark.md` and `.../q14_small_delta_validation.md`.

### Outputs required from Plan 03-01

| Artifact Type | File | Content Requirement |
| --- | --- | --- |
| mapping note (required) | `.gpd/phases/03/deliv-hardware-ready-note.md` | branch mapping, command matrix, exact limitations, and explicit no-relabel policy |
| hardware continuity artifact (required) | `files/quantum-math-lab/results/hardware/phase3_q14_bridge_reference_*.json` | q14 overlap and disjoint perturbation outputs, with raw and mitigated views |
| optional OLE-extension artifact | `files/quantum-math-lab/results/ole/q14_ole_hardware_candidate.md` | only if hardware-estimator extension is completed; must compare candidate to exact |

### Execution Matrix for q14 (manifest locked)

| Metric | Value |
| --- | --- |
| qubits | `14` |
| depths | `1,2,3,4` |
| trials | `3` |
| seed | `424242` |
| shots | `4000` |
| perturb branches | `0` and `10` |
| mitigation mode | `raw` and `readout-mitigated` |
| cal shots | `6000` for mitigated runs |

### Exact command templates (existing runner; no protocol drift)

```bash
scripts/run-in-qiskit-venv.sh python files/quantum-math-lab/qiskit_black_hole_hardware_runner.py \
  --qubits 14 --depths 1,2,3,4 --trials 3 --seed 424242 --shots 4000 \
  --perturb-qubit 0 --backend ibm_fez --readout-mitigation --cal-shots 6000 \
  --output-json files/quantum-math-lab/results/hardware/phase3_q14_overlap_raw_vs_mit.json

scripts/run-in-qiskit-venv.sh python files/quantum-math-lab/qiskit_black_hole_hardware_runner.py \
  --qubits 14 --depths 1,2,3,4 --trials 3 --seed 424242 --shots 4000 \
  --perturb-qubit 10 --backend ibm_fez --readout-mitigation --cal-shots 6000 \
  --output-json files/quantum-math-lab/results/hardware/phase3_q14_disjoint_raw_vs_mit.json
```

### Mapping rule for hardware-readiness note

- The phase-3 hardware note must explicitly define that existing `qiskit_black_hole_hardware_runner.py` outputs are hardware estimates of:
  - `ideal_echo` and `perturbed_echo` for fixed full-length kick (`X` at the perturb qubit),
  - subset fields when configured.
- The note must map these to the fixed-observable bridge as: **compatibility only**, not as completed OLE equivalence.
- The note must include the phrase-level constraint: “existing `perturbed_echo`/`perturbed_subset_echo` are same-family baseline outputs and do not satisfy the final OLE estimator definition without explicit additional circuits.”
- If any script extension is added, the note must show the exact estimator rewrite used, including branch support labels and support overlap condition.

### Convergence / robustness checks in Plan 03-01

| Check family | Parameters | Acceptance |
| --- | --- | --- |
| shot convergence (diagnostic) | selected branch-depth points, `shots=4000` vs `8000` | mean stability within design tolerance before quoting small-δ hardware trend |
| mitigation convergence | raw vs readout mitigated on matched points | mitigation should reduce ideal/perturbed errors on the majority of points |
| seed-to-seed spread | fixed manifest trials | std across 3 trials must be finite and reported |
| cross-branch map check | overlap (`q=0`) vs disjoint (`q=10`) | disjoint branch should be visibly flatter on q14 and on any new OLE-extension mode |

## Plan 03-02: Immediate q80 subset strategy and unresolved full-q80 follow-up (PROT-02)

### q80 scope lock

- q80 results in this phase are subset-observable only and fixed-support:
  - `S_A = 0..9`
  - `S_B = 10..19`
- Two perturb-control branches for each subset:
  - overlap: `perturb-qubit = 0`
  - disjoint: `perturb-qubit = 10`
- The full-q80 global state-overlap/10-qubit-wide support proxy is explicitly not a final full-q80 OLE claim.

### Required q80 runs (compatibility with past evidence)

| Run family | Qubits | subsets | perturb qubit | mitigation |
| --- | --- | --- | --- | --- |
| q80 subset continuity A | `80` | `0..9` | `0` and `10` | raw + mitigated |
| q80 subset continuity B | `80` | `10..19` | `0` and `10` | raw + mitigated |

### Command templates (q80, fixed subsets)

```bash
scripts/run-in-qiskit-venv.sh python files/quantum-math-lab/qiskit_black_hole_hardware_runner.py \
  --qubits 80 --depths 1,2,3,4 --trials 3 --seed 424242 --shots 4000 \
  --perturb-qubit 0 --subset-qubits 0-9 --readout-mitigation --cal-shots 6000 \
  --skip-exact --output-json files/quantum-math-lab/results/hardware/phase3_q80_subset_A_q0.json

scripts/run-in-qiskit-venv.sh python files/quantum-math-lab/qiskit_black_hole_hardware_runner.py \
  --qubits 80 --depths 1,2,3,4 --trials 3 --seed 424242 --shots 4000 \
  --perturb-qubit 10 --subset-qubits 0-9 --readout-mitigation --cal-shots 6000 \
  --skip-exact --output-json files/quantum-math-lab/results/hardware/phase3_q80_subset_A_q10.json

scripts/run-in-qiskit-venv.sh python files/quantum-math-lab/qiskit_black_hole_hardware_runner.py \
  --qubits 80 --depths 1,2,3,4 --trials 3 --seed 424242 --shots 4000 \
  --perturb-qubit 0 --subset-qubits 10-19 --readout-mitigation --cal-shots 6000 \
  --skip-exact --output-json files/quantum-math-lab/results/hardware/phase3_q80_subset_B_q0.json

scripts/run-in-qiskit-venv.sh python files/quantum-math-lab/qiskit_black_hole_hardware_runner.py \
  --qubits 80 --depths 1,2,3,4 --trials 3 --seed 424242 --shots 4000 \
  --perturb-qubit 10 --subset-qubits 10-19 --readout-mitigation --cal-shots 6000 \
  --skip-exact --output-json files/quantum-math-lab/results/hardware/phase3_q80_subset_B_q10.json
```

### Deliverable for q80 scope note

` .gpd/phases/03/deliv-q80-scope-note.md ` must contain at least:

- explicit fixed subset labels `S_A`, `S_B`, and branch labels `q=0` / `q=10`,
- locality comparison with a depth-wise disjoint-overlap table,
- raw-vs-mitigated and error bars using the exact same support fields (`subset_qubits`) and summary naming,
- reproducibility notes and rerun deltas if reruns are performed,
- explicit statement that full-q80 global OLE remains unresolved and open.

## Measurement Semantics and Statistical Plan

### Statistics and error metrics

- Per-depth summaries remain mean/std over 3 fixed manifest trials.
- If `readout-mitigation` is enabled, report the same summary fields for raw and mitigated in pairwise tables.
- For subset runs report:
  - `subset_qubits`
  - `raw.ideal_subset_echo`
  - `raw.perturbed_subset_echo`
  - `readout_mitigated.ideal_subset_echo`
  - `readout_mitigated.perturbed_subset_echo`
- Reproduction check: for at least one `(subset, branch, depth)` pair, repeat all 3 trials and report rerun spread.

### Convergence and stability protocol (numerical parameters)

This phase has fixed manifest values for production runs; convergence checks are run as non-production diagnostics.

| Parameter | Diagnostics |
| --- | --- |
| shots | 4000 -> 8000 on matched q14 + one q80 subset branch |
| trials | 3 -> 5 on one q80 subset-family checkpoint |
| mitigation depth | compare raw and mitigated for all 4 depths |
| circuit family | fixed runner family only |

No production statistic should be mixed with diagnostic variants in final scope claims.

## Validation Gates (VALD-02)

1. No artifact may state `perturbed_echo` / `perturbed_subset_echo` as OLE without explicit estimator rewrite and proof-of-mapping section.
2. q80 statements must always include subset labels and cannot claim global 80q operator-overlap proof.
3. q14 mapping note must preserve exact-manifest fields unchanged and list any unimplemented OLE-bridge steps.
4. Full-q80 OLE must remain a forward question and appear in each phase-3 note’s “open question” block.

## Execution Order

1. Finalize 03-01 mapping note, include command-to-output mapping table and limitations.
2. Run q14 overlap/disjoint continuity jobs with and without mitigation.
3. Run q80 subset jobs for `S_A` and `S_B`, both perturb branches.
4. Produce per-depth summary tables for raw vs mitigated and overlap/disjoint contrast.
5. Generate `deliv-q80-scope-note.md` and keep unresolved full-q80 item explicit.
6. Only after all checks, update phase-3 handoff if full schema extension is implemented.

## Cost Estimate (coarse)

| Run class | N configs | N circuits per config | Dominant shot load |
| --- | --- | --- | --- |
| q14 mapping continuity | 4 raw+mit combos | 4×3 trials×2 circuits = 24 | 96k shots each |
| q80 subset continuity | 4 subset/branch combos | 24 each | 96k shots each |
| mitigation calibration | +1 calibration per mitigated config | 2×10 two-qubit cal circuits per config (in runner) | additional overhead only |

## Fallbacks

- If direct fixed-observable OLE hardware estimator cannot be added without introducing a new circuit construction, close Phase 3 at the mapping-documentation stage and keep q80 subset scope explicit.
- If q80 subset locality signal disappears under raw-to-mitigated pipeline checks, rerun with increased shots or rerun-day check before revising the scope note.
- If disjoint control ceases to be informative in q14/q80 diagnostics, pause and escalate via failure review rather than reframing the result as global OLE.

## Unresolved Full-q80 Question (must remain visible)

Full-q80 global OLE remains unresolved. Phase 3 does not convert this into a closed deliverable. The note should keep the explicit follow-up question: "Can one define and validate a scalable full-q80 fixed-observable OLE estimator, with bias-controlled hardware mapping, without relying on subset-reduction identities?"
