# Phase 1: Formal OLE Bridge - Research

**Researched:** 2026-03-17
**Domain:** quantum information scrambling / operator echoes / circuit benchmarks
**Depth:** standard
**Confidence:** MEDIUM

<user_constraints>

## User Constraints (from approved project contract)

No phase-local CONTEXT.md exists. Use the approved project contract and initialization decisions as the locked constraints for planning.

### Locked Decisions

- Stay centered on the existing q14/q80 workflow.
- Keep both classical and hardware-ready paths visible.
- Use fixed observables first; do not start with an observable-family search.
- Keep q80 subset and possible full-q80 directions both in sight.
- Treat `perturbed_echo` only as a baseline, not as OLE itself.

### Agent's Discretion

- Choose the first fixed local observable and generator pair if it preserves compatibility with the current scripts and manifest.
- Decide whether the reported q14 curve should use a unit-intercept Pauli convention or an explicitly rescaled Hilbert-Schmidt-normalized convention, as long as the choice is written down and testable.
- Decide how much of the Phase 3 hardware story must already be carried into the Phase 2 handoff note.

### Deferred Ideas (OUT OF SCOPE)

- Full 80q global OLE claim or proxy as a Phase 1 deliverable.
- Randomized-measurement fallback as the primary path before the echo-style bridge is tried.
- Fresh observable-family search.

</user_constraints>

<research_summary>

## Summary

Phase 1 is not a literature-broadening step; it is a contract-narrowing step. The repo already has a stable q14 exact-short `perturbed_echo` baseline, q80 subset-observable hardware evidence, and a fixed local X-kick implementation. The missing piece is a phase-local formalism lock that makes the first OLE benchmark explicit enough that Phase 2 can execute without semantic drift.

The decisive technical issue is normalization and picture choice. With the currently written form `2^-n Tr(U O U^dagger V_delta^dagger U O U^dagger V_delta)`, a Hilbert-Schmidt-normalized `O` satisfying `Tr(O^2)=1` gives `f_delta(0)=2^-n`, not `1`. The common unit-intercept infinite-temperature convention instead uses an unnormalized Pauli operator `P` with `P^2 = I`, or equivalently reports `2^n f_delta(O)` when `O = P / sqrt(2^n)`. Phase 1 should resolve this explicitly instead of carrying an inconsistent intercept into the q14 fit.

The most repo-compatible default is a Pauli-specialized first bridge: use the current local X-kick semantics as the generator family and freeze a single-site Pauli-Z observable. The overlap benchmark can use `P = Z_0`, `G = X_0`, and the disjoint control can use `P = Z_0`, `G = X_10`, matching the existing locality language while staying within q14.

**Primary recommendation:** Plan Phase 1 around a formalism lock that (1) freezes `P = Z_0`, overlap `G = X_0`, disjoint control `G = X_10`, and support labels, and (2) writes the small-`delta` bridge in one picture with an explicit unit-intercept versus Hilbert-Schmidt-normalized translation.

</research_summary>

<literature_landscape>

## Literature Landscape

### Foundational Papers

| Paper | Authors | Year | Key Result | Relevance |
| ----- | ------- | ---- | ---------- | --------- |
| Reversibility and the Arrow of Time in a Quantum System | Yan, Cincio, Zurek | 2019 | Loschmidt echo / OTOC bridge in a controlled scrambling setting | Primary bridge from echo language to commutator growth |
| Toward a Statistical Mechanics of Commuting Observables | Zanardi | 2021 | Observable/subalgebra viewpoint for operator growth and partial observables | Useful for honest subset-observable language |
| Benchmarking Quantum Information Scrambling | Harris, Yan, Sinitsyn | 2021 | Anti-butterfly control logic; decay alone is not enough | Important guardrail against false progress |
| Measuring the Operator Loschmidt Echo Without Ancilla Qubits | Kastner, Osterholz, Gross | 2024 | Echo-style operator measurement path without ancilla-heavy overhead | Supports a hardware-ready route close to the current repo |

