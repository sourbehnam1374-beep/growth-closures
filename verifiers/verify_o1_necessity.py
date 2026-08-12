#!/usr/bin/env python3
"""
verify_o1_necessity.py — O1: premise inscription is NECESSARY for exact
record-local deletion.

Model the kappa'-store (premises NOT committed: block address = H(kind,rule,
descr) only -> one block identity per descriptor). Facts checked:

  O1-a  multiplicity: on a 4-atom cohort the single block part has 5 distinct
        derivations (all admissible subsets), so 'single derivation' fails.
  O1-b  EXHAUSTIVE: for EVERY representative premise record r (any admissible
        subset stored as 'the' children), there EXISTS a single-atom deletion
        d where record-local cone excision diverges from ground-truth
        re-closure. (forall r, exists d.)
  O1-c  repair = counting/DRed: storing ALL derivations and keeping the part
        iff one derivation survives reproduces re-closure exactly, for every
        deletion subset (exhaustive over all 2^4 deletions).
  O1-d  conservation of the blow-up: #derivation records under kappa' equals
        #parts (blocks) under kappa0 = sum_{m>=3} C(n,m); checked n=3..8.
"""
import itertools
from math import comb
import growth_check as gc

def adm_subsets(cohort):
    n = len(cohort)
    for m in range(3, n + 1):
        for c in itertools.combinations(sorted(cohort), m):
            yield frozenset(c)

def kprime_block_exists(cohort_alive):
    """Ground truth under kappa': the (single) block is in K(S) iff some
    admissible subset survives."""
    return len(cohort_alive) >= 3

# ---- O1-a: multiplicity on n=4 ----
A = ["a1", "a2", "a3", "a4"]
derivs = list(adm_subsets(A))
print("O1-a  derivations of the one kappa'-block (n=4): %d  (expect 5: C43+C44)"
      % len(derivs), "->", "PASS" if len(derivs) == 5 else "FAIL")

# ---- O1-b: forall record r, exists single-atom deletion d that breaks excision ----
all_break = True
witness_rows = []
for r in derivs:                       # every possible representative record
    found = None
    for d in A:                        # single-atom deletions
        alive = [x for x in A if x != d]
        truth = kprime_block_exists(alive)        # re-closure keeps block?
        excis = (d not in r)                      # record-local excision keeps?
        if truth != excis:
            found = (d, truth, excis); break
    witness_rows.append((sorted(r), found))
    if found is None:
        all_break = False
for r, w in witness_rows:
    print("      record r=%-22s  breaking d=%s  (truth keep=%s, excision keep=%s)"
          % (r, w[0], w[1], w[2]))
print("O1-b  every record has a breaking single-atom deletion:",
      "PASS" if all_break else "FAIL")

# ---- O1-c: counting repair, exhaustive over all 16 deletion subsets ----
ok = True
for k in range(0, 5):
    for D in itertools.combinations(A, k):
        alive = [x for x in A if x not in D]
        truth = kprime_block_exists(alive)
        counting = any(dr.isdisjoint(D) for dr in derivs)   # any derivation survives
        if truth != counting:
            ok = False
print("O1-c  counting/DRed regime == re-closure on all 2^4 deletions:",
      "PASS" if ok else "FAIL")

# ---- O1-d: conservation of the blow-up ----
cons_ok = True
for n in range(3, 9):
    cohort = ["x%d" % i for i in range(n)]
    n_derivs_kprime = sum(1 for _ in adm_subsets(cohort))
    # kappa0 parts: actual block count from the reference implementation
    atoms = [gc.atom("x%d" % i, "D1") for i in range(n)]
    parts, _ = gc.close_field(atoms)
    n_blocks_k0 = sum(1 for p in parts.values() if p["kind"] == "Block")
    pred = sum(comb(n, m) for m in range(3, n + 1))
    row_ok = n_derivs_kprime == n_blocks_k0 == pred
    cons_ok &= row_ok
    print("      n=%d : kappa' derivation-records=%3d  kappa0 parts=%3d  closed form=%3d  %s"
          % (n, n_derivs_kprime, n_blocks_k0, pred, "OK" if row_ok else "MISMATCH"))
print("O1-d  blow-up conserved (records <-> parts):", "PASS" if cons_ok else "FAIL")

print("-" * 70)
print("O1 VERIFICATION:", "ALL PASS" if (len(derivs) == 5 and all_break and ok and cons_ok) else "FAILURE")
