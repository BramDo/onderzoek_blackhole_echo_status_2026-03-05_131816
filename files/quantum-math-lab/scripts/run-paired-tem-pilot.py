#!/usr/bin/env python3
"""Run a paired q80 TEM pilot on magnetization-based observables.

This is an additive bonus-path pilot for Algorithmiq TEM. It does not replace
the existing sampler-based full-register evidence chain.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

import numpy as np
from qiskit.quantum_info import SparsePauliOp

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from qiskit_black_hole_hardware_runner import (
    _mad_trimmed_diagnostic,
    _mean_std,
    _relative_perturbed_echo,
    _robust_location_summary,
    _stability_report,
)
from qiskit_black_hole_scrambling import (
    brickwork_scrambler,
    build_echo_measurement_circuits,
    parse_depths,
)


VARIANT_KEYS = [
    "tem_mitigated",
    "non_mitigated",
    "tem_mitigated_no_readout",
    "non_mitigated_with_readout_mitigation",
]


def _parse_subset_qubits(spec: str, n_qubits: int) -> List[int]:
    if not spec.strip():
        raise ValueError("paired-perturb-qubits is leeg")
    out: List[int] = []
    for token in spec.split(","):
        tok = token.strip()
        if not tok:
            continue
        value = int(tok)
        if not (0 <= value < n_qubits):
            raise ValueError(f"qubit {value} valt buiten bereik 0..{n_qubits - 1}")
        out.append(value)
    if len(out) < 2:
        raise ValueError("paired-perturb-qubits moet minstens 2 qubits bevatten")
    return out


def _single_qubit_z_label(n_qubits: int, qubit: int) -> str:
    chars = ["I"] * n_qubits
    chars[n_qubits - 1 - qubit] = "Z"
    return "".join(chars)


def _build_tem_observables(n_qubits: int) -> Tuple[List[SparsePauliOp], Dict[str, object]]:
    mean_terms = [(_single_qubit_z_label(n_qubits, q), 1.0 / float(n_qubits)) for q in range(n_qubits)]
    observables: List[SparsePauliOp] = [SparsePauliOp.from_list(mean_terms)]
    observable_labels = ["global_mean_z"]
    for q in range(n_qubits):
        observables.append(SparsePauliOp.from_list([(_single_qubit_z_label(n_qubits, q), 1.0)]))
        observable_labels.append(f"z_q{q}")
    return observables, {"labels": observable_labels, "num_observables": len(observables)}


def _strip_final_measurements(circuit):
    return circuit.remove_final_measurements(inplace=False)


def _json_safe(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return [_json_safe(x) for x in value.tolist()]
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    return value


def _extract_vector(meta: Mapping[str, Any], ev_key: str, std_key: str) -> Optional[Tuple[List[float], List[float]]]:
    if ev_key not in meta or std_key not in meta:
        return None
    evs = np.asarray(meta[ev_key], dtype=float).reshape(-1)
    stds = np.asarray(meta[std_key], dtype=float).reshape(-1)
    return ([float(x) for x in evs.tolist()], [float(x) for x in stds.tolist()])


def _metrics_from_vector(evs: Iterable[float], stds: Iterable[float]) -> Dict[str, object]:
    ev_arr = np.asarray(list(evs), dtype=float)
    std_arr = np.asarray(list(stds), dtype=float)
    if ev_arr.size < 1:
        raise ValueError("TEM result bevat geen observables")

    global_mean_z = float(ev_arr[0])
    global_mean_z_std = float(std_arr[0]) if std_arr.size >= 1 else 0.0
    local_z = [float(x) for x in ev_arr[1:].tolist()]
    local_z_std = [float(x) for x in std_arr[1:].tolist()] if std_arr.size > 1 else [0.0] * len(local_z)
    one_probs = [float(np.clip(0.5 * (1.0 - z), 0.0, 1.0)) for z in local_z]
    hamming_return_linear = float(np.clip(0.5 * (1.0 + global_mean_z), 0.0, 1.0))
    return {
        "global_mean_z": global_mean_z,
        "global_mean_z_std": global_mean_z_std,
        "mean_excitation_fraction": float(np.clip(1.0 - hamming_return_linear, 0.0, 1.0)),
        "hamming_return_linear": hamming_return_linear,
        "hamming_return_linear_std": float(abs(global_mean_z_std) * 0.5),
        "z_expectation_by_qubit": local_z,
        "z_expectation_std_by_qubit": local_z_std,
        "one_probability_by_qubit": one_probs,
    }


def _extract_variant_metrics(pub_result: Any) -> Dict[str, Dict[str, object]]:
    out: Dict[str, Dict[str, object]] = {}
    data = getattr(pub_result, "data")
    meta = dict(getattr(pub_result, "metadata", {}) or {})

    out["tem_mitigated"] = _metrics_from_vector(
        np.asarray(getattr(data, "evs"), dtype=float).reshape(-1),
        np.asarray(getattr(data, "stds"), dtype=float).reshape(-1),
    )

    extra_keys = {
        "non_mitigated": ("evs_non_mitigated", "stds_non_mitigated"),
        "tem_mitigated_no_readout": (
            "evs_mitigated_no_readout_mitigation",
            "stds_mitigated_no_readout_mitigation",
        ),
        "non_mitigated_with_readout_mitigation": (
            "evs_non_mitigated_with_readout_mitigation",
            "stds_non_mitigated_with_readout_mitigation",
        ),
    }
    for out_key, (ev_key, std_key) in extra_keys.items():
        vector = _extract_vector(meta, ev_key=ev_key, std_key=std_key)
        if vector is not None:
            out[out_key] = _metrics_from_vector(vector[0], vector[1])
    return out


def _aggregate_branch(rows: List[Dict[str, object]]) -> Dict[str, object]:
    out: Dict[str, object] = {}
    for variant in VARIANT_KEYS:
        if variant not in rows[0]["variants"]:
            continue
        ideal_vals = [float(r["ideal_variants"][variant]["hamming_return_linear"]) for r in rows]
        pert_vals = [float(r["variants"][variant]["hamming_return_linear"]) for r in rows]
        rel_vals = [float(r["relative"][variant]["relative_hamming_return_linear"]) for r in rows]
        out[variant] = {
            "ideal_hamming_return_linear": _mean_std(ideal_vals),
            "perturbed_hamming_return_linear": _mean_std(pert_vals),
            "relative_hamming_return_linear": _mean_std(rel_vals),
            "relative_hamming_return_linear_stability": _stability_report(rel_vals),
            "relative_hamming_return_linear_robust": _robust_location_summary(rel_vals),
        }
    return out


def _aggregate_paired(rows: List[Dict[str, object]], perturb_qubits: List[int]) -> Dict[str, object]:
    anchor = int(perturb_qubits[0])
    compare = int(perturb_qubits[1])
    keyed = {(int(r["depth"]), int(r["trial"]), int(r["perturb_qubit"])): r for r in rows}

    out: Dict[str, object] = {
        "anchor_perturb_qubit": anchor,
        "compare_perturb_qubit": compare,
    }
    for variant in VARIANT_KEYS:
        deltas: List[float] = []
        for depth in sorted({int(r["depth"]) for r in rows}):
            for trial in sorted({int(r["trial"]) for r in rows if int(r["depth"]) == depth}):
                anchor_row = keyed.get((depth, trial, anchor))
                compare_row = keyed.get((depth, trial, compare))
                if anchor_row is None or compare_row is None:
                    continue
                if variant not in anchor_row["relative"] or variant not in compare_row["relative"]:
                    continue
                delta = float(
                    compare_row["relative"][variant]["relative_hamming_return_linear"]
                    - anchor_row["relative"][variant]["relative_hamming_return_linear"]
                )
                deltas.append(delta)
        if deltas:
            out[variant] = {
                "relative_hamming_return_linear_delta": _mean_std(deltas),
                "relative_hamming_return_linear_delta_stability": _stability_report(deltas),
                "relative_hamming_return_linear_delta_robust": _robust_location_summary(deltas),
                "relative_hamming_return_linear_delta_trimmed_diagnostic": _mad_trimmed_diagnostic(deltas),
            }
    return out


def _build_options(args: argparse.Namespace) -> Dict[str, Any]:
    options: Dict[str, Any] = {
        "seed": int(args.seed),
        "mitigate_readout_error": True,
        "num_readout_calibration_shots": int(args.num_readout_calibration_shots),
        "num_randomizations": int(args.num_randomizations),
    }
    if args.compute_shadows_bias_from_observable:
        options["compute_shadows_bias_from_observable"] = True
    if args.default_shots is not None:
        options["default_shots"] = int(args.default_shots)
    else:
        options["default_precision"] = float(args.default_precision)
    if args.max_execution_time is not None:
        options["max_execution_time"] = int(args.max_execution_time)
    return options


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a paired Algorithmiq TEM pilot on q80 echo circuits.")
    parser.add_argument("--qubits", type=int, default=80)
    parser.add_argument("--depths", type=str, default="2")
    parser.add_argument("--trials", type=int, default=5)
    parser.add_argument("--seed", type=int, default=424242)
    parser.add_argument("--backend", type=str, default="ibm_fez")
    parser.add_argument("--paired-perturb-qubits", type=str, default="0,79")
    parser.add_argument("--channel", type=str, default="ibm_quantum_platform")
    parser.add_argument("--default-precision", type=float, default=0.03)
    parser.add_argument("--default-shots", type=int, default=None)
    parser.add_argument("--num-readout-calibration-shots", type=int, default=6000)
    parser.add_argument("--num-randomizations", type=int, default=8)
    parser.add_argument("--max-execution-time", type=int, default=None)
    parser.add_argument("--compute-shadows-bias-from-observable", action="store_true")
    parser.add_argument("--plan-only", action="store_true")
    parser.add_argument("--output-json", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    depths = parse_depths(args.depths)
    perturb_qubits = _parse_subset_qubits(args.paired_perturb_qubits, n_qubits=args.qubits)
    observables, observable_info = _build_tem_observables(args.qubits)

    master_rng = np.random.default_rng(args.seed)
    pubs = []
    pub_meta: List[Dict[str, object]] = []
    logical_circuits: List[object] = []

    for depth in depths:
        for trial in range(args.trials):
            trial_seed = int(master_rng.integers(0, 2**32 - 1))
            rng = np.random.default_rng(trial_seed)
            u_circuit = brickwork_scrambler(args.qubits, depth=depth, rng=rng)

            ideal_meas, _ = build_echo_measurement_circuits(
                u_circuit=u_circuit,
                n_qubits=args.qubits,
                perturb_qubit=perturb_qubits[0],
            )
            ideal = _strip_final_measurements(ideal_meas)
            pubs.append((ideal, observables))
            logical_circuits.append(ideal)
            pub_meta.append(
                {
                    "depth": int(depth),
                    "trial": int(trial),
                    "seed": int(trial_seed),
                    "kind": "ideal",
                }
            )

            for perturb_qubit in perturb_qubits:
                _, pert_meas = build_echo_measurement_circuits(
                    u_circuit=u_circuit,
                    n_qubits=args.qubits,
                    perturb_qubit=perturb_qubit,
                )
                pert = _strip_final_measurements(pert_meas)
                pubs.append((pert, observables))
                logical_circuits.append(pert)
                pub_meta.append(
                    {
                        "depth": int(depth),
                        "trial": int(trial),
                        "seed": int(trial_seed),
                        "kind": "perturbed",
                        "perturb_qubit": int(perturb_qubit),
                    }
                )

    plan_summary = {
        "plan_only": True,
        "backend": args.backend,
        "channel": args.channel,
        "qubits": int(args.qubits),
        "depths": depths,
        "trials": int(args.trials),
        "paired_perturb_qubits": [int(x) for x in perturb_qubits],
        "num_pubs": len(pubs),
        "observables": observable_info,
        "options": _build_options(args),
        "output_json": str(args.output_json),
    }
    if args.plan_only:
        print(json.dumps(plan_summary, indent=2))
        return 0

    try:
        from qiskit_ibm_catalog import QiskitFunctionsCatalog
    except Exception as exc:
        print(
            "TEM pilot vereist qiskit_ibm_catalog in de qiskit-venv. "
            f"Import faalde: {exc}",
            file=sys.stderr,
        )
        return 1

    try:
        catalog = QiskitFunctionsCatalog(channel=args.channel)
        tem = catalog.load("algorithmiq/tem")
    except Exception as exc:
        print(
            "TEM function laden faalde. Controleer IBM Quantum Platform account/access "
            f"voor algorithmiq/tem. Detail: {exc}",
            file=sys.stderr,
        )
        return 1

    options = _build_options(args)
    try:
        job = tem.run(
            pubs=pubs,
            backend_name=args.backend,
            options=options,
        )
        result = job.result()
    except Exception as exc:
        print(f"TEM run faalde: {exc}", file=sys.stderr)
        return 1

    job_id = getattr(job, "job_id", None)
    if callable(job_id):
        job_id = job_id()
    status = getattr(job, "status", None)
    if callable(status):
        try:
            status = status()
        except Exception:
            status = None

    ideal_by_key: Dict[Tuple[int, int], Dict[str, object]] = {}
    rows: List[Dict[str, object]] = []

    for meta, pub_result in zip(pub_meta, result):
        metrics = _extract_variant_metrics(pub_result)
        payload = {
            "depth": int(meta["depth"]),
            "trial": int(meta["trial"]),
            "seed": int(meta["seed"]),
            "variants": metrics,
            "metadata": _json_safe(getattr(pub_result, "metadata", {}) or {}),
        }
        if meta["kind"] == "ideal":
            ideal_by_key[(int(meta["depth"]), int(meta["trial"]))] = payload
            continue

        perturb_qubit = int(meta["perturb_qubit"])
        ideal_payload = ideal_by_key[(int(meta["depth"]), int(meta["trial"]))]
        relative: Dict[str, Dict[str, float]] = {}
        for variant in VARIANT_KEYS:
            if variant not in metrics or variant not in ideal_payload["variants"]:
                continue
            rel = _relative_perturbed_echo(
                float(ideal_payload["variants"][variant]["hamming_return_linear"]),
                float(metrics[variant]["hamming_return_linear"]),
            )
            relative[variant] = {
                "relative_hamming_return_linear": float(rel["value"]),
                "relative_hamming_return_linear_unclipped": float(rel["unclipped"]),
            }

        rows.append(
            {
                "depth": int(meta["depth"]),
                "trial": int(meta["trial"]),
                "seed": int(meta["seed"]),
                "perturb_qubit": perturb_qubit,
                "ideal_variants": ideal_payload["variants"],
                "ideal_metadata": ideal_payload["metadata"],
                "variants": metrics,
                "metadata": _json_safe(getattr(pub_result, "metadata", {}) or {}),
                "relative": relative,
            }
        )

    branches: Dict[str, object] = {}
    for perturb_qubit in perturb_qubits:
        branch_rows = [r for r in rows if int(r["perturb_qubit"]) == int(perturb_qubit)]
        branches[str(int(perturb_qubit))] = _aggregate_branch(branch_rows)

    out = {
        "analysis_kind": "algorithmiq_tem_paired_hamming_pilot",
        "exploratory_only": True,
        "function_name": "algorithmiq/tem",
        "channel": args.channel,
        "backend": args.backend,
        "job_id": str(job_id) if job_id is not None else None,
        "status": str(status) if status is not None else None,
        "config": {
            "qubits": int(args.qubits),
            "depths": depths,
            "trials": int(args.trials),
            "seed": int(args.seed),
            "paired_perturb_qubits": [int(x) for x in perturb_qubits],
            "options": _json_safe(options),
        },
        "plan_summary": plan_summary,
        "observables": observable_info,
        "result_metadata": _json_safe(getattr(result, "metadata", {}) or {}),
        "branches": branches,
        "paired_branch_comparison": _aggregate_paired(rows, perturb_qubits),
        "trial_rows": _json_safe(rows),
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(args.output_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
