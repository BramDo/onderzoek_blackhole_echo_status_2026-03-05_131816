# Known Pitfalls Research

**Domain:** quantum information scrambling and fixed-observable echo benchmarks
**Researched:** 2026-03-17
**Confidence:** HIGH

## Critical Pitfalls

### Pitfall 1: Relabeling `perturbed_echo` as OLE

**What goes wrong:**
The project appears to make rapid progress by renaming the existing state-overlap observable as OLE, but no explicit fixed observable `O`, perturbation generator `G`, or `delta` sweep has actually been introduced.

**Why it happens:**
The current repo is already echo-based, so it is tempting to treat conceptual similarity as equivalence.

**How to avoid:**
Require an explicit OLE task definition with frozen `O`, `G`, `delta` values, normalization, and a separate output label before any benchmark is called OLE.

**Warning signs:**
Plots or summaries discuss OLE while the code still emits only `ideal_echo` / `perturbed_echo`, or there is no observable definition beyond "same as before".

**Phase to address:**
Phase 1 formalism lock and q14 exact implementation.

---

### Pitfall 2: Mistaking noisy decay for scrambling

**What goes wrong:**
A decreasing signal is interpreted as scrambling even though decoherence, readout error, or forward/backward mismatch could produce the same trend.

**Why it happens:**
Echo-like diagnostics are fragile, and literature explicitly warns that OTOC decay alone can produce false positives.

**How to avoid:**
Carry control benchmarks with the signal: overlap vs disjoint support, raw vs mitigated comparison, and at least one recovery-style or locality-based diagnostic.

**Warning signs:**
Signal decay persists but locality controls fail, or hardware drift changes the curve without corresponding exact/classical support.

**Phase to address:**
Phase 2 q14 benchmark validation and Phase 3 hardware-readiness checks.

---

### Pitfall 3: Treating q80 subset observables as full-system OLE

**What goes wrong:**
Subset observables are presented as though they already establish global 80q scrambling or full-system OLE.

**Why it happens:**
Subset signals are the only scalable large-system route in the current code, and they can look compelling enough to invite overstatement.

**How to avoid:**
Name subset observables explicitly, freeze the subset register `S`, and state in every summary that q80 evidence is local/subset-only unless a separate full-system proxy is derived and validated.

**Warning signs:**
Documentation drops the word "subset", or q80 plots are compared directly with q14 exact global quantities without a caveat.

**Phase to address:**
Phase 3 q80 subset extension and all write-up phases.

---

### Pitfall 4: Using approximation ladders without convergence checks

**What goes wrong:**
A low-order randomized-measurement approximation, a narrow subset observable, or a single fixed Pauli is treated as representative without demonstrating stability or locality relevance.

**Why it happens:**
Hardware-friendly approximations are cheaper, and the first visually clean curve can look decisive.

**How to avoid:**
Use convergence or robustness checks appropriate to the approximation: extra random-unitary samples, support-variation checks, overlap/disjoint controls, or multiple subset placements.

**Warning signs:**
Conclusions depend on one observable choice, one subset, or one `delta` point.

**Phase to address:**
Phase 2 q14 benchmark and Phase 3 q80 extension.

---

### Pitfall 5: Leaving the small-`delta` regime without noticing

**What goes wrong:**
Higher-order terms contaminate the benchmark, but the result is still interpreted as a clean quadratic OLE onset.

**Why it happens:**
The first interesting-looking points often sit at `delta` values that are already too large for the asymptotic formula.

**How to avoid:**
Fit several shrinking `delta` windows and require coefficient stability before claiming agreement with the small-`delta` theory.

**Warning signs:**
The fitted quadratic coefficient drifts strongly as points are removed from the largest-`delta` end.

**Phase to address:**
Phase 2 q14 exact benchmark.

---

### Pitfall 6: Runtime metric drift

**What goes wrong:**
Hardware advantage language drifts back in, or IBM `quantum_seconds` gets mixed with local wall-clock timing in a way that invalidates comparisons.

**Why it happens:**
The repo contains both historical and current benchmark narratives, and the runtime definition changed the practical claim boundary.

**How to avoid:**
Keep the manifest-fixed task and metric definition attached to every runtime statement, and treat new OLE work as extending the current q14-only campaign rather than reopening the historical Level-C claim.

**Warning signs:**
A summary compares `26 qs` to unrelated local orchestration time, or reintroduces multi-size advantage language without resolving q12.

**Phase to address:**
All benchmark-reporting phases.

## Approximation Shortcuts

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
| -------- | ----------------- | -------------- | --------------- |
| Reuse the current `perturbed_echo` circuit without explicit `O` bookkeeping | fast first plot | fake OLE progress | never |
| Use one `delta` point instead of a sweep | minimal compute | no quadratic-onset evidence | never for the first deliverable |
| Use one q80 subset and stop | simplest hardware extension | cannot separate local signal from subset-specific artifact | only for pilot debugging, not for claims |
| Ignore overlap/disjoint support comparisons | fewer runs | weak interpretation of locality and scrambling sensitivity | only during very early implementation debugging |

