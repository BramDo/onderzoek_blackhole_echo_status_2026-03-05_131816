#!/usr/bin/env python3
"""Train a small repo-local subset-ML stack on canonical NPZ datasets.

This script is a practical starter stack for follow-on ML-QEM work.
It trains:
1. a conservative ridge / vnCDR-like baseline
2. a small MLP sidecar

It does not implement IBM ML-QEM directly. It gives the repo a stable
groupwise training and evaluation path before a fuller external ML-QEM
integration is added.
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import torch


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset",
        type=Path,
        required=True,
        help="Canonical NPZ dataset produced by ml_qem_build_dataset.py.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results/hardware/ml_qem_training"),
    )
    parser.add_argument("--val-fraction", type=float, default=0.25)
    parser.add_argument("--seed", type=int, default=424242)
    parser.add_argument("--ridge-alpha", type=float, default=1.0)
    parser.add_argument("--epochs", type=int, default=400)
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--weight-decay", type=float, default=1e-2)
    parser.add_argument("--hidden-dim", type=int, default=64)
    parser.add_argument(
        "--baseline-feature",
        type=str,
        default="mitigated_perturbed_echo",
    )
    return parser.parse_args(argv)


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def load_dataset(
    path: Path,
) -> Tuple[np.ndarray, np.ndarray, List[str], List[Dict[str, object]], np.ndarray]:
    data = np.load(path, allow_pickle=True)
    X = np.asarray(data["X"], dtype=np.float32)
    Y = np.asarray(data["Y"], dtype=np.float32)
    feature_names = [str(name) for name in data["feature_names"].tolist()]
    metadata = [dict(row) for row in data["metadata"].tolist()]
    if "group_ids" in data:
        group_ids = np.asarray(data["group_ids"], dtype=np.int64)
    else:
        group_ids = np.asarray(
            [int(row.get("group_id", idx)) for idx, row in enumerate(metadata)],
            dtype=np.int64,
        )
    return X, Y, feature_names, metadata, group_ids


def split_groupwise(group_ids: np.ndarray, val_fraction: float, seed: int) -> Tuple[np.ndarray, np.ndarray]:
    unique_groups = sorted({int(group) for group in group_ids.tolist()})
    if len(unique_groups) < 2:
        raise ValueError("Need at least two groups for validation.")
    rng = random.Random(seed)
    rng.shuffle(unique_groups)
    n_val = max(1, int(round(len(unique_groups) * val_fraction)))
    n_val = min(n_val, len(unique_groups) - 1)
    val_groups = set(unique_groups[:n_val])
    val_mask = np.asarray([int(group) in val_groups for group in group_ids], dtype=bool)
    train_mask = ~val_mask
    return train_mask, val_mask


def standardize_from_train(X: np.ndarray, train_mask: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    mean = X[train_mask].mean(axis=0)
    std = X[train_mask].std(axis=0)
    std = np.where(std < 1e-6, 1.0, std)
    X_scaled = (X - mean) / std
    return X_scaled.astype(np.float32), mean.astype(np.float32), std.astype(np.float32)


def mae_rmse(pred: np.ndarray, target: np.ndarray) -> Dict[str, float]:
    err = pred - target
    return {
        "mae": float(np.mean(np.abs(err))),
        "rmse": float(np.sqrt(np.mean(np.square(err)))),
    }


def fit_ridge(X: np.ndarray, y: np.ndarray, alpha: float) -> Tuple[np.ndarray, float]:
    n_features = X.shape[1]
    xtx = X.T @ X
    reg = alpha * np.eye(n_features, dtype=np.float32)
    xtx_reg = xtx + reg
    xty = X.T @ y
    weights = np.linalg.solve(xtx_reg, xty)
    bias = float(y.mean() - X.mean(axis=0) @ weights)
    return weights.astype(np.float32), bias


class MLPRegressor(torch.nn.Module):
    def __init__(self, in_dim: int, hidden_dim: int) -> None:
        super().__init__()
        self.net = torch.nn.Sequential(
            torch.nn.Linear(in_dim, hidden_dim),
            torch.nn.ReLU(),
            torch.nn.Linear(hidden_dim, hidden_dim),
            torch.nn.ReLU(),
            torch.nn.Linear(hidden_dim, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x).squeeze(-1)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    set_seed(args.seed)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    X, Y, feature_names, metadata, group_ids = load_dataset(args.dataset)
    if args.baseline_feature not in feature_names:
        raise SystemExit(f"Baseline feature '{args.baseline_feature}' not present in dataset.")
    baseline_idx = feature_names.index(args.baseline_feature)
    baseline = X[:, baseline_idx].astype(np.float32)

    train_mask, val_mask = split_groupwise(group_ids, args.val_fraction, args.seed)
    X_scaled, x_mean, x_std = standardize_from_train(X, train_mask)

    # Ridge / vnCDR-like baseline
    ridge_w, ridge_b = fit_ridge(X_scaled[train_mask], Y[train_mask], args.ridge_alpha)
    ridge_pred = (X_scaled @ ridge_w) + ridge_b

    # Small MLP sidecar
    model = MLPRegressor(in_dim=X.shape[1], hidden_dim=args.hidden_dim)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    X_train = torch.tensor(X_scaled[train_mask], dtype=torch.float32)
    y_train = torch.tensor(Y[train_mask], dtype=torch.float32)
    X_val = torch.tensor(X_scaled[val_mask], dtype=torch.float32)
    y_val = torch.tensor(Y[val_mask], dtype=torch.float32)

    best_state = None
    best_epoch = 0
    best_val_rmse = float("inf")

    for epoch in range(1, args.epochs + 1):
        model.train()
        optimizer.zero_grad()
        pred = model(X_train)
        loss = torch.nn.functional.mse_loss(pred, y_train)
        loss.backward()
        optimizer.step()

        model.eval()
        with torch.no_grad():
            val_pred = model(X_val)
            val_rmse = float(torch.sqrt(torch.mean(torch.square(val_pred - y_val))).cpu().item())
        if val_rmse < best_val_rmse:
            best_val_rmse = val_rmse
            best_epoch = epoch
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}

    if best_state is None:
        raise RuntimeError("MLP training failed to produce a checkpoint.")
    model.load_state_dict(best_state)
    model.eval()
    with torch.no_grad():
        mlp_pred = model(torch.tensor(X_scaled, dtype=torch.float32)).cpu().numpy()

    summary = {
        "dataset": str(args.dataset),
        "feature_names": feature_names,
        "baseline_feature": args.baseline_feature,
        "train_samples": int(train_mask.sum()),
        "val_samples": int(val_mask.sum()),
        "unique_groups": int(len(set(group_ids.tolist()))),
        "best_epoch_mlp": best_epoch,
        "metrics": {
            "baseline_train": mae_rmse(baseline[train_mask], Y[train_mask]),
            "baseline_val": mae_rmse(baseline[val_mask], Y[val_mask]),
            "ridge_like_train": mae_rmse(ridge_pred[train_mask], Y[train_mask]),
            "ridge_like_val": mae_rmse(ridge_pred[val_mask], Y[val_mask]),
            "mlp_train": mae_rmse(mlp_pred[train_mask], Y[train_mask]),
            "mlp_val": mae_rmse(mlp_pred[val_mask], Y[val_mask]),
        },
    }

    predictions = []
    for idx, row in enumerate(metadata):
        payload = dict(row)
        payload.update(
            {
                "split": "train" if bool(train_mask[idx]) else "val",
                "target": float(Y[idx]),
                "baseline_prediction": float(baseline[idx]),
                "ridge_like_prediction": float(ridge_pred[idx]),
                "mlp_prediction": float(mlp_pred[idx]),
            }
        )
        predictions.append(payload)

    np.savez(
        args.output_dir / "model_artifacts.npz",
        ridge_weights=ridge_w.astype(np.float32),
        ridge_bias=np.asarray([ridge_b], dtype=np.float32),
        x_mean=x_mean,
        x_std=x_std,
        feature_names=np.asarray(feature_names, dtype=object),
    )
    torch.save(
        {
            "state_dict": model.state_dict(),
            "hidden_dim": args.hidden_dim,
            "feature_names": feature_names,
            "x_mean": x_mean,
            "x_std": x_std,
        },
        args.output_dir / "mlp_sidecar.pt",
    )
    (args.output_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (args.output_dir / "predictions.json").write_text(json.dumps(predictions, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
