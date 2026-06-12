# Prior-art sweep — Theorem 11 and the growth trilemma

**Phase 1 deliverable** · sweep date 2026-06-11 · feeds paper v2 (Phase 2)

---

## 1. Executive verdict

**The bare mathematical kernel of Theorem 11 is not novel. The packaging is.**

Two prior results cover the kernel:

1. **Non-monotonicity of extremal aggregation is classical database theory.**
   Ross & Sagiv (PODS 1992; JCSS 1997) built an entire semantics for
   aggregates-in-recursion around the requirement of monotonicity with respect
   to lattice orders, precisely because max-style aggregates over growing sets
   break monotone fixpoint semantics. A database referee will read
   "Φ_max is non-monotone" as textbook.

2. **The deep, general version is the CALM theorem.** Conjectured by
   Hellerstein (PODS 2010 keynote), proved by Ameloot, Neven & Van den Bussche
   (PODS 2011; J. ACM 60(2), 2013), popularized in Hellerstein & Alvaro
   (CACM 63(9), 2020): *a problem has a consistent, coordination-free
   distributed implementation if and only if it is monotone.* Under the
   correspondence dictionary in §3 below, Theorem 11 is a content-addressed,
   MDL-flavored **instance of the CALM "only-if" boundary**: maximality is
   non-monotone, therefore not implementable by oblivious (payload-determined)
   side conditions, and demanding it in storage forces non-monotone updates —
   i.e., retraction.

**What survives as a defensible contribution (§4): the trilemma formulation
with address-stable conservativity, payload-determinism as the exact boundary
in the MDL/binding rule format, the decidable machine-checked witness, and the
resolution architecture mapped onto the trilemma faces.** None of these appear
in the swept literature in this form.

**Action required before arXiv:** reposition Theorem 11 from "we prove an
impossibility theorem" to "we sharpen and mechanize the known monotonicity
boundary in this rule format" — drop-in edits in §5. This is not a demotion;
attaching the result to a celebrated theorem strengthens the paper and
pre-empts the referee's first objection.

---

## 2. Neighbor map

| Literature | Key result | Relation to this paper | Verdict |
|---|---|---|---|
| **CALM** — Hellerstein 2010; Ameloot–Neven–Van den Bussche 2013; Hellerstein–Alvaro 2020 | Consistent + coordination-free ⟺ monotone; proved via relational transducer networks; the syntactic class of **oblivious** transducers captures exactly the monotone queries | Thm 11 ≈ the only-if direction instantiated for maximal bindings; "payload-determined" ≈ "oblivious"; (H) history-independence ≈ their confluence-based consistency | **Must cite; must reposition Thm 11 relative to it** |
| **Weakened monotonicity** — Ameloot–Ketsman–Neven–Zinn (PODS 2014; TODS 40(4), 2015); Zinn–Green–Ludäscher (ICDT 2012) | Non-monotone queries (e.g. win-move) become coordination-free given knowledge of data distribution; hierarchy of weaker monotonicities ⟷ larger coordination-free classes | Mirrors §6 resolutions: extra seed-level knowledge (versioned cohorts) buys back what payload-determinism forbids | Cite in §6/§8; one sentence drawing the parallel |
| **Monotonic aggregation** — Ross–Sagiv (PODS 1992; JCSS 54(1):79–97, 1997); Van Gelder (DOOD 1993) | Aggregates in recursion require lattice-monotonicity; non-monotone aggregates (max over growing sets) must be stratified | The folklore kernel of Thm 11; also the lineage for the MDL side condition as a "monotone aggregate" | Cite in §5 and §8 |
| **Incremental view maintenance** — Gupta–Mumick–Subrahmanian (SIGMOD 1993, 157–166): counting + **DRed** | Views with negation/aggregation need over-delete + rederive on updates | Already cited; sharpen: DRed's deletion machinery is exactly what storing Φ_max re-imports, and what Thm 2 removes | Keep; tighten the sentence |
| **Chase / data exchange** — Fagin–Kolaitis–Miller–Popa (ICDT 2003; TCS 336(1), 2005); Marnette (PODS 2009): Skolem chase | TGD saturation; Skolem chase determinism; oblivious-termination analysis | Already cited informally; Marnette 2009 is the precise anchor for "content addressing = collision-resistant Skolemization, confluence = chase determinism" | Add Marnette to §8 |
| **CRDTs / Merkle-CRDTs** — Shapiro et al. (SSS 2011); Sanjuán–Pöyhtäri–Teixeira–Psaras (arXiv:2004.00107, 2020) | Join-semilattice merge ⇒ convergence; Merkle-DAGs as causality/convergence substrate | The G-Set remark in §3 of the paper; Merkle-CRDTs is the closest *systems* sibling (Merkle-DAG + monotone merge) but states no generation/closure theory and no parsimony impossibility | Cite both; one sentence of differentiation |
| **Content-addressed knowledge stores** — IPFS/IPLD; Git; recent content-addressable hypergraph systems | Merkle-DAG identity, dedup, immutability | Infrastructure lineage only; none states growth theorems or the trilemma | Already covered via Merkle 1987; optional |

