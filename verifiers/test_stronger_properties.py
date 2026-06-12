#!/usr/bin/env python3
"""
test_stronger_properties.py  —  Rung 1 for the STRENGTHENED variants.

Randomized adversarial verification (Hypothesis) of the reference
implementation against the strengthened theorem variants added in
lean/GrowthClosure.lean (section "STRENGTHENED VARIANTS"):

    V1  K_fixpoint               K(S) = S ⊔ Φ(K(S))  — the field is exactly
                                 the seed plus the ONE-step image of the field
    V2  K_least_fixpoint         K(S) ⊆ every closed fixed point containing S
    V3  K_merge                  K(K(S) ⊔ K(T)) = K(S ⊔ T)  — replica merge
    V4  ingest_extends           prolonging a history only grows the field,
                                 address-stably
    V5  tombstone_permanence_set re-adding ANY subset of removed content
                                 is a no-op under 2P
    V6  live_extend_adds         add-only log suffix grows the live store
                                 (even when it re-adds removed content)
    V7  live_extend_removes      remove-only log suffix shrinks the live store
    V8  live_replay              replaying a whole log (here: a SHUFFLED full
                                 replay, via live_replay + live_swap) is a no-op

Falsification pressure, not deductive proof (that is Rung 2, the Lean file).
Pure stdlib + hypothesis. Run:  python3 test_stronger_properties.py
"""

import random

from hypothesis import given, settings, strategies as st, HealthCheck

import growth_check as gc
from delete_growth import two_phase

EX = 60  # examples per property
CFG = settings(max_examples=EX, deadline=None,
               suppress_health_check=[HealthCheck.too_slow])

DESCRIPTORS = ["D1", "D2", "D3"]


@st.composite
def atoms_strategy(draw, min_size=0, max_size=6, prefix="s"):
    """Distinct-address atoms: payload indexed within the example."""
    n = draw(st.integers(min_size, max_size))
    return [gc.atom("%s-%d" % (prefix, i), draw(st.sampled_from(DESCRIPTORS)))
            for i in range(n)]


@st.composite
def batches_strategy(draw, prefix="b", max_batches=3, max_per=2):
    """A short ingestion history: a list of small atom batches."""
    out, k = [], 0
    for _ in range(draw(st.integers(0, max_batches))):
        m = draw(st.integers(1, max_per))
        out.append([gc.atom("%s-%d" % (prefix, k + i),
                            draw(st.sampled_from(DESCRIPTORS)))
                    for i in range(m)])
        k += m
    return out


def addrset(parts):
    return set(parts.keys())


def fp(parts, gov):
    return gc.canonical(parts, gov)[0]


def one_step_image(parts, b=2.0, o=2.0, r=0.0):
    """Φ(X): everything some rule instance derives in ONE step from X."""
    img = {}
    img.update(gc._bind_blocks(parts, b, o, r))
    for p in parts.values():
        if p["kind"] == "Block":
            s = gc.composite("Section", "lift", p["sign"], [p["addr"]])
            img[s["addr"]] = s
        elif p["kind"] == "Section":
            rt = gc.composite("Root", "frame", p["sign"], [p["addr"]])
            img[rt["addr"]] = rt
    return img


def close_parts(parts, b=2.0, o=2.0, r=0.0):
    """K over an arbitrary part dict (not only atom seeds): expand to
    fixpoint, exactly as close_field does after seeding."""
    cur = {a: dict(p) for a, p in parts.items()}
    while True:
        cur, changed = gc.expand(cur, b, o, r)
        if not changed:
            break
    roots = [p for p in cur.values() if p["kind"] == "Root"]
    gov = sorted((rt["addr"], gc.TOP_ADDR) for rt in roots)
    return cur, gov


# ======================================================================
# V1  K_fixpoint — K(S) = S ⊔ Φ(K(S)), both inclusions exactly
# ======================================================================
@CFG
@given(atoms_strategy(0, 7))
def test_v1_fixpoint(seed):
    parts, _ = gc.close_field(seed)
    img = one_step_image(parts)
    # the atom layer of K(S) is exactly S ...
    assert {a for a, p in parts.items() if p["kind"] == "Atom"} == \
           {a["addr"] for a in seed}
    # ... and the composite layer is exactly the one-step image of K(S):
    # ⊆ is closedness, ⊇ says nothing in the field is more than one
    # rule application away from the field — the fixed-point identity.
    assert set(img) == {a for a, p in parts.items() if p["kind"] != "Atom"}


# ======================================================================
# V2  K_least_fixpoint — K(S) sits inside every closed fixed point ⊇ S
# ======================================================================
@CFG
@given(atoms_strategy(0, 6, "s"), atoms_strategy(0, 4, "e"))
def test_v2_least_fixpoint(seed, extra):
    pS, _ = gc.close_field(seed)
    X, _ = gc.close_field(seed + extra)  # a closed fixed point containing S
    assert set(one_step_image(X)) <= addrset(X)  # X is closed
    assert addrset(pS) <= addrset(X)             # K(S) ⊆ X: minimality


# ======================================================================
# V3  K_merge — closing the join of two closed replicas == closing the
#               joined seeds, bit-identical fingerprints
# ======================================================================
@CFG
@given(atoms_strategy(0, 5, "s"), atoms_strategy(0, 5, "t"))
def test_v3_replica_merge(sa, ta):
    pS, _ = gc.close_field(sa)
    pT, _ = gc.close_field(ta)
    merged = {**pS, **pT}                 # K(S) ⊔ K(T)
    pM, gM = close_parts(merged)          # K(K(S) ⊔ K(T))
    pU, gU = gc.close_field(sa + ta)      # K(S ⊔ T)
    assert fp(pM, gM) == fp(pU, gU)


