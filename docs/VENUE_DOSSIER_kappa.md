# Venue dossier — κ-correspondence paper v1

**M6 deliverable** · venue facts carried from the growth dossier (verified live 2026-06-11) where shared; items not re-verified are marked · all deadlines AoE

---

## 1. Recommendation (read this first)

**Track A — arXiv now, then LMCS as the primary peer venue, staggered behind the growth paper.** Same logic that won for paper 1, with one addition specific to this paper: the κ paper is the most cross-community of the trilogy (security + DB theory + data structures + build systems), and LMCS remains the only venue where all readings land at once, with no deadline, no fee, no anonymization, and a 50-page ceiling we don't approach (10 pp). Sequence: growth paper to LMCS first (it is the foundation this paper cites), κ paper **2–4 weeks later** — same editor model, but don't double-load one editor on day one; the arXiv IDs of papers 1–2 replace the "in preparation" cites before upload.

**Track B — fold this paper into the single ICDT 2027 "Database Theory in Action" note** (abstract Sep 3 / paper Sep 10, 2026 — dates verified for the growth dossier). Do **not** submit two competing 4-page notes from one solo author to one short track. One note, trilogy-wide — "Database Theory in Action: Content-Addressed Rule Closures" — covering the CALM localization (paper 1), the provenance-regime dichotomy and the cone theorem's relation to deletion propagation (papers 2–3), and the correspondence headline. The track explicitly allows work published elsewhere, so it stacks with Track A. The PC fact from the growth dossier doubles in force here: **Ketsman is on the PC and this paper cites Baccaert–Ketsman (PODS 2023) directly** — instant comprehension, zero overclaim tolerance; the related-work generosity built in v0.4 is the armor.

**Track C — CPP, only if you want exactly one of the three papers in front of the formal-methods community: it should be this one.** Unlike paper 1 (★★★ at CPP), the κ paper has a genuine CPP headline: the Determination Theorem and both corollaries axiom-free, `dedup_is_confirmability` deriving a known production attack as a typing fact in the kernel, the whole development mathlib-free and one-command. Honest counterweights: CPP rewards scale and proof-engineering novelty, and this development is elegant-but-compact; submission requires anonymization + restructuring around the formalization narrative; and it replaces, not supplements, an immediate LMCS submission for this paper. Default: **skip, keep LMCS**; revisit only if LMCS rejects with formalization-positive reviews. CPP 2027 CFP still pending (pattern: ~mid-Sep 2026 — **verify at CFP**).

**Spin-off option (hold, do not start now) — PoPETs.** The erasure triangle + tag dial + measured price of deniability is a self-contained privacy paper (GDPR Art. 17 erasure economics; quarterly deadlines). Two reasons to hold: (i) the local-cousin risk is maximal there — Harnik/MLE-literate reviewers will read the triangle first and the unification last; (ii) it cannibalizes §4–6 of the LMCS submission while that is under review. Decision point: after the LMCS outcome.

**Not recommended:** PODS (concurrent-review ban blocks Track A; breadth-over-depth shape penalized), ICDT regular track (same reasons as paper 1, plus this paper is even less LIPIcs-theory-shaped), CCS/S&P/USENIX as primary (this is not an attack/defense paper; the security content is one vertex of a correspondence), JAR (APC; captures only the formalization reading).

## 2. What the paper is, to each community

| Reading | Headline for that audience | Venue family |
|---|---|---|
| Database theory | Deletion propagation made optimization-free by premise inscription; the inscription-or-provenance dichotomy with a conservation law; κ4 as the CALM slice of one determination statement | ICDT-DTiA / LMCS |
| Formal methods | An axiom-free, mathlib-free Lean 4 development in which storage guarantees are FDs and a production side-channel derives as a one-line typing fact (`dedup_is_confirmability`) | CPP / ITP / LMCS |
| Security & privacy | The dedup/audit/deniability triangle is tight; all three pairs achievable; deniability priced on a corpus with an explicit λ exchange rate | PoPETs (spin-off) |
| Systems / build | The first formal account of the input-addressed vs content-addressed dilemma Nix documents in RFC 0062 | CIDR-flavored exposure via DTiA note |
| Logic in CS (journal) | All four readings at once, on a kernel-checked spine | **LMCS** |

## 3. Venue matrix (delta from growth dossier)

| Venue | Fit (this paper) | Change vs paper 1 | Why |
|---|---|---|---|
| **LMCS** | ★★★★★ | = | journal-shaped as written; cross-community is a feature there |
| **ICDT 2027 DTiA (trilogy note)** | ★★★★☆ | = | one note for three papers, not three notes |
| **CPP 2027** | ★★★★☆ | **↑ from ★★★☆☆** | Unified namespace is a real formalization headline; still costs restructure + anonymity, still either/or with LMCS |
| PoPETs | ★★★☆☆ (spin-off only) | new | triangle+dial+O5 self-contained; local-cousin risk highest |
| ICDT regular / PODS | ★★☆☆☆ / blocked | = | unchanged |
| JAR / TCS | ★★★☆☆ | = | unchanged |

## 4. Constraint analysis (unchanged from paper 1, one addition)

Solo author, medical affiliation, zero budget, speed-to-citable: all four constraints again point at LMCS (editor-routed, diamond OA, no deadline, artifact does the credibility work). The addition: **the trilogy is now a portfolio.** Reviewers of any one paper will look up the others; arXiv-first for all three, with consistent cross-references and the shared Lean file shipped identically in each `anc/`, makes the portfolio self-verifying. The packaging-bug lesson from v1.4.1 applies with force: the **extended** Lean file must be the top-level file in every bundle.

## 5. Execution order

1. Produce the pdflatex-compatible variant of `kappa_paper_v1.tex` (fontspec → lmodern; see SUBMISSION_kappa.md §compile-path) and clean-room test.
2. Upload growth paper to arXiv (its pack is ready) → obtain ID.
3. Swap `\cite{growth}` / `\cite{deletion}` placeholders to arXiv IDs in this paper; upload κ pack → ID.
4. Submit growth to LMCS; κ to LMCS at +2–4 weeks.
5. By Aug 2026: decide on the single DTiA trilogy note (4 pp; ~2 sessions of work).
6. Camera-ready duties whenever triggered: verify Mokhov et al. (ICFP 2018) before citing; clear residual sweep list (Unison, Git/IPLD formalisms, incremental chase).
