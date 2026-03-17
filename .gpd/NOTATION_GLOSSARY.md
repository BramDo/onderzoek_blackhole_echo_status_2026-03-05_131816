# Notation Glossary

**Analysis Date:** 2026-03-17
**Last Updated:** 2026-03-17

## Hilbert Space and Circuit Objects

| Symbol | Meaning | Units | Defined In |
| ------ | ------- | ----- | ---------- |
| `n` | total qubit count | dimensionless | project initialization |
| `d` | brickwork circuit depth | dimensionless | project initialization |
| `U` | scrambling unitary / brickwork scrambler | unitary operator | current q14/q80 workflow |
| `U^dagger` | inverse of the scrambling unitary | unitary operator | current q14/q80 workflow |
| `|psi0>` | prepared reference state, typically `|0...0>` | normalized state | current q14/q80 workflow |

## Observables and Perturbations

| Symbol | Meaning | Value / Range | Units | Defined In |
| ------ | ------- | ------------- | ----- | ---------- |
| `O` | fixed observable used in OLE | normalized so `Tr(O^2)=1` | dimensionless | project initialization |
| `G` | generator of the perturbation unitary | chosen explicitly per benchmark | dimensionless | project initialization |
| `V_delta` | perturbation unitary `exp(-i delta G)` | small-`delta` regime first | unitary operator | project initialization |
| `delta` | perturbation strength | small positive benchmark window | dimensionless | project initialization |
| `f_delta(O)` | operator Loschmidt echo for fixed `O` | scalar in benchmarked regimes | dimensionless | project initialization |
| `perturbed_echo` | repo baseline state-return quantity `|<psi0|U^dagger X U|psi0>|^2` | scalar baseline | dimensionless | existing workflow |
| `S` | subset support of a measured observable | explicit subset of qubit labels | dimensionless | q80 subset route |
| `q_p` | perturbation qubit / perturbation support label | explicit qubit or support set | dimensionless | locality controls |

## Indices

| Index | Range | Convention | Example |
| ----- | ----- | ---------- | ------- |
| `q` | `0,1,...,n-1` | qubit index in Qiskit ordering | `q = 10` |
| `S` | subset of `{0,...,n-1}` | measured support set, always stated explicitly | `S = {10,...,19}` |

## Abbreviations and Acronyms

| Abbreviation | Full Term | Context |
| ------------ | --------- | ------- |
| `OLE` | Operator Loschmidt Echo | fixed-observable target of this project |
| `OTOC` | Out-of-Time-Ordered Correlator | operator-growth comparison target |
| `LE` | Loschmidt Echo | broader echo language |
| `PLE` | Pauli Loschmidt Echo | possible later label for a Pauli-specialized branch |
| `MAE` | Mean Absolute Error | current q14 hardware benchmark accuracy metric |

## Fourier Transform Convention

No active Fourier-transform notation is central to the current circuit benchmark.

If later introduced, use the `physics` convention locked in `.gpd/CONVENTIONS.md`.

## Special Functions and Notation

| Notation | Meaning | Notes |
| -------- | ------- | ----- |
| `Tr(...)` | operator trace | OLE uses normalized trace factors explicitly |
| `[A,B]` | commutator `AB - BA` | enters the small-`delta` OLE expansion |
| `(...)^dagger` | Hermitian conjugate | used for `U^dagger` and `V_delta^dagger` |
| `~=` | asymptotic / small-parameter approximation | used in the small-`delta` expansion |

## Potential Conflicts

| Symbol / Term | Meaning 1 | Meaning 2 | Resolution |
| ------------- | --------- | --------- | ---------- |
| `O(t)` | evolved observable in one picture | evolved observable in the opposite picture | always state which defining OLE expression is primary before rewriting |
| `perturbed_echo` vs `OLE` | state-return baseline | fixed-observable operator correlator | keep the names separate; `perturbed_echo` is a baseline, not a synonym |
| subset signal | local / subset observable result | full-system scrambling claim | never drop the subset support label from q80 artifacts |

---

_Notation glossary created: 2026-03-17_
