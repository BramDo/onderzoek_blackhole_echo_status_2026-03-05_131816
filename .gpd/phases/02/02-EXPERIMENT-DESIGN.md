# Phase 2: q14 Exact Benchmark - Experiment Design

**Designed:** 2026-03-18
**Phase:** 02
**Purpose:** define the exact computational protocol for the q14 OLE benchmark before execution starts

## Objective

Produce exact q14 `F_delta(Z_0)` onset data on the active manifest, compare it against the current q14 `perturbed_echo` baseline, and validate that the overlap branch obeys the promised small-delta interpretation while the disjoint control stays exactly flat.

## Locked Inputs

- qubits: `14`
- depths: `1, 2, 3, 4`
- trials per depth: `3`
- master seed: `424242`
- observable: `P = Z_0`
- overlap generator: `G = X_0`
- disjoint generator: `G = X_10`
- report-level quantity: `F_delta(P)`
- normalized translation: `f_delta(O) = 2^-14 F_delta(P)` with `O = Z_0 / sqrt(2^14)`

## Estimator Design

### Core method

Use exact sparse Pauli propagation through the existing `RX/RZ/CZ` brickwork circuit:

1. build the same random scrambler `U` used by the current q14 exact-short workflow
2. propagate `P = Z_0` through `U` as a sparse Pauli expansion
3. compute the anti-commuting local weight `w_anti(q)` for `q = 0` and `q = 10`
4. derive

```text
F_delta(Z_0; U, X_q) = 1 - (1 - cos(2 delta)) w_anti(q)
kappa_q = 4 w_anti(q)
```

5. emit both `F_delta` and `f_delta`

### Why this is the right method

- exact on the active q14 phase
- preserves the Phase 1 OLE semantics
- avoids dense `4^n` operator objects
- makes the q10 disjoint branch an exact flat control on the full active manifest

## Reporting Grid

Use one declared small-delta grid for the benchmark artifact:

```text
delta = [0.000, 0.025, 0.050, 0.075, 0.100, 0.125, 0.150, 0.200, 0.250, 0.300]
```

Derived `delta^2` values are the x-axis for the OLE onset panels.

This grid is cheap because the estimator is analytic once `w_anti(q)` is known, and it gives enough points to test shrinking fit windows without cluttering the report.

## Branches To Compute

### Overlap branch

- generator: `G = X_0`
- expectation: nontrivial onset with trial/depth-dependent `kappa_0`

### Disjoint control branch

- generator: `G = X_10`
- expectation on active manifest: `F_delta = 1` exactly for every depth/trial because qubit `10` is outside the depth-4 light cone from `Z_0`

If the disjoint branch is not flat, fail the implementation and debug before writing the benchmark report.

## Output Schema

Write one exact benchmark JSON artifact containing:

- manifest metadata: qubits, depths, trials, seed, observable, generators, delta grid
- per-depth aggregates and per-trial samples
- for each branch:
  - `term_count`
  - `hilbert_schmidt_norm`
  - `w_anti`
  - `kappa`
  - `F_delta` values on the declared delta grid
  - `f_delta` values on the declared delta grid

## Baseline Comparison Design

Use the current exact-short q14 baseline artifact as a same-family comparison anchor:

- baseline artifact: `files/quantum-math-lab/results/benchmark/classical/black_hole_scrambling_q14_exact_short.json`
- baseline metric: `perturbed_echo`
- interpretation: full local `X_q` kick / state-return benchmark

### Presentation rule

Do not force the full-kick baseline onto the same narrow small-delta axis if it damages readability. The report may use:

- small-delta `delta^2` panels for OLE onset
- a side table or side marker for the full-kick `perturbed_echo` baseline

That still satisfies the Phase 2 comparison contract because the roadmap explicitly allows overlay or juxtaposition.

## Fit Protocol

Fit the overlap branch in `x = delta^2` with

```text
F_delta = b0 + b2 x
```

on at least three shrinking windows:

- Window A: `delta <= 0.30`
- Window B: `delta <= 0.20`
- Window C: `delta <= 0.10`

For the disjoint branch, report the same windows but expect `b0 = 1` and `b2 = 0` up to numerical roundoff.

## Acceptance Checks

### Exactness checks

- Hilbert-Schmidt norm of the propagated operator remains `1` within numerical tolerance.
- Depth-0 sanity check reproduces overlap `kappa = 4`, disjoint `kappa = 0`, and overlap `F_delta = cos(2 delta)`.
- Active-manifest disjoint branch remains exactly flat for `q = 10`.

### Small-delta checks

- overlap-branch fitted intercept stays close to `1` as the fit window shrinks
- overlap-branch slope stabilizes across shrinking windows
- disjoint branch stays at intercept `1` and slope `0`
- no fit includes the full-kick `perturbed_echo` baseline point

## Expected Runtime / Complexity

The key feasibility fact is that the evolved operator remains sparse on the active manifest. A local probe on the current gate family gave term counts:

- depth 1: `3`
- depth 2: `12`
- depth 3: `39`
- depth 4: `195`

That is small enough that exact q14 execution should be routine.

## Failure Triggers

Stop and debug rather than writing the benchmark artifact if any of the following happens:

- the implementation falls back to dense full-operator matrices
- the q10 disjoint branch is not exactly flat
- Hilbert-Schmidt norm drifts materially from `1`
- the benchmark report starts describing `perturbed_echo` as if it were itself OLE

## Phase 2 Deliverables This Design Supports

- exact q14 OLE JSON artifact
- q14 `delta^2` benchmark report against the existing baseline
- small-delta validation note
- Phase 3 handoff note with hardware/q80 guardrails
