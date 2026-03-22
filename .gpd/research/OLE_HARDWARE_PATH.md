# Phase 3 Plan 03-01: Hardware Mapping Note for q14 Fixed-Observable OLE

**Status:** completed
**Phase:** 03
**Plan:** 03-01
**Created:** 2026-03-19

## 1. Scope and contract

This note maps the locked q14 fixed-observable OLE target onto the existing hardware pipeline for execution continuity.

- It is **hardware-ready mapping only**.
- Current runner outputs are baseline-compatible, not final OLE estimator outputs.
- `perturbed_echo` / `perturbed_subset_echo` are same-family baselines only.
- Full fixed-observable OLE claims on hardware require an explicit estimator rewrite and explicit circuits.

## 2. Fixed-observable bridge definition

Use AP-picture notation:

- A_P(U) = U P U^dagger
- V_delta = exp(-i delta X_q)
- F_delta(P) = 2^-n Tr(A_P V_delta^dagger A_P V_delta), dimensionless
- f_delta(O) = 2^-n F_delta(P), with O = Z_0 / sqrt(2^14), dimensionless

Branch labels:

- q = 0 (overlap branch)
- q = 10 (disjoint control branch)

## 3. Manifest lock (q14, no drift)

Values are fixed and must match `files/quantum-math-lab/benchmarks/q14_only_manifest.json`:

- qubits: 14
- depths: 1,2,3,4
- trials: 3
- seed: 424242
- shots: 4000
- optimization_level: 1
- perturb_qubit: 0 or 10
- readout_mitigation policy: `--readout-mitigation --cal-shots 6000`

## 4. Command-output matrix (raw and mitigated)

| ID | Command | Branch | Output file | Required runner fields | Observable fields present |
| --- | --- | --- | --- | --- | --- |
| S1-raw | `scripts/run-in-qiskit-venv.sh python files/quantum-math-lab/qiskit_black_hole_hardware_runner.py --qubits 14 --depths 1,2,3,4 --trials 3 --seed 424242 --shots 4000 --perturb-qubit 0 --backend ibm_fez --output-json files/quantum-math-lab/results/hardware/phase3_q14_overlap_raw.json` | overlap (q=0) | `.../phase3_q14_overlap_raw.json` | config.qubits, depths, trials, seed, shots, perturb_qubit=0, readout_mitigation=false, cal_shots default, skip_exact false, subset_qubits=[] | raw.ideal_echo, raw.perturbed_echo, raw.ideal_abs_error_vs_exact, raw.perturbed_abs_error_vs_exact, summary_by_depth.raw.ideal_echo, summary_by_depth.raw.perturbed_echo |
| S1-mit | same as above with `--readout-mitigation --cal-shots 6000` and output `.../phase3_q14_overlap_raw_vs_mit.json` | overlap (q=0) | `.../phase3_q14_overlap_raw_vs_mit.json` | adds config.readout_mitigation=true, cal_shots=6000 | raw.* and readout_mitigated.* plus calibration metadata |
| S2-raw | `... --perturb-qubit 10 --output-json .../phase3_q14_disjoint_raw.json` | disjoint (q=10) | `.../phase3_q14_disjoint_raw.json` | as S1-raw with perturb_qubit=10 | same raw fields as S1-raw |
| S2-mit | `... --perturb-qubit 10 --readout-mitigation --cal-shots 6000 --output-json .../phase3_q14_disjoint_raw_vs_mit.json` | disjoint (q=10) | `.../phase3_q14_disjoint_raw_vs_mit.json` | as S1-mit with perturb_qubit=10 | raw.* and readout_mitigated.* plus calibration metadata |

Machine-consumable schema mapping (expected keys in JSON):

