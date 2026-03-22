# IBM runs — raw vs mitigated (one-pager)

Bronbestanden:
- `results/hardware/black_hole_hardware_q10_pilot.json`
- `results/hardware/black_hole_hardware_q80_raw.json`
- `results/hardware/black_hole_hardware_q80_subset01_mit.json`

## Headlines

### Q10 pilot (met exact referentie)
- Gem. ideal abs error: **0.205533 -> 0.006396**
  - absolute winst: 0.199137
  - relatieve winst: 96.89%
- Gem. perturbed abs error: **0.048992 -> 0.034291**
  - absolute winst: 0.014701
  - relatieve winst: 30.01%

### Q80 subset-mit run (subset [0..9])
- Gem. subset ideal echo: **0.773271 -> 0.875524** (shift +0.102253)
- Gem. subset perturbed echo: **0.077167 -> 0.072603** (shift -0.004564)

> Let op: bij Q80 is mitigatie toegepast op subsetmetingen (q0..q9), niet op volledige 80-qubit string-overlap.

## Per-depth tabel — Q10

| depth | raw ideal err | mit ideal err | raw pert err | mit pert err |
|---:|---:|---:|---:|---:|
| 1 | 0.201467 | 0.005544 | 0.021561 | 0.012051 |
| 2 | 0.206800 | 0.006594 | 0.049507 | 0.021741 |
| 3 | 0.206067 | 0.006293 | 0.059583 | 0.022902 |
| 4 | 0.204867 | 0.005173 | 0.020886 | 0.047007 |
| 5 | 0.210400 | 0.006676 | 0.062112 | 0.039217 |
| 6 | 0.204000 | 0.005800 | 0.040522 | 0.025260 |
| 8 | 0.205933 | 0.008174 | 0.083461 | 0.060889 |
| 10 | 0.204733 | 0.006917 | 0.054304 | 0.045258 |

## Per-depth tabel — Q80 subset

| depth | raw subset ideal | mit subset ideal | raw subset pert | mit subset pert |
|---:|---:|---:|---:|---:|
| 1 | 0.767500 | 0.990725 | 0.024333 | 0.014996 |
| 2 | 0.772167 | 0.816451 | 0.069750 | 0.058144 |
| 3 | 0.772167 | 0.841806 | 0.097750 | 0.100838 |
| 4 | 0.781250 | 0.853112 | 0.116833 | 0.116432 |

Artifacts:
- `hardware/summary/ibm_q10_raw_vs_mitigated_by_depth.csv`
- `hardware/summary/ibm_q80_subset_raw_vs_mitigated_by_depth.csv`
