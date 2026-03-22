#!/usr/bin/env bash
set -euo pipefail

# q20 subset-locality bundle with optional PE-LiNN diagnostic sidecar.
# Default mode is dry-run (prints commands only).

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${QISKIT_VENV:-/home/bram/.venvs/qiskit}/bin/python"
BACKEND="ibm_fez"
DEPTHS="1,2,3,4"
TRIALS=3
SEED=424242
SEED_TRANSPILER=424242
SHOTS=8000
CAL_SHOTS=6000
SIDEcar_CKPT="results/hardware/phase3_q80_subset_pelinn_sidecar_s16/q80_subset_pelinn_sidecar.pt"
INITIAL_LAYOUT=""
EXECUTE=0
STAGE="plan"

usage() {
  cat <<'USAGE'
Usage:
  scripts/run-q80-subset-sidecar-bundle.sh [--stage <name>] [--execute] [--backend <name>] [--sidecar-checkpoint <path>] [--initial-layout <spec>]

Stages:
  plan    Print all q20 subset sidecar commands (default)
  sa-q0   Subset S_A=0-9, overlap branch q=0
  sa-q19  Subset S_A=0-9, preferred far-disjoint branch q=19
  sa-q10  Subset S_A=0-9, diagnostic near-disjoint branch q=10
  sb-q10  Subset S_B=10-19, overlap branch q=10
  sb-q0   Subset S_B=10-19, preferred far-disjoint branch q=0
  all     Print or run the preferred four-command set

Flags:
  --execute                   Actually run commands. Without this flag, only prints.
  --backend <name>            IBM backend name (default: ibm_fez)
  --sidecar-checkpoint <path> PE-LiNN diagnostic checkpoint path
  --initial-layout <spec>     Optional fixed physical layout in logical-qubit order

Notes:
  - ml_diagnostic is diagnostic-only and does not replace readout_mitigated.
  - This is the canonical q20 subset-sidecar runner.
  - The older run-q80-subset-sidecar-bundle.sh name is kept only as a legacy alias.
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
    --sidecar-checkpoint)
      SIDEcar_CKPT="${2:-}"
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
  echo "=== q20 subset-locality sidecar plan ==="
  echo "Mode: $([[ $EXECUTE -eq 1 ]] && echo EXECUTE || echo DRY-RUN)"
  echo "Backend: $BACKEND"
  echo "Sidecar checkpoint: $SIDEcar_CKPT"
  echo "Seed transpiler: $SEED_TRANSPILER"
  echo "Initial layout: ${INITIAL_LAYOUT:-<unset>}"
  echo
  echo "This bundle emits raw + readout_mitigated + ml_diagnostic."
  echo "Use readout_mitigated as the primary result."
}

subset_cmd() {
  local subset_label="$1"
  local subset_qubits="$2"
  local perturb_qubit="$3"
  local out_json="$4"
  local extra_layout=""
  if [[ -n "$INITIAL_LAYOUT" ]]; then
    extra_layout=" --initial-layout ${INITIAL_LAYOUT}"
  fi

  run_cmd "$PYTHON_BIN qiskit_black_hole_hardware_runner.py \
    --qubits 20 \
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
    --twirl-randomizations 8 \
    --ml-sidecar-checkpoint ${SIDEcar_CKPT} \
    --output-json ${out_json}${extra_layout}"
}

stage_sa_q0() {
  subset_cmd "S_A" "0-9" "0" "results/hardware/phase3_q20_SA_q0_raw_vs_mit.json"
}

stage_sa_q10() {
  subset_cmd "S_A" "0-9" "10" "results/hardware/phase3_q20_SA_q10_raw_vs_mit.json"
}

stage_sa_q19() {
  subset_cmd "S_A" "0-9" "19" "results/hardware/phase3_q20_SA_q19_raw_vs_mit.json"
}

stage_sb_q0() {
  subset_cmd "S_B" "10-19" "0" "results/hardware/phase3_q20_SB_q0_raw_vs_mit.json"
}

stage_sb_q10() {
  subset_cmd "S_B" "10-19" "10" "results/hardware/phase3_q20_SB_q10_raw_vs_mit.json"
}

run_stage() {
  case "$1" in
    plan)
      print_plan
      stage_sa_q0
      stage_sa_q19
      stage_sb_q10
      stage_sb_q0
      ;;
    sa-q0)
      print_plan
      stage_sa_q0
      ;;
    sa-q10)
      print_plan
      stage_sa_q10
      ;;
    sa-q19)
      print_plan
      stage_sa_q19
      ;;
    sb-q0)
      print_plan
      stage_sb_q0
      ;;
    sb-q10)
      print_plan
      stage_sb_q10
      ;;
    all)
      print_plan
      stage_sa_q0
      stage_sa_q19
      stage_sb_q10
      stage_sb_q0
      ;;
    *)
      echo "Unknown stage: $1" >&2
      usage
      exit 2
      ;;
  esac
}

run_stage "$STAGE"
