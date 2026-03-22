#!/usr/bin/env python3
"""Generate a q14/q20/q24/q32/q80 signal-above-noise summary plot."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
HARDWARE = ROOT / "results" / "hardware"
OUT_DIR = HARDWARE / "summary"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def subset_branch_values(path: Path):
    data = load_json(path)
    values = {}
    for row in data["summary_by_depth"]:
        depth = int(row["depth"])
        values[depth] = {
            "mean": float(row["readout_mitigated"]["perturbed_subset_echo"]["mean"]),
            "std": float(row["readout_mitigated"]["perturbed_subset_echo"]["std"]),
        }
    return values


def main() -> int:
    q20_q0 = subset_branch_values(HARDWARE / "phase3_q20_SA_q0_raw_vs_mit.json")
    q20_q19 = subset_branch_values(HARDWARE / "phase3_q20_SA_q19_raw_vs_mit.json")
    q24_q0 = subset_branch_values(HARDWARE / "phase3_q24_SA_q0_raw_vs_mit.json")
    q24_q23 = subset_branch_values(HARDWARE / "phase3_q24_SA_q23_raw_vs_mit.json")
    q32_q0 = subset_branch_values(HARDWARE / "phase3_q32_SA_q0_raw_vs_mit.json")
    q32_q31 = subset_branch_values(HARDWARE / "phase3_q32_SA_q31_raw_vs_mit.json")
    q80_q0 = subset_branch_values(HARDWARE / "phase3_q80pilot_SA_q0_raw_vs_mit.json")
    q80_q79 = subset_branch_values(HARDWARE / "phase3_q80pilot_SA_q79_raw_vs_mit.json")

    q14_zne = load_json(HARDWARE / "phase3_q14_zne_xsup_s8000_f135_localfold.json")
    q14_branch_map = {}
    for entry in q14_zne["summaries"]:
        depth = int(entry["depth"])
        perturb_qubit = int(entry["perturb_qubit"])
        q14_branch_map[(depth, perturb_qubit)] = entry
    q14_gap = {}
    for depth in sorted({d for d, _ in q14_branch_map}):
        overlap_entry = q14_branch_map[(depth, 0)]
        disjoint_entry = q14_branch_map[(depth, 10)]
        overlap = float(overlap_entry["zne"]["perturbed_echo"]["recommended_extrapolated"])
        disjoint = float(disjoint_entry["zne"]["perturbed_echo"]["recommended_extrapolated"])
        q14_gap[depth] = {
            "overlap_minus_disjoint": overlap - disjoint,
            "overlap": overlap,
            "disjoint": disjoint,
        }

    q80_fullreg = load_json(
        HARDWARE
        / "bonus_full_q80_2026-03-21"
        / "depth2_paired_blockz_reuse"
        / "full_q80_q0_q79_paired_t5_blockz_front10_back10.json"
    )
    block_cmp = q80_fullreg["summary_by_depth"][0]["paired_branch_comparison"]["comparisons"][0][
        "z_observable_blocks"
    ]["readout_mitigated"]
    front10_median = abs(float(block_cmp["front10"]["relative_linear_return_delta"]["median"]))
    back10_median = abs(float(block_cmp["back10"]["relative_linear_return_delta"]["median"]))
    symmetric_block_marker = 0.5 * (front10_median + back10_median)

    series = {
        "subset_depth1": {
            20: q20_q19[1]["mean"] - q20_q0[1]["mean"],
            24: q24_q23[1]["mean"] - q24_q0[1]["mean"],
            32: q32_q31[1]["mean"] - q32_q0[1]["mean"],
            80: q80_q79[1]["mean"] - q80_q0[1]["mean"],
        },
        "subset_depth2": {
            20: q20_q19[2]["mean"] - q20_q0[2]["mean"],
            24: q24_q23[2]["mean"] - q24_q0[2]["mean"],
            32: q32_q31[2]["mean"] - q32_q0[2]["mean"],
            80: q80_q79[2]["mean"] - q80_q0[2]["mean"],
        },
        "q14_checkpoint_zne_d2": {
            14: q14_gap[2]["overlap_minus_disjoint"],
        },
        "q80_full_register_blockz_d2": {
            80: symmetric_block_marker,
        },
    }

    payload = {
        "metric_definition": {
            "subset_depth1_depth2": (
                "readout-mitigated shallow subset-proxy contrast = "
                "far-disjoint perturbed_subset_echo minus overlap perturbed_subset_echo"
            ),
            "q14_checkpoint_zne_d2": (
                "corrected local-fold checkpoint ZNE overlap minus disjoint on q14 at depth 2"
            ),
            "q80_full_register_blockz_d2": (
                "symmetric mean absolute paired block-Z linear-return delta across "
                "front10 and back10 on the exploratory full-register bonus track at depth 2"
            ),
        },
        "data": {
            "q14_checkpoint_zne_d2": q14_gap,
            "q20_subset_SA_seeded": {
                "source_files": [
                    "results/hardware/phase3_q20_SA_q0_raw_vs_mit.json",
                    "results/hardware/phase3_q20_SA_q19_raw_vs_mit.json",
                ],
                "depth1_overlap": q20_q0[1],
                "depth1_far": q20_q19[1],
                "depth1_delta": q20_q19[1]["mean"] - q20_q0[1]["mean"],
                "depth2_overlap": q20_q0[2],
                "depth2_far": q20_q19[2],
                "depth2_delta": q20_q19[2]["mean"] - q20_q0[2]["mean"],
            },
            "q24_subset_SA": {
                "depth1_overlap": q24_q0[1],
                "depth1_far": q24_q23[1],
                "depth1_delta": q24_q23[1]["mean"] - q24_q0[1]["mean"],
                "depth2_overlap": q24_q0[2],
                "depth2_far": q24_q23[2],
                "depth2_delta": q24_q23[2]["mean"] - q24_q0[2]["mean"],
            },
            "q32_subset_SA": {
                "depth1_overlap": q32_q0[1],
                "depth1_far": q32_q31[1],
                "depth1_delta": q32_q31[1]["mean"] - q32_q0[1]["mean"],
                "depth2_overlap": q32_q0[2],
                "depth2_far": q32_q31[2],
                "depth2_delta": q32_q31[2]["mean"] - q32_q0[2]["mean"],
            },
            "q80_subset_SA_pilot": {
                "depth1_overlap": q80_q0[1],
                "depth1_far": q80_q79[1],
                "depth1_delta": q80_q79[1]["mean"] - q80_q0[1]["mean"],
                "depth2_overlap": q80_q0[2],
                "depth2_far": q80_q79[2],
                "depth2_delta": q80_q79[2]["mean"] - q80_q0[2]["mean"],
            },
            "q80_full_register_bonus_blockz": {
                "front10_relative_linear_return_delta": block_cmp["front10"]["relative_linear_return_delta"],
                "back10_relative_linear_return_delta": block_cmp["back10"]["relative_linear_return_delta"],
                "full_register_signal_marker": symmetric_block_marker,
                "full_register_signal_marker_definition": (
                    "0.5 * (abs(front10 median delta) + abs(back10 median delta))"
                ),
            },
        },
    }

    json_path = OUT_DIR / "signal_above_noise_scale_plot_2026-03-21.json"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    fig, ax = plt.subplots(figsize=(9, 5.5))
    xs1 = sorted(series["subset_depth1"])
    ys1 = [series["subset_depth1"][x] for x in xs1]
    xs2 = sorted(series["subset_depth2"])
    ys2 = [series["subset_depth2"][x] for x in xs2]

    ax.plot(xs1, ys1, marker="o", linewidth=2.2, color="#1f77b4", label="Subset-proxy delta d=1")
    ax.plot(xs2, ys2, marker="s", linewidth=2.2, color="#d62728", label="Subset-proxy delta d=2")
    ax.scatter(
        [14],
        [series["q14_checkpoint_zne_d2"][14]],
        marker="^",
        s=110,
        color="#2ca02c",
        label="q14 checkpoint ZNE d=2",
    )
    ax.scatter(
        [80],
        [series["q80_full_register_blockz_d2"][80]],
        marker="D",
        s=90,
        color="#9467bd",
        label="80q full-register bonus block-Z",
    )

    for x, y in zip(xs1, ys1):
        ax.annotate(
            f"{y:.3f}",
            (x, y),
            textcoords="offset points",
            xytext=(0, 8),
            ha="center",
            fontsize=8,
            color="#1f77b4",
        )
    for x, y in zip(xs2, ys2):
        ax.annotate(
            f"{y:.3f}",
            (x, y),
            textcoords="offset points",
            xytext=(0, -14),
            ha="center",
            fontsize=8,
            color="#d62728",
        )

    ax.annotate(
        f"{series['q14_checkpoint_zne_d2'][14]:.3f}",
        (14, series["q14_checkpoint_zne_d2"][14]),
        textcoords="offset points",
        xytext=(0, 8),
        ha="center",
        fontsize=8,
        color="#2ca02c",
    )
    ax.annotate(
        f"{series['q80_full_register_blockz_d2'][80]:.3f}",
        (80, series["q80_full_register_blockz_d2"][80]),
        textcoords="offset points",
        xytext=(12, 10),
        ha="left",
        fontsize=8,
        color="#9467bd",
    )

    ax.set_title("Signal Above Pure Noise Across q14/q20/q24/q32/q80")
    ax.set_xlabel("Qubits")
    ax.set_ylabel("Signal magnitude / delta")
    ax.set_xticks([14, 20, 24, 32, 80])
    ax.set_ylim(0, 1.08)
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False, fontsize=9, loc="upper right")
    fig.tight_layout()

    png_path = OUT_DIR / "signal_above_noise_scale_plot_2026-03-21.png"
    fig.savefig(png_path, dpi=180)
    plt.close(fig)

    print(json_path)
    print(png_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
