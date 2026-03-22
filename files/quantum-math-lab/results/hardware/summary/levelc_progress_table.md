# Level C progress table (interim)

⚠️ Interim overzicht. Nog **geen** final Level-C verdict, omdat de matrix nog niet volledig/identiek is over alle punten en dagen.

## Classical track (available so far)

| tag | q | shots | wall_s | max_rss_GiB | perturbed_echo depth-avg |
|---|---:|---:|---:|---:|---:|
| q8_s5000 | 8 | 5000 | 12.84 | 0.263 | 0.144986 |
| q8_s10000 | 8 | 10000 | 13.18 | 0.263 | 0.144986 |
| q10_s5000 | 10 | 5000 | 89.73 | 0.392 | 0.145375 |
| q10_s10000 | 10 | 10000 | 90.00 | 0.377 | 0.145375 |

## Hardware track (short pilot points)

| tag | q | shots | backend | perturbed_echo depth-avg | hw_job_id | cal_job_id |
|---|---:|---:|---|---:|---|---|
| q10_raw_short | 10 | 5000 | ibm_marrakesh | 0.167250 | d6k9jk4mmeis739sg54g | None |
| q10_mit_short | 10 | 5000 | ibm_fez | 0.161533 | d6k9k6sgmsgc73c02e70 | d6k9kjg60irc7395h41g |
| q14_raw_exact | 14 | 4000 | ibm_fez | 0.077937 | d6k96nsmmeis739sfjg0 | None |

## Pass/fail snapshot

- Level A: **PASS**
- Level B: **PASS (strong support)**
- Level C: **NOT YET** (needs fixed target accuracy + full matched classical/hardware runtime matrix + multi-day reproducibility)
