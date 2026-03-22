# Bonus Full-Q80 Exploratory Track

Date: 2026-03-21
Status: executed additive path

This folder is reserved for a **bonus full-register q80 exploratory run**. It exists to keep every earlier file and result intact while trying a wider 80-qubit path in a separate output line.

## Non-destructive contract

- Do not overwrite existing `phase3_q80*`, `phase3_q32*`, `phase3_q24*`, or q14 phase-3 artifacts.
- Keep all new output JSON under this folder.
- Treat this folder as exploratory until results are verified.

## Physics boundary

- This run uses the existing hardware runner on **all 80 qubits** with no subset restriction.
- The main observable is full-register `perturbed_echo` / `readout_mitigated.perturbed_echo`.
- This is **not** a proven full-q80 fixed-observable OLE estimator.
- Any result here must therefore be described as a **full-register q80 state-return bonus experiment**, not as closed full-q80 OLE.

## Planned run pair

- overlap branch: `q = 0`
- far-disjoint branch: `q = 79`
- qubits: `80`
- depths: `1,2`
- trials: `3`
- seed / seed_transpiler: `424242`
- shots: `8000`
- mitigation: `--readout-mitigation --cal-shots 6000`
- extra suppression: `XY4` + gate twirling (`8` randomizations)

Expected output files:

- `full_q80_q0_raw_vs_mit.json`
- `full_q80_q79_raw_vs_mit.json`

## Execution update

Executed on `ibm_fez` with the planned pair:

- overlap branch `q=0`
  - hardware job: `d6vahis69uic73cj3d1g`
  - calibration job: `d6vahsgv5rlc73f4pmng`
- far-disjoint branch `q=79`
  - hardware job: `d6vai5qtnsts73et0s10`
  - calibration job: `d6vaif2tnsts73et0sag`

Observed full-register `perturbed_echo` means:

| depth | branch | raw `perturbed_echo` | `readout_mitigated` `perturbed_echo` |
| --- | --- | --- | --- |
| 1 | overlap `q=0` | `0.00413 +/- 0.00137` | `0.01449 +/- 0.00504` |
| 1 | far-disjoint `q=79` | `0.03942 +/- 0.04880` | `0.31299 +/- 0.44263` |
| 2 | overlap `q=0` | `0.01013 +/- 0.00504` | `0.07271 +/- 0.04567` |
| 2 | far-disjoint `q=79` | `0.01825 +/- 0.01123` | `0.14898 +/- 0.09976` |

Observed far-minus-overlap deltas:

- depth 1: raw `+0.03529`, mitigated `+0.29850`
- depth 2: raw `+0.00813`, mitigated `+0.07628`

First interpretation:

- The bonus full-register pair did complete end-to-end on hardware.
- The far-disjoint branch sits above the overlap branch on both tested depths.
- The depth-1 mitigated far-disjoint point is extremely broad, so this is not stable claim-bearing evidence.
- This folder therefore records a **successful exploratory full-register q80 hardware run**, not a resolved full-q80 physics claim.

## Run entrypoint

Use:

```bash
bash scripts/run-q80-full-register-bonus.sh --stage pair --execute
```

Dry-run only:

```bash
bash scripts/run-q80-full-register-bonus.sh --stage plan
```

Stability rerun only:

```bash
bash scripts/run-q80-full-register-bonus.sh --stage rerun_shallow_stability --execute
```

That stage writes into:

- `bonus_full_q80_2026-03-21/rerun_shallow_stability/full_q80_q0_raw_vs_mit_t5.json`
- `bonus_full_q80_2026-03-21/rerun_shallow_stability/full_q80_q79_raw_vs_mit_t5.json`

It keeps the original pair untouched and bumps the shallow rerun to `5` trials.

Depth-2 layout-controlled rerun:

```bash
bash scripts/run-q80-full-register-bonus.sh --stage depth2_layout_rerun --execute
```

That stage uses the transpiler-derived fixed layout stored in:

- `ibm_fez_depth2_seed424242_initial_layout.txt`

and writes into:

- `bonus_full_q80_2026-03-21/depth2_layout_rerun/full_q80_q0_raw_vs_mit_t5_layout.json`
- `bonus_full_q80_2026-03-21/depth2_layout_rerun/full_q80_q79_raw_vs_mit_t5_layout.json`

