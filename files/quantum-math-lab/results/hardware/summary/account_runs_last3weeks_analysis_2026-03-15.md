# IBM account runs analysis (last 3 weeks)

Window checked: 2026-02-22 through 2026-03-15.

## Account inventory

- Total jobs in window: 21
- Research-relevant jobs: 20 runtime jobs on 2026-03-04
- Non-research job: 1 Composer sampler job on 2026-03-07 (`d6m2q30fh9oc73enhol0`)
- Cancelled research attempt: 1 Torino job on 2026-03-04 (`d6k7vc633pjc73dmteh0`)
- Total quantum usage in window: 365 s
- Research-related quantum usage in window: 363 s

## Research bundles found in the account

| Bundle | Evidence in repo | Hardware job(s) | Calibration job(s) | Notes |
|---|---|---|---|---|
| q10 pilot with exact reference | `black_hole_hardware_q10_pilot.json` | `d6k786o60irc7395dqkg` | `d6k78r4mmeis739sct00` | Strong Level-A evidence |
| q80 raw baseline | `black_hole_hardware_q80_raw.json` | `d6k7f1e33pjc73dmsq60` | none | Global raw 80q baseline |
| q80 subset01 mitigated | `black_hole_hardware_q80_subset01_mit.json` | `d6k818u33pjc73dmthcg` | `d6k82skmmeis739sdtvg` | Subset `[0..9]` on `ibm_fez` |
| q80 subset01 mitigated + x-suppression | `black_hole_hardware_q80_subset01_mit_xsup.json` | `d6k8ft860irc7395fep0` | `d6k8g8860irc7395ff4g` | Subset `[0..9]` on `ibm_torino` |
| q80 subset02 locality control (`perturb_qubit=0`) | `black_hole_hardware_q80_subset02_mit_xsup.json` | `d6k8n7cgmsgc73c013og` | `d6k8nhcmmeis739sepo0` | Control on subset `[10..19]` |
| q80 subset02 signal (`perturb_qubit=10`) | `black_hole_hardware_q80_subset02_mit_xsup_pq10.json` | `d6k8r1sgmsgc73c01b20` | `d6k8rm860irc7395g2o0` | Local signal on subset `[10..19]` |
| q80 subset02 rerun (`perturb_qubit=10`) | `black_hole_hardware_q80_subset02_mit_xsup_pq10_rerun1.json` | `d6k8tjsmmeis739sf5j0` | `d6k8v8sgmsgc73c01ha0` | Reproducibility rerun |
| q14 raw exact-short | `black_hole_hardware_q14_raw_exact.json` | `d6k96nsmmeis739sfjg0` | none | Interim Level-C pilot point |
| q10 raw short | `levelc_progress_table.json`, `q_vs_c_olddata_q10.json` | `d6k9jk4mmeis739sg54g` | none | Old-data runtime comparison |
| q10 mitigated short | `levelc_progress_table.json`, `q_vs_c_olddata_q10.json` | `d6k9k6sgmsgc73c02e70` | `d6k9kjg60irc7395h41g` | Old-data runtime comparison |
| q80 subset01 light | `black_hole_hardware_q80_subset01_light.json` | `d6k9f4cgmsgc73c027fg` | `d6k9fdsmmeis739sfvk0` | Extra short mitigated subset run not included in the earlier Level-B report |

## What changed relative to the earlier repo summaries

- No new black-hole/echo hardware evidence appeared after 2026-03-04.
- The only later account job was a Composer sampler job on 2026-03-07 and is unrelated to the black-hole campaign.
- There is one extra useful run in the account-backed artifacts: `black_hole_hardware_q80_subset01_light.json`.

## Extra evidence from `q80_subset01_light`

For subset `[0..9]` at 80 qubits (depths 1-2, trials 2):

- raw subset gap: `0.760167`
- mitigated subset gap: `0.879629`
- mitigated ideal shift: `+0.112000`
- mitigated perturbed shift: `-0.007462`

This is qualitatively consistent with the earlier `q80_subset01_mit` result (`0.696104 -> 0.802921`) and therefore strengthens Level B slightly, but it does not address Level C.

## A / B / C status after checking the account

- Level A: still PASS
- Level B: still PASS, now with one extra supporting subset run (`q80_subset01_light`)
- Level C: still NOT YET

## Why Level C is still not proven

1. The substantive research jobs are all concentrated on 2026-03-04, so the account does not add true multi-day reproducibility.
2. The existing matched q10 runtime comparison still shows hardware slower than classical at the current setup:
   - raw hardware / classical wall-time ratio: `1.3836`
   - mitigated hardware / classical wall-time ratio: `1.3451`
3. The q10 short runtime comparison is explicitly marked as interim and uses different hardware backends for raw vs mitigated (`ibm_marrakesh` vs `ibm_fez`).
4. There is still no full matched classical-vs-hardware runtime matrix across multiple problem sizes and days with a fixed accuracy target.

## Minimum next evidence needed for Level C

1. Choose one fixed observable and one fixed accuracy target.
2. Re-run the same hardware bundle on at least two additional calendar days.
3. Add matched classical baselines for the same observable/target at the next sizes you want to claim.
4. Keep backend effects controlled: same backend when possible, otherwise treat backend changes as a separate factor.
