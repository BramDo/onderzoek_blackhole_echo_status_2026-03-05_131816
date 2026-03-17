# Research Gaps and Open Issues

**Analysis Date:** 2026-03-17

## Incomplete Derivations

**Physical interpretation of the toy model:**

- What exists: a clear circuit-model scrambling benchmark with explicit observables
- What's missing: an in-project derivation tying this toy workflow to a concrete black-hole or holographic model
- Files: `files/quantum-math-lab/README.md`, `files/quantum-math-lab/hardware_advantage_protocol.md`
- Impact: limits how literally the project can be framed outside benchmarking language
- Difficulty estimate: research-level

## Unchecked Limits

**Strict Level-C multi-size claim:**

- Limit: two consecutive sizes must beat classical under the same runtime metric
- Expected behavior: both q12 and q14 should pass
- Current status: not satisfied; q12 is the blocker
- Files: `STATUS.md`, `files/quantum-math-lab/results/hardware/summary/levelc_runtime_quantum_seconds_2026-03-16.md`

**Global 80-qubit fidelity / overlap:**

- Limit: a full-system observable should be checked rather than only subsets
- Current status: not checked; subset-only by design
- Files: `STATUS.md`, `files/quantum-math-lab/hardware_advantage_protocol.md`

## Unjustified Approximations

**Subset observable as stand-in for full 80q performance:**

- Where used: `STATUS.md`, `files/quantum-math-lab/results/hardware/summary/levelb_evidence_report.md`
- Justification status: explicitly argued, but still only partial
- What could go wrong: subset utility may not track full-state fidelity or broader advantage
- How to justify: add more subset families or a feasible global proxy with controlled interpretation
- Priority: High

**`IBM quantum_seconds` versus classical wall time comparator:**

- Where used: active q14-only claim
- Justification status: documented and frozen, but still a mixed-runtime comparison
- What could go wrong: readers may interpret the claim as an apples-to-apples end-to-end runtime win
- How to justify: keep the wording narrow and preserve the metric clarification note in every downstream write-up
- Priority: High

## Missing Cross-Checks

**Hardware-valid ZNE on real devices:**

- What to verify: mitigation improvements beyond raw/readout-only estimates on actual hardware
- Method: implement the protocol’s hardware-valid scaling path rather than Aer-style scaling
- Expected outcome: stronger mitigation story for hardware runs
- Files to modify: `files/quantum-math-lab/qiskit_black_hole_hardware_runner.py`, `files/quantum-math-lab/hardware_advantage_protocol.md`
- Priority: Medium

**External literature anchoring:**

- What to verify: whether the chosen toy benchmark and claim language align with existing scrambling / advantage literature
- Method: add an explicit bibliography layer
- Expected outcome: more defensible framing outside the repo
- Files to modify: no bibliography files currently present
- Priority: Medium

## Numerical Concerns

**Automated regression coverage is absent:**

- Problem: there is no test suite to catch estimator, schema, or campaign-logic regressions
- Files: entire snapshot
- Symptoms: subtle claim drift or parser breakage can survive until a campaign run
- Resolution: add JSON-schema checks and regression tests around the daily runner and emitted artifact structure

**Historical parser fragility already occurred once:**

- Problem: `STATUS.md` notes a day-2 runner crash after the q12 job because of a PowerShell MAE-parser bug
- Files: `STATUS.md`, `run_q14_only_exact_short_day.ps1`
- Symptoms: hardware execution succeeds but wrapper automation breaks
- Resolution: regression-test the parser logic against representative hardware JSON artifacts

## Physical Consistency Issues

**Over-claiming risk from legacy names:**

- Concern: filenames and wrapper names still use “Level C” even though the active claim is narrower
- Files: `run_levelc_exact_short_day.ps1`, `files/quantum-math-lab/results/hardware/summary/levelc_*.md`
- Impact: easy for later planning or writing to overstate what has been shown
- Resolution path: preserve `STATUS.md` wording and consider renaming or quarantining legacy entry points

## Missing Generalizations

**Second consecutive passing size:**

- Current scope: q14-only narrow runtime-positive claim
- Natural extension: recover a second size that passes under the same frozen runtime metric
- Difficulty: hard under current evidence, because q12 already fails
- Blocks: honest restoration of the broader Level-C claim

## Documentation Gaps

**Snapshot completeness mismatch:**

- What's undocumented: the README references helper scripts and modules that are absent from this snapshot
- Files: `files/quantum-math-lab/README.md`
- Impact: execution instructions in the snapshot are only partially self-contained

## Stale or Dead Content

**Legacy Level-C wrapper:**

- What: `run_levelc_exact_short_day.ps1` now only forwards to the q14-only runner
- Files: `run_levelc_exact_short_day.ps1`
- Action: rename or clearly archive
- Risk: moderate confusion in future planning and writing

## Missing Literature Connections

**No external bibliography:**

- What: no paper list, BibTeX file, or explicit external reference map
- Why relevant: downstream planning and manuscript writing currently have only internal anchors
- Priority: Medium

## Priority Ranking

**Critical (blocks correctness):**
1. Legacy Level-C claim remains blocked by q12 runtime FAIL under `IBM quantum_seconds`.
2. Over-claiming remains a live risk unless downstream work preserves the current narrow q14-only wording.

**High (blocks completeness):**
1. No automated regression or schema-validation layer guards the benchmark pipeline.
2. 80q evidence remains subset-only, not a global-fidelity result.
3. The snapshot is not fully self-contained because README-referenced helper assets are missing.

**Medium (improves quality):**
1. External literature anchors are missing.
2. Hardware-valid ZNE on real devices is still a planned rather than demonstrated layer.

**Low (nice to have):**
1. Rename or archive legacy Level-C wrappers and notes to reduce narrative drift.

---

_Gap analysis: 2026-03-17_
