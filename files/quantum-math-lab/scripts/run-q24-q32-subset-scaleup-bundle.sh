#!/usr/bin/env bash
set -euo pipefail

# q24/q32 subset-locality scale-up bundle.
# Default mode is dry-run (prints commands only).

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${QISKIT_VENV:-/home/bram/.venvs/qiskit}/bin/python"
BACKEND="ibm_fez"
DEPTHS="1,2"
TRIALS=3
SEED=424242
SEED_TRANSPILER=424242
SHOTS=8000
CAL_SHOTS=6000
INITIAL_LAYOUT=""
EXECUTE=0
STAGE="plan"

usage() {
  cat <<'USAGE'
Usage:
  scripts/run-q24-q32-subset-scaleup-bundle.sh [--stage <name>] [--execute] [--backend <name>] [--initial-layout <spec>]

Stages:
  plan     Print all preferred scale-up commands (default)
  q24      Print or run the 24-qubit preferred control set
  q32      Print or run the 32-qubit preferred control set
  all      Print or run both q24 and q32 sets

Flags:
  --execute                 Actually run commands. Without this flag, only prints.
  --backend <name>          IBM backend name (default: ibm_fez)
  --initial-layout <spec>   Optional fixed physical layout in logical-qubit order

Notes:
  - q24 keeps exact references available in the runner.
  - q32 uses --skip-exact and is hardware-only subset-proxy evidence.
  - Preferred shallow-depth control pairs:
    q24: S_A q0 vs q23, S_B q14 vs q0
    q32: S_A q0 vs q31, S_B q22 vs q0
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
    --backend)
      BACKEND="${2:-}"
      shift 2
      ;;
    --initial-layout)
      INITIAL_LAYOUT="${2:-}"
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

mkdir -p results/hardware

run_cmd() {
  local cmd="$1"
  echo
  echo ">> $cmd"
  if (( EXECUTE )); then
    eval "$cmd"
  fi
}

print_plan() {
  echo "=== q24/q32 subset-locality scale-up plan ==="
  echo "Mode: $([[ $EXECUTE -eq 1 ]] && echo EXECUTE || echo DRY-RUN)"
  echo "Backend: $BACKEND"
  echo "Seed transpiler: $SEED_TRANSPILER"
  echo "Initial layout: ${INITIAL_LAYOUT:-<unset>}"
  echo
  echo "Use shallow depths only and judge the runs from readout_mitigated subset echoes."
}

subset_cmd() {
  local qubits="$1"
  local subset_qubits="$2"
  local perturb_qubit="$3"
  local out_json="$4"
  local extra_exact="$5"
  local extra_layout=""

  if [[ -n "$INITIAL_LAYOUT" ]]; then
    extra_layout=" --initial-layout ${INITIAL_LAYOUT}"
  fi

  run_cmd "$PYTHON_BIN qiskit_black_hole_hardware_runner.py \
    --qubits ${qubits} \
    --depths ${DEPTHS} \
    --trials ${TRIALS} \
    --seed ${SEED} \
    --seed-transpiler ${SEED_TRANSPILER} \
    --shots ${SHOTS} \
    --perturb-qubit ${perturb_qubit} \
    --backend ${BACKEND} \
    --subset-qubits ${subset_qubits} \
    --readout-mitigation \
    --cal-shots ${CAL_SHOTS} \
    --extra-error-suppression \
    --dd-sequence XY4 \
    --twirl-randomizations 8${extra_exact} \
    --output-json ${out_json}${extra_layout}"
}

stage_q24() {
  subset_cmd "24" "0-9" "0" "results/hardware/phase3_q24_SA_q0_raw_vs_mit.json" ""
  subset_cmd "24" "0-9" "23" "results/hardware/phase3_q24_SA_q23_raw_vs_mit.json" ""
  subset_cmd "24" "14-23" "14" "results/hardware/phase3_q24_SB_q14_raw_vs_mit.json" ""
  subset_cmd "24" "14-23" "0" "results/hardware/phase3_q24_SB_q0_raw_vs_mit.json" ""
}

stage_q32() {
  subset_cmd "32" "0-9" "0" "results/hardware/phase3_q32_SA_q0_raw_vs_mit.json" " --skip-exact"
  subset_cmd "32" "0-9" "31" "results/hardware/phase3_q32_SA_q31_raw_vs_mit.json" " --skip-exact"
  subset_cmd "32" "22-31" "22" "results/hardware/phase3_q32_SB_q22_raw_vs_mit.json" " --skip-exact"
  subset_cmd "32" "22-31" "0" "results/hardware/phase3_q32_SB_q0_raw_vs_mit.json" " --skip-exact"
}

run_stage() {
  case "$1" in
    plan)
      print_plan
      stage_q24
      stage_q32
      ;;
    q24)
      print_plan
      stage_q24
      ;;
    q32)
      print_plan
      stage_q32
      ;;
    all)
      print_plan
      stage_q24
      stage_q32
      ;;
    *)
      echo "Unknown stage: $1" >&2
      usage
      exit 2
      ;;
  esac
}

run_stage "$STAGE"
