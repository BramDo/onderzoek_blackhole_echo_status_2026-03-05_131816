# Technical Note: Signal-Scale Snapshot Across q14/q20/q24/q32/q80

Generated: 2026-03-21

## Scope

This note is a narrow technical basis document for the current hardware evidence snapshot. It is not the full article draft and it does not attempt a full black-hole / OLE interpretation layer yet.

The purpose here is only:

- to record a consistent cross-scale signal snapshot
- to show where the signal clearly sits above pure noise
- to keep the claim boundary explicit

## Artifacts

Primary artifacts for this note:

- `results/hardware/summary/signal_above_noise_scale_plot_2026-03-21.png`
- `results/hardware/summary/signal_above_noise_scale_plot_2026-03-21.json`
- `results/hardware/phase3_q14_zne_xsup_s8000_f135_localfold.json`
- `results/hardware/phase3_q24_SA_q0_raw_vs_mit.json`
- `results/hardware/phase3_q24_SA_q23_raw_vs_mit.json`
- `results/hardware/phase3_q32_SA_q0_raw_vs_mit.json`
- `results/hardware/phase3_q32_SA_q31_raw_vs_mit.json`
- `results/hardware/phase3_q80pilot_SA_q0_raw_vs_mit.json`
- `results/hardware/phase3_q80pilot_SA_q79_raw_vs_mit.json`
- `results/hardware/bonus_full_q80_2026-03-21/depth2_paired_blockz_reuse/full_q80_q0_q79_paired_t5_blockz_front10_back10.json`

## Metric Definitions

Three related but not identical signal metrics are used in the plot:

1. Subset-proxy signal at q20/q24/q32/q80:
   `signal = far-disjoint perturbed_subset_echo - overlap perturbed_subset_echo`
   using the readout-mitigated shallow subset observable.

2. q14 checkpoint signal:
   `signal = overlap - disjoint`
   using the corrected local-fold checkpoint ZNE estimate at fixed depth.

3. 80q exploratory full-register bonus signal:
   `signal = |median paired block-Z linear-return delta|`
   from the depth-2 `front10/back10` reuse analysis.

These should be read together as a scale snapshot, not as one perfectly uniform observable family.

## Main Table

| System | Regime | Depth | Signal |
| --- | --- | ---: | ---: |
| q14 | checkpoint ZNE | 2 | 0.27957 |
| q20 | subset-proxy | 1 | 0.98326 |
| q20 | subset-proxy | 2 | 0.66936 |
| q24 | subset-proxy | 1 | 0.98216 |
| q24 | subset-proxy | 2 | 0.86030 |
| q32 | subset-proxy | 1 | 0.98712 |
| q32 | subset-proxy | 2 | 0.66240 |
| q80 | subset-proxy pilot | 1 | 0.98420 |
| q80 | subset-proxy pilot | 2 | 0.89110 |
| q80 | full-register bonus block-Z | 2 | 0.09418 |

## Immediate Readout

What the plot shows:

- The subset-proxy locality signal remains very large from q20 through q80 at depth 1.
- The same subset-proxy signal remains clearly positive at depth 2 on all recorded scales.
- The q80 subset pilot is not weaker than the intermediate scales; in this snapshot it remains one of the cleanest shallow-depth separations.
- The stricter q14 checkpoint metric is smaller but still clearly positive at depth 2.
- The exploratory q80 full-register bonus track is much smaller than the subset line, but it does not collapse to zero; the block-local reuse still retains a visible structured signal.

## Interpretation Boundary

This note supports the following narrow wording:

- `signal above pure noise is visible across the subset-proxy scale-up path to 80 qubits`
- `the exploratory full-register 80q bonus track retains a smaller but nonzero structured locality signal`

This note does **not** support:

- full-q80 OLE closure
- global-q80 hardware confirmation
- direct one-to-one quantitative comparison between the q14 checkpoint metric and the subset-proxy line as if they were the same observable

## Why The 80q Bonus Point Is Smaller

The 80q bonus marker is intentionally harder:

- it is full-register rather than subset-proxy
- it comes from a block-`Z` fallback observable instead of the subset-echo observable
- it is reported as a robust median paired delta rather than a more forgiving branch-mean contrast

So the fact that it still remains positive is informative. The right reading is not `80q full-register is weak`, but rather `even after moving to a stricter full-register-like observable family, the signal does not disappear completely`.

## Technical Bottom Line

The cleanest current basis statement is:

> Across q20, q24, q32, and q80, the shallow-depth subset-proxy hardware signal remains far above a pure-noise baseline, while the exploratory 80q full-register bonus analysis retains a smaller but still structured residual locality signal.

That sentence is narrow enough for a technical report and strong enough to serve as the basis for a later longer article.

## Next Writing Step

This note is the basis document for a second-stage write-up that can add:

- the black-hole / scrambling / OLE interpretation layer
- the explicit formulas
- the connection between overlap, echo, locality controls, and the chosen observables
- the broader literature context and references
