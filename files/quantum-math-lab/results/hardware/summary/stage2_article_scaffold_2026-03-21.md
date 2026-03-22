# Stage-2 Article Scaffold: From Echo Benchmarks to OLE-Motivated Scrambling Evidence

Generated: 2026-03-21

## Purpose

This document is the next writing layer above:

- `signal_scale_technical_note_2026-03-21.md`
- `signal_above_noise_scale_plot_2026-03-21.png`
- `signal_above_noise_scale_plot_2026-03-21.json`

It is not yet the final article. The goal is to provide a semi-filled scaffold that can later be expanded into a full paper-style narrative with all technical and conceptual layers.

## Candidate Titles

Conservative:

- `Cross-scale locality signal in echo-based scrambling benchmarks from q14 to q80`
- `From q14 checkpoints to q80 subset locality: a staged hardware signal report`
- `Exploratory echo and block-local scrambling evidence across q14-q80 hardware benchmarks`

More ambitious but still safe:

- `Toward operator Loschmidt echo on hardware: staged locality evidence from q14 to q80`
- `Echo-based locality structure across q14-q80 hardware benchmarks on the path toward fixed-observable OLE`

## One-Paragraph Abstract Draft

We report a staged signal snapshot across q14, q20, q24, q32, and q80 echo-based hardware benchmarks, with emphasis on locality-sensitive overlap-versus-far-disjoint controls. The strongest large-system evidence remains subset-proxy: for q20, q24, q32, and q80, shallow-depth readout-mitigated subset contrasts remain large and positive, indicating a signal clearly above pure noise under fixed control geometry. At q14, the best admissible fixed-branch hardware checkpoint remains the corrected local-fold ZNE separation at depth 2. At q80, an exploratory full-register bonus analysis using a block-`Z` fallback observable yields a smaller but still structured residual locality signal. We interpret these results as strong staged continuity for locality-sensitive echo observables across scale, while keeping the distinction explicit between current echo-family observables, subset-level diagnostics, and the still-unresolved full fixed-observable OLE target.

## Extended Abstract Draft

The present work does not begin from a blank slate. The repo already contains a frozen q14 echo benchmark, a hardware runner for overlap and disjoint perturbation placement, and a scale-up path to q80 through subset observables. The main challenge is therefore not to invent a new benchmark family, but to interpret the existing family rigorously and carry it forward without overclaim drift. Our approach is to separate three layers of evidence. First, at q14 we use the best admissible checkpoint-level hardware signal, namely corrected local-fold zero-noise extrapolation on the overlap-versus-disjoint branch pair. Second, at q20, q24, q32, and q80 we use readout-mitigated subset-proxy contrasts between overlap and far-disjoint control branches. Third, at q80 we supplement the subset line with an exploratory full-register bonus analysis based on block-local `Z` observables, which are stricter than the subset echo but still physically interpretable. Across these layers, we observe a consistent pattern: the locality-sensitive signal is large and stable along the subset scale-up path and remains detectably structured even in the stricter 80q full-register bonus view. The current evidence therefore supports a strong staged locality narrative, but not yet a full-q80 fixed-observable OLE claim.

## Suggested Section Structure

### 1. Introduction

Draft opening paragraph:

Information scrambling is often discussed through OTOCs, Loschmidt echoes, and related recovery diagnostics, but the practical challenge on hardware is to turn these conceptual links into observables that remain both scalable and interpretable under realistic noise. The present project starts from an existing echo-style benchmark workflow rather than from an abstract OTOC protocol. The central question is therefore not whether scrambling can be probed in principle, but whether the current echo-family hardware observables already show locality-sensitive structure that is stable enough to justify a careful bridge toward operator Loschmidt echo (OLE).

Draft second paragraph:

The answer must be staged. A frozen q14 benchmark allows stronger checkpoint-level interpretation, while larger systems require subset observables and explicit control geometry. This naturally leads to a ladder of evidence: q14 checkpoint separation, q20-q80 subset-proxy locality contrasts, and finally exploratory full-register q80 diagnostics. The main contribution of the current write-up is to show that this ladder carries a nontrivial signal above pure noise across scale, while remaining explicit about the gap between the present observables and a final fixed-observable OLE implementation.

