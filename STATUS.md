# Onderzoekstatus: black hole / echo circuits / berekening

Aangemaakt: 2026-03-05 13:18:18 +01:00
Scope: bestanden in qlab met wijzigingsdatum <= 2 dagen oud.

## Zoekresultaat
- Totaal relevante bestanden gekopieerd: 40
- Zoektermen: blackhode, blackhole, black_hole, echo circuit(s), berekening
- Opmerking: term berekening is niet gevonden in recente bestanden.

## Actief benchmarkdoel
- Actieve campagneclaim: `q14-only` exact-short `perturbed_echo`, sneller dan de matching classical baseline op `IBM quantum_seconds`, gereproduceerd op 3 onafhankelijke kalenderdagen.
- Legacy referentie: de oudere `q12/q14` Level-C route blijft historisch relevant, maar is niet langer het actieve campagnedoel.

## Verdedigbare claimtaal
- Strakke repo-formulering: we hebben nu bewijs voor een smal, taak-specifiek quantum runtime-voordeel op `q14`, plus reproduceerbare hardware utility op 80-qubit subset-observables.
- Belangrijke grens: dit is nog geen volledige `hardware advantage` in de strengere Level-C betekenis, en ook geen claim over volledige 80-qubit globale state-overlap.
- Toegestane inference: de combinatie van `q14` runtime-winst en consistente 80q subset-signalen is verenigbaar met een plausibel pad naar bredere quantum advantage als noise verder kan worden onderdrukt.
- Niet als feit formuleren: dat bredere voordeel is nu nog een hypothese, geen bewezen eindclaim.

## Status van het onderzoek (op basis van recente samenvattingen)
- Level A: PASS
- Level B: PASS (sterke ondersteuning)
- Legacy Level C: NOT YET
- Kernreden legacy Level C: onder de door jou bevestigde runtime-definitie op `quantum_seconds` blijft `q12` de blocker (`26 qs` versus classical `21.33 s`), ook al haalt `q14` de runtime-gate nu op day-1, day-2 en day-3 (`26 qs` versus `51.05 s`); de 3-daagse reproduceerbaarheid is daarmee wel binnen voor de smallere `q14-only` claim.
- Q14-only campagneclaim: DAYS 1-3 PASS; frozen claim criteria gehaald

## Belangrijkste recente signalen
- Q10 pilot: mitigatie verlaagt ideal abs error sterk (ongeveer 0.2055 -> 0.0064).
- Q80 subset-runs: mitigatie verhoogt ideal subset-echo; perturbed subset-echo daalt licht, met locality-check en rerun die consistent zijn.
- Q12/Q14 exact-short day-1 hardware-kwalificatie op `perturbed_echo` is aanwezig; raw hardware haalt MAE `0.037174` (q12) en `0.032857` (q14) versus exact referentie.
- Classical exact-short baselines voor dezelfde taak zijn nu lokaal aanwezig: q12 `0:21.33`, q14 `0:51.05`.
- Deze nieuwere classical runtimes vervangen de oudere, zwaardere pre-fix metingen; elke runtime-advantage claim moet daarom opnieuw tegen deze baselines worden beoordeeld.
- Q12 day-2 raw exact-short op `ibm_fez` is uitgevoerd met hardware job `d6rv3ef90okc73erlkb0`; de perturbed-echo MAE blijft onder target op `0.035924`.
- De day-2 runner crashte pas na de q12-job door een PowerShell MAE-parserbug; de runner is inmiddels gepatcht.
- De verrijkte IBM jobmetadata laat voor q12 day-1, q12 day-2 en q14 day-1 telkens `quantum_seconds = 26` en `billed_seconds = 26` zien.
- Q14-only day-2 op `ibm_fez` is nu ook uitgevoerd met hardware job `d6s2qnfgtkcc73cl1qvg`; de perturbed-echo MAE is `0.033684` en de runtime-gate slaagt opnieuw met `26 < 51.05`.
- Q14-only day-3 op `ibm_fez` is nu uitgevoerd met hardware job `d6sj7jrbjfas73fohiig`; de perturbed-echo MAE is `0.031142` en de runtime-gate slaagt opnieuw met `26 < 51.05`.
- Onder de runtime-definitie op `quantum_seconds` betekent dat: q12 day-1 `26 > 21.33` en q12 day-2 `26 > 21.33` dus runtime FAIL; q14 day-1, day-2 en day-3 geven telkens `26 < 51.05` dus runtime PASS.
- Een volledige herlezing van het 2026-03-15 Level-C plan onder `quantum_seconds` bevestigt dat q10 al runtime-negatief was (`36/35 s` versus classical `26.02 s`), dat de oude q12-rationale op `19:42.63` obsolete is, en dat vooral het claimpad moet worden herzien, niet de budgetraming.
- Daarom is het actieve benchmarkdoel nu expliciet omgezet naar een `q14-only` 3-daagse reproduceerbare claim; na de day-3 run op `2026-03-17` is die frozen claim nu gesloten met drie PASS-dagen.
- De lokale wall time van q12 day-2 was ongeveer `349 s` (`00:05:49`); dat verschil met `26 qs` wijst op aanzienlijke queue/orchestratie-overhead en is niet meer de primaire runtime-gate.

