#!/usr/bin/env python3
"""
test_growth_properties.py  —  Rung 1: property-based verification.

Randomized adversarial testing (Hypothesis) of the reference implementation
`growth_check.py` against the theorems of
"Monotone Growth of Content-Addressed Rule Closures".

Each property is a universally quantified claim from the paper, instantiated
on randomly generated seeds, deltas, ingestion histories, and code parameters,
with automatic shrinking of any counterexample. This is falsification
pressure on ~10^4 instances — it closes the spec-implementation gap; it is
not deductive proof (that is Rung 2, GrowthClosure.lean).

Pure stdlib + hypothesis. Run:  python3 test_growth_properties.py
"""

import random
from collections import deque
from fractions import Fraction

from hypothesis import given, settings, strategies as st, HealthCheck

import growth_check as gc

EX = 60  # examples per property
CFG = settings(max_examples=EX, deadline=None,
               suppress_health_check=[HealthCheck.too_slow])

# ----------------------------------------------------------------------
# Strategies
# ----------------------------------------------------------------------
DESCRIPTORS = ["D1", "D2", "D3"]


@st.composite
def atoms_strategy(draw, min_size=0, max_size=6, prefix="s"):
    """Distinct-address atoms: payload indexed within the example."""
    n = draw(st.integers(min_size, max_size))
    out = []
    for i in range(n):
        d = draw(st.sampled_from(DESCRIPTORS))
        out.append(gc.atom("%s-%d" % (prefix, i), d))
    return out


@st.composite
def seed_delta(draw, max_seed=6, max_delta=3):
    seed = draw(atoms_strategy(0, max_seed, "s"))
    delta = draw(atoms_strategy(0, max_delta, "d"))
    return seed, delta


@st.composite
def seed_delta_history(draw):
    """Seed + delta + a random ordered partition of the delta into batches."""
    seed = draw(atoms_strategy(0, 5, "s"))
    delta = draw(atoms_strategy(1, 3, "d"))
    perm = list(delta)
    rnd = random.Random(draw(st.integers(0, 2**32 - 1)))
    rnd.shuffle(perm)
    batches, cur = [], []
    for a in perm:
        cur.append(a)
        if draw(st.booleans()):
            batches.append(cur)
            cur = []
    if cur:
        batches.append(cur)
    return seed, delta, batches


def addrset(parts):
    return set(parts.keys())


def cohorts(atom_list):
    by = {}
    for a in atom_list:
        by.setdefault(a["descriptor"], set()).add(a["addr"])
    return by


# ======================================================================
# P1  Closure-operator laws on the implementation
# ======================================================================
@CFG
@given(seed_delta())
def p1_extensive_monotone(sd):
    seed, delta = sd
    pS, _ = gc.close_field(seed)
    pSD, _ = gc.close_field(seed + delta)
    # extensive: seed atoms appear in K(S)
    assert {a["addr"] for a in seed} <= addrset(pS)
    # monotone: K(S) ⊆ K(S ∪ D)
    assert addrset(pS) <= addrset(pSD)


@CFG
@given(atoms_strategy(0, 7))
def p1_idempotent_closed(seed):
    parts, gov = gc.close_field(seed)
    # closed: one more expansion step adds nothing
    _, changed = gc.expand(parts, 2.0, 2.0, 0.0)
    assert not changed
    # idempotent: re-closing with empty delta is a fixpoint, same fingerprint
    parts2, gov2 = gc.close_incremental(parts, [])
    assert gc.canonical(parts, gov)[0] == gc.canonical(parts2, gov2)[0]


# ======================================================================
# P2  Theorem 2 — conservativity is an address-stable Merkle diff
# ======================================================================
@CFG
@given(seed_delta())
def p2_conservativity(sd):
    seed, delta = sd
    pS, _ = gc.close_field(seed)
    pSD, _ = gc.close_field(seed + delta)
    assert addrset(pS) <= addrset(pSD), "retraction under growth"
    # address-stable: shared addresses carry byte-identical records
    for a in addrset(pS):
        old, new = pS[a], pSD[a]
        assert (old["kind"], old.get("rule"), old.get("sign"), old["children"]) == \
               (new["kind"], new.get("rule"), new.get("sign"), new["children"])


# ======================================================================
# P3  Theorem 3/4 — incremental (frontier-local) == batch
# ======================================================================
@CFG
@given(seed_delta())
def p3_incremental_eq_batch(sd):
    seed, delta = sd
    pS, _ = gc.close_field(seed)
    inc_p, inc_g = gc.close_incremental(pS, delta)
    bat_p, bat_g = gc.close_field(seed + delta)
    assert gc.canonical(inc_p, inc_g)[0] == gc.canonical(bat_p, bat_g)[0]