## Depth-2 layout-controlled rerun update

The fixed-layout depth-2 pair was executed on `2026-03-21`:

- overlap branch `q=0`
  - hardware job: `d6vb07atnsts73et19ug`
  - calibration job: `d6vb0faf84ks73df4hu0`
  - output: `depth2_layout_rerun/full_q80_q0_raw_vs_mit_t5_layout.json`
- far-disjoint branch `q=79`
  - hardware job: `d6vb0mov5rlc73f4q5fg`
  - calibration job: `d6vb0us69uic73cj3rug`
  - output: `depth2_layout_rerun/full_q80_q79_raw_vs_mit_t5_layout.json`

Observed depth-2 layout-controlled deltas (`q79 - q0`):

- raw `+0.00668`
- mitigated `+0.05949`

Observed mitigated trial values:

- `q=0`: `0.65700, 0.00000, 0.19995, 0.11691, 0.01796`
- `q=79`: `0.04587, 0.02181, 1.00000, 0.18121, 0.04038`

Stability verdict:

- `q=0`: `std_exceeds_mean`
- `q=79`: `std_exceeds_mean`

Interpretation update:

- The fixed layout preserves a positive depth-2 overlap-versus-far-disjoint separation.
- It does **not** remove the high-variance behavior; both branches remain mitigation-unstable.
- Within this bonus track, layout control alone is therefore not sufficient. The next clean escalation is a depth-2-only shot increase on the better of the two current protocols rather than broader depth expansion.

## Depth-2 shot-increase plan

The next staged rerun keeps the cleaner no-layout protocol and only increases hardware shots:

- stage: `depth2_shot_increase`
- depths: `2`
- trials: `5`
- hardware shots: `16000`
- calibration shots: `6000`
- layout: none
- output files:
  - `bonus_full_q80_2026-03-21/depth2_shot_increase/full_q80_q0_raw_vs_mit_t5_s16000.json`
  - `bonus_full_q80_2026-03-21/depth2_shot_increase/full_q80_q79_raw_vs_mit_t5_s16000.json`

Use:

```bash
bash scripts/run-q80-full-register-bonus.sh --stage depth2_shot_increase --execute
```

## Depth-2 shot-increase update

The `16000`-shot no-layout depth-2 pair was executed on `2026-03-21`:

- overlap branch `q=0`
  - hardware job: `d6vb3qif84ks73df4l6g`
  - calibration job: `d6vb49itnsts73et1do0`
  - output: `depth2_shot_increase/full_q80_q0_raw_vs_mit_t5_s16000.json`
- far-disjoint branch `q=79`
  - hardware job: `d6vb4iitnsts73et1e10`
  - calibration job: `d6vb50qf84ks73df4mdg`
  - output: `depth2_shot_increase/full_q80_q79_raw_vs_mit_t5_s16000.json`

Observed depth-2 shot-increase deltas (`q79 - q0`):

- raw `+0.00419`
- mitigated `+0.06016`

Observed mitigated trial values:

- `q=0`: `0.53159, 0.01343, 0.16325, 0.11334, 0.03480`
- `q=79`: `0.04005, 0.02356, 0.96024, 0.11036, 0.02301`

Stability verdict:

- `q=0`: `std_exceeds_mean`
- `q=79`: `std_exceeds_mean`, `single_trial_dominates`

Comparison against the earlier depth-2-only reruns:

- previous no-layout `8000`-shot rerun: raw `+0.00690`, mitigated `+0.06811`, no stability flags on either branch
- fixed-layout `8000`-shot rerun: raw `+0.00667`, mitigated `+0.05949`, `std_exceeds_mean` on both branches

Interpretation update:

- Doubling hardware shots preserves a positive depth-2 overlap-versus-far-disjoint separation.
- It does **not** improve the bonus-track stability relative to the cleaner no-layout `8000`-shot depth-2 rerun.
- The far-disjoint mitigated branch is still dominated by one large trial, so extra hardware shots alone are not the limiting fix here.
- Within this bonus track, the best currently recorded depth-2 point remains the earlier no-layout `5`-trial rerun at `8000` shots.
- The next credible improvement should target mitigation robustness directly, for example by increasing calibration support or changing the full-register estimator, rather than just pushing the same shot pattern harder.

