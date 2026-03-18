#!/usr/bin/env python3
"""Generate the Phase 2 q14 OLE versus perturbed_echo benchmark report."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OLE_JSON = REPO_ROOT / "files/quantum-math-lab/results/ole/black_hole_ole_q14_exact_small_delta.json"
DEFAULT_BASELINE_JSON = (
    REPO_ROOT / "files/quantum-math-lab/results/benchmark/classical/black_hole_scrambling_q14_exact_short.json"
)
DEFAULT_MANIFEST_JSON = REPO_ROOT / "files/quantum-math-lab/benchmarks/q14_only_manifest.json"
DEFAULT_REPORT_MD = REPO_ROOT / "files/quantum-math-lab/results/ole/q14_ole_vs_delta2_benchmark.md"
DEFAULT_REPORT_CSV = REPO_ROOT / "files/quantum-math-lab/results/ole/q14_ole_vs_delta2_benchmark.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ole-json", type=Path, default=DEFAULT_OLE_JSON)
    parser.add_argument("--baseline-json", type=Path, default=DEFAULT_BASELINE_JSON)
    parser.add_argument("--manifest-json", type=Path, default=DEFAULT_MANIFEST_JSON)
    parser.add_argument("--report-md", type=Path, default=DEFAULT_REPORT_MD)
    parser.add_argument("--report-csv", type=Path, default=DEFAULT_REPORT_CSV)
    return parser.parse_args()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def check_equal(label: str, lhs, rhs) -> None:
    if lhs != rhs:
        raise ValueError(f"{label} mismatch: {lhs!r} != {rhs!r}")


def validate_inputs(ole_data: dict, baseline_data: dict, manifest_data: dict) -> None:
    ole_config = ole_data["config"]
    baseline_config = baseline_data["config"]
    manifest_fixed = manifest_data["fixed_parameters"]

    check_equal("qubits", ole_config["qubits"], baseline_config["qubits"])
    check_equal("trials", ole_config["trials"], baseline_config["trials"])
    check_equal("depths", ole_config["depths"], baseline_config["depths"])
    check_equal("seed", ole_config["seed"], baseline_config["seed"])

    check_equal("manifest qubits", ole_config["qubits"], manifest_fixed["qubits"])
    check_equal("manifest depths", ole_config["depths"], manifest_fixed["depths"])
    check_equal("manifest trials", ole_config["trials"], manifest_fixed["trials_per_day"])
    check_equal("manifest seed", ole_config["seed"], manifest_fixed["seed"])


def build_csv_rows(ole_data: dict, baseline_data: dict) -> list[dict[str, object]]:
    delta_grid = ole_data["config"]["delta_grid"]
    delta_squared_grid = ole_data["config"]["delta_squared_grid"]
    baseline_by_depth = {row["depth"]: row for row in baseline_data["results"]}
    rows: list[dict[str, object]] = []

    for depth_entry in ole_data["results"]:
        depth = depth_entry["depth"]
        baseline_entry = baseline_by_depth[depth]
        operator_stats = depth_entry["operator_stats"]

        rows.append(
            {
                "row_kind": "baseline",
                "depth": depth,
                "branch": "perturbed_echo",
                "generator_label": "full local X kick in the state-return workflow",
                "delta": "",
                "delta_sq": "",
                "F_delta_mean": "",
                "F_delta_std": "",
                "f_delta_mean": "",
                "f_delta_std": "",
                "w_anti_mean": "",
                "w_anti_std": "",
                "kappa_mean": "",
                "kappa_std": "",
                "term_count_mean": operator_stats["term_count"]["mean"],
                "term_count_std": operator_stats["term_count"]["std"],
                "support_max_mean": operator_stats["support_max_qubit"]["mean"],
                "support_max_std": operator_stats["support_max_qubit"]["std"],
                "perturbed_echo_mean": baseline_entry["perturbed_echo"]["mean"],
                "perturbed_echo_std": baseline_entry["perturbed_echo"]["std"],
                "notes": "State-return baseline only; not OLE.",
            }
        )

        for branch_name, branch_entry in depth_entry["branches"].items():
            for delta, delta_sq, f_mean, f_std, fn_mean, fn_std in zip(
                delta_grid,
                delta_squared_grid,
                branch_entry["F_delta"]["mean"],
                branch_entry["F_delta"]["std"],
                branch_entry["f_delta"]["mean"],
                branch_entry["f_delta"]["std"],
            ):
                rows.append(
                    {
                        "row_kind": "ole",
                        "depth": depth,
                        "branch": branch_name,
                        "generator_label": branch_entry["generator_label"],
                        "delta": delta,
                        "delta_sq": delta_sq,
                        "F_delta_mean": f_mean,
                        "F_delta_std": f_std,
                        "f_delta_mean": fn_mean,
                        "f_delta_std": fn_std,
                        "w_anti_mean": branch_entry["w_anti"]["mean"],
                        "w_anti_std": branch_entry["w_anti"]["std"],
                        "kappa_mean": branch_entry["kappa"]["mean"],
                        "kappa_std": branch_entry["kappa"]["std"],
                        "term_count_mean": operator_stats["term_count"]["mean"],
                        "term_count_std": operator_stats["term_count"]["std"],
                        "support_max_mean": operator_stats["support_max_qubit"]["mean"],
                        "support_max_std": operator_stats["support_max_qubit"]["std"],
                        "perturbed_echo_mean": baseline_entry["perturbed_echo"]["mean"],
                        "perturbed_echo_std": baseline_entry["perturbed_echo"]["std"],
                        "notes": "",
                    }
                )

    return rows


def write_csv(path: Path, rows: Iterable[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: float, digits: int = 6) -> str:
    return f"{value:.{digits}f}"


def fmt_pm(mean: float, std: float, digits: int = 6) -> str:
    return f"{mean:.{digits}f} +/- {std:.{digits}f}"


def render_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    separator = ["---"] * len(headers)
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(separator) + " |"]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return lines


def render_report(ole_data: dict, baseline_data: dict, manifest_data: dict, csv_path: Path) -> str:
    ole_config = ole_data["config"]
    manifest_fixed = manifest_data["fixed_parameters"]
    baseline_by_depth = {row["depth"]: row for row in baseline_data["results"]}
    generated_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    normalized_scale = 2 ** (-ole_config["qubits"])

    lines: list[str] = []
    lines.append("# q14 OLE vs delta^2 benchmark")
    lines.append("")
    lines.append(f"Generated: {generated_utc}")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("- Fixed observable: `P = Z_0`.")
    lines.append(
        f"- Reported OLE quantity: `F_delta(P)` with normalized translation `f_delta(O) = 2^-14 F_delta(P)` and `O = Z_0 / sqrt(2^14)`."
    )
    lines.append("- OLE support variants: overlap `G = X_0` and disjoint control `G = X_10`.")
    lines.append(
        "- Comparison baseline: `perturbed_echo` from the q14 exact-short state-return workflow. It is a same-family reference, not the OLE curve."
    )
    lines.append("")
    lines.append("## Manifest continuity")
    lines.append("")
    lines.extend(
        render_table(
            ["field", "value"],
            [
                ["benchmark_id", manifest_data["benchmark_id"]],
                ["qubits", str(ole_config["qubits"])],
                ["depths", ", ".join(str(depth) for depth in ole_config["depths"])],
                ["trials", str(ole_config["trials"])],
                ["seed", str(ole_config["seed"])],
                ["shots", str(manifest_fixed["shots"])],
                ["delta grid", ", ".join(f"{delta:.3f}" for delta in ole_config["delta_grid"])],
                ["delta^2 grid", ", ".join(f"{delta_sq:.6f}" for delta_sq in ole_config["delta_squared_grid"])],
                ["normalized scale", f"2^-14 = {normalized_scale:.14f}"],
                ["CSV export", str(csv_path.relative_to(REPO_ROOT))],
            ],
        )
    )
    lines.append("")
    lines.append("## Baseline reference")
    lines.append("")
    lines.append(
        "The baseline is listed separately because it is a full-kick state-return observable and would collapse the small-delta onset panel if it were forced onto the same narrow `delta^2` axis."
    )
    lines.append("")
    baseline_rows: list[list[str]] = []
    for depth_entry in ole_data["results"]:
        depth = depth_entry["depth"]
        baseline_entry = baseline_by_depth[depth]
        baseline_rows.append(
            [
                str(depth),
                fmt_pm(baseline_entry["perturbed_echo"]["mean"], baseline_entry["perturbed_echo"]["std"]),
                fmt_pm(baseline_entry["ideal_echo"]["mean"], baseline_entry["ideal_echo"]["std"]),
                fmt_pm(baseline_entry["renyi2"]["mean"], baseline_entry["renyi2"]["std"]),
            ]
        )
    lines.extend(
        render_table(
            ["depth", "perturbed_echo", "ideal_echo", "renyi2"],
            baseline_rows,
        )
    )
    lines.append("")
    lines.append("## OLE onset overview")
    lines.append("")
    overview_rows: list[list[str]] = []
    for depth_entry in ole_data["results"]:
        depth = depth_entry["depth"]
        overlap = depth_entry["branches"]["overlap"]
        disjoint = depth_entry["branches"]["disjoint"]
        operator_stats = depth_entry["operator_stats"]
        baseline_entry = baseline_by_depth[depth]
        overview_rows.append(
            [
                str(depth),
                fmt_pm(operator_stats["term_count"]["mean"], operator_stats["term_count"]["std"], digits=2),
                fmt_pm(operator_stats["support_max_qubit"]["mean"], operator_stats["support_max_qubit"]["std"], digits=2),
                fmt_pm(overlap["kappa"]["mean"], overlap["kappa"]["std"]),
                fmt_pm(disjoint["kappa"]["mean"], disjoint["kappa"]["std"]),
                fmt_pm(baseline_entry["perturbed_echo"]["mean"], baseline_entry["perturbed_echo"]["std"]),
            ]
        )
    lines.extend(
        render_table(
            ["depth", "term_count", "support_max_qubit", "kappa overlap", "kappa disjoint", "perturbed_echo baseline"],
            overview_rows,
        )
    )
    lines.append("")
    lines.append("## delta^2 onset panels")
    lines.append("")
    lines.append(
        "Tables below use `delta^2` as the x-axis for the exact OLE onset. Both branches are shown explicitly for every active depth."
    )
    lines.append("")

    delta_sq_headers = [f"{delta_sq:.6f}" for delta_sq in ole_config["delta_squared_grid"]]
    for depth_entry in ole_data["results"]:
        depth = depth_entry["depth"]
        lines.append(f"### Depth {depth}")
        lines.append("")
        depth_rows: list[list[str]] = []
        for branch_name in ("overlap", "disjoint"):
            branch_entry = depth_entry["branches"][branch_name]
            curve = [
                fmt_pm(mean, std)
                for mean, std in zip(branch_entry["F_delta"]["mean"], branch_entry["F_delta"]["std"])
            ]
            depth_rows.append(
                [branch_name, branch_entry["generator_label"]] + curve
            )
        lines.extend(
            render_table(
                ["branch", "generator"] + delta_sq_headers,
                depth_rows,
            )
        )
        lines.append("")

    lines.append("## Reading guide")
    lines.append("")
    lines.append("- The overlap branch is the exact OLE signal. Its near-zero drop is controlled by `kappa_{X_0}(Z_0; U)`.")
    lines.append("- The disjoint branch is an exact locality control on the active manifest and should stay flat at `F_delta = 1`.")
    lines.append("- The `perturbed_echo` numbers remain a state-return baseline. They are intentionally juxtaposed rather than relabeled as OLE.")
    lines.append("- Formal fit-window validation is deferred to `.gpd/phases/02/q14_small_delta_validation.md` in Wave 3.")
    lines.append("")

    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    ole_data = load_json(args.ole_json)
    baseline_data = load_json(args.baseline_json)
    manifest_data = load_json(args.manifest_json)

    validate_inputs(ole_data, baseline_data, manifest_data)
    csv_rows = build_csv_rows(ole_data, baseline_data)
    write_csv(args.report_csv, csv_rows)

    report_text = render_report(ole_data, baseline_data, manifest_data, args.report_csv)
    args.report_md.parent.mkdir(parents=True, exist_ok=True)
    args.report_md.write_text(report_text, encoding="utf-8")

    print(f"CSV saved to: {args.report_csv.relative_to(REPO_ROOT)}")
    print(f"Report saved to: {args.report_md.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