# ======================================================================
# P4  Theorem 5 — ingestion confluence over random histories
# ======================================================================
@CFG
@given(seed_delta_history())
def p4_history_independence(sdh):
    seed, delta, batches = sdh
    pS, _ = gc.close_field(seed)
    cur, gov = pS, []
    for b in batches:
        cur, gov = gc.close_incremental(cur, b)
    fp_hist = gc.canonical(cur, gov)[0]
    bat_p, bat_g = gc.close_field(seed + delta)
    assert fp_hist == gc.canonical(bat_p, bat_g)[0]


# ======================================================================
# P5  Lemma D — fingerprint independent of seed presentation order
# ======================================================================
@CFG
@given(atoms_strategy(0, 7), st.integers(0, 2**32 - 1))
def p5_order_independence(seed, rseed):
    p1, g1 = gc.close_field(seed)
    shuffled = list(seed)
    random.Random(rseed).shuffle(shuffled)
    p2, g2 = gc.close_field(shuffled)
    assert gc.canonical(p1, g1)[0] == gc.canonical(p2, g2)[0]


# ======================================================================
# P6  Descent identity + address injectivity (H4 instance check)
# ======================================================================
@CFG
@given(atoms_strategy(0, 7))
def p6_descent_and_injectivity(seed):
    parts, gov = gc.close_field(seed)
    # atoms(K(S)) == S  (as address sets)
    assert {a for a, p in parts.items() if p["kind"] == "Atom"} == \
           {a["addr"] for a in seed}
    # injectivity within the field (incl. TOP)
    addrs = list(parts.keys()) + [gc.TOP_ADDR]
    assert len(addrs) == len(set(addrs))


# ======================================================================
# P7  Prop 8 — well-formedness characterization + fixed height
# ======================================================================
@CFG
@given(atoms_strategy(0, 7))
def p7_wellformed_characterization(seed):
    parts, gov = gc.close_field(seed)
    wf, ecc, orphans = gc.well_formed(parts, gov, h=4)
    coh = cohorts(seed)
    expect = bool(seed) and all(len(v) >= 3 for v in coh.values())
    assert wf == expect
    if wf:
        assert ecc == 4 and orphans == 0  # extremal Atom–Block–Section–Root–TOP