### 2. Observable Ladder and Interpretation Discipline

Key paragraph:

The observables in this project should be read as a ladder rather than as interchangeable quantities. The current `perturbed_echo` is a state-return baseline quantity. The subset-proxy observable promotes that baseline into a locality-sensitive support diagnostic on a fixed measured subset. The block-`Z` full-register bonus observable then moves part of the analysis toward a more operator-like, diagonal-in-`Z` family. Only after these layers are separated does it become meaningful to discuss the final fixed-observable OLE target. This ladder is essential: it preserves continuity with the data while blocking semantic drift.

Suggested boxed statement:

> Current echo-family observables are not yet identical to the final OLE observable, but they form a structured bridge toward it when interpreted through explicit support controls and fixed observable families.

### 3. Theoretical Framework and Minimal Formalism

Draft framing paragraph:

The paper should make one convention choice explicit up front and never silently drift away from it. In the project notation, `perturbed_echo` remains the state-return baseline `|<psi0|U^dagger X U|psi0>|^2` and must not be relabeled as OLE. The fixed-observable target is instead the Pauli-specialized report-level OLE curve `F_delta(P)` together with its Hilbert-Schmidt-normalized translation `f_delta(O)`. This is the clean bridge between the existing hardware workflow and the later operator-growth interpretation.

Recommended notation paragraph:

We use the project's locked operator picture

```math
A_P(U) = U P U^\dagger,
```

with Pauli-specialized report quantity

```math
F_\delta(P) = 2^{-n}\mathrm{Tr}\!\left(A_P(U)\,V_\delta^\dagger\,A_P(U)\,V_\delta\right),
\qquad
V_\delta = e^{-i\delta G},
```

and Hilbert-Schmidt-normalized observable

```math
O = \frac{P}{\sqrt{2^n}},
\qquad
f_\delta(O) = 2^{-n}F_\delta(P).
```

This keeps the unit-intercept benchmark `F_0(P)=1` while preserving the normalized observable language when needed.

Current echo-family baseline:

```math
E_q(U) = |\langle 0^n | U^\dagger X_q U | 0^n \rangle|^2
```

where `q` labels the perturbation site and the overlap-versus-disjoint comparison is implemented by changing the relative location of `q` and the measured support.

Operator-growth bridge:

```math
A_P(U) = \sum_Q c_Q(U;P)\,Q,
\qquad
\sum_Q |c_Q(U;P)|^2 = 1
```

for an initial Pauli string `P`. This Pauli expansion is the cleanest formal bridge between the current echo ladder and operator spreading: the coefficients `|c_Q|^2` act like a probability distribution over Pauli strings.

Support geometry:

```math
\mathrm{supp}(Q) = \{r \in \{0,\dots,n-1\} \;|\; Q_r \neq I\},
\qquad
\mathrm{dist}(q_p,S) = \min_{r\in S} |q_p-r|.
```

The support-sensitive control logic then asks how much of the evolved operator lands on or near a measured region `S` when the perturbation support is moved from overlap to far-disjoint placements.

Operator-support density:

```math
\rho(r;U,P)
=
\sum_{Q:\,r\in\mathrm{supp}(Q)}
\frac{|c_Q(U;P)|^2}{|\mathrm{supp}(Q)|}.
```

Interpretive sentence:

The quantity `rho(r;U,P)` is the formal object that the overlap-versus-far-disjoint controls are probing indirectly. The current subset and block observables are therefore not arbitrary diagnostics; they are experimentally accessible surrogates for where the evolved operator weight is geometrically concentrated.

Subset-proxy signal:

```math
\Delta_S = \tilde p_{\mathrm{far}}(S) - \tilde p_{\mathrm{overlap}}(S)
```

where `S` is the measured subset and `\tilde p` denotes the readout-mitigated subset-return statistic.

Practical support-proxy refinement:

```math
\Delta_S(d;q_p)
=
\tilde p(S\,|\,d,q_p\in\mathrm{far})
-
\tilde p(S\,|\,d,q_p\in\mathrm{overlap}),
```

