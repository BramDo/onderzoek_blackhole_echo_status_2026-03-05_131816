#!/usr/bin/env python3
"""Build a canonical subset-ML dataset from hardware JSONs and/or surrogate NPZs.

This is a repo-local data preparation step for follow-on ML-QEM work.
It does not implement IBM ML-QEM directly. It normalizes current project
artifacts into one feature schema so multiple sidecar methods can train on
the same dataset.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
from qiskit.quantum_info import Statevector

from qiskit_black_hole_scrambling import brickwork_scrambler, build_echo_measurement_circuits


FEATURE_NAMES = [
    "qubits",
    "subset_size",
    "depth",
    "trial",
    "branch_overlap",
    "perturb_qubit_norm",
    "raw_perturbed_echo",
    "mitigated_perturbed_echo",
    "mitigation_gain",
    "transpiled_depth",
    "two_qubit_gate_count",
    "zne_factor",
    "optimization_level",
    "seed_transpiler",
    "extra_error_suppression",
    "twirl_randomizations",
]


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--hardware-json",
        type=Path,
        nargs="*",
        default=[],
        help="Hardware runner JSONs produced by qiskit_black_hole_hardware_runner.py.",
    )
    parser.add_argument(
        "--surrogate-npz",
        type=Path,
        nargs="*",
        default=[],
        help="Surrogate NPZs such as q80_subset_surrogate_dataset.npz.",
    )
    parser.add_argument(
        "--target-field",
        type=str,
        default="readout_mitigated.perturbed_subset_echo",
        help=(
            "Dot-path target field for hardware JSON runs. Use 'auto' to pick the first "
            "available trusted field."
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results/hardware/ml_qem_dataset"),
    )
    parser.add_argument(
        "--dataset-name",
        type=str,
        default="subset_ml_dataset",
    )
    parser.add_argument(
        "--progress-every",
        type=int,
        default=1,
        help="Emit a progress line every N processed rows.",
    )
    parser.add_argument(
        "--checkpoint-every",
        type=int,
        default=1,
        help="Write partial dataset/progress snapshots every N processed rows.",
    )
    return parser.parse_args(argv)


def _read_json(path: Path) -> Dict[str, object]:
    return json.loads(path.read_text())


def _pick_nested(row: Dict[str, object], field: str) -> float:
    value: object = row
    for token in field.split("."):
        if not isinstance(value, dict) or token not in value:
            raise KeyError(field)
        value = value[token]
    return float(value)


def _pick_first_available(row: Dict[str, object], fields: Iterable[str]) -> Tuple[str, float]:
    for field in fields:
        try:
            return field, _pick_nested(row, field)
        except Exception:
            continue
    raise KeyError(f"No target field found in {list(fields)}")


def _auto_target_field(row: Dict[str, object]) -> Tuple[str, float]:
    return _pick_first_available(
        row,
        (
            "trusted.perturbed_subset_echo",
            "trusted.perturbed_echo",
            "readout_mitigated.perturbed_subset_echo",
            "readout_mitigated.perturbed_echo",
            "exact.perturbed_subset_echo",
            "exact.perturbed_echo",
            "raw.perturbed_subset_echo",
            "raw.perturbed_echo",
        ),
    )


def _target_from_row(row: Dict[str, object], target_field: str) -> Tuple[str, float]:
    if target_field == "auto":
        return _auto_target_field(row)
    return target_field, _pick_nested(row, target_field)


def _exact_subset_zero_probability(circuit, subset_qubits: List[int]) -> float:
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


def _derive_exact_subset_target(
    *,
    qubits: int,
    depth: int,
    seed: int,
    perturb_qubit: int,
    subset_qubits: List[int],
) -> float:
    rng = np.random.default_rng(seed)
    u_circuit = brickwork_scrambler(qubits, depth=depth, rng=rng)
    _, pert_circuit = build_echo_measurement_circuits(
        u_circuit=u_circuit,
        n_qubits=qubits,
        perturb_qubit=perturb_qubit,
    )
    return _exact_subset_zero_probability(pert_circuit, subset_qubits=subset_qubits)


def _raw_feature_value(row: Dict[str, object]) -> float:
    return _pick_first_available(
        row,
        ("raw.perturbed_subset_echo", "raw.perturbed_echo"),
    )[1]


def _mitigated_feature_value(row: Dict[str, object]) -> float:
    return _pick_first_available(
        row,
        ("readout_mitigated.perturbed_subset_echo", "readout_mitigated.perturbed_echo"),
    )[1]


def _subset_qubits_for_row(config: Dict[str, object], row: Dict[str, object]) -> List[int]:
    subset = config.get("subset_qubits")
    if isinstance(subset, list) and subset:
        return [int(q) for q in subset]
    raw = row.get("raw", {})
    if isinstance(raw, dict):
        row_subset = raw.get("subset_qubits")
        if isinstance(row_subset, list) and row_subset:
            return [int(q) for q in row_subset]
    return []


def _branch_overlap(perturb_qubit: int, subset_qubits: List[int]) -> float:
    if subset_qubits:
        return 1.0 if perturb_qubit in subset_qubits else 0.0
    return 1.0 if perturb_qubit == 0 else 0.0


def _hardware_rows(
    path: Path,
    target_field: str,
    progress_every: int = 1,
    progress_cb: Optional[
        Callable[
            [List[List[float]], List[float], List[Dict[str, object]], List[int], Dict[str, object]],
            None,
        ]
    ] = None,
) -> Tuple[List[List[float]], List[float], List[Dict[str, object]], List[int]]:
    data = _read_json(path)
    config = dict(data.get("config", {}))
    runs = list(data.get("runs", []))
    rows: List[List[float]] = []
    targets: List[float] = []
    metadata: List[Dict[str, object]] = []
    groups: List[int] = []
    group_index: Dict[str, int] = {}

    qubits = int(config.get("qubits", 0))
    perturb_qubit = int(config.get("perturb_qubit", 0))
    optimization_level = int(config.get("optimization_level", -1))
    seed_transpiler = int(config.get("seed_transpiler", -1) or -1)
    extra_error_suppression = 1.0 if bool(config.get("extra_error_suppression", False)) else 0.0
    twirl_randomizations = float(config.get("twirl_randomizations") or 0.0)
    exact_subset_cache: Dict[Tuple[int, int, int], float] = {}
    started_at = time.time()
    total_runs = len(runs)

    for idx, row in enumerate(runs, start=1):
        if not isinstance(row, dict):
            continue
        subset_qubits = _subset_qubits_for_row(config, row)
        raw_value = _raw_feature_value(row)
        mitigated_value = _mitigated_feature_value(row)
        trial = int(row.get("trial", 0))
        depth = int(row.get("depth", 0))
        seed = int(row.get("seed", 0))
        transpiled = dict(row.get("transpiled", {})).get("perturbed", {})
        transpiled_depth = int(dict(transpiled).get("depth", 0))
        two_qubit_gate_count = int(dict(transpiled).get("two_qubit_gate_count", 0))

        if target_field == "exact.perturbed_subset_echo":
            if not subset_qubits:
                raise ValueError(
                    f"{path} requested exact.perturbed_subset_echo without subset_qubits."
                )
            if qubits > 24:
                raise ValueError(
                    f"{path} requested exact.perturbed_subset_echo at {qubits} qubits; offline exact subset target is capped at 24."
                )
            cache_key = (depth, seed, perturb_qubit)
            if cache_key not in exact_subset_cache:
                exact_subset_cache[cache_key] = _derive_exact_subset_target(
                    qubits=qubits,
                    depth=depth,
                    seed=seed,
                    perturb_qubit=perturb_qubit,
                    subset_qubits=subset_qubits,
                )
            target_name = target_field
            target_value = exact_subset_cache[cache_key]
        else:
            target_name, target_value = _target_from_row(row, target_field)

        group_key = (
            f"{path.stem}|q{qubits}|subset{','.join(map(str, subset_qubits))}|"
            f"depth{depth}|trial{trial}|seed{seed}|pert{perturb_qubit}"
        )
        group_id = group_index.setdefault(group_key, len(group_index))

        rows.append(
            [
                float(qubits),
                float(len(subset_qubits)),
                float(depth),
                float(trial),
                _branch_overlap(perturb_qubit, subset_qubits),
                float(perturb_qubit) / float(max(qubits - 1, 1)),
                float(raw_value),
                float(mitigated_value),
                float(mitigated_value - raw_value),
                float(transpiled_depth),
                float(two_qubit_gate_count),
                1.0,
                float(optimization_level),
                float(seed_transpiler),
                extra_error_suppression,
                twirl_randomizations,
            ]
        )
        targets.append(float(target_value))
        groups.append(int(group_id))
        metadata.append(
            {
                "source_kind": "hardware_json",
                "source_path": str(path),
                "target_name": target_name,
                "qubits": qubits,
                "subset_qubits": subset_qubits,
                "perturb_qubit": perturb_qubit,
                "depth": depth,
                "trial": trial,
                "seed": seed,
                "circuit_group": group_key,
                "group_id": group_id,
            }
        )
        if progress_cb is not None:
            progress_cb(
                rows,
                targets,
                metadata,
                groups,
                {
                    "source_kind": "hardware_json",
                    "source_path": str(path),
                    "rows_done": idx,
                    "rows_total": total_runs,
                    "depth": depth,
                    "trial": trial,
                    "seed": seed,
                    "elapsed_s": float(time.time() - started_at),
                },
            )
        if idx % max(progress_every, 1) == 0 or idx == total_runs:
            print(
                "[progress] "
                f"source={path.name} rows={idx}/{total_runs} "
                f"depth={depth} trial={trial} seed={seed} "
                f"elapsed={time.time() - started_at:.1f}s",
                flush=True,
            )

    return rows, targets, metadata, groups


def _surrogate_rows(path: Path) -> Tuple[List[List[float]], List[float], List[Dict[str, object]], List[int]]:
    data = np.load(path, allow_pickle=True)
    feature_names = [str(name) for name in data["feature_names"].tolist()]
    X = np.asarray(data["X"], dtype=np.float32)
    Y = np.asarray(data["Y"], dtype=np.float32)
    metadata_in = [dict(row) for row in data["metadata"].tolist()]

    index_map = {name: idx for idx, name in enumerate(feature_names)}

    def col(name: str, default: float = 0.0) -> np.ndarray:
        if name in index_map:
            return X[:, index_map[name]]
        return np.full(X.shape[0], default, dtype=np.float32)

    rows: List[List[float]] = []
    targets: List[float] = []
    metadata: List[Dict[str, object]] = []
    groups: List[int] = []
    group_index: Dict[str, int] = {}

    for idx, meta in enumerate(metadata_in):
        group_key = f"{path.stem}|{meta.get('circuit_index', idx)}"
        group_id = group_index.setdefault(group_key, len(group_index))
        rows.append(
            [
                float(col("total_qubits")[idx]),
                float(col("subset_size")[idx]),
                float(col("depth")[idx]),
                float(col("trial")[idx]),
                float(col("branch_overlap")[idx]),
                float(col("perturb_qubit_norm")[idx]),
                float(col("raw_subset_perturbed_echo")[idx]),
                float(col("mitigated_subset_perturbed_echo")[idx]),
                float(col("mitigation_gain")[idx]),
                float(col("logical_pert_depth")[idx]),
                float(col("logical_pert_two_qubit_count")[idx]),
                float(col("zne_factor", 1.0)[idx]),
                -1.0,
                -1.0,
                float(col("suppression_enabled", 0.0)[idx]),
                0.0,
            ]
        )
        targets.append(float(Y[idx]))
        groups.append(int(group_id))
        meta_out = dict(meta)
        meta_out.update(
            {
                "source_kind": "surrogate_npz",
                "source_path": str(path),
                "target_name": str(meta.get("target_name", "surrogate_target")),
                "circuit_group": group_key,
                "group_id": group_id,
            }
        )
        metadata.append(meta_out)

    return rows, targets, metadata, groups


def _shift_metadata_group_ids(
    metadata: List[Dict[str, object]],
    group_offset: int,
) -> List[Dict[str, object]]:
    shifted: List[Dict[str, object]] = []
    for row in metadata:
        row_out = dict(row)
        row_out["group_id"] = int(row_out["group_id"]) + group_offset
        shifted.append(row_out)
    return shifted


def _write_dataset_npz(
    path: Path,
    rows: List[List[float]],
    targets: List[float],
    metadata: List[Dict[str, object]],
    groups: List[int],
) -> None:
    if not rows:
        return
    X = np.asarray(rows, dtype=np.float32)
    Y = np.asarray(targets, dtype=np.float32)
    group_ids = np.asarray(groups, dtype=np.int64)
    np.savez(
        path,
        X=X,
        Y=Y,
        feature_names=np.asarray(FEATURE_NAMES, dtype=object),
        metadata=np.asarray(metadata, dtype=object),
        group_ids=group_ids,
    )


def _write_progress_snapshot(
    *,
    output_dir: Path,
    dataset_name: str,
    rows: List[List[float]],
    targets: List[float],
    metadata: List[Dict[str, object]],
    groups: List[int],
    target_field: str,
    hardware_inputs: Sequence[Path],
    surrogate_inputs: Sequence[Path],
    hardware_done: int,
    surrogate_done: int,
    current: Optional[Dict[str, object]],
    status: str,
) -> None:
    partial_npz = output_dir / f"{dataset_name}_partial.npz"
    progress_json = output_dir / f"{dataset_name}_progress.json"
    _write_dataset_npz(partial_npz, rows, targets, metadata, groups)
    progress = {
        "status": status,
        "dataset_path": str(partial_npz),
        "n_rows": int(len(rows)),
        "n_features": int(len(FEATURE_NAMES)),
        "n_groups": int(len(set(groups))),
        "feature_names": FEATURE_NAMES,
        "hardware_inputs": [str(path) for path in hardware_inputs],
        "surrogate_inputs": [str(path) for path in surrogate_inputs],
        "hardware_inputs_completed": int(hardware_done),
        "surrogate_inputs_completed": int(surrogate_done),
        "target_field_for_hardware": target_field,
        "current": current,
    }
    progress_json.write_text(json.dumps(progress, indent=2) + "\n")


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    all_rows: List[List[float]] = []
    all_targets: List[float] = []
    all_metadata: List[Dict[str, object]] = []
    all_groups: List[int] = []
    group_offset = 0
    completed_hardware = 0
    completed_surrogates = 0

    for path in args.hardware_json:
        checkpoint_every = max(args.checkpoint_every, 1)

        def _checkpoint_cb(
            local_rows: List[List[float]],
            local_targets: List[float],
            local_metadata: List[Dict[str, object]],
            local_groups: List[int],
            current: Dict[str, object],
        ) -> None:
            rows_done = int(current.get("rows_done", 0))
            rows_total = int(current.get("rows_total", 0))
            if rows_done % checkpoint_every != 0 and rows_done != rows_total:
                return
            shifted_metadata = _shift_metadata_group_ids(local_metadata, group_offset)
            shifted_groups = [int(group) + group_offset for group in local_groups]
            _write_progress_snapshot(
                output_dir=args.output_dir,
                dataset_name=args.dataset_name,
                rows=all_rows + list(local_rows),
                targets=all_targets + list(local_targets),
                metadata=all_metadata + shifted_metadata,
                groups=all_groups + shifted_groups,
                target_field=args.target_field,
                hardware_inputs=args.hardware_json,
                surrogate_inputs=args.surrogate_npz,
                hardware_done=completed_hardware,
                surrogate_done=completed_surrogates,
                current=current,
                status="partial",
            )

        rows, targets, metadata, groups = _hardware_rows(
            path,
            args.target_field,
            progress_every=max(args.progress_every, 1),
            progress_cb=_checkpoint_cb,
        )
        all_rows.extend(rows)
        all_targets.extend(targets)
        shifted_metadata = _shift_metadata_group_ids(metadata, group_offset)
        all_metadata.extend(shifted_metadata)
        all_groups.extend([int(group) + group_offset for group in groups])
        group_offset += len(set(groups))
        completed_hardware += 1
        _write_progress_snapshot(
            output_dir=args.output_dir,
            dataset_name=args.dataset_name,
            rows=all_rows,
            targets=all_targets,
            metadata=all_metadata,
            groups=all_groups,
            target_field=args.target_field,
            hardware_inputs=args.hardware_json,
            surrogate_inputs=args.surrogate_npz,
            hardware_done=completed_hardware,
            surrogate_done=completed_surrogates,
            current={
                "source_kind": "hardware_json",
                "source_path": str(path),
                "rows_done": len(rows),
                "rows_total": len(rows),
            },
            status="partial",
        )

    for path in args.surrogate_npz:
        rows, targets, metadata, groups = _surrogate_rows(path)
        all_rows.extend(rows)
        all_targets.extend(targets)
        shifted_metadata = _shift_metadata_group_ids(metadata, group_offset)
        all_metadata.extend(shifted_metadata)
        all_groups.extend([int(group) + group_offset for group in groups])
        group_offset += len(set(groups))
        completed_surrogates += 1
        _write_progress_snapshot(
            output_dir=args.output_dir,
            dataset_name=args.dataset_name,
            rows=all_rows,
            targets=all_targets,
            metadata=all_metadata,
            groups=all_groups,
            target_field=args.target_field,
            hardware_inputs=args.hardware_json,
            surrogate_inputs=args.surrogate_npz,
            hardware_done=completed_hardware,
            surrogate_done=completed_surrogates,
            current={
                "source_kind": "surrogate_npz",
                "source_path": str(path),
            },
            status="partial",
        )

    if not all_rows:
        raise SystemExit("No input rows found. Provide --hardware-json and/or --surrogate-npz.")

    X = np.asarray(all_rows, dtype=np.float32)
    Y = np.asarray(all_targets, dtype=np.float32)
    group_ids = np.asarray(all_groups, dtype=np.int64)

    out_npz = args.output_dir / f"{args.dataset_name}.npz"
    _write_dataset_npz(out_npz, all_rows, all_targets, all_metadata, all_groups)

    summary = {
        "dataset_path": str(out_npz),
        "n_rows": int(X.shape[0]),
        "n_features": int(X.shape[1]),
        "n_groups": int(len(set(group_ids.tolist()))),
        "feature_names": FEATURE_NAMES,
        "hardware_inputs": [str(path) for path in args.hardware_json],
        "surrogate_inputs": [str(path) for path in args.surrogate_npz],
        "target_field_for_hardware": args.target_field,
    }
    (args.output_dir / f"{args.dataset_name}_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n"
    )
    _write_progress_snapshot(
        output_dir=args.output_dir,
        dataset_name=args.dataset_name,
        rows=all_rows,
        targets=all_targets,
        metadata=all_metadata,
        groups=all_groups,
        target_field=args.target_field,
        hardware_inputs=args.hardware_json,
        surrogate_inputs=args.surrogate_npz,
        hardware_done=completed_hardware,
        surrogate_done=completed_surrogates,
        current=None,
        status="complete",
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
