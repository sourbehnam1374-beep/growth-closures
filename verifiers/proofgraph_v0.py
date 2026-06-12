#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ProofGraph v0  —  the science-mining primitive, made executable.

Bitcoin:  electricity  -> scarcity -> money   (Proof of Work)
ProofGraph: verified cross-domain insight -> scarcity -> value  (Proof of Intersection)

A Kernel is a structured, context-qualified, evidence-graded, content-hashed unit
of knowledge. A Solution Sheet is MINTABLE only when a bundle of kernels passes
Proof of Intersection (PoI) — four closures that must ALL hold:

  1. Intersection gain   : bundle bridges >=2 distant domains via >=1 cross-domain edge
  2. Constraint closure  : no UNRESOLVED `contradicts` edge inside the bundle
  3. Evidence closure    : every load-bearing kernel >= grade C; bundle median >= grade B
  4. Action closure       : the Sheet carries >=1 executable step (a "snake")

The reward is for making a real surface appear — not for posting facts.

Deterministic. Stdlib only. No network. No secrets. Content-addressed (SHA-256).
Honesty rule (SHIVA): DEMONSTRATED != PROVEN. In-prep / single-study claims are
graded down and flagged, even when they are the author's own work.
"""

from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass, field
from typing import Optional

SEED = 42  # determinism marker (no RNG is used; ordering is canonical/sorted)
FIXED_TS = "2026-01-01T00:00:00Z"  # frozen so kernel hashes are reproducible

# ---- evidence grades -------------------------------------------------------
GRADE_VALUE = {"A": 5, "B": 4, "C": 3, "D": 2, "E": 1}
GRADE_C = GRADE_VALUE["C"]
GRADE_B = GRADE_VALUE["B"]

# ---- canonicalization + hashing -------------------------------------------
def canonical(obj) -> str:
    """JCS-style canonical JSON (sorted keys, no spaces). Not full RFC8785, but
    deterministic and sufficient for content addressing in v0."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def merkle_root(leaf_hashes: list[str]) -> str:
    """Standard binary Merkle root over sorted leaves; duplicate last if odd."""
    if not leaf_hashes:
        return sha256("")
    layer = sorted(leaf_hashes)
    while len(layer) > 1:
        if len(layer) % 2 == 1:
            layer.append(layer[-1])
        layer = [sha256(layer[i] + layer[i + 1]) for i in range(0, len(layer), 2)]
    return layer[0]

# ---- kernel ----------------------------------------------------------------
@dataclass
class Kernel:
    kid: str
    ktype: str               # FACT | RELATION | PRINCIPLE | CONSTRAINT | NEGATIVE_RESULT
    claim: str
    domains: list[str]
    grade: str               # A..E
    replication: str         # REPLICATED | SINGLE | THEORY | CONTRADICTED | UNKNOWN
    source: str              # DOI / dataset / internal pointer
    note: str = ""           # honesty flags live here
    flagged: bool = False
    kernel_hash: str = field(default="", init=False)

    def content(self) -> dict:
        # identity = everything except the hash itself and any signatures
        return {
            "kid": self.kid, "ktype": self.ktype, "claim": self.claim,
            "domains": sorted(self.domains), "grade": self.grade,
            "replication": self.replication, "source": self.source,
            "note": self.note, "flagged": self.flagged, "ts": FIXED_TS,
        }

    def finalize(self) -> "Kernel":
        self.kernel_hash = "sha256:" + sha256(canonical(self.content()))
        return self

@dataclass
class Edge:
    src: str
    dst: str
    rel: str                 # supports|implies|equivalent_under_transform|depends_on|contradicts
    resolved: bool = False   # only meaningful for `contradicts`

