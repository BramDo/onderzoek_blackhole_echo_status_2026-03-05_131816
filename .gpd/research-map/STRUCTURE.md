# Project Structure

**Analysis Date:** 2026-03-17

## Directory Layout

```
[project-root]/
+-- STATUS.md
+-- gevonden_bestanden.csv
+-- run_levelc_exact_short_day.ps1
+-- run_q14_only_exact_short_day.ps1
+-- files/
    +-- quantum-math-lab/
        +-- README.md
        +-- hardware_advantage_protocol.md
        +-- qiskit_black_hole_scrambling.py
        +-- qiskit_black_hole_hardware_runner.py
        +-- benchmarks/
        +-- results/
        +-- scripts/run-levelc-bundle.sh
```

## Directory Purposes

**`files/quantum-math-lab/benchmarks/`:**

- Purpose: frozen benchmark and claim-definition manifests
- Contains: `.json`
- Key files: `files/quantum-math-lab/benchmarks/levelc_manifest.json`, `files/quantum-math-lab/benchmarks/q14_only_manifest.json`

**`files/quantum-math-lab/results/benchmark/classical/`:**

- Purpose: exact or noisy classical baselines plus `/usr/bin/time -v` logs
- Contains: classical result `.json` files and timing `.txt` files
- Key files: `files/quantum-math-lab/results/benchmark/classical/black_hole_scrambling_q14_exact_short.json`, `files/quantum-math-lab/results/benchmark/classical/time_black_hole_scrambling_q14_exact_short.txt`

**`files/quantum-math-lab/results/hardware/`:**

- Purpose: raw hardware JSON outputs, logs, and timing sidecars
- Contains: `.json`, `.log`, `.txt`
- Key files: `files/quantum-math-lab/results/hardware/benchmark_q14_raw_exact_short_day3.json`, `files/quantum-math-lab/results/hardware/black_hole_hardware_q10_pilot.json`, `files/quantum-math-lab/results/hardware/black_hole_hardware_q80_subset01_mit.json`

**`files/quantum-math-lab/results/hardware/summary/`:**

- Purpose: campaign interpretation, evidence synthesis, and claim-language governance
- Contains: summary `.md` and `.json`
- Key files: `files/quantum-math-lab/results/hardware/summary/levelb_evidence_report.md`, `files/quantum-math-lab/results/hardware/summary/q14_only_campaign_plan_2026-03-16.md`, `files/quantum-math-lab/results/hardware/summary/q14_only_day3_update_2026-03-17.md`

**`files/quantum-math-lab/results/hardware/archives/2026-03-05_q80_run1_run2/`:**

- Purpose: archived 80q run bundle with checksums and summary
- Contains: raw archive `.json`, `.md`, checksum file

**`files/quantum-math-lab/scripts/`:**

- Purpose: orchestration bundle for multi-stage benchmark execution
- Contains: shell runner(s)
- Key files: `files/quantum-math-lab/scripts/run-levelc-bundle.sh`

## Key File Locations

**Theory / Formalism:**

- `files/quantum-math-lab/hardware_advantage_protocol.md`: claim-level framework and benchmark rules
- `files/quantum-math-lab/README.md`: general repo overview and older demo-oriented entry points

**Computation / Numerics:**

- `files/quantum-math-lab/qiskit_black_hole_scrambling.py`: exact/noisy classical workflow
- `files/quantum-math-lab/qiskit_black_hole_hardware_runner.py`: IBM Runtime execution and mitigation workflow
- `files/quantum-math-lab/scripts/run-levelc-bundle.sh`: matrix-style shell orchestration
- `run_q14_only_exact_short_day.ps1`: daily q14-only gate runner

**Data / Results:**

- `files/quantum-math-lab/results/benchmark/classical/`: classical reference curves and timing logs
- `files/quantum-math-lab/results/hardware/`: hardware raw/mitigated JSONs and daily runner logs

**Configuration / Parameters:**

- `files/quantum-math-lab/benchmarks/levelc_manifest.json`
- `files/quantum-math-lab/benchmarks/q14_only_manifest.json`

## Document Dependency Graph

**Computation Dependencies:**

- `files/quantum-math-lab/qiskit_black_hole_scrambling.py` produces classical JSON outputs in `files/quantum-math-lab/results/benchmark/classical/`
- `files/quantum-math-lab/qiskit_black_hole_hardware_runner.py` produces hardware JSON outputs in `files/quantum-math-lab/results/hardware/`
- `run_q14_only_exact_short_day.ps1` reads classical timing files and hardware JSON outputs, then writes timing sidecars and stdout logs
- `run_levelc_exact_short_day.ps1` forwards to `run_q14_only_exact_short_day.ps1`
- `STATUS.md` and the markdown files in `files/quantum-math-lab/results/hardware/summary/` synthesize those artifacts into claim-level status

## Naming Conventions

**Files:**

- Daily exact-short hardware outputs: `benchmark_q{n}_raw_exact_short_day{d}.json`
- Large-system subset outputs: `black_hole_hardware_q80_subset{nn}_mit[_xsup][_pq10][_rerun1].json`
- Summary notes: semantic name plus date, for example `q14_only_day3_update_2026-03-17.md`

**Variables in Code:**

- Core observable names are stable across code and data: `ideal_echo`, `perturbed_echo`, `readout_mitigated`, `summary_by_depth`
- Runtime gate fields use explicit names such as `quantum_seconds`, `billed_seconds`, and `runtime_gate_seconds`

## Where to Add New Content

**New Benchmark Definition:**

- Add or revise JSON under `files/quantum-math-lab/benchmarks/`
- Update claim language in `files/quantum-math-lab/hardware_advantage_protocol.md`

**New Classical Observable:**

- Implement in `files/quantum-math-lab/qiskit_black_hole_scrambling.py`
- Emit result JSON under `files/quantum-math-lab/results/benchmark/classical/`

**New Hardware Campaign:**

- Extend `files/quantum-math-lab/qiskit_black_hole_hardware_runner.py`
- Add a PowerShell or shell entry point alongside `run_q14_only_exact_short_day.ps1`
- Summarize in `files/quantum-math-lab/results/hardware/summary/`

## Build and Execution

**Running Computations:**

```bash
bash files/quantum-math-lab/scripts/run-levelc-bundle.sh --stage plan
/home/bram/.venvs/qiskit/bin/python files/quantum-math-lab/qiskit_black_hole_scrambling.py --qubits 14 --depths 1,2,3,4 --trials 3 --seed 424242 --json-out results/benchmark/classical/black_hole_scrambling_q14_exact_short.json
/home/bram/.venvs/qiskit/bin/python files/quantum-math-lab/qiskit_black_hole_hardware_runner.py --backend ibm_fez --qubits 14 --depths 1,2,3,4 --trials 3 --shots 4000 --output-json results/hardware/benchmark_q14_raw_exact_short_day3.json
```

**Campaign Entry Point:**

```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\Lenna\SynologyDrive\qlab\onderzoek_blackhole_echo_status_2026-03-05_131816\run_q14_only_exact_short_day.ps1 -DryRun
```

## Special Directories

**`files/quantum-math-lab/results/hardware/archives/2026-03-05_q80_run1_run2/`:**

- Purpose: preserved historical bundle for an earlier 80q snapshot
- Generated: yes
- Committed: yes

**Missing expected helper assets:**

- The snapshot does not contain `scripts/run-in-qiskit-venv.sh`, `quant_math_lab.py`, `qcqi_pure_math_playground.py`, `quantum_app.py`, or `quantumapp/`, even though `README.md` still references them.

---

_Structure analysis: 2026-03-17_
