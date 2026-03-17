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
| `P` | Pauli-specialized fixed observable before Hilbert-Schmidt normalization | default lock `Z_0` for the first q14 benchmark | dimensionless | Phase 1 formalism lock |
| `O` | fixed observable used in OLE | normalized so `Tr(O^2)=1` | dimensionless | project initialization |
| `G` | generator of the perturbation unitary | chosen explicitly per benchmark | dimensionless | project initialization |
| `V_delta` | perturbation unitary `exp(-i delta G)` | small-`delta` regime first | unitary operator | project initialization |
| `delta` | perturbation strength | small positive benchmark window | dimensionless | project initialization |
| `F_delta(P)` | report-level Pauli-specialized OLE curve `2^-n Tr(U P U^dagger V_delta^dagger U P U^dagger V_delta)` | primary q14 plotting quantity with `F_0(P)=1` for Pauli `P` | dimensionless | Phase 1 bridge lock |
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
| `PLE` | Pauli Loschmidt Echo | optional later label for the Pauli-specialized `F_delta(P)` branch; not the primary project term yet |
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
| `A_P(U)` | primary evolved Pauli observable `U P U^dagger` | this is the fixed picture used for the first q14 bridge |
| `A_O(U)` | normalized evolved observable `U O U^dagger` | equals `A_P(U) / sqrt(2^n)` for the locked benchmark |
| `kappa_G(P;U)` | quadratic small-`delta` coefficient `2^-n Tr([G,A_P][G,A_P]^dagger)` | governs `F_delta(P) = 1 - (delta^2/2) kappa_G + O(delta^4)` |
| `tilde G(U)` | rotated generator `U^dagger G U` in the alternate `U^dagger O U` picture | must be rotated if the observable picture is rotated |

## Potential Conflicts

| Symbol / Term | Meaning 1 | Meaning 2 | Resolution |
| ------------- | --------- | --------- | ---------- |
| `O(t)` | evolved observable in one picture | evolved observable in the opposite picture | always state which defining OLE expression is primary before rewriting |
| `F_delta(P)` vs `f_delta(O)` | unit-intercept Pauli-specialized reporting quantity | Hilbert-Schmidt-normalized OLE | use `F_delta(P)` for figures and report `f_delta(O) = 2^-n F_delta(P)` explicitly when needed |
| `perturbed_echo` vs `OLE` | state-return baseline | fixed-observable operator correlator | keep the names separate; `perturbed_echo` is a baseline, not a synonym |
| subset signal | local / subset observable result | full-system scrambling claim | never drop the subset support label from q80 artifacts |

---

_Notation glossary created: 2026-03-17_
