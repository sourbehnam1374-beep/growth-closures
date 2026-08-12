# The κ-correspondence — naming disciplines and their guarantees

**Working note / paper-3 skeleton · in preparation · 2026-06-11**
Companion to: *Monotone Growth of Content-Addressed Rule Closures* (growth) and *Principled Deletion in Content-Addressed Rule Closures* (deletion). Status labels below: **[L]** kernel-checked in `GrowthClosure.lean` (extended file, compiles clean on Lean 4.30.0); **[P]** paper-proved; **[M]** machine-checked at instance/property level; **[O]** open obligation.

---

## 0. Thesis

Both companion papers trade in one unnamed currency: **what the address commits to**. Every guarantee they prove, and every impossibility, is a consequence of a single design choice — the contents of the address preimage. Make that choice the *parameter* of the theory and the scattered results become faces of one object:

> **An identity scheme is a commitment map κ from parts to preimage features. Each storage guarantee is equivalent to a closure condition on κ. CALM is the slice of this correspondence obtained by forgetting identity.**

The growth trilemma, the deletion dichotomy, tombstone permanence, and the dedup/deniability dilemma are then projections of one correspondence, not four results.

## 1. Definitions

**D1 (feature space).** Fix a feature alphabet for a part *v*: `content(v)` (payload bytes), `premises(v)` (sorted child addresses), `rule(v)`, `descr(v)`, `nonce(v)` (fresh randomness, min-entropy ≥ λ), `epoch(v)` (ingestion-era tag), `pos(v)` (arrival index).

**D2 (identity scheme).** A scheme is a pair (κ, H): a commitment set κ ⊆ features and a collision-resistant H; `addr(v) = H(κ-projection of v)`, recursively through `premises`. The companion papers fix **κ₀ = {rule, descr, premises, content}** (H4) and derive everything from it.

**D3 (guarantee vocabulary).** DEDUP (equal content ⇒ equal address); SD (single derivation; equivalently cone-exact deletion, DRed-free); CONS (address-stable conservativity, growth Thm 2); HIST (history independence, growth Thm 5); MONO (closure monotone over ⊆); DEN (deniable erasure: retained addresses do not enable guess-verification beyond 2^−λ); READD (a removed identity can be live again); XSTAB (addresses stable across epochs); AUDIT (provable was-present-and-removed without retention).

## 2. The correspondence (target table of paper 3)

| # | condition on κ | ⟺ guarantees | status |
|---|---|---|---|
| κ1 | premises ⊆ κ | SD; hence cone theorem, semi-naive deletion, DRed-free | ⇐ **[P]** (deletion Lemma 2) **[M]**; ⇒ **DONE [P][L][M]** (`Growth.Necessity.necessity`, axioms [propext]; exhaustive 4-atom witness; repair `counting_exact`) |
| κ2 | κ ⊆ content-determined features (no randomness) | DEDUP ∧ ¬DEN | subsumed by erasure triangle **[P]** (kappa_nucleus_v0, Thm: impossibility edge + achievability) |
| κ3 | nonce ∈ κ | DEN ∧ ¬DEDUP | subsumed by erasure triangle **[P]**: salted vertex = {AUDIT, DEN}, selective-audit remark |
| κ4 | side conditions payload-determined (κ-analogue: no seed-global feature) | MONO; hence CONS ∧ HIST | MONO ⇐ **[L]** axiom-free (`step_mono`); only-if family = growth Thm 11 **[L]** (`impossibility`) |
| κ5 | epoch ∈ κ | READD ∧ ¬XSTAB | **DONE [L]** both directions: `tombstone_permanence` (fixed identity, permanent) + `Growth.Epoch.epoch_readd` / `epoch_fresh` (fresh era, returns; XSTAB/dedup fail) — **all axiom-free**; implementation demo in `corpus_o5.py` |
| κ6 | address-only retention over κ₀ | AUDIT ∧ DEN-up-to-entropy | **DONE [P][M]**: confirmation bound (q·2^−(H∞(payload)+H∞(tag))) + corpus exchange rate measured: dedup mass 0.45% vs 128 deniability bits (`corpus_o5.py`) |