## Shallow stability rerun update

The `5`-trial rerun pair was executed on `2026-03-21`:

- overlap branch `q=0`
  - hardware job: `d6vasmgv5rlc73f4q1jg`
  - calibration job: `d6vat50v5rlc73f4q210`
  - output: `rerun_shallow_stability/full_q80_q0_raw_vs_mit_t5.json`
- far-disjoint branch `q=79`
  - hardware job: `d6vatdqtnsts73et1760`
  - calibration job: `d6vatsaf84ks73df4fdg`
  - output: `rerun_shallow_stability/full_q80_q79_raw_vs_mit_t5.json`

Observed rerun deltas (`q79 - q0`):

- depth 1: raw `-0.00323`, mitigated `-0.02178`
- depth 2: raw `+0.00690`, mitigated `+0.06811`

Stability verdict from the new JSON flags:

- depth 1:
  - `q=0`: `std_exceeds_mean`
  - `q=79`: `two_or_more_zero_clips`, `std_exceeds_mean`, `single_trial_dominates`
- depth 2:
  - no stability flags on either branch

Interpretation update:

- The extra trials did **not** rescue shallow depth 1; that point remains unstable and should not carry claim weight.
- Depth 2 is materially cleaner and remains the only shallow full-register q80 point with a usable positive separation in this bonus track.
- The immediate improvement path should therefore prioritize layout control and depth-2-first reruns, not broader claim language.

## Verification checklist

Before any interpretation, verify:

1. `config.qubits = 80`
2. `config.depths = [1,2]`
3. `config.skip_exact = true`
4. `config.readout_mitigation = true`
5. `summary_by_depth[*].raw.perturbed_echo` exists
6. `summary_by_depth[*].readout_mitigated.perturbed_echo` exists
7. `summary_by_depth[*].readout_mitigated.perturbed_echo_stability` exists
8. Both branch files are present in this folder

## Interpretation guardrail

Even if the overlap/disjoint separation looks clean, that would still be:

- evidence for a bonus full-register q80 hardware state-return experiment
- not yet a replacement for the subset-locality chain
- not yet a justified full-q80 OLE-equivalent claim

## Full-register estimator update

The hardware runner now writes an additive self-normalized full-register estimator for non-subset runs:

- `relative_perturbed_echo = perturbed_echo / ideal_echo`
- clipped to `[0,1]` per trial
- summarized both by mean/std and by a robust `median`/`MAD` block
- preferred future readout-mitigated full-register readout:
  - `readout_mitigated.relative_perturbed_echo_robust.median`

Reason for the change:

- the old full-register bonus track was being read mainly through `readout_mitigated.perturbed_echo`
- on the current depth-2 bonus data, that mean can stay positive even when the branch is carried by one large trial
- self-normalizing by the branch's own `ideal_echo` makes the metric less sensitive to branch-dependent baseline return differences

Offline check on the already recorded depth-2 bonus runs:

- earlier no-layout rerun (`8000` shots):
  - mean delta on `relative_perturbed_echo`: `+0.07415`
  - median delta on `relative_perturbed_echo`: `-0.03360`
- fixed-layout rerun (`8000` shots):
  - mean delta: `+0.05949`
  - median delta: `-0.07104`
- shot-increase rerun (`16000` shots):
  - mean delta: `+0.04369`
  - median delta: `-0.08314`

Interpretation update:

- the positive full-register depth-2 mean separation is currently outlier-sensitive
- once the branch is read through the new self-normalized robust estimator, the median does **not** support a stable far-disjoint-above-overlap statement
- future bonus reruns should therefore be judged against the robust full-register estimator first, not against `perturbed_echo` mean alone

## Paired capture entrypoint

The bonus script now also contains a non-destructive paired capture stage for the next rerun:

```bash
bash scripts/run-q80-full-register-bonus.sh --stage depth2_paired_capture --execute
```

That stage:

- runs `q=0` and `q=79` together in one hardware job
- uses one shared readout-calibration job
- writes one paired JSON into:
  - `bonus_full_q80_2026-03-21/depth2_paired_capture/full_q80_q0_q79_paired_t5.json`