```json
{
  "config": {
    "qubits": 14,
    "depths": [1,2,3,4],
    "trials": 3,
    "seed": 424242,
    "shots": 4000,
    "perturb_qubit": 0,
    "optimization_level": 1,
    "readout_mitigation": false,
    "cal_shots": 6000,
    "skip_exact": false
  },
  "runs": [
    {
      "depth": 1,
      "trial": 0,
      "seed": 123,
      "raw": {
        "ideal_echo": 0.0,
        "perturbed_echo": 0.0,
        "ideal_abs_error_vs_exact": 0.0,
        "perturbed_abs_error_vs_exact": 0.0
      },
      "exact": {
        "ideal_echo": 1.0,
        "perturbed_echo": 1.0
      },
      "transpiled": {
        "ideal": {"depth": 0, "two_qubit_gate_count": 0},
        "perturbed": {"depth": 0, "two_qubit_gate_count": 0}
      }
    }
  ],
  "summary_by_depth": [{"depth":1,"raw":{"ideal_echo":{"mean":0.0,"std":0.0},"perturbed_echo":{"mean":0.0,"std":0.0}}}]
}
```

Notes:

- When `--subset-qubits` is used, `raw`/`readout_mitigated` include subset fields and subset labels.
- `readout_mitigated` fields are only present when mitigation is enabled.

## 5. Anti-overclaim clause and unresolved estimator gate

Hard statement for the phase-3 deliverable:

> Existing `perturbed_echo` and `perturbed_subset_echo` outputs are same-family baseline statistics from the state-return workflow and must not be treated as final fixed-observable OLE estimator values. A final OLE-equivalent claim requires an explicit additional circuit+estimator definition that reconstructs `F_delta(P)` / `f_delta(O)` observables from fixed-support hardware measurements.

Gate before `OLE`-equivalent interpretation:

- Branch labels `q=0` and `q=10` are explicit in command and metadata.
- Manifest lock checks pass exactly.
- Small-delta interpretation is separated (`<=0.10` quoted, `<=0.20` diagnostic).
- Depth-0 controls remain interpretable (`kappa≈4` expected for overlap branch and flat disjoint branch behavior).
- raw vs mitigated comparison is reported and does not hide spread.
- Any full OLE claim is blocked until this checklist passes and a new estimator artifact is added.

## 6. O(δ) discipline and handoff checks

- Primary quoted short-window: `delta <= 0.10`.
- Broad diagnostic support window: `delta <= 0.20`.
- Disqualifier: progression is halted if disjoint branch loses expected flatness or overlap branch loses small-δ structure.

## 7. Resource and error-budget assumptions

- Per q14 branch class:
  - shots = 4000
  - trials = 3
  - depths = 4
  - circuits per trial-depth = 2
  - total shots = 4000 × 3 × 4 × 2 = 96k
- Mitigation overhead per class:
  - calibration circuits = 2, each 6000 shots = 12k shots
  - extra metadata/mitigation diagnostics recorded in output `calibration`

## 8. Output contract and q80 continuity link

Deliverables in this plan:

- `.gpd/research/OLE_HARDWARE_PATH.md` (this document)
- q14 output artifacts (planned):
  - `files/quantum-math-lab/results/hardware/phase3_q14_overlap_raw.json`
  - `files/quantum-math-lab/results/hardware/phase3_q14_overlap_raw_vs_mit.json`
  - `files/quantum-math-lab/results/hardware/phase3_q14_disjoint_raw.json`
  - `files/quantum-math-lab/results/hardware/phase3_q14_disjoint_raw_vs_mit.json`

Open-item for downstream phase-3 work:

- `.gpd/phases/03/03-02-PLAN.md` and `q80` scope continuation must remain explicit subset-observable and keep "full-q80 global OLE unresolved" visible.

## 9. Executed q14 hardware evidence (2026-03-19)

The q14 mapping runs in this note were executed on `ibm_fez` for both overlap (`q=0`) and disjoint (`q=10`) branches in raw and readout-mitigated modes. The practical q14 mitigation path required one implementation adjustment in `qiskit_black_hole_hardware_runner.py`: for full-register 14-qubit mitigation, the code now uses a direct local-tensor `p_zero` estimator instead of constructing the dense `2^n x 2^n` assignment matrix.

Executed artifacts:

