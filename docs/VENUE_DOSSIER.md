# Venue dossier — growth-closures v2.1

**Phase 5 deliverable** · facts verified live 2026-06-11 · all deadlines AoE

---

## 1. Recommendation (read this first)

**Track A — submit the full paper to LMCS (Logical Methods in Computer Science), now, as the primary venue.** It is the unique venue where every constraint points the same way: an arXiv-overlay journal (your Phase 3 step *is* its prerequisite), diamond open access with zero fees, copyright retained, no anonymization, solo-author-friendly, 50-page ceiling (we use 16), ~9-month target turnaround, indexed in Scopus/WoS/DBLP/MathSciNet.

**Track B — in parallel, a 4-page "Database Theory in Action" note to ICDT 2027** (deadline Sep 3/10, 2026). A short, non-anonymous showcase track explicitly inviting connections between database theory and neighboring communities; it places the work in front of the exact CALM-lineage program committee at a 4-page cost, without colliding with Track A.

**Track C — CPP 2027 only if you decide you want the formal-methods community specifically** (deadline expected ~mid-Sep 2026 by pattern; CFP not yet out). It replaces, not supplements, an immediate LMCS submission and costs a real restructuring. Default: skip.

Not recommended: ICDT regular track, PODS, JAR/TCS (reasons in §7).

---

## 2. What the paper is, to each community

| Reading | Headline for that audience | Venue family |
|---|---|---|
| Database theory | A localization of the CALM boundary with a new axis CALM lacks — content-addressed *identity* — plus the trilemma and forced-resolution architecture, with corpus-scale evidence | ICDT / PODS / LMCS (DB-logic editors) |
| Formal methods | A fully constructive, self-contained, mathlib-free Lean development: closure algebra + Theorem 4 + axiom-free H1/H2 discharges + a `decide`-proved impossibility witness | CPP / ITP / JAR |
| Logic in CS (journal) | Closure-operator growth theory under content addressing, mechanized and measured | **LMCS** — the only venue that takes all three readings at once |

The paper as written (v2.1) is already in journal shape: full proofs, verification apparatus, empirics, 16 pages. That is LMCS-native and conference-hostile (every conference below requires surgery).

## 3. Verified venue matrix

| Venue | Type | Deadline / timeline | Format | Fit | Gate | Cost / OA | Paper surgery needed |
|---|---|---|---|---|---|---|---|
| **LMCS** | journal (arXiv overlay) | none — submit when arXiv ID exists; first editor contact ≤ 2 weeks; ~9 mo to publication | ≤ 50 pp; `lmcs.cls` only at final version | ★★★★★ | high but solo-friendly; 2–3 referees, "excellent" bar | free, diamond OA, CC BY, author keeps © | **none now** (cls conversion only on acceptance) |
| **ICDT 2027 — Database Theory in Action** | conf. short track | abstract **Sep 3** / paper **Sep 10, 2026**; notify Dec 1; conf. Lille Apr 6–9, 2027 | 4 pp + refs, LIPIcs, **not** anonymous; title must start "Database Theory in Action:" | ★★★★☆ | moderate; explicitly cross-community; may be based on work published elsewhere | LIPIcs OA | new 4-page note (1 session) |
| **CPP 2027** | conf. (ACM SIGPLAN, w/ POPL, Jan 2027) | CFP pending; pattern: abstract ~Sep 8–10, paper ~Sep 15–17, 2026 | ACM SIGPLAN 2-col 10 pt, anonymized, supplementary artifact uploaded at submission | ★★★☆☆ | high; competes with large-scale formalizations — ours is elegant but compact (~550 lines) | ACM | full restructure around the formalization narrative |
| ICDT 2027 — regular | conf. | same Sep cycle | 15 pp LIPIcs, anonymized | ★★☆☆☆ | highest here for this paper: the core boundary is (correctly) presented as a CALM instance, so the *depth* novelty for ICDT taste is the conceptual identity axis — thin for a regular-track theory bar; Lean/empirics are not ICDT currency | LIPIcs OA | major; and weakens the LMCS path |
| PODS 2027 | conf./journal hybrid | cycles mid/late 2026 | 15 pp, anonymized | ★★☆☆☆ | hardest; **ACM rule: cannot be under review anywhere else** — blocks Track A entirely | ACM | major |
| JAR | journal (Springer) | none | — | ★★★☆☆ (formalization reading) | moderate | hybrid: OA costs APC | reframe toward proof engineering |
| TCS | journal (Elsevier) | none | — | ★★★☆☆ | moderate, slow | hybrid | minor |

