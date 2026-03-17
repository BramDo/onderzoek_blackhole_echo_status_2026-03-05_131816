# Computational Approaches: OLE Extension of the q14/q80 Scrambling Workflow

**Surveyed:** 2026-03-17
**Domain:** quantum-circuit scrambling benchmarks
**Confidence:** HIGH

## Recommended Stack

The recommended computational approach is conservative: preserve the current q14/q80 Qiskit workflow and add the smallest possible fixed-observable OLE layer on top of it. The first benchmark should live in the exact q14 regime, where the repo already has a frozen manifest, exact-short reference artifacts, and a clear comparison target in `perturbed_echo`.

For hardware, the correct large-system route remains subset observables measured with the existing hardware runner and local-tensored readout mitigation. Full-system 80q overlap or global OLE should not be treated as an immediate computational target because the current code and evidence already show that exact references do not scale there and global readout sensitivity becomes the dominant failure mode.

## Numerical Algorithms

| Algorithm | Problem | Convergence | Cost per Step | Memory | Key Reference |
| --------- | ------- | ----------- | ------------- | ------ | ------------- |
| Exact statevector forward/reverse evolution with direct trace evaluation | q14 fixed-observable OLE reference | exact up to floating-point error | exponential in qubit count; practical only at small/medium `n` | exponential in qubit count | current repo workflow |
| Shot-based Sampler estimation | hardware or noise-aware observable estimation | statistical error scales as `1/sqrt(shots)` | proportional to shots times circuit count | modest client-side memory | current IBM Runtime workflow |
| Local-tensored readout mitigation on a subset register | stabilize q80 subset observables | improves with calibration quality; limited by subset size | calibration overhead plus per-shot post-processing | scales with subset, not full register | current repo workflow |
| Small-`delta` quadratic fit | extract OLE onset coefficient and compare with theory | fit stability improves with enough small-`delta` points and exact references | negligible compared with circuit generation | negligible | Algorithmiq OLE note |
| Randomized-measurement averaging (optional path) | ancilla-free, no-reversal OTOC estimation | statistical error scales with both shots and number of random unitaries | high sampling cost | moderate bookkeeping | Vermersch et al. (`1807.09087v2`) |

### Convergence Properties

- **Exact statevector OLE:** convergence criterion is trivial because the method is numerically exact for the chosen qubit/depth regime; failure mode is simply exponential blow-up with system size.
- **Sampler estimates:** convergence criterion is stable mean and uncertainty under repeated shots or repeated jobs; failure mode is large variance or backend drift.
- **Subset mitigation:** convergence criterion is calibration stability and raw-vs-mitigated consistency on the same subset; failure mode is ill-conditioned mitigation or subset definitions that erase the signal.
- **Small-`delta` fit:** convergence criterion is stable quadratic coefficient under shrinking fit window; failure mode is choosing `delta` values so large that higher-order terms dominate.
- **Randomized measurements:** convergence criterion is stability versus extra random unitaries and shots; failure mode is overinterpreting low-order approximations without convergence tests.

## Software Ecosystem

### Primary Tools

| Tool | Version | Purpose | License | Maturity |
| ---- | ------- | ------- | ------- | -------- |
| Qiskit | `1.4.5` in recorded hardware artifacts | circuit construction, exact references, transpilation, Sampler interfaces | open source | stable |
| `qiskit_ibm_runtime` | `0.40.0` in recorded hardware artifacts | IBM hardware execution and metadata capture | open source / service client | stable |
| `qiskit_aer` | `0.17.0` in recorded hardware artifacts | simulator support and local noise-aware checks | open source | stable |
| NumPy | repo dependency | numerical post-processing and fitting | open source | stable |

### Supporting Tools

| Tool | Version | Purpose | When Needed |
| ---- | ------- | ------- | ----------- |
| `/usr/bin/time -v` | system tool | classical runtime and memory capture | whenever runtime claims are updated |
| `qiskit_experiments` | `0.7.0` in recorded artifacts | calibration/experiment utilities | only if mitigation workflow expands |
| `circuit_knitting_toolbox` | `0.7.2` in recorded artifacts | ancillary environment dependency | not central to the first OLE deliverable |

