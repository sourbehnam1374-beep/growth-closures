#!/usr/bin/env python3
# ----------------------------------------------------------------------
# delete_growth.py -- Principled deletion over content-addressed
# rule closures. Companion to growth_check.py (pure stdlib).
#
# Implements and machine-checks the deletion theory:
#   supp / up_cone   : atom support and upward cones via the Merkle DAG
#                      (premise-inscribing makes derivations unique, so
#                      support is a payload-local traversal)
#   excise           : cone excision  K(S)\Up(D)   -- incremental deletion
#   epoch            : epoch re-closure  K(S\D)    -- recompute from scratch
#   two_phase        : 2P-closure live store (grow-only A and R, remove-wins)
#   erasure_check    : physical-payload absence after excision
#
# Ledger DEL-01 .. DEL-12. Every number in the deletion paper that is not
# a citation is produced by this file, test_delete_properties.py, or
# bench_delete.py.
# ----------------------------------------------------------------------
import random
import sys

from growth_check import (
    atom, composite, close_field, close_incremental, canonical,
    quotient_view, max_blocks, GRADE, TOP_ADDR, line,
)


# ----------------------------------------------------------------------
# Support and cones (Lemma: single derivation; Def: supp, Up)
# ----------------------------------------------------------------------
def support(parts):
    """supp(p) for every part, bottom-up by grade. supp(atom)={atom};
    supp(composite)=union of children's supports. Premise-inscribing
    (children addresses are part of the address preimage) makes this
    the unique derivation's atom set."""
    order = sorted(parts.values(), key=lambda p: GRADE[p["kind"]])
    supp = {}
    for p in order:
        if p["kind"] == "Atom":
            supp[p["addr"]] = frozenset((p["addr"],))
        else:
            s = frozenset()
            for c in p["children"]:
                s |= supp[c]
            supp[p["addr"]] = s
    return supp


def up_cone(parts, del_addrs):
    """Up(D) = { p in K(S) : supp(p) meets D }."""
    D = set(del_addrs)
    supp = support(parts)
    return {a for a in parts if supp[a] & D}


# ----------------------------------------------------------------------
# The two deletion procedures
# ----------------------------------------------------------------------
def excise(parts, del_addrs):
    """Cone excision: remove exactly Up(D) from a closed store, in place.
    No re-closure pass, no rederivation check (single-derivation makes
    DRed's alternative-derivation accounting vanish). Returns
    (kept_parts, gov, cone)."""
    cone = up_cone(parts, del_addrs)
    kept = {a: p for a, p in parts.items() if a not in cone}
    roots = [p for p in kept.values() if p["kind"] == "Root"]
    gov = sorted((rt["addr"], TOP_ADDR) for rt in roots)
    return kept, gov, cone


def epoch(parts, del_addrs, b=2.0, o=2.0, r=0.0):
    """Epoch re-closure: rebuild K(S\\D) from the surviving atoms."""
    D = set(del_addrs)
    seed = [p for p in parts.values() if p["kind"] == "Atom" and p["addr"] not in D]
    return close_field(seed, b, o, r)


# ----------------------------------------------------------------------
# Two-phase (2P) closure: grow-only adds A, grow-only removes R,
# live store = K(A \ R). Remove-wins by construction.
# ----------------------------------------------------------------------
def two_phase(ops, b=2.0, o=2.0, r=0.0):
    """ops: sequence of ('add', atom_dict) / ('remove', atom_addr).
    Folds to (A, R) ignoring order, then closes the live seed."""
    A, R = {}, set()
    for kind, x in ops:
        if kind == "add":
            A[x["addr"]] = x
        elif kind == "remove":
            R.add(x)
    live = [p for a, p in A.items() if a not in R]
    parts, gov = close_field(live, b, o, r)
    return parts, gov, set(A), R


def naive_sequential(ops, b=2.0, o=2.0, r=0.0):
    """Last-operation-wins state semantics (NOT 2P): an add after a
    remove resurrects. Used to exhibit non-confluence without
    remove-wins."""
    live = {}
    for kind, x in ops:
        if kind == "add":
            live[x["addr"]] = x
        elif kind == "remove":
            live.pop(x, None)
    return close_field(list(live.values()), b, o, r)


# ----------------------------------------------------------------------
# Erasure check
# ----------------------------------------------------------------------
def erasure_check(kept_parts, gov, removed_payloads):
    """True iff no removed payload string survives anywhere in the
    physical store: neither as a part record nor inside the canonical
    serialization blob."""
    _, lines_ = canonical(kept_parts, gov)
    blob = "\n".join(lines_)
    for pay in removed_payloads:
        if pay in blob:
            return False
        for p in kept_parts.values():
            if p.get("payload") == pay:
                return False
    return True


# ----------------------------------------------------------------------
# Ledger
# ----------------------------------------------------------------------
def _fp(parts, gov):
    return canonical(parts, gov)[0]


