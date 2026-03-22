# Q80 subset scope note

## Purpose

Carry the Phase-3 q14 hardware verdict forward into the q80 subset-continuation work without overclaim drift.

This note does not claim full-q80 fixed-observable OLE. It defines the allowed scope for q80 subset-observable hardware interpretation after the completed q14 mapping, corrected local-fold checkpoint ZNE update, and negative PE-LiNN mitigation result.

## Carry-forward boundary from q14

Authoritative q14 verdict source:

- `.gpd/research/OLE_HARDWARE_PATH.md`

Carry-forward rules:

- Allowed q14 hardware evidence: readout mitigation plus corrected checkpoint ZNE.
- Blocked q14 hardware evidence: PE-LiNN outputs, whole-grid overclaim, or OLE-equivalent relabeling.
- q80 wording must inherit this stricter boundary, not weaken it.

## Fixed q80 subset scope

Canonical subset labels:

- `S_A = 0..9`
- `S_B = 10..19`

Canonical branch controls:

- overlap branch: `q = 0`
- disjoint branch: `q = 10`

Fixed execution conventions for scope planning:

- qubits: `80`
- depths: `1,2,3,4`
- trials: `3`
- seed: `424242`
- shots: `4000`
- raw and readout-mitigated outputs both recorded

Interpretation rule:

- q80 subset results are locality/support diagnostics only.
- They are not a substitute for a full-q80 fixed-observable estimator.

## Allowed evidence language

Allowed wording for q80 notes and later summaries:

- `subset-locality evidence`
- `support-controlled exploratory hardware evidence`
- `raw-vs-mitigated subset contrast`
- `hardware-ready continuation under the q14-validated interpretation boundary`

Blocked wording:

- `full-q80 OLE confirmed`
- `global OLE visible on hardware`
- `PE-LiNN-mitigated q80 confirmation`
- `subset evidence closes the full-q80 question`

## Practical q80 guardrails

Before any q80 claim language is strengthened, all of the following must remain explicit:

- subset label on every table or artifact
- branch label (`q=0` or `q=10`) on every table or artifact
- raw versus mitigated separation
- unresolved full-q80 block
- no PE-LiNN evidence in the support chain

## Full-q80 unresolved block

Closed now:

- q14 hardware mapping path
- corrected q14 checkpoint ZNE as admissible checkpoint evidence
- q80 can proceed only as subset-observable continuation

Still unresolved:

- a defensible full-q80 fixed-observable estimator
- a hardware path that justifies global-q80 OLE-equivalent wording
- any learned-mitigation route that improves on the current mitigated baseline

Trigger for future full-q80 design work:

- subset evidence remains stable under rerun and mitigation checks
- estimator semantics are upgraded beyond state-return baseline quantities
- the full-q80 observable definition is explicit and independently verifiable

## Immediate planning consequence

- Use `.gpd/phases/03/03-02-PLAN.md` only in the subset-locality sense.
- Treat q14 corrected checkpoint ZNE as the strongest hardware interpretation anchor now available.
- Do not route q80 claim support through PE-LiNN outputs.

## Control-boundary update (2026-03-19)

Canonical q80 subset-language is refined as follows:
- `S_A = 0..9`: `q=10` is a near-disjoint boundary control, not the preferred far-disjoint comparator.
- `S_A = 0..9`: use `q=19` as the far-disjoint comparator for primary subset-locality checks.
- `S_B = 10..19`: `q=0` is the far-disjoint comparator.
- Main subset-locality checkpoints should compare overlap versus far-disjoint at shallow depths (`d=1,2`).
- Near-disjoint controls may still be reported, but they are diagnostic-only when they disagree with the far-disjoint pair.

## q80 pilot validation update (2026-03-20)

The first q80 pilot subset was completed successfully for `S_A = 0..9` using the preferred overlap-versus-far-disjoint control pair `q=0` versus `q=79`.

Pilot result (`readout_mitigated`, shallow depths):
- depth 1: `q79 - q0 = +0.98420`
- depth 2: `q79 - q0 = +0.89110`

Interpretation boundary:
- This validates the scale-up path to q80 in the subset-locality sense for the first subset pilot.
- The pilot is strong enough to support `q80 subset-proxy locality evidence` language for `S_A = 0..9`.
- It is not yet a symmetric two-subset q80 result, and it does not justify full-q80 or global-OLE wording.

Planning consequence:
- A symmetric second-subset q80 pilot is now optional follow-up validation, not a blocker for recording the scale-up milestone.
- Main q80 wording should remain: `successful q80 subset-proxy pilot under the shallow-depth far-disjoint control rule`.

## Pilot raw-vs-mitigated table and reproducibility gate (2026-03-20)

Claim-bearing pilot family recorded in this note:
- subset: `S_A = 0..9`
- overlap branch: `q = 0`
- far-disjoint branch: `q = 79`
- depths: `1,2`
- trials: `3`
- seed / seed_transpiler: `424242`

Every claim-bearing q80 table must carry these fields explicitly:
- `subset_label`
- `branch_label`
- `perturb_qubit`
- `depth`
- `trials`
- `shots`
- `raw.perturbed_subset_echo` (mean, std)
- `readout_mitigated.perturbed_subset_echo` (mean, std)
- `transpiled perturbed depth`
- `transpiled perturbed two_qubit_gate_count`

Pilot contrast table for the first q80 subset family:

| depth | branch | raw `perturbed_subset_echo` | `readout_mitigated` `perturbed_subset_echo` | interpretation |
| --- | --- | --- | --- | --- |
| 1 | overlap `q=0` | `0.01925 +/- 0.00461` | `0.00669 +/- 0.00293` | low overlap-side subset echo |
| 1 | far-disjoint `q=79` | `0.97117 +/- 0.00129` | `0.99089 +/- 0.00027` | clean far-disjoint control |
| 2 | overlap `q=0` | `0.07717 +/- 0.03422` | `0.06551 +/- 0.03523` | still low, but broader trial spread |
| 2 | far-disjoint `q=79` | `0.86763 +/- 0.00233` | `0.95661 +/- 0.00227` | clean far-disjoint control |

Reproducibility gate:
- The default claim-bearing configuration remains `3` trials with fixed seed discipline.
- `4000 -> 8000` shot reruns and `3 -> 5` trial expansions remain diagnostic-only unless a later note explicitly promotes them.
- Claim upgrades are blocked if overlap-versus-far-disjoint ordering flips sign at matched depth, or if trial spread exceeds `25%` on both rows at the same depth.