- stores per-trial Hamming-weight and single-qubit marginal observables so later full-register estimator work does not require another blind rerun

## Paired capture update

The new paired depth-2 capture was executed on `2026-03-21`:

- shared hardware job: `d6vblg2f84ks73df5680`
- shared calibration job: `d6vblrgv5rlc73f4qq80`
- output:
  - `depth2_paired_capture/full_q80_q0_q79_paired_t5.json`

Preferred paired full-register readout:

- `readout_mitigated.relative_perturbed_echo_robust.median`

Branch-level readout-mitigated relative estimator:

- `q=0`: mean `0.23166`, median `0.13947`, MAD `0.10079`
- `q=79`: mean `0.25879`, median `0.05587`, MAD `0.01721`

Paired trial-by-trial delta on `relative_perturbed_echo` (`q79 - q0`):

- mean `+0.02713`
- std `0.45246`
- median `+0.01468`
- MAD `0.00733`
- flags: `std_exceeds_mean`, `single_trial_dominates`
- per-trial deltas:
  - `-0.67028`, `+0.02201`, `+0.75974`, `+0.01468`, `+0.00950`
- sign count:
  - `4/5` paired trials positive

Paired Hamming/marginal check on perturbed mean excitation fraction (`q79 - q0`):

- mean `+0.00035`
- median `+0.00048`

Interpretation update:

- The paired capture is better than the earlier split-job bonus runs because the preferred paired robust delta is now slightly positive.
- That positive paired median is not visible if one only compares branch medians afterwards; the pairing itself matters.
- Two very large opposite-sign outliers are still present, so this is not clean claim-bearing full-register evidence.
- The right next step is now to stay in paired mode and either increase trial count or derive a paired Hamming-weight-based full-register estimator from this richer capture, rather than going back to separate branch jobs.

## Trimmed diagnostic between-result

As a strictly diagnostic interim read, the paired delta was also trimmed with a MAD rule and written to:

- `depth2_paired_capture/full_q80_q0_q79_paired_t5_trimmed_diagnostic.json`

Rule used:

- center = raw paired-delta median `+0.01468`
- MAD = `0.00733`
- robust threshold = `3 * 1.4826 * MAD = 0.03258`

Dropped paired trials:

- trial `0`: `-0.67028`
- trial `2`: `+0.75974`

Kept paired trials:

- trial `1`: `+0.02201`
- trial `3`: `+0.01468`
- trial `4`: `+0.00950`

Trimmed paired delta summary:

- kept mean `+0.01540`
- kept median `+0.01468`
- kept MAD `0.00519`
- positive kept trials: `3/3`

Guardrail:

- this trimmed view is useful as a quick between-result to see what the central paired cluster is doing
- it is **not** a replacement for the raw paired record
- with only `5` paired trials, trimmed diagnostics must stay explicitly exploratory

## Paired Hamming-weight analysis

The first paired Hamming-weight-based full-register analysis was backfilled from the paired capture into:

- `depth2_paired_capture/full_q80_q0_q79_paired_t5_hamming_analysis.json`

Estimator used:

- `readout_mitigated.relative_hamming_return_linear`
- definition:
  - per branch, correct single-qubit `P(1)` marginals with the local readout model
  - compute `hamming_return_linear = 1 - mean(P(1))`
  - compare branches through the paired delta on the relative score

Branch summaries:

- `q=0`:
  - mean `0.98746`
  - median `0.98801`
  - MAD `0.00392`
- `q=79`:
  - mean `0.98696`
  - median `0.98451`
  - MAD `0.00295`

Paired delta (`q79 - q0`):

- mean `-0.00050`
- std `0.00935`
- median `-0.00059`
- MAD `0.00400`
- no stability flags
- no MAD-trimmed drops

Per-trial paired deltas:

- `-0.01384`, `+0.00161`, `+0.01491`, `-0.00059`, `-0.00459`

Interpretation update:

- the Hamming-weight-based paired estimator is materially more stable than the paired full-register echo delta
- but it does **not** currently show a positive far-disjoint advantage; it is effectively near-null to slightly negative
- that means the current paired full-register picture is mixed:
  - the paired echo-style delta has a small positive central cluster once the two extreme trials are treated diagnostically
  - the paired Hamming-weight estimator does not confirm that direction