so that the depth and perturbation placement are both explicit. This is the quantity that generates the strong q20-q80 scale-up line in the current report.

Block-`Z` fallback observable:

```math
M_B = \frac{1}{|B|}\sum_{q \in B} Z_q,
\qquad
R_B = \frac{1 + \langle M_B \rangle}{2}
=
1 - \frac{1}{|B|}\sum_{q \in B} p_q(1)
```

with paired block contrast

```math
\Delta_B = R_B^{(\mathrm{far})} - R_B^{(\mathrm{overlap})}.
```

Interpretive sentence:

The block-`Z` observable is not the final OLE, but it is already closer to a fixed observable family than the raw state-return signal. That is why it is the right full-register fallback for the present bonus track.

Fixed-observable OLE target:

```math
F_\delta(P) = 2^{-n}\mathrm{Tr}\!\left(A_P(U)\,V_\delta^\dagger\,A_P(U)\,V_\delta\right)
```

and normalized signal

```math
f_\delta(O) = 2^{-n} F_\delta(P).
```

Small-`delta` onset:

```math
F_\delta(P)
=
1
-
\frac{\delta^2}{2}\,
\kappa_G(P;U)
+
O(\delta^4),
```

with

```math
\kappa_G(P;U)
=
2^{-n}\mathrm{Tr}\!\left([G,A_P(U)][G,A_P(U)]^\dagger\right).
```

Equivalently, in normalized notation,

```math
f_\delta(O)
\approx
2^{-n}
\left[
1
-
\frac{\delta^2}{2}\,
\kappa_G(P;U)
\right].
```

Interpretive sentence:

This is the precise OTOC bridge: the initial quadratic decay of OLE is governed by the commutator norm of the evolved observable with the perturbation generator. The current hardware observables do not yet reconstruct `f_delta(O)` directly, but they test whether the same support-sensitive operator-growth logic survives in hardware before the final OLE estimator is fully closed.

Recommended theory paragraph:

The paper should be explicit that the present q20-q80 subset results are not "poor man's OTOCs." They are support-sensitive echo diagnostics whose meaning comes from the same operator-growth geometry that appears in the commutator expression above. This is strong enough for a staged scrambling claim, but narrow enough to avoid semantic drift.

### 4. Why Overlap Versus Far-Disjoint Controls Matter

Draft text:

The overlap-versus-far-disjoint comparison is the core anti-noise control in this workflow. If the observed contrast were only a generic decay artifact, then moving the perturbation site relative to the measured support would not systematically restore a large branch separation. In contrast, when the signal is locality-sensitive, overlap branches remain strongly affected while far-disjoint controls remain comparatively clean. This logic is exactly what makes the subset-proxy line meaningful: the signal is not merely “nonzero,” but spatially structured under controlled support variation.

### 5. Main Results Narrative

#### 5.1 q14 checkpoint anchor

Draft text:

The strongest admissible q14 hardware anchor is the corrected local-fold checkpoint ZNE separation. At depth 2 the overlap-minus-disjoint signal is `0.27957`, which is smaller than the later subset-proxy line but still clearly positive. This is the best current q14 hardware anchor because it uses the stricter checkpoint-level mitigation discipline rather than the broader and more mixed whole-grid raw-vs-mitigated picture.

#### 5.2 q20-q80 subset-proxy scale-up

Draft text:

The cross-scale subset line is the main result of the current hardware report. At depth 1 the readout-mitigated far-minus-overlap contrast is near `0.98` for q20, q24, q32, and q80. At depth 2 the signal decreases but remains strongly positive at every scale. The q80 result here is specifically the first `S_A = 0..9` subset pilot rather than symmetric whole-machine coverage, but even with that narrower scope it does not collapse relative to intermediate sizes and remains among the strongest shallow-depth subset contrasts. This is the cleanest evidence that locality-sensitive signal survives the scale-up path to 80 qubits in the subset-observable sense.

#### 5.3 Exploratory q80 full-register bonus track

Draft text:

