# q14 Small-Delta Validation

**Written:** 2026-03-18
**Phase:** 02
**Purpose:** record the shrinking-window quadratic fits and state whether the exact q14 benchmark really supports the promised small-delta interpretation

## Inputs Used

- exact OLE artifact: `files/quantum-math-lab/results/ole/black_hole_ole_q14_exact_small_delta.json`
- benchmark report: `files/quantum-math-lab/results/ole/q14_ole_vs_delta2_benchmark.md`
- bridge rule: `.gpd/phases/01/ole_small_delta_bridge.md`
- execution handoff: `.gpd/phases/01/q14_phase2_handoff.md`

Fits use the exact branch means from the OLE artifact only. The `perturbed_echo` baseline is **excluded** from every fit because it is a full-kick state-return reference, not a small-`delta` OLE datum.

## Fit Model

For each depth and branch, fit

$$
F_\delta(Z_0) = b_0 + b_2 \delta^2
$$

on three nested windows:

- Window A: `delta <= 0.30`
- Window B: `delta <= 0.20`
- Window C: `delta <= 0.10`

The Phase 1 target is

$$
b_0 \to 1,
\qquad
b_2 \to -\kappa/2.
$$

## Overlap Branch: `G = X_0`

| depth | target slope `-kappa/2` | `b0 @ 0.30` | `b2 @ 0.30` | `b0 @ 0.20` | `b2 @ 0.20` | `b0 @ 0.10` | `b2 @ 0.10` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | -1.981336 | 0.999586 | -1.926716 | 0.999901 | -1.956231 | 0.999994 | -1.974783 |
| 2 | -1.171643 | 0.999755 | -1.139344 | 0.999941 | -1.156797 | 0.999996 | -1.167768 |
| 3 | -0.955992 | 0.999800 | -0.929638 | 0.999952 | -0.943879 | 0.999997 | -0.952830 |
| 4 | -1.288917 | 0.999731 | -1.253385 | 0.999935 | -1.272586 | 0.999996 | -1.284654 |

### Overlap verdict

- **PASS:** the intercept stays close to `1` on every window and every depth.
- Worst intercept deviation from `1` across depths:
  - Window A (`delta <= 0.30`): `4.14e-4`
  - Window B (`delta <= 0.20`): `9.94e-5`
  - Window C (`delta <= 0.10`): `6.33e-6`
- Worst relative slope error versus `-kappa/2` across depths:
  - Window A (`delta <= 0.30`): `2.76%`
  - Window B (`delta <= 0.20`): `1.27%`
  - Window C (`delta <= 0.10`): `0.33%`

### Overlap interpretation

The overlap branch behaves exactly as the small-`delta` story predicted:

- the fitted intercept converges rapidly to `1` as the window shrinks
- the fitted slope converges rapidly to `-kappa/2`
- the widest Window A is already usable as an overview panel, but Window C is the cleanest validation window

For downstream wording, it is fair to say:

- the q14 overlap branch **supports** the small-`delta` OLE interpretation on all three declared windows
- the preferred quoted fit window for coefficient statements is `delta <= 0.10`
- `delta <= 0.20` is still acceptable as a broader presentation window

## Disjoint Control Branch: `G = X_10`

| depth | target slope `-kappa/2` | `b0 @ 0.30` | `b2 @ 0.30` | `b0 @ 0.20` | `b2 @ 0.20` | `b0 @ 0.10` | `b2 @ 0.10` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | -0.000000 | 1.000000 | 0.000000 | 1.000000 | 0.000000 | 1.000000 | 0.000000 |
| 2 | -0.000000 | 1.000000 | 0.000000 | 1.000000 | 0.000000 | 1.000000 | 0.000000 |
| 3 | -0.000000 | 1.000000 | 0.000000 | 1.000000 | 0.000000 | 1.000000 | 0.000000 |
| 4 | -0.000000 | 1.000000 | 0.000000 | 1.000000 | 0.000000 | 1.000000 | 0.000000 |

### Disjoint verdict

- **PASS EXACTLY:** the disjoint branch stays at intercept `1` and slope `0` to machine precision on every declared window.
- This is not just "flatter than overlap." It is the exact locality control promised by the active light-cone argument.
- Any materially non-flat `X_10` result on this active q14 manifest should be treated as an implementation failure, not as a successful physics observation.

## Branch-Level Acceptance Decision

- **Overlap branch:** accepted as a valid small-`delta` OLE onset on the active q14 benchmark family.
- **Disjoint branch:** accepted as an exact flat control on the active q14 benchmark family.
- **Baseline exclusion:** the `perturbed_echo` reference remains outside the quadratic fit by design and by contract.

## What Phase 2 Validated

Phase 2 validated all of the following:

- the exact q14 `F_delta(Z_0)` artifact exists on the active manifest
- the benchmark report keeps OLE and `perturbed_echo` semantics separate
- the overlap branch shows stable quadratic onset under shrinking windows
- the disjoint branch is an exact flat locality control on the active manifest

## What Phase 2 Did Not Validate

Phase 2 did **not** validate:

- a hardware estimator for OLE
- a full-80q global OLE quantity
- any claim that the existing hardware `perturbed_echo` outputs are already OLE measurements
- any equivalence between the baseline point and the fitted small-`delta` curve
