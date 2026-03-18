# Phase 2: q14 Exact Benchmark - Research

**Researched:** 2026-03-18
**Domain:** quantum information scrambling / operator Loschmidt echoes / exact Pauli propagation
**Depth:** standard
**Confidence:** HIGH

<user_constraints>

## User Constraints (from approved project contract and Phase 1 lock)

No phase-local CONTEXT.md exists. Use the approved project contract, the Phase 1 lock, and the active q14 manifest as the binding constraints.

### Locked Inputs

- Stay centered on the existing q14/q80 workflow.
- Keep the active q14 exact-short manifest unchanged for the first benchmark.
- Use the fixed Phase 1 choices: `P = Z_0`, overlap `G = X_0`, disjoint control `G = X_10`.
- Report the first exact benchmark as `F_delta(P)` with `f_delta(O) = 2^-14 F_delta(P)` carried explicitly as the normalized translation.
- Keep `perturbed_echo` only as a baseline comparison, not as the OLE quantity.
- Keep the hardware-ready and q80 subset/full guardrails visible, but do not let Phase 2 turn into a Phase 3 protocol rewrite.

### Agent's Discretion

- Choose the exact computational route as long as it preserves the manifest, the Phase 1 observable/generator lock, and the exact-small-delta contract.
- Decide whether the implementation should extend the current scrambling script or add a dedicated exact OLE script.
- Choose the small-delta reporting grid and nested fit windows as long as they are explicit and testable.

### Deferred Ideas (OUT OF SCOPE)

- A Phase 2 hardware estimator implementation.
- Any attempt to turn the q80 subset story into a full-q80 global OLE claim.
- A dense-operator rewrite of the current codebase.
- A randomized-measurement fallback as the primary path before the direct fixed-observable bridge is tried.

</user_constraints>

<research_summary>

## Summary

Phase 2 is an exact-computation phase, not a broadening phase. The core problem is no longer the formal definition of the observable; Phase 1 already fixed that. The Phase 2 problem is computational: how to evaluate the q14 infinite-temperature fixed-observable OLE exactly on the active manifest without constructing dense `2^14 x 2^14` operators or a doubled 28-qubit Choi state.

The best route is an exact sparse-Pauli propagation method specialized to the current circuit family. Starting from `P = Z_0`, the brickwork `RX/RZ/CZ` circuit propagates the operator only inside a narrow light cone. Because the active q14 benchmark uses depths `1,2,3,4`, the evolved operator remains sparse enough to track exactly as a Pauli expansion rather than as a dense matrix.

For the locked local generator family `G = X_q`, the exact OLE curve is then determined only by the Hilbert-Schmidt weight of the evolved operator on Pauli strings that anti-commute with `X_q` at the kick qubit. This makes the whole q14 benchmark exact, cheap, and directly tied to the Phase 1 small-delta bridge:

```text
F_delta(P; U, X_q) = 1 - (1 - cos(2 delta)) w_anti(q),
kappa_q(P; U) = 4 w_anti(q).
```

That route preserves the current q14 seeds/depths, keeps the baseline intact, and avoids both semantic and numerical drift.

**Primary recommendation:** plan Phase 2 around a dedicated exact OLE script that reuses the existing brickwork circuit family and manifest settings, computes the sparse evolved-Pauli expansion exactly, emits q14 overlap/disjoint data, and then feeds a separate benchmark report plus a small-delta validation note.

</research_summary>

<literature_landscape>

## Phase 2 Anchor Set

### Prior Artifacts That Must Constrain the Phase

| Anchor | Coverage | Why It Matters |
| ------ | -------- | -------------- |
| `.gpd/phases/01/ole_formalism_lock.md` | fixed observable/generator lock | Prevents Phase 2 from reopening the observable semantics |
| `.gpd/phases/01/ole_small_delta_bridge.md` | exact small-delta formula | Supplies the coefficient structure and intercept rule |
| `.gpd/phases/01/q14_phase2_handoff.md` | benchmark contract | Freezes the comparison rules, fit checks, and hardware/q80 guardrails |
| `files/quantum-math-lab/benchmarks/q14_only_manifest.json` | active task family | Fixes qubits, depths, trials, seed, and benchmark continuity |
| `files/quantum-math-lab/results/benchmark/classical/black_hole_scrambling_q14_exact_short.json` | active baseline artifact | Gives the exact `perturbed_echo` comparison target |
| `files/quantum-math-lab/qiskit_black_hole_scrambling.py` | current exact baseline semantics | Reuses the brickwork circuit family and seed discipline |
| `STATUS.md` | project claim discipline | Keeps Phase 2 from overclaiming beyond the q14 bridge |
| `files/quantum-math-lab/hardware_advantage_protocol.md` | hardware continuity | Keeps the future hardware path honest without turning it into a Phase 2 deliverable |
| `files/quantum-math-lab/results/hardware/summary/levelb_evidence_report.md` | q80 subset/full guardrail | Preserves the later subset/full split |

