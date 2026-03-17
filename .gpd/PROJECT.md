# Operator Loschmidt Echo Extension of q14/q80 Scrambling Benchmarks

## What This Is

This project continues the existing q14/q80 black-hole scrambling benchmark repository by extending the current `perturbed_echo` state-echo workflow into a fixed-observable operator Loschmidt echo (OLE) program. The immediate deliverable is a q14 small-delta OLE-vs-delta^2 benchmark against the active q14 `perturbed_echo` baseline, with a hardware-ready measurement path and explicit q80 subset/full scope discipline.

## Working Distinction

Use this wording consistently:

- `perturbed_echo` is the repo's state-return echo observable: for the fixed input state `|0...0>`, it measures the return probability after `U`, a local kick, and `U^dagger`, i.e. a state-overlap quantity of the form `|<psi0|U^dagger X U|psi0>|^2`.
- OLE is a fixed-observable operator correlator: `f_delta(O) = 2^{-n} Tr(U O U^dagger V_delta^dagger U O U^dagger V_delta)` for an explicitly chosen observable `O` and perturbation `V_delta = exp(-i delta G)`.
- Therefore `perturbed_echo` is a state-return benchmark, while OLE is an operator-space scrambling diagnostic. The project may compare or bridge them, but it must not describe `perturbed_echo` itself as OLE unless the fixed observable and perturbation unitary are made explicit.
- For this project, OLE is the more informative target because it opens a larger probing space: explicit choice of `O`, explicit choice of `G`, overlap versus disjoint support tests, subset-observable variants, and a controlled small-`delta` link to commutator/OTOC growth. `perturbed_echo` remains valuable because it is already implemented, benchmarked, and hardware-tested in this repo.

## Phase 1 Default Lock

Phase 1 freezes the first q14 benchmark as a Pauli-specialized fixed-observable OLE bridge:

- Fixed observable: `P = Z_0`
- Hilbert-Schmidt-normalized translation: `O = Z_0 / sqrt(2^14)`
- Overlap generator: `G = X_0`
- Disjoint control generator: `G = X_10`

The report-level q14 benchmark quantity is

$$
F_\delta(P) = 2^{-n} \operatorname{Tr}(U P U^\dagger V_\delta^\dagger U P U^\dagger V_\delta),
$$

with `F_0(P) = 1` because `P^2 = I`. When normalized-operator notation is needed, the project uses

$$
f_\delta(O) = 2^{-n} F_\delta(P),
$$

so `f_0(O) = 2^{-n}`. This explicit translation resolves the initialization ambiguity between the normalized `Tr(O^2)=1` convention and the unit-intercept onset language needed for the first `delta^2` benchmark.

## Core Research Question

Can the existing q14/q80 `perturbed_echo` pipeline be turned into a fixed-observable OLE workflow that yields a decisive q14 small-delta benchmark and a credible hardware-ready path without overclaiming the meaning of q80 subset observables?

## Scoping Contract Summary

### Contract Coverage

- First decisive claim / deliverable: produce a q14 small-delta fixed-observable OLE benchmark that overlays the current q14 `perturbed_echo` baseline and keeps a hardware-ready path visible.
- Acceptance signal: a q14 OLE-vs-delta^2 benchmark artifact with explicit fixed-observable definitions plus a hardware-ready note that maps the protocol onto the existing pipeline.
- False progress to reject: a classical-only curve, a renamed `perturbed_echo` proxy, or a q80 subset result presented as if it settles the full-q80 question.

### User Guidance To Preserve

- **User-stated observables:** fixed-observable OLE first, not an observable-family search; keep both overlap-support and disjoint-support variants in scope.
- **User-stated deliverables:** start with a q14 small-delta OLE-vs-delta^2 benchmark against the current `perturbed_echo` baseline.
- **Must-have references / prior outputs:** `STATUS.md`, `files/quantum-math-lab/benchmarks/q14_only_manifest.json`, `files/quantum-math-lab/results/hardware/summary/levelb_evidence_report.md`, and the Algorithmiq OLE theory PDF.
- **Stop / rethink conditions:** stop if the first result collapses back to a classical-only state-overlap proxy, if the OLE framing is only a relabeling of `perturbed_echo`, or if q80 subset outputs start being interpreted as full-q80 global OLE.

### Scope Boundaries

**In scope**

- Fixed-observable OLE built from the existing q14/q80 `perturbed_echo` workflow.
- q14 small-delta OLE-vs-delta^2 benchmarking as the first success gate.
- Classical exact/reference and hardware-ready measurement paths.
- q80 subset observables as the immediate scalable route, with full-q80 OLE kept visible as a later extension.

**Out of scope**

- Restoring the legacy full Level-C two-size claim during initialization.
- Presenting q80 subset results as if they already establish full-q80 global OLE.
- Relabeling existing `perturbed_echo` outputs as OLE without implementing the fixed-observable protocol.

### Active Anchor Registry

