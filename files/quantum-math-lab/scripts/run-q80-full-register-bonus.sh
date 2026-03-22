#!/usr/bin/env bash
set -euo pipefail

# Exploratory, non-destructive full-register q80 run path.
# This does NOT replace the existing subset-locality evidence chain.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

STAGE="plan"
EXECUTE=0
BACKEND="ibm_fez"
DEPTHS="1,2"
TRIALS=3
SEED=424242
SEED_TRANSPILER=424242
SHOTS=8000
CAL_SHOTS=6000
BOOTSTRAP_REPS=100
INITIAL_LAYOUT=""
OUT_DIR="results/hardware/bonus_full_q80_2026-03-21"
PYTHON_BIN="${QISKIT_VENV:-/home/bram/.venvs/qiskit}/bin/python"
RUNNER="qiskit_black_hole_hardware_runner.py"
RECOMMENDED_LAYOUT_CSV="3,2,4,5,16,23,1,0,6,7,22,21,24,25,8,9,17,27,36,41,37,45,10,11,28,29,42,43,46,47,12,13,18,31,38,49,56,63,57,67,14,15,32,33,50,51,62,61,64,65,68,69,19,35,39,53,58,71,76,81,77,85,78,89,54,55,72,73,82,83,86,87,90,91,59,75,79,93,96,103"
PAIRED_CAPTURE_HW_JOB_ID="d6vblg2f84ks73df5680"
PAIRED_CAPTURE_CAL_JOB_ID="d6vblrgv5rlc73f4qq80"

usage() {
  cat <<'EOF'
Usage:
  scripts/run-q80-full-register-bonus.sh [--stage plan|overlap|far|pair|rerun_shallow_stability|depth2_layout_rerun|depth2_shot_increase|depth2_paired_capture|depth2_paired_m3_reuse|depth2_paired_cal_bootstrap|depth2_paired_blockz_reuse|depth2_paired_tem_pilot]
                                        [--execute] [--backend BACKEND]
                                        [--depths CSV] [--trials N]
                                        [--shots N] [--cal-shots N]
                                        [--bootstrap-reps N]
                                        [--seed N] [--seed-transpiler N]
                                        [--initial-layout LAYOUT]
                                        [--out-dir PATH]

Stages:
  plan     Print both exploratory full-register q80 commands (default)
  overlap  Only overlap branch q=0
  far      Only far-disjoint branch q=79
  pair     Print/run both q=0 and q=79
  rerun_shallow_stability
           Non-destructive shallow rerun pair with 5 trials in a subfolder
  depth2_layout_rerun
           Depth-2-only rerun pair with the transpiler-derived fixed layout
  depth2_shot_increase
           Depth-2-only rerun pair on the cleaner no-layout protocol at 16000 shots
  depth2_paired_capture
           Depth-2-only paired q=0/q=79 capture with one shared hardware job and shared calibration
  depth2_paired_m3_reuse
           Re-read the existing paired capture through marginal-calibrated M3 using the saved job ids
  depth2_paired_cal_bootstrap
           Bootstrap calibration uncertainty on the existing paired capture under the local mitigation model
  depth2_paired_blockz_reuse
           Re-read the existing paired capture with front10/back10 block-Z observables under the local mitigation model
  depth2_paired_tem_pilot
           Separate Algorithmiq TEM pilot on the same logical depth-2 paired q=0/q=79 circuits,
           targeting TEM-native magnetization/Hamming observables instead of p_zero

Notes:
  - This path is additive only: outputs go to a dedicated bonus folder.
  - It runs full-register q80 state-return statistics (`perturbed_echo`),
    not a proven full-q80 fixed-observable OLE estimator.
  - It uses skip-exact, readout mitigation, XY4, and gate twirling.
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
    --depths)
      DEPTHS="$2"
      shift 2
      ;;
    --trials)
      TRIALS="$2"
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
    --bootstrap-reps)
      BOOTSTRAP_REPS="$2"
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
    --out-dir)
      OUT_DIR="$2"
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

mkdir -p "$OUT_DIR"