- so the next honest step is not broader claim language but either:
  - a second paired capture with more trials, or
  - a better full-register observable derived from the stored richer statistics

## Symmetrized local-mitigation diagnostic

As a mitigation-method cross-check, the same paired capture was re-read with a symmetrized local readout model and written to:

- `depth2_paired_capture/full_q80_q0_q79_paired_t5_hamming_symmetrized_mitigation_comparison.json`

Diagnostic comparison for the paired Hamming delta (`q79 - q0`):

- asymmetric local mitigation:
  - mean `-0.00050`
  - median `-0.00059`
  - MAD `0.00400`
- symmetrized local mitigation:
  - mean `-0.00044`
  - median `-0.00047`
  - MAD `0.00409`

Per-trial deltas move only slightly:

- trial 0: `-0.01384 -> -0.01384`
- trial 1: `+0.00161 -> +0.00169`
- trial 2: `+0.01491 -> +0.01500`
- trial 3: `-0.00059 -> -0.00047`
- trial 4: `-0.00459 -> -0.00456`

Interpretation update:

- on this paired capture, switching from the asymmetric local model to a symmetrized local model does **not** materially change the Hamming-weight conclusion
- the full-register Hamming signal remains near-null to slightly negative under both local mitigation variants
- that makes the mitigation-model choice a secondary issue here; the limiting problem is still the observable sensitivity, not this particular local readout inversion

## M3 replay diagnostic

The same paired capture was then re-read through a marginal-calibrated M3 pass, reusing the original hardware job and the original all0/all1 calibration job:

- `depth2_paired_m3_reuse/full_q80_q0_q79_paired_t5_m3.json`

Method:

- reuse hardware job `d6vblg2f84ks73df5680`
- reuse calibration job `d6vblrgv5rlc73f4qq80`
- build single-qubit marginal M3 calibrations from the saved all0/all1 calibration counts
- apply M3 quasi-distribution correction branch-wise, then read out both:
  - `relative_perturbed_echo`
  - `relative_hamming_return_linear`

Paired depth-2 result (`q79 - q0`):

- M3 echo-style delta:
  - mean `+0.07283`
  - median `+0.00500`
  - MAD `0.00632`
  - trimmed-diagnostic median `+0.00500`
- M3 Hamming delta:
  - mean `-0.00039`
  - median `-0.00021`
  - MAD `0.00595`

Branch medians:

- `q=0`:
  - M3 `relative_perturbed_echo` median `0.04545`
  - M3 `relative_hamming_return_linear` median `0.98548`
- `q=79`:
  - M3 `relative_perturbed_echo` median `0.01219`
  - M3 `relative_hamming_return_linear` median `0.98149`

Interpretation update:

- the M3 replay does **not** strengthen the positive full-register direction
- its echo-style paired median stays only slightly positive and much smaller than the earlier local paired central cluster
- its Hamming-weight paired median remains slightly negative, so M3 also does not supply a positive full-register Hamming confirmation
- within this bonus track, M3 therefore changes the mitigation backend but not the broad conclusion: the full-register signal remains mixed and non-claim-bearing

## Calibration-bootstrap diagnostic

As the next step after M3, the original paired capture was re-read through a calibration bootstrap that resamples only the saved all0/all1 calibration histograms:

- `depth2_paired_cal_bootstrap/full_q80_q0_q79_paired_t5_local_cal_bootstrap.json`

Bootstrap setup:

- hardware counts fixed to the original paired capture
- only calibration uncertainty resampled
- model: multinomial resample of the full all0/all1 calibration histograms
- current diagnostic batch: `20` replicates

Paired delta bootstrap summaries (`q79 - q0`):

- local `relative_perturbed_echo`:
  - trial-delta mean summary:
    - mean `+0.02752`
    - median `+0.02697`
    - 95% interval `[+0.01817, +0.03959]`
    - positive-rate `1.0`
  - trial-delta median summary:
    - mean `+0.01537`
    - median `+0.01507`
    - 95% interval `[+0.01134, +0.02003]`
    - positive-rate `1.0`