- `files/quantum-math-lab/results/hardware/phase3_q14_overlap_raw.json`
- `files/quantum-math-lab/results/hardware/phase3_q14_overlap_raw_vs_mit.json`
- `files/quantum-math-lab/results/hardware/phase3_q14_disjoint_raw.json`
- `files/quantum-math-lab/results/hardware/phase3_q14_disjoint_raw_vs_mit.json`
- `files/quantum-math-lab/results/hardware/phase3_q14_overlap_raw_vs_mit_s8000.json`
- `files/quantum-math-lab/results/hardware/phase3_q14_disjoint_raw_vs_mit_s8000.json`

Operational result:

- The hardware mapping pipeline is functioning end-to-end for the locked q14 branch pair.
- Raw full-register ideal echoes sit near `0.73-0.78`, so unmitigated runs remain readout-limited.
- Readout mitigation lifts the ideal branch to `1.0` in all q14 mitigated summaries, which is a useful calibration sanity check but not itself a physics claim.

Mitigated control comparison (`perturbed_echo`, 8000-shot rerun):

- depth 1: overlap `0.0184 +/- 0.0077`, disjoint `0.1079 +/- 0.1414`
- depth 2: overlap `0.2045 +/- 0.2425`, disjoint `0.0174 +/- 0.0167`
- depth 3: overlap `0.1882 +/- 0.1593`, disjoint `0.0269 +/- 0.0222`
- depth 4: overlap `0.0218 +/- 0.0060`, disjoint `0.0863 +/- 0.0945`

Interpretation gate:

- Depths 2 and 3 show the desired overlap-above-disjoint pattern.
- Depths 1 and 4 invert that ordering.
- The overlap branch remains broad at depths 2 and 3 even after the 8000-shot rerun.

Current status for this phase note:

- q14 hardware mapping: **successful**
- q14 readout-mitigated control evidence: **mixed**
- allowed wording: hardware-ready continuity and branch-controlled exploratory evidence
- blocked wording: decisive q14 hardware confirmation of the fixed-observable OLE bridge

## 10. Focused q14 checkpoint ZNE with extra suppression

A focused checkpoint run was added for the unstable q14 hardware points using hardware-valid global folding on the measured circuit body, combined with the existing mitigation stack:

- depths: `2,3`
- branches: overlap `q=0`, disjoint `q=10`
- ZNE factors: `1,3`
- shots: `8000`
- readout mitigation: enabled
- extra suppression: enabled (`DD=XY4`, gate twirling with `8` randomizations)
- artifact: `files/quantum-math-lab/results/hardware/phase3_q14_zne_xsup_s8000.json`

Checkpoint result summary (`mitigated perturbed_echo`, then linear ZNE-to-zero-noise estimate):

- overlap, depth 2: `f=1 -> 0.38045`, `f=3 -> 0.37082`, `zne(0) -> 0.38527`
- disjoint, depth 2: `f=1 -> 0.08493`, `f=3 -> 0.08276`, `zne(0) -> 0.08601`
- overlap, depth 3: `f=1 -> 0.06045`, `f=3 -> 0.05745`, `zne(0) -> 0.06196`
- disjoint, depth 3: `f=1 -> 0.00937`, `f=3 -> 0.00804`, `zne(0) -> 0.01003`

Interpretation:

- The overlap branch remains above the disjoint branch at both checkpoint depths.
- The `f=1 -> f=3` drift is small and monotone in this checkpoint set, so the ZNE fit is at least internally consistent.
- This is stronger than the earlier mixed whole-grid readout-mitigated evidence, but it is still checkpoint evidence rather than a full q14 hardware closure.

## 11. Corrected local-fold checkpoint ZNE update

The earlier checkpoint ZNE interpretation needed one correction: folding the full measured echo body can self-cancel too strongly for this circuit family. The checkpoint runner was therefore updated to apply odd-factor local folding after transpilation, targeting the transpiled two-qubit gates rather than the full `U X U^-1` body.

Replacement artifact:

- `files/quantum-math-lab/results/hardware/phase3_q14_zne_xsup_s8000_f135_localfold.json`

Execution details:

- backend: `ibm_fez`
- hardware job: `d6turec69uic73chl4sg`
- calibration job: `d6tusv8v5rlc73f3biqg`
- depths: `2,3`
- branches: overlap `q=0`, disjoint `q=10`
- ZNE factors: `1,3,5`
- shots: `8000`
- readout mitigation: enabled
- extra suppression: enabled (`DD=XY4`, gate twirling with `8` randomizations)

Corrected checkpoint summary (`mitigated perturbed_echo`):

- overlap, depth 2: `f=1 -> 0.36110`, `f=3 -> 0.36168`, `zne(0) -> 0.36592`
- disjoint, depth 2: `f=1 -> 0.08075`, `f=3 -> 0.07340`, `zne(0) -> 0.08635`
- overlap, depth 3: `f=1 -> 0.05502`, `f=3 -> 0.08826`, `zne(0) -> 0.02583`
- disjoint, depth 3: `f=1 -> 0.01033`, `f=3 -> 0.01370`, `zne(0) -> 0.00808`

Interpretation update:

- The corrected local-fold run does produce nonidentical folded checkpoint values, so the factors are now probing a real circuit-level noise change.
- Depth 2 remains the cleanest hardware checkpoint, with overlap well above disjoint.
- Depth 3 remains noisier, but overlap still stays above disjoint.
- Allowed wording: corrected checkpoint-level overlap-versus-disjoint separation on q14 hardware.
- Blocked wording: full q14 hardware closure or decisive OLE-equivalent confirmation.

## 12. Narrow PE-LiNN / ML mitigation verdict

A narrow ML mitigation branch was tested against the q14 hardware artifacts using a local bridge to the `PELINN-Q` model checkout. The bridge script lives in:

- `files/quantum-math-lab/q14_pelinn_ml.py`

Generated artifacts:

- `files/quantum-math-lab/results/hardware/phase3_q14_pelinn/`
- `files/quantum-math-lab/results/hardware/phase3_q14_pelinn_residual/`
- `files/quantum-math-lab/results/hardware/phase3_q14_pelinn_zne_only/`
- `files/quantum-math-lab/results/hardware/phase3_q14_pelinn_zne_localfold/`

Observed validation results:

- direct model on mixed data: `MAE 0.0675`, `RMSE 0.0873`
- residual model on mixed data: `MAE 0.1667`, `RMSE 0.2221`
- direct model on old ZNE-only data: `MAE 0.0314`, `RMSE 0.0383`
- direct model on corrected local-fold ZNE-only data: `MAE 0.0642`, `RMSE 0.0810`
- current mitigated baseline on the matched validation splits stays much lower (`RMSE ~= 0.009-0.013`)

Verdict:

- The PE-LiNN branch does not improve on the existing mitigated estimator for the current q14 dataset.
- The present q14 ML dataset is too small and too unstable to support a defensible learned-mitigation claim.
- Phase-3 hardware interpretation should therefore rely on readout mitigation plus corrected checkpoint ZNE, not on PE-LiNN.

## 13. q80 subset control-boundary update (2026-03-19)

The symmetric far-disjoint control for `S_B = 10..19` is already available from the existing `q=0` run; no rerun was required because the `ml_diagnostic` sidecar was postprocessing-only and did not affect the `raw` or `readout_mitigated` observables.

Updated rule for q20/q80 subset-locality controls:
- `S_A = 0..9`: `q=0` is overlap, `q=10` is near-disjoint boundary control, `q=19` is far-disjoint control.
- `S_B = 10..19`: `q=10` is overlap, `q=0` is far-disjoint control.
- Claim-bearing subset-locality comparisons should use the overlap-versus-far-disjoint pair at shallow depths first (`d=1,2`).
- `q=10` for `S_A` is retained only as a diagnostic near-disjoint control; it is not robust enough to serve as the sole disjoint comparator.