The exploratory q80 full-register bonus path is intentionally harder than the subset line. Global full-register state-return observables were fragile and mitigation-sensitive, so the stronger follow-up was a block-local `Z` fallback on the same paired capture. This produces a smaller signal, with a symmetric mirrored-block marker of `0.10932` defined as the mean absolute median delta across `front10` and `back10`, but crucially it remains structured rather than null. Moreover, the sign pattern is spatially correct: a perturbation near `q=0` primarily suppresses the `front10` block, while a perturbation near `q=79` suppresses the `back10` block. The right interpretation is not that the full-register route is “as strong” as the subset route, but that it still retains locality structure after a stricter observable change.

### 6. Figure Caption Draft

Suggested caption for the current plot:

> Cross-scale snapshot of locality-sensitive signal magnitude across q14, q20, q24, q32, and q80. Blue and red lines show the readout-mitigated subset-proxy far-minus-overlap contrast at depths 1 and 2. The green marker shows the corrected local-fold q14 checkpoint ZNE overlap-minus-disjoint signal at depth 2, selected as the cleanest checkpoint within a broader mixed q14 hardware picture. The q80 subset point is the first `S_A = 0..9` pilot only. The purple marker shows the exploratory 80q full-register bonus signal based on the symmetric mean absolute paired block-`Z` linear-return delta across `front10` and `back10`. The plot should be read as a staged evidence ladder rather than as a single observable family.

### 7. Claim Boundary Section

Suggested paragraph:

The present evidence supports strong subset-level locality language and a weaker full-register exploratory locality language, but it does not support full-q80 OLE closure, global-q80 hardware confirmation, or a claim that the current observables already implement the final fixed-observable OLE estimator. The disciplined reading is therefore two-tiered: strong subset-proxy continuity through q80, and a smaller but nonzero structured residual signal in the stricter 80q full-register bonus analysis.

### 8. Discussion Bridge to Black-Hole / Scrambling Language

Draft text:

The black-hole motivation enters here as an interpretation layer, not as a license to rename the current observables. In black-hole and fast-scrambler language, the relevant physical picture is that a local perturbation rapidly spreads across many degrees of freedom so that recovery of its footprint becomes support- and time-dependent. The present circuits are not gravity duals and do not directly test a black-hole model. What they do test is the hardware-visible remnant of the same mechanism: local perturbations affect nearby measured supports strongly, affect far-disjoint supports much less, and gradually erase that geometric distinction as scrambling proceeds. This is exactly why overlap-versus-far-disjoint controls matter.

Recommended black-hole paragraph:

The right bridge sentence is therefore modest but meaningful: black-hole scrambling motivates the question, OLE provides the clean operator-space target, and the present echo ladder provides hardware evidence that the underlying locality-sensitive signal survives across scale. That is enough for a staged article. It is not enough for a direct gravity-style claim or a statement that the present `perturbed_echo` itself already is the final OLE observable.

### 9. Curated References and How To Use Them

#### 9.1 Black-hole and fast-scrambling motivation

