#!/usr/bin/env bash
set -euo pipefail

# Level-C benchmark command bundle
# Default mode is dry-run (prints commands only).

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

MANIFEST="benchmarks/levelc_manifest.json"
STAGE="plan"
EXECUTE=0

usage() {
  cat <<'USAGE'
Usage:
  scripts/run-levelc-bundle.sh [--stage <name>] [--execute] [--manifest <path>]

Stages:
  plan                 Print the frozen benchmark plan and commands (default)
  classical-pilot      Classical baseline matrix (q=8,10,12; shots=5000,10000)
  hardware-pilot       Hardware pilot on q=8,10 (raw + readout mitigation)
  hardware-80-subset   80q raw + subset mitigated runs (subset 0-9 and 10-19)
  hardware-80-xsup     80q subset run with extra suppression (DD + twirling)
  hardware-q80-subset-proxy-sidecar 20q subset-locality proxy bundle with optional PE-LiNN diagnostic sidecar
  all                  Run all stages above in order

Flags:
  --execute            Actually run commands. Without this flag, only prints.
  --manifest <path>    Manifest path (default: benchmarks/levelc_manifest.json)

Examples:
  scripts/run-levelc-bundle.sh --stage plan
  scripts/run-levelc-bundle.sh --stage hardware-80-xsup --execute
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --stage)
      STAGE="${2:-}"
      shift 2
      ;;
    --execute)
      EXECUTE=1
      shift
      ;;
    --manifest)
      MANIFEST="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 2
      ;;
  esac
done

if [[ ! -f "$MANIFEST" ]]; then
  echo "Manifest not found: $MANIFEST" >&2
  exit 2
fi

mkdir -p results/benchmark/classical results/hardware

run_cmd() {
  local cmd="$1"
  echo
  echo ">> $cmd"
  if (( EXECUTE )); then
    eval "$cmd"
  fi
}

print_plan() {
  echo "=== Level-C benchmark plan ==="
  echo "Manifest: $MANIFEST"
  echo "Mode: $([[ $EXECUTE -eq 1 ]] && echo EXECUTE || echo DRY-RUN)"
  echo
  echo "Frozen task + criteria are in manifest."
  echo "Use --execute only when you want to consume runtime budget."
}

stage_classical_pilot() {
  local depths="1,2,3,4,5,6,8,10"
  for q in 8 10 12; do
    for shots in 5000 10000; do
      local out_json="results/benchmark/classical/black_hole_scrambling_q${q}_s${shots}.json"
      local out_time="results/benchmark/classical/time_black_hole_scrambling_q${q}_s${shots}.txt"
      run_cmd "/usr/bin/time -v -o ${out_time} scripts/run-in-qiskit-venv.sh python qiskit_black_hole_scrambling.py --qubits ${q} --depths ${depths} --trials 3 --seed 424242 --with-noise --shots ${shots} --json-out ${out_json}"
    done
  done
}

stage_hardware_pilot() {
  local depths="1,2,3,4,5,6,8,10"
  for q in 8 10; do
    local out_raw="results/hardware/benchmark_q${q}_raw.json"
    local out_mit="results/hardware/benchmark_q${q}_mit.json"

    run_cmd "scripts/run-in-qiskit-venv.sh python qiskit_black_hole_hardware_runner.py --qubits ${q} --depths ${depths} --trials 3 --shots 5000 --output-json ${out_raw}"

    run_cmd "scripts/run-in-qiskit-venv.sh python qiskit_black_hole_hardware_runner.py --qubits ${q} --depths ${depths} --trials 3 --shots 5000 --readout-mitigation --cal-shots 4000 --output-json ${out_mit}"
  done
}

stage_hardware_80_subset() {
  local depths="1,2,3,4"

  run_cmd "scripts/run-in-qiskit-venv.sh python qiskit_black_hole_hardware_runner.py --qubits 80 --depths ${depths} --trials 3 --shots 4000 --skip-exact --output-json results/hardware/black_hole_hardware_q80_raw.json"

  run_cmd "scripts/run-in-qiskit-venv.sh python qiskit_black_hole_hardware_runner.py --qubits 80 --depths ${depths} --trials 3 --shots 4000 --readout-mitigation --cal-shots 6000 --subset-qubits 0-9 --skip-exact --output-json results/hardware/black_hole_hardware_q80_subset01_mit.json"

  run_cmd "scripts/run-in-qiskit-venv.sh python qiskit_black_hole_hardware_runner.py --qubits 80 --depths ${depths} --trials 3 --shots 4000 --readout-mitigation --cal-shots 6000 --subset-qubits 10-19 --skip-exact --output-json results/hardware/black_hole_hardware_q80_subset02_mit.json"
}

stage_hardware_80_xsup() {
  local depths="1,2,3,4"

  run_cmd "scripts/run-in-qiskit-venv.sh python qiskit_black_hole_hardware_runner.py --qubits 80 --depths ${depths} --trials 3 --shots 4000 --readout-mitigation --cal-shots 6000 --subset-qubits 0-9 --skip-exact --extra-error-suppression --dd-sequence XY4 --twirl-randomizations 8 --output-json results/hardware/black_hole_hardware_q80_subset01_mit_xsup.json"
}

stage_hardware_q80_sidecar() {
  run_cmd "scripts/run-q80-subset-sidecar-bundle.sh --stage all$([[ $EXECUTE -eq 1 ]] && printf ' --execute')"
}

run_stage() {
  case "$1" in
    plan)
      print_plan
      stage_classical_pilot
      stage_hardware_pilot
      stage_hardware_80_subset
      stage_hardware_80_xsup
      stage_hardware_q80_sidecar
      ;;
    classical-pilot)
      print_plan
      stage_classical_pilot
      ;;
    hardware-pilot)
      print_plan
      stage_hardware_pilot
      ;;
    hardware-80-subset)
      print_plan
      stage_hardware_80_subset
      ;;
    hardware-80-xsup)
      print_plan
      stage_hardware_80_xsup
      ;;
    hardware-q80-subset-proxy-sidecar|hardware-q80-sidecar)
      print_plan
      stage_hardware_q80_sidecar
      ;;
    all)
      print_plan
      stage_classical_pilot
      stage_hardware_pilot
      stage_hardware_80_subset
      stage_hardware_80_xsup
      stage_hardware_q80_sidecar
      ;;
    *)
      echo "Unknown stage: $1" >&2
      usage
      exit 2
      ;;
  esac
}

run_stage "$STAGE"
