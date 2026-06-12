# Prior-art sweep — round 2: the κ-correspondence and the Determination Theorem

**Sweep date 2026-06-11 · feeds κ nucleus v0.4 · companion to `prior_art_thm11.md` (round 1)**

---

## 1. Executive verdict

**Nothing in the swept literature states the κ-correspondence, the Determination Theorem, the necessity converse (O1), or the erasure triangle as such. But every vertex and edge has a near neighbor in some community, and three of them are close enough that the paper's identity must be declared as *the unifying formal frame plus the kernel-checked converse*, with each neighbor placed as an instance.** The related-work section is load-bearing; written generously, the neighbors strengthen the paper (the frame explains deployed, documented trade-offs); written thinly, any one of three referees — security, database theory, build systems — will find their community's version first and read the paper as rediscovery.

The three closest neighbors:

1. **Harnik–Pinkas–Shulman-Peleg (IEEE S&P Mag. 2010): dedup as an existence side-channel.** Cross-user deduplication deterministically answers "does this file exist?" — the confirmation attack, in production systems, fifteen years ago. **This is the systems form of the two-observer identity.** The paper's claim must be: the *typing* of that observation (dedup and confirmability are one determination at two stations), its one-line kernel derivation, and its placement inside closure theory — not the observation itself.
2. **Nix's input-addressed vs content-addressed derivations (Dolstra's thesis; RFC 0062): the κ dial, deployed.** Output path = hash of the *derivation* (premises ⊆ κ) vs hash of the *output content* (κ = content) is a live, ecosystem-scale design debate with exactly the predicted trade-offs: input addressing gives eval-time-stable references but requires trust signatures and propagates rebuilds; content addressing gives early cutoff (= the dedup schema at output granularity) and signature-free verification (= the confirmability clause, and its dark side). **The correspondence is the missing formal account of a documented engineering dilemma — say so, prominently; it is the paper's best evidence of reach.**
3. **Hartline et al. (2002): strongly history-independent ⟺ canonical representation.** The growth paper's canonical serialization + fingerprint is, in their vocabulary, a canonical representation — so the store is *strongly history-independent for free*. Cite as an instance gained, not a threat.

## 2. Neighbor map

| cluster | key results (verified) | relation to the κ paper | action |
|---|---|---|---|
| **CALM follow-ons** | Bloom^L (Conway–Marczak–Alvaro–Hellerstein–Maier, SoCC 2012): lattices + cross-lattice morphisms extend CALM beyond sets. Keep CALM and CRDT On (Laddad–Power–Milano–Cheung–Crooks–Hellerstein, PVLDB 16(4), 2022): monotone *queries* over CRDTs. Free Termination (Power, ICDT 2025); Baccaert–Ketsman (PODS 2023): coordination with global knowledge. | All on the order/monotonicity axis; none has identity. The 2P closure's order-extension move is the Bloom^L move — cite at deletion §two-phase. | cite 4; one differentiating sentence each |
| **Dedup security** | Harnik et al. 2010 (side channel); Halevi–Harnik–Pinkas–Shulman-Peleg, CCS 2011 (proofs of ownership — dedup as access oracle); Douceur et al., ICDCS 2002 (convergent encryption); Bellare–Keelveedhi–Ristenpart: MLE, EUROCRYPT 2013 + DupLESS, USENIX Sec 2013 (formal games for the DEDUP/confidentiality edge); defense line (random thresholds, RARE, randomized MLE). | The triangle's DEDUP/DEN edge is this community's home turf; AUDIT-of-deletion axis and the determination typing are absent there. | already cite Douceur/DupLESS; **add Harnik 2010 + Halevi 2011 + MLE EUROCRYPT 2013**; recast two-observer remark as "the typing of Harnik et al.'s observation" |
| **History independence** | Micciancio (STOC 1997, oblivious trees — origin); Naor–Teague (STOC 2001, anti-persistence: representation reveals nothing of history; motivation includes deleted data); Hartline et al. 2002 (SHI ⟺ canonical representation); HI cuckoo hashing (ICALP 2008); HI sparse tables (PODS 2016); auditable HI structures (Goodrich et al.). | Their HIST is *physical-representation*-level; growth Thm 5 is *canonical-state*-level. Bridge: content addressing supplies Hartline-style canonical representations for free ⇒ the store is SHI. Their deleted-data privacy motivation is DEN's ancestor. | cite Micciancio, Naor–Teague, Hartline; one bridge sentence in related work |
| **Secure deletion** | Reardon–Basin–Čapkun, SoK: Secure Data Deletion, IEEE S&P 2013 (taxonomy of erasure: physical media to systems). | The erasure §'s systems frame; the κ paper adds the identity-layer cut (what *addresses* retain) absent from the SoK. | cite in erasure remark |
| **Deletion propagation** | Buneman–Khanna–Tan, PODS 2002 (P vs NP-hard dichotomy for side-effect-minimizing deletion; why-provenance ICDT 2001); Cong–Fan–Geerts (key preservation ⇒ tractable); Kimelfeld–Vondrák–Williams (head-domination dichotomy/trichotomy); Kimelfeld PODS 2012 (with FDs). | Their problem *optimizes among alternative derivations*; the cone theorem makes propagation trivial because premise inscription removes alternatives. Key preservation is the relational cousin of premise inscription. | cite BKT + KVW at the cone theorem: "singleton why-provenance ⇒ exact, optimization-free propagation" |
| **Provenance semirings** | Green–Karvounarakis–Tannen, PODS 2007 (+ Green–Tannen PODS 2017 retrospective); ORCHESTRA explicitly lists incremental deletion propagation via maintainable provenance. | Branch (ii) of the O1 dichotomy *is* provenance-polynomial bookkeeping; N[X]-style records are exactly the derivation multiset whose size the conservation remark counts. | cite GKT at Corollary dichotomy; rename branch (ii) "the provenance regime" |
| **Build systems / Nix** | Dolstra PhD thesis 2006 (intensional vs extensional store); NixOS RFC 0062 (CA derivations: early cutoff, trust model, eval-time path loss); Nix manuals (input-addressed needs signatures; CA verifiable without). | The κ dial deployed; clauses (a)–(d) predict each documented trade-off. | **new paragraph in §dial**; cite thesis + RFC; flag *Build Systems à la Carte* (Mokhov–Mitchell–Peyton Jones, ICFP 2018) for early-cutoff theory — **verify before camera-ready** (not independently verified this sweep) |
| **FD theory** | Armstrong, IFIP 1974 (already cited in v0.3). | Determination = FD; antitone lattice = Armstrong closures; recursive clause is the non-FD part. | already placed; keep |

