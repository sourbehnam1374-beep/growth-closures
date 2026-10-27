# Content-Addressed Rule Closures — verified trilogy

Three working papers on the least-fixpoint theory of content-addressed knowledge stores. Each is presented on a three-rung verification ladder:

1. paper proof
2. executable verification
3. Lean 4 kernel check

Code is released under MIT. Paper sources are released under CC BY 4.0; the canonical manuscript versions are prepared for scholarly archiving.

| Paper | Version | Pages | Public status |
| --- | --- | ---: | --- |
| Monotone Growth of Content-Addressed Rule Closures | v2.1 | 14 | Working paper with executable and kernel checks |
| Principled Deletion in Content-Addressed Rule Closures | v1.1 | 11 | Working paper with executable and kernel checks |
| Naming Disciplines for Generated Knowledge: the κ-Correspondence | v1 | 9 | Working paper with executable and kernel checks |

## Kernel verification

Lean version: 4.30.0. The development is self-contained, uses no `mathlib`, and contains no `sorry`.

```bash
lean lean/GrowthClosure.lean
```

Audited declarations include `conservativity`, `galois`, `descent`, `step_mono`, `step_finitary`, the survivor and two-phase lemmas, `Epoch.*`, and all six `Unified.*` theorems.

- `Unified.*` and the central growth declarations are axiom-free.
- `Necessity.*` uses `[propext]` only.
- Remaining declarations use `[propext, Quot.sound]`.
- `Classical.choice` does not occur in the development.

## Executable verification

```bash
python3 -m pip install -r requirements-verification.txt
python3 verifiers/run_verification.py --out verification-logs
# Include the pinned Lean kernel check when Lean 4.30.0 is installed:
python3 verifiers/run_verification.py --lean lean --out verification-logs
```

The runner covers the published ledgers, growth and anomaly properties,
deletion properties, identity-conflict regressions, independent finite-oracle
checks, corpus measurements, and negative controls for failed verifiers.
It writes logs and a JSON receipt containing code/input hashes and runtime
versions. GitHub Actions runs the full Python + Lean audit on pull requests
to `main` and pushes to `main`.

Verification reads a bundled, hash-checked corpus and needs no network after
dependencies and Lean are installed. The pinned 27 October 2026 revision
has 8,632 described sentences and 5,013 in cohorts of size at least four.
The papers' earlier 8,631 / 5,014 result is preserved as historical evidence;
its original input bytes were not retained. These are separately identified
corpus revisions. No manuscript figures or paper counts are changed here.

See [the input contract and repair receipt](docs/IDENTITY_AND_REPRODUCIBILITY.md)
for the two-phase fix, regression evidence, and SHIVA adapter requirements.

## Repository layout

| Path | Public artifact |
| --- | --- |
| `lean/` | Single-source Lean development for the trilogy |
| `papers/` | Canonical TeX sources and rendered manuscripts |
| `packs/` | Clean manuscript source bundles |
| `verifiers/` | Python ledgers, exhaustive checks, and property suites |
| `docs/` | Public verification and theorem-correspondence notes |
| `icdt/` | Short-note manuscript and reproducible typesetting assets |
| `CITATION.cff` | Citation metadata |

## Interpretation boundary

A passing executable or kernel check establishes only the property encoded by that check. It does not by itself establish originality, peer-review status, applicability to a deployed system, or correctness of claims outside the formalized scope.

The papers remain working research until independently reviewed and accepted through the relevant scholarly process.
