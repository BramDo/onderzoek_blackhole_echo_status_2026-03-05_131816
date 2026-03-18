#!/usr/bin/env python3
"""Exact q14 operator Loschmidt echo benchmark for the fixed-observable bridge.

This script keeps the existing q14 exact-short benchmark family intact while
adding the fixed-observable OLE quantity

    F_delta(P; U, X_q) = 2^-n Tr(U P U^dagger V_delta^dagger U P U^dagger V_delta)

for the Phase 1 lock:
  - P = Z_0
  - overlap branch  : G = X_0
  - disjoint branch : G = X_10

The implementation stays exact by propagating the observable through the
brickwork circuit as a sparse Pauli expansion instead of constructing dense
14-qubit operators.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import DefaultDict, Dict, Iterable, List, Sequence, Tuple

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator, SparsePauliOp

from qiskit_black_hole_scrambling import brickwork_scrambler, parse_depths

PAULI_IDENTITY = "I"
ANTI_COMMUTING_LOCAL_FACTORS = {"Y", "Z"}
TRUNCATION_TOL = 1e-12
SELF_CHECK_TOL = 1e-10


def parse_float_grid(raw: str) -> List[float]:
    values = [float(token.strip()) for token in raw.split(",") if token.strip()]
    if not values:
        raise ValueError("delta-grid is empty")
    if any(value < 0.0 for value in values):
        raise ValueError("delta-grid must be non-negative")
    return values


def replace_pauli(label: str, qubit: int, pauli: str) -> str:
    return label[:qubit] + pauli + label[qubit + 1 :]


def physical_to_qiskit_label(label: str) -> str:
    return label[::-1]


def pauli_matrix_from_physical_label(label: str) -> np.ndarray:
    qiskit_label = physical_to_qiskit_label(label)
    return SparsePauliOp.from_list([(qiskit_label, 1.0)]).to_matrix()


def multiply_single_pauli(left: str, right: str) -> Tuple[complex, str]:
    if left == PAULI_IDENTITY:
        return 1.0 + 0.0j, right
    if right == PAULI_IDENTITY:
        return 1.0 + 0.0j, left
    if left == right:
        return 1.0 + 0.0j, PAULI_IDENTITY

    table = {
        ("X", "Y"): (1.0j, "Z"),
        ("Y", "X"): (-1.0j, "Z"),
        ("Y", "Z"): (1.0j, "X"),
        ("Z", "Y"): (-1.0j, "X"),
        ("Z", "X"): (1.0j, "Y"),
        ("X", "Z"): (-1.0j, "Y"),
    }
    return table[(left, right)]


def apply_rx_conjugation(label: str, qubit: int, theta: float) -> Dict[str, complex]:
    factor = label[qubit]
    if factor in {"I", "X"}:
        return {label: 1.0 + 0.0j}
    if factor == "Y":
        return {
            label: complex(math.cos(theta), 0.0),
            replace_pauli(label, qubit, "Z"): complex(math.sin(theta), 0.0),
        }
    if factor == "Z":
        return {
            label: complex(math.cos(theta), 0.0),
            replace_pauli(label, qubit, "Y"): complex(-math.sin(theta), 0.0),
        }
    raise ValueError(f"Unexpected Pauli factor for RX conjugation: {factor}")


def apply_rz_conjugation(label: str, qubit: int, theta: float) -> Dict[str, complex]:
    factor = label[qubit]
    if factor in {"I", "Z"}:
        return {label: 1.0 + 0.0j}
    if factor == "X":
        return {
            label: complex(math.cos(theta), 0.0),
            replace_pauli(label, qubit, "Y"): complex(math.sin(theta), 0.0),
        }
    if factor == "Y":
        return {
            label: complex(math.cos(theta), 0.0),
            replace_pauli(label, qubit, "X"): complex(-math.sin(theta), 0.0),
        }
    raise ValueError(f"Unexpected Pauli factor for RZ conjugation: {factor}")


def apply_cz_conjugation(label: str, qubit_a: int, qubit_b: int) -> Dict[str, complex]:
    local_a = label[qubit_a]
    local_b = label[qubit_b]

    map_a = {
        "I": ("I", "I"),
        "X": ("X", "Z"),
        "Y": ("Y", "Z"),
        "Z": ("Z", "I"),
    }
    map_b = {
        "I": ("I", "I"),
        "X": ("Z", "X"),
        "Y": ("Z", "Y"),
        "Z": ("I", "Z"),
    }

    a0, a1 = map_a[local_a]
    b0, b1 = map_b[local_b]
    phase_a, new_a = multiply_single_pauli(a0, b0)
    phase_b, new_b = multiply_single_pauli(a1, b1)

    out = list(label)
    out[qubit_a] = new_a
    out[qubit_b] = new_b
    return {"".join(out): phase_a * phase_b}


def propagate_observable_pauli_basis(
    n_qubits: int,
    circuit: QuantumCircuit,
    observable_qubit: int,
    observable_axis: str,
) -> Dict[str, complex]:
    label = ["I"] * n_qubits
    label[observable_qubit] = observable_axis.upper()
    coefficients: Dict[str, complex] = {"".join(label): 1.0 + 0.0j}

    for instruction in circuit.data:
        operation = instruction.operation
        qubits = [qubit._index for qubit in instruction.qubits]
        updated: DefaultDict[str, complex] = defaultdict(complex)

        if operation.name == "rx":
            theta = float(operation.params[0])
            target = qubits[0]
            for term, coeff in coefficients.items():
                for new_term, phase in apply_rx_conjugation(term, target, theta).items():
                    updated[new_term] += coeff * phase
        elif operation.name == "rz":
            theta = float(operation.params[0])
            target = qubits[0]
            for term, coeff in coefficients.items():
                for new_term, phase in apply_rz_conjugation(term, target, theta).items():
                    updated[new_term] += coeff * phase
        elif operation.name == "cz":
            qubit_a, qubit_b = qubits
            for term, coeff in coefficients.items():
                for new_term, phase in apply_cz_conjugation(term, qubit_a, qubit_b).items():
                    updated[new_term] += coeff * phase
        else:
            raise ValueError(f"Unsupported gate in exact OLE propagation: {operation.name}")

        coefficients = {
            term: coeff
            for term, coeff in updated.items()
            if abs(coeff) > TRUNCATION_TOL
        }

    return coefficients


def hilbert_schmidt_norm(coefficients: Dict[str, complex]) -> float:
    return float(sum(abs(coeff) ** 2 for coeff in coefficients.values()))


def support_qubits(coefficients: Dict[str, complex]) -> List[int]:
    active = set()
    for label, coeff in coefficients.items():
        if abs(coeff) <= TRUNCATION_TOL:
            continue
        for qubit, factor in enumerate(label):
            if factor != PAULI_IDENTITY:
                active.add(qubit)
    return sorted(active)


def top_terms(coefficients: Dict[str, complex], limit: int = 8) -> List[Dict[str, object]]:
    ranked = sorted(
        coefficients.items(),
        key=lambda item: (-abs(item[1]) ** 2, physical_to_qiskit_label(item[0])),
    )
    rows: List[Dict[str, object]] = []
    for label, coeff in ranked[:limit]:
        rows.append(
            {
                "physical_label": label,
                "qiskit_label": physical_to_qiskit_label(label),
                "coeff_real": float(np.real(coeff)),
                "coeff_imag": float(np.imag(coeff)),
                "weight": float(abs(coeff) ** 2),
            }
        )
    return rows


def branch_metrics(
    coefficients: Dict[str, complex],
    generator_qubit: int,
    delta_grid: Sequence[float],
    n_qubits: int,
) -> Dict[str, object]:
    anti_weight = float(
        sum(
            abs(coeff) ** 2
            for label, coeff in coefficients.items()
            if label[generator_qubit] in ANTI_COMMUTING_LOCAL_FACTORS
        )
    )
    kappa = float(4.0 * anti_weight)
    f_scale = float(2.0 ** (-n_qubits))

    f_delta = [
        float(1.0 - (1.0 - math.cos(2.0 * delta)) * anti_weight)
        for delta in delta_grid
    ]
    normalized = [float(value * f_scale) for value in f_delta]

    return {
        "w_anti": anti_weight,
        "kappa": kappa,
        "small_delta_quadratic_coeff": float(-0.5 * kappa),
        "F_delta": f_delta,
        "f_delta": normalized,
    }


def summarize_samples(values: Sequence[float]) -> Dict[str, float]:
    array = np.asarray(values, dtype=float)
    return {
        "mean": float(np.mean(array)),
        "std": float(np.std(array)),
        "min": float(np.min(array)),
        "max": float(np.max(array)),
    }


def summarize_curve(curves: Sequence[Sequence[float]]) -> Dict[str, List[float]]:
    array = np.asarray(curves, dtype=float)
    return {
        "mean": [float(value) for value in np.mean(array, axis=0)],
        "std": [float(value) for value in np.std(array, axis=0)],
    }


def coeffs_to_dense_matrix(coefficients: Dict[str, complex]) -> np.ndarray:
    dimension = 2 ** len(next(iter(coefficients)))
    dense = np.zeros((dimension, dimension), dtype=complex)
    for label, coeff in coefficients.items():
        dense += coeff * pauli_matrix_from_physical_label(label)
    return dense


def gate_rule_self_check() -> Dict[str, object]:
    checked_cases = 0
    max_abs_error = 0.0

    one_qubit_terms = ["I", "X", "Y", "Z"]
    rx_angle = 0.371
    rz_angle = 0.643

    for label in one_qubit_terms:
        term = {"physical_label": label}

        rx_coeffs = apply_rx_conjugation(label, 0, rx_angle)
        rx_dense = coeffs_to_dense_matrix(rx_coeffs)
        rx_circuit = QuantumCircuit(1)
        rx_circuit.rx(rx_angle, 0)
        exact_rx = (
            Operator(rx_circuit).data
            @ pauli_matrix_from_physical_label(label)
            @ Operator(rx_circuit).data.conj().T
        )
        max_abs_error = max(max_abs_error, float(np.max(np.abs(rx_dense - exact_rx))))
        checked_cases += 1

        rz_coeffs = apply_rz_conjugation(label, 0, rz_angle)
        rz_dense = coeffs_to_dense_matrix(rz_coeffs)
        rz_circuit = QuantumCircuit(1)
        rz_circuit.rz(rz_angle, 0)
        exact_rz = (
            Operator(rz_circuit).data
            @ pauli_matrix_from_physical_label(label)
            @ Operator(rz_circuit).data.conj().T
        )
        max_abs_error = max(max_abs_error, float(np.max(np.abs(rz_dense - exact_rz))))
        checked_cases += 1

    two_qubit_terms = [a + b for a in one_qubit_terms for b in one_qubit_terms]
    cz_circuit = QuantumCircuit(2)
    cz_circuit.cz(0, 1)
    cz_operator = Operator(cz_circuit).data
    for label in two_qubit_terms:
        cz_coeffs = apply_cz_conjugation(label, 0, 1)
        cz_dense = coeffs_to_dense_matrix(cz_coeffs)
        exact_cz = (
            cz_operator
            @ pauli_matrix_from_physical_label(label)
            @ cz_operator.conj().T
        )
        max_abs_error = max(max_abs_error, float(np.max(np.abs(cz_dense - exact_cz))))
        checked_cases += 1

    passed = max_abs_error < SELF_CHECK_TOL
    return {
        "passed": passed,
        "checked_cases": checked_cases,
        "max_abs_error": max_abs_error,
        "tolerance": SELF_CHECK_TOL,
    }


def dense_ole_cross_check(delta_grid: Sequence[float]) -> Dict[str, object]:
    n_qubits = 3
    depth = 2
    seed = 123456
    rng = np.random.default_rng(seed)
    circuit = brickwork_scrambler(n_qubits=n_qubits, depth=depth, rng=rng)
    coefficients = propagate_observable_pauli_basis(
        n_qubits=n_qubits,
        circuit=circuit,
        observable_qubit=0,
        observable_axis="Z",
    )
    dense_observable = coeffs_to_dense_matrix(coefficients)
    overlap_metrics = branch_metrics(coefficients, generator_qubit=0, delta_grid=delta_grid, n_qubits=n_qubits)
    disjoint_metrics = branch_metrics(coefficients, generator_qubit=2, delta_grid=delta_grid, n_qubits=n_qubits)

    pauli_x = pauli_matrix_from_physical_label("XII")
    pauli_x_far = pauli_matrix_from_physical_label("IIX")
    identity = np.eye(2**n_qubits, dtype=complex)
    max_abs_error = 0.0

    for delta_index, delta in enumerate(delta_grid[:3]):
        for branch_name, generator in (
            ("overlap", pauli_x),
            ("disjoint", pauli_x_far),
        ):
            v_delta = math.cos(delta) * identity - 1.0j * math.sin(delta) * generator
            exact_value = float(
                np.real(
                    np.trace(
                        dense_observable
                        @ v_delta.conj().T
                        @ dense_observable
                        @ v_delta
                    )
                )
                / (2**n_qubits)
            )
            predicted = (
                overlap_metrics["F_delta"][delta_index]
                if branch_name == "overlap"
                else disjoint_metrics["F_delta"][delta_index]
            )
            max_abs_error = max(max_abs_error, abs(exact_value - predicted))

    passed = max_abs_error < SELF_CHECK_TOL
    return {
        "passed": passed,
        "n_qubits": n_qubits,
        "depth": depth,
        "seed": seed,
        "max_abs_error": max_abs_error,
        "tolerance": SELF_CHECK_TOL,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Exact fixed-observable q14 OLE benchmark")
    parser.add_argument("--manifest", type=str, default="files/quantum-math-lab/benchmarks/q14_only_manifest.json")
    parser.add_argument("--qubits", type=int, default=14)
    parser.add_argument("--depths", type=str, default="1,2,3,4")
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--seed", type=int, default=424242)
    parser.add_argument("--observable-qubit", type=int, default=0)
    parser.add_argument("--observable-axis", type=str, default="Z")
    parser.add_argument("--overlap-qubit", type=int, default=0)
    parser.add_argument("--disjoint-qubit", type=int, default=10)
    parser.add_argument(
        "--delta-grid",
        type=str,
        default="0.000,0.025,0.050,0.075,0.100,0.125,0.150,0.200,0.250,0.300",
    )
    parser.add_argument(
        "--json-out",
        type=str,
        default="files/quantum-math-lab/results/ole/black_hole_ole_q14_exact_small_delta.json",
    )
    parser.add_argument("--skip-self-check", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.qubits < 1:
        raise ValueError("qubits must be positive")
    if args.trials < 1:
        raise ValueError("trials must be at least 1")

    depths = parse_depths(args.depths)
    delta_grid = parse_float_grid(args.delta_grid)
    delta_squared_grid = [float(delta * delta) for delta in delta_grid]

    if not (0 <= args.observable_qubit < args.qubits):
        raise ValueError("observable-qubit outside qubit range")
    if not (0 <= args.overlap_qubit < args.qubits):
        raise ValueError("overlap-qubit outside qubit range")
    if not (0 <= args.disjoint_qubit < args.qubits):
        raise ValueError("disjoint-qubit outside qubit range")

    output_path = Path(args.json_out)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    manifest = {}
    manifest_path = Path(args.manifest)
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    self_checks = {}
    if args.skip_self_check:
        self_checks["skipped"] = True
    else:
        self_checks["gate_rules"] = gate_rule_self_check()
        self_checks["dense_cross_check"] = dense_ole_cross_check(delta_grid)
        if not self_checks["gate_rules"]["passed"]:
            raise RuntimeError("Gate-rule self-check failed")
        if not self_checks["dense_cross_check"]["passed"]:
            raise RuntimeError("Dense small-n OLE cross-check failed")

    master_rng = np.random.default_rng(args.seed)
    results: List[Dict[str, object]] = []

    print("depth | terms(mean) | support_max(mean) | kappa_overlap(mean) | kappa_disjoint(mean)")

    for depth in depths:
        samples: List[Dict[str, object]] = []
        term_counts: List[float] = []
        norm_values: List[float] = []
        support_max_values: List[float] = []
        overlap_wanti: List[float] = []
        overlap_kappa: List[float] = []
        overlap_curves: List[List[float]] = []
        overlap_curves_norm: List[List[float]] = []
        disjoint_wanti: List[float] = []
        disjoint_kappa: List[float] = []
        disjoint_curves: List[List[float]] = []
        disjoint_curves_norm: List[List[float]] = []

        for trial in range(args.trials):
            trial_seed = int(master_rng.integers(0, 2**32 - 1))
            rng = np.random.default_rng(trial_seed)
            circuit = brickwork_scrambler(n_qubits=args.qubits, depth=depth, rng=rng)
            coefficients = propagate_observable_pauli_basis(
                n_qubits=args.qubits,
                circuit=circuit,
                observable_qubit=args.observable_qubit,
                observable_axis=args.observable_axis,
            )

            norm = hilbert_schmidt_norm(coefficients)
            active_support = support_qubits(coefficients)
            support_max = max(active_support) if active_support else -1
            overlap = branch_metrics(coefficients, args.overlap_qubit, delta_grid, args.qubits)
            disjoint = branch_metrics(coefficients, args.disjoint_qubit, delta_grid, args.qubits)

            term_counts.append(float(len(coefficients)))
            norm_values.append(norm)
            support_max_values.append(float(support_max))
            overlap_wanti.append(float(overlap["w_anti"]))
            overlap_kappa.append(float(overlap["kappa"]))
            overlap_curves.append(list(overlap["F_delta"]))
            overlap_curves_norm.append(list(overlap["f_delta"]))
            disjoint_wanti.append(float(disjoint["w_anti"]))
            disjoint_kappa.append(float(disjoint["kappa"]))
            disjoint_curves.append(list(disjoint["F_delta"]))
            disjoint_curves_norm.append(list(disjoint["f_delta"]))

            samples.append(
                {
                    "trial": trial + 1,
                    "seed": trial_seed,
                    "term_count": int(len(coefficients)),
                    "hilbert_schmidt_norm": norm,
                    "support_qubits": active_support,
                    "support_max_qubit": support_max,
                    "top_terms": top_terms(coefficients),
                    "branches": {
                        "overlap": {
                            "generator_label": f"X_{args.overlap_qubit}",
                            **overlap,
                        },
                        "disjoint": {
                            "generator_label": f"X_{args.disjoint_qubit}",
                            **disjoint,
                        },
                    },
                }
            )

        depth_record = {
            "depth": depth,
            "operator_stats": {
                "term_count": summarize_samples(term_counts),
                "hilbert_schmidt_norm": summarize_samples(norm_values),
                "support_max_qubit": summarize_samples(support_max_values),
            },
            "branches": {
                "overlap": {
                    "generator_label": f"X_{args.overlap_qubit}",
                    "w_anti": summarize_samples(overlap_wanti),
                    "kappa": summarize_samples(overlap_kappa),
                    "F_delta": summarize_curve(overlap_curves),
                    "f_delta": summarize_curve(overlap_curves_norm),
                },
                "disjoint": {
                    "generator_label": f"X_{args.disjoint_qubit}",
                    "w_anti": summarize_samples(disjoint_wanti),
                    "kappa": summarize_samples(disjoint_kappa),
                    "F_delta": summarize_curve(disjoint_curves),
                    "f_delta": summarize_curve(disjoint_curves_norm),
                },
            },
            "samples": samples,
        }
        results.append(depth_record)

        print(
            f"{depth:>5d} | "
            f"{depth_record['operator_stats']['term_count']['mean']:11.2f} | "
            f"{depth_record['operator_stats']['support_max_qubit']['mean']:16.2f} | "
            f"{depth_record['branches']['overlap']['kappa']['mean']:18.8f} | "
            f"{depth_record['branches']['disjoint']['kappa']['mean']:19.8f}"
        )

    depth0_overlap = branch_metrics(
        coefficients={"Z" + "I" * (args.qubits - 1): 1.0 + 0.0j},
        generator_qubit=args.overlap_qubit,
        delta_grid=delta_grid,
        n_qubits=args.qubits,
    )
    depth0_disjoint = branch_metrics(
        coefficients={"Z" + "I" * (args.qubits - 1): 1.0 + 0.0j},
        generator_qubit=args.disjoint_qubit,
        delta_grid=delta_grid,
        n_qubits=args.qubits,
    )

    artifact = {
        "config": {
            "qubits": args.qubits,
            "trials": args.trials,
            "depths": depths,
            "seed": args.seed,
            "delta_grid": delta_grid,
            "delta_squared_grid": delta_squared_grid,
            "observable": {
                "label": f"{args.observable_axis.upper()}_{args.observable_qubit}",
                "axis": args.observable_axis.upper(),
                "qubit": args.observable_qubit,
                "normalized_translation": f"{args.observable_axis.upper()}_{args.observable_qubit} / sqrt(2^{args.qubits})",
            },
            "branches": {
                "overlap": {"generator_label": f"X_{args.overlap_qubit}", "qubit": args.overlap_qubit},
                "disjoint": {"generator_label": f"X_{args.disjoint_qubit}", "qubit": args.disjoint_qubit},
            },
            "report_quantity": "F_delta(P)",
            "normalized_quantity": "f_delta(O)",
            "normalized_translation_rule": f"f_delta(O) = 2^-{args.qubits} F_delta(P)",
        },
        "manifest_ref": str(manifest_path),
        "manifest_snapshot": manifest,
        "baseline_ref": "files/quantum-math-lab/results/benchmark/classical/black_hole_scrambling_q14_exact_short.json",
        "self_checks": self_checks,
        "sanity_checks": {
            "depth0_overlap": {
                "branch": "overlap",
                "generator_label": f"X_{args.overlap_qubit}",
                "expected_kappa": 4.0 if args.overlap_qubit == args.observable_qubit else 0.0,
                "computed": depth0_overlap,
                "expected_formula": "cos(2 delta)" if args.overlap_qubit == args.observable_qubit else "1",
            },
            "depth0_disjoint": {
                "branch": "disjoint",
                "generator_label": f"X_{args.disjoint_qubit}",
                "expected_kappa": 4.0 if args.disjoint_qubit == args.observable_qubit else 0.0,
                "computed": depth0_disjoint,
                "expected_formula": "cos(2 delta)" if args.disjoint_qubit == args.observable_qubit else "1",
            },
        },
        "results": results,
    }

    output_path.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    print(f"\nJSON saved to: {output_path}")


if __name__ == "__main__":
    main()
