#!/usr/bin/env python3
"""Generate a q80-subset-shaped surrogate dataset for PE-LiNN diagnostics.

This does not produce claim-bearing q80 evidence. It builds a smaller exact
surrogate with the same subset-observable shape we care about for q80:
`perturbed_subset_echo` under overlap/disjoint branches, finite-shot noise,
readout mitigation, and optional ZNE-like noise scaling factors.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Dict, List, Sequence

import numpy as np
from qiskit.quantum_info import Statevector

from qiskit_black_hole_hardware_runner import (
    _aggregate_counts_on_qubits,
    _count_two_qubit_gates,
    _parse_subset_qubits,
)
from qiskit_black_hole_scrambling import (
    brickwork_scrambler,
    build_echo_measurement_circuits,
    mitigate_all_zero_probability,
    parse_depths,
    parse_noise_factors,
    sample_with_fallback_noise,
    try_aer_noise_run_pair,
)


FEATURE_NAMES = [
    "total_qubits",
    "subset_size",
    "depth",
    "trial",
    "branch_overlap",
    "perturb_qubit_norm",
    "raw_subset_perturbed_echo",
    "mitigated_subset_perturbed_echo",
    "mitigation_gain",
    "logical_pert_depth",
    "logical_pert_two_qubit_count",
    "zne_factor",
    "noise_dep_effective",
    "noise_readout_effective",
    "suppression_enabled",
]


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--surrogate-qubits", type=int, default=20)
    p.add_argument("--subset-qubits", type=str, default="10-19")
    p.add_argument("--depths", type=str, default="1,2,3,4")
    p.add_argument("--trials", type=int, default=6)
    p.add_argument("--seed", type=int, default=424242)
    p.add_argument("--shots", type=int, default=4000)
    p.add_argument("--noise-dep", type=float, default=0.04)
    p.add_argument("--noise-readout", type=float, default=0.02)
    p.add_argument("--zne-factors", type=str, default="1,3,5")
    p.add_argument("--include-suppressed", action="store_true")
    p.add_argument("--suppression-dep-scale", type=float, default=0.75)
    p.add_argument("--suppression-readout-scale", type=float, default=0.85)
    p.add_argument("--progress-every", type=int, default=10)
    p.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results/hardware/phase3_q80_subset_pelinn_surrogate"),
    )
    return p.parse_args(argv)


def exact_subset_zero_probability(circuit, n_qubits: int, subset_qubits: List[int]) -> float:
    qc = circuit.remove_final_measurements(inplace=False)
    sv = Statevector.from_instruction(qc)
    probs = np.asarray(sv.probabilities(), dtype=float)
    total = 0.0
    for idx, prob in enumerate(probs.tolist()):
        keep = True
        for q in subset_qubits:
            if (idx >> q) & 1:
                keep = False
                break
        if keep:
            total += float(prob)
    return float(total)


def subset_zero_from_counts(counts: Dict[str, int], n_qubits: int, subset_desc: List[int]) -> float:
    sub_counts = _aggregate_counts_on_qubits(counts, n_qubits=n_qubits, qubits_desc=subset_desc)
    total = float(sum(sub_counts.values()))
    if total <= 0.0:
        raise ValueError("Subset histogram is leeg.")
    return float(sub_counts.get("0" * len(subset_desc), 0)) / total


def mitigated_subset_zero_from_counts(
    counts: Dict[str, int],
    n_qubits: int,
    subset_desc: List[int],
    p_ro: float,
) -> float:
    sub_counts = _aggregate_counts_on_qubits(counts, n_qubits=n_qubits, qubits_desc=subset_desc)
    value, _ = mitigate_all_zero_probability(
        sub_counts,
        n_qubits=len(subset_desc),
        shots=int(sum(sub_counts.values())),
        p_ro=p_ro,
    )
    return float(value)


def write_partial_artifacts(
    output_dir: Path,
    samples: List[List[float]],
    targets: List[float],
    metadata: List[Dict[str, object]],
    progress_payload: Dict[str, object],
) -> None:
    if not samples:
        return
    np.savez(
        output_dir / "partial_dataset.npz",
        X=np.asarray(samples, dtype=np.float32),
        Y=np.asarray(targets, dtype=np.float32),
        metadata=np.asarray(metadata, dtype=object),
        feature_names=np.asarray(FEATURE_NAMES, dtype=object),
    )
    (output_dir / "progress.json").write_text(json.dumps(progress_payload, indent=2))


def maybe_run_noisy_pair(
    ideal_circuit,
    pert_circuit,
    shots: int,
    seed: int,
    p_dep: float,
    p_ro: float,
    n_qubits: int,
):
    aer_ok, counts_ideal, counts_pert, mode = try_aer_noise_run_pair(
        ideal_circuit=ideal_circuit,
        pert_circuit=pert_circuit,
        shots=shots,
        seed=seed,
        p_dep=p_dep,
        p_ro=p_ro,
    )
    if aer_ok:
        return counts_ideal, counts_pert, mode

    probs_ideal = np.asarray(
        Statevector.from_instruction(ideal_circuit.remove_final_measurements(inplace=False)).probabilities(),
        dtype=float,
    )
    probs_pert = np.asarray(
        Statevector.from_instruction(pert_circuit.remove_final_measurements(inplace=False)).probabilities(),
        dtype=float,
    )
    counts_ideal = sample_with_fallback_noise(
        ideal_probs=probs_ideal,
        shots=shots,
        rng=np.random.default_rng(seed),
        p_dep=p_dep,
        p_ro=p_ro,
        n_qubits=n_qubits,
    )
    counts_pert = sample_with_fallback_noise(
        ideal_probs=probs_pert,
        shots=shots,
        rng=np.random.default_rng(seed + 1),
        p_dep=p_dep,
        p_ro=p_ro,
        n_qubits=n_qubits,
    )
    return counts_ideal, counts_pert, mode


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.surrogate_qubits > 24:
        raise ValueError("surrogate-qubits must stay <= 24 for exact statevector labels.")

    subset_qubits = _parse_subset_qubits(args.subset_qubits, n_qubits=args.surrogate_qubits)
    if not subset_qubits:
        raise ValueError("subset-qubits mag niet leeg zijn.")
    subset_desc = sorted(subset_qubits, reverse=True)
    depths = parse_depths(args.depths)
    zne_factors = parse_noise_factors(args.zne_factors)
    suppression_modes = [False, True] if args.include_suppressed else [False]
    total_samples = len(depths) * args.trials * 2 * len(zne_factors) * len(suppression_modes)
    completed_samples = 0
    started_at = time.time()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    partial_jsonl = args.output_dir / "partial_records.jsonl"
    partial_jsonl.write_text("")
    master_rng = np.random.default_rng(args.seed)

    samples: List[List[float]] = []
    targets: List[float] = []
    metadata: List[Dict[str, object]] = []
    circuit_index_map: Dict[str, int] = {}
    backend_mode_counts: Dict[str, int] = {}

    for depth in depths:
        for trial in range(args.trials):
            trial_seed = int(master_rng.integers(0, 2**32 - 1))
            rng = np.random.default_rng(trial_seed)
            u_circuit = brickwork_scrambler(args.surrogate_qubits, depth=depth, rng=rng)

            for perturb_qubit in (0, 10):
                ideal_c, pert_c = build_echo_measurement_circuits(
                    u_circuit=u_circuit,
                    n_qubits=args.surrogate_qubits,
                    perturb_qubit=perturb_qubit,
                )
                exact_subset_pert = exact_subset_zero_probability(
                    pert_c,
                    n_qubits=args.surrogate_qubits,
                    subset_qubits=subset_qubits,
                )
                circuit_key = f"d{depth}|t{trial}|s{trial_seed}|q{perturb_qubit}"
                circuit_index = circuit_index_map.setdefault(circuit_key, len(circuit_index_map))

                for suppression_enabled in suppression_modes:
                    dep_scale = args.suppression_dep_scale if suppression_enabled else 1.0
                    ro_scale = args.suppression_readout_scale if suppression_enabled else 1.0

                    for factor in zne_factors:
                        if args.progress_every > 0:
                            elapsed_pre = time.time() - started_at
                            print(
                                (
                                    f"[start] {completed_samples + 1}/{total_samples} "
                                    f"depth={depth} trial={trial} branch="
                                    f"{'overlap' if perturb_qubit == 0 else 'disjoint'} "
                                    f"factor={factor} suppressed={int(suppression_enabled)} "
                                    f"elapsed={elapsed_pre:.1f}s"
                                ),
                                flush=True,
                            )
                        p_dep_eff = float(np.clip(args.noise_dep * factor * dep_scale, 0.0, 0.999))
                        p_ro_eff = float(np.clip(args.noise_readout * factor * ro_scale, 0.0, 0.499))
                        noisy_seed = int(
                            (trial_seed + depth * 10007 + int(round(factor * 100)) + (1 if suppression_enabled else 0) * 1000003)
                            % (2**32 - 1)
                        )
                        counts_ideal, counts_pert, mode = maybe_run_noisy_pair(
                            ideal_circuit=ideal_c,
                            pert_circuit=pert_c,
                            shots=args.shots,
                            seed=noisy_seed,
                            p_dep=p_dep_eff,
                            p_ro=p_ro_eff,
                            n_qubits=args.surrogate_qubits,
                        )
                        backend_mode_counts[mode] = backend_mode_counts.get(mode, 0) + 2

                        raw_subset_pert = subset_zero_from_counts(
                            counts_pert,
                            n_qubits=args.surrogate_qubits,
                            subset_desc=subset_desc,
                        )
                        mit_subset_pert = mitigated_subset_zero_from_counts(
                            counts_pert,
                            n_qubits=args.surrogate_qubits,
                            subset_desc=subset_desc,
                            p_ro=p_ro_eff,
                        )
                        samples.append(
                            [
                                float(args.surrogate_qubits),
                                float(len(subset_qubits)),
                                float(depth),
                                float(trial),
                                1.0 if perturb_qubit == 0 else 0.0,
                                float(perturb_qubit) / float(args.surrogate_qubits - 1),
                                float(raw_subset_pert),
                                float(mit_subset_pert),
                                float(mit_subset_pert - raw_subset_pert),
                                float(pert_c.depth()),
                                float(_count_two_qubit_gates(pert_c)),
                                float(factor),
                                float(p_dep_eff),
                                float(p_ro_eff),
                                1.0 if suppression_enabled else 0.0,
                            ]
                        )
                        targets.append(float(exact_subset_pert))
                        sample_meta = {
                            "circuit_index": int(circuit_index),
                            "depth": int(depth),
                            "trial": int(trial),
                            "seed": int(trial_seed),
                            "perturb_qubit": int(perturb_qubit),
                            "branch": "overlap" if perturb_qubit == 0 else "disjoint",
                            "subset_qubits": list(subset_qubits),
                            "target_name": "exact_perturbed_subset_echo",
                            "zne_factor": float(factor),
                            "suppression_enabled": bool(suppression_enabled),
                            "raw_subset_perturbed_echo": float(raw_subset_pert),
                            "mitigated_subset_perturbed_echo": float(mit_subset_pert),
                            "exact_perturbed_subset_echo": float(exact_subset_pert),
                        }
                        metadata.append(sample_meta)
                        with partial_jsonl.open("a", encoding="utf-8") as fh:
                            fh.write(json.dumps(sample_meta) + "\n")
                        completed_samples += 1
                        elapsed = time.time() - started_at
                        rate = completed_samples / elapsed if elapsed > 0.0 else 0.0
                        remaining = total_samples - completed_samples
                        eta = remaining / rate if rate > 0.0 else float("inf")
                        write_partial_artifacts(
                            args.output_dir,
                            samples,
                            targets,
                            metadata,
                            {
                                "completed_samples": int(completed_samples),
                                "total_samples": int(total_samples),
                                "percent_complete": float(100.0 * completed_samples / total_samples),
                                "elapsed_seconds": float(elapsed),
                                "eta_seconds": float(eta),
                                "last_sample": sample_meta,
                                "feature_names": FEATURE_NAMES,
                            },
                        )
                        if args.progress_every > 0 and (
                            completed_samples % args.progress_every == 0 or completed_samples == total_samples
                        ):
                            print(
                                (
                                    f"[progress] {completed_samples}/{total_samples} "
                                    f"({100.0 * completed_samples / total_samples:.1f}%) "
                                    f"depth={depth} trial={trial} branch="
                                    f"{'overlap' if perturb_qubit == 0 else 'disjoint'} "
                                    f"factor={factor} suppressed={int(suppression_enabled)} "
                                    f"elapsed={elapsed:.1f}s eta="
                                    f"{eta:.1f}s"
                                ),
                                flush=True,
                            )

    X = np.asarray(samples, dtype=np.float32)
    Y = np.asarray(targets, dtype=np.float32)
    metadata_arr = np.asarray(metadata, dtype=object)

    np.savez(
        args.output_dir / "q80_subset_surrogate_dataset.npz",
        X=X,
        Y=Y,
        metadata=metadata_arr,
        feature_names=np.asarray(FEATURE_NAMES, dtype=object),
    )

    summary = {
        "feature_names": FEATURE_NAMES,
        "dataset_samples": int(len(X)),
        "unique_logical_circuits": int(len(circuit_index_map)),
        "surrogate_qubits": int(args.surrogate_qubits),
        "subset_qubits": list(subset_qubits),
        "depths": depths,
        "trials": int(args.trials),
        "shots": int(args.shots),
        "zne_factors": [float(x) for x in zne_factors],
        "include_suppressed": bool(args.include_suppressed),
        "backend_modes": backend_mode_counts,
        "target": "exact_perturbed_subset_echo",
        "observable_shape": "q80-subset-like perturbed_subset_echo surrogate",
    }
    (args.output_dir / "summary.json").write_text(json.dumps(summary, indent=2))

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