- `ref-algorithmiq-ole`: Algorithmiq, "Model Description and Theory: Information flow in complex materials" (PDF, accessed 2026-03-17)
  - Why it matters: defines the OLE observable, the small-delta expansion, and the measurement framing for the bridge from the current workflow.
  - Carry forward: `planning`, `execution`, `verification`, `writing`
  - Required action: `read`, `compare`, `cite`
- `ref-status`: `STATUS.md`
  - Why it matters: freezes the current narrow q14-only claim language and the q12 blocker, and marks q80 as subset-only evidence so far.
  - Carry forward: `planning`, `execution`, `verification`, `writing`
  - Required action: `read`, `use`, `avoid`
- `ref-q14-manifest`: `files/quantum-math-lab/benchmarks/q14_only_manifest.json`
  - Why it matters: anchors the first OLE benchmark to the active q14 exact-short campaign settings.
  - Carry forward: `planning`, `execution`, `verification`
  - Required action: `read`, `use`, `compare`
- `ref-levelb-evidence`: `files/quantum-math-lab/results/hardware/summary/levelb_evidence_report.md`
  - Why it matters: preserves the current q80 subset/locality evidence trail without overstating it as full-system validation.
  - Carry forward: `planning`, `execution`, `verification`, `writing`
  - Required action: `read`, `use`, `avoid`

### Carry-Forward Inputs

- `STATUS.md`
- `files/quantum-math-lab/benchmarks/q14_only_manifest.json`
- `files/quantum-math-lab/results/hardware/summary/levelb_evidence_report.md`
- Current `perturbed_echo` baseline in the q14-only exact-short campaign
- Existing q80 subset-observable locality evidence

### Skeptical Review

- **Weakest anchor:** the external benchmark layer is currently anchored mainly by the Algorithmiq theory note rather than a broader literature set.
- **Unvalidated assumptions:** the current `perturbed_echo` workflow can be cleanly bridged to fixed-observable OLE; a hardware-ready OLE measurement path can remain aligned with the existing q14/q80 pipeline constraints.
- **Competing explanation:** apparent small-delta agreement could come from a renamed or closely related `perturbed_echo` proxy rather than a genuine fixed-observable OLE implementation.
- **Disconfirming observation:** the first q14 benchmark cannot be expressed as an explicit fixed-observable OLE curve against delta^2, or the q80 subset/full split proves operationally incoherent under the current pipeline.
- **False progress to reject:** a good-looking classical-only benchmark with no hardware-ready route, or subset-only q80 results drifting into full-q80 claims.

### Open Contract Questions

- Will full-q80 OLE admit a meaningful feasible proxy, or remain a longer-horizon target?
- Should later phases use explicit PLE terminology for a Pauli-specialized fixed-observable OLE path?

## Research Questions

### Answered

- [x] The repository already supports a q14 exact-short `perturbed_echo` baseline and the current narrow q14-only runtime-positive claim.
- [x] The broader legacy Level-C two-size claim is not currently established because q12 remains the blocker under `IBM quantum_seconds`.
- [x] q80 subset observables already show locality-sensitive evidence, but only at subset level rather than as a full-system global observable.
- [x] The default first fixed-observable q14 bridge is now frozen as `P = Z_0` with overlap `G = X_0` and disjoint control `G = X_10`, reported through `F_delta(P)` with an explicit normalized-operator translation.

### Active

- [ ] Can fixed-observable OLE be implemented in the existing q14 pipeline and benchmarked against `perturbed_echo` through the small-delta delta^2 law?
- [ ] What hardware-ready measurement protocol best maps fixed-observable OLE onto the current q14/q80 pipeline?
- [ ] How should q80 subset and full-q80 OLE targets stay visible without overclaiming subset results?

### Out of Scope

- Exploring a broad observable family before the fixed-observable OLE bridge exists — the user asked to stay with fixed observables.
- Restoring the legacy full Level-C claim immediately — blocked by q12 and not the decisive initialization target.
- Treating subset-only q80 outputs as global OLE — explicitly forbidden by the approved contract.

## Research Context

### Physical System

The physical system is an `n`-qubit gate-model scrambling toy model built from random brickwork circuits with single-qubit `Rx/Rz` layers and staggered `CZ` couplings. The active computational stack already supports exact statevector evolution where feasible, noisy classical sampling, and IBM Runtime Sampler execution with subset-observable mitigation for large-system runs.

### Theoretical Framework

This is a quantum-information scrambling benchmark framed through Loschmidt-echo-style observables, OTOC-related diagnostics, and hardware-oriented measurement pipelines. The extension under study is a fixed-observable OLE formulation whose small-delta behavior is tied to the commutator/OTOC structure while remaining compatible with the repo's current q14/q80 benchmarking architecture.

More explicitly for this project:

- `perturbed_echo` lives in state space and is read as a return probability for a fixed prepared state.
- OLE lives in operator space and is read as the self-correlation of a fixed observable under a controlled perturbation.
- OLE is therefore the broader and potentially more informative object, while `perturbed_echo` is the narrower baseline already available in the repo.
- The bridge question is whether the existing state-return workflow can be upgraded into an explicit fixed-observable operator diagnostic without changing the task family or overclaiming what the old observable already means.