## Data Flow

```
Frozen manifest and fixed observable definition
-> generate brickwork scrambler U and perturbation V_delta
-> exact q14 OLE reference and current perturbed_echo baseline
-> delta sweep and delta^2 fit
-> hardware-ready circuit mapping with same observable semantics
-> raw / mitigated subset estimates on frozen backend settings
-> comparison artifacts and claim-bounded summaries
```

## Computation Order and Dependencies

| Step | Depends On | Produces | Can Parallelize? |
| ---- | ---------- | -------- | ---------------- |
| Freeze first fixed observable and generator conventions | project contract, literature survey | OLE task definition | no |
| Implement q14 exact OLE evaluation | frozen definition, existing q14 exact-short path | reference curves vs `delta^2` | limited |
| Overlay with current `perturbed_echo` baseline | q14 exact OLE output, existing manifest artifacts | first decisive benchmark | yes once both inputs exist |
| Map hardware measurement route | exact definition, current hardware runner semantics | hardware-ready protocol | limited |
| Run q80 subset feasibility / locality checks | hardware mapping, subset definitions | extension evidence | yes across subsets / days |

## Resource Estimates

| Computation | Time (estimate) | Memory | Storage | Hardware |
| ----------- | --------------- | ------ | ------- | -------- |
| Replay of current q14 exact-short baseline | about `51.05 s` wall time from the active manifest | moderate workstation RAM | small JSON artifacts | local CPU |
| q14 hardware raw exact-short campaign point | `26` IBM `quantum_seconds` in current day-1/day-3 artifacts, with higher local orchestration wall time | low local memory | small JSON plus logs | IBM backend |
| q80 subset hardware batch | budget-limited; existing Level-B snapshot used `255 s` total across pilot and subset jobs | low local memory | moderate JSON/summary storage | IBM backend |
| full 80q exact OLE | not feasible in current runner | prohibitive | prohibitive | not a current target |

## Integration with Existing Code

The new computations should plug into the current codebase instead of creating a parallel stack.

- **Input formats:** frozen manifest JSON, command-line flags for qubits/depths/shots/subsets, and existing hardware summary conventions.
- **Output formats:** JSON benchmark artifacts plus markdown summaries, matching the current q14/q80 reporting flow.
- **Interface points:** `qiskit_black_hole_scrambling.py` for exact q14 OLE generation, `qiskit_black_hole_hardware_runner.py` for hardware/subset mapping, and the existing summary scripts for claim-bounded reporting.

## Validation Strategy

| Result | Validation Method | Benchmark | Source |
| ------ | ----------------- | --------- | ------ |
| q14 fixed-observable OLE onset | fit `f_delta(O)` against `delta^2` in a small-`delta` window and confirm intercept near `1` | Algorithmiq small-`delta` prediction | Algorithmiq OLE note |
| q14 OLE implementation | compare direct trace evaluation against independent exact-state evolution checks | exact q14 regime | local repo exact workflow |
| OLE versus current baseline | overlay OLE and `perturbed_echo` outputs on the same manifest-defined task family | active q14-only campaign | `q14_only_manifest.json` |
| q80 subset extension | verify locality behavior under overlap vs disjoint perturbation placement and compare raw vs mitigated on the same subset | existing subset-control evidence | `levelb_evidence_report.md` |
| any runtime claim update | keep same task, same accuracy target, and same metric definition | current q14-only claim discipline | `STATUS.md` and `hardware_advantage_protocol.md` |

## Sources

- `STATUS.md` -- runtime metric discipline and q80 subset interpretation.
- `files/quantum-math-lab/benchmarks/q14_only_manifest.json` -- current q14 exact-short benchmark definition.
- `files/quantum-math-lab/hardware_advantage_protocol.md` -- hardware benchmarking rules and subset workflow.
- `files/quantum-math-lab/results/hardware/summary/levelb_evidence_report.md` -- q80 subset locality and reproducibility evidence.
- recorded hardware JSON artifacts with environment metadata -- current tool versions and runtime-client stack.
- Algorithmiq OLE theory note -- small-`delta` benchmark target.
- Vermersch et al. (`1807.09087v2`) -- randomized-measurement cost structure and convergence considerations.