### Recent Advances and Practical Alternatives

| Paper | Authors | Year | Key Result | Relevance |
| ----- | ------- | ---- | ---------- | --------- |
| Probing Scrambling Using Statistical Correlations Between Randomized Measurements | Vermersch et al. | 2018 | Randomized-measurement OTOC protocol | Backup route if reverse-evolution hardware mapping proves too brittle |
| Quantum Information Scrambling in a Superconducting Qutrit Processor | Joshi et al. | 2020 | Hardware scrambling diagnostic without idealized assumptions | Practical experimental benchmark for later phases |

### Project Anchors That Must Constrain Phase 1

| Anchor | Coverage | Best For |
| ------ | -------- | -------- |
| Algorithmiq OLE theory note | OLE definition, small-`delta` expansion, hardware framing | Formal operator definition and benchmark target |
| `STATUS.md` | Current q14-only claim language and q80 scope discipline | Preventing overclaiming and proxy relabeling |
| `q14_only_manifest.json` | Frozen q14 benchmark task family | Keeping Phase 2 tied to the active campaign |
| `levelb_evidence_report.md` | Existing q80 subset/locality evidence | Carrying the q80 subset/full split forward honestly |

### Notation Conventions Across Sources

| Quantity | Common convention A | Common convention B | Phase 1 implication | Candidate lock |
| -------- | ------------------- | ------------------- | ------------------- | -------------- |
| Heisenberg operator | `U^dagger O U` | `U O U^dagger` | Picture switches must be explicit | Freeze one defining picture and translate the other |
| Observable normalization | `Tr(P^2) = 2^n` for Pauli `P` | `Tr(O^2) = 1` for `O = P / sqrt(2^n)` | Intercept differs by `2^n` | Report both relation and chosen plotting convention |
| Perturbation unitary | `V_delta = exp(-i delta G)` | same, but with varying generator normalization | Generator choice must stay explicit | Reuse local X-generator family from current scripts |
| Reported curve | unit-intercept infinite-temperature correlator | Hilbert-Schmidt-normalized correlator with `2^-n` intercept | Fit target changes if this is silent | Freeze one report-level quantity before Phase 2 |

**Key notational hazards:** picture switching and normalization switching can make the same symbolic-looking `f_delta` mean different intercepts and different plotted quantities.

</literature_landscape>

<methods_and_approaches>

## Methods and Approaches

### Standard Analytical Methods

| Method | When to Use | Limitations | Key Reference |
| ------ | ----------- | ----------- | ------------- |
| Fixed-observable OLE definition with explicit normalization translation | Phase 1 formalism lock | Fails if normalization is left implicit | Algorithmiq OLE note |
| Small-`delta` commutator expansion | Build the `delta^2` benchmark target | Only valid inside a stable small-`delta` window | Algorithmiq OLE note; Yan-Cincio-Zurek |
| Depth-0 and support-overlap controls | Check that overlap and disjoint variants mean different things | Only a control, not the full scrambling story | Harris-Yan-Sinitsyn |
| Observable/subset language | Keep q80 subset work honest | Does not itself solve full-q80 scaling | Zanardi |

### Computational Tools

| Tool/Package | Version | Purpose | Why Standard |
| ------------ | ------- | ------- | ------------ |
| `qiskit_black_hole_scrambling.py` | current repo snapshot | Exact reference and current `perturbed_echo` definition | Active q14 task family already lives here |
| `qiskit_black_hole_hardware_runner.py` | current repo snapshot | Hardware-ready measurement path | Existing q14/q80 hardware architecture |
| `q14_only_manifest.json` | current campaign manifest | Frozen q14 benchmark parameters | Prevents task drift between baseline and OLE bridge |
| Qiskit `1.4.5` stack | recorded in repo artifacts | Local simulation and hardware interfaces | Current evidence trail already uses it |

