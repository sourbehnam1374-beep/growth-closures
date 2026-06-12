#!/usr/bin/env python3
"""
test_anomaly_characterization.py — properties P13–P14 + corpus identity.

Randomized adversarial verification (Hypothesis, with shrinking) of the
anomaly-characterization theorem for the deletion paper:

  Ser(K(S\\D)) \\ Ser(K(S)) = disjoint union over cohorts c with
  1 <= |D∩C_c| and |C_c| - |D∩C_c| >= tau of cone(B_{C_c\\D}),
  tau = max(3, m0);  single-atom case: insertion <=> |cohort(a)| >= tau+1.

Corpus identity (optional, networked): anomaly frequency on Moby-Dick
= atom mass of cohorts of size >= 4 = 5014/8631 = 58.1%.

Pure stdlib + hypothesis. Run:  python3 test_anomaly_characterization.py
"""

import random
import re
import urllib.request
import collections

from hypothesis import given, settings, strategies as st, HealthCheck

import growth_check as gc

EX = 120
CFG = settings(max_examples=EX, deadline=None,
               suppress_health_check=[HealthCheck.too_slow])

DESCRIPTORS = ["D1", "D2", "D3", "D4"]
TAU = 3  # max(3, m0) at the paper's default code parameters b=2,o=2,r=0


# ----------------------------------------------------------------------
# Strategies
# ----------------------------------------------------------------------
@st.composite
def seed_and_deletion(draw, max_per_cohort=8, max_delete=4):
    """Multi-cohort seed + nonempty deletion set drawn from it."""
    seed = []
    for d in DESCRIPTORS:
        for i in range(draw(st.integers(0, max_per_cohort))):
            seed.append(gc.atom("a-%s-%d-%d" % (d, i, draw(st.integers(0, 9))), d))
    if not seed:
        seed.append(gc.atom("a-D1-0-0", "D1"))
    k = draw(st.integers(1, min(max_delete, len(seed))))
    idx = draw(st.permutations(range(len(seed))))[:k]
    D = [seed[i] for i in idx]
    return seed, D


def view_parts(parts):
    v, _ = gc.quotient_view(parts)
    return v


def predicted_insertions(seed, D):
    """The theorem's right-hand side: one 3-part cone per touched,
    still-bindable cohort."""
    daddr = {a["addr"] for a in D}
    pred = set()
    for d in DESCRIPTORS:
        C = [a for a in seed if a["descriptor"] == d]
        k = sum(1 for a in D if a["descriptor"] == d)
        if k >= 1 and len(C) - k >= TAU:
            rest = sorted(a["addr"] for a in C if a["addr"] not in daddr)
            B = gc.composite("Block", "bind", d, rest)
            S = gc.composite("Section", "lift", d, [B["addr"]])
            R = gc.composite("Root", "frame", d, [S["addr"]])
            pred |= {B["addr"], S["addr"], R["addr"]}
    return pred


# ======================================================================
# P13  Single-atom iff law:  insertion <=> |cohort(a)| >= tau+1
# ======================================================================
@CFG
@given(seed_and_deletion(max_delete=1))
def p13_single_atom_iff(sd):
    seed, D = sd
    a = D[0]
    n = sum(1 for x in seed if x["descriptor"] == a["descriptor"])
    pS, _ = gc.close_field(seed)
    pSD, _ = gc.close_field([x for x in seed if x["addr"] != a["addr"]])
    inserted = bool(set(view_parts(pSD)) - set(view_parts(pS)))
    assert inserted == (n >= TAU + 1), \
        "iff law failed: cohort n=%d inserted=%s" % (n, inserted)


# ======================================================================
# P14  General law: inserted set == disjoint union of predicted cones
# ======================================================================
@CFG
@given(seed_and_deletion())
def p14_exact_cone_law(sd):
    seed, D = sd
    daddr = {a["addr"] for a in D}
    pS, _ = gc.close_field(seed)
    pSD, _ = gc.close_field([x for x in seed if x["addr"] not in daddr])
    inserted = set(view_parts(pSD)) - set(view_parts(pS))
    assert inserted == predicted_insertions(seed, D), \
        "inserted set != predicted cones"


# ======================================================================
# Corpus identity (networked; skipped gracefully offline)
# ======================================================================
STOP = set("""the a an and or but of to in on at by for with from as is are was were be been
being it its this that these those he she they we you i his her their our your my me him them
us not no nor so if then than there here when where which who whom what all any some such own
same very can will just do does did done have has had may might must shall should would could
about into over under again further once more most other only out up down off above below""".split())


def corpus_identity():
    url = "https://www.gutenberg.org/files/2701/2701-0.txt"
    raw = urllib.request.urlopen(url, timeout=60).read().decode("utf-8", "replace")
    s, e = raw.find("*** START"), raw.find("*** END")
    body = raw[raw.find("\n", s):e] if s != -1 and e != -1 else raw
    sentences = [t.strip() for t in re.split(r"[.!?]+", body) if len(t.strip()) >= 20]
    coh = collections.Counter()
    for sent in sentences:
        words = [w for w in re.findall(r"[a-z]+", sent.lower())
                 if len(w) >= 3 and w not in STOP]
        if not words:
            continue
        coh[sorted(collections.Counter(words).items(),
                   key=lambda kv: (-kv[1], kv[0]))[0][0]] += 1
    n_atoms = sum(coh.values())
    mass4 = sum(n for n in coh.values() if n >= TAU + 1)
    pct = 100.0 * mass4 / n_atoms
    print("  corpus: atoms=%d  mass(n>=%d)=%d  -> %.1f%%  (paper: 58.1%%)"
          % (n_atoms, TAU + 1, mass4, pct))
    return abs(pct - 58.1) < 0.05 and mass4 == 5014 and n_atoms == 8631


# ======================================================================
# Runner
# ======================================================================
PROPS = [
    ("P13 single-atom iff (n >= tau+1)", p13_single_atom_iff),
    ("P14 exact per-cohort cone law", p14_exact_cone_law),
]

if __name__ == "__main__":
    failures = 0
    for name, fn in PROPS:
        try:
            fn()
            print("[PASS] %-38s (%d randomized examples)" % (name, EX))
        except Exception as exc:
            failures += 1
            print("[FAIL] %s\n%s" % (name, exc))
    try:
        ok = corpus_identity()
        print("[%s] corpus identity 58.1%% == mass(n>=4)" % ("PASS" if ok else "FAIL"))
        failures += 0 if ok else 1
    except Exception as exc:
        print("[SKIP] corpus identity (offline?): %s" % exc)
    print("-" * 70)
    print("ANOMALY CHARACTERIZATION: %s"
          % ("ALL PASS" if failures == 0 else "%d FAILURE(S)" % failures))
    raise SystemExit(1 if failures else 0)
