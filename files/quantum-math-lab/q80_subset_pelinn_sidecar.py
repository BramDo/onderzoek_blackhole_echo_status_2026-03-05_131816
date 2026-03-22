#!/usr/bin/env python3
"""Train a diagnostic PE-LiNN sidecar on q80-subset-shaped surrogate data."""

from __future__ import annotations

import argparse
import importlib.util
import json
import random
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np
import torch


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path(
            "results/hardware/phase3_q80_subset_pelinn_surrogate_s16_ckpt/"
            "q80_subset_surrogate_dataset.npz"
        ),
    )
    parser.add_argument(
        "--pelinn-model",
        type=Path,
        default=Path("/tmp/pelinnq.G4gAic/repo/src/model.py"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results/hardware/phase3_q80_subset_pelinn_sidecar_s16"),
    )
    parser.add_argument("--epochs", type=int, default=400)
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--weight-decay", type=float, default=1e-2)
    parser.add_argument("--hid-dim", type=int, default=64)
    parser.add_argument("--steps", type=int, default=6)
    parser.add_argument("--dt", type=float, default=0.25)
    parser.add_argument("--val-fraction", type=float, default=0.25)
    parser.add_argument("--seed", type=int, default=424242)
    parser.add_argument("--alpha-inv", type=float, default=0.10)
    parser.add_argument("--target-mode", choices=("residual", "direct"), default="residual")
    parser.add_argument("--loss-type", choices=("mse", "huber"), default="huber")
    parser.add_argument("--tanh-head", action="store_true")
    return parser.parse_args(argv)


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def load_pelinn_model_class(path: Path):
    spec = importlib.util.spec_from_file_location("pelinn_q_model", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load PE-LiNN model from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.PELiNNQEM


def load_dataset(
    path: Path,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, List[Dict[str, object]], List[str]]:
    data = np.load(path, allow_pickle=True)
    X = np.asarray(data["X"], dtype=np.float32)
    y = np.asarray(data["Y"], dtype=np.float32)
    metadata = [dict(row) for row in data["metadata"].tolist()]
    feature_names = [str(name) for name in data["feature_names"].tolist()]
    return X, y, metadata, feature_names


def split_groupwise(
    groups: np.ndarray, val_fraction: float, seed: int
) -> Tuple[np.ndarray, np.ndarray]:
    unique_groups = sorted({int(group) for group in groups.tolist()})
    if len(unique_groups) < 2:
        raise ValueError("Need at least two circuit groups for a sidecar validation split.")

    rng = random.Random(seed)
    rng.shuffle(unique_groups)
    n_val = max(1, int(round(len(unique_groups) * val_fraction)))
    n_val = min(n_val, len(unique_groups) - 1)
    val_groups = set(unique_groups[:n_val])
    val_mask = np.asarray([int(group) in val_groups for group in groups], dtype=bool)
    train_mask = ~val_mask
    return train_mask, val_mask


def standardize_from_train(
    X: np.ndarray, train_mask: np.ndarray
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    mean = X[train_mask].mean(axis=0)
    std = X[train_mask].std(axis=0)
    std = np.where(std < 1e-6, 1.0, std)
    X_scaled = (X - mean) / std
    return X_scaled.astype(np.float32), mean.astype(np.float32), std.astype(np.float32)


def build_group_lists(groups: np.ndarray) -> List[List[int]]:
    index_map: Dict[int, List[int]] = {}
    for idx, group in enumerate(groups.tolist()):
        index_map.setdefault(int(group), []).append(idx)
    return list(index_map.values())


def mae_rmse(pred: np.ndarray, target: np.ndarray) -> Dict[str, float]:
    err = pred - target
    return {
        "mae": float(np.mean(np.abs(err))),
        "rmse": float(np.sqrt(np.mean(np.square(err)))),
    }


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    set_seed(args.seed)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    X, y_exact, metadata, feature_names = load_dataset(args.dataset)
    mitigated_idx = feature_names.index("mitigated_subset_perturbed_echo")
    baseline = X[:, mitigated_idx].astype(np.float32)
    groups = np.asarray([int(row["circuit_index"]) for row in metadata], dtype=np.int64)
    train_mask, val_mask = split_groupwise(groups, args.val_fraction, args.seed)
    X_scaled, x_mean, x_std = standardize_from_train(X, train_mask)

    PELiNNQEM = load_pelinn_model_class(args.pelinn_model)
    model = PELiNNQEM(
        in_dim=X.shape[1],
        hid_dim=args.hid_dim,
        steps=args.steps,
        dt=args.dt,
        use_tanh_head=args.tanh_head,
    )
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=args.lr, weight_decay=args.weight_decay
    )

    X_train = torch.tensor(X_scaled[train_mask], dtype=torch.float32)
    X_val = torch.tensor(X_scaled[val_mask], dtype=torch.float32)
    y_train = torch.tensor(y_exact[train_mask], dtype=torch.float32)
    y_val = torch.tensor(y_exact[val_mask], dtype=torch.float32)
    baseline_train = torch.tensor(baseline[train_mask], dtype=torch.float32)
    baseline_val = torch.tensor(baseline[val_mask], dtype=torch.float32)
    train_groups = build_group_lists(groups[train_mask])

    best_val_rmse = float("inf")
    best_state = None
    best_epoch = 0

    for epoch in range(1, args.epochs + 1):
        model.train()
        optimizer.zero_grad()
        train_raw = model(X_train)
        train_pred = train_raw + baseline_train if args.target_mode == "residual" else train_raw
        train_loss = model.compute_loss(
            train_pred,
            y_train,
            groups=train_groups,
            alpha_inv=args.alpha_inv,
            loss_type=args.loss_type,
        )
        train_loss.backward()
        optimizer.step()

        model.eval()
        with torch.no_grad():
            val_raw = model(X_val)
            val_pred = val_raw + baseline_val if args.target_mode == "residual" else val_raw
            val_rmse = float(
                torch.sqrt(torch.mean(torch.square(val_pred - y_val))).cpu().item()
            )
        if val_rmse < best_val_rmse:
            best_val_rmse = val_rmse
            best_epoch = epoch
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}

    if best_state is None:
        raise RuntimeError("Training failed to produce a best validation checkpoint.")

    model.load_state_dict(best_state)
    model.eval()
    with torch.no_grad():
        all_raw = model(torch.tensor(X_scaled, dtype=torch.float32)).cpu().numpy()
    final_pred = all_raw + baseline if args.target_mode == "residual" else all_raw

    train_metrics = mae_rmse(final_pred[train_mask], y_exact[train_mask])
    val_metrics = mae_rmse(final_pred[val_mask], y_exact[val_mask])
    baseline_train_metrics = mae_rmse(baseline[train_mask], y_exact[train_mask])
    baseline_val_metrics = mae_rmse(baseline[val_mask], y_exact[val_mask])

    torch.save(
        {
            "state_dict": model.state_dict(),
            "feature_names": feature_names,
            "x_mean": x_mean,
            "x_std": x_std,
            "target_mode": args.target_mode,
            "hid_dim": args.hid_dim,
            "steps": args.steps,
            "dt": args.dt,
            "use_tanh_head": bool(args.tanh_head),
        },
        args.output_dir / "q80_subset_pelinn_sidecar.pt",
    )

    predictions = []
    for idx, row in enumerate(metadata):
        payload = dict(row)
        payload.update(
            {
                "split": "train" if bool(train_mask[idx]) else "val",
                "target_exact": float(y_exact[idx]),
                "baseline_mitigated": float(baseline[idx]),
                "sidecar_prediction": float(final_pred[idx]),
                "sidecar_delta_vs_baseline": float(final_pred[idx] - baseline[idx]),
                "abs_error_sidecar": float(abs(final_pred[idx] - y_exact[idx])),
                "abs_error_baseline": float(abs(baseline[idx] - y_exact[idx])),
            }
        )
        predictions.append(payload)

    summary = {
        "dataset": str(args.dataset),
        "feature_names": feature_names,
        "target_mode": args.target_mode,
        "best_epoch": best_epoch,
        "epochs": args.epochs,
        "train_samples": int(train_mask.sum()),
        "val_samples": int(val_mask.sum()),
        "unique_logical_circuits": int(len(set(groups.tolist()))),
        "train_metrics_sidecar": train_metrics,
        "val_metrics_sidecar": val_metrics,
        "train_metrics_baseline": baseline_train_metrics,
        "val_metrics_baseline": baseline_val_metrics,
        "val_improvement_over_baseline": {
            "mae": float(baseline_val_metrics["mae"] - val_metrics["mae"]),
            "rmse": float(baseline_val_metrics["rmse"] - val_metrics["rmse"]),
        },
    }

    (args.output_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (args.output_dir / "predictions.json").write_text(json.dumps(predictions, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