Nothing in the sweep states (a) conservativity as *address-stable embedding*,
(b) the three-way C/H/P trilemma, or (c) an MDL-admissibility rule format with
a mechanized impossibility witness.

---

## 3. Correspondence dictionary (CALM ↔ this paper)

| CALM / transducer-network term | This paper |
|---|---|
| consistency (= confluence: same output for any ordering/batching of inputs) | **(H)** history independence (Thm 5) |
| coordination-free | computable under **payload-determined** side conditions (H2) |
| oblivious transducer (decides without global knowledge) | payload-determined rule (decides from premise payloads alone) |
| monotone query | `Mono Φ` / Lemma A persistence |
| non-monotone query requires coordination | maximality requires seed-global knowledge (Thm 11) |
| coordination | retraction + global re-binding (loss of **(C)**) |
| distribution-aware relaxations (Zinn et al.) | seed-level knowledge resolutions (§6.2 versioned cohorts) |

The one element with **no CALM counterpart** is (C) as *content-addressed*
conservativity: stages embed at identical hashes, references never dangle.
CALM's vocabulary has no notion of part identity at all. That is the wedge the
trilemma adds.

---

## 4. What survives as novel — the defensible claim set

1. **The trilemma formulation.** (C) conservativity-as-Merkle-embedding,
   (H) history independence, (P) extensional maximal parsimony, with
   (C)∧(P) already contradictory, complete field = (C)∧(H), quotient view =
   (H)∧(P). CALM relates two of these notions (H ↔ monotonicity); the
   three-way statement over a content-addressed store is unstated prior art.
2. **Payload-determinism as the exact boundary in the MDL/binding format.**
   Theorem 11's specific statement — no payload-determined side condition
   realizes ⊆-maximal admissible bindings at every seed — plus the corollary
   that codebook *globality* is precisely the non-monotone ingredient of MDL.
   The MDL ↔ CALM-boundary connection appears new.
3. **The mechanized witness.** A `decide`-proved impossibility instance and a
   constructive (choice-free) Lean closure algebra; no swept work couples a
   CALM-type boundary to a kernel-checked artifact.
4. **The resolution architecture as trilemma faces** with the design
   principle *monotone, complete storage; parsimonious views* — echoing
   CALM-inspired systems practice but stated and proved for content-addressed
   closure stores.

---

## 5. Drop-in edits for paper v2

### 5.1 §5, insert immediately after Theorem 11's proof (positioning paragraph)

> **Positioning.** Theorem 11 should be read as a content-addressed,
> MDL-flavored instance of a known boundary rather than a new phenomenon.
> That extremal aggregation is non-monotone is classical: semantics for
> aggregates inside recursion require monotonicity with respect to a lattice
> order precisely because operators like "maximal set" break it [Ross–Sagiv].
> The general form of the boundary is the CALM theorem [Hellerstein–Alvaro;
> Ameloot–Neven–Van den Bussche]: a problem has a consistent,
> coordination-free implementation iff it is monotone, where "consistency" is
> confluence over input orderings — our history independence — and where the
> coordination-free computations are captured by *oblivious* transducers,
> deciding without global knowledge, exactly as our payload-determined side
> conditions decide from premise payloads alone. Under this dictionary,
> Theorem 11 instantiates the only-if direction for maximal bindings, and
> Corollary 12 adds the element CALM does not speak of: identity. In a
> content-addressed store, the cost of non-monotonicity is not abstract
> "coordination" but the retraction of named, referenced parts. The
> contribution claimed here is accordingly the trilemma formulation with
> address-stable conservativity, the localization of the boundary at MDL
> codebook globality, and the mechanized witness — not the existence of the
> boundary itself.

### 5.2 §6, one sentence at the end of §6.2 (versioned cohorts)

> This resolution is the storage-layer analogue of the distribution-aware
> relaxations of CALM [Zinn–Green–Ludäscher; Ameloot–Ketsman–Neven–Zinn]:
> granting the system knowledge beyond individual payloads (here, the cohort
> version chain) buys back behavior that obliviousness forbids.

### 5.3 §8, replace the "Selection as set cover" block's neighbors with two new blocks

