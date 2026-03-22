#!/usr/bin/env python3
"""Narrow q14 hardware PEC checkpoints with a simple local depolarizing model."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
from qiskit import QuantumCircuit, transpile

from mitiq.pec import (
    combine_results,
    construct_circuits,
    represent_operations_in_circuit_with_local_depolarizing_noise,
)

from qiskit_black_hole_hardware_runner import (
    _backend_name,
    _build_runtime_service,
    _count_two_qubit_gates,
    _estimate_local_readout_params,
    _exact_perturbed_echo,
    _extract_counts_list_from_sampler_result,
    _mean_std,
    _mitigate_p_zero_local_tensor,
    _p_zero_from_counts,
    _run_sampler_job,
    _select_backend,
)
from qiskit_black_hole_scrambling import (
    brickwork_scrambler,
    build_echo_measurement_circuits,
    parse_depths,
)


@dataclass
class SampleMeta:
    depth: int
    trial: int
    seed: int
    perturb_qubit: int
    kind: str
    sample_index: int
    sign: int
    exact_value: float
    noise_level: float


@dataclass
class BaselineMeta:
    depth: int
    trial: int
    seed: int
    perturb_qubit: int
    kind: str
    exact_value: float
    noise_level: float


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run narrow q14 hardware PEC checkpoints.")
    p.add_argument("--qubits", type=int, default=14)
    p.add_argument("--depths", type=str, default="2,3")
    p.add_argument("--trials", type=int, default=1)
    p.add_argument("--seed", type=int, default=424242)
    p.add_argument("--shots", type=int, default=8000)
    p.add_argument("--backend", type=str, default="ibm_fez")
    p.add_argument("--pec-samples", type=int, default=8)
    p.add_argument("--readout-mitigation", action="store_true")
    p.add_argument("--cal-shots", type=int, default=6000)
    p.add_argument("--extra-error-suppression", action="store_true")
    p.add_argument("--dd-sequence", type=str, default="XY4", choices=["XX", "XpXm", "XY4"])
    p.add_argument("--twirl-randomizations", type=int, default=8)
    p.add_argument(
        "--output-json",
        type=str,
        default="results/hardware/q14_pec_checkpoints.json",
    )
    return p


def remove_measurements(circuit: QuantumCircuit) -> QuantumCircuit:
    return circuit.remove_final_measurements(inplace=False)


def strip_identity_gates(circuit: QuantumCircuit) -> QuantumCircuit:
    out = QuantumCircuit(circuit.num_qubits, circuit.num_clbits, name=f"{circuit.name}_noid")
    for instruction in circuit.data:
        if instruction.operation.name in {"id", "i"}:
            continue
        out.append(instruction.operation, instruction.qubits, instruction.clbits)
    return out


def pec_representation_body(circuit: QuantumCircuit, backend: Any) -> QuantumCircuit:
    basis_gates = [
        name
        for name in getattr(backend, "operation_names", [])
        if name not in {"measure", "reset", "delay", "barrier"}
    ]
    logical = transpile(circuit, basis_gates=basis_gates or None, optimization_level=1)
    return strip_identity_gates(logical)


def add_terminal_measurements(circuit: QuantumCircuit) -> QuantumCircuit:
    out = circuit.copy()
    out.measure_all()
    return out


def lookup_gate_error(backend: Any, gate_name: str, qubits: Sequence[int]) -> Optional[float]:
    try:
        props = backend.properties()
        if props is not None:
            value = props.gate_error(gate_name, list(qubits))
            if value is not None:
                return float(value)
    except Exception:
        pass

    try:
        target_item = backend.target[gate_name][tuple(qubits)]
        value = getattr(target_item, "error", None)
        if value is not None:
            return float(value)
    except Exception:
        pass

    return None


def estimate_noise_level(transpiled_body: QuantumCircuit, backend: Any) -> float:
    weighted = 0.0
    total_weight = 0.0

    for instruction in transpiled_body.data:
        op = instruction.operation
        name = op.name
        if name in {"barrier", "delay", "measure"}:
            continue
        qubits = [transpiled_body.find_bit(q).index for q in instruction.qubits]
        err = lookup_gate_error(backend, name, qubits)
        if err is None:
            continue
        weight = max(1, len(qubits))
        weighted += weight * float(err)
        total_weight += weight

    if total_weight <= 0.0:
        return 0.01
    return float(np.clip(weighted / total_weight, 1e-4, 0.2))


def build_runtime_options(args: argparse.Namespace) -> Optional[Dict[str, Any]]:
    if not args.extra_error_suppression:
        return None
    return {
        "dynamical_decoupling": {
            "enable": True,
            "sequence_type": args.dd_sequence,
            "scheduling_method": "alap",
        },
        "twirling": {
            "enable_gates": True,
            "num_randomizations": int(args.twirl_randomizations),
            "strategy": "active-accum",
        },
    }


def main(argv: Optional[List[str]] = None) -> int:
    args = build_arg_parser().parse_args(sys.argv[1:] if argv is None else argv)
    depths = parse_depths(args.depths)
    if args.qubits != 14:
        print("This PEC checkpoint runner is locked to q14.", file=sys.stderr)
        return 2

    try:
        service = _build_runtime_service()
        backend = _select_backend(service, args.backend, min_qubits=args.qubits)
    except Exception as exc:
        print(f"Runtime service/backend selectie faalde: {exc}", file=sys.stderr)
        return 1

    runtime_sampler_options = build_runtime_options(args)

    master_rng = np.random.default_rng(args.seed)
    baseline_circuits: List[QuantumCircuit] = []
    baseline_meta: List[BaselineMeta] = []
    sample_circuits: List[QuantumCircuit] = []
    sample_meta: List[SampleMeta] = []
    sample_groups: Dict[Tuple[int, int, int, str], Dict[str, Any]] = {}

    for depth in depths:
        for trial in range(args.trials):
            trial_seed = int(master_rng.integers(0, 2**32 - 1))
            rng = np.random.default_rng(trial_seed)
            u_circuit = brickwork_scrambler(args.qubits, depth=depth, rng=rng)

            for perturb_qubit in (0, 10):
                ideal_full, pert_full = build_echo_measurement_circuits(
                    u_circuit=u_circuit,
                    n_qubits=args.qubits,
                    perturb_qubit=perturb_qubit,
                )
                exact_pert = _exact_perturbed_echo(
                    u_circuit=u_circuit,
                    n_qubits=args.qubits,
                    perturb_qubit=perturb_qubit,
                )

                for kind, full_circuit, exact_value in (
                    ("ideal", ideal_full, 1.0),
                    ("perturbed", pert_full, exact_pert),
                ):
                    body = remove_measurements(full_circuit)
                    t_body = pec_representation_body(body, backend)
                    noise_level = estimate_noise_level(t_body, backend)
                    reps = represent_operations_in_circuit_with_local_depolarizing_noise(
                        t_body, noise_level=noise_level
                    )
                    sampled_bodies, signs, norm = construct_circuits(
                        t_body,
                        reps,
                        num_samples=args.pec_samples,
                        random_state=trial_seed + perturb_qubit + (0 if kind == "ideal" else 1000),
                        full_output=True,
                    )

                    key = (depth, trial, perturb_qubit, kind)
                    sample_groups[key] = {
                        "norm": float(norm),
                        "signs": [int(s) for s in signs],
                        "noise_level": float(noise_level),
                        "exact_value": float(exact_value),
                    }

                    baseline_circuits.append(add_terminal_measurements(t_body))
                    baseline_meta.append(
                        BaselineMeta(
                            depth=depth,
                            trial=trial,
                            seed=trial_seed,
                            perturb_qubit=perturb_qubit,
                            kind=kind,
                            exact_value=float(exact_value),
                            noise_level=float(noise_level),
                        )
                    )

                    for idx, sampled in enumerate(sampled_bodies):
                        sample_circuits.append(add_terminal_measurements(sampled))
                        sample_meta.append(
                            SampleMeta(
                                depth=depth,
                                trial=trial,
                                seed=trial_seed,
                                perturb_qubit=perturb_qubit,
                                kind=kind,
                                sample_index=idx,
                                sign=int(signs[idx]),
                                exact_value=float(exact_value),
                                noise_level=float(noise_level),
                            )
                        )

    all_circuits = baseline_circuits + sample_circuits

    try:
        tcircuits = transpile(all_circuits, backend=backend, optimization_level=1)
        if not isinstance(tcircuits, list):
            tcircuits = [tcircuits]
        hw_job_id, hw_result, sampler_interface, _ = _run_sampler_job(
            service=service,
            backend=backend,
            circuits=tcircuits,
            shots=args.shots,
            sampler_options=runtime_sampler_options,
        )
        counts = _extract_counts_list_from_sampler_result(
            hw_result,
            shots=args.shots,
            num_bits=args.qubits,
            n_items=len(tcircuits),
        )
    except Exception as exc:
        print(f"Hardware sampler run faalde: {exc}", file=sys.stderr)
        return 1

    calibration_job_id: Optional[str] = None
    p01 = None
    p10 = None
    qubits_desc = list(range(args.qubits - 1, -1, -1))
    calibration: Optional[Dict[str, Any]] = None

    if args.readout_mitigation:
        cal0 = QuantumCircuit(args.qubits, args.qubits, name="cal_all0")
        cal0.measure(range(args.qubits), range(args.qubits))
        cal1 = QuantumCircuit(args.qubits, args.qubits, name="cal_all1")
        for q in range(args.qubits):
            cal1.x(q)
        cal1.measure(range(args.qubits), range(args.qubits))

        try:
            tcal = transpile([cal0, cal1], backend=backend, optimization_level=1)
            if not isinstance(tcal, list):
                tcal = [tcal]
            calibration_job_id, cal_result, _, _ = _run_sampler_job(
                service=service,
                backend=backend,
                circuits=tcal,
                shots=args.cal_shots,
                sampler_options=None,
            )
            cal_counts = _extract_counts_list_from_sampler_result(
                cal_result,
                shots=args.cal_shots,
                num_bits=args.qubits,
                n_items=2,
            )
            p01, p10, cal_info = _estimate_local_readout_params(
                cal_counts[0], cal_counts[1], n_qubits=args.qubits
            )
            calibration = {
                **cal_info,
                "mitigation_strategy": "direct_local_tensor_p_zero",
                "mitigation_qubits": list(reversed(qubits_desc)),
            }
        except Exception as exc:
            print(f"Readout calibration faalde: {exc}", file=sys.stderr)
            return 1

    baseline_records: List[Dict[str, Any]] = []
    sample_records: List[Dict[str, Any]] = []

    baseline_count = len(baseline_meta)
    for idx, meta in enumerate(baseline_meta):
        raw_value = _p_zero_from_counts(counts[idx], n_qubits=args.qubits)
        mitigated_value = None
        if args.readout_mitigation and p01 is not None and p10 is not None:
            mitigated_value, _ = _mitigate_p_zero_local_tensor(
                counts[idx],
                p01=p01,
                p10=p10,
                n_qubits=args.qubits,
                qubits_desc=qubits_desc,
            )
        baseline_records.append(
            {
                "depth": meta.depth,
                "trial": meta.trial,
                "seed": meta.seed,
                "perturb_qubit": meta.perturb_qubit,
                "kind": meta.kind,
                "noise_level": meta.noise_level,
                "exact_value": meta.exact_value,
                "raw_value": raw_value,
                "mitigated_value": mitigated_value,
            }
        )

    for offset, meta in enumerate(sample_meta, start=baseline_count):
        raw_value = _p_zero_from_counts(counts[offset], n_qubits=args.qubits)
        mitigated_value = None
        if args.readout_mitigation and p01 is not None and p10 is not None:
            mitigated_value, _ = _mitigate_p_zero_local_tensor(
                counts[offset],
                p01=p01,
                p10=p10,
                n_qubits=args.qubits,
                qubits_desc=qubits_desc,
            )
        sample_records.append(
            {
                "depth": meta.depth,
                "trial": meta.trial,
                "seed": meta.seed,
                "perturb_qubit": meta.perturb_qubit,
                "kind": meta.kind,
                "sample_index": meta.sample_index,
                "sign": meta.sign,
                "noise_level": meta.noise_level,
                "exact_value": meta.exact_value,
                "raw_value": raw_value,
                "mitigated_value": mitigated_value,
            }
        )

    summaries: List[Dict[str, Any]] = []
    target_field = "mitigated_value" if args.readout_mitigation else "raw_value"
    for depth in depths:
        for perturb_qubit in (0, 10):
            branch = "overlap" if perturb_qubit == 0 else "disjoint"
            for kind in ("ideal", "perturbed"):
                baseline_vals = [
                    float(r[target_field])
                    for r in baseline_records
                    if r["depth"] == depth and r["perturb_qubit"] == perturb_qubit and r["kind"] == kind
                ]
                checkpoint_groups = [
                    r
                    for r in sample_records
                    if r["depth"] == depth and r["perturb_qubit"] == perturb_qubit and r["kind"] == kind
                ]
                if not checkpoint_groups:
                    continue
                key = (depth, checkpoint_groups[0]["trial"], perturb_qubit, kind)
                if key not in sample_groups:
                    key = next(
                        k for k in sample_groups if k[0] == depth and k[2] == perturb_qubit and k[3] == kind
                    )
                group_info = sample_groups[key]
                pec_results = [float(r[target_field]) for r in checkpoint_groups]
                pec_estimate = combine_results(
                    pec_results,
                    norm=float(group_info["norm"]),
                    signs=group_info["signs"],
                )
                baseline_mean, baseline_std = _mean_std(baseline_vals)
                exact_value = float(checkpoint_groups[0]["exact_value"])
                summaries.append(
                    {
                        "depth": depth,
                        "perturb_qubit": perturb_qubit,
                        "branch": branch,
                        "kind": kind,
                        "noise_level": float(group_info["noise_level"]),
                        "target": target_field,
                        "baseline": {
                            "mean": baseline_mean,
                            "std": baseline_std,
                            "abs_error_vs_exact": abs(baseline_mean - exact_value),
                        },
                        "pec": {
                            "num_samples": len(pec_results),
                            "norm": float(group_info["norm"]),
                            "estimate": float(pec_estimate),
                            "abs_error_vs_exact": abs(float(pec_estimate) - exact_value),
                        },
                        "exact_value": exact_value,
                    }
                )

    output = {
        "config": {
            "qubits": args.qubits,
            "depths": depths,
            "trials": args.trials,
            "seed": args.seed,
            "shots": args.shots,
            "pec_samples": args.pec_samples,
            "branches": [0, 10],
            "readout_mitigation": bool(args.readout_mitigation),
            "cal_shots": args.cal_shots,
            "extra_error_suppression": bool(args.extra_error_suppression),
            "dd_sequence": args.dd_sequence if args.extra_error_suppression else None,
            "twirl_randomizations": (
                int(args.twirl_randomizations) if args.extra_error_suppression else None
            ),
        },
        "runtime": {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "backend": _backend_name(backend),
            "sampler_interface": sampler_interface,
            "hardware_job_id": hw_job_id,
            "calibration_job_id": calibration_job_id,
            "sampler_options": runtime_sampler_options,
        },
        "calibration": calibration,
        "baseline_records": baseline_records,
        "sample_records": sample_records,
        "summaries": summaries,
    }

    out_path = Path(args.output_json)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")

    print(f"Backend: {_backend_name(backend)}")
    print(f"Hardware job id: {hw_job_id}")
    if calibration_job_id:
        print(f"Calibration job id: {calibration_job_id}")
    print(f"JSON opgeslagen in: {out_path}")
    print("branch depth kind | baseline | pec | exact")
    for entry in summaries:
        print(
            f"{entry['branch']:>8s} {entry['depth']:>5d} {entry['kind']:>9s} | "
            f"{entry['baseline']['mean']:8.5f} | "
            f"{entry['pec']['estimate']:8.5f} | "
            f"{entry['exact_value']:8.5f}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