### Supporting Tools

| Tool/Package | Version | Purpose | When to Use |
| ------------ | ------- | ------- | ----------- |
| `hardware_advantage_protocol.md` | repo document | Guardrail for hardware claims and subset rules | When writing the Phase 2 handoff and Phase 3 carry-forward note |
| `levelb_evidence_report.md` | repo artifact | Existing q80 subset/locality benchmark logic | When keeping q80 subset/full scope explicit |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
| ---------- | --------- | -------- |
| Echo-style OLE bridge | Randomized-measurement OTOC route | More hardware-friendly in some settings, but drifts away from the current repo semantics too early |
| Single-site Pauli lock | Broader observable-family search | More flexible, but violates the user's request for fixed observables first |
| q14 exact benchmark first | Immediate q80-only exploration | Keeps hardware scale visible but loses the exact reference gate |

**Installation / Setup:**

```bash
scripts/run-in-qiskit-venv.sh python files/quantum-math-lab/qiskit_black_hole_scrambling.py ...
scripts/run-in-qiskit-venv.sh python files/quantum-math-lab/qiskit_black_hole_hardware_runner.py ...
```

</methods_and_approaches>

<known_results>

## Known Results and Benchmarks

### Established Results

| Result | Value/Expression | Conditions | Source | Confidence |
| ------ | ---------------- | ---------- | ------ | ---------- |
| Active q14 benchmark observable is `perturbed_echo` | State-return quantity after `U`, local X kick, `U^dagger` | q14 exact-short campaign | `q14_only_manifest.json`; `qiskit_black_hole_scrambling.py` | HIGH |
| q80 evidence is subset-only, not global | Fixed subset observable with locality-sensitive behavior | Level-B hardware evidence | `STATUS.md`; `levelb_evidence_report.md` | HIGH |
| `P = Z_q` implies `Tr(P^2) = 2^n` | Unit-intercept OLE convention if used inside `2^-n Tr(...)` | Pauli-string observable | standard Pauli algebra | HIGH |
| `O = P / sqrt(2^n)` implies `Tr(O^2) = 1` | Same operator direction, but plot intercept shifts by `2^-n` | Hilbert-Schmidt-normalized observable | direct algebra | HIGH |

### Limiting Cases

| Limit | Expected Behavior | Expression | Source |
| ----- | ----------------- | ---------- | ------ |
| `delta -> 0` | Reported OLE curve reaches its intercept exactly | `F_0 = 1` for Pauli `P`; `f_0 = 2^-n` for `O = P / sqrt(2^n)` | direct algebra |
| `U = I` with disjoint support | Commutator term vanishes | `[X_10, Z_0] = 0` | direct Pauli algebra |
| `U = I` with overlap support | Commutator term is nonzero | `[X_0, Z_0] != 0` | direct Pauli algebra |
| `[G, U P U^dagger] = 0` | No quadratic decay at order `delta^2` | small-`delta` coefficient `= 0` | Algorithmiq OLE note |

### Numerical Benchmarks

| Quantity | Published / local value | Method Used | Parameters | Source |
| -------- | ----------------------- | ----------- | ---------- | ------ |
| q14 exact-short baseline | active classical reference artifact exists | exact statevector | q14, depths 1-4, perturb qubit 0 | `results/benchmark/classical/black_hole_scrambling_q14_exact_short.json` |
| q14 raw hardware benchmark | active three-day reproducibility trail exists | IBM Runtime Sampler | q14, depths 1-4, raw exact-short | `STATUS.md`; hardware day summaries |

**Key insight:** Phase 1 does not need new numerics to justify itself. It needs a formalism lock that turns the already-frozen q14 task family into a true fixed-observable OLE benchmark target.

</known_results>

<dont_rederive>

## Don't Re-derive