- Patrick Hayden and John Preskill, `Black holes as mirrors: quantum information in random subsystems`, JHEP 09 (2007) 120. Use for the retrieval/scrambling motivation and the "rapidly mixing" black-hole information picture. Primary source: [arXiv:0708.4025](https://arxiv.org/abs/0708.4025).
- Yasuhiro Sekino and Leonard Susskind, `Fast Scramblers`, JHEP 10 (2008) 065. Use for the fast-scrambler timescale narrative and the black-hole motivation layer. Primary source: [arXiv:0808.2096](https://arxiv.org/abs/0808.2096).
- Juan Maldacena, Stephen H. Shenker, and Douglas Stanford, `A bound on chaos`, JHEP 08 (2016) 106. Use only for the chaos/OTOC ceiling language, not as if the current experiment directly saturates or tests the MSS bound. Primary source: [arXiv:1503.01409](https://arxiv.org/abs/1503.01409).

#### 9.2 Echo, OTOC, and operator-growth bridge

- Bin Yan, Lukasz Cincio, and Wojciech H. Zurek, `Information Scrambling and Loschmidt Echo`, Phys. Rev. Lett. 124, 160603 (2020). This is the cleanest citation for the OTOC/Loschmidt-echo bridge. Primary source: [arXiv:1903.02651](https://arxiv.org/abs/1903.02651).
- `Loschmidt echo for probing operator hydrodynamics in heterogeneous structures`, Algorithmiq theory note. Use for the operator-support-density viewpoint, the OLE measurement framing, and the explicit OLE-to-OTOC small-`delta` bridge that best matches the present project's target notation. Primary source: [PDF](https://algorithmiq.fi/files/model-information-flow-complex-material-document.pdf).
- Simon Karch et al., `Probing quantum many-body dynamics using subsystem Loschmidt echos` (2025). Use as a modern reference for why subsystem or quasi-local Loschmidt-style observables are scientifically meaningful even when the full-system Loschmidt echo is too hard or too small. Primary source: [arXiv:2501.16995](https://arxiv.org/abs/2501.16995).

#### 9.3 Experimental scrambling diagnostics

- Benoit Vermersch, Andreas Elben, Lukas M. Sieberer, Norman Y. Yao, and Peter Zoller, `Probing scrambling using statistical correlations between randomized measurements`. Use for experimentally accessible scrambling diagnostics that avoid explicit backward evolution. Primary source: [arXiv:1807.09087](https://arxiv.org/abs/1807.09087).
- Xiao Mi et al., `Information scrambling in quantum circuits`, Science 374, 1479-1483 (2021). Use for the large-device experimental scrambling benchmark and for the distinction between operator spreading and operator entanglement. Primary sources: [PubMed abstract](https://pubmed.ncbi.nlm.nih.gov/34709938/) and [arXiv:2101.08870](https://arxiv.org/abs/2101.08870).

#### 9.4 Observable and subsystem framing

- Faidon Andreadakis, Emanuel Dallas, and Paolo Zanardi, `Long-time Quantum Scrambling and Generalized Tensor Product Structures` (2023). Use when the article wants a more algebraic or subalgebra-sensitive notion of scrambling instead of an entirely state-centric one. Primary source: [arXiv:2312.13386](https://arxiv.org/abs/2312.13386).
- If the article later leans harder on the subset/block observable route, explicitly connect those observables to subsystem or subalgebra probes rather than presenting them as ad hoc engineering choices.

#### 9.5 Mitigation and utility-scale execution context

- Sergey Filippov, Michael Leahy, Maria A. C. Rossi, and G. Garcia-Perez, `Scalable tensor-network error mitigation for near-term quantum computing` (2023). Use for the tensor-network mitigation context that motivated the TEM/TEM-like discussion. Current project relevance: mitigation layer, not the core physics claim.
- Sergey N. Filippov, Sabrina Maniscalco, and G. Garcia-Perez, `Scalability of quantum error mitigation techniques: from utility to advantage` (2024). Use for a broad mitigation-limit discussion if the full article needs one.

Recommended usage rule:

The paper should treat these references as a layered bibliography. Hayden-Preskill and Sekino-Susskind motivate the problem. Yan-Cincio-Zurek and the Algorithmiq OLE note define the closest formal bridge. Vermersch and Mi give experimental scrambling context. Karch gives cover for subsystem-style observables. The mitigation papers belong in methods/discussion, not in the central physics claim.

### 10. Ready-To-Use Closing Paragraph

The present hardware evidence does not yet close the full fixed-observable OLE question, but it establishes a strong and useful intermediate result. Across q20, q24, q32, and q80, shallow-depth subset-proxy locality signals remain far above a pure-noise baseline, while a stricter 80q full-register bonus analysis retains a smaller but still structured residual locality signature. This gives a coherent staged basis for a later full OLE-oriented write-up: the hardware signal is already there, but the final observable semantics still need to be completed explicitly.

## What To Add Next

To turn this scaffold into the longer article, the next pass should add:

- a proper abstract and introduction in final prose
- one polished notation table that exactly matches `.gpd/NOTATION_GLOSSARY.md`
- one results section built directly from the technical note and plot JSON
- one discussion section linking the current observables to the final OLE target
- bibliography formatting in the target journal style