### External Theory Anchor

| Source | Use In Phase 2 |
| ------ | -------------- |
| Algorithmiq OLE theory note | Supplies the fixed-observable OLE definition and the small-delta commutator bridge |

### Practical Reading of the Theory For This Phase

Phase 2 does not need more symbolic derivation. It needs a computational realization of the already-approved Pauli-specialized bridge. The theory note matters here only insofar as it fixes what quantity the code must compute and what the near-zero fit is allowed to mean.

</literature_landscape>

<methods_and_approaches>

## Exact Computation Routes Considered

| Route | Exact? | Practical at q14? | Verdict |
| ----- | ------ | ----------------- | ------- |
| Dense `Operator(U Z_0 U^dagger)` construction | yes | no; `2^14 x 2^14` dense operators are too large and unnecessary | Reject |
| Doubled-state / Choi-state evaluation on `2n = 28` qubits | yes | no; doubled statevector memory is too expensive for a routine benchmark path | Reject |
| Average over all `2^14` computational basis states | yes | too slow for the active manifest | Reject |
| Exact sparse-Pauli propagation inside the brickwork light cone | yes | yes; the active depths stay local and sparse | Recommended |

## Recommended Exact Estimator

### Step 1: Propagate the fixed observable as a Pauli expansion

Start from `P = Z_0` and conjugate it gate by gate through the exact brickwork scrambler:

- `RX(theta)` rotates the local `Y/Z` sector on one qubit
- `RZ(phi)` rotates the local `X/Y` sector on one qubit
- `CZ` spreads support only across one nearest-neighbor edge and keeps the representation in the Pauli basis

This keeps the operator exact while avoiding dense matrices.

### Step 2: Group terms by local commutation class at the kick qubit

Write

```text
A_P(U) = sum_s c_s P_s
```

with Pauli strings `P_s` orthonormal under `2^-n Tr(P_s P_t) = delta_st`.

For a kick `G = X_q`, a Pauli string on qubit `q`:

- commutes with `X_q` if its local factor is `I` or `X`
- anti-commutes with `X_q` if its local factor is `Y` or `Z`

Define

```text
w_anti(q) = sum_{s : P_s(q) in {Y, Z}} |c_s|^2.
```

Then

```text
F_delta(P; U, X_q) = 1 - (1 - cos(2 delta)) w_anti(q),
kappa_q(P; U) = 4 w_anti(q).
```

This is exact for the Phase 1 Pauli-specialized branch and automatically preserves `F_0 = 1`.

### Step 3: Report the normalized translation

Once `F_delta(P)` is known, the Phase 1 translation is immediate:

```text
f_delta(O) = 2^-14 F_delta(P),  with  O = Z_0 / sqrt(2^14).
```

### Step 4: Compare to the existing baseline without renaming it

The current q14 baseline remains

```text
perturbed_echo = |<0...0| U^dagger X_q U |0...0>|^2.
```

It should be compared as a same-family full-kick state-return reference, not as the OLE curve itself.

## Implementation Strategy

| Choice | Recommendation | Why |
| ------ | -------------- | --- |
| Where to implement exact OLE | add a dedicated `qiskit_black_hole_ole_exact.py` script | Preserves the validated baseline script and avoids destabilizing hardware code paths |
| How to reuse current workflow | import or mirror only the brickwork/seed logic from `qiskit_black_hole_scrambling.py` | Keeps manifest continuity without a broad refactor |
| How to build the report | separate analysis/report script | Keeps computation and presentation concerns separated |
| How to express the baseline comparison | juxtapose or side-panel if needed | Avoids crushing the small-delta axis with the full-kick baseline point |

</methods_and_approaches>

<known_results>

## Known Results and Feasibility Checks

### Already Established by Phase 1

| Result | Value / Meaning | Confidence |
| ------ | --------------- | ---------- |
| overlap branch | `P = Z_0`, `G = X_0` | HIGH |
| disjoint control | `P = Z_0`, `G = X_10` | HIGH |
| report-level quantity | plot `F_delta(P)` and carry `f_delta(O) = 2^-14 F_delta(P)` | HIGH |
| depth-0 limits | overlap `kappa = 4`, disjoint `kappa = 0`, overlap `F_delta = cos(2 delta)` | HIGH |

### Local Feasibility Probe on the Active Gate Family

A quick exact propagation probe on the current `RX/RZ/CZ` brickwork family shows that the evolved Pauli stays sparse for the active q14 depths:

| Depth | Nonzero Pauli Terms in `A_P(U)` |
| ----- | ------------------------------- |
| 1 | 3 |
| 2 | 12 |
| 3 | 39 |
| 4 | 195 |