> **Monotonicity boundaries.** The CALM conjecture [Hellerstein 2010], proved
> via relational transducer networks [Ameloot–Neven–Van den Bussche 2013] and
> surveyed in [Hellerstein–Alvaro 2020], equates coordination-free consistency
> with logical monotonicity; weakened monotonicities enlarge the
> coordination-free class [Ameloot–Ketsman–Neven–Zinn 2015;
> Zinn–Green–Ludäscher 2012]. Non-monotonicity of aggregates in recursion is
> classical [Ross–Sagiv 1992/1997]. Theorem 11 instantiates this boundary in
> the content-addressed MDL format; §5.1's positioning paragraph gives the
> dictionary.
>
> **Merkle-replicated state.** Merkle-CRDTs [Sanjuán et al. 2020] combine
> Merkle-DAGs with join-semilattice merge for convergent replication; the
> present work differs in studying the *generation* of the DAG by a rule
> closure and the parsimony impossibility, not replication. Content
> addressing as collision-resistant Skolemization places the closure in the
> Skolem-chase regime [Marnette 2009].

### 5.4 Abstract, replace "we prove an impossibility theorem"

> ...and we localize a known monotonicity boundary (CALM) in this rule
> format: no payload-determined side condition can store exactly the maximal
> bindings at every seed (Theorem 11, with a machine-checked witness), giving
> a trilemma between conservativity, history independence, and extensional
> maximal parsimony.

---

## 6. Verified citation list (add to v2 bibliography)

All entries below were verified to exist during this sweep (venue/pages as
confirmed by the indexed sources):

- J. M. Hellerstein. *The Declarative Imperative: Experiences and Conjectures
  in Distributed Logic.* SIGMOD Record 39(1), 2010 (PODS 2010 keynote;
  origin of the CALM conjecture).
- T. J. Ameloot, F. Neven, J. Van den Bussche. *Relational transducers for
  declarative networking.* PODS 2011, 283–292; J. ACM 60(2), Article 15, 2013.
  (Proof of CALM; oblivious transducers ⟷ monotone queries.)
- J. M. Hellerstein, P. Alvaro. *Keeping CALM: When Distributed Consistency
  Is Easy.* CACM 63(9), 2020 (also arXiv:1901.01930).
- T. J. Ameloot, B. Ketsman, F. Neven, D. Zinn. *Weaker Forms of Monotonicity
  for Declarative Networking: A More Fine-Grained Answer to the
  CALM-Conjecture.* PODS 2014, 64–75; TODS 40(4), Article 21, 2015.
- D. Zinn, T. J. Green, B. Ludäscher. *Win-move is coordination-free
  (sometimes).* ICDT 2012, 99–113.
- K. A. Ross, Y. Sagiv. *Monotonic Aggregation in Deductive Databases.*
  PODS 1992, 114–126; JCSS 54(1):79–97, 1997.
- A. Gupta, I. S. Mumick, V. S. Subrahmanian. *Maintaining Views
  Incrementally.* SIGMOD 1993, 157–166. (Counting + DRed.)
- B. Marnette. *Generalized Schema-Mappings: From Termination to
  Tractability.* PODS 2009, 13–22. (Skolem/oblivious chase.)
- R. Fagin, P. G. Kolaitis, R. J. Miller, L. Popa. *Data Exchange: Semantics
  and Query Answering.* ICDT 2003, 207–224; TCS 336(1):89–124, 2005.
- M. Shapiro, N. Preguiça, C. Baquero, M. Zawirski. *Conflict-free Replicated
  Data Types.* SSS 2011.
- H. Sanjuán, S. Pöyhtäri, P. Teixeira, Y. Psaras. *Merkle-CRDTs: Merkle-DAGs
  meet CRDTs.* arXiv:2004.00107, 2020.

(Existing v1 citations — Tarski, Kleene, van Emden–Kowalski, Bancilhon,
Ullman, Rissanen, Grünwald, Merkle, Chvátal — unchanged.)

---

## 7. Residual risk notes (honest scope of the sweep)

- **Swept:** CALM cluster and its weakenings; aggregation-in-Datalog
  semantics; incremental view maintenance; chase termination/determinism;
  Merkle-CRDT and content-addressed storage lineage.
- **Not exhaustively swept:** the Bloom/Bloom^L/Hydro systems-language papers
  (Conway et al. 2012 onward) and "CALM + CRDT" follow-ons — these are
  systems instantiations of the same boundary and are unlikely to contain the
  trilemma, but a one-pass skim before journal submission (not before arXiv)
  is cheap insurance; likewise recent PODS/ICDT work on incremental chase
  maintenance (2020s).
- **Confidence:** high that the trilemma *formulation* and the mechanized
  MDL-format witness are unclaimed; certain that the bare non-monotonicity of
  maximality is prior art and must be presented as such.
