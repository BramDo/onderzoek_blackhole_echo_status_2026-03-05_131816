# Level C plan reassessment under IBM quantum_seconds

Date: 2026-03-16

## Scope

Re-evaluate the 2026-03-15 Level-C plan and the older timing assumptions under the clarified hardware runtime metric:

- hardware runtime metric: `IBM quantum_seconds` when available
- classical runtime metric: matching classical wall time for the same frozen task

For mitigated hardware runs, calibration usage must be counted in the total hardware runtime.

## Verified matched runtime points

| task | source date | hardware runtime basis | hardware runtime | classical comparator | verdict |
|---|---|---|---:|---:|---|
| q10 raw short | 2026-03-04 | IBM hardware usage | `36 s` | q10 exact-short classical `26.02 s` | FAIL |
| q10 mitigated short | 2026-03-04 | IBM hardware + calibration usage | `35 s` | q10 exact-short classical `26.02 s` | FAIL |
| q12 raw exact-short day 1 | 2026-03-15 | IBM `quantum_seconds` | `26 s` | q12 exact-short classical `21.33 s` | FAIL |
| q12 raw exact-short day 2 | 2026-03-16 | IBM `quantum_seconds` | `26 s` | q12 exact-short classical `21.33 s` | FAIL |
| q14 raw exact-short day 1 | 2026-03-15 | IBM `quantum_seconds` | `26 s` | q14 exact-short classical `51.05 s` | PASS |

## What this changes in the 2026-03-15 plan

### 1. The q8/q10 warning was correct and is now stronger

- The 2026-03-15 plan already said not to force Level C through `q8/q10`.
- Under `quantum_seconds`, that conclusion is confirmed directly:
  - q10 raw is slower than classical (`36 > 26.02`)
  - q10 mitigated total usage is also slower than classical (`35 > 26.02`)

### 2. The original reason to pivot to q12/q14 is obsolete

The 2026-03-15 plan justified the q12/q14 route partly with the statement that q12 classical exact-short already cost `19:42.63`.

That rationale is no longer valid because the classical exact workflow was sped up afterward:

- q12 exact-short classical is now `21.33 s`
- q14 exact-short classical is now `51.05 s`

So the earlier expectation that q12 would likely be runtime-favorable does not survive the updated classical baseline.

### 3. Under the frozen current claim, q12 already blocks Level C

The fixed Level-C route was:

- observable: `perturbed_echo`
- accuracy target: `MAE <= 0.05`
- runtime claim: hardware faster than classical on two consecutive sizes
- reproducibility: three independent calendar days

Under the clarified runtime metric:

- q12 meets the accuracy target on both day 1 and day 2
- q12 does not meet the runtime target on either day (`26 > 21.33`)
- q14 day 1 does meet the runtime target (`26 < 51.05`)

That means the current Level-C claim is blocked before the 3-day replication criterion even becomes the main issue.

### 4. The day-by-day stop rule should now be interpreted differently

If the runtime definition is fixed on `quantum_seconds`, the strict stop rule should be:

- if q12 raw does not beat q12 classical on `quantum_seconds`, stop the claim campaign
- do not use local queue-heavy wall time as the primary runtime gate

On that reading, the current evidence says the campaign is not ready to continue under the frozen q12/q14 claim.

## Budget reassessment

The budget planning itself was reasonable even though the claim path was not.

- The 2026-03-15 budget note estimated `q12 raw + q14 raw` at about `50-70` quantum_seconds total.
- The observed day-1 pair is `26 + 26 = 52` quantum_seconds.
- So the budget estimate was good.

What failed was not the budget forecast but the expectation that q12 would be runtime-positive under the updated benchmark.

## Old timing notes reinterpreted

- Use `IBM quantum_seconds` or IBM job usage as the hardware runtime metric when available.
- Do not use local end-to-end wall time like the q12 day-2 `~349 s` as the main runtime verdict; that reflects queue/orchestration overhead.
- For mitigated runs, include calibration usage in the hardware total.
- The older classical `q8/q10 s5000/s10000` timings are still valid measurements, but they are not the right comparator for the frozen exact-short q12/q14 claim.

## Bottom line

- Level A remains PASS.
- Level B remains PASS.
- Level C remains NOT YET.
- Under `quantum_seconds`, the current Level-C path fails on `q12`, not on budget and not on q14.
- The strongest defensible statement now is:
  - q10 is already runtime-negative on usage
  - q12 is accurate but runtime-negative on usage
  - q14 day 1 is runtime-positive on usage
  - therefore the present two-consecutive-size Level-C claim is not currently supportable