COMMON_ARGS=(
  --qubits 80
  --depths "$DEPTHS"
  --trials "$TRIALS"
  --seed "$SEED"
  --seed-transpiler "$SEED_TRANSPILER"
  --shots "$SHOTS"
  --backend "$BACKEND"
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

run_overlap() {
  run_cmd "$PYTHON_BIN" "$RUNNER" \
    "${COMMON_ARGS[@]}" \
    --perturb-qubit 0 \
    --output-json "$OUT_DIR/full_q80_q0_raw_vs_mit.json"
}

run_far() {
  run_cmd "$PYTHON_BIN" "$RUNNER" \
    "${COMMON_ARGS[@]}" \
    --perturb-qubit 79 \
    --output-json "$OUT_DIR/full_q80_q79_raw_vs_mit.json"
}

run_shallow_stability_rerun() {
  local stability_dir="${OUT_DIR}/rerun_shallow_stability"
  local stability_args=(
    --qubits 80
    --depths 1,2
    --trials 5
    --seed "$SEED"
    --seed-transpiler "$SEED_TRANSPILER"
    --shots "$SHOTS"
    --backend "$BACKEND"
    --skip-exact
    --readout-mitigation
    --cal-shots "$CAL_SHOTS"
    --extra-error-suppression
    --dd-sequence XY4
    --twirl-randomizations 8
  )
  mkdir -p "$stability_dir"
  if [[ -n "$INITIAL_LAYOUT" ]]; then
    stability_args+=(--initial-layout "$INITIAL_LAYOUT")
  fi

  run_cmd "$PYTHON_BIN" "$RUNNER" \
    "${stability_args[@]}" \
    --perturb-qubit 0 \
    --output-json "$stability_dir/full_q80_q0_raw_vs_mit_t5.json"

  run_cmd "$PYTHON_BIN" "$RUNNER" \
    "${stability_args[@]}" \
    --perturb-qubit 79 \
    --output-json "$stability_dir/full_q80_q79_raw_vs_mit_t5.json"
}

run_depth2_layout_rerun() {
  local layout_dir="${OUT_DIR}/depth2_layout_rerun"
  local layout_args=(
    --qubits 80
    --depths 2
    --trials 5
    --seed "$SEED"
    --seed-transpiler "$SEED_TRANSPILER"
    --shots "$SHOTS"
    --backend "$BACKEND"
    --skip-exact
    --readout-mitigation
    --cal-shots "$CAL_SHOTS"
    --extra-error-suppression
    --dd-sequence XY4
    --twirl-randomizations 8
    --initial-layout "$RECOMMENDED_LAYOUT_CSV"
  )
  mkdir -p "$layout_dir"

  run_cmd "$PYTHON_BIN" "$RUNNER" \
    "${layout_args[@]}" \
    --perturb-qubit 0 \
    --output-json "$layout_dir/full_q80_q0_raw_vs_mit_t5_layout.json"

  run_cmd "$PYTHON_BIN" "$RUNNER" \
    "${layout_args[@]}" \
    --perturb-qubit 79 \
    --output-json "$layout_dir/full_q80_q79_raw_vs_mit_t5_layout.json"
}

run_depth2_shot_increase() {
  local shot_dir="${OUT_DIR}/depth2_shot_increase"
  local shot_args=(
    --qubits 80
    --depths 2
    --trials 5
    --seed "$SEED"
    --seed-transpiler "$SEED_TRANSPILER"
    --shots 16000
    --backend "$BACKEND"
    --skip-exact
    --readout-mitigation
    --cal-shots "$CAL_SHOTS"
    --extra-error-suppression
    --dd-sequence XY4
    --twirl-randomizations 8
  )
  mkdir -p "$shot_dir"

  run_cmd "$PYTHON_BIN" "$RUNNER" \
    "${shot_args[@]}" \
    --perturb-qubit 0 \
    --output-json "$shot_dir/full_q80_q0_raw_vs_mit_t5_s16000.json"

  run_cmd "$PYTHON_BIN" "$RUNNER" \
    "${shot_args[@]}" \
    --perturb-qubit 79 \
    --output-json "$shot_dir/full_q80_q79_raw_vs_mit_t5_s16000.json"
}

run_depth2_paired_capture() {
  local paired_dir="${OUT_DIR}/depth2_paired_capture"
  local paired_args=(
    --qubits 80
    --depths 2
    --trials 5
    --seed "$SEED"
    --seed-transpiler "$SEED_TRANSPILER"
    --shots "$SHOTS"
    --backend "$BACKEND"
    --skip-exact
    --readout-mitigation
    --cal-shots "$CAL_SHOTS"
    --extra-error-suppression
    --dd-sequence XY4
    --twirl-randomizations 8
    --paired-perturb-qubits 0,79
  )
  mkdir -p "$paired_dir"
  if [[ -n "$INITIAL_LAYOUT" ]]; then
    paired_args+=(--initial-layout "$INITIAL_LAYOUT")
  fi

  run_cmd "$PYTHON_BIN" "$RUNNER" \
    "${paired_args[@]}" \
    --output-json "$paired_dir/full_q80_q0_q79_paired_t5.json"
}

run_depth2_paired_m3_reuse() {
  local m3_dir="${OUT_DIR}/depth2_paired_m3_reuse"
  local m3_args=(
    --qubits 80
    --depths 2
    --trials 5
    --seed 424242
    --seed-transpiler 424242
    --shots 8000
    --backend "$BACKEND"
    --skip-exact
    --readout-mitigation
    --readout-mitigation-method m3
    --cal-shots 6000
    --paired-perturb-qubits 0,79
    --reuse-hardware-job-id "$PAIRED_CAPTURE_HW_JOB_ID"
    --reuse-calibration-job-id "$PAIRED_CAPTURE_CAL_JOB_ID"
  )
  mkdir -p "$m3_dir"

  run_cmd "$PYTHON_BIN" "$RUNNER" \
    "${m3_args[@]}" \
    --output-json "$m3_dir/full_q80_q0_q79_paired_t5_m3.json"
}

run_depth2_paired_cal_bootstrap() {
  local boot_dir="${OUT_DIR}/depth2_paired_cal_bootstrap"
  mkdir -p "$boot_dir"

  run_cmd "$PYTHON_BIN" scripts/analyze-paired-calibration-bootstrap.py \
    --source-json "${OUT_DIR}/depth2_paired_capture/full_q80_q0_q79_paired_t5.json" \
    --output-json "${boot_dir}/full_q80_q0_q79_paired_t5_local_cal_bootstrap.json" \
    --bootstrap-reps "$BOOTSTRAP_REPS" \
    --seed 424242
}

run_depth2_paired_blockz_reuse() {
  local blockz_dir="${OUT_DIR}/depth2_paired_blockz_reuse"
  local blockz_args=(
    --qubits 80
    --depths 2
    --trials 5
    --seed 424242
    --seed-transpiler 424242
    --shots 8000
    --backend "$BACKEND"
    --skip-exact
    --readout-mitigation
    --readout-mitigation-method local
    --cal-shots 6000
    --paired-perturb-qubits 0,79
    --z-observable-blocks "front10:0-9;back10:70-79"
    --reuse-hardware-job-id "$PAIRED_CAPTURE_HW_JOB_ID"
    --reuse-calibration-job-id "$PAIRED_CAPTURE_CAL_JOB_ID"
  )
  mkdir -p "$blockz_dir"

  run_cmd "$PYTHON_BIN" "$RUNNER" \
    "${blockz_args[@]}" \
    --output-json "$blockz_dir/full_q80_q0_q79_paired_t5_blockz_front10_back10.json"
}

run_depth2_paired_tem_pilot() {
  local tem_dir="${OUT_DIR}/depth2_paired_tem_pilot"
  mkdir -p "$tem_dir"

  run_cmd "$PYTHON_BIN" scripts/run-paired-tem-pilot.py \
    --qubits 80 \
    --depths 2 \
    --trials 5 \
    --seed 424242 \
    --backend "$BACKEND" \
    --paired-perturb-qubits 0,79 \
    --default-precision 0.03 \
    --num-readout-calibration-shots 6000 \
    --num-randomizations 8 \
    --compute-shadows-bias-from-observable \
    --output-json "${tem_dir}/full_q80_q0_q79_paired_t5_tem_hamming.json"
}

case "$STAGE" in
  plan)
    run_overlap
    run_far
    ;;
  overlap)
    run_overlap
    ;;
  far)
    run_far
    ;;
  pair)
    run_overlap
    run_far
    ;;
  rerun_shallow_stability)
    run_shallow_stability_rerun
    ;;
  depth2_layout_rerun)
    run_depth2_layout_rerun
    ;;
  depth2_shot_increase)
    run_depth2_shot_increase
    ;;
  depth2_paired_capture)
    run_depth2_paired_capture
    ;;
  depth2_paired_m3_reuse)
    run_depth2_paired_m3_reuse
    ;;
  depth2_paired_cal_bootstrap)
    run_depth2_paired_cal_bootstrap
    ;;
  depth2_paired_blockz_reuse)
    run_depth2_paired_blockz_reuse
    ;;
  depth2_paired_tem_pilot)
    run_depth2_paired_tem_pilot
    ;;
  *)
    echo "Unknown stage: $STAGE" >&2
    usage >&2
    exit 1
    ;;
esac
