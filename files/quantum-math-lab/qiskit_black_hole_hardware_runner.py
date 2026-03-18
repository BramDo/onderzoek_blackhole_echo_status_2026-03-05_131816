#!/usr/bin/env python3
"""Hardware runner for black-hole scrambling echoes via IBM Runtime.

This script runs ideal and perturbed Loschmidt-echo circuits on real IBM hardware,
logs raw estimates from counts, and optionally applies local-tensored readout
mitigation from on-device calibration circuits.

Output is JSON with per-run records and per-depth summaries.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Set, Tuple

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from qiskit_black_hole_scrambling import (
    brickwork_scrambler,
    build_echo_measurement_circuits,
    parse_depths,
)


@dataclass
class PairMeta:
    depth: int
    trial: int
    seed: int
    exact_ideal: Optional[float]
    exact_perturbed: Optional[float]
    idx_ideal: int
    idx_perturbed: int


MAX_EXACT_QUBITS = 24
MAX_MITIGATION_SUBSET_QUBITS = 12


def _backend_name(backend: Any) -> str:
    name_attr = getattr(backend, "name", None)
    if callable(name_attr):
        try:
            return str(name_attr())
        except TypeError:
            pass
    if name_attr is not None:
        return str(name_attr)
    return str(backend)


def _normalize_counts(counts: Mapping[Any, Any], num_bits: int) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for key, value in counts.items():
        if isinstance(key, int):
            bitstring = format(key, f"0{num_bits}b")
        else:
            bitstring = str(key).replace(" ", "")
            bitstring = bitstring.zfill(num_bits)
        out[bitstring] = int(round(float(value)))
    return out


def _quasi_to_counts(quasi: Mapping[Any, Any], shots: int, num_bits: int) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for key, prob in quasi.items():
        if isinstance(key, int):
            bitstring = format(key, f"0{num_bits}b")
        else:
            bitstring = str(key).replace(" ", "")
            bitstring = bitstring.zfill(num_bits)
        counts[bitstring] = int(round(float(prob) * shots))
    return counts


def _extract_counts_list_from_sampler_result(
    result: Any,
    shots: int,
    num_bits: int,
    n_items: int,
) -> List[Dict[str, int]]:
    """Extract one histogram per circuit from Sampler results (v1 and v2 shapes)."""
    if hasattr(result, "quasi_dists"):
        quasi_dists = getattr(result, "quasi_dists")
        if len(quasi_dists) < n_items:
            raise RuntimeError(
                f"Sampler result has {len(quasi_dists)} quasi dists, expected >= {n_items}."
            )
        return [_quasi_to_counts(qd, shots=shots, num_bits=num_bits) for qd in quasi_dists[:n_items]]

    out: List[Dict[str, int]] = []
    for i in range(n_items):
        item = None

        if isinstance(result, (list, tuple)):
            if i < len(result):
                item = result[i]
        elif hasattr(result, "__getitem__"):
            try:
                item = result[i]
            except Exception:
                item = None

        if item is None:
            raise RuntimeError(f"Could not index sampler result at item {i}.")

        counts = None
        data = getattr(item, "data", None)
        if data is not None:
            for register_name in ("c", "meas"):
                register = getattr(data, register_name, None)
                if register is not None and hasattr(register, "get_counts"):
                    counts = register.get_counts()
                    break
            if counts is None and hasattr(data, "get_counts"):
                counts = data.get_counts()

        if counts is None and hasattr(item, "get_counts"):
            counts = item.get_counts()

        if counts is None:
            raise RuntimeError(f"Could not extract counts for sampler item {i}.")

        out.append(_normalize_counts(counts, num_bits=num_bits))

    return out


def _build_runtime_service() -> Any:
    try:
        from qiskit_ibm_runtime import QiskitRuntimeService
    except ImportError as exc:
        raise RuntimeError(
            "qiskit-ibm-runtime ontbreekt. Installeer het in je qiskit-venv."
        ) from exc

    token = (
        os.getenv("QCAPI_TOKEN")
        or os.getenv("QISKIT_IBM_TOKEN")
        or os.getenv("IBM_QUANTUM_TOKEN")
    )
    instance = os.getenv("QISKIT_IBM_INSTANCE")

    if token:
        kwargs: Dict[str, str] = {"token": token}
        if instance:
            kwargs["instance"] = instance
        try:
            return QiskitRuntimeService(channel="ibm_quantum", **kwargs)
        except TypeError:
            return QiskitRuntimeService(**kwargs)

    return QiskitRuntimeService()


def _select_backend(service: Any, requested_backend: Optional[str], min_qubits: int) -> Any:
    if requested_backend:
        return service.backend(requested_backend)

    candidates = service.backends(
        simulator=False,
        operational=True,
        min_num_qubits=min_qubits,
    )
    if not candidates:
        candidates = service.backends(simulator=False, min_num_qubits=min_qubits)
    if not candidates:
        raise RuntimeError(f"Geen geschikte hardware-backend gevonden voor >= {min_qubits} qubits.")

    try:
        from qiskit_ibm_runtime import least_busy

        return least_busy(candidates)
    except Exception:
        scored = []
        for backend in candidates:
            pending = 10**9
            try:
                pending = int(backend.status().pending_jobs)
            except Exception:
                pass
            scored.append((pending, _backend_name(backend), backend))
        scored.sort(key=lambda item: (item[0], item[1]))
        return scored[0][2]


def _run_sampler_job(
    service: Any,
    backend: Any,
    circuits: List[QuantumCircuit],
    shots: int,
    sampler_options: Optional[Dict[str, Any]] = None,
) -> Tuple[str, Any, str, Any]:
    job = None
    result = None

    try:
        from qiskit_ibm_runtime import SamplerV2

        if sampler_options:
            sampler = SamplerV2(mode=backend, options=sampler_options)
        else:
            sampler = SamplerV2(mode=backend)
        job = sampler.run(circuits, shots=shots)
        result = job.result()
        return str(job.job_id()), result, "SamplerV2", job
    except ImportError:
        from qiskit_ibm_runtime import Sampler, Session

        with Session(service=service, backend=backend) as session:
            sampler = Sampler(session=session)
            job = sampler.run(circuits, shots=shots)
            result = job.result()
        return str(job.job_id()), result, "SamplerV1", job


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}

    if isinstance(value, (list, tuple, set)):
        return [_json_safe(v) for v in value]

    if hasattr(value, "tolist"):
        try:
            return value.tolist()
        except Exception:
            pass

    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass

    return repr(value)


def _collect_runtime_job_metadata(job: Optional[Any], backend_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
    if job is None:
        return None

    metadata: Dict[str, Any] = {"job_id": None}

    try:
        metadata["job_id"] = str(job.job_id())
    except Exception:
        metadata["job_id"] = None

    try:
        metadata["status"] = str(job.status())
    except Exception:
        metadata["status"] = None

    try:
        metadata["creation_date"] = _json_safe(job.creation_date())
    except Exception:
        try:
            metadata["creation_date"] = _json_safe(job.creation_date)
        except Exception:
            metadata["creation_date"] = None

    try:
        metadata["usage"] = _json_safe(job.usage())
    except Exception:
        metadata["usage"] = None

    try:
        metadata["usage_estimation"] = _json_safe(job.usage_estimation)
    except Exception:
        metadata["usage_estimation"] = None

    try:
        metadata["metrics"] = _json_safe(job.metrics())
    except Exception:
        metadata["metrics"] = None

    try:
        metadata["session_id"] = _json_safe(job.session_id)
    except Exception:
        metadata["session_id"] = None

    if backend_name is None:
        try:
            backend_name = _backend_name(job.backend())
        except Exception:
            backend_name = None
    metadata["backend_name"] = backend_name

    return metadata


def _count_two_qubit_gates(circuit: QuantumCircuit) -> int:
    total = 0
    for instr in circuit.data:
        op = getattr(instr, "operation", None)
        if op is None:
            op = instr[0]
        if getattr(op, "num_qubits", 0) == 2:
            total += 1
    return total


def _counts_to_prob_vector(counts: Dict[str, int], n_qubits: int) -> np.ndarray:
    n_labels = 2**n_qubits
    p_obs = np.zeros(n_labels, dtype=float)
    total = 0.0

    for bitstring, c in counts.items():
        b = bitstring.replace(" ", "").zfill(n_qubits)
        idx = int(b, 2)
        value = float(c)
        p_obs[idx] += value
        total += value

    if total <= 0.0:
        raise ValueError("Histogram is leeg; kan geen kansen vormen.")
    p_obs /= total
    return p_obs


def _p_zero_from_counts(counts: Dict[str, int], n_qubits: int) -> float:
    total = float(sum(counts.values()))
    if total <= 0.0:
        raise ValueError("Histogram is leeg; kan geen kansen vormen.")
    zero_key = "0" * n_qubits
    return float(counts.get(zero_key, 0)) / total


def _bit_from_qiskit_bitstring(bitstring: str, qubit: int, n_qubits: int) -> int:
    """Return measured bit for qubit index q from qiskit output string.

    With measure(range(n), range(n)), qiskit count keys are c[n-1]..c[0].
    """
    bits = bitstring.replace(" ", "").zfill(n_qubits)
    pos = n_qubits - 1 - qubit
    return 1 if bits[pos] == "1" else 0


def _parse_subset_qubits(spec: Optional[str], n_qubits: int) -> List[int]:
    if spec is None or not spec.strip():
        return []

    out: List[int] = []
    seen: Set[int] = set()
    for raw in spec.split(","):
        token = raw.strip()
        if not token:
            continue
        if "-" in token:
            parts = token.split("-", 1)
            if len(parts) != 2:
                raise ValueError(f"Ongeldige subset token: '{token}'")
            a = int(parts[0].strip())
            b = int(parts[1].strip())
            if a > b:
                a, b = b, a
            for q in range(a, b + 1):
                if q < 0 or q >= n_qubits:
                    raise ValueError(f"Qubit index {q} buiten bereik [0,{n_qubits - 1}]")
                if q not in seen:
                    seen.add(q)
                    out.append(q)
        else:
            q = int(token)
            if q < 0 or q >= n_qubits:
                raise ValueError(f"Qubit index {q} buiten bereik [0,{n_qubits - 1}]")
            if q not in seen:
                seen.add(q)
                out.append(q)

    out.sort()
    return out


def _aggregate_counts_on_qubits(
    counts: Dict[str, int],
    n_qubits: int,
    qubits_desc: List[int],
) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for bitstring, c in counts.items():
        key = "".join(
            "1" if _bit_from_qiskit_bitstring(bitstring, q, n_qubits) == 1 else "0" for q in qubits_desc
        )
        out[key] = out.get(key, 0) + int(c)
    return out


def _p_zero_on_qubit_subset(
    counts: Dict[str, int],
    n_qubits: int,
    qubits_desc: List[int],
) -> float:
    k = len(qubits_desc)
    if k == 0:
        raise ValueError("subset heeft 0 qubits")
    sub_counts = _aggregate_counts_on_qubits(counts, n_qubits=n_qubits, qubits_desc=qubits_desc)
    total = float(sum(sub_counts.values()))
    if total <= 0.0:
        raise ValueError("Histogram is leeg; kan geen kansen vormen.")
    return float(sub_counts.get("0" * k, 0)) / total


def _estimate_local_readout_params(
    counts_all0: Dict[str, int],
    counts_all1: Dict[str, int],
    n_qubits: int,
) -> Tuple[np.ndarray, np.ndarray, Dict[str, object]]:
    shots0 = float(sum(counts_all0.values()))
    shots1 = float(sum(counts_all1.values()))
    if shots0 <= 0 or shots1 <= 0:
        raise ValueError("Calibration shots ontbreken.")

    ones_given_0 = np.zeros(n_qubits, dtype=float)
    zeros_given_1 = np.zeros(n_qubits, dtype=float)

    for bitstring, c in counts_all0.items():
        for q in range(n_qubits):
            if _bit_from_qiskit_bitstring(bitstring, q, n_qubits) == 1:
                ones_given_0[q] += float(c)

    for bitstring, c in counts_all1.items():
        for q in range(n_qubits):
            if _bit_from_qiskit_bitstring(bitstring, q, n_qubits) == 0:
                zeros_given_1[q] += float(c)

    p01 = np.clip(ones_given_0 / shots0, 0.0, 0.499999)
    p10 = np.clip(zeros_given_1 / shots1, 0.0, 0.499999)

    info: Dict[str, object] = {
        "shots_all0": int(shots0),
        "shots_all1": int(shots1),
        "p01_per_qubit": p01.tolist(),
        "p10_per_qubit": p10.tolist(),
    }
    return p01, p10, info


def _build_assignment_for_qubits(
    p01: np.ndarray,
    p10: np.ndarray,
    qubits_desc: List[int],
) -> np.ndarray:
    if not qubits_desc:
        raise ValueError("mitigation qubit subset is leeg")

    mats: List[np.ndarray] = []
    for q in qubits_desc:
        mats.append(
            np.asarray(
                [
                    [1.0 - p01[q], p10[q]],
                    [p01[q], 1.0 - p10[q]],
                ],
                dtype=float,
            )
        )

    assignment = mats[0]
    for m in mats[1:]:
        assignment = np.kron(assignment, m)
    return assignment


def _mitigate_p_zero(
    counts: Dict[str, int],
    assignment: np.ndarray,
    n_qubits: int,
    qubits_desc: List[int],
) -> Tuple[float, Dict[str, float]]:
    sub_counts = _aggregate_counts_on_qubits(counts, n_qubits=n_qubits, qubits_desc=qubits_desc)
    p_obs = _counts_to_prob_vector(sub_counts, n_qubits=len(qubits_desc))

    p_true = np.linalg.pinv(assignment, rcond=1e-12) @ p_obs
    neg_mass = float(-np.minimum(p_true, 0.0).sum())
    p_true = np.clip(p_true, 0.0, None)

    norm = float(p_true.sum())
    if norm <= 0.0:
        raise ValueError("Mitigated distribution normalisatie faalde.")
    p_true /= norm

    info = {
        "negative_mass_before_clip": neg_mass,
    }
    return float(p_true[0]), info


def _exact_perturbed_echo(u_circuit: QuantumCircuit, n_qubits: int, perturb_qubit: int) -> float:
    psi0 = Statevector.from_label("0" * n_qubits)
    kick = QuantumCircuit(n_qubits)
    kick.x(perturb_qubit)
    psi_pert = psi0.evolve(u_circuit).evolve(kick).evolve(u_circuit.inverse())
    return float(abs(np.vdot(psi0.data, psi_pert.data)) ** 2)


def _mean_std(values: List[float]) -> Dict[str, float]:
    arr = np.asarray(values, dtype=float)
    return {
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr)),
    }


def parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run black-hole echo circuits on IBM hardware.")
    p.add_argument("--qubits", type=int, default=8)
    p.add_argument("--depths", type=str, default="1,2,3,4,5,6,8,10")
    p.add_argument("--trials", type=int, default=3)
    p.add_argument("--seed", type=int, default=424242)
    p.add_argument("--shots", type=int, default=5000)
    p.add_argument("--perturb-qubit", type=int, default=0)
    p.add_argument("--backend", type=str, default=None)
    p.add_argument("--optimization-level", type=int, default=1)
    p.add_argument("--skip-exact", action="store_true", help="Skip noiseless exact references.")

    p.add_argument("--readout-mitigation", action="store_true")
    p.add_argument("--cal-shots", type=int, default=4000)
    p.add_argument(
        "--subset-qubits",
        type=str,
        default="",
        help=(
            "Optionele qubit-subset voor extra observabele en schaalbare mitigatie, "
            "bv. '0-7' of '0,1,2,3,4,5,6,7'."
        ),
    )

    p.add_argument(
        "--extra-error-suppression",
        action="store_true",
        help=(
            "Enable extra hardware error suppression via dynamical decoupling + gate twirling "
            "in SamplerV2 runtime options."
        ),
    )
    p.add_argument(
        "--dd-sequence",
        type=str,
        default="XY4",
        choices=["XX", "XpXm", "XY4"],
        help="Dynamical decoupling sequence when --extra-error-suppression is enabled.",
    )
    p.add_argument(
        "--twirl-randomizations",
        type=int,
        default=8,
        help="Number of gate-twirling randomizations for extra suppression (SamplerV2).",
    )

    p.add_argument("--list-backends", action="store_true")
    p.add_argument(
        "--reuse-hardware-job-id",
        type=str,
        default=None,
        help="Hergebruik bestaande IBM Runtime hardware job id i.p.v. een nieuwe sampler run starten.",
    )
    p.add_argument(
        "--output-json",
        type=str,
        default="results/hardware/black_hole_hardware_results.json",
    )
    return p.parse_args(argv)


def list_backends(min_qubits: int) -> None:
    service = _build_runtime_service()
    backends = service.backends(simulator=False, operational=True, min_num_qubits=min_qubits)
    print(f"Beschikbare hardware-backends (>={min_qubits} qubits):")
    for backend in sorted(backends, key=_backend_name):
        print(f"- {_backend_name(backend)}")


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)

    if args.qubits < 2:
        print("Gebruik minimaal 2 qubits.", file=sys.stderr)
        return 2
    if args.trials < 1 or args.shots < 1 or args.cal_shots < 1:
        print("trials/shots/cal-shots moeten > 0 zijn.", file=sys.stderr)
        return 2
    if not (0 <= args.perturb_qubit < args.qubits):
        print("perturb-qubit valt buiten bereik.", file=sys.stderr)
        return 2
    if args.twirl_randomizations < 1:
        print("twirl-randomizations moet >= 1 zijn.", file=sys.stderr)
        return 2

    try:
        subset_qubits = _parse_subset_qubits(args.subset_qubits, n_qubits=args.qubits)
    except Exception as exc:
        print(f"subset-qubits parse fout: {exc}", file=sys.stderr)
        return 2

    subset_desc = sorted(subset_qubits, reverse=True)

    if args.qubits > MAX_EXACT_QUBITS and not args.skip_exact:
        print(
            f"Exact statevector referentie boven {MAX_EXACT_QUBITS} qubits is niet haalbaar; gebruik --skip-exact.",
            file=sys.stderr,
        )
        return 2

    mitigation_qubits_desc: List[int] = []
    if args.readout_mitigation:
        if subset_desc:
            mitigation_qubits_desc = subset_desc
        else:
            mitigation_qubits_desc = list(range(args.qubits - 1, -1, -1))
        if len(mitigation_qubits_desc) > MAX_MITIGATION_SUBSET_QUBITS:
            print(
                (
                    "Readout-mitigatie subset te groot. Gebruik --subset-qubits met max "
                    f"{MAX_MITIGATION_SUBSET_QUBITS} qubits voor schaalbaarheid."
                ),
                file=sys.stderr,
            )
            return 2

    depths = parse_depths(args.depths)

    if args.list_backends:
        try:
            list_backends(min_qubits=args.qubits)
            return 0
        except Exception as exc:
            print(f"Backend-lijst ophalen faalde: {exc}", file=sys.stderr)
            return 1

    try:
        from qiskit import transpile
    except ImportError as exc:
        print(f"Qiskit import faalde: {exc}", file=sys.stderr)
        return 1

    reuse_hw_job = None
    backend_hint: Optional[str] = args.backend

    try:
        service = _build_runtime_service()
        if args.reuse_hardware_job_id:
            reuse_hw_job = service.job(args.reuse_hardware_job_id)
            if backend_hint is None:
                try:
                    backend_hint = _backend_name(reuse_hw_job.backend())
                except Exception:
                    backend_hint = None
        backend = _select_backend(service, backend_hint, min_qubits=args.qubits)
    except Exception as exc:
        print(f"Runtime service/backend selectie faalde: {exc}", file=sys.stderr)
        return 1

    print(f"Backend: {_backend_name(backend)}")
    print(f"Qubits={args.qubits}, depths={depths}, trials/depth={args.trials}, shots={args.shots}")

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
        print(
            "Extra suppression actief: "
            f"DD={args.dd_sequence}, twirl_randomizations={args.twirl_randomizations}"
        )

    master_rng = np.random.default_rng(args.seed)
    pairs: List[PairMeta] = []
    circuits: List[QuantumCircuit] = []

    for depth in depths:
        for trial in range(args.trials):
            trial_seed = int(master_rng.integers(0, 2**32 - 1))
            rng = np.random.default_rng(trial_seed)
            u_circuit = brickwork_scrambler(args.qubits, depth=depth, rng=rng)
            ideal_c, pert_c = build_echo_measurement_circuits(
                u_circuit=u_circuit,
                n_qubits=args.qubits,
                perturb_qubit=args.perturb_qubit,
            )

            exact_ideal = None if args.skip_exact else 1.0
            exact_pert = None if args.skip_exact else _exact_perturbed_echo(
                u_circuit,
                n_qubits=args.qubits,
                perturb_qubit=args.perturb_qubit,
            )

            idx_ideal = len(circuits)
            circuits.append(ideal_c)
            idx_pert = len(circuits)
            circuits.append(pert_c)

            pairs.append(
                PairMeta(
                    depth=depth,
                    trial=trial,
                    seed=trial_seed,
                    exact_ideal=exact_ideal,
                    exact_perturbed=exact_pert,
                    idx_ideal=idx_ideal,
                    idx_perturbed=idx_pert,
                )
            )

    tcircuits = transpile(circuits, backend=backend, optimization_level=args.optimization_level)
    if not isinstance(tcircuits, list):
        tcircuits = [tcircuits]

    if len(tcircuits) != len(circuits):
        print(
            f"Transpile gaf {len(tcircuits)} circuits terug, verwacht {len(circuits)}.",
            file=sys.stderr,
        )
        return 1

    if args.reuse_hardware_job_id:
        try:
            if reuse_hw_job is None:
                reuse_hw_job = service.job(args.reuse_hardware_job_id)
            hw_job_id = str(args.reuse_hardware_job_id)
            hw_result = reuse_hw_job.result()
            sampler_interface = "reused_hardware_job"
            hw_job = reuse_hw_job
        except Exception as exc:
            print(f"Hergebruik hardware job faalde: {exc}", file=sys.stderr)
            return 1
    else:
        try:
            hw_job_id, hw_result, sampler_interface, hw_job = _run_sampler_job(
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

    calibration_info: Optional[Dict[str, object]] = None
    calibration_job_id: Optional[str] = None
    calibration_job = None
    assignment: Optional[np.ndarray] = None

    if args.readout_mitigation:
        cal0 = QuantumCircuit(args.qubits, args.qubits, name="cal_all0")
        cal0.measure(range(args.qubits), range(args.qubits))

        cal1 = QuantumCircuit(args.qubits, args.qubits, name="cal_all1")
        for q in range(args.qubits):
            cal1.x(q)
        cal1.measure(range(args.qubits), range(args.qubits))

        tcal = transpile([cal0, cal1], backend=backend, optimization_level=args.optimization_level)
        if not isinstance(tcal, list):
            tcal = [tcal]

        if len(tcal) != 2:
            print("Calibration transpile gaf niet precies 2 circuits terug.", file=sys.stderr)
            return 1

        try:
            calibration_job_id, cal_result, _, calibration_job = _run_sampler_job(
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
            assignment = _build_assignment_for_qubits(
                p01=p01,
                p10=p10,
                qubits_desc=mitigation_qubits_desc,
            )
            calibration_info = {
                **cal_info,
                "local_model": "independent per-qubit asymmetric readout",
                "calibration_job_id": calibration_job_id,
                "p01_mean": float(np.mean(p01)),
                "p10_mean": float(np.mean(p10)),
                "mitigation_qubits": list(reversed(mitigation_qubits_desc)),
                "mitigation_qubit_count": len(mitigation_qubits_desc),
                "assignment_condition_number": float(np.linalg.cond(assignment)),
            }
        except Exception as exc:
            print(f"Readout calibration faalde: {exc}", file=sys.stderr)
            return 1

    runs: List[Dict[str, object]] = []

    for pair in pairs:
        counts_i = hw_counts[pair.idx_ideal]
        counts_p = hw_counts[pair.idx_perturbed]

        raw_ideal = _p_zero_from_counts(counts_i, n_qubits=args.qubits)
        raw_pert = _p_zero_from_counts(counts_p, n_qubits=args.qubits)

        t_i = tcircuits[pair.idx_ideal]
        t_p = tcircuits[pair.idx_perturbed]

        record: Dict[str, object] = {
            "depth": pair.depth,
            "trial": pair.trial,
            "seed": pair.seed,
            "raw": {
                "ideal_echo": raw_ideal,
                "perturbed_echo": raw_pert,
            },
            "transpiled": {
                "ideal": {
                    "depth": int(t_i.depth()),
                    "two_qubit_gate_count": _count_two_qubit_gates(t_i),
                },
                "perturbed": {
                    "depth": int(t_p.depth()),
                    "two_qubit_gate_count": _count_two_qubit_gates(t_p),
                },
            },
        }

        if pair.exact_ideal is not None and pair.exact_perturbed is not None:
            record["exact"] = {
                "ideal_echo": pair.exact_ideal,
                "perturbed_echo": pair.exact_perturbed,
            }
            record["raw"]["ideal_abs_error_vs_exact"] = abs(raw_ideal - pair.exact_ideal)
            record["raw"]["perturbed_abs_error_vs_exact"] = abs(raw_pert - pair.exact_perturbed)

        if subset_desc:
            raw_subset_i = _p_zero_on_qubit_subset(
                counts_i,
                n_qubits=args.qubits,
                qubits_desc=subset_desc,
            )
            raw_subset_p = _p_zero_on_qubit_subset(
                counts_p,
                n_qubits=args.qubits,
                qubits_desc=subset_desc,
            )
            record["raw"]["ideal_subset_echo"] = raw_subset_i
            record["raw"]["perturbed_subset_echo"] = raw_subset_p
            record["raw"]["subset_qubits"] = subset_qubits

        if args.readout_mitigation and assignment is not None:
            mit_i, mit_info_i = _mitigate_p_zero(
                counts_i,
                assignment=assignment,
                n_qubits=args.qubits,
                qubits_desc=mitigation_qubits_desc,
            )
            mit_p, mit_info_p = _mitigate_p_zero(
                counts_p,
                assignment=assignment,
                n_qubits=args.qubits,
                qubits_desc=mitigation_qubits_desc,
            )

            if subset_desc:
                record["readout_mitigated"] = {
                    "ideal_subset_echo": mit_i,
                    "perturbed_subset_echo": mit_p,
                    "subset_qubits": subset_qubits,
                    "ideal_negative_mass_before_clip": mit_info_i["negative_mass_before_clip"],
                    "perturbed_negative_mass_before_clip": mit_info_p["negative_mass_before_clip"],
                }
            else:
                record["readout_mitigated"] = {
                    "ideal_echo": mit_i,
                    "perturbed_echo": mit_p,
                    "ideal_negative_mass_before_clip": mit_info_i["negative_mass_before_clip"],
                    "perturbed_negative_mass_before_clip": mit_info_p["negative_mass_before_clip"],
                }
                if pair.exact_ideal is not None and pair.exact_perturbed is not None:
                    record["readout_mitigated"]["ideal_abs_error_vs_exact"] = abs(mit_i - pair.exact_ideal)
                    record["readout_mitigated"]["perturbed_abs_error_vs_exact"] = abs(
                        mit_p - pair.exact_perturbed
                    )

        runs.append(record)

    summary_by_depth: List[Dict[str, object]] = []
    for depth in sorted({r["depth"] for r in runs}):
        rows = [r for r in runs if r["depth"] == depth]
        entry: Dict[str, object] = {
            "depth": depth,
            "raw": {
                "ideal_echo": _mean_std([float(r["raw"]["ideal_echo"]) for r in rows]),
                "perturbed_echo": _mean_std([float(r["raw"]["perturbed_echo"]) for r in rows]),
            },
        }
        if subset_desc:
            entry["raw"]["subset_qubits"] = subset_qubits
            entry["raw"]["ideal_subset_echo"] = _mean_std([float(r["raw"]["ideal_subset_echo"]) for r in rows])
            entry["raw"]["perturbed_subset_echo"] = _mean_std(
                [float(r["raw"]["perturbed_subset_echo"]) for r in rows]
            )

        if "exact" in rows[0]:
            entry["exact"] = {
                "ideal_echo": _mean_std([float(r["exact"]["ideal_echo"]) for r in rows]),
                "perturbed_echo": _mean_std([float(r["exact"]["perturbed_echo"]) for r in rows]),
            }
            entry["raw"]["ideal_abs_error_vs_exact"] = _mean_std(
                [float(r["raw"]["ideal_abs_error_vs_exact"]) for r in rows]
            )
            entry["raw"]["perturbed_abs_error_vs_exact"] = _mean_std(
                [float(r["raw"]["perturbed_abs_error_vs_exact"]) for r in rows]
            )

        if args.readout_mitigation:
            if subset_desc:
                entry["readout_mitigated"] = {
                    "subset_qubits": subset_qubits,
                    "ideal_subset_echo": _mean_std(
                        [float(r["readout_mitigated"]["ideal_subset_echo"]) for r in rows]
                    ),
                    "perturbed_subset_echo": _mean_std(
                        [float(r["readout_mitigated"]["perturbed_subset_echo"]) for r in rows]
                    ),
                }
            else:
                entry["readout_mitigated"] = {
                    "ideal_echo": _mean_std([float(r["readout_mitigated"]["ideal_echo"]) for r in rows]),
                    "perturbed_echo": _mean_std(
                        [float(r["readout_mitigated"]["perturbed_echo"]) for r in rows]
                    ),
                }
                if "exact" in rows[0]:
                    entry["readout_mitigated"]["ideal_abs_error_vs_exact"] = _mean_std(
                        [float(r["readout_mitigated"]["ideal_abs_error_vs_exact"]) for r in rows]
                    )
                    entry["readout_mitigated"]["perturbed_abs_error_vs_exact"] = _mean_std(
                        [float(r["readout_mitigated"]["perturbed_abs_error_vs_exact"]) for r in rows]
                    )

        summary_by_depth.append(entry)

    backend_info: Dict[str, object] = {
        "name": _backend_name(backend),
    }
    for attr in ("backend_version", "num_qubits"):
        val = getattr(backend, attr, None)
        if val is not None:
            backend_info[attr] = val

    try:
        props = backend.properties()
        if props is not None:
            lu = getattr(props, "last_update_date", None)
            if lu is not None:
                backend_info["properties_last_update"] = str(lu)
    except Exception:
        pass

    output: Dict[str, object] = {
        "config": {
            "qubits": args.qubits,
            "depths": depths,
            "trials": args.trials,
            "seed": args.seed,
            "shots": args.shots,
            "perturb_qubit": args.perturb_qubit,
            "optimization_level": args.optimization_level,
            "readout_mitigation": bool(args.readout_mitigation),
            "cal_shots": args.cal_shots,
            "skip_exact": bool(args.skip_exact),
            "subset_qubits": subset_qubits,
            "extra_error_suppression": bool(args.extra_error_suppression),
            "dd_sequence": args.dd_sequence if args.extra_error_suppression else None,
            "twirl_randomizations": int(args.twirl_randomizations)
            if args.extra_error_suppression
            else None,
        },
        "runtime": {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "sampler_interface": sampler_interface,
            "hardware_job_id": hw_job_id,
            "calibration_job_id": calibration_job_id,
            "sampler_options": runtime_sampler_options,
            "hardware_job_metadata": _collect_runtime_job_metadata(
                hw_job, backend_name=_backend_name(backend)
            ),
            "calibration_job_metadata": _collect_runtime_job_metadata(
                calibration_job, backend_name=_backend_name(backend)
            ),
        },
        "backend": backend_info,
        "calibration": calibration_info,
        "runs": runs,
        "summary_by_depth": summary_by_depth,
    }

    out_path = Path(args.output_json)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")

    print(f"Hardware job id: {hw_job_id}")
    if calibration_job_id is not None:
        print(f"Calibration job id: {calibration_job_id}")
    print(f"JSON opgeslagen in: {out_path}")

    print("depth | raw_ideal       | raw_pert")
    for entry in summary_by_depth:
        d = int(entry["depth"])
        raw_i = entry["raw"]["ideal_echo"]
        raw_p = entry["raw"]["perturbed_echo"]
        print(
            f"{d:>5d} | "
            f"{raw_i['mean']:8.5f}±{raw_i['std']:7.5f} | "
            f"{raw_p['mean']:8.5f}±{raw_p['std']:7.5f}"
        )

    if subset_desc:
        print("depth | raw_subset_ideal | raw_subset_pert")
        for entry in summary_by_depth:
            d = int(entry["depth"])
            raw_si = entry["raw"]["ideal_subset_echo"]
            raw_sp = entry["raw"]["perturbed_subset_echo"]
            print(
                f"{d:>5d} | "
                f"{raw_si['mean']:8.5f}±{raw_si['std']:7.5f} | "
                f"{raw_sp['mean']:8.5f}±{raw_sp['std']:7.5f}"
            )

    if args.readout_mitigation:
        if subset_desc:
            print("depth | mit_subset_ideal | mit_subset_pert")
            for entry in summary_by_depth:
                d = int(entry["depth"])
                mit_i = entry["readout_mitigated"]["ideal_subset_echo"]
                mit_p = entry["readout_mitigated"]["perturbed_subset_echo"]
                print(
                    f"{d:>5d} | "
                    f"{mit_i['mean']:8.5f}±{mit_i['std']:7.5f} | "
                    f"{mit_p['mean']:8.5f}±{mit_p['std']:7.5f}"
                )
        else:
            print("depth | mit_ideal       | mit_pert")
            for entry in summary_by_depth:
                d = int(entry["depth"])
                mit_i = entry["readout_mitigated"]["ideal_echo"]
                mit_p = entry["readout_mitigated"]["perturbed_echo"]
                print(
                    f"{d:>5d} | "
                    f"{mit_i['mean']:8.5f}±{mit_i['std']:7.5f} | "
                    f"{mit_p['mean']:8.5f}±{mit_p['std']:7.5f}"
                )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