### Key Parameters and Scales

| Parameter | Symbol | Regime | Notes |
| --------- | ------ | ------ | ----- |
| Qubit count | `n` | `14` active; `80` large-system route | Exact references are currently practical only in the small/medium regime; q80 uses subset observables. |
| Circuit depth | `d` | `1, 2, 3, 4` active q14 campaign | Broader historical plans included deeper circuits, but the active exact-short gate is shallower. |
| Perturbation strength | `delta` | small-delta expansion regime | New OLE benchmark parameter; first deliverable is an OLE-vs-delta^2 curve. |
| Fixed observable | `O` | fixed, not a family search | Initial framing allows both overlap-support and disjoint-support variants. |
| Perturbation generator | `G` | local generator for `V_delta = exp(-i delta G)` | Must stay interpretable relative to the current local perturbation path. |
| Perturbation location | `q_p` | typically local | Existing locality controls already compare perturbations on qubits `0` and `10`. |
| Subset qubits | `S` | subset route for q80 | Current q80 evidence uses explicit subset observables rather than full-system overlap. |
| Trials / shots / seeds | `N_trials`, `N_shots`, `seed` | frozen manifest-controlled | Existing q14 and q80 campaigns are governed by frozen benchmark manifests. |

### Known Results

- The active q14 exact-short campaign already produces the current `perturbed_echo` baseline and the repo's narrow runtime-positive claim language under the frozen q14-only manifest.
- q80 subset-observable hardware evidence already supports locality-sensitive behavior, especially when perturbation support overlaps the measured subset, but remains explicitly subset-only.
- The Algorithmiq OLE theory note provides a fixed-observable definition, a small-delta expansion, and a measurement framing that can guide the bridge from the current state-echo workflow.

### What Is New

The new contribution is not a fresh scrambling benchmark from scratch. It is a controlled bridge from the existing q14/q80 `perturbed_echo` pipeline to a fixed-observable OLE program: first a decisive q14 small-delta benchmark against the current baseline, then a hardware-ready path that preserves the distinction between q80 subset observables and the still-open full-q80 target.

### Target Venue

Not fixed yet. Keep the framing suitable for an internal methods note or a future quantum-information/benchmarking preprint once the OLE bridge and q14 benchmark are validated.

### Computational Environment

The project uses the existing Python/Qiskit stack in `files/quantum-math-lab/`, local exact and noisy classical runs, and IBM Runtime Sampler hardware execution. Exact statevector references are disabled above `24` qubits in the current hardware runner, so q80 work must remain subset-observable unless a distinct full-system proxy is justified later.

## Notation and Conventions

See `.gpd/CONVENTIONS.md` for all notation and sign conventions.
See `.gpd/NOTATION_GLOSSARY.md` for symbol definitions.

## Unit System

Dimensionless scrambling observables (`perturbed_echo`, OLE, OTOC proxies) with runtime metrics reported in seconds. This is a circuit-model benchmark; no spacetime metric signature or continuum natural-unit convention is central to the current scope.

## Requirements

See `.gpd/REQUIREMENTS.md` for the detailed requirements specification.

Key requirement categories: `ANAL` (observable/formulation bridge), `NUMR` (classical and hardware benchmarking), `VALD` (anchor and scope validation)

## Key References

- `ref-algorithmiq-ole` — OLE definition and small-delta theory anchor
- `ref-status` — current q14-only claim language and q80 interpretation guardrail
- `ref-q14-manifest` — active q14 benchmark settings
- `ref-levelb-evidence` — q80 subset/locality evidence to carry forward

## Constraints

- **Computational resources**: Exact statevector reference is currently limited to small/medium sizes; q80 must remain subset-observable unless a new feasible proxy is established.
- **Claim discipline**: `IBM quantum_seconds` versus local wall-clock timing must stay narrowly described, and the blocked q12 result means the broader Level-C claim stays out of scope.
- **Observable discipline**: Fixed-observable OLE must remain distinct from the existing `perturbed_echo` state-echo observable.
- **Snapshot completeness**: Some README-referenced helper assets are absent from the snapshot, so planning must stay grounded in the files that actually exist here.

## Key Decisions

| Decision | Rationale | Outcome |
| -------- | --------- | ------- |
| Stay centered on the existing q14/q80 workflow | The user explicitly asked not to drift into a fresh standalone OLE project. | — Pending |
| Use fixed observables | The first bridge should be a controlled fixed-observable OLE extension, not an observable-family search. | — Pending |
| Keep both classical and hardware-ready paths in scope | A classical-only result would not satisfy the user's requested research direction. | — Pending |
| Keep q80 subset and full-q80 directions both visible | The immediate route is subset-observable, but the full-q80 question must not disappear from view. | — Pending |

Full log: `.gpd/DECISIONS.md`

---

_Last updated: 2026-03-17 after initialization_
