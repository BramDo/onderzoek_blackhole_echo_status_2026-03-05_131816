#!/usr/bin/env python3
"""Calibration-bootstrap diagnostic for paired full-register captures.

This reuses an existing paired hardware job and its all0/all1 calibration job,
then bootstraps only the calibration histograms to estimate sensitivity of the
paired deltas to readout-calibration noise under the existing local model.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Dict, List, Mapping, Tuple

import numpy as np

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from qiskit_black_hole_hardware_runner import (
    _build_runtime_service,
    _distributional_observables_from_counts,
    _estimate_local_readout_params,
    _extract_counts_list_from_sampler_result,
    _hamming_return_linear_from_one_probs,
    _mean_std,
    _mitigate_one_probability,
    _mitigate_p_zero_local_tensor,
    _relative_perturbed_echo,
    _robust_location_summary,
)


def _bootstrap_counts(
    counts: Mapping[str, int],
    shots: int,
    rng: np.random.Generator,
) -> Dict[str, int]:
    keys = list(counts.keys())
    weights = np.asarray([float(counts[k]) for k in keys], dtype=float)
    total = float(np.sum(weights))
    if total <= 0.0:
        raise ValueError("Bootstrap counts require positive total weight.")
    probs = weights / total
    sampled = rng.multinomial(int(shots), probs)
    return {k: int(v) for k, v in zip(keys, sampled) if int(v) > 0}


def _percentile_summary(values: List[float]) -> Dict[str, float]:
    arr = np.asarray(values, dtype=float)
    return {
        **_mean_std(values),
        **_robust_location_summary(values),
        "q025": float(np.percentile(arr, 2.5)),
        "q975": float(np.percentile(arr, 97.5)),
        "positive_rate": float(np.mean(arr > 0.0)),
    }


def _reconstruct_pairs(config: Dict[str, Any]) -> Tuple[List[Dict[str, int]], int]:
    depths = [int(x) for x in config["depths"]]
    trials = int(config["trials"])
    paired_perturb_qubits = [int(x) for x in config["paired_perturb_qubits"]]
    if not paired_perturb_qubits:
        raise ValueError("Source JSON is not a paired capture.")

    pairs: List[Dict[str, int]] = []
    idx = 0
    for depth in depths:
        for trial in range(trials):
            idx_ideal = idx
            idx += 1
            for perturb_qubit in paired_perturb_qubits:
                pairs.append(
                    {
                        "depth": int(depth),
                        "trial": int(trial),
                        "perturb_qubit": int(perturb_qubit),
                        "idx_ideal": idx_ideal,
                        "idx_perturbed": idx,
                    }
                )
                idx += 1
    return pairs, idx


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap calibration uncertainty for paired captures.")
    parser.add_argument("--source-json", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--bootstrap-reps", type=int, default=500)
    parser.add_argument("--seed", type=int, default=424242)
    args = parser.parse_args()

    payload = json.loads(args.source_json.read_text(encoding="utf-8"))
    config = payload["config"]
    runtime = payload["runtime"]
    if not bool(config.get("paired_mode")):
        raise ValueError("Calibration bootstrap currently expects paired_mode=true.")
    if list(config.get("subset_qubits") or []):
        raise ValueError("Calibration bootstrap is currently scoped to full-register captures.")

    hardware_job_id = str(runtime["hardware_job_id"])
    calibration_job_id = str(runtime["calibration_job_id"])
    qubits = int(config["qubits"])
    shots = int(config["shots"])
    cal_shots = int(config["cal_shots"])
    mitigation_qubits_desc = list(range(qubits - 1, -1, -1))

    service = _build_runtime_service()
    hw_result = service.job(hardware_job_id).result()
    cal_result = service.job(calibration_job_id).result()

    pairs, expected_items = _reconstruct_pairs(config)
    hw_counts = _extract_counts_list_from_sampler_result(
        hw_result,
        shots=shots,
        num_bits=qubits,
        n_items=expected_items,
    )
    cal_counts = _extract_counts_list_from_sampler_result(
        cal_result,
        shots=cal_shots,
        num_bits=qubits,
        n_items=2,
    )
    cal0_counts = cal_counts[0]
    cal1_counts = cal_counts[1]

    raw_dists: Dict[Tuple[int, int], Dict[str, object]] = {}
    fixed_counts: Dict[Tuple[int, int], Dict[str, int]] = {}
    for pair in pairs:
        key = (int(pair["trial"]), int(pair["perturb_qubit"]))
        fixed_counts[(key[0], -1)] = hw_counts[pair["idx_ideal"]]
        fixed_counts[key] = hw_counts[pair["idx_perturbed"]]
        raw_dists[(key[0], -1)] = _distributional_observables_from_counts(hw_counts[pair["idx_ideal"]], qubits)
        raw_dists[key] = _distributional_observables_from_counts(hw_counts[pair["idx_perturbed"]], qubits)

    rng = np.random.default_rng(args.seed)
    rel_mean_values: List[float] = []
    rel_median_values: List[float] = []
    ham_mean_values: List[float] = []
    ham_median_values: List[float] = []

    paired_perturb_qubits = [int(x) for x in config["paired_perturb_qubits"]]
    if len(paired_perturb_qubits) != 2:
        raise ValueError("Calibration bootstrap currently expects exactly 2 paired perturb qubits.")
    anchor_q, compare_q = paired_perturb_qubits

    for _ in range(int(args.bootstrap_reps)):
        boot0 = _bootstrap_counts(cal0_counts, shots=cal_shots, rng=rng)
        boot1 = _bootstrap_counts(cal1_counts, shots=cal_shots, rng=rng)
        p01, p10, _ = _estimate_local_readout_params(boot0, boot1, n_qubits=qubits)

        rel_deltas: List[float] = []
        ham_deltas: List[float] = []
        for trial in range(int(config["trials"])):
            trial_rel: Dict[int, float] = {}
            trial_ham: Dict[int, float] = {}
            counts_i = fixed_counts[(trial, -1)]
            raw_i = raw_dists[(trial, -1)]

            mit_i, _ = _mitigate_p_zero_local_tensor(
                counts_i,
                p01=p01,
                p10=p10,
                n_qubits=qubits,
                qubits_desc=mitigation_qubits_desc,
            )
            mitigated_one_probs_i = [
                _mitigate_one_probability(
                    float(raw_i["one_probability_by_qubit"][q]),
                    float(p01[q]),
                    float(p10[q]),
                )
                for q in range(qubits)
            ]
            mit_ham_i = _hamming_return_linear_from_one_probs(mitigated_one_probs_i)

            for perturb_qubit in paired_perturb_qubits:
                counts_p = fixed_counts[(trial, perturb_qubit)]
                raw_p = raw_dists[(trial, perturb_qubit)]
                mit_p, _ = _mitigate_p_zero_local_tensor(
                    counts_p,
                    p01=p01,
                    p10=p10,
                    n_qubits=qubits,
                    qubits_desc=mitigation_qubits_desc,
                )
                mitigated_one_probs_p = [
                    _mitigate_one_probability(
                        float(raw_p["one_probability_by_qubit"][q]),
                        float(p01[q]),
                        float(p10[q]),
                    )
                    for q in range(qubits)
                ]
                mit_ham_p = _hamming_return_linear_from_one_probs(mitigated_one_probs_p)
                trial_rel[perturb_qubit] = float(_relative_perturbed_echo(mit_i, mit_p)["value"])
                trial_ham[perturb_qubit] = float(_relative_perturbed_echo(mit_ham_i, mit_ham_p)["value"])

            rel_deltas.append(float(trial_rel[compare_q] - trial_rel[anchor_q]))
            ham_deltas.append(float(trial_ham[compare_q] - trial_ham[anchor_q]))

        rel_mean_values.append(float(np.mean(rel_deltas)))
        rel_median_values.append(float(np.median(rel_deltas)))
        ham_mean_values.append(float(np.mean(ham_deltas)))
        ham_median_values.append(float(np.median(ham_deltas)))

    out = {
        "diagnostic_only": True,
        "source_json": str(args.source_json),
        "hardware_job_id": hardware_job_id,
        "calibration_job_id": calibration_job_id,
        "bootstrap_reps": int(args.bootstrap_reps),
        "bootstrap_seed": int(args.seed),
        "bootstrap_model": "multinomial_resample_full_all0_all1_calibration_histograms",
        "paired_compare": {
            "anchor_perturb_qubit": int(anchor_q),
            "compare_perturb_qubit": int(compare_q),
        },
        "local_relative_perturbed_echo_delta": {
            "bootstrap_mean_of_trial_deltas": _percentile_summary(rel_mean_values),
            "bootstrap_median_of_trial_deltas": _percentile_summary(rel_median_values),
        },
        "local_relative_hamming_return_linear_delta": {
            "bootstrap_mean_of_trial_deltas": _percentile_summary(ham_mean_values),
            "bootstrap_median_of_trial_deltas": _percentile_summary(ham_median_values),
        },
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(args.output_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
