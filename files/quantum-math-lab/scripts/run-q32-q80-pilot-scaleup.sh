#!/usr/bin/env bash
set -euo pipefail

STAGE="plan"
EXECUTE=0
BACKEND="ibm_fez"
SHOTS=8000
CAL_SHOTS=6000
SEED=424242
SEED_TRANSPILER=424242
INITIAL_LAYOUT=""

usage() {
  cat <<'EOF'
Usage:
  scripts/run-q32-q80-pilot-scaleup.sh [--stage plan|q32|q80|all] [--execute]
                                     [--backend BACKEND] [--shots N]
                                     [--cal-shots N] [--seed N]
                                     [--seed-transpiler N]
                                     [--initial-layout LAYOUT]

Stages:
  plan   Print both pilot pairs only (default)
  q32    Print/run the q32 pilot pair
  q80    Print/run the q80 pilot pair
  all    Print/run q32 first, then q80

Notes:
  - Dry-run by default. Add --execute to actually launch jobs.
  - q32 pilot: subset 0-9, q=0 vs q=31
  - q80 pilot: subset 0-9, q=0 vs q=79
  - Both use skip-exact, shallow depths 1,2, readout mitigation, XY4, twirling.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --stage)
      STAGE="$2"
      shift 2
      ;;
    --execute)
      EXECUTE=1
      shift
      ;;
    --backend)
      BACKEND="$2"
      shift 2
      ;;
    --shots)
      SHOTS="$2"
      shift 2
      ;;
    --cal-shots)
      CAL_SHOTS="$2"
      shift 2
      ;;
    --seed)
      SEED="$2"
      shift 2
      ;;
    --seed-transpiler)
      SEED_TRANSPILER="$2"
      shift 2
      ;;
    --initial-layout)
      INITIAL_LAYOUT="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

PYTHON_BIN="/home/bram/.venvs/qiskit/bin/python"
RUNNER="qiskit_black_hole_hardware_runner.py"
COMMON_ARGS=(
  --depths 1,2
  --trials 3
  --seed "$SEED"
  --seed-transpiler "$SEED_TRANSPILER"
  --shots "$SHOTS"
  --backend "$BACKEND"
  --subset-qubits 0-9
  --skip-exact
  --readout-mitigation
  --cal-shots "$CAL_SHOTS"
  --extra-error-suppression
  --dd-sequence XY4
  --twirl-randomizations 8
)

if [[ -n "$INITIAL_LAYOUT" ]]; then
  COMMON_ARGS+=(--initial-layout "$INITIAL_LAYOUT")
fi

run_cmd() {
  echo
  printf '%q ' "$@"
  echo
  if [[ "$EXECUTE" -eq 1 ]]; then
    "$@"
  fi
}

run_q32() {
  run_cmd "$PYTHON_BIN" "$RUNNER" \
    --qubits 32 \
    "${COMMON_ARGS[@]}" \
    --perturb-qubit 0 \
    --output-json results/hardware/phase3_q32_SA_q0_raw_vs_mit.json

  run_cmd "$PYTHON_BIN" "$RUNNER" \
    --qubits 32 \
    "${COMMON_ARGS[@]}" \
    --perturb-qubit 31 \
    --output-json results/hardware/phase3_q32_SA_q31_raw_vs_mit.json
}

run_q80() {
  run_cmd "$PYTHON_BIN" "$RUNNER" \
    --qubits 80 \
    "${COMMON_ARGS[@]}" \
    --perturb-qubit 0 \
    --output-json results/hardware/phase3_q80pilot_SA_q0_raw_vs_mit.json

  run_cmd "$PYTHON_BIN" "$RUNNER" \
    --qubits 80 \
    "${COMMON_ARGS[@]}" \
    --perturb-qubit 79 \
    --output-json results/hardware/phase3_q80pilot_SA_q79_raw_vs_mit.json
}

case "$STAGE" in
  plan)
    run_q32
    run_q80
    ;;
  q32)
    run_q32
    ;;
  q80)
    run_q80
    ;;
  all)
    run_q32
    run_q80
    ;;
  *)
    echo "Unknown stage: $STAGE" >&2
    usage >&2
    exit 1
    ;;
esac