**O1 (the one substantive new proof).** If premises ⊄ κ, construct two distinct rule instances with the same address: alternative derivations reappear, `supp` is ill-defined, the cone theorem fails, and DRed's over-delete/rederive machinery returns. Construction: bind-address omitting premises ⇒ any two ≥τ subsets of a cohort collide. Gives the converse: *content addressing is not merely sufficient for exact deletion — premise inscription is necessary.*

**O2/O3.** State DEN as an indistinguishability game against the retained address set; κ2 ⇒ ¬DEN is the confirmation-of-file attack; κ3 trades DEDUP away. **Prior art duty: this is the convergent-encryption trade-off — cite Douceur et al. (ICDCS 2002) and DupLESS (Bellare–Keelveedhi–Ristenpart, USENIX Sec 2013). The contribution is connecting it to closure theory and to AUDIT, not the trade-off itself.**

**O4 — DONE.** See κ5 row. Bonus: the three-axis separation — tag *mutability* ⇒ READD, tag *entropy* ⇒ DEN, tag *granularity* ⇒ dedup scope — unifies κ3/κ5 into one dial (nucleus v0.2 §4).

**O5 — DONE.** Bound stated+proved (standard, attributed); per-corpus instrumentation delivered: Moby-Dick dedup mass 39/8636 = 0.45%, source-aware confirmation 2^13.07, salted exchange rate 128 bits ↔ 0.45% storage (nucleus v0.2 §5).

## 3. The model statement (target main theorem)

Commitment sets ordered by ⊆ form a lattice; guarantees form a poset under implication. The correspondence is **antitone in the identity-forgetting direction and exact at six named points** (table above). Two named projections:

- **CALM slice.** Forget identity (quotient by addr): κ4 collapses to *monotone ⟺ coordination-free consistent* — the CALM theorem. So CALM = the κ-correspondence after erasing the identity axis; rows κ1–κ3, κ5–κ6 are invisible to it. (This is the precise content of "CALM has no vocabulary for identity.")
- **Trilemma/dichotomy slices.** Growth trilemma (C,H,P) = {κ4 guarantees} vs extensional parsimony; deletion dichotomy = κ4 vs strict shrink over ⊆; both already **[L]/[P]** — they become *corollaries* of the correspondence, which is the test that the model is real rather than a relabeling.