- local `relative_hamming_return_linear`:
  - trial-delta mean summary:
    - mean `-0.00050`
    - median `-0.00049`
    - 95% interval `[-0.00057, -0.00043]`
    - positive-rate `0.0`
  - trial-delta median summary:
    - mean `-0.00057`
    - median `-0.00058`
    - 95% interval `[-0.00065, -0.00048]`
    - positive-rate `0.0`

Interpretation update:

- within this first calibration-bootstrap diagnostic, the sign pattern is stable under calibration resampling
- the local echo-style paired delta stays positive across all `20/20` bootstrap replicates
- the local Hamming-weight paired delta stays negative across all `20/20` bootstrap replicates
- so the mixed full-register picture is not coming from one lucky calibration inversion; it persists under calibration uncertainty as well
- this bootstrap is intentionally small and diagnostic only; if we want tighter intervals later, the right next move is to speed up the bootstrap code rather than naively pushing the same Python loop harder

## Block-Z fallback reuse

Since direct access to the Algorithmiq TEM function is likely unavailable in the current environment, the existing paired hardware capture was re-read through a TEM-friendlier fallback inside the current runner:

- `depth2_paired_blockz_reuse/full_q80_q0_q79_paired_t5_blockz_front10_back10.json`

Method:

- reuse hardware job `d6vblg2f84ks73df5680`
- reuse calibration job `d6vblrgv5rlc73f4qq80`
- keep the existing local readout-mitigation model
- add two diagonal-in-Z block observables on the same paired depth-2 capture:
  - `front10 = 0..9`
  - `back10 = 70..79`
- summarize for each block:
  - block mean-`Z`
  - block linear return
  - block `Z`-parity

Paired readout-mitigated block result (`q79 - q0`):

- `front10`:
  - relative linear return delta mean `+0.09856`
  - median `+0.09418`
  - MAD `0.03078`
  - perturbed mean-`Z` delta mean `+0.19419`
  - median `+0.18539`
- `back10`:
  - relative linear return delta mean `-0.10373`
  - median `-0.12447`
  - MAD `0.02272`
  - perturbed mean-`Z` delta mean `-0.20526`
  - median `-0.24605`

Branch view:

- `q=0`:
  - `front10` linear return mean `0.90105`, median `0.90549`
  - `back10` linear return mean `0.99945`, median `0.99993`
- `q=79`:
  - `front10` linear return mean `0.99961`, median `0.99967`
  - `back10` linear return mean `0.89572`, median `0.87422`

Interpretation update:

- this fallback is materially more informative than the global full-register Hamming summary
- it shows the expected spatial pattern directly:
  - a perturbation at `q=0` suppresses the nearby `front10` block much more than the far `back10` block
  - a perturbation at `q=79` does the mirror image
- that does **not** close the full-q80 claim, but it is stronger evidence that the paired full-register bonus track contains structured locality information rather than only estimator noise
- the block `Z`-parity channel is much less stable here; under local quasi-mitigation it can leave the physical `[-1,1]` range, so the cleaner fallback observable is the block linear-return / mean-`Z` family, not parity

## TEM pilot stage

A separate Algorithmiq TEM pilot stage is now wired into the bonus flow:

- `depth2_paired_tem_pilot/full_q80_q0_q79_paired_t5_tem_hamming.json`

Entry points:

- `scripts/run-paired-tem-pilot.py`
- `scripts/run-q80-full-register-bonus.sh --stage depth2_paired_tem_pilot`

Method:

- keep the existing sampler-based full-register chain untouched
- rebuild the same logical depth-2 paired `q=0/q=79` circuits
- remove final measurements because IBM TEM only accepts unitary circuits
- query the `algorithmiq/tem` Qiskit Function on TEM-native observables:
  - global mean magnetization
  - per-qubit `Z` expectations
- derive `hamming_return_linear` and paired `q79 - q0` summaries from the TEM outputs
- store all four TEM output variants when available:
  - fully TEM-mitigated
  - non-mitigated
  - TEM-mitigated without readout mitigation
  - non-mitigated with readout mitigation only

Practical prerequisites:

- IBM Quantum Platform access to `algorithmiq/tem`
- `qiskit_ibm_catalog` installed in the qiskit venv
- this TEM path is meant as an additive pilot for the Hamming/magnetization observable family, not as a drop-in replacement for the current `p_zero`-style full-register echo metric