## 3. What survives as the paper's own (post-round-2)

1. **The Determination Theorem as a unification** — no swept work states guarantee ⟺ determination-on-committed-features across dedup/stability/confirmation/identity, with a kernel-checked core.
2. **The necessity converse (O1)** and the **dichotomy with the conservation law** (blow-up paid in parts or in provenance records — the bridge between Prop 10 and GKT bookkeeping).
3. **The two-observer *typing*** (the observation is Harnik et al.'s; the identification of dedup and confirmability as one predicate, and its derivation, is new).
4. **The erasure triangle's AUDIT axis and tightness** (MLE has the DEDUP/DEN edge; deletion-audit as a vertex with achievability rows, and selective audit under salting, appear nowhere swept).
5. **The tag dial's three-axis separation** (mutability/entropy/granularity) and its account of the Nix dilemma.
6. The whole apparatus standing on a one-command, axiom-audited Lean development — none of the neighbor communities couples their result to a kernel artifact.

## 4. Drop-in edits for nucleus v0.4

1. **§triangle, Remark (selective audit):** open with "The mechanism is the convergent-encryption trade-off [Douceur02, Bellare13-MLE], and the confirmation attack was demonstrated against production cloud dedup by Harnik, Pinkas & Shulman-Peleg [Harnik10] — Corollary (two-observer) is the typing of their observation." Add Halevi et al. [Halevi11] for dedup-as-access-oracle.
2. **§dial, new closing paragraph:** the Nix paragraph (input-addressed = premises-committed; CA = content-committed; early cutoff = schema (b); signature-free verification and its trust concerns = schema (d) and the two-observer identity), citing Dolstra's thesis and RFC 0062.
3. **§o1, Corollary (dichotomy):** rename branch (ii) "the provenance regime," cite [GKT07]; at the cone-theorem mention, cite [BKT02, KVW] with the "no alternatives ⇒ no optimization problem" sentence.
4. **New §Related work** before Status: seven short blocks per the neighbor map, including the Hartline SHI bridge and the CALM-follow-on quartet.
5. **Bibliography adds (all existence-verified this sweep):** Harnik10, Halevi11, BKR-MLE-Eurocrypt13, Micciancio97, NaorTeague01, Hartline02, Reardon13, BKT02, KimelfeldVW, GKT07, Conway12-BloomL, Laddad22, Power25, BaccaertKetsman23, Dolstra06, NixRFC062. Flagged for verification before camera-ready: Mokhov18.

## 5. Residual risks (honest scope)

- **Not exhaustively swept:** formal treatments of Git/IPLD/UCAN identity semantics; Unison's content-addressed code model (likely a systems sibling of κ₀-for-code — skim before camera-ready); recent PODS/ICDT incremental-chase maintenance (carried over from round 1); the randomized-MLE defense line in depth.
- **Confidence:** high that the unified statement, the converse, the AUDIT axis, and the dial's three-axis separation are unclaimed; certain that every individual edge has a community cousin that must be cited generously.
- **Strategic note:** with this density of neighbors, the venue should value unification + mechanization (database theory or formal-methods adjacent) rather than any single community's home turf, where the local cousin will dominate the review.
