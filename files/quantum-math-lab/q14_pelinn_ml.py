#!/usr/bin/env python3
"""Build a narrow q14 ML mitigation dataset and train a local PE-LiNN regressor.

This bridges the existing q14 hardware artifacts in this repo to the local
PELINN-Q model checkout without modifying that external checkout.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np
import torch


FEATURE_NAMES = [
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
    "folded_two_qubit_load",
    "extra_error_suppression",
    "source_is_zne",
]


@dataclass
class Sample:
    features: List[float]
    target: float
    circuit_index: int
    metadata: Dict[str, object]


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--overlap-json",
        type=Path,
        default=Path("results/hardware/phase3_q14_overlap_raw_vs_mit_s8000.json"),
    )
    parser.add_argument(
        "--disjoint-json",
        type=Path,
        default=Path("results/hardware/phase3_q14_disjoint_raw_vs_mit_s8000.json"),
    )
    parser.add_argument(
        "--zne-json",
        type=Path,
        default=Path("results/hardware/phase3_q14_zne_xsup_s8000_f135.json"),
    )
    parser.add_argument(
        "--pelinn-model",
        type=Path,
        default=Path("/tmp/pelinnq.G4gAic/repo/src/model.py"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results/hardware/phase3_q14_pelinn"),
    )
    parser.add_argument("--epochs", type=int, default=300)
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--weight-decay", type=float, default=1e-2)
    parser.add_argument("--hid-dim", type=int, default=96)
    parser.add_argument("--steps", type=int, default=6)
    parser.add_argument("--dt", type=float, default=0.25)
    parser.add_argument("--val-fraction", type=float, default=0.25)
    parser.add_argument("--seed", type=int, default=424242)
    parser.add_argument("--alpha-inv", type=float, default=0.10)
    parser.add_argument("--target-mode", choices=("direct", "residual"), default="direct")
    parser.add_argument("--source-filter", choices=("all", "base", "zne"), default="all")
    parser.add_argument("--tanh-head", action="store_true")
    return parser.parse_args(argv)


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def load_json(path: Path) -> Dict[str, object]:
    return json.loads(path.read_text())


def logical_key(depth: int, trial: int, branch: str, seed: int) -> str:
    return f"{branch}|d{depth}|t{trial}|s{seed}"


def base_features(
    *,
    depth: int,
    trial: int,
    perturb_qubit: int,
    raw_value: float,
    mitigated_value: float,
    transpiled_depth: int,
    two_qubit_gate_count: int,
    factor: int,
    extra_error_suppression: bool,
    source_is_zne: bool,
) -> List[float]:
    branch_overlap = 1.0 if perturb_qubit == 0 else 0.0
    perturb_qubit_norm = float(perturb_qubit) / 13.0
    mitigation_gain = mitigated_value - raw_value
    folded_two_qubit_load = float(two_qubit_gate_count) * float(factor)
    return [
        float(depth),
        float(trial),
        branch_overlap,
        perturb_qubit_norm,
        float(raw_value),
        float(mitigated_value),
        float(mitigation_gain),
        float(transpiled_depth),
        float(two_qubit_gate_count),
        float(factor),
        folded_two_qubit_load,
        1.0 if extra_error_suppression else 0.0,
        1.0 if source_is_zne else 0.0,
    ]


def append_base_runs(
    samples: List[Sample],
    circuit_ids: Dict[str, int],
    data: Dict[str, object],
    branch: str,
) -> None:
    perturb_qubit = int(data["config"]["perturb_qubit"])
    extra_error_suppression = bool(data["config"]["extra_error_suppression"])

    for run in data["runs"]:
        key = logical_key(
            depth=int(run["depth"]),
            trial=int(run["trial"]),
            branch=branch,
            seed=int(run["seed"]),
        )
        circuit_index = circuit_ids.setdefault(key, len(circuit_ids))
        raw_value = float(run["raw"]["perturbed_echo"])
        mitigated_value = float(run["readout_mitigated"]["perturbed_echo"])
        features = base_features(
            depth=int(run["depth"]),
            trial=int(run["trial"]),
            perturb_qubit=perturb_qubit,
            raw_value=raw_value,
            mitigated_value=mitigated_value,
            transpiled_depth=int(run["transpiled"]["perturbed"]["depth"]),
            two_qubit_gate_count=int(run["transpiled"]["perturbed"]["two_qubit_gate_count"]),
            factor=1,
            extra_error_suppression=extra_error_suppression,
            source_is_zne=False,
        )
        samples.append(
            Sample(
                features=features,
                target=float(run["exact"]["perturbed_echo"]),
                circuit_index=circuit_index,
                metadata={
                    "source": "base",
                    "branch": branch,
                    "depth": int(run["depth"]),
                    "trial": int(run["trial"]),
                    "seed": int(run["seed"]),
                    "perturb_qubit": perturb_qubit,
                    "factor": 1,
                },
            )
        )


def append_zne_records(
    samples: List[Sample],
    circuit_ids: Dict[str, int],
    data: Dict[str, object],
) -> None:
    extra_error_suppression = bool(data["config"]["extra_error_suppression"])

    for record in data["records"]:
        if record["kind"] != "perturbed":
            continue
        perturb_qubit = int(record["perturb_qubit"])
        branch = "overlap" if perturb_qubit == 0 else "disjoint"
        key = logical_key(
            depth=int(record["depth"]),
            trial=int(record["trial"]),
            branch=branch,
            seed=int(record["seed"]),
        )
        circuit_index = circuit_ids.setdefault(key, len(circuit_ids))
        factor = int(record["factor"])
        raw_value = float(record["raw_value"])
        mitigated_value = float(record["mitigated_value"])
        features = base_features(
            depth=int(record["depth"]),
            trial=int(record["trial"]),
            perturb_qubit=perturb_qubit,
            raw_value=raw_value,
            mitigated_value=mitigated_value,
            transpiled_depth=int(record["transpiled_depth"]),
            two_qubit_gate_count=int(record["two_qubit_gate_count"]),
            factor=factor,
            extra_error_suppression=extra_error_suppression,
            source_is_zne=True,
        )
        samples.append(
            Sample(
                features=features,
                target=float(record["exact_value"]),
                circuit_index=circuit_index,
                metadata={
                    "source": "zne",
                    "branch": branch,
                    "depth": int(record["depth"]),
                    "trial": int(record["trial"]),
                    "seed": int(record["seed"]),
                    "perturb_qubit": perturb_qubit,
                    "factor": factor,
                },
            )
        )


def build_dataset(args: argparse.Namespace) -> Tuple[np.ndarray, np.ndarray, np.ndarray, List[Dict[str, object]]]:
    overlap = load_json(args.overlap_json)
    disjoint = load_json(args.disjoint_json)
    zne = load_json(args.zne_json)

    samples: List[Sample] = []
    circuit_ids: Dict[str, int] = {}
    if args.source_filter in ("all", "base"):
        append_base_runs(samples, circuit_ids, overlap, "overlap")
        append_base_runs(samples, circuit_ids, disjoint, "disjoint")
    if args.source_filter in ("all", "zne"):
        append_zne_records(samples, circuit_ids, zne)

    X = np.asarray([sample.features for sample in samples], dtype=np.float32)
    y = np.asarray([sample.target for sample in samples], dtype=np.float32)
    groups = np.asarray([sample.circuit_index for sample in samples], dtype=np.int64)
    metadata = []
    for sample in samples:
        row = dict(sample.metadata)
        row["circuit_index"] = int(sample.circuit_index)
        metadata.append(row)
    return X, y, groups, metadata


def split_groupwise(circuit_ids: np.ndarray, val_fraction: float, seed: int) -> Tuple[np.ndarray, np.ndarray]:
    unique = np.unique(circuit_ids)
    rng = np.random.default_rng(seed)
    shuffled = unique.copy()
    rng.shuffle(shuffled)
    n_val = int(round(len(shuffled) * val_fraction))
    if len(shuffled) > 1:
        n_val = min(max(n_val, 1), len(shuffled) - 1)
    else:
        n_val = 0
    val_groups = set(int(x) for x in shuffled[:n_val])
    train_idx = np.asarray([i for i, cid in enumerate(circuit_ids) if int(cid) not in val_groups], dtype=np.int64)
    val_idx = np.asarray([i for i, cid in enumerate(circuit_ids) if int(cid) in val_groups], dtype=np.int64)
    return train_idx, val_idx


def normalise_features(X_train: np.ndarray, X_other: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    mean = X_train.mean(axis=0)
    std = X_train.std(axis=0)
    std = np.maximum(std, 1e-6)
    return (X_train - mean) / std, (X_other - mean) / std, mean


def normalise_with_stats(X: np.ndarray, mean: np.ndarray, std: np.ndarray) -> np.ndarray:
    return (X - mean) / std


def group_positions(group_ids: Iterable[int]) -> List[List[int]]:
    grouped: Dict[int, List[int]] = {}
    for pos, group_id in enumerate(group_ids):
        grouped.setdefault(int(group_id), []).append(pos)
    return list(grouped.values())


def load_pelinn(model_path: Path):
    spec = importlib.util.spec_from_file_location("pelinn_bridge_model", model_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load PELINN model from {model_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.PELiNNQEM, module.physics_loss


def regression_metrics(pred: np.ndarray, true: np.ndarray) -> Dict[str, float]:
    diff = pred - true
    return {
        "mae": float(np.mean(np.abs(diff))),
        "rmse": float(np.sqrt(np.mean(diff**2))),
    }


def train_model(
    *,
    X_train: np.ndarray,
    y_train: np.ndarray,
    groups_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    pelinn_model_path: Path,
    hid_dim: int,
    steps: int,
    dt: float,
    tanh_head: bool,
    epochs: int,
    lr: float,
    weight_decay: float,
    alpha_inv: float,
) -> Tuple[torch.nn.Module, Dict[str, object]]:
    PELiNNQEM, physics_loss = load_pelinn(pelinn_model_path)
    device = torch.device("cpu")
    model = PELiNNQEM(
        in_dim=X_train.shape[1],
        hid_dim=hid_dim,
        steps=steps,
        dt=dt,
        use_tanh_head=tanh_head,
    ).to(device)
    optimiser = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)

    X_train_t = torch.from_numpy(X_train).to(device)
    y_train_t = torch.from_numpy(y_train).to(device)
    train_groups = group_positions(groups_train.tolist())

    X_val_t = torch.from_numpy(X_val).to(device) if len(X_val) else None
    best_state = None
    best_metric = math.inf
    history: List[Dict[str, float]] = []

    for epoch in range(1, epochs + 1):
        model.train()
        pred = model(X_train_t)
        loss = physics_loss(
            pred,
            y_train_t,
            groups=train_groups,
            alpha_inv=alpha_inv,
            reg_gate=model.last_gate_reg,
            reg_A=model.last_A_reg,
        )
        optimiser.zero_grad()
        loss.backward()
        optimiser.step()

        epoch_info: Dict[str, float] = {"epoch": float(epoch), "train_loss": float(loss.detach().cpu())}

        if X_val_t is not None and len(X_val):
            model.eval()
            with torch.no_grad():
                val_pred = model(X_val_t).cpu().numpy()
            val_metrics = regression_metrics(val_pred, y_val)
            epoch_info["val_mae"] = val_metrics["mae"]
            epoch_info["val_rmse"] = val_metrics["rmse"]
            if val_metrics["rmse"] < best_metric:
                best_metric = val_metrics["rmse"]
                best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
        history.append(epoch_info)

    if best_state is not None:
        model.load_state_dict(best_state)

    return model, {"history": history}


def predict(model: torch.nn.Module, X: np.ndarray) -> np.ndarray:
    model.eval()
    with torch.no_grad():
        return model(torch.from_numpy(X)).cpu().numpy().astype(np.float64)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    set_seed(args.seed)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    X, y, groups, metadata = build_dataset(args)
    baseline_all = X[:, FEATURE_NAMES.index("mitigated_perturbed_echo")].astype(np.float64)
    if args.target_mode == "residual":
        y_train_target_full = y.astype(np.float64) - baseline_all
    else:
        y_train_target_full = y.astype(np.float64)
    train_idx, val_idx = split_groupwise(groups, args.val_fraction, args.seed)

    X_train_raw = X[train_idx]
    X_val_raw = X[val_idx]
    y_train = y_train_target_full[train_idx].astype(np.float32)
    y_val = y_train_target_full[val_idx].astype(np.float32)
    y_exact_train = y[train_idx].astype(np.float64)
    y_exact_val = y[val_idx].astype(np.float64)
    groups_train = groups[train_idx]

    train_std = np.maximum(X_train_raw.std(axis=0), 1e-6)
    X_train, X_val, train_mean = normalise_features(X_train_raw, X_val_raw)

    model, training = train_model(
        X_train=X_train,
        y_train=y_train,
        groups_train=groups_train,
        X_val=X_val,
        y_val=y_val,
        pelinn_model_path=args.pelinn_model,
        hid_dim=args.hid_dim,
        steps=args.steps,
        dt=args.dt,
        tanh_head=args.tanh_head,
        epochs=args.epochs,
        lr=args.lr,
        weight_decay=args.weight_decay,
        alpha_inv=args.alpha_inv,
    )

    model_output = predict(model, normalise_with_stats(X, train_mean, train_std))
    if args.target_mode == "residual":
        all_pred = baseline_all + model_output
    else:
        all_pred = model_output
    train_pred = all_pred[train_idx]
    val_pred = all_pred[val_idx]
    baseline_train = baseline_all[train_idx]
    baseline_val = baseline_all[val_idx]

    summary = {
        "feature_names": FEATURE_NAMES,
        "dataset": {
            "samples": int(len(X)),
            "train_samples": int(len(train_idx)),
            "val_samples": int(len(val_idx)),
            "unique_circuits": int(len(np.unique(groups))),
            "train_unique_circuits": int(len(np.unique(groups[train_idx]))),
            "val_unique_circuits": int(len(np.unique(groups[val_idx]))),
        },
        "metrics": {
            "train_model": regression_metrics(train_pred, y_exact_train),
            "train_baseline_mitigated": regression_metrics(baseline_train, y_exact_train),
            "val_model": regression_metrics(val_pred, y_exact_val) if len(val_idx) else {},
            "val_baseline_mitigated": regression_metrics(baseline_val, y_exact_val) if len(val_idx) else {},
        },
        "training": training,
        "config": {
            "epochs": int(args.epochs),
            "lr": float(args.lr),
            "weight_decay": float(args.weight_decay),
            "hid_dim": int(args.hid_dim),
            "steps": int(args.steps),
            "dt": float(args.dt),
            "alpha_inv": float(args.alpha_inv),
            "seed": int(args.seed),
            "tanh_head": bool(args.tanh_head),
            "target_mode": str(args.target_mode),
            "source_filter": str(args.source_filter),
            "pelinn_model": str(args.pelinn_model),
        },
    }

    np.savez(
        args.output_dir / "q14_pelinn_dataset.npz",
        X=X,
        Y=y_train_target_full.astype(np.float32),
        Y_exact=y.astype(np.float32),
        circuit_ids=groups,
        metadata=np.asarray(metadata, dtype=object),
        feature_names=np.asarray(FEATURE_NAMES, dtype=object),
    )
    torch.save(
        {
            "state_dict": model.state_dict(),
            "feature_names": FEATURE_NAMES,
            "feature_mean": train_mean,
            "feature_std": train_std,
        },
        args.output_dir / "q14_pelinn_model.pt",
    )
    (args.output_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    predictions = []
    for idx, row in enumerate(metadata):
        item = dict(row)
        item["target_exact"] = float(y[idx])
        item["training_target"] = float(y_train_target_full[idx])
        item["baseline_mitigated"] = float(baseline_all[idx])
        item["ml_prediction"] = float(all_pred[idx])
        item["ml_model_output"] = float(model_output[idx])
        predictions.append(item)
    (args.output_dir / "predictions.json").write_text(json.dumps(predictions, indent=2))

    print(
        json.dumps(
            {
                "output_dir": str(args.output_dir),
                "dataset_samples": int(len(X)),
                "train_samples": int(len(train_idx)),
                "val_samples": int(len(val_idx)),
                "val_model": summary["metrics"]["val_model"],
                "val_baseline_mitigated": summary["metrics"]["val_baseline_mitigated"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