| Problem | Don't Derive From Scratch | Use Instead | Why |
| ------- | ------------------------- | ----------- | --- |
| Current q14 task family | Reconstruct the manifest informally from log files | `q14_only_manifest.json` | The manifest already freezes the exact-short benchmark gate |
| Existing `perturbed_echo` semantics | Infer it only from prose descriptions | `qiskit_black_hole_scrambling.py` and `README.md` | The code path is the actual baseline semantics |
| q80 subset hardware guardrails | Rebuild the full large-q evidence trail | `levelb_evidence_report.md` and `hardware_advantage_protocol.md` | Phase 1 only needs the scope guardrail, not a new q80 analysis |

**Key insight:** The error-prone part is not the physics of Pauli algebra; it is semantic drift between docs, formulas, and the existing benchmark scripts.

</dont_rederive>

<common_pitfalls>

## Common Pitfalls

### Pitfall 1: Normalization mismatch

**What goes wrong:** The note states `Tr(O^2) = 1` and keeps the `2^-n` prefactor, then still talks about a unit intercept near `1`.
**Why it happens:** The Pauli-operator and Hilbert-Schmidt-normalized conventions are mixed.
**How to avoid:** Write both conventions and freeze one report-level quantity.
**Warning signs:** The `delta = 0` limit cannot be stated cleanly in one line.

### Pitfall 2: Silent picture switch

**What goes wrong:** The derivation starts from `U O U^dagger` and quotes the commutator term in `U^dagger O U` language without translating.
**Why it happens:** Different sources pick different Heisenberg-picture conventions.
**How to avoid:** Introduce `A = U O U^dagger` or `A = U P U^dagger` once and keep every later formula in terms of that `A`.
**Warning signs:** The sign or location of `U` and `U^dagger` changes from one paragraph to the next.

### Pitfall 3: Relabeling `perturbed_echo` as OLE

**What goes wrong:** The existing state-return quantity is treated as if it were already the fixed-observable operator correlator.
**Why it happens:** Both use echo-style circuits and local perturbations.
**How to avoid:** Keep `perturbed_echo` only as a baseline overlay and always state explicit `P`/`O` and `G`.
**Warning signs:** A figure or note mentions only the baseline curve but not the fixed observable.

### Pitfall 4: Losing the q80 scope split

**What goes wrong:** Phase 1 notes speak as if subset-observable q80 work already answers the full-q80 question.
**Why it happens:** The hardware-ready path and the large-system scope note get conflated.
**How to avoid:** Carry the subset/full distinction into the Phase 2 handoff note.
**Warning signs:** The word "subset" disappears from q80 planning language.

</common_pitfalls>

<key_derivations>

## Key Derivations and Formulas

### Defining operator-space quantity

```text
# Source: project convention + Algorithmiq OLE note
Let d = 2^n and A_P = U P U^dagger.

F_delta(P) = d^-1 Tr(A_P V_delta^dagger A_P V_delta),
V_delta = exp(-i delta G).
```

**Valid when:** `P` is the explicit fixed observable used for the benchmark.
**Breaks down when:** `P` is left implicit or silently renormalized mid-derivation.

### Hilbert-Schmidt-normalized translation

```text
# Source: direct algebra
O = P / sqrt(d)

f_delta(O) = d^-1 Tr(U O U^dagger V_delta^dagger U O U^dagger V_delta)
           = d^-1 F_delta(P).
```

**Valid when:** `O` is exactly `P / sqrt(d)`.
**Breaks down when:** the note claims both `Tr(O^2)=1` and a unit intercept without the extra factor of `d`.

### Small-delta bridge

```text
# Source: Algorithmiq OLE note, expressed in the A_P = U P U^dagger picture
F_delta(P) = F_0(P)
           - (delta^2 / 2) d^-1 Tr([G, A_P][G, A_P]^dagger)
           + O(delta^3).
```

For Pauli `P`, `F_0(P) = 1`. For `O = P / sqrt(d)`, the same bridge can be reported as `f_delta(O) = d^-1 F_delta(P)`.