## Verantwoording subsetmetingen bij 80 qubits
- Voor 80 qubits gebruiken we een vaste subset-observable (typisch 10 qubits) in plaats van globale 80-qubit string-overlap.
- Reden: globale overlap verliest op deze schaal snel contrast door readout/SPAM-fouten; volledige readout-mitigatie over alle 80 qubits is niet schaalbaar.
- Daarom vergelijken we raw en mitigated resultaten op exact dezelfde, vooraf vastgelegde subset.
- De keuze is inhoudelijk ondersteund door locality-controls: subset 10-19 gaf vrijwel geen gap bij perturbatie op qubit 0, maar wel een grote en reproduceerbare gap bij perturbatie op qubit 10.
- Conclusie: de 80q-resultaten ondersteunen lokale, reproduceerbare hardware utility op subset-observables, maar vormen geen claim over volledige 80-qubit fidelity of globale state-overlap.

## English note on subset measurements at 80 qubits
- For 80 qubits, we use a fixed subset observable (typically 10 qubits) instead of global 80-qubit string overlap.
- Reason: at this scale, global overlap rapidly loses contrast due to readout/SPAM errors, while full readout mitigation across all 80 qubits is not scalable.
- We therefore compare raw and mitigated results on the exact same pre-declared subset.
- This choice is supported by locality controls: subset 10-19 showed almost no gap when the perturbation was applied to qubit 0, but a large and reproducible gap when the perturbation was applied to qubit 10.
- Conclusion: the 80q results support local, reproducible hardware utility on subset observables, but they do not constitute a claim about full 80-qubit fidelity or global state overlap.

## Bronnen voor status
- quantum-math-lab/results/hardware/summary/levelb_evidence_report.md
- quantum-math-lab/results/hardware/summary/levelc_progress_table.md
- quantum-math-lab/results/hardware/summary/ibm_runs_raw_vs_mitigated_summary.md
- quantum-math-lab/results/hardware/archives/2026-03-05_q80_run1_run2/RESULTS_SUMMARY.md
- quantum-math-lab/results/hardware/summary/levelc_day1_q12_q14_update_2026-03-15.md
- quantum-math-lab/results/hardware/summary/levelc_day2_q12_stop_2026-03-16.md
- quantum-math-lab/results/hardware/summary/levelc_runtime_quantum_seconds_2026-03-16.md
- quantum-math-lab/results/hardware/summary/levelc_plan_reassessment_quantum_seconds_2026-03-16.md
- quantum-math-lab/benchmarks/q14_only_manifest.json
- quantum-math-lab/results/hardware/summary/q14_only_campaign_plan_2026-03-16.md
- quantum-math-lab/results/hardware/summary/q14_only_day2_update_2026-03-16.md
- quantum-math-lab/results/hardware/summary/q14_only_day3_update_2026-03-17.md