Notable PC fact: the ICDT 2027 committee includes **Bas Ketsman** (co-author of the weakened-monotonicity answer to CALM that the paper cites) and **Floris Geerts** (senior PC), with **Dan Suciu** senior PC — the audience that recognizes the contribution in one read sits on this PC. That cuts both ways: instant comprehension, and zero tolerance for overclaiming. The v2 repositioning (Phase 1) was built for exactly this reader.

## 4. Constraint analysis for this author

1. **Solo, cross-domain, medical affiliation.** LMCS reviews non-anonymously but its culture is content-first and the editor model (you pick the editor) routes the paper to someone who reads it natively. ICDT regular/PODS are anonymized — which *neutralizes* the affiliation prior — but their bar punishes breadth-over-depth, which is this paper's shape.
2. **Cost.** LMCS and LIPIcs venues: zero. JAR OA: APC. Decisive at the margin.
3. **Speed to citable peer review.** LMCS ~9 months from a submission you can make as soon as the arXiv ID exists. Every conference path waits for Sep deadlines + Dec notifications + 2027 proceedings.
4. **Claim ladder as asset.** LMCS referees can rerun all three rungs; the verification artifact does the credibility work that affiliation usually does. This is the venue where the artifact's value is maximal.

## 5. Track A — LMCS execution

Verified mechanics: submission requires the paper to already be a CoRR/arXiv preprint with subject at least cs.LO; you submit the *arXiv version* (correct version number if several) and choose **exactly one** handling editor from the live board; acknowledgment is immediate, editor contact within two weeks; 2–3 referees; outcomes accept / revise / reject; ≤ 50 pages; abstract ≤ ~20 lines avoiding math symbols where possible (final-version concern); `lmcs.cls` with `alphaurl` bibliography and `\lmcsorcid{}` required only for the accepted version (note: their style forbids `lmodern`/`times` font packages — irrelevant until acceptance).

**Ordered actions:**
1. Push repo + Zenodo toggle + tag (RELEASE_CHECKLIST steps 1–6) — pending, ~10 min.
2. arXiv submission per `arxiv/SUBMISSION_arxiv.md` — pending; endorsement lead time budgeted.
3. arXiv announcement → ID exists → create episciences account (ORCID-linked).
4. Submit at lmcs.episciences.org → "Submit": arXiv ID + version, choose handling editor, paste note to editor (below).
5. Calendar a check at +2 weeks (editor contact) and +6 months (status nudge if silent).