**THE UNIFIED STATEMENT — DONE (nucleus v0.3 §Determination).** The Determination Theorem: every guarantee is a functional dependency `Det(k, x)` on ingestion events; clauses (a) unification, (b) dedup-at-granularity, (c) stability-under-context, (d) confirmation — **all kernel-checked axiom-free** (`Growth.Unified`) and instantiated on the implementation (`verify_unified.py`); clause (e), the recursive premises-clause, provably non-reducible (= O1's home). Two-observer identity: DEDUP and ¬DEN are one predicate at two stations; the triangle edge derived in one line (`triangle_edge`). Prior-art placement: dependency lattice = Armstrong 1974 (cited); new = recursive clause, two-observer reading, min-entropy quantification. Bonus finding: schema (a) exposed the atom constructor's uncommitted descriptor argument — safe only under the papers' descriptor-is-a-payload-field invariant (recorded as a check).

**Falsifiable novelty test for paper 3:** the correspondence must yield ≥1 statement no slice contains. Candidates: (a) O1's necessity converse; (b) the three-way impossibility **DEDUP ∧ DEN ∧ AUDIT jointly unsatisfiable for any κ** (sketch: AUDIT needs retained addresses; DEDUP forces content-determined addresses; retained content-determined addresses defeat DEN — assemble from κ2+κ6); (c) O5's quantitative bound. If none survives, the paper is a survey, not a contribution — say so and stop.

## 4. Prior-art anchors (citation duties before any submission)

| duty | anchors | what remains ours |
|---|---|---|
| dedup vs confidentiality | Douceur et al. 2002; Bellare et al. 2013 (DupLESS); Rogaway–Shrimpton 2004 | the closure-theoretic placement + AUDIT axis + O5 bound |
| order-extension escape | **Bloom^L**: Conway–Marczak–Alvaro–Hellerstein–Maier, CIDR 2012 (lattice generalization of CALM) | derived superstructure + identity stability on top of the lattice move (deletion §two-phase already cites CRDTs; add Bloom^L) |
| deletion propagation | Buneman–Khanna–Tan, ICDT 2002; Kimelfeld et al. | cone theorem positioned as: singleton why-provenance ⇒ exact, linear deletion propagation |
| monotonicity boundary | CALM trio (Hellerstein 2010; Ameloot–Neven–Van den Bussche 2013; Hellerstein–Alvaro 2020); Ross–Sagiv 1992/97 | already repositioned in growth v2 — keep |
| identity-as-Skolem | Marnette 2009 | already in growth v2 — keep |

## 5. Mechanization plan (reuse the existing Lean development)

- Already in place: `step_mono` (κ4 ⇐, axiom-free), `impossibility` (κ4 only-if witness), `tombstone_permanence` (κ5 ¬epoch case), `twoP_mono`, cone-side checks at ledger/property level.
- New: a `Kappa` structure (selector functions feature → Option Bytes); `addr` as `H ∘ select`; **O1** at the mask level in the style of the `Impossibility` namespace (two colliding instances, `decide`); κ2/κ3 as propositional statements over an abstract H with an injectivity-on-committed-features hypothesis (the same H4-style split: combinatorics in Lean, cryptography as the named assumption).
- DEN stays a *game-based* definition outside Lean (crypto layer, by design — same separation both papers already use for SHA-256).

## 6. Milestones

1. **M1 (days):** splice `anomaly_characterization_dropin.tex` into deletion v1 → v1.1; register P13/P14 + DEL-13; rerun ledgers. *(P13/P14 + corpus identity already pass: this package.)*
2. **M2 — DONE (this package):** O1 proved both directions, converse kernel-checked (`Growth.Necessity`), exhaustive; conservation checked n=3..8. Gate passed: first non-slice theorem exists.
3. **M3 — DONE in nucleus form:** erasure triangle stated + proved (impossibility edge, three achievability vertices on measured policies, selective-audit remark). Remaining: O5 quantitative bound.
4. **M4 — table complete AND unified (this package):** Determination Theorem proved, mechanized axiom-free, instantiated; nucleus v0.3 is the paper-3 core. Next: expand nucleus into full draft (intro/related-work prose around the existing theorem spine).
5. **M5 — DONE (this package):** sweep round 2 delivered (`prior_art_kappa_round2.md`): 7 clusters, 16 verified citations added, placements integrated into nucleus v0.4 §Related work. Verdict: unified statement / necessity converse / AUDIT axis / three-axis dial unclaimed; three close neighbors declared and credited (Harnik 2010 = systems form of two-observer; Nix input- vs content-addressed = the dial deployed; Hartline 2002 = SHI-via-canonical-representation, an instance gained). One citation flagged for camera-ready verification (build-systems early cutoff). **Next: venue selection.**
6. **M6 — DONE (this package):** full draft assembled — `kappa_paper_v1` (10 pp, exit 0, 0 undefined refs): abstract, introduction with seven scoped contributions, verification-ladder section quoting the fresh axiom audit verbatim (33 declarations re-run 2026-06-11, exit 0, sole diagnostic one cosmetic linter warning), limitations, conclusion. `VENUE_DOSSIER_kappa.md` (LMCS primary staggered +2-4 wks behind growth; single trilogy DTiA note Sep 2026; CPP up-rated to alternate; PoPETs spin-off held) and `SUBMISSION_kappa.md` (metadata paste-ready; pdflatex-variant flagged as the one real risk; extended-Lean top-level rule enforced in checklist) delivered, bundled as `kappa_submission_v1.zip`. **Next: AUTHOR DECISIONS — (a) venue track per dossier §1, (b) build+test the pdflatex variant, (c) arXiv-ID swaps after papers 1–2 upload.**

## 7. Honesty ledger (what this is and is not)

- κ2, κ5, κ6 are *near-definitional once stated* — their value is unification, not depth. The depth lives in O1, candidate (b), and O5.
- The correspondence is a **model proposal until M2–M3 deliver**; until then, label all of §3 "conjectured correspondence."
- The deniability boundary is inherited from the security literature; we add placement and quantification, nothing more. Say exactly that.
