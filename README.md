# Content-Addressed Rule Closures — verified trilogy

Three working papers on the least-fixpoint theory of content-addressed knowledge stores,
each on a three-rung verification ladder (paper proofs / executable verification /
Lean 4 kernel check). Code: MIT. Papers: CC BY 4.0 (canonical home: arXiv).

| Paper | Version | Pages (arXiv build) | Status |
|---|---|---|---|
| Monotone Growth of Content-Addressed Rule Closures | v2.1 | 14 | arXiv → LMCS |
| Principled Deletion in Content-Addressed Rule Closures | v1.1 | 11 | arXiv |
| Naming Disciplines for Generated Knowledge: the κ-Correspondence | v1 | 9 | arXiv → LMCS |

## One-command kernel check (Lean 4.30.0, no mathlib, no sorry)
    lean lean/GrowthClosure.lean        # exit 0; 33 declarations audited

Audit facts: `conservativity`, `galois`, `descent`, `step_mono`, `step_finitary`,
the survivor/2P lemmas, `Epoch.*`, and all six `Unified.*` theorems are **axiom-free**;
`Necessity.*` uses `[propext]` only; the remainder `[propext, Quot.sound]`;
no `Classical.choice` anywhere in the development.

## Executable verification
    python3 verifiers/growth_check.py                    # 15/15 ledger
    python3 verifiers/test_growth_properties.py          # 14/14 properties
    python3 verifiers/delete_growth.py                   # 12/12 ledger
    python3 verifiers/test_anomaly_characterization.py   # Thm 9: 698 instances + corpus identity 5014/8631
    python3 verifiers/verify_o1_necessity.py             # exhaustive converse + conservation n=3..8
    python3 verifiers/verify_unified.py                  # 7/7 determination schemas
    python3 verifiers/test_stronger_properties.py        # 8/8 strengthened variants

## Strengthened variants (this branch)
`lean/GrowthClosure.lean` gains a "STRENGTHENED VARIANTS" section, each statement
strictly strengthening a theorem of the trilogy on the same constructive base:
`K_fixpoint` / `K_least_fixpoint` (Theorem 1 upgraded from least closed superset
to least FIXED POINT of X ↦ S ⊔ Φ(X)), `K_merge` (Theorem 3 upgraded to replica
merge), `ingest_extends` (Theorem 5: histories only grow, address-stably),
`tombstone_permanence_set` (set-level tombstones), `live_extend_adds` /
`live_extend_removes` (the 2P CALM sandwich over operation logs), and
`live_replay` (idempotent log replay). Rung-1 coverage:
`verifiers/test_stronger_properties.py` (V1–V8, ~480 randomized instances).
NOTE: this branch was authored without a local Lean toolchain — re-run the
rung-2 kernel check (`lean lean/GrowthClosure.lean`) before merging.

## Layout
    lean/        single source of truth: the full trilogy development (38,138 B)
    papers/      canonical XeLaTeX sources + PDFs + arXiv (pdflatex) variants
    packs/       clean-room-tested arXiv tarballs
    verifiers/   Python ledgers and property suites
    docs/        venue dossiers, prior-art sweeps, milestone ledger
    icdt/        ICDT "Database Theory in Action" note (LIPIcs)

DOI: Zenodo badge appears here after the v1.0.0 release (see EXECUTION_MASTER pkg_02).