# ======================================================================
# V4  ingest_extends — prolonging a history only grows the field,
#                      and shared addresses keep identical records
# ======================================================================
@CFG
@given(atoms_strategy(0, 4, "s"), batches_strategy("b"), batches_strategy("c"))
def test_v4_ingest_extends(seed, Bs, Cs):
    cur, gov = gc.close_field(seed)
    for b in Bs:
        cur, gov = gc.close_incremental(cur, b)
    ext = {a: dict(p) for a, p in cur.items()}
    egov = gov
    for c in Cs:
        ext, egov = gc.close_incremental(ext, c)
    assert addrset(cur) <= addrset(ext), "history extension retracted a part"
    for a in cur:  # address-stable persistence
        assert cur[a]["children"] == ext[a]["children"]
        assert cur[a].get("payload") == ext[a].get("payload")


# ======================================================================
# V5  tombstone_permanence_set — re-adding ANY subset of removed content
# ======================================================================
@CFG
@given(atoms_strategy(1, 8, "x"),
       st.lists(st.booleans(), min_size=8, max_size=8),
       st.lists(st.booleans(), min_size=8, max_size=8))
def test_v5_tombstone_set(seed, mask_remove, mask_readd):
    D = [a for a, m in zip(seed, mask_remove) if m]
    readd = [a for a, m in zip(D, mask_readd) if m]  # arbitrary subset of D
    ops = [("add", a) for a in seed] + [("remove", a["addr"]) for a in D]
    p1, g1, _, _ = two_phase(ops)
    p2, g2, _, _ = two_phase(ops + [("add", a) for a in readd])
    assert fp(p1, g1) == fp(p2, g2)


# ======================================================================
# V6  live_extend_adds — add-only suffix grows the live store, even when
#     it re-adds removed content (remove-wins absorbs those silently)
# ======================================================================
@CFG
@given(atoms_strategy(0, 6, "x"),
       st.lists(st.booleans(), min_size=6, max_size=6),
       atoms_strategy(0, 4, "n"))
def test_v6_live_extend_adds(seed, mask, fresh):
    D = [a["addr"] for a, m in zip(seed, mask) if m]
    ops = [("add", a) for a in seed] + [("remove", d) for d in D]
    ext = [("add", a) for a in fresh] + \
          [("add", a) for a, m in zip(seed, mask) if m]  # adversarial re-adds
    p1, _, _, _ = two_phase(ops)
    p2, _, _, _ = two_phase(ops + ext)
    assert addrset(p1) <= addrset(p2), "add-only suffix removed a part"


# ======================================================================
# V7  live_extend_removes — remove-only suffix shrinks the live store
# ======================================================================
@CFG
@given(atoms_strategy(0, 6, "x"),
       st.lists(st.booleans(), min_size=6, max_size=6),
       st.lists(st.booleans(), min_size=6, max_size=6))
def test_v7_live_extend_removes(seed, m1, m2):
    D1 = [a["addr"] for a, m in zip(seed, m1) if m]
    D2 = [a["addr"] for a, m in zip(seed, m2) if m]
    ops = [("add", a) for a in seed] + [("remove", d) for d in D1]
    ext = [("remove", d) for d in D2]
    p1, _, _, _ = two_phase(ops)
    p2, _, _, _ = two_phase(ops + ext)
    assert addrset(p2) <= addrset(p1), "remove-only suffix created a part"


# ======================================================================
# V8  live_replay (+ live_swap) — a shuffled full replay of the log is
#     a no-op: at-least-once delivery is free under 2P
# ======================================================================
@CFG
@given(atoms_strategy(0, 6, "x"),
       st.lists(st.booleans(), min_size=6, max_size=6),
       st.integers(0, 2**31 - 1))
def test_v8_live_replay(seed, mask, rs):
    D = [a["addr"] for a, m in zip(seed, mask) if m]
    ops = [("add", a) for a in seed] + [("remove", d) for d in D]
    dup = ops + ops
    random.Random(rs).shuffle(dup)
    p1, g1, _, _ = two_phase(ops)
    p2, g2, _, _ = two_phase(dup)
    assert fp(p1, g1) == fp(p2, g2)


# ======================================================================
# Runner
# ======================================================================
PROPS = [
    ("V1 K_fixpoint: K(S) = S ⊔ Φ(K(S))", test_v1_fixpoint),
    ("V2 K_least_fixpoint: minimality", test_v2_least_fixpoint),
    ("V3 K_merge: replica merge", test_v3_replica_merge),
    ("V4 ingest_extends: histories only grow", test_v4_ingest_extends),
    ("V5 tombstone set: re-add subset no-op", test_v5_tombstone_set),
    ("V6 live_extend_adds: CALM growth half", test_v6_live_extend_adds),
    ("V7 live_extend_removes: deletion half", test_v7_live_extend_removes),
    ("V8 live_replay: shuffled replay no-op", test_v8_live_replay),
]

if __name__ == "__main__":
    failures = 0
    for name, fn in PROPS:
        try:
            fn()
            print("[PASS] %-42s (%d randomized examples)" % (name, EX))
        except Exception as e:  # hypothesis raises with shrunk counterexample
            failures += 1
            print("[FAIL] %s\n%s" % (name, e))
    total = len(PROPS)
    print("-" * 70)
    print("PROPERTIES: %d/%d PASS  (~%d randomized instances)"
          % (total - failures, total, total * EX))
    raise SystemExit(1 if failures else 0)