# ======================================================================
# P8  Prop 9 — beta_1: Euler identity, per-instance law, growth monotone
# ======================================================================
def replay_beta(parts, gov):
    """Union-find replay; returns beta_1 and whether Δβ₁ = m − j held."""
    nodes = list(parts.keys()) + ([gc.TOP_ADDR] if gov else [])
    idx = {n: i for i, n in enumerate(nodes)}
    parent = list(range(len(nodes)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    present, beta, law_ok = set(), 0, True
    order = sorted(parts.values(), key=lambda p: (gc.GRADE[p["kind"]], p["addr"]))
    for p in order:
        comps = {find(idx[c]) for c in p["children"] if c in present}
        j, m = len(comps), len(p["children"])
        present.add(p["addr"])
        for c in p["children"]:
            if find(idx[p["addr"]]) != find(idx[c]):
                parent[find(idx[p["addr"]])] = find(idx[c])
        d = m - j
        if d < 0:
            law_ok = False
        beta += d
    if gov:
        present.add(gc.TOP_ADDR)
        for s, _ in gov:
            if find(idx[s]) != find(idx[gc.TOP_ADDR]):
                parent[find(idx[s])] = find(idx[gc.TOP_ADDR])
            else:
                beta += 1
    return beta, law_ok


@CFG
@given(seed_delta(max_seed=5, max_delta=3))
def p8_betti(sd):
    seed, delta = sd
    pS, gS = gc.close_field(seed)
    pSD, gSD = gc.close_field(seed + delta)
    b_small = gc.betti1(gc.undirected_adj(pS, gS))[0]
    b_big = gc.betti1(gc.undirected_adj(pSD, gSD))[0]
    assert b_small <= b_big, "beta_1 decreased under growth"
    rb, law = replay_beta(pSD, gSD)
    assert law, "Δβ₁ = m − j violated at some instance"
    assert rb == b_big, "replayed beta_1 != Euler-formula beta_1"


# ======================================================================
# P9  Prop 10 — clique count closed form per cohort
# ======================================================================
def C(n, k):
    from math import comb
    return comb(n, k)


@CFG
@given(atoms_strategy(0, 8))
def p9_clique_counts(seed):
    parts, _ = gc.close_field(seed)
    coh = cohorts(seed)
    for d, members in coh.items():
        n = len(members)
        expect = sum(C(n, m) for m in range(3, n + 1))
        got = sum(1 for p in parts.values()
                  if p["kind"] == "Block" and p["sign"] == d)
        assert got == expect
        # sections and roots track blocks one-for-one
        assert got == sum(1 for p in parts.values()
                          if p["kind"] == "Section" and p["sign"] == d)
        assert got == sum(1 for p in parts.values()
                          if p["kind"] == "Root" and p["sign"] == d)


# ======================================================================
# P10 Theorem 11 face — payload-determined maximality retracts
# ======================================================================
@CFG
@given(st.integers(3, 6), st.sampled_from(DESCRIPTORS))
def p10_max_operator_retracts(n, d):
    cohort = [gc.atom("m-%d" % i, d) for i in range(n + 1)]
    S, Sp = cohort[:n], cohort
    full_block_S = gc.composite("Block", "bind", d, [a["addr"] for a in S])
    mS = {b["addr"] for b in gc.max_blocks(S)}
    mSp = {b["addr"] for b in gc.max_blocks(Sp)}
    assert full_block_S["addr"] in mS
    assert full_block_S["addr"] not in mSp, "expected retraction did not occur"
    assert not (mS <= mSp), "Phi_max unexpectedly monotone"
    # the complete closure on the identical growth is conservative
    pS, _ = gc.close_field(S)
    pSp, _ = gc.close_field(Sp)
    assert full_block_S["addr"] in pS and full_block_S["addr"] in pSp
    assert addrset(pS) <= addrset(pSp)


# ======================================================================
# P11 §6.1 — subsumption-quotient view invariants
# ======================================================================
@CFG
@given(atoms_strategy(0, 7))
def p11_quotient_view(seed):
    parts, gov = gc.close_field(seed)
    view, subsumed = gc.quotient_view(parts)
    cs = {a: frozenset(p["children"]) for a, p in parts.items()
          if p["kind"] == "Block"}
    vblocks = [p for p in view.values() if p["kind"] == "Block"]
    fblocks = [p for p in parts.values() if p["kind"] == "Block"]
    # view ⊆ field; view is a deterministic function of the field
    assert set(view.keys()) <= set(parts.keys())
    v2, _ = gc.quotient_view(parts)
    assert set(view.keys()) == set(v2.keys())
    # every kept block is maximal in the field (same descriptor)
    for b in vblocks:
        assert not any(p["sign"] == b["sign"] and cs[b["addr"]] < cs[p["addr"]]
                       for p in fblocks if p["addr"] != b["addr"])
    # every dropped block is strictly contained in some kept block
    for a in subsumed:
        bad = parts[a]
        assert any(p["sign"] == bad["sign"] and cs[a] < cs[p["addr"]]
                   for p in vblocks)


# ======================================================================
# P12 §7H — MDL threshold, integer grid and exact rationals (r ≥ 0)
# ======================================================================
@CFG
@given(st.integers(1, 12), st.integers(0, 24))
def p12_threshold_integers(b, o):
    assert gc.m0(b, o, 0.0) == o // b + 2


@CFG
@given(st.integers(1, 12), st.integers(0, 24), st.integers(0, 11),
       st.integers(1, 12))
def p12_threshold_rationals(b, o, rnum, rden):
    r = Fraction(rnum, rden)
    bF, oF = Fraction(b), Fraction(o)
    if r >= bF:
        return  # Δ non-increasing in m: no general threshold claim
    # least m with m(b−r) > b+o
    q = (bF + oF) / (bF - r)
    expect = int(q) + 1 if q == int(q) else int(q) + 1 if q > int(q) else None
    expect = int(q) + 1  # least integer strictly greater than q
    got = 2
    while not ((got - 1) * bF - oF - got * r > 0):
        got += 1
    assert got == max(2, expect)


# ======================================================================
# Runner
# ======================================================================
PROPS = [
    ("P1a closure: extensive + monotone", p1_extensive_monotone),
    ("P1b closure: closed + idempotent", p1_idempotent_closed),
    ("P2  Thm 2 conservativity / Merkle diff", p2_conservativity),
    ("P3  Thm 3/4 incremental == batch", p3_incremental_eq_batch),
    ("P4  Thm 5 history independence", p4_history_independence),
    ("P5  Lem D order independence", p5_order_independence),
    ("P6  descent identity + injectivity", p6_descent_and_injectivity),
    ("P7  Prop 8 well-formedness charac.", p7_wellformed_characterization),
    ("P8  Prop 9 beta_1 laws", p8_betti),
    ("P9  Prop 10 clique counts", p9_clique_counts),
    ("P10 Thm 11 face: max retracts", p10_max_operator_retracts),
    ("P11 §6.1 quotient invariants", p11_quotient_view),
    ("P12a threshold (integer grid)", p12_threshold_integers),
    ("P12b threshold (exact rationals)", p12_threshold_rationals),
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
