# VERIFICATION.md — proof status of "Monotone Growth of Content-Addressed Rule Closures"

Three independent verification layers, each reproducible from this package.
Date of run: 2026-06-11 · Lean 4.30.0 · Python 3 (stdlib + hypothesis).

---

## Rung 0 — Deductive proofs (paper)

All theorems carry complete pen-and-paper proofs from elementary lattice
theory in `growth_of_content_addressed_closures_v1.md`. Verified by author;
not independently refereed.

## Rung 1 — Instance + property verification (Python)

| artifact | what it establishes | result |
|---|---|---|
| `growth_check.py` | 15 fixed instance checks: real SHA-256 addresses/fingerprints, 13-history confluence, absorption run, retraction counterexample, 42-block clique, β₁ = 150 replay, 11×11 threshold grid | **15/15 PASS** |
| `test_growth_properties.py` | 14 universally-quantified properties from the paper, each on 60 randomized adversarial instances (Hypothesis, with shrinking): closure laws, conservativity as address-stable Merkle diff, incremental = batch, history independence over random partitions, presentation-order independence, descent identity, address injectivity, well-formedness characterization (wf ⟺ every cohort ≥ 3, ecc = 4), β₁ Euler identity + Δβ₁ = m−j per instance + growth-monotone, per-cohort clique closed form, Φ_max retraction vs complete-closure conservativity, quotient-view maximality/coverage invariants, MDL threshold on integers and exact rationals (r ≥ 0) | **14/14 PASS** (~840 instances) |

Reproduce: `python python/growth_check.py` · `cd python && python test_growth_properties.py`
(needs `pip install hypothesis`).

Epistemic status: falsification pressure on the implementation–theory pair;
not proof of the universal statements.

## Rung 2 — Machine-checked proofs (Lean 4)

`GrowthClosure.lean` — self-contained, **no imports, no mathlib, no `sorry`**.
Compiles clean on Lean 4.30.0 (`lean lean/GrowthClosure.lean`). The closure is
defined impredicatively (Knaster–Tarski least pre-fixed point), so no
iteration machinery is needed for existence. The v1.3 extension adds a concrete payload-determined rule format (`RuleFamily`), Kleene stages, and the semi-naive frontier development — Theorem 4 is now inside the kernel-checked perimeter, with H1/H2 discharged as theorems rather than assumed.

Formally proved, kernel-checked:

| paper | Lean theorem |
|---|---|
| Thm 1 closure operator | `extensive`, `K_mono`, `K_idem`, `K_closed` |
| Thm 2 conservativity (abstract) | `conservativity` |
| Galois adjunction K ⊣ ι | `galois` |
| Thm 3 incremental closure | `incremental` |
| Thm 5 ingestion confluence | `ingest_eq`, `history_independent` |
| Thm 6 continuity in the seed | `continuity` (under `Finitary` + directedness) |
| Descent identity | `descent` |
| Thm 11 impossibility | `Impossibility.impossibility` (decidable witness: mask 7 maximal at seed 7, not at seed 15) |
| Thm 4 semi-naive frontier locality | `seminaive_eq`, `seminaive_incremental` — over `RuleFamily`; the frontier-restricted iteration (never firing an all-old instance) provably reaches the full incremental closure |
| Kleene stages = closure | `stage`, `stageUnion_eq_K`, `rule_stageUnion_eq_K` |
| H2 ⇒ Mono (Lemma A/B discharge) | `RuleFamily.step_mono` — **axiom-free** |
| H1 ⇒ Finitary discharge | `RuleFamily.step_finitary` — **axiom-free** |

Axiom audit (verbatim compiler output):

```
'Growth.K_idem'                    depends on axioms: [propext, Quot.sound]
'Growth.conservativity'            does not depend on any axioms
'Growth.galois'                    does not depend on any axioms
'Growth.incremental'               depends on axioms: [propext, Quot.sound]
'Growth.ingest_eq'                 depends on axioms: [propext, Quot.sound]
'Growth.history_independent'       depends on axioms: [propext, Quot.sound]
'Growth.continuity'                depends on axioms: [propext, Quot.sound]
'Growth.descent'                   does not depend on any axioms
'Growth.Impossibility.impossibility' depends on axioms: [propext]
'Growth.RuleFamily.step_mono'      does not depend on any axioms
'Growth.RuleFamily.step_finitary'  does not depend on any axioms
'Growth.stageUnion_eq_K'           depends on axioms: [propext, Quot.sound]
'Growth.seminaive_eq'              depends on axioms: [propext, Quot.sound]
'Growth.seminaive_incremental'     depends on axioms: [propext, Quot.sound]
```

Reading: `conservativity`, `galois`, `descent`, and the two discharge theorems
`RuleFamily.step_mono` and `RuleFamily.step_finitary` are **axiom-free** — pure
constructive logic. The remaining theorems use only Lean's standard kernel
axioms `propext` and `Quot.sound` (the latter via `funext`), and only because
they are stated as set *equalities*. **No `Classical.choice` anywhere** — the
entire development is constructive.

## What is deliberately NOT machine-proved

1. **The cryptographic layer of H4.** SHA-256 collision resistance is an
   assumption, not a theorem — in the Lean development, parts are identified
   with elements of `U`, which is exactly the "addresses are injective"
   hypothesis. This split is by design and stated in the paper (Thm 14-style
   combinatorial/cryptographic separation).

*(v1.3 note: the two items formerly listed here — Theorem 4 and the `Mono`
discharge — moved inside the kernel-checked perimeter: `seminaive_eq`,
`seminaive_incremental`, `RuleFamily.step_mono`, `RuleFamily.step_finitary`.)*

## Claim-status summary

| claim class | status |
|---|---|
| Closure algebra (Thms 1–6, Galois, descent, Kleene stages) | **machine-proved** (Lean, constructive) + paper proof + 840 random instances |
| Impossibility (Thm 11) | **machine-proved** (Lean, `decide`) + paper proof + randomized retraction tests |
| Semi-naive (Thm 4) | **machine-proved** (Lean, constructive, over `RuleFamily`) + paper proof + randomized equivalence tests |
| H1/H2 discharge (Mono, Finitary as theorems) | **machine-proved** (Lean, **axiom-free**) |
| Quantitative claims (clique counts, β₁ laws, threshold) | paper proof + fixed ledger + randomized tests |
| Hash-identity claims | conditional on SHA-256 injectivity (assumption, by design) |
