# Provenance and attribution for the Qiskit echo hardware runner

Publication date: 11 October 2026.

This record accompanies [the file-scoped licence notice](../../LICENSE_SCOPE.md).
It is a provenance record, not a licence for the entire repository.

## Bram's runner contributions

Sole credited author: **Bram Dobbelaar**.

Bram confirms that he developed the runner with assistance from ChatGPT/Codex.
They were tools, not co-authors. The credited authorship does not claim
ownership of any protected underlying third-party material.

The grant covers Bram-controlled contributions in
`files/quantum-math-lab/qiskit_black_hole_hardware_runner.py`, including its
corresponding comments and docstrings, under Apache-2.0. The recorded
components include job handling, counts conversion, logging, observables,
statistics, CLI handling, local tensor/subset/block-Z helpers and the
runner's own library/model adapters, subject to the separate attribution below.

Source snapshot commit: `78e09c48ab25b3c6ebc3fed36c483123fc057a61`.

Original runner blob: `30905b5b42a559f233527f0ea487f330cb6b1888`.

Runner blob with licensing comments: `b9909c78d25779aeb715caa2350bb12e4001becc`.

The first visible runner import was commit
`ac38bea0f30e23d505d179c3e75747f98c7befae` on 18 March 2026; the last
substantive runner update in the recorded history was
`c5e6c9e7c83b5f3dbc8e204400d822cbf44bbfeb` on 22 March 2026.
The author's confirmation supplies the authorship declaration; an import
commit alone does not establish passage-by-passage provenance.

## Potentially adapted M3 calibration material

Component: `_build_m3_marginal_mitigator`.

Provenance status: **potential adaptation, conservatively attributed**.

- Upstream: [Qiskit/qiskit-addon-mthree](https://github.com/Qiskit/qiskit-addon-mthree)
- File: `mthree/mitigation.py`
- Comparison commit: `8402654566900aed11b64f625e18b49aefb902eb` (6 August 2025)
- Comparison blob: `486105ee893f5abce0bc6006af45b8cf12506d69`
- [Permanent comparison-source link](https://github.com/Qiskit/qiskit-addon-mthree/blob/8402654566900aed11b64f625e18b49aefb902eb/mthree/mitigation.py)
- Upstream file notice: `(C) Copyright IBM 2021.`
- Upstream licence: Apache-2.0
- Upstream licence-file notice: `Copyright 2017 IBM and its contributors`
- [Unaltered upstream licence file retained here](../../LICENSES/third-party/M3-LICENSE.txt)

The matching sequence constructs a 2-by-2 float32 calibration matrix per qubit,
reverses bit positions, counts zero results after zero preparation and one
results after one preparation, fills the two matrix columns and uses the same
faulty-qubit comparison as the marginal branch of upstream `_job_thread`.
Similarity supports conservative attribution; it does not establish that the
source was literally copied or identify the development checkout.

Compared with the upstream marginal-calibration branch, this adapter accepts
already collected all-zero and all-one histograms, normalises their
bitstrings, populates an M3Mitigation object directly and returns calibration
diagnostics. This describes the possible adaptation already present in the
recorded runner; no executable changes were made by the licence publication.

The comparison source carries the following header, retained here verbatim:

```python
# This code is part of Mthree.
#
# (C) Copyright IBM 2021.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.
```

The runner also carries the IBM notice, Apache-2.0 reference, retention notice,
comparison reference and modification description adjacent to the adapter.
The separate IBM notice is an upstream attribution, not a co-author credit
for Bram's runner contributions.

## Separate libraries and external material

Imports and API calls do not grant ownership of the imported implementations.
The following dependencies and external sources retain their own terms:

| Component | Recorded upstream terms | Scope boundary |
| --- | --- | --- |
| Qiskit SDK, qiskit-ibm-runtime, qiskit-aer | Apache-2.0 | Imported libraries are excluded; Aer is imported by the companion module. |
| M3 / mthree | Apache-2.0 | Library implementation is excluded; the possibly adapted calibration material is separately attributed above. |
| NumPy | BSD-3-Clause | Imported library is excluded. |
| PyTorch | Its upstream BSD-style licence and separate notices | Imported library is excluded. |
| External PELINN-Q model source | Candidate repository: MIT, Copyright (c) 2025 paolodarold | Model code and checkpoints/weights are excluded. |

The exact historical installed dependency versions have not been established.
For the candidate PELINN-Q model, comparison commit
`04a399f942058bf5cee761958b7d513982d848c2` carries the MIT notice naming
paolodarold; `src/model.py` has blob
`d1e0c8ee68f84b49dd1c9e142d472c62924b7bf8`. This does not establish the
exact external checkout or checkpoint used in a hardware run.

The separately stored `qiskit_black_hole_scrambling.py` module refers to a shared
ChatGPT discussion. That module is excluded from this grant. The original
AI session, historical service terms and passage-level assistance record have
not been independently reconstructed. The grant does not resolve separate
contractual obligations or grant rights owned by third parties.

Experimental data, job outputs, figures, papers and other repository files
are excluded. This publication makes no new claim about experimental
validation or dataset inclusion.

## Licence-publication change

On 11 October 2026, only licensing/provenance comments were added to the runner.
Removing the two inserted comment blocks reconstructs the original bytes
exactly, with Git blob `30905b5b42a559f233527f0ea487f330cb6b1888`.
Both that original version and the new blob `b9909c78d25779aeb715caa2350bb12e4001becc` are
explicitly recorded in the scope notice.

The [original Dutch research proposal](Licentieonderzoek_Qiskit_echo_runner_CONCEPT.md)
is retained unchanged as a historical pre-publication record. Its statements
that publication had not yet occurred describe that draft's status; the
published scope notice states the grant now in effect.