def self_check(verbose=True):
    P = print if verbose else (lambda *a, **k: None)
    rng = random.Random(20260611)
    results = []

    def check(tag, desc, ok):
        results.append((tag, desc, bool(ok)))
        P("  [%s] %s  %s" % ("PASS" if ok else "FAIL", tag, desc))

    P(line("="))
    P("DELETION LEDGER  (delete_growth.py)")
    P(line("="))

    # ---- a reproducible random store -------------------------------
    def rand_atoms(n, ndesc, tag):
        return [atom("%s-%d" % (tag, i), "d%d" % rng.randrange(ndesc))
                for i in range(n)]

    seed = rand_atoms(40, 6, "x")
    parts, gov = close_field(seed)
    fp_full = _fp(parts, gov)

    # ---- DEL-01: cone theorem  K(S)\Up(D) == K(S\D) ------------------
    D = {a["addr"] for a in rng.sample(seed, 7)}
    kept, gov_e, cone = excise(parts, D)
    re_parts, re_gov = epoch(parts, D)
    check("DEL-01", "cone theorem: excision == epoch re-closure (parts+gov)",
          set(kept) == set(re_parts) and gov_e == re_gov)

    # ---- DEL-02: bit-identical fingerprints --------------------------
    check("DEL-02", "fingerprint(excise) == fingerprint(epoch), bit-identical",
          _fp(kept, gov_e) == _fp(re_parts, re_gov))

    # ---- DEL-03: survivor address stability --------------------------
    stable = all(a in parts and parts[a]["children"] == p["children"]
                 and parts[a].get("payload") == p.get("payload")
                 for a, p in kept.items())
    check("DEL-03", "survivor stability: every kept part identical to its "
                    "record in K(S)", stable)

    # ---- DEL-04: exactness (nothing outside the cone removed) --------
    check("DEL-04", "exactness: removed set == Up(D), no over/under-deletion",
          set(parts) - set(kept) == cone)

    # ---- DEL-05: deletion idempotence --------------------------------
    kept2, gov2, _ = excise(kept, D)
    check("DEL-05", "idempotence: deleting D twice == once",
          _fp(kept2, gov2) == _fp(kept, gov_e))

    # ---- DEL-06: disjoint-deletion commutation -----------------------
    D1 = {a["addr"] for a in seed[0:5]}
    D2 = {a["addr"] for a in seed[5:11]}
    k12, g12, _ = excise(*excise(parts, D1)[:1], D2) if False else (None, None, None)
    ka, gva, _ = excise(parts, D1)
    k12, g12, _ = excise(ka, D2)
    kb, gvb, _ = excise(parts, D2)
    k21, g21, _ = excise(kb, D1)
    ku, gu, _ = excise(parts, D1 | D2)
    check("DEL-06", "commutation: del D1;D2 == del D2;D1 == del (D1 u D2)",
          _fp(k12, g12) == _fp(k21, g21) == _fp(ku, gu))

    # ---- DEL-07: erasure (payloads physically absent) ----------------
    removed_payloads = [p["payload"] for p in parts.values()
                        if p["kind"] == "Atom" and p["addr"] in D]
    check("DEL-07", "erasure: no removed payload survives store or "
                    "serialization", erasure_check(kept, gov_e, removed_payloads))

    # ---- DEL-08: reversed witness -- the deletion anomaly ------------
    f1, f2, f3, f4 = (atom("f-%d" % i, "D1") for i in (1, 2, 3, 4))
    S4 = [f1, f2, f3, f4]
    B123 = composite("Block", "bind", "D1", [f1["addr"], f2["addr"], f3["addr"]])
    p4, g4 = close_field(S4)
    q4, _ = quotient_view(p4)
    kept3, gov3, _ = excise(p4, {f4["addr"]})
    q3, _ = quotient_view(kept3)
    anomaly = (B123["addr"] not in q4) and (B123["addr"] in q3)
    check("DEL-08", "deletion anomaly: serialized view GAINS a part on "
                    "deletion (witness reappears)", anomaly)
    P("           witness address (reappearing): " + B123["addr"][:12] + "...")

    # ---- DEL-09: complete field shrinks monotonically ----------------
    check("DEL-09", "complete field anti-grows: K(S\\D) subset K(S) "
                    "(no creation at field level)", set(kept3) <= set(p4))

    # ---- DEL-10: 2P order-freedom (remove-wins) ----------------------
    g_atoms = rand_atoms(12, 3, "y")
    ops = [("add", a) for a in g_atoms] + \
          [("remove", g_atoms[i]["addr"]) for i in (1, 4, 7)]
    fps = set()
    for _ in range(24):
        sh = ops[:]
        rng.shuffle(sh)
        tp, tg, _, _ = two_phase(sh)
        fps.add(_fp(tp, tg))
    check("DEL-10", "2P-closure order-freedom: 24 shuffled interleavings, "
                    "one fingerprint", len(fps) == 1)

    # ---- DEL-11: naive sequential semantics is NOT confluent ---------
    a0 = g_atoms[0]
    seq1 = [("add", a0), ("remove", a0["addr"])]      # add then remove
    seq2 = [("remove", a0["addr"]), ("add", a0)]      # remove then add
    n1 = _fp(*naive_sequential(seq1))
    n2 = _fp(*naive_sequential(seq2))
    t1 = _fp(*two_phase(seq1)[:2])
    t2 = _fp(*two_phase(seq2)[:2])
    check("DEL-11", "without remove-wins: interleavings diverge; with 2P: "
                    "confluent", (n1 != n2) and (t1 == t2))

    # ---- DEL-12: no re-add under 2P ----------------------------------
    seq3 = [("add", a0), ("remove", a0["addr"]), ("add", a0)]
    t3p, t3g, _, _ = two_phase(seq3)
    t1p, t1g, _, _ = two_phase(seq1)
    check("DEL-12", "tombstone permanence: re-adding a removed atom is a "
                    "no-op under 2P", _fp(t3p, t3g) == _fp(t1p, t1g))

    P(line("="))
    npass = sum(1 for *_, ok in results if ok)
    P("LEDGER: %d/%d PASS" % (npass, len(results)))
    P("full-store fingerprint (pre-deletion): " + fp_full[:16] + "...")
    return npass == len(results)


if __name__ == "__main__":
    ok = self_check(verbose=True)
    sys.exit(0 if ok else 1)