**Valid when:** the same picture and normalization are kept throughout the derivation.
**Breaks down when:** higher-order `delta` terms are not negligible or the observable definition changes across steps.

</key_derivations>

<open_questions>

## Open Questions

1. **Which report-level symbol should Phase 2 plot?**

   - What we know: `F_delta(P)` gives a unit intercept, while `f_delta(O)` with `Tr(O^2)=1` gives intercept `2^-n`.
   - What's unclear: which notation will create the cleanest benchmark figure without fighting existing project docs.
   - Recommendation: keep the Hilbert-Schmidt-normalized operator relation in the note, but plot the unit-intercept quantity and state the rescaling explicitly.

2. **Should the disjoint control use qubit `10` by default?**

   - What we know: the existing locality language already uses `0` versus `10`, and q14 includes qubits `0..13`.
   - What's unclear: whether a nearer disjoint site would simplify later hardware routing.
   - Recommendation: default to `10` for continuity unless script inspection exposes a concrete implementation cost.

3. **How much hardware path detail must Phase 1 write down?**

   - What we know: the user wants hardware readiness visible from the start.
   - What's unclear: whether a short carry-forward paragraph is enough, or whether Phase 1 should already draft a dedicated note.
   - Recommendation: include one explicit hardware-ready carry-forward section in the Phase 2 handoff note, but leave the full protocol note for Phase 3.

</open_questions>

<not_found>

## What Was NOT Found

- No existing repo artifact that already resolves the unit-intercept versus `Tr(O^2)=1` ambiguity for OLE.
- No existing code path that already computes fixed-observable OLE as distinct from `perturbed_echo`.
- No credible full-80q global OLE route in the current snapshot that would justify making it a Phase 1 deliverable.

</not_found>

<sources>

## Sources

### Primary (HIGH)

- Algorithmiq OLE theory note - fixed-observable definition, small-`delta` bridge, measurement framing.
- `STATUS.md` - current claim discipline and q80 subset guardrail.
- `files/quantum-math-lab/benchmarks/q14_only_manifest.json` - active q14 task definition.
- `files/quantum-math-lab/qiskit_black_hole_scrambling.py` - baseline semantics and current local X-kick implementation.
- `files/quantum-math-lab/hardware_advantage_protocol.md` - hardware claim guardrails and subset rules.

### Secondary (MEDIUM)

- Yan, Cincio, Zurek (`1903.02651v4`) - Loschmidt echo / OTOC bridge.
- Harris, Yan, Sinitsyn (`2110.12355v2`) - anti-butterfly controls.
- Zanardi (`2107.01102v3`) - observable/subalgebra scrambling language.
- Kastner, Osterholz, Gross (`2403.08670v1`) - ancilla-free backward-evolution measurement route.
- Vermersch et al. (`1807.09087v2`) and Joshi et al. (`2001.02176v2`) - randomized-measurement fallback literature.

### Tertiary (LOW - needs validation during execution)

- none

</sources>

<metadata>

## Metadata

**Research scope:**

- Physics subfield: quantum information scrambling and operator echoes
- Methods explored: formal operator definitions, small-`delta` expansion, benchmark-interface design
- Known results catalogued: q14 manifest lock, q80 subset guardrail, Pauli normalization identities
- Pitfalls: normalization mismatch, picture drift, proxy relabeling, q80 overclaiming

**Confidence breakdown:**

- Literature coverage: MEDIUM - enough for this phase because the repo-specific anchors matter more than new papers
- Methods: HIGH - the first bridge can stay close to Pauli algebra and current Qiskit scripts
- Known results: HIGH - main anchors are local repo artifacts
- Pitfalls: HIGH - the failure modes are already visible in the current wording

**Research date:** 2026-03-17
**Valid until:** 2026-04-16

</metadata>

---

_Phase: 01_
_Research completed: 2026-03-17_
_Ready for planning: yes_
