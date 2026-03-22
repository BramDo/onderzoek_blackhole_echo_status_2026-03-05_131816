#!/usr/bin/env python3
"""Focused q14 hardware-valid ZNE checkpoints for overlap/disjoint controls.

This keeps the scope narrow on the unstable q14 hardware points: depths 2 and 3,
branches q=0 and q=10, and odd gate-folding factors such as 1 and 3.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from qiskit import QuantumCircuit, transpile

from qiskit_black_hole_hardware_runner import (
    _backend_name,
    _build_runtime_service,
    _count_two_qubit_gates,
    _estimate_local_readout_params,
    _exact_perturbed_echo,
    _extract_counts_list_from_sampler_result,
    _mean_std,
    _mitigate_p_zero,
    _mitigate_p_zero_local_tensor,
    _run_sampler_job,
    _select_backend,
)
from qiskit_black_hole_scrambling import (
    brickwork_scrambler,
    build_echo_measurement_circuits,
    metric_zne_summary,
    parse_depths,
)


@dataclass
class CircuitMeta:
    depth: int
    trial: int
    seed: int
    perturb_qubit: int
    factor: int
    kind: str
    exact_value: float


def parse_factors(raw: str) -> List[int]:
    factors: List[int] = []
    for token in raw.split(","):
        token = token.strip()
        if not token:
            continue
        factor = int(token)
        if factor < 1 or factor % 2 == 0:
            raise ValueError(f"ZNE factor must be a positive odd integer, got {factor}")
        factors.append(factor)
    if not factors:
        raise ValueError("At least one ZNE factor is required")
    return factors


def fold_transpiled_two_qubit_local(circuit: QuantumCircuit, factor: int) -> QuantumCircuit:
    if factor == 1:
        return circuit.copy()

    folded = QuantumCircuit(circuit.num_qubits, circuit.num_clbits, name=f"{circuit.name}_lfold{factor}")
    extra_pairs = (factor - 1) // 2

    for inst in circuit.data:
        qargs = [circuit.find_bit(qubit).index for qubit in inst.qubits]
        cargs = [circuit.find_bit(clbit).index for clbit in inst.clbits]
        folded.append(inst.operation, qargs, cargs)

        if len(inst.qubits) == 2:
            inv_op = inst.operation.inverse()
            for _ in range(extra_pairs):
                folded.append(inv_op, qargs, [])
                folded.append(inst.operation, qargs, [])
    return folded


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run q14 hardware-valid ZNE checkpoints.")
    p.add_argument("--qubits", type=int, default=14)
    p.add_argument("--depths", type=str, default="2,3")
    p.add_argument("--trials", type=int, default=3)
    p.add_argument("--seed", type=int, default=424242)
    p.add_argument("--shots", type=int, default=8000)
    p.add_argument("--backend", type=str, default="ibm_fez")
    p.add_argument("--zne-factors", type=str, default="1,3")
    p.add_argument("--readout-mitigation", action="store_true")
    p.add_argument("--cal-shots", type=int, default=6000)
    p.add_argument("--extra-error-suppression", action="store_true")
    p.add_argument("--dd-sequence", type=str, default="XY4", choices=["XX", "XpXm", "XY4"])
    p.add_argument("--twirl-randomizations", type=int, default=8)
    p.add_argument(
        "--output-json",
        type=str,
        default="results/hardware/q14_zne_checkpoints.json",
    )
    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = build_arg_parser().parse_args(sys.argv[1:] if argv is None else argv)
    depths = parse_depths(args.depths)
    factors = parse_factors(args.zne_factors)
    if args.qubits != 14:
        print("This focused checkpoint runner is locked to q14.", file=sys.stderr)
        return 2

    try:
        service = _build_runtime_service()
        backend = _select_backend(service, args.backend, min_qubits=args.qubits)
    except Exception as exc:
        print(f"Runtime service/backend selectie faalde: {exc}", file=sys.stderr)
        return 1

    runtime_sampler_options: Optional[Dict[str, Any]] = None
    if args.extra_error_suppression:
        runtime_sampler_options = {
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

    master_rng = np.random.default_rng(args.seed)
    base_metas: List[CircuitMeta] = []
    circuits: List[QuantumCircuit] = []

    for depth in depths:
        for trial in range(args.trials):
            trial_seed = int(master_rng.integers(0, 2**32 - 1))
            rng = np.random.default_rng(trial_seed)
            u_circuit = brickwork_scrambler(args.qubits, depth=depth, rng=rng)
            for perturb_qubit in (0, 10):
                ideal_c, pert_c = build_echo_measurement_circuits(
                    u_circuit=u_circuit,
                    n_qubits=args.qubits,
                    perturb_qubit=perturb_qubit,
                )
                exact_pert = _exact_perturbed_echo(
                    u_circuit=u_circuit,
                    n_qubits=args.qubits,
                    perturb_qubit=perturb_qubit,
                )
                circuits.append(ideal_c)
                base_metas.append(
                    CircuitMeta(
                        depth=depth,
                        trial=trial,
                        seed=trial_seed,
                        perturb_qubit=perturb_qubit,
                        factor=1,
                        kind="ideal",
                        exact_value=1.0,
                    )
                )
                circuits.append(pert_c)
                base_metas.append(
                    CircuitMeta(
                        depth=depth,
                        trial=trial,
                        seed=trial_seed,
                        perturb_qubit=perturb_qubit,
                        factor=1,
                        kind="perturbed",
                        exact_value=exact_pert,
                    )
                )

    tbase_circuits = transpile(circuits, backend=backend, optimization_level=1)
    if not isinstance(tbase_circuits, list):
        tbase_circuits = [tbase_circuits]

    metas: List[CircuitMeta] = []
    tcircuits: List[QuantumCircuit] = []
    for base_meta, tcircuit in zip(base_metas, tbase_circuits):
        for factor in factors:
            tcircuits.append(fold_transpiled_two_qubit_local(tcircuit, factor))
            metas.append(
                CircuitMeta(
                    depth=base_meta.depth,
                    trial=base_meta.trial,
                    seed=base_meta.seed,
                    perturb_qubit=base_meta.perturb_qubit,
                    factor=factor,
                    kind=base_meta.kind,
                    exact_value=base_meta.exact_value,
                )
            )

    try:
        hw_job_id, hw_result, sampler_interface, _ = _run_sampler_job(
            service=service,
            backend=backend,
            circuits=tcircuits,
            shots=args.shots,
            sampler_options=runtime_sampler_options,
        )
    except Exception as exc:
        print(f"Hardware sampler run faalde: {exc}", file=sys.stderr)
        return 1

    try:
        hw_counts = _extract_counts_list_from_sampler_result(
            hw_result,
            shots=args.shots,
            num_bits=args.qubits,
            n_items=len(tcircuits),
        )
    except Exception as exc:
        print(f"Counts extractie faalde: {exc}", file=sys.stderr)
        return 1

    calibration_job_id: Optional[str] = None
    mitigation_info: Optional[Dict[str, Any]] = None
    assignment = None
    p01 = None
    p10 = None
    qubits_desc = list(range(args.qubits - 1, -1, -1))
    use_dense_mitigation = False

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
            mitigation_info = {
                **cal_info,
                "mitigation_strategy": "direct_local_tensor_p_zero",
                "mitigation_qubits": list(reversed(qubits_desc)),
            }
        except Exception as exc:
            print(f"Readout calibration faalde: {exc}", file=sys.stderr)
            return 1

    records: List[Dict[str, Any]] = []
    grouped: Dict[Tuple[int, int, int, str], List[float]] = {}

    for idx, meta in enumerate(metas):
        counts = hw_counts[idx]
        raw_value = 0.0
        if meta.kind == "ideal" or meta.kind == "perturbed":
            from qiskit_black_hole_hardware_runner import _p_zero_from_counts

            raw_value = _p_zero_from_counts(counts, n_qubits=args.qubits)

        mitigated_value: Optional[float] = None
        if args.readout_mitigation and p01 is not None and p10 is not None:
            mitigated_value, _ = _mitigate_p_zero_local_tensor(
                counts,
                p01=p01,
                p10=p10,
                n_qubits=args.qubits,
                qubits_desc=qubits_desc,
            )

        record = {
            "depth": meta.depth,
            "trial": meta.trial,
            "seed": meta.seed,
            "perturb_qubit": meta.perturb_qubit,
            "factor": meta.factor,
            "kind": meta.kind,
            "exact_value": meta.exact_value,
            "raw_value": raw_value,
            "mitigated_value": mitigated_value,
            "transpiled_depth": int(tcircuits[idx].depth()),
            "two_qubit_gate_count": _count_two_qubit_gates(tcircuits[idx]),
        }
        records.append(record)
        grouped.setdefault((meta.depth, meta.perturb_qubit, meta.factor, meta.kind), []).append(raw_value)

    summaries: List[Dict[str, Any]] = []
    for depth in depths:
        for perturb_qubit in (0, 10):
            entry: Dict[str, Any] = {
                "depth": depth,
                "perturb_qubit": perturb_qubit,
                "branch": "overlap" if perturb_qubit == 0 else "disjoint",
                "factors": [],
            }

            target_means: List[float] = []
            exact_reference = None
            for factor in factors:
                raw_ideal_vals = [
                    r["raw_value"]
                    for r in records
                    if r["depth"] == depth
                    and r["perturb_qubit"] == perturb_qubit
                    and r["factor"] == factor
                    and r["kind"] == "ideal"
                ]
                raw_pert_vals = [
                    r["raw_value"]
                    for r in records
                    if r["depth"] == depth
                    and r["perturb_qubit"] == perturb_qubit
                    and r["factor"] == factor
                    and r["kind"] == "perturbed"
                ]
                factor_entry: Dict[str, Any] = {
                    "factor": factor,
                    "raw": {
                        "ideal_echo": _mean_std(raw_ideal_vals),
                        "perturbed_echo": _mean_std(raw_pert_vals),
                    },
                }

                if args.readout_mitigation:
                    mit_ideal_vals = [
                        float(r["mitigated_value"])
                        for r in records
                        if r["depth"] == depth
                        and r["perturb_qubit"] == perturb_qubit
                        and r["factor"] == factor
                        and r["kind"] == "ideal"
                    ]
                    mit_pert_vals = [
                        float(r["mitigated_value"])
                        for r in records
                        if r["depth"] == depth
                        and r["perturb_qubit"] == perturb_qubit
                        and r["factor"] == factor
                        and r["kind"] == "perturbed"
                    ]
                    factor_entry["readout_mitigated"] = {
                        "ideal_echo": _mean_std(mit_ideal_vals),
                        "perturbed_echo": _mean_std(mit_pert_vals),
                    }
                    target_means.append(float(np.mean(mit_pert_vals)))
                else:
                    target_means.append(float(np.mean(raw_pert_vals)))

                exact_reference = [
                    r["exact_value"]
                    for r in records
                    if r["depth"] == depth
                    and r["perturb_qubit"] == perturb_qubit
                    and r["factor"] == factor
                    and r["kind"] == "perturbed"
                ][0]
                entry["factors"].append(factor_entry)

            entry["zne"] = {
                "target": "readout_mitigated" if args.readout_mitigation else "raw",
                "perturbed_echo": metric_zne_summary(
                    factors=[float(f) for f in factors],
                    target_curve_means=target_means,
                    requested_order=1,
                    exact_reference=float(exact_reference),
                ),
            }
            summaries.append(entry)

    output = {
        "config": {
            "qubits": args.qubits,
            "depths": depths,
            "trials": args.trials,
            "seed": args.seed,
            "shots": args.shots,
            "zne_factors": factors,
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
        "calibration": mitigation_info,
        "records": records,
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
    print("branch depth | f=1 mitigated_pert | f=3 mitigated_pert | zne(0)")
    for entry in summaries:
        by_factor = {item["factor"]: item for item in entry["factors"]}
        fac1 = by_factor.get(1, {})
        fac3 = by_factor.get(3, {})
        mit1 = fac1.get("readout_mitigated", fac1.get("raw", {})).get("perturbed_echo", {})
        mit3 = fac3.get("readout_mitigated", fac3.get("raw", {})).get("perturbed_echo", {})
        zne0 = entry["zne"]["perturbed_echo"]["recommended_extrapolated"]
        print(
            f"{entry['branch']:>8s} {entry['depth']:>5d} | "
            f"{mit1.get('mean', float('nan')):8.5f} | "
            f"{mit3.get('mean', float('nan')):8.5f} | "
            f"{zne0:8.5f}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
