# Level B evidence report (IBM hardware)

Generated (UTC): 2026-03-04T20:05:54.084715+00:00

## Verdict (current)

- **Level A: gehaald** (mitigatie-effect duidelijk op q10 met exact referentie).
- **Level B: sterk ondersteund** (80q hardware utility + locality + reproduceerbaarheid op subset-observables).
- **Level C: nog niet** (geen bewezen hardware-vs-classical runtime win op vaste accuracy target over meerdere groottes/dagen).

## Q10 pilot (exact referentie beschikbaar)

- Raw ideal abs error mean: **0.205533**
- Mitigated ideal abs error mean: **0.006396**
- Ideal improvement: **0.199137** (96.89%)
- Raw pert abs error mean: **0.048992**
- Mitigated pert abs error mean: **0.034291**
- Pert improvement: **0.014701** (30.01%)

## 80q subset evidence (samenvatting)

| Run | Backend | Raw gap (ideal-pert) | Mitigated gap (ideal-pert) | Ideal shift (mit-raw) | Pert shift (mit-raw) |
|---|---|---:|---:|---:|---:|
| q80_subset01_mit | ibm_fez | 0.696104 | 0.802921 | 0.102253 | -0.004564 |
| q80_subset01_mit_xsup | ibm_torino | 0.643729 | 0.831016 | 0.161870 | -0.025416 |
| q80_subset02_mit_xsup_control_pq0 | ibm_torino | 0.002646 | -0.000735 | 0.114430 | 0.117811 |
| q80_subset02_mit_xsup_pq10 | ibm_fez | 0.693646 | 0.737767 | 0.050365 | 0.006244 |
| q80_subset02_mit_xsup_pq10_rerun1 | ibm_fez | 0.693958 | 0.735875 | 0.047219 | 0.005302 |

**Interpretatie locality-check:**
- subset `10-19` met perturbatie op qubit `0` gaf vrijwel geen gap (controle).
- dezelfde subset met `--perturb-qubit 10` gaf grote en stabiele gap (signaal lokaal aantoonbaar).

## Reproduceerbaarheid (subset 10-19, perturb-qubit 10)

- mitigated gap run1: **0.737767**
- mitigated gap rerun1: **0.735875**
- delta gap: **-0.001892**
- delta mitigated ideal mean: -0.004292
- delta mitigated pert mean: -0.002400

## Budget snapshot

- Used: **255s** / 600s
- Remaining: **345s** (~5.75 min)

## Referentie job IDs

- `q10_pilot`: hw=d6k786o60irc7395dqkg, cal=d6k78r4mmeis739sct00, backend=ibm_fez
- `q80_subset01_mit`: hw=d6k818u33pjc73dmthcg, cal=d6k82skmmeis739sdtvg, backend=ibm_fez
- `q80_subset01_mit_xsup`: hw=d6k8ft860irc7395fep0, cal=d6k8g8860irc7395ff4g, backend=ibm_torino
- `q80_subset02_mit_xsup_control_pq0`: hw=d6k8n7cgmsgc73c013og, cal=d6k8nhcmmeis739sepo0, backend=ibm_torino
- `q80_subset02_mit_xsup_pq10`: hw=d6k8r1sgmsgc73c01b20, cal=d6k8rm860irc7395g2o0, backend=ibm_fez
- `q80_subset02_mit_xsup_pq10_rerun1`: hw=d6k8tjsmmeis739sf5j0, cal=d6k8v8sgmsgc73c01ha0, backend=ibm_fez