# ---- the graph + PoI -------------------------------------------------------
class ProofGraph:
    def __init__(self) -> None:
        self.kernels: dict[str, Kernel] = {}
        self.edges: list[Edge] = []

    def add_kernel(self, k: Kernel) -> None:
        self.kernels[k.kid] = k.finalize()

    def add_edge(self, e: Edge) -> None:
        assert e.src in self.kernels and e.dst in self.kernels, f"dangling edge {e.src}->{e.dst}"
        self.edges.append(e)

    def _bundle_edges(self, ids: set[str]) -> list[Edge]:
        return [e for e in self.edges if e.src in ids and e.dst in ids]

    def proof_of_intersection(
        self, bundle: list[str], load_bearing: set[str], executable_path: list[str]
    ) -> dict:
        ids = set(bundle)
        edges = self._bundle_edges(ids)
        K = self.kernels

        # 1. intersection gain
        lb_domains = set()
        for kid in load_bearing:
            lb_domains |= set(K[kid].domains)
        # a cross-domain edge spans >=2 domains across its endpoints and is not
        # domain-identical (so an edge INTO a multi-domain bridge kernel counts).
        cross_edges = []
        for e in edges:
            ds, dd = set(K[e.src].domains), set(K[e.dst].domains)
            if len(ds | dd) >= 2 and ds != dd:
                cross_edges.append(e)
        c1 = len(lb_domains) >= 2 and len(cross_edges) >= 1
        gain_score = round(len(cross_edges) / max(1, len(edges)), 3)

        # 2. constraint closure (no unresolved contradiction)
        unresolved = [(e.src, e.dst) for e in edges if e.rel == "contradicts" and not e.resolved]
        c2 = len(unresolved) == 0

        # 3. evidence closure
        lb_grades = [GRADE_VALUE[K[kid].grade] for kid in load_bearing]
        all_grades = sorted(GRADE_VALUE[K[kid].grade] for kid in bundle)
        median = all_grades[len(all_grades) // 2] if all_grades else 0
        min_lb = min(lb_grades) if lb_grades else 0
        c3 = (min_lb >= GRADE_C) and (median >= GRADE_B)
        flagged = [kid for kid in bundle if K[kid].flagged or GRADE_VALUE[K[kid].grade] <= GRADE_VALUE["D"]]

        # 4. action closure
        c4 = len(executable_path) >= 1

        mintable = c1 and c2 and c3 and c4
        return {
            "mintable": mintable,
            "closures": {
                "1_intersection_gain": {
                    "pass": c1, "domains_bridged": sorted(lb_domains),
                    "cross_domain_edges": [f"{e.src}->{e.dst}" for e in cross_edges],
                    "gain_score": gain_score,
                },
                "2_constraint_closure": {"pass": c2, "unresolved_contradictions": unresolved},
                "3_evidence_closure": {
                    "pass": c3, "min_load_bearing_grade": min_lb,
                    "median_grade": median, "flagged_kernels": flagged,
                },
                "4_action_closure": {"pass": c4, "steps": len(executable_path)},
            },
        }

    def mint_sheet(
        self, sheet_id: str, thesis: str, bundle: list[str],
        load_bearing: set[str], executable_path: list[str],
    ) -> dict:
        poi = self.proof_of_intersection(bundle, load_bearing, executable_path)
        leaves = [self.kernels[k].kernel_hash for k in bundle]
        root = merkle_root(leaves)
        body = {
            "sheet_id": sheet_id, "thesis": thesis,
            "kernels": sorted(bundle), "load_bearing": sorted(load_bearing),
            "executable_path": executable_path, "kernel_merkle_root": root,
            "poi_mintable": poi["mintable"], "ts": FIXED_TS, "seed": SEED,
        }
        sheet_hash = "sha256:" + sha256(canonical(body))
        return {"minted": poi["mintable"], "sheet_hash": sheet_hash,
                "merkle_root": root, "poi": poi, "body": body}

# ---- REAL kernels from the SHIVA corpus -----------------------------------
def build_corpus() -> ProofGraph:
    g = ProofGraph()
    add = g.add_kernel
    # information theory / MDL
    add(Kernel("k01", "PRINCIPLE",
        "A model earns existence only if it compresses its data below the null "
        "description length (MDL/BIC).",
        ["INFOTHEORY"], "B", "THEORY", "Rissanen MDL; Schwarz BIC"))
    add(Kernel("k02", "RELATION",
        "Description-length gain dL = L(null) - L(rule) > 0 is NECESSARY for a rule "
        "to carry information beyond chance.",
        ["INFOTHEORY"], "B", "THEORY", "derived from k01"))
    # orthopedic decision rules (anchors)
    add(Kernel("k03", "FACT",
        "Lewinnek 'safe zone': acetabular cup inclination 40+-10 deg, anteversion "
        "15+-10 deg as THA orientation target.",
        ["ORTHO"], "B", "REPLICATED", "doi:10.2106/00004623-197860020-00014",
        note="widely cited but clinically contested"))
    add(Kernel("k05", "FACT",
        "GAP (Global Alignment & Proportion) score predicts mechanical complications "
        "in adult spinal deformity.",
        ["SPINE"], "A", "REPLICATED", "doi:10.2106/JBJS.16.01594"))
    # RuleAudit worked examples (DEMONSTRATED, not proven -> grade C/SINGLE)
    add(Kernel("k04", "NEGATIVE_RESULT",
        "Under MDL audit the Lewinnek rule shows a structural-fragility signature: it "
        "does not compress dislocation outcomes better than null in modern cohorts.",
        ["ORTHO", "INFOTHEORY"], "C", "SINGLE", "RuleAudit v0.2 worked example",
        note="DEMONSTRATED in RuleAudit, not independently replicated"))
    add(Kernel("k06", "NEGATIVE_RESULT",
        "GAP exhibits a DIFFERENT structural failure signature than Lewinnek under MDL "
        "audit (distinct fragility mode).",
        ["SPINE", "INFOTHEORY"], "C", "SINGLE", "RuleAudit v0.2 worked example",
        note="DEMONSTRATED, single-tool finding"))
    # metrology / reliability
    add(Kernel("k07", "PRINCIPLE",
        "Test-retest reliability defines a minimum detectable change MDC95; any "
        "difference below MDC95 is indistinguishable from measurement noise.",
        ["METROLOGY"], "B", "THEORY", "classical measurement theory"))
    add(Kernel("k08", "FACT",
        "Pelvic ratio R: single-session ICC=0.42 but 6-session-average ICC=0.815 "
        "(95%CI 0.60-0.90); SEM=0.113, MDC95=0.312.",
        ["METROLOGY"], "C", "SINGLE", "R reliability substudy (29 images x 6 sessions)",
        note="single-rater, in preparation"))
    add(Kernel("k09", "FACT",
        "Femoral-head landmarks are ~2x noisier than S1 corners; variance partition = "
        "42% signal / 0% session-drift / 58% random error.",
        ["METROLOGY"], "C", "SINGLE", "R reliability substudy",
        note="in preparation"))
    add(Kernel("k10", "CONSTRAINT",
        "A rule whose decision-boundary spacing is smaller than the MDC95 of its input "
        "measurement cannot be reliably applied at the INDIVIDUAL level.",
        ["METROLOGY", "ORTHO"], "B", "THEORY", "metrology x decision-rule bridge"))
    # morphometry (breadth)
    add(Kernel("k11", "FACT",
        "Coronal-axial knee malalignment resolves into 3 phenotypes incl. two distinct "
        "varus rotational subtypes; ARI=0.845, decision-tree CV accuracy 78.5%.",
        ["ORTHO"], "C", "SINGLE", "knee phenotype study, n=1400 CT",
        note="in preparation"))
    # FLAGGED kernel — honest: references unverified
    add(Kernel("k12", "RELATION",
        "Reported discrimination of audited clinical rules spans AUC 0.50-0.86 across "
        "32 studies / 5,700 patients.",
        ["ORTHO"], "D", "UNKNOWN", "RuleAudit abstract (refs 8,10,11,13)",
        note="FLAGGED: supporting refs unverified; Ref 13 malformed", flagged=True))

    # edges (the chain = causal/logical lineage, not chronology)
    g.add_edge(Edge("k01", "k02", "implies"))
    g.add_edge(Edge("k02", "k04", "supports"))   # INFOTHEORY -> ORTHO   (cross)
    g.add_edge(Edge("k02", "k06", "supports"))   # INFOTHEORY -> SPINE   (cross)
    g.add_edge(Edge("k07", "k10", "implies"))    # METROLOGY  -> METRO/ORTHO
    g.add_edge(Edge("k09", "k08", "supports"))   # FH noise explains low single-ICC
    g.add_edge(Edge("k10", "k04", "supports"))   # METROLOGY -> ORTHO    (cross)
    return g

# ---- run two attempts: one that REFUSES, one that MINTS --------------------
def show(title: str, result: dict) -> None:
    print("=" * 72)
    print(title)
    print("-" * 72)
    print("MINTED:", result["minted"])
    if result["minted"]:
        print("sheet_hash :", result["sheet_hash"])
        print("merkle_root:", result["merkle_root"])
    for name, c in result["poi"]["closures"].items():
        mark = "PASS" if c["pass"] else "FAIL"
        extra = {k: v for k, v in c.items() if k != "pass"}
        print(f"  [{mark}] {name}  {canonical(extra)}")
    print()

def main() -> None:
    g = build_corpus()
    print(f"ProofGraph v0  | kernels={len(g.kernels)}  edges={len(g.edges)}  seed={SEED}\n")

    # Attempt A — naive bundle: two ortho facts + the flagged claim. Should REFUSE.
    a = g.mint_sheet(
        "SS-000-naive",
        "Lewinnek is a good rule because AUC looks fine.",
        bundle=["k03", "k04", "k12"],
        load_bearing={"k03", "k04", "k12"},
        executable_path=[],  # no action
    )
    show("ATTEMPT A  (naive single-domain bundle — the gate should bite)", a)

    # Attempt B — the real intersection: MDL structural axis  x  MDC input axis.
    thesis = (
        "Pre-outcome trustworthiness of a clinical decision rule requires BOTH "
        "structural compressibility (MDL: dL>0 vs null) AND input resolvability "
        "(decision-boundary spacing >= MDC95 of its measured inputs). These are two "
        "independent, pre-data audit axes; a rule can fail either, and both are "
        "detectable WITHOUT any new outcome study."
    )
    path = [
        "1. Extract rule structure; compute dL = L(null) - L(rule) on the outcome proxy. dL<=0 -> structural fragility (RuleAudit).",
        "2. List every decision boundary/threshold and the input landmark(s) it depends on.",
        "3. Estimate MDC95 for each input landmark via test-retest.",
        "4. Flag any boundary spaced < MDC95 of its input -> input non-resolvable.",
        "5. Rule is INDIVIDUALLY applicable only if it passes BOTH axes; else label population-only or revise.",
    ]
    b = g.mint_sheet(
        "SS-001-rule-trustworthiness",
        thesis,
        bundle=["k01", "k02", "k04", "k06", "k03", "k05", "k07", "k08", "k09", "k10", "k12"],
        load_bearing={"k01", "k02", "k04", "k06", "k03", "k05", "k07", "k10"},
        executable_path=path,
    )
    show("ATTEMPT B  (RuleAudit/MDL  x  pelvic-R reliability/MDC — a real bridge)", b)

    if b["minted"]:
        print("MINTED SHEET SS-001")
        print("thesis:", b["body"]["thesis"])
        print("\nexecutable path (the 'snake'):")
        for s in b["body"]["executable_path"]:
            print("  ", s)
        print("\nflagged in-bundle (carried as context, non-load-bearing):",
              b["poi"]["closures"]["3_evidence_closure"]["flagged_kernels"])

if __name__ == "__main__":
    main()
