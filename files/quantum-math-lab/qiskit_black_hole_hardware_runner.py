#!/usr/bin/env python3
"""Hardware runner for black-hole scrambling echoes via IBM Runtime.

This script runs ideal and perturbed Loschmidt-echo circuits on real IBM hardware,
logs raw estimates from counts, and optionally applies local-tensored readout
mitigation from on-device calibration circuits.

Output is JSON with per-run records and per-depth summaries.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Set, Tuple

import numpy as np
import torch
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
    perturb_qubit: int
    exact_ideal: Optional[float]
    exact_perturbed: Optional[float]
    idx_ideal: int
    idx_perturbed: int


MAX_EXACT_QUBITS = 24
MAX_MITIGATION_SUBSET_QUBITS = 12
MAX_BLOCK_Z_LOCAL_TENSOR_QUBITS = 10


@dataclass
class MLSidecarBundle:
    model: Any
    feature_names: List[str]
    x_mean: np.ndarray
    x_std: np.ndarray
    target_mode: str
    checkpoint_path: str


def _load_ml_sidecar_bundle(checkpoint_path: Path, model_path: Path) -> MLSidecarBundle:
    payload = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    feature_names = [str(name) for name in payload["feature_names"]]
    spec = importlib.util.spec_from_file_location("pelinn_q_sidecar_model", model_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Kon PE-LiNN modeldefinitie niet laden uit {model_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    model = module.PELiNNQEM(
        in_dim=len(feature_names),
        hid_dim=int(payload.get("hid_dim", 64)),
        steps=int(payload.get("steps", 6)),
        dt=float(payload.get("dt", 0.25)),
        use_tanh_head=bool(payload.get("use_tanh_head", True)),
    )
    model.load_state_dict(payload["state_dict"])
    model.eval()
    return MLSidecarBundle(
        model=model,
        feature_names=feature_names,
        x_mean=np.asarray(payload["x_mean"], dtype=np.float32),
        x_std=np.asarray(payload["x_std"], dtype=np.float32),
        target_mode=str(payload.get("target_mode", "residual")),
        checkpoint_path=str(checkpoint_path),
    )


def _nominal_sidecar_noise_features(extra_error_suppression: bool) -> Tuple[float, float]:
    dep = 0.04
    readout = 0.02
    if extra_error_suppression:
        dep *= 0.75
        readout *= 0.85
    return float(dep), float(readout)


def _predict_ml_sidecar_subset_echo(
    bundle: MLSidecarBundle,
    *,
    total_qubits: int,
    subset_qubits: List[int],
    depth: int,
    trial: int,
    perturb_qubit: int,
    raw_subset_perturbed_echo: float,
    mitigated_subset_perturbed_echo: float,
    logical_pert_depth: int,
    logical_pert_two_qubit_count: int,
    extra_error_suppression: bool,
) -> Dict[str, float]:
    p_dep_eff, p_ro_eff = _nominal_sidecar_noise_features(extra_error_suppression)
    values = {
        "total_qubits": float(total_qubits),
        "subset_size": float(len(subset_qubits)),
        "depth": float(depth),
        "trial": float(trial),
        "branch_overlap": 1.0 if perturb_qubit == 0 else 0.0,
        "perturb_qubit_norm": float(perturb_qubit) / float(max(total_qubits - 1, 1)),
        "raw_subset_perturbed_echo": float(raw_subset_perturbed_echo),
        "mitigated_subset_perturbed_echo": float(mitigated_subset_perturbed_echo),
        "mitigation_gain": float(mitigated_subset_perturbed_echo - raw_subset_perturbed_echo),
        "logical_pert_depth": float(logical_pert_depth),
        "logical_pert_two_qubit_count": float(logical_pert_two_qubit_count),
        "zne_factor": 1.0,
        "noise_dep_effective": p_dep_eff,
        "noise_readout_effective": p_ro_eff,
        "suppression_enabled": 1.0 if extra_error_suppression else 0.0,
    }
    feature_row = np.asarray([values[name] for name in bundle.feature_names], dtype=np.float32)
    x_std = np.where(bundle.x_std < 1e-6, 1.0, bundle.x_std)
    x_scaled = (feature_row - bundle.x_mean) / x_std
    with torch.no_grad():
        raw_pred = float(
            bundle.model(torch.tensor(x_scaled, dtype=torch.float32).unsqueeze(0)).cpu().item()
        )
    final_pred = raw_pred + mitigated_subset_perturbed_echo if bundle.target_mode == "residual" else raw_pred
    clipped_pred = float(np.clip(final_pred, 0.0, 1.0))
    return {
        "perturbed_subset_echo": clipped_pred,
        "unclipped_prediction": float(final_pred),
        "delta_vs_mitigated": float(clipped_pred - mitigated_subset_perturbed_echo),
        "diagnostic_only": True,
        "source": "pelinn_sidecar",
        "checkpoint": bundle.checkpoint_path,
        "feature_noise_mode": "surrogate_nominal",
        "nominal_noise_dep_effective": p_dep_eff,
        "nominal_noise_readout_effective": p_ro_eff,
    }


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


def _distributional_observables_from_counts(
    counts: Dict[str, int],
    n_qubits: int,
) -> Dict[str, object]:
    total = float(sum(counts.values()))
    if total <= 0.0:
        raise ValueError("Histogram is leeg; kan geen kansen vormen.")

    weight_hist = np.zeros(n_qubits + 1, dtype=float)
    one_probs = np.zeros(n_qubits, dtype=float)

    for bitstring, c in counts.items():
        bits = bitstring.replace(" ", "").zfill(n_qubits)
        count_val = float(c)
        weight = bits.count("1")
        weight_hist[weight] += count_val
        for q in range(n_qubits):
            if _bit_from_qiskit_bitstring(bits, q, n_qubits) == 1:
                one_probs[q] += count_val

    weight_hist /= total
    one_probs /= total
    mean_weight = float(np.dot(np.arange(n_qubits + 1, dtype=float), weight_hist))
    return {
        "hamming_weight_distribution": [float(x) for x in weight_hist.tolist()],
        "mean_hamming_weight": mean_weight,
        "mean_excitation_fraction": float(mean_weight / float(n_qubits)),
        "one_probability_by_qubit": [float(x) for x in one_probs.tolist()],
    }


def _weighted_distribution_from_mapping(
    distribution: Mapping[Any, Any],
    n_qubits: int,
) -> Dict[str, float]:
    out: Dict[str, float] = {}
    for key, value in distribution.items():
        if isinstance(key, int):
            bitstring = format(key, f"0{n_qubits}b")
        else:
            bitstring = str(key).replace(" ", "").zfill(n_qubits)
        out[bitstring] = out.get(bitstring, 0.0) + float(value)
    return out


def _p_zero_from_weighted_distribution(
    distribution: Mapping[Any, Any],
    n_qubits: int,
) -> float:
    weighted = _weighted_distribution_from_mapping(distribution, n_qubits=n_qubits)
    total = float(sum(weighted.values()))
    if abs(total) <= 1e-12:
        raise ValueError("Gewogen distributie heeft geen netto massa.")
    zero_key = "0" * n_qubits
    return float(weighted.get(zero_key, 0.0)) / total


def _distributional_observables_from_weighted_distribution(
    distribution: Mapping[Any, Any],
    n_qubits: int,
) -> Dict[str, object]:
    weighted = _weighted_distribution_from_mapping(distribution, n_qubits=n_qubits)
    total = float(sum(weighted.values()))
    if abs(total) <= 1e-12:
        raise ValueError("Gewogen distributie heeft geen netto massa.")

    weight_hist = np.zeros(n_qubits + 1, dtype=float)
    one_probs = np.zeros(n_qubits, dtype=float)
    negative_mass = 0.0

    for bitstring, prob in weighted.items():
        bits = bitstring.replace(" ", "").zfill(n_qubits)
        prob_val = float(prob)
        if prob_val < 0.0:
            negative_mass += -prob_val
        weight = bits.count("1")
        weight_hist[weight] += prob_val
        for q in range(n_qubits):
            if _bit_from_qiskit_bitstring(bits, q, n_qubits) == 1:
                one_probs[q] += prob_val

    weight_hist /= total
    one_probs /= total
    mean_weight = float(np.dot(np.arange(n_qubits + 1, dtype=float), weight_hist))
    return {
        "hamming_weight_distribution": [float(x) for x in weight_hist.tolist()],
        "mean_hamming_weight": mean_weight,
        "mean_excitation_fraction": float(mean_weight / float(n_qubits)),
        "one_probability_by_qubit": [float(x) for x in one_probs.tolist()],
        "distribution_total_mass": total,
        "distribution_negative_mass": negative_mass,
    }


def _mitigate_one_probability(obs_one_prob: float, p01_q: float, p10_q: float) -> float:
    det = 1.0 - float(p01_q) - float(p10_q)
    if det <= 0.0:
        raise ValueError("Singuliere lokale readout-inversie voor qubit-marginal.")
    true_one = (float(obs_one_prob) - float(p01_q)) / det
    return float(np.clip(true_one, 0.0, 1.0))


def _hamming_return_linear_from_one_probs(one_probs: List[float]) -> float:
    arr = np.asarray(one_probs, dtype=float)
    if arr.size == 0:
        raise ValueError("one_probs is leeg")
    return float(np.clip(1.0 - float(np.mean(arr)), 0.0, 1.0))


def _parse_named_qubit_blocks(spec: Optional[str], n_qubits: int) -> List[Tuple[str, List[int]]]:
    if spec is None or not spec.strip():
        return []

    out: List[Tuple[str, List[int]]] = []
    seen_names: Set[str] = set()
    for idx, raw in enumerate(spec.split(";")):
        token = raw.strip()
        if not token:
            continue
        if ":" in token:
            name_raw, qubit_spec = token.split(":", 1)
            name = name_raw.strip().replace(" ", "_")
            subset_spec = qubit_spec.strip()
        else:
            name = f"block{idx}"
            subset_spec = token
        if not name:
            raise ValueError(f"Ongeldige z-observable-block token: '{token}'")
        if name in seen_names:
            raise ValueError(f"Dubbele z-observable-block naam: '{name}'")
        qubits = _parse_subset_qubits(subset_spec, n_qubits=n_qubits)
        if not qubits:
            raise ValueError(f"z-observable-block '{name}' heeft geen qubits")
        seen_names.add(name)
        out.append((name, qubits))
    return out


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


def _parse_initial_layout(spec: Optional[str], n_qubits: int) -> List[int]:
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
                raise ValueError(f"Ongeldige initial-layout token: '{token}'")
            a = int(parts[0].strip())
            b = int(parts[1].strip())
            step = 1 if a <= b else -1
            for q in range(a, b + step, step):
                if q < 0 or q >= n_qubits:
                    raise ValueError(f"Initial-layout qubit index {q} buiten bereik [0,{n_qubits - 1}]")
                if q in seen:
                    raise ValueError(f"Initial-layout bevat duplicaat qubit {q}")
                seen.add(q)
                out.append(q)
        else:
            q = int(token)
            if q < 0 or q >= n_qubits:
                raise ValueError(f"Initial-layout qubit index {q} buiten bereik [0,{n_qubits - 1}]")
            if q in seen:
                raise ValueError(f"Initial-layout bevat duplicaat qubit {q}")
            seen.add(q)
            out.append(q)

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


def _z_parity_from_counts(
    counts: Dict[str, int],
    n_qubits: int,
    qubits_desc: List[int],
) -> float:
    sub_counts = _aggregate_counts_on_qubits(counts, n_qubits=n_qubits, qubits_desc=qubits_desc)
    total = float(sum(sub_counts.values()))
    if total <= 0.0:
        raise ValueError("Histogram is leeg; kan geen kansen vormen.")
    estimate = 0.0
    for bitstring, c in sub_counts.items():
        sign = 1.0 if bitstring.count("1") % 2 == 0 else -1.0
        estimate += sign * float(c)
    return float(estimate / total)


def _z_parity_from_weighted_distribution(
    distribution: Mapping[Any, Any],
    n_qubits: int,
    qubits_desc: List[int],
) -> float:
    weighted = _weighted_distribution_from_mapping(distribution, n_qubits=n_qubits)
    total = float(sum(weighted.values()))
    if abs(total) <= 1e-12:
        raise ValueError("Gewogen distributie heeft geen netto massa.")
    estimate = 0.0
    for bitstring, prob in weighted.items():
        ones = 0
        for q in qubits_desc:
            ones += _bit_from_qiskit_bitstring(bitstring, q, n_qubits)
        sign = 1.0 if ones % 2 == 0 else -1.0
        estimate += sign * float(prob)
    return float(estimate / total)


def _z_parity_from_reduced_weighted_distribution(
    distribution: Mapping[Any, Any],
    n_qubits: int,
) -> float:
    weighted = _weighted_distribution_from_mapping(distribution, n_qubits=n_qubits)
    total = float(sum(weighted.values()))
    if abs(total) <= 1e-12:
        raise ValueError("Gewogen distributie heeft geen netto massa.")
    estimate = 0.0
    for bitstring, prob in weighted.items():
        sign = 1.0 if bitstring.count("1") % 2 == 0 else -1.0
        estimate += sign * float(prob)
    return float(estimate / total)


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


def _build_m3_marginal_mitigator(
    counts_all0: Dict[str, int],
    counts_all1: Dict[str, int],
    n_qubits: int,
    cal_shots: int,
) -> Tuple[Any, Dict[str, object]]:
    try:
        from mthree import M3Mitigation
    except ImportError as exc:
        raise RuntimeError("mthree ontbreekt; installeer het in je qiskit-venv.") from exc

    mitigator = M3Mitigation(None)
    mitigator.num_qubits = n_qubits
    mitigator.cal_shots = int(cal_shots)
    mitigator.cal_method = "marginal"
    mitigator.single_qubit_cals = [None] * n_qubits

    bad_qubits: List[int] = []
    for q in range(n_qubits):
        index = n_qubits - q - 1
        mat = np.zeros((2, 2), dtype=np.float32)

        p00_counts = 0.0
        for bitstring, c in counts_all0.items():
            bits = bitstring.replace(" ", "").zfill(n_qubits)
            if bits[index] == "0":
                p00_counts += float(c)
        p00 = p00_counts / float(cal_shots)
        p10_q = 1.0 - p00
        mat[:, 0] = [p00, p10_q]

        p11_counts = 0.0
        for bitstring, c in counts_all1.items():
            bits = bitstring.replace(" ", "").zfill(n_qubits)
            if bits[index] == "1":
                p11_counts += float(c)
        p11 = p11_counts / float(cal_shots)
        p01_q = 1.0 - p11
        mat[:, 1] = [p01_q, p11]

        mitigator.single_qubit_cals[q] = mat
        if p01_q >= p00:
            bad_qubits.append(q)

    mitigator.faulty_qubits = bad_qubits
    info = {
        "cal_method": "marginal",
        "faulty_qubits": bad_qubits,
        "readout_fidelity_mean": float(
            np.mean([x for x in mitigator.readout_fidelity() if x is not None])
        ),
        "readout_fidelity_min": float(
            np.min([x for x in mitigator.readout_fidelity() if x is not None])
        ),
    }
    return mitigator, info


def _apply_m3_correction(
    counts: Dict[str, int],
    mitigator: Any,
    n_qubits: int,
    qubits_desc: List[int],
) -> Tuple[float, Dict[str, object], Dict[str, object]]:
    if not qubits_desc:
        raise ValueError("M3 mitigation vereist minstens 1 qubit.")

    if len(qubits_desc) == n_qubits and qubits_desc == list(range(n_qubits - 1, -1, -1)):
        counts_for_mit = counts
        reduced_n_qubits = n_qubits
        measured_qubits = list(range(n_qubits))
    else:
        counts_for_mit = _aggregate_counts_on_qubits(
            counts,
            n_qubits=n_qubits,
            qubits_desc=qubits_desc,
        )
        reduced_n_qubits = len(qubits_desc)
        measured_qubits = list(reversed(qubits_desc))

    quasi, details = mitigator.apply_correction(
        counts_for_mit,
        qubits=measured_qubits,
        details=True,
    )
    quasi_dist = _weighted_distribution_from_mapping(quasi, n_qubits=reduced_n_qubits)
    nearest_prob, l2_distance = quasi.nearest_probability_distribution(return_distance=True)
    nearest_dist = _weighted_distribution_from_mapping(nearest_prob, n_qubits=reduced_n_qubits)

    p_zero_unclipped = _p_zero_from_weighted_distribution(quasi_dist, n_qubits=reduced_n_qubits)
    observables = _distributional_observables_from_weighted_distribution(
        quasi_dist,
        n_qubits=reduced_n_qubits,
    )
    observables["weighted_distribution"] = {k: float(v) for k, v in quasi_dist.items()}
    nearest_observables = _distributional_observables_from_weighted_distribution(
        nearest_dist,
        n_qubits=reduced_n_qubits,
    )
    nearest_observables["weighted_distribution"] = {k: float(v) for k, v in nearest_dist.items()}
    info = {
        "method": "m3_marginal",
        "solver_details": _json_safe(details),
        "p_zero_unclipped": p_zero_unclipped,
        "negative_quasi_mass": float(observables["distribution_negative_mass"]),
        "quasi_total_mass": float(observables["distribution_total_mass"]),
        "nearest_probability_l2_distance": float(l2_distance),
        "support_size": len(quasi_dist),
        "nearest_probability_observables": nearest_observables,
        "negative_mass_before_clip": float(observables["distribution_negative_mass"]),
    }
    return float(np.clip(p_zero_unclipped, 0.0, 1.0)), info, observables


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


def _mitigate_p_zero_local_tensor(
    counts: Dict[str, int],
    p01: np.ndarray,
    p10: np.ndarray,
    n_qubits: int,
    qubits_desc: List[int],
) -> Tuple[float, Dict[str, Optional[float]]]:
    """Estimate p_true(0...0) directly from the local inverse model.

    For large mitigation domains we only need the all-zero probability, not the
    full mitigated distribution. Under the independent per-qubit readout model,
    the first row of the inverse tensor-product assignment factorizes, so we can
    evaluate p_true(0...0) without materializing the dense 2^n x 2^n matrix.
    """
    sub_counts = _aggregate_counts_on_qubits(counts, n_qubits=n_qubits, qubits_desc=qubits_desc)
    total = float(sum(sub_counts.values()))
    if total <= 0.0:
        raise ValueError("Histogram is leeg; kan geen kansen vormen.")

    estimate = 0.0
    for bitstring, c in sub_counts.items():
        coeff = 1.0
        for idx, bit in enumerate(bitstring):
            q = qubits_desc[idx]
            det = 1.0 - p01[q] - p10[q]
            if det <= 0.0:
                raise ValueError(f"Singuliere lokale readout-inversie op qubit {q}.")
            if bit == "0":
                coeff *= (1.0 - p10[q]) / det
            else:
                coeff *= (-p10[q]) / det
        estimate += coeff * (float(c) / total)

    info: Dict[str, Optional[float]] = {
        "negative_mass_before_clip": None,
    }
    return float(np.clip(estimate, 0.0, 1.0)), info


def _mitigate_distribution_local_tensor(
    counts: Dict[str, int],
    p01: np.ndarray,
    p10: np.ndarray,
    n_qubits: int,
    qubits_desc: List[int],
) -> Tuple[Dict[str, float], Dict[str, object]]:
    k = len(qubits_desc)
    if k == 0:
        raise ValueError("z-observable-block heeft 0 qubits")
    if k > MAX_BLOCK_Z_LOCAL_TENSOR_QUBITS:
        raise ValueError(
            "Lokale tensor block-Z mitigatie is nu begrensd tot "
            f"{MAX_BLOCK_Z_LOCAL_TENSOR_QUBITS} qubits; kreeg {k}."
        )

    sub_counts = _aggregate_counts_on_qubits(counts, n_qubits=n_qubits, qubits_desc=qubits_desc)
    total = float(sum(sub_counts.values()))
    if total <= 0.0:
        raise ValueError("Histogram is leeg; kan geen kansen vormen.")

    p_obs = np.zeros(2**k, dtype=float)
    for bitstring, c in sub_counts.items():
        idx = int(str(bitstring).replace(" ", "").zfill(k), 2)
        p_obs[idx] += float(c) / total

    assignment = np.asarray([[1.0]], dtype=float)
    for q in qubits_desc:
        a_q = np.asarray(
            [
                [1.0 - float(p01[q]), float(p10[q])],
                [float(p01[q]), 1.0 - float(p10[q])],
            ],
            dtype=float,
        )
        assignment = np.kron(assignment, a_q)

    p_true = np.linalg.solve(assignment, p_obs)
    negative_mass = float(np.sum(np.clip(-p_true, 0.0, None)))
    weighted_dist = {
        format(idx, f"0{k}b"): float(val)
        for idx, val in enumerate(p_true.tolist())
        if abs(float(val)) > 1e-15
    }
    info: Dict[str, object] = {
        "negative_mass_before_clip": negative_mass,
        "subset_qubits": [int(q) for q in qubits_desc],
    }
    return weighted_dist, info


def _block_z_metrics_from_one_probs_and_parity(
    one_probs: List[float],
    qubits_desc: List[int],
    z_parity: float,
) -> Dict[str, object]:
    block_one_probs = [float(one_probs[q]) for q in qubits_desc]
    linear_return = _hamming_return_linear_from_one_probs(block_one_probs)
    mean_z = float(1.0 - 2.0 * np.mean(np.asarray(block_one_probs, dtype=float)))
    return {
        "qubits": [int(q) for q in qubits_desc],
        "size": int(len(qubits_desc)),
        "mean_z": mean_z,
        "linear_return": float(linear_return),
        "z_parity": float(z_parity),
    }


def _build_block_z_observables_from_counts(
    counts: Dict[str, int],
    n_qubits: int,
    named_blocks: List[Tuple[str, List[int]]],
    one_probs: List[float],
) -> Dict[str, object]:
    out: Dict[str, object] = {}
    for name, qubits_desc in named_blocks:
        out[name] = _block_z_metrics_from_one_probs_and_parity(
            one_probs=one_probs,
            qubits_desc=qubits_desc,
            z_parity=_z_parity_from_counts(counts, n_qubits=n_qubits, qubits_desc=qubits_desc),
        )
    return out


def _build_block_z_observables_from_weighted_distribution(
    distribution: Mapping[Any, Any],
    n_qubits: int,
    named_blocks: List[Tuple[str, List[int]]],
    one_probs: List[float],
) -> Dict[str, object]:
    out: Dict[str, object] = {}
    for name, qubits_desc in named_blocks:
        out[name] = _block_z_metrics_from_one_probs_and_parity(
            one_probs=one_probs,
            qubits_desc=qubits_desc,
            z_parity=_z_parity_from_weighted_distribution(
                distribution,
                n_qubits=n_qubits,
                qubits_desc=qubits_desc,
            ),
        )
    return out


def _build_block_z_observables_from_local_mitigation(
    counts: Dict[str, int],
    p01: np.ndarray,
    p10: np.ndarray,
    n_qubits: int,
    named_blocks: List[Tuple[str, List[int]]],
    one_probs: List[float],
) -> Dict[str, object]:
    out: Dict[str, object] = {}
    for name, qubits_desc in named_blocks:
        weighted_dist, info = _mitigate_distribution_local_tensor(
            counts,
            p01=p01,
            p10=p10,
            n_qubits=n_qubits,
            qubits_desc=qubits_desc,
        )
        entry = _block_z_metrics_from_one_probs_and_parity(
            one_probs=one_probs,
            qubits_desc=qubits_desc,
            z_parity=_z_parity_from_reduced_weighted_distribution(
                weighted_dist,
                n_qubits=len(qubits_desc),
            ),
        )
        entry["negative_mass_before_clip"] = info["negative_mass_before_clip"]
        out[name] = entry
    return out


def _build_block_z_variant_record(
    ideal_blocks: Dict[str, object],
    perturbed_blocks: Dict[str, object],
) -> Dict[str, object]:
    out: Dict[str, object] = {}
    common_names = sorted(set(ideal_blocks).intersection(perturbed_blocks))
    for name in common_names:
        ideal = ideal_blocks[name]
        pert = perturbed_blocks[name]
        rel = _relative_perturbed_echo(
            float(ideal["linear_return"]),
            float(pert["linear_return"]),
        )
        payload: Dict[str, object] = {
            "qubits": list(ideal["qubits"]),
            "size": int(ideal["size"]),
            "ideal_mean_z": float(ideal["mean_z"]),
            "perturbed_mean_z": float(pert["mean_z"]),
            "ideal_linear_return": float(ideal["linear_return"]),
            "perturbed_linear_return": float(pert["linear_return"]),
            "relative_linear_return": float(rel["value"]),
            "relative_linear_return_unclipped": float(rel["unclipped"]),
            "ideal_z_parity": float(ideal["z_parity"]),
            "perturbed_z_parity": float(pert["z_parity"]),
            "z_parity_delta": float(float(pert["z_parity"]) - float(ideal["z_parity"])),
        }
        if "negative_mass_before_clip" in ideal:
            payload["ideal_negative_mass_before_clip"] = float(ideal["negative_mass_before_clip"])
        if "negative_mass_before_clip" in pert:
            payload["perturbed_negative_mass_before_clip"] = float(pert["negative_mass_before_clip"])
        out[name] = payload
    return out


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
        "median": float(np.median(arr)),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
    }


def _robust_location_summary(values: List[float]) -> Dict[str, float]:
    arr = np.asarray(values, dtype=float)
    median = float(np.median(arr))
    q25 = float(np.percentile(arr, 25))
    q75 = float(np.percentile(arr, 75))
    mad = float(np.median(np.abs(arr - median)))
    return {
        "median": median,
        "mad": mad,
        "q25": q25,
        "q75": q75,
        "iqr": float(q75 - q25),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
    }


def _relative_perturbed_echo(ideal_echo: float, perturbed_echo: float) -> Dict[str, float]:
    denom = max(float(ideal_echo), 1e-12)
    unclipped = float(perturbed_echo) / denom
    return {
        "value": float(np.clip(unclipped, 0.0, 1.0)),
        "unclipped": float(unclipped),
    }


def _stability_report(values: List[float]) -> Dict[str, object]:
    arr = np.asarray(values, dtype=float)
    flags: List[str] = []
    zero_clipped = int(np.sum(np.isclose(arr, 0.0, atol=1e-12)))
    one_clipped = int(np.sum(np.isclose(arr, 1.0, atol=1e-12)))
    mean_val = float(np.mean(arr))
    std_val = float(np.std(arr))
    total = float(np.sum(arr))
    dominant_share = float(np.max(arr) / total) if total > 0.0 else 0.0

    if zero_clipped >= 2:
        flags.append("two_or_more_zero_clips")
    if one_clipped >= 2:
        flags.append("two_or_more_one_clips")
    if mean_val > 0.0 and std_val > mean_val:
        flags.append("std_exceeds_mean")
    if dominant_share > 0.8:
        flags.append("single_trial_dominates")

    return {
        "trial_values": [float(x) for x in arr.tolist()],
        "median": float(np.median(arr)),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
        "zero_clipped_count": zero_clipped,
        "one_clipped_count": one_clipped,
        "dominant_trial_share": dominant_share,
        "flags": flags,
        "unstable_mitigation": bool(flags),
    }


def _mad_trimmed_diagnostic(values: List[float], z_threshold: float = 3.0) -> Dict[str, object]:
    arr = np.asarray(values, dtype=float)
    median = float(np.median(arr))
    mad = float(np.median(np.abs(arr - median)))
    robust_scale = float(1.4826 * mad)
    if len(arr) < 3 or robust_scale <= 1e-12:
        keep_mask = np.ones(len(arr), dtype=bool)
    else:
        keep_mask = np.abs(arr - median) <= float(z_threshold) * robust_scale
        if not np.any(keep_mask):
            keep_mask = np.ones(len(arr), dtype=bool)

    kept = arr[keep_mask]
    dropped = arr[~keep_mask]
    kept_indices = [int(i) for i in np.where(keep_mask)[0].tolist()]
    dropped_indices = [int(i) for i in np.where(~keep_mask)[0].tolist()]
    return {
        "diagnostic_only": True,
        "rule": "median_absolute_deviation",
        "z_threshold": float(z_threshold),
        "raw_median": median,
        "raw_mad": mad,
        "robust_scale": robust_scale,
        "trim_threshold": float(z_threshold) * robust_scale,
        "kept_count": int(len(kept)),
        "dropped_count": int(len(dropped)),
        "kept_positive_count": int(np.sum(kept > 0.0)),
        "kept_negative_count": int(np.sum(kept < 0.0)),
        "kept_indices": kept_indices,
        "dropped_indices": dropped_indices,
        "kept_values": [float(x) for x in kept.tolist()],
        "dropped_values": [float(x) for x in dropped.tolist()],
        "kept_summary": _mean_std([float(x) for x in kept.tolist()]),
        "kept_robust": _robust_location_summary([float(x) for x in kept.tolist()]),
    }


def _mean_vector(values: List[List[float]]) -> List[float]:
    arr = np.asarray(values, dtype=float)
    return [float(x) for x in np.mean(arr, axis=0).tolist()]


def _build_branch_summary(rows: List[Dict[str, object]]) -> Dict[str, object]:
    subset_mode = "ideal_subset_echo" in rows[0]["raw"]
    entry: Dict[str, object] = {
        "raw": {
            "ideal_echo": _mean_std([float(r["raw"]["ideal_echo"]) for r in rows]),
            "perturbed_echo": _mean_std([float(r["raw"]["perturbed_echo"]) for r in rows]),
        },
    }

    if subset_mode:
        subset_qubits = list(rows[0]["raw"]["subset_qubits"])
        entry["raw"]["subset_qubits"] = subset_qubits
        entry["raw"]["ideal_subset_echo"] = _mean_std([float(r["raw"]["ideal_subset_echo"]) for r in rows])
        entry["raw"]["perturbed_subset_echo"] = _mean_std(
            [float(r["raw"]["perturbed_subset_echo"]) for r in rows]
        )
    else:
        raw_relative_values = [float(r["raw"]["relative_perturbed_echo"]) for r in rows]
        entry["raw"]["relative_perturbed_echo"] = _mean_std(raw_relative_values)
        entry["raw"]["relative_perturbed_echo_stability"] = _stability_report(raw_relative_values)
        entry["raw"]["relative_perturbed_echo_robust"] = _robust_location_summary(
            raw_relative_values
        )

    if "distributional_observables" in rows[0]:
        entry["distributional_observables"] = {
            "ideal": {
                "mean_hamming_weight": _mean_std(
                    [float(r["distributional_observables"]["ideal"]["mean_hamming_weight"]) for r in rows]
                ),
                "mean_excitation_fraction": _mean_std(
                    [
                        float(r["distributional_observables"]["ideal"]["mean_excitation_fraction"])
                        for r in rows
                    ]
                ),
                "hamming_weight_distribution_mean": _mean_vector(
                    [
                        list(r["distributional_observables"]["ideal"]["hamming_weight_distribution"])
                        for r in rows
                    ]
                ),
                "one_probability_by_qubit_mean": _mean_vector(
                    [
                        list(r["distributional_observables"]["ideal"]["one_probability_by_qubit"])
                        for r in rows
                    ]
                ),
            },
            "perturbed": {
                "mean_hamming_weight": _mean_std(
                    [
                        float(r["distributional_observables"]["perturbed"]["mean_hamming_weight"])
                        for r in rows
                    ]
                ),
                "mean_excitation_fraction": _mean_std(
                    [
                        float(r["distributional_observables"]["perturbed"]["mean_excitation_fraction"])
                        for r in rows
                    ]
                ),
                "hamming_weight_distribution_mean": _mean_vector(
                    [
                        list(r["distributional_observables"]["perturbed"]["hamming_weight_distribution"])
                        for r in rows
                    ]
                ),
                "one_probability_by_qubit_mean": _mean_vector(
                    [
                        list(r["distributional_observables"]["perturbed"]["one_probability_by_qubit"])
                        for r in rows
                    ]
                ),
            },
        }

    if "distributional_estimators" in rows[0]:
        entry["distributional_estimators"] = {
            "raw": {
                "ideal_hamming_return_linear": _mean_std(
                    [
                        float(r["distributional_estimators"]["raw"]["ideal_hamming_return_linear"])
                        for r in rows
                    ]
                ),
                "perturbed_hamming_return_linear": _mean_std(
                    [
                        float(r["distributional_estimators"]["raw"]["perturbed_hamming_return_linear"])
                        for r in rows
                    ]
                ),
                "relative_hamming_return_linear": _mean_std(
                    [
                        float(r["distributional_estimators"]["raw"]["relative_hamming_return_linear"])
                        for r in rows
                    ]
                ),
                "relative_hamming_return_linear_stability": _stability_report(
                    [
                        float(r["distributional_estimators"]["raw"]["relative_hamming_return_linear"])
                        for r in rows
                    ]
                ),
                "relative_hamming_return_linear_robust": _robust_location_summary(
                    [
                        float(r["distributional_estimators"]["raw"]["relative_hamming_return_linear"])
                        for r in rows
                    ]
                ),
            }
        }
        if "readout_mitigated" in rows[0]["distributional_estimators"]:
            entry["distributional_estimators"]["readout_mitigated"] = {
                "ideal_hamming_return_linear": _mean_std(
                    [
                        float(
                            r["distributional_estimators"]["readout_mitigated"][
                                "ideal_hamming_return_linear"
                            ]
                        )
                        for r in rows
                    ]
                ),
                "perturbed_hamming_return_linear": _mean_std(
                    [
                        float(
                            r["distributional_estimators"]["readout_mitigated"][
                                "perturbed_hamming_return_linear"
                            ]
                        )
                        for r in rows
                    ]
                ),
                "relative_hamming_return_linear": _mean_std(
                    [
                        float(
                            r["distributional_estimators"]["readout_mitigated"][
                                "relative_hamming_return_linear"
                            ]
                        )
                        for r in rows
                    ]
                ),
                "relative_hamming_return_linear_stability": _stability_report(
                    [
                        float(
                            r["distributional_estimators"]["readout_mitigated"][
                                "relative_hamming_return_linear"
                            ]
                        )
                        for r in rows
                    ]
                ),
                "relative_hamming_return_linear_robust": _robust_location_summary(
                    [
                        float(
                            r["distributional_estimators"]["readout_mitigated"][
                                "relative_hamming_return_linear"
                            ]
                        )
                        for r in rows
                    ]
                ),
            }

    if "z_observable_blocks" in rows[0]:
        entry["z_observable_blocks"] = {}
        for variant_name in rows[0]["z_observable_blocks"]:
            entry["z_observable_blocks"][variant_name] = {}
            for block_name, block_entry in rows[0]["z_observable_blocks"][variant_name].items():
                rel_vals = [
                    float(r["z_observable_blocks"][variant_name][block_name]["relative_linear_return"])
                    for r in rows
                ]
                parity_delta_vals = [
                    float(r["z_observable_blocks"][variant_name][block_name]["z_parity_delta"])
                    for r in rows
                ]
                payload: Dict[str, object] = {
                    "qubits": list(block_entry["qubits"]),
                    "size": int(block_entry["size"]),
                    "ideal_mean_z": _mean_std(
                        [
                            float(r["z_observable_blocks"][variant_name][block_name]["ideal_mean_z"])
                            for r in rows
                        ]
                    ),
                    "perturbed_mean_z": _mean_std(
                        [
                            float(r["z_observable_blocks"][variant_name][block_name]["perturbed_mean_z"])
                            for r in rows
                        ]
                    ),
                    "ideal_linear_return": _mean_std(
                        [
                            float(
                                r["z_observable_blocks"][variant_name][block_name][
                                    "ideal_linear_return"
                                ]
                            )
                            for r in rows
                        ]
                    ),
                    "perturbed_linear_return": _mean_std(
                        [
                            float(
                                r["z_observable_blocks"][variant_name][block_name][
                                    "perturbed_linear_return"
                                ]
                            )
                            for r in rows
                        ]
                    ),
                    "relative_linear_return": _mean_std(rel_vals),
                    "relative_linear_return_stability": _stability_report(rel_vals),
                    "relative_linear_return_robust": _robust_location_summary(rel_vals),
                    "ideal_z_parity": _mean_std(
                        [
                            float(r["z_observable_blocks"][variant_name][block_name]["ideal_z_parity"])
                            for r in rows
                        ]
                    ),
                    "perturbed_z_parity": _mean_std(
                        [
                            float(
                                r["z_observable_blocks"][variant_name][block_name]["perturbed_z_parity"]
                            )
                            for r in rows
                        ]
                    ),
                    "z_parity_delta": _mean_std(parity_delta_vals),
                    "z_parity_delta_robust": _robust_location_summary(parity_delta_vals),
                }
                if "ideal_negative_mass_before_clip" in block_entry:
                    payload["ideal_negative_mass_before_clip"] = _mean_std(
                        [
                            float(
                                r["z_observable_blocks"][variant_name][block_name][
                                    "ideal_negative_mass_before_clip"
                                ]
                            )
                            for r in rows
                        ]
                    )
                if "perturbed_negative_mass_before_clip" in block_entry:
                    payload["perturbed_negative_mass_before_clip"] = _mean_std(
                        [
                            float(
                                r["z_observable_blocks"][variant_name][block_name][
                                    "perturbed_negative_mass_before_clip"
                                ]
                            )
                            for r in rows
                        ]
                    )
                entry["z_observable_blocks"][variant_name][block_name] = payload

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
        if not subset_mode:
            entry["exact"]["relative_perturbed_echo"] = _mean_std(
                [float(r["exact"]["relative_perturbed_echo"]) for r in rows]
            )
            entry["raw"]["relative_perturbed_abs_error_vs_exact"] = _mean_std(
                [float(r["raw"]["relative_perturbed_abs_error_vs_exact"]) for r in rows]
            )

    if "readout_mitigated" in rows[0]:
        if subset_mode:
            subset_qubits = list(rows[0]["readout_mitigated"]["subset_qubits"])
            mit_subset_pert_values = [
                float(r["readout_mitigated"]["perturbed_subset_echo"]) for r in rows
            ]
            entry["readout_mitigated"] = {
                "subset_qubits": subset_qubits,
                "ideal_subset_echo": _mean_std(
                    [float(r["readout_mitigated"]["ideal_subset_echo"]) for r in rows]
                ),
                "perturbed_subset_echo": _mean_std(mit_subset_pert_values),
                "perturbed_subset_echo_stability": _stability_report(mit_subset_pert_values),
            }
            if "ml_diagnostic" in rows[0]:
                entry["ml_diagnostic"] = {
                    "subset_qubits": subset_qubits,
                    "perturbed_subset_echo": _mean_std(
                        [float(r["ml_diagnostic"]["perturbed_subset_echo"]) for r in rows]
                    ),
                    "delta_vs_mitigated": _mean_std(
                        [float(r["ml_diagnostic"]["delta_vs_mitigated"]) for r in rows]
                    ),
                }
        else:
            mit_pert_values = [float(r["readout_mitigated"]["perturbed_echo"]) for r in rows]
            mit_relative_values = [
                float(r["readout_mitigated"]["relative_perturbed_echo"]) for r in rows
            ]
            entry["readout_mitigated"] = {
                "ideal_echo": _mean_std([float(r["readout_mitigated"]["ideal_echo"]) for r in rows]),
                "perturbed_echo": _mean_std(mit_pert_values),
                "perturbed_echo_stability": _stability_report(mit_pert_values),
                "relative_perturbed_echo": _mean_std(mit_relative_values),
                "relative_perturbed_echo_stability": _stability_report(mit_relative_values),
                "relative_perturbed_echo_robust": _robust_location_summary(
                    mit_relative_values
                ),
            }
            if "exact" in rows[0]:
                entry["readout_mitigated"]["ideal_abs_error_vs_exact"] = _mean_std(
                    [float(r["readout_mitigated"]["ideal_abs_error_vs_exact"]) for r in rows]
                )
                entry["readout_mitigated"]["perturbed_abs_error_vs_exact"] = _mean_std(
                    [float(r["readout_mitigated"]["perturbed_abs_error_vs_exact"]) for r in rows]
                )
                entry["readout_mitigated"]["relative_perturbed_abs_error_vs_exact"] = _mean_std(
                    [
                        float(r["readout_mitigated"]["relative_perturbed_abs_error_vs_exact"])
                        for r in rows
                    ]
                )

    return entry


def _build_paired_branch_comparison(
    rows: List[Dict[str, object]],
    perturb_qubits: List[int],
) -> Dict[str, object]:
    anchor = perturb_qubits[0]
    grouped: Dict[Tuple[int, int], Dict[int, Dict[str, object]]] = {}
    for row in rows:
        key = (int(row["depth"]), int(row["trial"]))
        grouped.setdefault(key, {})[int(row["perturb_qubit"])] = row

    comparisons: List[Dict[str, object]] = []
    for compare in perturb_qubits[1:]:
        rel_deltas: List[float] = []
        hamming_rel_deltas: List[float] = []
        mean_excitation_deltas: List[float] = []
        block_variant_deltas: Dict[str, Dict[str, Dict[str, List[float]]]] = {}
        for key in sorted(grouped):
            branch_rows = grouped[key]
            if anchor not in branch_rows or compare not in branch_rows:
                continue
            anchor_row = branch_rows[anchor]
            compare_row = branch_rows[compare]
            rel_deltas.append(
                float(compare_row["readout_mitigated"]["relative_perturbed_echo"])
                - float(anchor_row["readout_mitigated"]["relative_perturbed_echo"])
            )
            hamming_rel_deltas.append(
                float(
                    compare_row["distributional_estimators"]["readout_mitigated"][
                        "relative_hamming_return_linear"
                    ]
                )
                - float(
                    anchor_row["distributional_estimators"]["readout_mitigated"][
                        "relative_hamming_return_linear"
                    ]
                )
            )
            mean_excitation_deltas.append(
                float(compare_row["distributional_observables"]["perturbed"]["mean_excitation_fraction"])
                - float(anchor_row["distributional_observables"]["perturbed"]["mean_excitation_fraction"])
            )
            if "z_observable_blocks" in anchor_row and "z_observable_blocks" in compare_row:
                common_variants = set(anchor_row["z_observable_blocks"]).intersection(
                    compare_row["z_observable_blocks"]
                )
                for variant_name in sorted(common_variants):
                    common_blocks = set(anchor_row["z_observable_blocks"][variant_name]).intersection(
                        compare_row["z_observable_blocks"][variant_name]
                    )
                    for block_name in sorted(common_blocks):
                        bucket = (
                            block_variant_deltas.setdefault(variant_name, {})
                            .setdefault(
                                block_name,
                                {
                                    "relative_linear_return_delta": [],
                                    "z_parity_delta_delta": [],
                                    "perturbed_mean_z_delta": [],
                                },
                            )
                        )
                        bucket["relative_linear_return_delta"].append(
                            float(
                                compare_row["z_observable_blocks"][variant_name][block_name][
                                    "relative_linear_return"
                                ]
                            )
                            - float(
                                anchor_row["z_observable_blocks"][variant_name][block_name][
                                    "relative_linear_return"
                                ]
                            )
                        )
                        bucket["z_parity_delta_delta"].append(
                            float(
                                compare_row["z_observable_blocks"][variant_name][block_name]["z_parity_delta"]
                            )
                            - float(
                                anchor_row["z_observable_blocks"][variant_name][block_name]["z_parity_delta"]
                            )
                        )
                        bucket["perturbed_mean_z_delta"].append(
                            float(
                                compare_row["z_observable_blocks"][variant_name][block_name][
                                    "perturbed_mean_z"
                                ]
                            )
                            - float(
                                anchor_row["z_observable_blocks"][variant_name][block_name][
                                    "perturbed_mean_z"
                                ]
                            )
                        )

        if not rel_deltas or not hamming_rel_deltas or not mean_excitation_deltas:
            continue

        comparisons.append(
            {
                "anchor_perturb_qubit": anchor,
                "perturb_qubit": compare,
                "readout_mitigated": {
                    "relative_perturbed_echo_delta": _mean_std(rel_deltas),
                    "relative_perturbed_echo_delta_stability": _stability_report(rel_deltas),
                    "relative_perturbed_echo_delta_robust": _robust_location_summary(rel_deltas),
                    "relative_perturbed_echo_delta_trimmed_diagnostic": _mad_trimmed_diagnostic(
                        rel_deltas
                    ),
                },
                "distributional_estimators": {
                    "readout_mitigated": {
                        "relative_hamming_return_linear_delta": _mean_std(hamming_rel_deltas),
                        "relative_hamming_return_linear_delta_stability": _stability_report(
                            hamming_rel_deltas
                        ),
                        "relative_hamming_return_linear_delta_robust": _robust_location_summary(
                            hamming_rel_deltas
                        ),
                        "relative_hamming_return_linear_delta_trimmed_diagnostic": (
                            _mad_trimmed_diagnostic(hamming_rel_deltas)
                        ),
                    }
                },
                "distributional_observables": {
                    "perturbed_mean_excitation_fraction_delta": _mean_std(mean_excitation_deltas),
                    "perturbed_mean_excitation_fraction_delta_robust": _robust_location_summary(
                        mean_excitation_deltas
                    ),
                },
            }
        )
        if block_variant_deltas:
            comparisons[-1]["z_observable_blocks"] = {}
            for variant_name, blocks in block_variant_deltas.items():
                comparisons[-1]["z_observable_blocks"][variant_name] = {}
                for block_name, values in blocks.items():
                    rel_vals = values["relative_linear_return_delta"]
                    parity_vals = values["z_parity_delta_delta"]
                    meanz_vals = values["perturbed_mean_z_delta"]
                    comparisons[-1]["z_observable_blocks"][variant_name][block_name] = {
                        "relative_linear_return_delta": _mean_std(rel_vals),
                        "relative_linear_return_delta_stability": _stability_report(rel_vals),
                        "relative_linear_return_delta_robust": _robust_location_summary(rel_vals),
                        "z_parity_delta_delta": _mean_std(parity_vals),
                        "z_parity_delta_delta_robust": _robust_location_summary(parity_vals),
                        "perturbed_mean_z_delta": _mean_std(meanz_vals),
                        "perturbed_mean_z_delta_robust": _robust_location_summary(meanz_vals),
                    }

    return {
        "paired_mode": True,
        "anchor_perturb_qubit": anchor,
        "comparisons": comparisons,
    }


def parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run black-hole echo circuits on IBM hardware.")
    p.add_argument("--qubits", type=int, default=8)
    p.add_argument("--depths", type=str, default="1,2,3,4,5,6,8,10")
    p.add_argument("--trials", type=int, default=3)
    p.add_argument("--seed", type=int, default=424242)
    p.add_argument("--shots", type=int, default=5000)
    p.add_argument("--perturb-qubit", type=int, default=0)
    p.add_argument(
        "--paired-perturb-qubits",
        type=str,
        default="",
        help=(
            "Optionele lijst met perturb-qubits die in een gedeelde hardwarejob "
            "en gedeelde calibratie samen moeten lopen, bv. '0,79'."
        ),
    )
    p.add_argument("--backend", type=str, default=None)
    p.add_argument("--optimization-level", type=int, default=1)
    p.add_argument("--seed-transpiler", type=int, default=None)
    p.add_argument(
        "--initial-layout",
        type=str,
        default="",
        help=(
            "Optionele vaste fysieke layout in logische qubit-volgorde, "
            "bv. '0,1,2,3' of '20-39'."
        ),
    )
    p.add_argument("--skip-exact", action="store_true", help="Skip noiseless exact references.")

    p.add_argument("--readout-mitigation", action="store_true")
    p.add_argument(
        "--readout-mitigation-method",
        type=str,
        default="local",
        choices=["local", "m3"],
        help=(
            "Readout mitigation backend: 'local' for the existing local-tensor inverse, "
            "'m3' for a marginal-calibrated M3 quasi-distribution solve."
        ),
    )
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
        "--z-observable-blocks",
        type=str,
        default="",
        help=(
            "Optionele blokken voor TEM-vriendelijkere Z-observabelen in full-register mode, "
            "bv. 'front10:0-9;back10:70-79'."
        ),
    )
    p.add_argument(
        "--ml-sidecar-checkpoint",
        type=Path,
        default=None,
        help="Optionele PE-LiNN checkpoint voor diagnostische subset-echo voorspelling.",
    )
    p.add_argument(
        "--ml-sidecar-model",
        type=Path,
        default=Path("/tmp/pelinnq.G4gAic/repo/src/model.py"),
        help="Modeldefinitie die hoort bij --ml-sidecar-checkpoint.",
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
        "--reuse-calibration-job-id",
        type=str,
        default=None,
        help="Hergebruik bestaande IBM Runtime calibration job id i.p.v. een nieuwe calibratierun starten.",
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
    try:
        z_observable_blocks = _parse_named_qubit_blocks(
            args.z_observable_blocks,
            n_qubits=args.qubits,
        )
    except Exception as exc:
        print(f"z-observable-blocks parse fout: {exc}", file=sys.stderr)
        return 2
    try:
        paired_perturb_qubits = _parse_subset_qubits(
            args.paired_perturb_qubits,
            n_qubits=args.qubits,
        )
    except Exception as exc:
        print(f"paired-perturb-qubits parse fout: {exc}", file=sys.stderr)
        return 2
    try:
        initial_layout = _parse_initial_layout(args.initial_layout, n_qubits=1000000)
    except Exception as exc:
        print(f"initial-layout parse fout: {exc}", file=sys.stderr)
        return 2
    if initial_layout and len(initial_layout) != args.qubits:
        print(
            f"initial-layout moet precies {args.qubits} fysieke qubits bevatten; kreeg {len(initial_layout)}.",
            file=sys.stderr,
        )
        return 2

    perturb_qubits = paired_perturb_qubits if paired_perturb_qubits else [args.perturb_qubit]
    if paired_perturb_qubits and len(paired_perturb_qubits) < 2:
        print("paired-perturb-qubits moet minstens 2 qubits bevatten.", file=sys.stderr)
        return 2
    paired_mode = len(perturb_qubits) > 1
    if paired_mode and not args.readout_mitigation:
        print("paired-perturb-qubits vereist --readout-mitigation.", file=sys.stderr)
        return 2
    if args.readout_mitigation_method == "m3" and not args.readout_mitigation:
        print("--readout-mitigation-method m3 vereist --readout-mitigation.", file=sys.stderr)
        return 2
    if z_observable_blocks and subset_qubits:
        print(
            "--z-observable-blocks ondersteunt nu alleen full-register runs zonder --subset-qubits.",
            file=sys.stderr,
        )
        return 2
    if (
        z_observable_blocks
        and args.readout_mitigation
        and args.readout_mitigation_method == "local"
        and any(len(qubits_desc) > MAX_BLOCK_Z_LOCAL_TENSOR_QUBITS for _, qubits_desc in z_observable_blocks)
    ):
        print(
            f"Lokale block-Z mitigatie ondersteunt nu maximaal {MAX_BLOCK_Z_LOCAL_TENSOR_QUBITS} qubits per block.",
            file=sys.stderr,
        )
        return 2

    subset_desc = sorted(subset_qubits, reverse=True)
    ml_sidecar: Optional[MLSidecarBundle] = None

    if args.ml_sidecar_checkpoint is not None:
        if not subset_desc:
            print("--ml-sidecar-checkpoint vereist --subset-qubits.", file=sys.stderr)
            return 2
        if not args.readout_mitigation:
            print("--ml-sidecar-checkpoint vereist --readout-mitigation.", file=sys.stderr)
            return 2
        try:
            ml_sidecar = _load_ml_sidecar_bundle(
                checkpoint_path=args.ml_sidecar_checkpoint,
                model_path=args.ml_sidecar_model,
            )
        except Exception as exc:
            print(f"ml-sidecar load fout: {exc}", file=sys.stderr)
            return 2

    if args.qubits > MAX_EXACT_QUBITS and not args.skip_exact:
        print(
            f"Exact statevector referentie boven {MAX_EXACT_QUBITS} qubits is niet haalbaar; gebruik --skip-exact.",
            file=sys.stderr,
        )
        return 2

    mitigation_qubits_desc: List[int] = []
    use_dense_mitigation = True
    if args.readout_mitigation:
        if subset_desc:
            mitigation_qubits_desc = subset_desc
        else:
            mitigation_qubits_desc = list(range(args.qubits - 1, -1, -1))
        use_dense_mitigation = len(mitigation_qubits_desc) <= MAX_MITIGATION_SUBSET_QUBITS

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
    reuse_cal_job = None
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
        if args.reuse_calibration_job_id:
            reuse_cal_job = service.job(args.reuse_calibration_job_id)
            if backend_hint is None:
                try:
                    backend_hint = _backend_name(reuse_cal_job.backend())
                except Exception:
                    backend_hint = None
        backend = _select_backend(service, backend_hint, min_qubits=args.qubits)
    except Exception as exc:
        print(f"Runtime service/backend selectie faalde: {exc}", file=sys.stderr)
        return 1

    print(f"Backend: {_backend_name(backend)}")
    print(f"Qubits={args.qubits}, depths={depths}, trials/depth={args.trials}, shots={args.shots}")
    if paired_mode:
        print(f"Paired perturb-qubits: {perturb_qubits}")
    else:
        print(f"Perturb qubit: {perturb_qubits[0]}")
    if args.seed_transpiler is not None:
        print(f"Transpiler seed vastgezet op {args.seed_transpiler}")
    if initial_layout:
        print(f"Initial layout vastgezet op: {initial_layout}")
    if args.readout_mitigation:
        print(f"Readout mitigation method: {args.readout_mitigation_method}")
    if z_observable_blocks:
        print(
            "Z-observable blocks: "
            + ", ".join(f"{name}={qubits}" for name, qubits in z_observable_blocks)
        )

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
            exact_ideal = None if args.skip_exact else 1.0
            ideal_c: Optional[QuantumCircuit] = None
            pert_circuits: Dict[int, QuantumCircuit] = {}
            exact_perturbed_by_qubit: Dict[int, Optional[float]] = {}

            for perturb_qubit in perturb_qubits:
                built_ideal, pert_c = build_echo_measurement_circuits(
                    u_circuit=u_circuit,
                    n_qubits=args.qubits,
                    perturb_qubit=perturb_qubit,
                )
                if ideal_c is None:
                    ideal_c = built_ideal
                pert_circuits[perturb_qubit] = pert_c
                exact_perturbed_by_qubit[perturb_qubit] = (
                    None
                    if args.skip_exact
                    else _exact_perturbed_echo(
                        u_circuit,
                        n_qubits=args.qubits,
                        perturb_qubit=perturb_qubit,
                    )
                )

            if ideal_c is None:
                print("Geen geldige ideal circuit opgebouwd.", file=sys.stderr)
                return 1

            idx_ideal = len(circuits)
            circuits.append(ideal_c)
            for perturb_qubit in perturb_qubits:
                idx_pert = len(circuits)
                circuits.append(pert_circuits[perturb_qubit])
                pairs.append(
                    PairMeta(
                        depth=depth,
                        trial=trial,
                        seed=trial_seed,
                        perturb_qubit=perturb_qubit,
                        exact_ideal=exact_ideal,
                        exact_perturbed=exact_perturbed_by_qubit[perturb_qubit],
                        idx_ideal=idx_ideal,
                        idx_perturbed=idx_pert,
                    )
                )

    transpile_kwargs: Dict[str, Any] = {
        "backend": backend,
        "optimization_level": args.optimization_level,
    }
    if args.seed_transpiler is not None:
        transpile_kwargs["seed_transpiler"] = args.seed_transpiler
    if initial_layout:
        transpile_kwargs["initial_layout"] = initial_layout

    tcircuits = transpile(circuits, **transpile_kwargs)
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
    p01: Optional[np.ndarray] = None
    p10: Optional[np.ndarray] = None
    m3_mitigator: Optional[Any] = None

    if args.readout_mitigation:
        cal0 = QuantumCircuit(args.qubits, args.qubits, name="cal_all0")
        cal0.measure(range(args.qubits), range(args.qubits))

        cal1 = QuantumCircuit(args.qubits, args.qubits, name="cal_all1")
        for q in range(args.qubits):
            cal1.x(q)
        cal1.measure(range(args.qubits), range(args.qubits))

        tcal = transpile([cal0, cal1], **transpile_kwargs)
        if not isinstance(tcal, list):
            tcal = [tcal]

        if len(tcal) != 2:
            print("Calibration transpile gaf niet precies 2 circuits terug.", file=sys.stderr)
            return 1

        try:
            if args.reuse_calibration_job_id:
                if reuse_cal_job is None:
                    reuse_cal_job = service.job(args.reuse_calibration_job_id)
                calibration_job_id = str(args.reuse_calibration_job_id)
                cal_result = reuse_cal_job.result()
                calibration_job = reuse_cal_job
            else:
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
            calibration_info = {
                **cal_info,
                "local_model": "independent per-qubit asymmetric readout",
                "calibration_job_id": calibration_job_id,
                "p01_mean": float(np.mean(p01)),
                "p10_mean": float(np.mean(p10)),
                "mitigation_qubits": list(reversed(mitigation_qubits_desc)),
                "mitigation_qubit_count": len(mitigation_qubits_desc),
                "mitigation_strategy": None,
                "mitigation_method": args.readout_mitigation_method,
            }
            if args.readout_mitigation_method == "m3":
                m3_mitigator, m3_info = _build_m3_marginal_mitigator(
                    cal_counts[0],
                    cal_counts[1],
                    n_qubits=args.qubits,
                    cal_shots=args.cal_shots,
                )
                calibration_info["local_model"] = "m3 marginal single-qubit calibration"
                calibration_info["mitigation_strategy"] = "m3_quasi_distribution"
                calibration_info["m3"] = m3_info
            else:
                calibration_info["mitigation_strategy"] = (
                    "dense_assignment"
                    if use_dense_mitigation
                    else "direct_local_tensor_p_zero"
                )
                if use_dense_mitigation:
                    assignment = _build_assignment_for_qubits(
                        p01=p01,
                        p10=p10,
                        qubits_desc=mitigation_qubits_desc,
                    )
                    calibration_info["assignment_condition_number"] = float(np.linalg.cond(assignment))
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
            "perturb_qubit": pair.perturb_qubit,
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
        raw_dist_ideal = _distributional_observables_from_counts(counts_i, n_qubits=args.qubits)
        raw_dist_pert = _distributional_observables_from_counts(counts_p, n_qubits=args.qubits)
        record["distributional_observables"] = {
            "ideal": raw_dist_ideal,
            "perturbed": raw_dist_pert,
        }
        raw_hamming_ideal = _hamming_return_linear_from_one_probs(
            list(raw_dist_ideal["one_probability_by_qubit"])
        )
        raw_hamming_pert = _hamming_return_linear_from_one_probs(
            list(raw_dist_pert["one_probability_by_qubit"])
        )
        raw_hamming_relative = _relative_perturbed_echo(raw_hamming_ideal, raw_hamming_pert)
        record["distributional_estimators"] = {
            "raw": {
                "ideal_hamming_return_linear": raw_hamming_ideal,
                "perturbed_hamming_return_linear": raw_hamming_pert,
                "relative_hamming_return_linear": raw_hamming_relative["value"],
                "relative_hamming_return_linear_unclipped": raw_hamming_relative["unclipped"],
            }
        }
        if z_observable_blocks:
            raw_one_probs_i = list(raw_dist_ideal["one_probability_by_qubit"])
            raw_one_probs_p = list(raw_dist_pert["one_probability_by_qubit"])
            record["z_observable_blocks"] = {
                "raw": _build_block_z_variant_record(
                    _build_block_z_observables_from_counts(
                        counts_i,
                        n_qubits=args.qubits,
                        named_blocks=z_observable_blocks,
                        one_probs=raw_one_probs_i,
                    ),
                    _build_block_z_observables_from_counts(
                        counts_p,
                        n_qubits=args.qubits,
                        named_blocks=z_observable_blocks,
                        one_probs=raw_one_probs_p,
                    ),
                )
            }

        raw_relative = _relative_perturbed_echo(raw_ideal, raw_pert)
        record["raw"]["relative_perturbed_echo"] = raw_relative["value"]
        record["raw"]["relative_perturbed_echo_unclipped"] = raw_relative["unclipped"]

        if pair.exact_ideal is not None and pair.exact_perturbed is not None:
            exact_relative = _relative_perturbed_echo(pair.exact_ideal, pair.exact_perturbed)
            record["exact"] = {
                "ideal_echo": pair.exact_ideal,
                "perturbed_echo": pair.exact_perturbed,
                "relative_perturbed_echo": exact_relative["value"],
            }
            record["raw"]["ideal_abs_error_vs_exact"] = abs(raw_ideal - pair.exact_ideal)
            record["raw"]["perturbed_abs_error_vs_exact"] = abs(raw_pert - pair.exact_perturbed)
            record["raw"]["relative_perturbed_abs_error_vs_exact"] = abs(
                raw_relative["value"] - exact_relative["value"]
            )

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

        if args.readout_mitigation:
            mitigated_dist_ideal: Optional[Dict[str, object]] = None
            mitigated_dist_pert: Optional[Dict[str, object]] = None
            if args.readout_mitigation_method == "m3":
                if m3_mitigator is None:
                    raise RuntimeError("M3 mitigator ontbreekt ondanks gevraagde m3-mitigatie.")
                mit_i, mit_info_i, mitigated_dist_ideal = _apply_m3_correction(
                    counts_i,
                    mitigator=m3_mitigator,
                    n_qubits=args.qubits,
                    qubits_desc=mitigation_qubits_desc,
                )
                mit_p, mit_info_p, mitigated_dist_pert = _apply_m3_correction(
                    counts_p,
                    mitigator=m3_mitigator,
                    n_qubits=args.qubits,
                    qubits_desc=mitigation_qubits_desc,
                )
            elif assignment is not None:
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
            else:
                if p01 is None or p10 is None:
                    raise RuntimeError("Lokale readout-parameters ontbreken.")
                mit_i, mit_info_i = _mitigate_p_zero_local_tensor(
                    counts_i,
                    p01=p01,
                    p10=p10,
                    n_qubits=args.qubits,
                    qubits_desc=mitigation_qubits_desc,
                )
                mit_p, mit_info_p = _mitigate_p_zero_local_tensor(
                    counts_p,
                    p01=p01,
                    p10=p10,
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
                    "mitigation_method": args.readout_mitigation_method,
                }
                if ml_sidecar is not None:
                    record["ml_diagnostic"] = _predict_ml_sidecar_subset_echo(
                        ml_sidecar,
                        total_qubits=args.qubits,
                        subset_qubits=subset_qubits,
                        depth=pair.depth,
                        trial=pair.trial,
                        perturb_qubit=pair.perturb_qubit,
                        raw_subset_perturbed_echo=raw_subset_p,
                        mitigated_subset_perturbed_echo=mit_p,
                        logical_pert_depth=int(t_p.depth()),
                        logical_pert_two_qubit_count=_count_two_qubit_gates(t_p),
                        extra_error_suppression=bool(args.extra_error_suppression),
                    )
                    record["ml_diagnostic"]["subset_qubits"] = subset_qubits
            else:
                mit_relative = _relative_perturbed_echo(mit_i, mit_p)
                if args.readout_mitigation_method == "m3":
                    if mitigated_dist_ideal is None or mitigated_dist_pert is None:
                        raise RuntimeError("M3-distributionele observabelen ontbreken.")
                    mitigated_one_probs_i = list(mitigated_dist_ideal["one_probability_by_qubit"])
                    mitigated_one_probs_p = list(mitigated_dist_pert["one_probability_by_qubit"])
                else:
                    if p01 is None or p10 is None:
                        raise RuntimeError("Lokale readout-parameters ontbreken.")
                    mitigated_one_probs_i = [
                        _mitigate_one_probability(
                            float(raw_dist_ideal["one_probability_by_qubit"][q]),
                            float(p01[q]),
                            float(p10[q]),
                        )
                        for q in range(args.qubits)
                    ]
                    mitigated_one_probs_p = [
                        _mitigate_one_probability(
                            float(raw_dist_pert["one_probability_by_qubit"][q]),
                            float(p01[q]),
                            float(p10[q]),
                        )
                        for q in range(args.qubits)
                    ]
                mit_hamming_ideal = _hamming_return_linear_from_one_probs(mitigated_one_probs_i)
                mit_hamming_pert = _hamming_return_linear_from_one_probs(mitigated_one_probs_p)
                mit_hamming_relative = _relative_perturbed_echo(
                    mit_hamming_ideal,
                    mit_hamming_pert,
                )
                record["readout_mitigated"] = {
                    "ideal_echo": mit_i,
                    "perturbed_echo": mit_p,
                    "relative_perturbed_echo": mit_relative["value"],
                    "relative_perturbed_echo_unclipped": mit_relative["unclipped"],
                    "ideal_negative_mass_before_clip": mit_info_i["negative_mass_before_clip"],
                    "perturbed_negative_mass_before_clip": mit_info_p["negative_mass_before_clip"],
                    "mitigation_method": args.readout_mitigation_method,
                }
                record["distributional_estimators"]["readout_mitigated"] = {
                    "ideal_hamming_return_linear": mit_hamming_ideal,
                    "perturbed_hamming_return_linear": mit_hamming_pert,
                    "relative_hamming_return_linear": mit_hamming_relative["value"],
                    "relative_hamming_return_linear_unclipped": mit_hamming_relative["unclipped"],
                }
                if z_observable_blocks:
                    if args.readout_mitigation_method == "m3":
                        if mitigated_dist_ideal is None or mitigated_dist_pert is None:
                            raise RuntimeError("M3 block-Z observabelen ontbreken.")
                        record["z_observable_blocks"]["readout_mitigated"] = _build_block_z_variant_record(
                            _build_block_z_observables_from_weighted_distribution(
                                mitigated_dist_ideal["weighted_distribution"],
                                n_qubits=args.qubits,
                                named_blocks=z_observable_blocks,
                                one_probs=mitigated_one_probs_i,
                            ),
                            _build_block_z_observables_from_weighted_distribution(
                                mitigated_dist_pert["weighted_distribution"],
                                n_qubits=args.qubits,
                                named_blocks=z_observable_blocks,
                                one_probs=mitigated_one_probs_p,
                            ),
                        )
                    else:
                        if p01 is None or p10 is None:
                            raise RuntimeError("Lokale readout-parameters ontbreken.")
                        record["z_observable_blocks"]["readout_mitigated"] = _build_block_z_variant_record(
                            _build_block_z_observables_from_local_mitigation(
                                counts_i,
                                p01=p01,
                                p10=p10,
                                n_qubits=args.qubits,
                                named_blocks=z_observable_blocks,
                                one_probs=mitigated_one_probs_i,
                            ),
                            _build_block_z_observables_from_local_mitigation(
                                counts_p,
                                p01=p01,
                                p10=p10,
                                n_qubits=args.qubits,
                                named_blocks=z_observable_blocks,
                                one_probs=mitigated_one_probs_p,
                            ),
                        )
                if args.readout_mitigation_method == "m3":
                    record["distributional_observables_readout_mitigated"] = {
                        "ideal": mitigated_dist_ideal,
                        "perturbed": mitigated_dist_pert,
                    }
                    record["readout_mitigated"]["ideal_echo_unclipped"] = mit_info_i["p_zero_unclipped"]
                    record["readout_mitigated"]["perturbed_echo_unclipped"] = mit_info_p["p_zero_unclipped"]
                    record["readout_mitigated"]["ideal_m3_solver"] = mit_info_i["solver_details"]
                    record["readout_mitigated"]["perturbed_m3_solver"] = mit_info_p["solver_details"]
                    record["readout_mitigated"]["ideal_m3_nearest_probability_l2_distance"] = mit_info_i[
                        "nearest_probability_l2_distance"
                    ]
                    record["readout_mitigated"]["perturbed_m3_nearest_probability_l2_distance"] = mit_info_p[
                        "nearest_probability_l2_distance"
                    ]
                if pair.exact_ideal is not None and pair.exact_perturbed is not None:
                    record["readout_mitigated"]["ideal_abs_error_vs_exact"] = abs(mit_i - pair.exact_ideal)
                    record["readout_mitigated"]["perturbed_abs_error_vs_exact"] = abs(
                        mit_p - pair.exact_perturbed
                    )
                    record["readout_mitigated"]["relative_perturbed_abs_error_vs_exact"] = abs(
                        mit_relative["value"] - record["exact"]["relative_perturbed_echo"]
                    )

        runs.append(record)

    summary_by_depth: List[Dict[str, object]] = []
    for depth in sorted({r["depth"] for r in runs}):
        rows = [r for r in runs if r["depth"] == depth]
        if paired_mode:
            entry: Dict[str, object] = {
                "depth": depth,
                "paired_branch_comparison": _build_paired_branch_comparison(rows, perturb_qubits),
                "branches": [],
            }
            for perturb_qubit in perturb_qubits:
                branch_rows = [r for r in rows if int(r["perturb_qubit"]) == perturb_qubit]
                branch_entry = _build_branch_summary(branch_rows)
                branch_entry["perturb_qubit"] = perturb_qubit
                entry["branches"].append(branch_entry)
        else:
            entry = {"depth": depth, **_build_branch_summary(rows)}

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
            "paired_perturb_qubits": perturb_qubits if paired_mode else [],
            "paired_mode": paired_mode,
            "optimization_level": args.optimization_level,
            "seed_transpiler": args.seed_transpiler,
            "initial_layout": initial_layout,
            "readout_mitigation": bool(args.readout_mitigation),
            "readout_mitigation_method": args.readout_mitigation_method if args.readout_mitigation else None,
            "cal_shots": args.cal_shots,
            "skip_exact": bool(args.skip_exact),
            "subset_qubits": subset_qubits,
            "z_observable_blocks": [
                {
                    "name": name,
                    "qubits": list(qubits_desc),
                }
                for name, qubits_desc in z_observable_blocks
            ],
            "preferred_full_register_estimator": (
                "readout_mitigated.relative_perturbed_echo_robust.median"
                if args.readout_mitigation and not subset_desc
                else (
                    "raw.relative_perturbed_echo_robust.median"
                    if not subset_desc
                    else None
                )
            ),
            "ml_sidecar_checkpoint": str(args.ml_sidecar_checkpoint)
            if args.ml_sidecar_checkpoint is not None
            else None,
            "ml_sidecar_model": str(args.ml_sidecar_model)
            if args.ml_sidecar_checkpoint is not None
            else None,
            "ml_diagnostic_only": bool(ml_sidecar is not None),
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
            "reused_calibration_job_id": args.reuse_calibration_job_id,
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

    if paired_mode:
        print("depth | pert_q | raw_ideal       | raw_pert")
        for entry in summary_by_depth:
            d = int(entry["depth"])
            for branch in entry["branches"]:
                raw_i = branch["raw"]["ideal_echo"]
                raw_p = branch["raw"]["perturbed_echo"]
                print(
                    f"{d:>5d} | "
                    f"{int(branch['perturb_qubit']):>6d} | "
                    f"{raw_i['mean']:8.5f}±{raw_i['std']:7.5f} | "
                    f"{raw_p['mean']:8.5f}±{raw_p['std']:7.5f}"
                )

        if args.readout_mitigation:
            print("depth | pert_q | mit_ideal       | mit_pert")
            for entry in summary_by_depth:
                d = int(entry["depth"])
                for branch in entry["branches"]:
                    mit_i = branch["readout_mitigated"]["ideal_echo"]
                    mit_p = branch["readout_mitigated"]["perturbed_echo"]
                    print(
                        f"{d:>5d} | "
                        f"{int(branch['perturb_qubit']):>6d} | "
                        f"{mit_i['mean']:8.5f}±{mit_i['std']:7.5f} | "
                        f"{mit_p['mean']:8.5f}±{mit_p['std']:7.5f}"
                    )
            print("depth | pert_q | mit_rel_pert   | median/mad")
            for entry in summary_by_depth:
                d = int(entry["depth"])
                for branch in entry["branches"]:
                    rel = branch["readout_mitigated"]["relative_perturbed_echo"]
                    robust = branch["readout_mitigated"]["relative_perturbed_echo_robust"]
                    print(
                        f"{d:>5d} | "
                        f"{int(branch['perturb_qubit']):>6d} | "
                        f"{rel['mean']:8.5f}±{rel['std']:7.5f} | "
                        f"median={robust['median']:.5f} mad={robust['mad']:.5f}"
                    )
            print("depth | anchor | compare | rel_delta      | median/mad")
            for entry in summary_by_depth:
                d = int(entry["depth"])
                for cmp_entry in entry["paired_branch_comparison"]["comparisons"]:
                    delta = cmp_entry["readout_mitigated"]["relative_perturbed_echo_delta"]
                    robust = cmp_entry["readout_mitigated"]["relative_perturbed_echo_delta_robust"]
                    trimmed = cmp_entry["readout_mitigated"][
                        "relative_perturbed_echo_delta_trimmed_diagnostic"
                    ]
                    print(
                        f"{d:>5d} | "
                        f"{int(cmp_entry['anchor_perturb_qubit']):>6d} | "
                        f"{int(cmp_entry['perturb_qubit']):>7d} | "
                        f"{delta['mean']:8.5f}±{delta['std']:7.5f} | "
                        f"median={robust['median']:.5f} mad={robust['mad']:.5f}"
                    )
                    if int(trimmed["dropped_count"]) > 0:
                        kept = trimmed["kept_robust"]
                        print(
                            f"       trimmed-diagnostic kept={trimmed['kept_count']} "
                            f"dropped={trimmed['dropped_count']} "
                            f"median={kept['median']:.5f} mad={kept['mad']:.5f}"
                        )
            print("depth | pert_q | ham_rel_lin    | median/mad")
            for entry in summary_by_depth:
                d = int(entry["depth"])
                for branch in entry["branches"]:
                    rel = branch["distributional_estimators"]["readout_mitigated"][
                        "relative_hamming_return_linear"
                    ]
                    robust = branch["distributional_estimators"]["readout_mitigated"][
                        "relative_hamming_return_linear_robust"
                    ]
                    print(
                        f"{d:>5d} | "
                        f"{int(branch['perturb_qubit']):>6d} | "
                        f"{rel['mean']:8.5f}±{rel['std']:7.5f} | "
                        f"median={robust['median']:.5f} mad={robust['mad']:.5f}"
                    )
            print("depth | anchor | compare | ham_delta      | median/mad")
            for entry in summary_by_depth:
                d = int(entry["depth"])
                for cmp_entry in entry["paired_branch_comparison"]["comparisons"]:
                    delta = cmp_entry["distributional_estimators"]["readout_mitigated"][
                        "relative_hamming_return_linear_delta"
                    ]
                    robust = cmp_entry["distributional_estimators"]["readout_mitigated"][
                        "relative_hamming_return_linear_delta_robust"
                    ]
                    trimmed = cmp_entry["distributional_estimators"]["readout_mitigated"][
                        "relative_hamming_return_linear_delta_trimmed_diagnostic"
                    ]
                    print(
                        f"{d:>5d} | "
                        f"{int(cmp_entry['anchor_perturb_qubit']):>6d} | "
                        f"{int(cmp_entry['perturb_qubit']):>7d} | "
                        f"{delta['mean']:8.5f}±{delta['std']:7.5f} | "
                        f"median={robust['median']:.5f} mad={robust['mad']:.5f}"
                    )
                    if int(trimmed["dropped_count"]) > 0:
                        kept = trimmed["kept_robust"]
                        print(
                            f"       hamming-trimmed kept={trimmed['kept_count']} "
                            f"dropped={trimmed['dropped_count']} "
                            f"median={kept['median']:.5f} mad={kept['mad']:.5f}"
                        )
    else:
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
                if ml_sidecar is not None:
                    print("depth | ml_subset_pert | ml_delta_vs_mit")
                    for entry in summary_by_depth:
                        d = int(entry["depth"])
                        ml_p = entry["ml_diagnostic"]["perturbed_subset_echo"]
                        ml_d = entry["ml_diagnostic"]["delta_vs_mitigated"]
                        print(
                            f"{d:>5d} | "
                            f"{ml_p['mean']:8.5f}±{ml_p['std']:7.5f} | "
                            f"{ml_d['mean']:8.5f}±{ml_d['std']:7.5f}"
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
                    stability = entry["readout_mitigated"].get("perturbed_echo_stability")
                    if stability and stability.get("flags"):
                        flags = ",".join(str(flag) for flag in stability["flags"])
                        print(
                            f"       mitigated-stability flags={flags} "
                            f"median={stability['median']:.5f} "
                            f"min={stability['min']:.5f} max={stability['max']:.5f}"
                        )
                print("depth | mit_rel_pert   | median/mad")
                for entry in summary_by_depth:
                    d = int(entry["depth"])
                    rel = entry["readout_mitigated"]["relative_perturbed_echo"]
                    robust = entry["readout_mitigated"]["relative_perturbed_echo_robust"]
                    print(
                        f"{d:>5d} | "
                        f"{rel['mean']:8.5f}±{rel['std']:7.5f} | "
                        f"median={robust['median']:.5f} mad={robust['mad']:.5f}"
                    )
                    stability = entry["readout_mitigated"].get("relative_perturbed_echo_stability")
                    if stability and stability.get("flags"):
                        flags = ",".join(str(flag) for flag in stability["flags"])
                        print(
                            f"       relative-stability flags={flags} "
                            f"median={stability['median']:.5f} "
                            f"min={stability['min']:.5f} max={stability['max']:.5f}"
                        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