These counts were stable across the active three-trial manifest seed pattern. This is the strongest practical argument for the sparse-Pauli route.

### Consequence of the Depth-4 Light Cone

Because the observable starts at qubit `0` and the circuit spreads support only locally, the active depths `1..4` do not reach qubit `10`. Therefore the chosen disjoint control `G = X_10` should remain exactly flat on the full active q14 manifest:

```text
w_anti(q=10) = 0,
kappa_{X_10}(Z_0; U) = 0,
F_delta(Z_0; U, X_10) = 1
```

for every active q14 depth and seed.

This is better than a merely "small" control. It is an exact implementation check. Any non-flat q10 branch in Phase 2 is a bug, not a physics effect.

### Expected Structure of the Overlap Branch

The overlap branch `G = X_0` remains nontrivial at every active depth, but it is still exact and cheap to compute because only the local anti-commuting weight on qubit `0` matters once the Pauli expansion is known.

</known_results>

<dont_rederive>

## Don't Re-derive

| Problem | Don't Do This | Use Instead | Why |
| ------- | ------------- | ----------- | --- |
| q14 task family | rebuild the benchmark settings from prose notes | `q14_only_manifest.json` | The manifest already freezes the active task family |
| Phase 1 normalization | re-open the intercept choice in code comments or captions | `.gpd/phases/01/ole_small_delta_bridge.md` | The bridge already fixed the report-level quantity |
| exact baseline semantics | infer the baseline only from project docs | `qiskit_black_hole_scrambling.py` and the q14 exact JSON artifact | The code and artifact are the real comparison anchors |
| hardware/q80 story | turn Phase 2 into a hardware-protocol rewrite | `hardware_advantage_protocol.md`, `levelb_evidence_report.md` | Phase 2 only needs carry-forward discipline |

</dont_rederive>

<common_pitfalls>

## Common Pitfalls

### Pitfall 1: Dense-operator temptation

**What goes wrong:** Phase 2 falls back to dense matrices because q14 sounds "small enough".
**Why it happens:** `14` qubits feels modest, but dense operator objects scale as `4^14`.
**How to avoid:** Use sparse Pauli propagation only.
**Warning sign:** Code constructs dense `Operator` objects for the full evolved observable.

### Pitfall 2: Computing a state expectation instead of an infinite-temperature trace

**What goes wrong:** The code evaluates a pure-state expectation value and calls it OLE.
**Why it happens:** The existing baseline is a state-return quantity and looks operationally similar.
**How to avoid:** Keep the exact Pauli-basis Hilbert-Schmidt calculation explicit in the data schema.
**Warning sign:** Output fields contain only `|0...0>` amplitudes or probabilities with no operator-basis weight ledger.

### Pitfall 3: Losing the exact disjoint control

**What goes wrong:** The q10 branch is treated as only an approximate control.
**Why it happens:** The code forgets the depth-limited light cone and assumes late-time spreading at all depths.
**How to avoid:** Treat `X_10` flatness as an exact active-manifest acceptance test.
**Warning sign:** The report describes nonzero q10 onset as "interesting" instead of as a likely bug.

### Pitfall 4: Forcing the full-kick baseline onto the small-delta axis

**What goes wrong:** The report places the `perturbed_echo` full-kick point on the same narrow `delta^2` axis and ruins readability.
**Why it happens:** "Overlay" is interpreted too literally.
**How to avoid:** Juxtapose if needed: small-delta panels plus a separate full-kick baseline table or side marker.
**Warning sign:** The small-delta onset becomes visually unreadable because the baseline reference sits at `(pi/2)^2`.

</common_pitfalls>

<key_derivations>

## Key Exact Formulas For Execution

### Sparse Pauli decomposition

```text
A_P(U) = U P U^dagger = sum_s c_s P_s,
sum_s |c_s|^2 = 1
```

for the report-level Pauli observable `P = Z_0`.

### Exact local-X kick formula

For `G = X_q`,

```text
F_delta(P; U, X_q) = 2^-n Tr(A_P e^{i delta X_q} A_P e^{-i delta X_q})
                   = 1 - (1 - cos(2 delta)) w_anti(q)
```

with

```text
w_anti(q) = sum_{s : P_s(q) in {Y, Z}} |c_s|^2.
```

### Small-delta coefficient

```text
kappa_q(P; U) = 4 w_anti(q),
F_delta(P; U, X_q) = 1 - (delta^2 / 2) kappa_q(P; U) + O(delta^4).
```

### Normalized translation

```text
O = P / sqrt(2^14),
f_delta(O; U, X_q) = 2^-14 F_delta(P; U, X_q).
```

### Exact disjoint-control rule on the active manifest

```text
q = 10 lies outside the depth-4 light cone of Z_0,
so F_delta(Z_0; U, X_10) = 1 exactly for the active q14 phase.
```

</key_derivations>