## Convention Traps

| Convention Issue | Common Mistake | Correct Approach |
| ---------------- | -------------- | ---------------- |
| `O(t)` picture choice | mixing `U O U^\dagger` and `U^\dagger O U` across notes and code | freeze one convention in `.gpd/CONVENTIONS.md` before implementation |
| Observable normalization | forgetting the `Tr(O^2)=1` convention when moving from single Pauli to subset Pauli strings | normalize the chosen observable explicitly and record it once |
| Perturbation labeling | using `V` both for observable and perturbation | reserve `O` for observable and `V_delta` for the perturbation unitary |
| Subset notation | treating subset indices as implementation details | include subset support `S` in filenames, plots, and summaries |

## Numerical Traps

| Trap | Symptoms | Prevention | When It Breaks |
| ---- | -------- | ---------- | -------------- |
| Too-large `delta` in the onset fit | non-quadratic curvature but a quadratic claim | shrink the fit window until the coefficient stabilizes | first q14 benchmark |
| Shot noise masquerading as physics | unstable fit coefficients or support-ordering reversals | repeat shots/jobs and track uncertainties | hardware runs with weak signals |
| Ill-conditioned subset mitigation | mitigated values jump outside plausible ranges or flip ranking unexpectedly | keep subset size moderate and compare raw vs mitigated on identical data | large q80 subsets |
| Backend/calibration drift across days | inconsistent curves under nominally same settings | freeze backend/day windows when comparing and log metadata | multi-day hardware claims |

## Interpretation Mistakes

| Mistake | Risk | Prevention |
| ------- | ---- | ---------- |
| "Any decay means scrambling" | confuses noise with scrambling | include locality and recovery-style controls |
| "Subset signal means full 80q scrambling" | overclaiming beyond what is measured | keep subset wording explicit everywhere |
| "Agreement with `perturbed_echo` proves OLE" | circular reasoning | require an independently defined fixed observable and separate label |
| "Exact q14 behavior will transfer unchanged to q80" | extrapolation beyond validated regime | treat q80 as extension work with separate feasibility checks |

## Publication Pitfalls

| Pitfall | Impact | Better Approach |
| ------- | ------ | --------------- |
| Claiming hardware advantage from the new OLE work prematurely | credibility loss and inconsistency with the repo's current status | keep language at the q14 benchmark / hardware-ready level unless the runtime criteria are re-satisfied |
| Citing the Algorithmiq note as if it settles all benchmarking questions | weak external support | pair it with peer-reviewed OTOC/benchmarking papers |
| Hiding subset/full distinctions in figure captions | overstatement by presentation | state subset support and limits directly in captions and summaries |

## "Looks Correct But Is Not" Checklist

- [ ] **q14 OLE benchmark:** often missing an explicit fixed observable definition; verify `O`, normalization, and support are written down.
- [ ] **Small-`delta` agreement:** often missing fit-window stability; verify the coefficient is stable under removing the largest `delta` points.
- [ ] **Hardware-readiness note:** often missing same-task comparability; verify the hardware path matches the benchmarked observable semantics.
- [ ] **q80 extension:** often missing subset disclaimers; verify no wording implies global 80q overlap or fidelity.

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
| ------- | ------------- | -------------- |
| relabeling `perturbed_echo` as OLE | MEDIUM | back out the claim, define `O/G/delta` explicitly, regenerate plots with correct labels |
| noisy decay misread as scrambling | HIGH | add locality/recovery controls and rerun the critical comparisons |
| subset overclaiming | LOW | relabel artifacts and tighten the write-up immediately |
| broken small-`delta` regime | MEDIUM | rerun with smaller `delta` values and narrower fit windows |
| runtime metric drift | LOW | restate the metric, task definition, and campaign boundary in the affected summaries |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
| ------- | ---------------- | ------------ |
| relabeling `perturbed_echo` as OLE | Phase 1 formalism lock | explicit convention and task-definition review |
| noisy decay misread as scrambling | Phase 2 q14 benchmark and Phase 3 hardware checks | locality / control comparisons present |
| subset overclaiming | Phase 3 q80 extension | summary language and captions audited |
| approximation without convergence | Phase 2 and Phase 3 | robustness checks recorded in artifacts |
| small-`delta` regime drift | Phase 2 | fit-window stability check |
| runtime metric drift | every reporting phase | manifest and metric references attached |

## Sources

- Harris, Yan, Sinitsyn (`2110.12355v2`) -- false-positive risk from noisy OTOC decay.
- Yoshida, Yao (`1803.10772v1`) -- scrambling versus decoherence verification logic.
- Swingle, Yunger Halpern (`1802.01587v2`) -- imperfect reversal and renormalization.
- Vermersch et al. (`1807.09087v2`) and Joshi et al. (`2001.02176v2`) -- approximation/convergence issues in randomized protocols.
- `STATUS.md` and `hardware_advantage_protocol.md` -- current project-specific claim and metric traps.
- `levelb_evidence_report.md` -- q80 subset-locality interpretation boundary.