**Handling-editor candidates** (from the live board's listed topics — choose ONE):
- **Diego Figueira** — *Automata and logic, Database theory, Finite model theory.* Primary recommendation: the paper's lead framing is database-theoretic (CALM, chase, semi-naive), and he reads that natively.
- **Maurizio Lenzerini** — *Database theory, Logic for knowledge representation.* Strong alternate; the KR angle (knowledge-store growth) is his home ground.
- **Assia Mahboubi** — *Type theory and constructive mathematics, Formalized mathematics, Interactive proof checking.* The pick **only if** you decide to lead with the verification narrative instead.

Decision inside the decision: lead with content (Figueira/Lenzerini), not apparatus (Mahboubi). The Lean development strengthens a DB-logic submission; a DB result does not strengthen a formalization submission of this size.

**Note to editor (paste-ready, ≤ 10 lines):**

> Dear Professor [name],
>
> I am submitting "Monotone Growth of Content-Addressed Rule Closures" (arXiv:XXXX.XXXXX, v[N]) for consideration at LMCS. The paper develops the growth theory of least-fixpoint closures over content-addressed stores — conservativity as Merkle-stable embedding, frontier-local incremental closure, ingestion confluence, continuity — and localizes the CALM monotonicity boundary in this format, yielding a conservativity / history-independence / maximal-parsimony trilemma whose identity axis CALM does not express. All theorems, including semi-naive frontier locality and the discharge of the standing hypotheses from the rule format, are kernel-checked in a self-contained constructive Lean 4 development included with the arXiv record as ancillary files, alongside a reference implementation, a randomized property suite, and corpus-scale measurements; the repository link and Zenodo DOI are on the title page. The paper is not under review elsewhere. A note on positioning: following a prior-art sweep, Theorem 11 is explicitly presented as an instance of the CALM boundary, with the trilemma formulation, the MDL localization, and the mechanization claimed as the contributions.
>
> Thank you for considering it. — Behnam Sour (ORCID 0009-0002-3176-1956)

## 6. Track B — ICDT 2027 "Database Theory in Action"

Verified: 4 pages + references, **non-anonymous**, LIPIcs style, title must begin "Database Theory in Action:", explicitly may be based on a previously published paper at another venue, explicitly inviting connections to Distributed Computing / KR / neighboring communities. Cycle-2 dates: abstract Sep 3, paper Sep 10, 2026; notification Dec 1, 2026; conference Lille, Apr 6–9, 2027.

Proposed note: **"Database Theory in Action: the CALM boundary in content-addressed knowledge stores"** — 4 pages distilling the dictionary (oblivious ↔ payload-determined, confluence ↔ history independence), the identity axis, the trilemma with the live retracted-address witness, and the Moby-Dick number (~10^80.7) as the one-figure punchline; the full paper cited as the arXiv/LMCS-under-review version.

Compatibility: this is a different, shorter, derivative paper — the Action track is designed for exactly this relationship, and LMCS's originality policy concerns the submitted paper itself. Residual caution: one two-line email to the PC chair (Stijn Vansummeren) confirming that "based on" covers an arXiv preprint under journal review costs nothing and removes all doubt. I can draft the 4-pager and the chair email on request — that is Phase 5b.

## 7. Why not the others

- **ICDT regular:** after the honest CALM repositioning, the regular-track-depth claim rests on the identity axis + mechanization + resolutions — a conceptual contribution profile that ICDT's regular bar historically treats as soft. Submitting there also forfeits nothing-under-review-elsewhere flexibility for a low-probability shot.
- **PODS:** the ACM concurrent-submission ban blocks the LMCS track entirely while under review; worst exclusivity-to-probability ratio available.
- **CPP 2027:** viable *only* as a deliberate strategy switch — restructure around the formalization (design choices, the mathlib-free decision, constructive engineering of the list lemmas, `decide` witness, axiom audit as result), anonymize, ship the artifact archive, then publish the extended journal version at LMCS afterward (their policy explicitly welcomes extended conference versions). Choose this only if entering the proof-assistant community matters to you as a goal in itself; expected acceptance is honestly medium-low against full-scale formalization papers.
- **JAR / TCS:** fallbacks if LMCS rejects; JAR needs the formalization reframe and APC for OA; TCS is slow and Elsevier.

## 8. Exclusivity map (what may run concurrently)

| Pair | Allowed? |
|---|---|
| arXiv preprint + anything below | yes — every venue here is arXiv-friendly; LMCS *requires* it |
| LMCS (full) + ICDT Action note (4 pp) | yes — different papers; Action track allows other-venue basis; confirm by chair email for zero residual risk |
| LMCS + CPP same content | no — pick a sequence: CPP first, extended LMCS after acceptance |
| Anything + PODS | no — ACM ban on concurrent review |

## 9. Decision rule and default

- Priority = fastest credible peer-reviewed citation, zero cost, paper as-is → **A**, with **B** as the cheap parallel showcase. ← default, executed unless you redirect.
- Priority = entering the formal-methods community → **C** in September, then extended-A in 2027.
- A and C are the only mutually exclusive choice; B composes with either.

## 10. Calendar (from today, 2026-06-11)

| When | What |
|---|---|
| now | push repo · Zenodo DOI · tag v1.3.0 (10 min, RELEASE_CHECKLIST) |
| now + endorsement lead | arXiv submit (pack ready) |
| arXiv ID + 1 day | LMCS submit (editor: Figueira; note above) |
| by Aug 2026 | decide on Track B; if yes, I draft the 4-pager (Phase 5b) |
| **Sep 3 / Sep 10, 2026** | ICDT Action abstract / paper deadlines |
| ~Sep 2026 | CPP 2027 deadline window — relevant only under the C switch |
| Dec 1, 2026 | ICDT notification |
| ~Q1–Q2 2027 | expected LMCS first decision window |