Shallow-depth mitigated subset contrasts (`disjoint - overlap`):
- `S_A`, depth 1: `q=10 - q=0 = +0.98312`; `q=19 - q=0 = +0.98246`.
- `S_A`, depth 2: `q=10 - q=0 = -0.04348`; `q=19 - q=0 = +0.68062`.
- `S_B`, depth 1: `q=0 - q=10 = +0.89711`.
- `S_B`, depth 2: `q=0 - q=10 = +0.77796`.

Interpretation:
- The q20 subset-locality proxy is not failing globally.
- The control failure is concentrated in the `S_A` near-boundary choice `q=10`, which collapses at depth 2.
- Promoting `q=19` to the far-disjoint comparator restores the expected overlap/disjoint separation for `S_A`.

## 14. Seeded q20 subset contrast addendum (2026-03-20)

A preferred seeded rerun was executed with `seed_transpiler = 424242` and the control set `{S_A q0, S_A q19, S_B q10, S_B q0}`. This confirms the preferred far-disjoint comparators at shallow depth using the seeded artifacts rather than the earlier mixed control bundle.

Shallow-depth mitigated subset contrasts (`far-disjoint - overlap`):
- `S_A`, depth 1: overlap `q=0 = 0.00749 +/- 0.00539`, far-disjoint `q=19 = 0.99075 +/- 0.00010`, delta `+0.98326`.
- `S_A`, depth 2: overlap `q=0 = 0.28135 +/- 0.34183`, far-disjoint `q=19 = 0.95072 +/- 0.00202`, delta `+0.66936`.
- `S_B`, depth 1: overlap `q=10 = 0.09717 +/- 0.11901`, far-disjoint `q=0 = 0.99481 +/- 0.00387`, delta `+0.89765`.
- `S_B`, depth 2: overlap `q=10 = 0.20799 +/- 0.24467`, far-disjoint `q=0 = 0.99040 +/- 0.00113`, delta `+0.78241`.

Decision update:
- The preferred q20 subset-proxy control set is now frozen at `S_A: q0 vs q19` and `S_B: q10 vs q0` for shallow-depth claim support.
- `S_A q10` remains diagnostic-only as a near-boundary control.

## 15. q80 pilot scale-up addendum (2026-03-20)

A seeded q80 pilot subset-locality run was completed for `S_A = 0..9` with `seed_transpiler = 424242`, overlap `q=0`, and far-disjoint `q=79`. The pilot used shallow depths `1,2`, readout mitigation, `XY4` dynamical decoupling, and twirling on `ibm_fez`.

Pilot artifacts:
- `files/quantum-math-lab/results/hardware/phase3_q80pilot_SA_q0_raw_vs_mit.json`
- `files/quantum-math-lab/results/hardware/phase3_q80pilot_SA_q79_raw_vs_mit.json`

Shallow-depth mitigated subset contrasts (`far-disjoint - overlap`):
- depth 1: overlap `q=0 = 0.00669 +/- 0.00293`, far-disjoint `q=79 = 0.99089 +/- 0.00027`, delta `+0.98420`.
- depth 2: overlap `q=0 = 0.06551 +/- 0.03523`, far-disjoint `q=79 = 0.95661 +/- 0.00227`, delta `+0.89110`.

Gate-burden note:
- The perturbed branch remains a real gate-based circuit at q80.
- For both `q=0` and `q=79`, the transpiled perturbed circuits are matched at shallow depth: depth `14` with `2` two-qubit gates at logical depth 1, and depth `18` with `2` two-qubit gates at logical depth 2.
- The q80 pilot separation is therefore not explained by a branch-specific transpilation burden mismatch.

Decision update:
- The scale-up path `q20 -> q24 -> q32 -> q80` now has a successful q80 subset-proxy pilot on hardware.
- This is strong q80 subset-locality pilot evidence for `S_A = 0..9` at shallow depth.
- It remains pilot evidence only: the result does not yet close the symmetric second-subset check, full-q80 visibility, or any full OLE-equivalent claim.
