#!/usr/bin/env python3
"""Qiskit toy experiments for black-hole-like scrambling.

Gebaseerd op de gedeelde ChatGPT-thread:
- random scrambling circuits
- Loschmidt echo (met en zonder lokale perturbatie)
- Renyi-2 entropy groei
- OTOC-achtige correlator / commutator-groei

Uitbreiding:
- optionele finite-shot noise met qiskit-aer (depolarizing + readout),
- optionele readout mitigation via assignment-matrix inversie,
- optionele zero-noise extrapolation (ZNE).
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from typing import Dict, List, Tuple

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, partial_trace


@dataclass
class RunResult:
    depth: int
    ideal_echo: float
    perturbed_echo: float
    renyi2: float
    otoc_real: float
    commutator_sq: float


def brickwork_scrambler(n_qubits: int, depth: int, rng: np.random.Generator) -> QuantumCircuit:
    """Random brickwork circuit met lokale rotaties + CZ-lagen."""
    qc = QuantumCircuit(n_qubits)

    for layer in range(depth):
        for q in range(n_qubits):
            qc.rx(float(rng.uniform(0.0, np.pi)), q)
            qc.rz(float(rng.uniform(0.0, np.pi)), q)

        start = layer % 2
        for q in range(start, n_qubits - 1, 2):
            qc.cz(q, q + 1)

    return qc


def pauli_circuit(n_qubits: int, qubit: int, axis: str) -> QuantumCircuit:
    """Bouw een enkel-qubit Pauli-circuit ingebed in n-qubit ruimte."""
    qc = QuantumCircuit(n_qubits)
    gate = axis.upper()
    if gate == "X":
        qc.x(qubit)
    elif gate == "Y":
        qc.y(qubit)
    elif gate == "Z":
        qc.z(qubit)
    else:
        raise ValueError(f"Onbekende as: {axis}")
    return qc


def renyi2_entropy(state: Statevector, traced_out: List[int]) -> float:
    """S2 = -log(Tr[rho_A^2])."""
    rho_a = partial_trace(state, traced_out)
    purity = float(np.real(np.trace(rho_a.data @ rho_a.data)))
    purity = min(1.0, max(0.0, purity))
    return float(-np.log(max(purity, 1e-15)))


def single_run(
    n_qubits: int,
    depth: int,
    seed: int,
    perturb_qubit: int,
    w_qubit: int,
    v_qubit: int,
) -> Tuple[RunResult, QuantumCircuit]:
    """Eén random-instance voor een vaste depth."""
    rng = np.random.default_rng(seed)
    psi0 = Statevector.from_label("0" * n_qubits)

    # Scrambler U
    u_circuit = brickwork_scrambler(n_qubits=n_qubits, depth=depth, rng=rng)
    u_inverse = u_circuit.inverse()

    # 1) Ideal Loschmidt echo: |<psi0|U†U|psi0>|^2 ≈ 1
    psi_ideal = psi0.evolve(u_circuit).evolve(u_inverse)
    ideal_echo = float(abs(np.vdot(psi0.data, psi_ideal.data)) ** 2)

    # 2) Perturbed Loschmidt echo: |<psi0|U† X U|psi0>|^2
    kick = QuantumCircuit(n_qubits)
    kick.x(perturb_qubit)
    psi_pert = psi0.evolve(u_circuit).evolve(kick).evolve(u_inverse)
    perturbed_echo = float(abs(np.vdot(psi0.data, psi_pert.data)) ** 2)

    # 3) Renyi-2 entropy na scrambling (helft subsystem)
    psi_scrambled = psi0.evolve(u_circuit)
    trace_out = list(range(n_qubits // 2, n_qubits))
    s2 = renyi2_entropy(psi_scrambled, trace_out)

    # 4) OTOC-achtige correlator F = <psi0| W(t) V W(t) V |psi0>
    #    met W(t)=U†WU, W=X op linker rand, V=Z op rechter rand.
    #
    # Dense 2^n x 2^n operators blow up quickly at q14+, so keep this in the
    # statevector domain and apply the evolved Pauli string directly.
    w_circuit = pauli_circuit(n_qubits, w_qubit, "X")
    v_circuit = pauli_circuit(n_qubits, v_qubit, "Z")
    psi_otoc = (
        psi0.evolve(v_circuit)
        .evolve(u_circuit)
        .evolve(w_circuit)
        .evolve(u_inverse)
        .evolve(v_circuit)
        .evolve(u_circuit)
        .evolve(w_circuit)
        .evolve(u_inverse)
    )
    otoc = complex(np.vdot(psi0.data, psi_otoc.data))
    otoc_real = float(np.real(otoc))

    # Vaak gebruikt: C = (1 - Re(F))/2
    comm_sq = float(0.5 * (1.0 - otoc_real))

    return (
        RunResult(
            depth=depth,
            ideal_echo=ideal_echo,
            perturbed_echo=perturbed_echo,
            renyi2=s2,
            otoc_real=otoc_real,
            commutator_sq=comm_sq,
        ),
        u_circuit,
    )


def mean_std(values: List[float]) -> Tuple[float, float]:
    arr = np.asarray(values, dtype=float)
    return float(np.mean(arr)), float(np.std(arr))


def parse_depths(raw: str) -> List[int]:
    depths = [int(x.strip()) for x in raw.split(",") if x.strip()]
    if not depths:
        raise ValueError("Depth-lijst is leeg")
    if any(d < 1 for d in depths):
        raise ValueError("Alle depths moeten >= 1 zijn")
    return depths


def parse_noise_factors(raw: str) -> List[float]:
    factors: List[float] = []
    for tok in raw.split(","):
        tok = tok.strip()
        if not tok:
            continue
        val = float(tok)
        if val <= 0.0:
            raise ValueError(f"Noise factor must be > 0, got {val}")
        factors.append(val)
    if not factors:
        raise ValueError("Geen geldige noise factors")
    return factors


def zne_extrapolate(factors: List[float], values: List[float], order: int) -> Dict[str, object]:
    if len(factors) != len(values):
        raise ValueError("factors en values moeten even lang zijn")

    x = np.asarray(factors, dtype=float)
    y = np.asarray(values, dtype=float)

    max_order = max(0, len(x) - 1)
    order_used = min(max(order, 0), max_order)

    if order_used == 0:
        coeff = np.asarray([float(np.mean(y))], dtype=float)
    else:
        coeff = np.polyfit(x, y, deg=order_used)

    poly = np.poly1d(coeff)
    y0 = float(poly(0.0))

    return {
        "factors": x.tolist(),
        "values": y.tolist(),
        "order_requested": int(order),
        "order_used": int(order_used),
        "poly_coeff_desc": coeff.tolist(),
        "extrapolated_zero_noise": y0,
    }


def build_echo_measurement_circuits(
    u_circuit: QuantumCircuit,
    n_qubits: int,
    perturb_qubit: int,
) -> Tuple[QuantumCircuit, QuantumCircuit]:
    """Bouw meetbare circuits voor ideal en perturbed echo."""
    ideal = QuantumCircuit(n_qubits, n_qubits)
    ideal.compose(u_circuit, inplace=True)
    ideal.compose(u_circuit.inverse(), inplace=True)
    ideal.measure(range(n_qubits), range(n_qubits))

    pert = QuantumCircuit(n_qubits, n_qubits)
    pert.compose(u_circuit, inplace=True)
    pert.x(perturb_qubit)
    pert.compose(u_circuit.inverse(), inplace=True)
    pert.measure(range(n_qubits), range(n_qubits))

    return ideal, pert


def measurement_probs_from_circuit(circuit_with_measurements: QuantumCircuit) -> np.ndarray:
    qc_nom = circuit_with_measurements.remove_final_measurements(inplace=False)
    sv = Statevector.from_instruction(qc_nom)
    probs = np.asarray(sv.probabilities(), dtype=float)
    probs = np.clip(probs, 0.0, None)
    probs = probs / probs.sum()
    return probs


def counts_to_prob_vector(counts: Dict[str, int], n_qubits: int, shots: int) -> np.ndarray:
    n_labels = 2**n_qubits
    p_obs = np.zeros(n_labels, dtype=float)
    if shots <= 0:
        raise ValueError("shots moet positief zijn")

    for key, value in counts.items():
        if isinstance(key, int):
            idx = int(key)
        else:
            bits = str(key).replace(" ", "")
            bits = bits.zfill(n_qubits)
            idx = int(bits, 2)
        if 0 <= idx < n_labels:
            p_obs[idx] += float(value) / float(shots)

    s = float(p_obs.sum())
    if s > 0.0:
        p_obs /= s
    return p_obs


def probability_all_zero_from_counts(counts: Dict[str, int], n_qubits: int, shots: int) -> float:
    p_obs = counts_to_prob_vector(counts, n_qubits=n_qubits, shots=shots)
    return float(p_obs[0])


def build_readout_assignment_matrix(n_qubits: int, p_ro: float) -> np.ndarray:
    """A met p_obs = A @ p_true voor onafhankelijke bit-flips met kans p_ro."""
    a1 = np.asarray([[1.0 - p_ro, p_ro], [p_ro, 1.0 - p_ro]], dtype=float)
    a = a1.copy()
    for _ in range(n_qubits - 1):
        a = np.kron(a, a1)
    return a


def mitigate_all_zero_probability(
    counts: Dict[str, int],
    n_qubits: int,
    shots: int,
    p_ro: float,
) -> Tuple[float, Dict[str, float]]:
    p_obs = counts_to_prob_vector(counts, n_qubits=n_qubits, shots=shots)
    a = build_readout_assignment_matrix(n_qubits=n_qubits, p_ro=p_ro)

    p_true = np.linalg.pinv(a, rcond=1e-12) @ p_obs
    neg_mass = float(-np.minimum(p_true, 0.0).sum())
    p_true = np.clip(p_true, 0.0, None)

    norm = float(p_true.sum())
    if norm <= 0.0:
        raise ValueError("Mitigatie normalisatie faalde")
    p_true /= norm

    info = {
        "assignment_matrix_condition_number": float(np.linalg.cond(a)),
        "negative_mass_before_clip": neg_mass,
        "mitigation_readout_flip_probability": float(p_ro),
    }
    return float(p_true[0]), info


def sample_with_fallback_noise(
    ideal_probs: np.ndarray,
    shots: int,
    rng: np.random.Generator,
    p_dep: float,
    p_ro: float,
    n_qubits: int,
) -> Dict[str, int]:
    """Fallback zonder Aer: mix met uniform + onafhankelijke readout bit-flips."""
    n_labels = 2**n_qubits
    dep = float(np.clip(p_dep, 0.0, 0.999))

    probs = np.asarray(ideal_probs, dtype=float)
    probs = np.clip(probs, 0.0, None)
    probs = probs / probs.sum()

    uniform = np.full(n_labels, 1.0 / n_labels, dtype=float)
    probs_noisy = (1.0 - dep) * probs + dep * uniform

    sampled = rng.choice(n_labels, size=shots, p=probs_noisy)

    if p_ro > 0.0:
        mask = np.zeros(shots, dtype=np.int64)
        for bit in range(n_qubits):
            flips = (rng.random(shots) < p_ro).astype(np.int64)
            mask ^= flips << bit
        sampled = sampled ^ mask

    hist = np.bincount(sampled, minlength=n_labels)
    counts: Dict[str, int] = {}
    for i, c in enumerate(hist.tolist()):
        if c:
            counts[format(i, f"0{n_qubits}b")] = int(c)
    return counts


def try_aer_noise_run_pair(
    ideal_circuit: QuantumCircuit,
    pert_circuit: QuantumCircuit,
    shots: int,
    seed: int,
    p_dep: float,
    p_ro: float,
) -> Tuple[bool, Dict[str, int], Dict[str, int], str]:
    try:
        from qiskit import transpile
        from qiskit_aer import AerSimulator
        from qiskit_aer.noise import NoiseModel, ReadoutError, depolarizing_error
    except Exception:
        return False, {}, {}, "qiskit-aer not available"

    try:
        dep = float(np.clip(p_dep, 0.0, 0.999))

        noise_model = NoiseModel()

        err1 = depolarizing_error(dep, 1)
        err2 = depolarizing_error(dep, 2)

        one_qubit_ops = ["x", "sx", "rz", "rx", "ry", "h", "u", "u1", "u2", "u3", "p"]
        two_qubit_ops = ["cx", "cz", "ecr"]
        noise_model.add_all_qubit_quantum_error(err1, one_qubit_ops)
        noise_model.add_all_qubit_quantum_error(err2, two_qubit_ops)

        ro = ReadoutError([[1.0 - p_ro, p_ro], [p_ro, 1.0 - p_ro]])
        noise_model.add_all_qubit_readout_error(ro)

        backend = AerSimulator(noise_model=noise_model, seed_simulator=int(seed))
        tcircs = transpile([ideal_circuit, pert_circuit], backend)
        res = backend.run(tcircs, shots=int(shots)).result()

        counts_ideal = res.get_counts(0)
        counts_pert = res.get_counts(1)
        return True, counts_ideal, counts_pert, "aer depolarizing+readout"
    except Exception as exc:
        return False, {}, {}, f"aer failed: {type(exc).__name__}: {exc}"


def run_noisy_echo_pair(
    u_circuit: QuantumCircuit,
    n_qubits: int,
    perturb_qubit: int,
    shots: int,
    seed: int,
    p_dep: float,
    p_ro: float,
    readout_mitigation: bool,
    mitigation_p_ro: float,
) -> Dict[str, object]:
    ideal_c, pert_c = build_echo_measurement_circuits(
        u_circuit=u_circuit,
        n_qubits=n_qubits,
        perturb_qubit=perturb_qubit,
    )

    aer_ok, counts_ideal, counts_pert, mode = try_aer_noise_run_pair(
        ideal_circuit=ideal_c,
        pert_circuit=pert_c,
        shots=shots,
        seed=seed,
        p_dep=p_dep,
        p_ro=p_ro,
    )

    if not aer_ok:
        probs_ideal = measurement_probs_from_circuit(ideal_c)
        probs_pert = measurement_probs_from_circuit(pert_c)

        rng_i = np.random.default_rng(seed)
        rng_p = np.random.default_rng(seed + 1)

        counts_ideal = sample_with_fallback_noise(
            ideal_probs=probs_ideal,
            shots=shots,
            rng=rng_i,
            p_dep=p_dep,
            p_ro=p_ro,
            n_qubits=n_qubits,
        )
        counts_pert = sample_with_fallback_noise(
            ideal_probs=probs_pert,
            shots=shots,
            rng=rng_p,
            p_dep=p_dep,
            p_ro=p_ro,
            n_qubits=n_qubits,
        )
        mode = "fallback: statevector probs + depolarize + readout flips"

    raw_ideal = probability_all_zero_from_counts(counts_ideal, n_qubits=n_qubits, shots=shots)
    raw_pert = probability_all_zero_from_counts(counts_pert, n_qubits=n_qubits, shots=shots)

    result: Dict[str, object] = {
        "backend_modes": {mode: 2},
        "raw": {
            "ideal_echo": float(raw_ideal),
            "perturbed_echo": float(raw_pert),
        },
    }

    if readout_mitigation:
        mit_i, info_i = mitigate_all_zero_probability(
            counts_ideal,
            n_qubits=n_qubits,
            shots=shots,
            p_ro=mitigation_p_ro,
        )
        mit_p, info_p = mitigate_all_zero_probability(
            counts_pert,
            n_qubits=n_qubits,
            shots=shots,
            p_ro=mitigation_p_ro,
        )
        result["readout_mitigated"] = {
            "ideal_echo": float(mit_i),
            "perturbed_echo": float(mit_p),
        }
        result["mitigation_info"] = {
            "ideal": info_i,
            "perturbed": info_p,
        }

    return result


def curve_summary(values_by_factor: Dict[float, List[float]], factors: List[float]) -> List[Dict[str, float]]:
    out: List[Dict[str, float]] = []
    for fac in factors:
        vals = values_by_factor[fac]
        m, s = mean_std(vals)
        out.append({"factor": float(fac), "mean": m, "std": s})
    return out


def metric_zne_summary(
    factors: List[float],
    target_curve_means: List[float],
    requested_order: int,
    exact_reference: float,
) -> Dict[str, object]:
    fit_lin = zne_extrapolate(factors, target_curve_means, order=1)
    fit_quad = zne_extrapolate(factors, target_curve_means, order=2)

    idx_f1 = int(np.argmin(np.abs(np.asarray(factors, dtype=float) - 1.0)))
    baseline_factor = float(factors[idx_f1])
    baseline_value = float(target_curve_means[idx_f1])
    baseline_err = abs(baseline_value - exact_reference)

    lin_est = float(fit_lin["extrapolated_zero_noise"])
    quad_est = float(fit_quad["extrapolated_zero_noise"])
    lin_err = abs(lin_est - exact_reference)
    quad_err = abs(quad_est - exact_reference)

    best_order = 1 if lin_err <= quad_err else 2
    best_est = lin_est if best_order == 1 else quad_est
    best_err = lin_err if best_order == 1 else quad_err

    return {
        "factors": [float(f) for f in factors],
        "baseline_factor_used": baseline_factor,
        "baseline_value": baseline_value,
        "baseline_abs_error_vs_exact": baseline_err,
        "linear": {
            **fit_lin,
            "abs_error_vs_exact": lin_err,
        },
        "quadratic": {
            **fit_quad,
            "abs_error_vs_exact": quad_err,
        },
        "recommended_order": best_order,
        "recommended_extrapolated": best_est,
        "recommended_abs_error_vs_exact": best_err,
        "absolute_error_improvement_vs_baseline": baseline_err - best_err,
        "exact_reference": float(exact_reference),
        "order_requested": int(requested_order),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Black-hole scrambling toy experiment in Qiskit")
    parser.add_argument("--qubits", type=int, default=5, help="Aantal qubits")
    parser.add_argument(
        "--depths",
        type=str,
        default="1,2,3,4,5,6",
        help="Comma-separated lijst met circuitdieptes",
    )
    parser.add_argument("--trials", type=int, default=12, help="Aantal random instances per depth")
    parser.add_argument("--seed", type=int, default=1234, help="Master seed")

    parser.add_argument(
        "--with-noise",
        action="store_true",
        help="Voeg finite-shot noise runs toe (Aer depolarizing + readout).",
    )
    parser.add_argument("--shots", type=int, default=4000, help="Aantal shots per noisy circuit run")
    parser.add_argument("--noise-dep", type=float, default=0.04, help="Depolarizing strength")
    parser.add_argument("--noise-readout", type=float, default=0.02, help="Per-bit readout flip probability")
    parser.add_argument(
        "--readout-mitigation",
        action="store_true",
        help="Apply assignment-matrix readout mitigation op noisy echo metingen",
    )
    parser.add_argument(
        "--mitigation-p-ro",
        type=float,
        default=None,
        help="Readout flip probability voor mitigatie (default: --noise-readout)",
    )
    parser.add_argument(
        "--zne",
        action="store_true",
        help="Run zero-noise extrapolation met noise scaling factors",
    )
    parser.add_argument(
        "--zne-factors",
        type=str,
        default="1,3,5",
        help="Comma-separated noise scaling factors, bv '1,3,5'",
    )
    parser.add_argument(
        "--zne-order",
        type=int,
        default=2,
        help="Gevraagde polynoom-orde voor ZNE fit (lineair/kwadratisch worden beide gerapporteerd)",
    )
    parser.add_argument(
        "--zne-target",
        type=str,
        default="auto",
        choices=["auto", "raw", "readout_mitigated"],
        help="Welke curve te extrapoleren: raw of readout_mitigated (auto kiest mitigated indien actief)",
    )
    parser.add_argument(
        "--noise-seed-offset",
        type=int,
        default=100000,
        help="Offset voor noise seeds t.o.v. trial seeds",
    )

    parser.add_argument("--json-out", type=str, default="", help="Optioneel pad voor JSON output")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.qubits < 2:
        raise ValueError("Gebruik minimaal 2 qubits")
    if args.trials < 1:
        raise ValueError("Gebruik minimaal 1 trial")
    if args.shots < 1:
        raise ValueError("Gebruik minimaal 1 shot")
    if not (0.0 <= args.noise_dep < 1.0):
        raise ValueError("noise-dep moet in [0, 1) liggen")
    if not (0.0 <= args.noise_readout < 1.0):
        raise ValueError("noise-readout moet in [0, 1) liggen")

    depths = parse_depths(args.depths)

    noise_enabled = bool(args.with_noise or args.readout_mitigation or args.zne)
    readout_enabled = bool(args.readout_mitigation)

    mitigation_p_ro = float(args.noise_readout if args.mitigation_p_ro is None else args.mitigation_p_ro)
    if not (0.0 <= mitigation_p_ro < 1.0):
        raise ValueError("mitigation-p-ro moet in [0, 1) liggen")

    zne_target = args.zne_target
    if zne_target == "auto":
        zne_target = "readout_mitigated" if readout_enabled else "raw"
    if zne_target == "readout_mitigated" and not readout_enabled:
        zne_target = "raw"

    factors = parse_noise_factors(args.zne_factors) if args.zne else [1.0]

    master_rng = np.random.default_rng(args.seed)

    summary: Dict[str, object] = {
        "config": {
            "qubits": args.qubits,
            "trials": args.trials,
            "depths": depths,
            "seed": args.seed,
        },
        "results": [],
    }

    noisy_by_depth: List[Dict[str, object]] = []

    print(f"Qubits={args.qubits}, trials/depth={args.trials}, depths={depths}")
    print("metric: mean ± std")
    print(
        "depth | ideal_echo        | pert_echo         | S2 (Renyi-2)      | Re(OTOC)          | C=(1-ReF)/2"
    )

    for depth in depths:
        rows: List[RunResult] = []

        raw_ideal_by_factor: Dict[float, List[float]] = {fac: [] for fac in factors}
        raw_pert_by_factor: Dict[float, List[float]] = {fac: [] for fac in factors}

        mit_ideal_by_factor: Dict[float, List[float]] = {fac: [] for fac in factors}
        mit_pert_by_factor: Dict[float, List[float]] = {fac: [] for fac in factors}

        mode_counts: Dict[str, int] = {}

        for trial in range(args.trials):
            trial_seed = int(master_rng.integers(0, 2**32 - 1))
            result, u_circuit = single_run(
                n_qubits=args.qubits,
                depth=depth,
                seed=trial_seed,
                perturb_qubit=0,
                w_qubit=0,
                v_qubit=args.qubits - 1,
            )
            rows.append(result)

            if noise_enabled:
                for fi, fac in enumerate(factors):
                    dep_scaled = float(np.clip(args.noise_dep * fac, 0.0, 0.999))
                    noise_seed = int(
                        (trial_seed + args.noise_seed_offset + depth * 10007 + fi * 97) % (2**32 - 1)
                    )

                    noisy = run_noisy_echo_pair(
                        u_circuit=u_circuit,
                        n_qubits=args.qubits,
                        perturb_qubit=0,
                        shots=args.shots,
                        seed=noise_seed,
                        p_dep=dep_scaled,
                        p_ro=args.noise_readout,
                        readout_mitigation=readout_enabled,
                        mitigation_p_ro=mitigation_p_ro,
                    )

                    raw = noisy["raw"]
                    raw_ideal_by_factor[fac].append(float(raw["ideal_echo"]))
                    raw_pert_by_factor[fac].append(float(raw["perturbed_echo"]))

                    if readout_enabled:
                        mit = noisy["readout_mitigated"]
                        mit_ideal_by_factor[fac].append(float(mit["ideal_echo"]))
                        mit_pert_by_factor[fac].append(float(mit["perturbed_echo"]))

                    for mode, cnt in noisy["backend_modes"].items():
                        mode_counts[mode] = mode_counts.get(mode, 0) + int(cnt)

        ideal_m, ideal_s = mean_std([r.ideal_echo for r in rows])
        pert_m, pert_s = mean_std([r.perturbed_echo for r in rows])
        s2_m, s2_s = mean_std([r.renyi2 for r in rows])
        otoc_m, otoc_s = mean_std([r.otoc_real for r in rows])
        comm_m, comm_s = mean_std([r.commutator_sq for r in rows])

        print(
            f"{depth:>5d} | "
            f"{ideal_m:8.5f}±{ideal_s:7.5f} | "
            f"{pert_m:8.5f}±{pert_s:7.5f} | "
            f"{s2_m:8.5f}±{s2_s:7.5f} | "
            f"{otoc_m:8.5f}±{otoc_s:7.5f} | "
            f"{comm_m:8.5f}±{comm_s:7.5f}"
        )

        summary["results"].append(
            {
                "depth": depth,
                "ideal_echo": {"mean": ideal_m, "std": ideal_s},
                "perturbed_echo": {"mean": pert_m, "std": pert_s},
                "renyi2": {"mean": s2_m, "std": s2_s},
                "otoc_real": {"mean": otoc_m, "std": otoc_s},
                "commutator_sq": {"mean": comm_m, "std": comm_s},
                "samples": [asdict(r) for r in rows],
            }
        )

        if noise_enabled:
            idx_f1 = int(np.argmin(np.abs(np.asarray(factors, dtype=float) - 1.0)))
            baseline_factor = float(factors[idx_f1])

            raw_curve_ideal = curve_summary(raw_ideal_by_factor, factors)
            raw_curve_pert = curve_summary(raw_pert_by_factor, factors)

            noisy_entry: Dict[str, object] = {
                "depth": depth,
                "backend_modes": mode_counts,
                "baseline_factor_used": baseline_factor,
                "raw": {
                    "ideal_echo": {
                        "curve": raw_curve_ideal,
                        "baseline": raw_curve_ideal[idx_f1],
                    },
                    "perturbed_echo": {
                        "curve": raw_curve_pert,
                        "baseline": raw_curve_pert[idx_f1],
                    },
                },
            }

            if readout_enabled:
                mit_curve_ideal = curve_summary(mit_ideal_by_factor, factors)
                mit_curve_pert = curve_summary(mit_pert_by_factor, factors)
                noisy_entry["readout_mitigated"] = {
                    "ideal_echo": {
                        "curve": mit_curve_ideal,
                        "baseline": mit_curve_ideal[idx_f1],
                    },
                    "perturbed_echo": {
                        "curve": mit_curve_pert,
                        "baseline": mit_curve_pert[idx_f1],
                    },
                }

            if args.zne:
                if zne_target == "readout_mitigated":
                    target_ideal_means = [
                        float(np.mean(mit_ideal_by_factor[fac]))
                        for fac in factors
                    ]
                    target_pert_means = [
                        float(np.mean(mit_pert_by_factor[fac]))
                        for fac in factors
                    ]
                else:
                    target_ideal_means = [
                        float(np.mean(raw_ideal_by_factor[fac]))
                        for fac in factors
                    ]
                    target_pert_means = [
                        float(np.mean(raw_pert_by_factor[fac]))
                        for fac in factors
                    ]

                noisy_entry["zne"] = {
                    "target": zne_target,
                    "ideal_echo": metric_zne_summary(
                        factors=factors,
                        target_curve_means=target_ideal_means,
                        requested_order=args.zne_order,
                        exact_reference=ideal_m,
                    ),
                    "perturbed_echo": metric_zne_summary(
                        factors=factors,
                        target_curve_means=target_pert_means,
                        requested_order=args.zne_order,
                        exact_reference=pert_m,
                    ),
                }

            noisy_by_depth.append(noisy_entry)

    if noise_enabled:
        print("")
        print("Noisy echoes @ baseline factor (f~1):")
        if readout_enabled:
            print(
                "depth | raw_ideal         | raw_pert          | mit_ideal         | mit_pert"
            )
        else:
            print("depth | raw_ideal         | raw_pert")

        for entry in noisy_by_depth:
            depth = int(entry["depth"])
            raw_i = entry["raw"]["ideal_echo"]["baseline"]
            raw_p = entry["raw"]["perturbed_echo"]["baseline"]

            if readout_enabled:
                mit_i = entry["readout_mitigated"]["ideal_echo"]["baseline"]
                mit_p = entry["readout_mitigated"]["perturbed_echo"]["baseline"]
                print(
                    f"{depth:>5d} | "
                    f"{raw_i['mean']:8.5f}±{raw_i['std']:7.5f} | "
                    f"{raw_p['mean']:8.5f}±{raw_p['std']:7.5f} | "
                    f"{mit_i['mean']:8.5f}±{mit_i['std']:7.5f} | "
                    f"{mit_p['mean']:8.5f}±{mit_p['std']:7.5f}"
                )
            else:
                print(
                    f"{depth:>5d} | "
                    f"{raw_i['mean']:8.5f}±{raw_i['std']:7.5f} | "
                    f"{raw_p['mean']:8.5f}±{raw_p['std']:7.5f}"
                )

        backend_modes_total: Dict[str, int] = {}
        for entry in noisy_by_depth:
            for mode, count in entry["backend_modes"].items():
                backend_modes_total[mode] = backend_modes_total.get(mode, 0) + int(count)

        print("")
        print(f"Noisy backend usage: {backend_modes_total}")

        if args.zne:
            print("")
            print(f"ZNE summary (target={zne_target})")
            print("depth | metric         | baseline|err|   | best@0noise|err|  | best order | improvement")
            for entry in noisy_by_depth:
                depth = int(entry["depth"])
                zne = entry["zne"]
                for metric in ("ideal_echo", "perturbed_echo"):
                    item = zne[metric]
                    print(
                        f"{depth:>5d} | "
                        f"{metric:<13} | "
                        f"{item['baseline_abs_error_vs_exact']:12.8f} | "
                        f"{item['recommended_abs_error_vs_exact']:12.8f} | "
                        f"{item['recommended_order']:>10d} | "
                        f"{item['absolute_error_improvement_vs_baseline']:11.8f}"
                    )

        summary["noise"] = {
            "enabled": True,
            "config": {
                "shots": args.shots,
                "noise_dep": args.noise_dep,
                "noise_readout": args.noise_readout,
                "readout_mitigation": readout_enabled,
                "mitigation_p_ro_effective": mitigation_p_ro,
                "zne": bool(args.zne),
                "zne_factors": [float(f) for f in factors],
                "zne_order_requested": int(args.zne_order),
                "zne_target_effective": zne_target,
            },
            "per_depth": noisy_by_depth,
        }

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        print(f"\nJSON opgeslagen in: {args.json_out}")


if __name__ == "__main__":
    main()
