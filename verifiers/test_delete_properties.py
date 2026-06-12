#!/usr/bin/env python3
# ----------------------------------------------------------------------
# test_delete_properties.py -- randomized adversarial properties for
# the deletion theory. Run: python3 -m pytest test_delete_properties.py -q
# ----------------------------------------------------------------------
import random

from hypothesis import given, settings, strategies as st

from growth_check import atom, close_field, canonical, quotient_view
from delete_growth import (
    support, up_cone, excise, epoch, two_phase, erasure_check,
)

MAXN = 60


def fp(parts, gov):
    return canonical(parts, gov)[0]


# strategy: a small universe of atoms over few descriptors, plus a
# deletion mask -- adversarial because cohorts collide constantly
atoms_strat = st.lists(
    st.tuples(st.integers(0, 30), st.integers(0, 3)),
    min_size=1, max_size=12, unique_by=lambda t: t[0],
).map(lambda ts: [atom("p-%d" % i, "d%d" % d) for i, d in ts])

mask_strat = st.lists(st.booleans(), min_size=12, max_size=12)


def pick(seed, mask):
    return {a["addr"] for a, m in zip(seed, mask) if m}


@settings(max_examples=MAXN, deadline=None)
@given(atoms_strat, mask_strat)
def test_cone_theorem(seed, mask):
    """K(S)\\Up(D) == K(S\\D), bit-identical fingerprints."""
    parts, gov = close_field(seed)
    D = pick(seed, mask)
    kept, gov_e, _ = excise(parts, D)
    re_p, re_g = epoch(parts, D)
    assert fp(kept, gov_e) == fp(re_p, re_g)


@settings(max_examples=MAXN, deadline=None)
@given(atoms_strat, mask_strat)
def test_survivor_stability(seed, mask):
    """Every surviving part keeps its exact record (address, children,
    payload) from the pre-deletion store."""
    parts, gov = close_field(seed)
    kept, _, _ = excise(parts, pick(seed, mask))
    for a, p in kept.items():
        q = parts[a]
        assert q["children"] == p["children"]
        assert q.get("payload") == p.get("payload")


@settings(max_examples=MAXN, deadline=None)
@given(atoms_strat, mask_strat)
def test_exactness(seed, mask):
    """Removed set is exactly Up(D)."""
    parts, gov = close_field(seed)
    D = pick(seed, mask)
    kept, _, cone = excise(parts, D)
    assert set(parts) - set(kept) == cone
    assert cone == up_cone(parts, D)


@settings(max_examples=MAXN, deadline=None)
@given(atoms_strat, mask_strat)
def test_idempotence(seed, mask):
    parts, gov = close_field(seed)
    D = pick(seed, mask)
    k1, g1, _ = excise(parts, D)
    k2, g2, _ = excise(k1, D)
    assert fp(k1, g1) == fp(k2, g2)


@settings(max_examples=MAXN, deadline=None)
@given(atoms_strat, mask_strat, mask_strat)
def test_commutation(seed, m1, m2):
    """Sequential excision commutes and equals union excision."""
    parts, gov = close_field(seed)
    D1, D2 = pick(seed, m1), pick(seed, m2)
    k1, g1, _ = excise(parts, D1)
    k12, g12, _ = excise(k1, D2)
    k2, g2, _ = excise(parts, D2)
    k21, g21, _ = excise(k2, D1)
    ku, gu, _ = excise(parts, D1 | D2)
    assert fp(k12, g12) == fp(k21, g21) == fp(ku, gu)


@settings(max_examples=MAXN, deadline=None)
@given(atoms_strat, mask_strat)
def test_erasure(seed, mask):
    """No removed payload string survives the physical store."""
    parts, gov = close_field(seed)
    D = pick(seed, mask)
    kept, gov_e, _ = excise(parts, D)
    removed = [p["payload"] for p in parts.values()
               if p["kind"] == "Atom" and p["addr"] in D]
    assert erasure_check(kept, gov_e, removed)


@settings(max_examples=MAXN, deadline=None)
@given(atoms_strat, mask_strat)
def test_anti_monotone(seed, mask):
    """The complete field only shrinks: K(S\\D) subset of K(S)."""
    parts, gov = close_field(seed)
    kept, _, _ = excise(parts, pick(seed, mask))
    assert set(kept) <= set(parts)


@settings(max_examples=MAXN, deadline=None)
@given(atoms_strat, mask_strat, st.integers(0, 2**31 - 1))
def test_2p_order_freedom(seed, mask, rs):
    """Any interleaving of the same add/remove multiset closes to the
    same fingerprint under remove-wins."""
    D = pick(seed, mask)
    ops = [("add", a) for a in seed] + [("remove", d) for d in D]
    rng = random.Random(rs)
    s1, s2 = ops[:], ops[:]
    rng.shuffle(s1)
    rng.shuffle(s2)
    p1, g1, _, _ = two_phase(s1)
    p2, g2, _, _ = two_phase(s2)
    assert fp(p1, g1) == fp(p2, g2)


@settings(max_examples=MAXN, deadline=None)
@given(atoms_strat, mask_strat)
def test_tombstone_permanence(seed, mask):
    """Re-adding removed atoms is a no-op under 2P."""
    D = pick(seed, mask)
    ops = [("add", a) for a in seed] + [("remove", d) for d in D]
    readds = [("add", a) for a in seed if a["addr"] in D]
    p1, g1, _, _ = two_phase(ops)
    p2, g2, _, _ = two_phase(ops + readds)
    assert fp(p1, g1) == fp(p2, g2)


@settings(max_examples=MAXN, deadline=None)
@given(atoms_strat, mask_strat, mask_strat)
def test_product_monotonicity(seed, mA, mR):
    """(A ordered by subset) x (R ordered by SUPERSET) -> live store
    monotone: A subset A', R' subset R  =>  live(A,R) subset live(A',R')."""
    A_small = [a for a, m in zip(seed, mA) if m]
    A_big = seed                                  # A_small subset A_big
    R_big = pick(seed, mR)
    R_small = {d for d, m in zip(sorted(R_big), mA) if m}  # R_small subset R_big
    ops_s = [("add", a) for a in A_small] + [("remove", d) for d in R_big]
    ops_b = [("add", a) for a in A_big] + [("remove", d) for d in R_small]
    ps, gs, _, _ = two_phase(ops_s)
    pb, gb, _, _ = two_phase(ops_b)
    assert set(ps) <= set(pb)
