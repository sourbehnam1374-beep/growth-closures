#!/usr/bin/env python3
"""
AI adversarial verification harness for growth-closures.

Purpose:
  - Do NOT merely rerun the repository's own assertions.
  - Build an independent oracle from the published operational semantics.
  - Compare implementation vs oracle exhaustively on bounded finite spaces.
  - Stress central growth, incremental, deletion/identity claims.
  - Record suspicious edge cases without silently normalizing them away.

No third-party dependencies.
"""
from __future__ import annotations
import hashlib
import itertools
import json
import os
from math import comb

import growth_check as gc

US = b"\x1f"

def H(*parts):
    h = hashlib.sha256()
    for p in parts:
        if isinstance(p, str):
            p = p.encode("utf-8")
        h.update(p)
        h.update(US)
    return h.hexdigest()

TOP_ADDR = hashlib.sha256(b"TOP").hexdigest()

def o_atom(payload, descriptor):
    # Independent implementation of the repository's stated atom commitment.
    return {
        "addr": H("Atom", payload),
        "kind": "Atom",
        "rule": "input",
        "sign": descriptor,
        "children": (),
        "payload": payload,
        "descriptor": descriptor,
    }

def o_comp(kind, rule, sign, child_addrs):
    ch = tuple(sorted(child_addrs))
    return {
        "addr": H(kind, rule, sign, *ch),
        "kind": kind,
        "rule": rule,
        "sign": sign,
        "children": ch,
    }

def o_admissible(m, b=2.0, o=2.0, r=0.0):
    return m >= 3 and ((m - 1) * b - o - m * r) > 0

def oracle_close(seed, b=2.0, o=2.0, r=0.0):
    # Direct closed-form oracle for this finite type tower.
    parts = {p["addr"]: dict(p) for p in seed}
    atoms = [p for p in parts.values() if p["kind"] == "Atom"]
    by_desc = {}
    for a in atoms:
        by_desc.setdefault(a["descriptor"], []).append(a)
    blocks = []
    for desc, group in by_desc.items():
        group = sorted(group, key=lambda x: x["addr"])
        for m in range(3, len(group) + 1):
            if not o_admissible(m, b, o, r):
                continue
            for combo in itertools.combinations(group, m):
                q = o_comp("Block", "bind", desc, [x["addr"] for x in combo])
                parts[q["addr"]] = q
                blocks.append(q)
    sections = []
    for p in list(parts.values()):
        if p["kind"] == "Block":
            q = o_comp("Section", "lift", p["sign"], [p["addr"]])
            parts[q["addr"]] = q
            sections.append(q)
    for p in list(parts.values()):
        if p["kind"] == "Section":
            q = o_comp("Root", "frame", p["sign"], [p["addr"]])
            parts[q["addr"]] = q
    gov = sorted((p["addr"], TOP_ADDR) for p in parts.values() if p["kind"] == "Root")
    return parts, gov

def norm(parts, gov):
    rows = []
    for a, p in parts.items():
        rows.append((a, p["kind"], p.get("rule", ""), p.get("sign", ""), tuple(p.get("children", ()))))
    return tuple(sorted(rows)), tuple(sorted(gov))

def powerset_indices(n):
    for mask in range(1 << n):
        yield [i for i in range(n) if mask & (1 << i)]

def determines(k, x, E):
    for e in E:
        for e2 in E:
            if k[e] == k[e2] and x[e] != x[e2]:
                return False
    return True

summary = {
    "status": "PASS",
    "checks": {},
    "observations": {},
}

# ------------------------------------------------------------------
# A. Oracle equivalence over every seed subset of a 7-atom universe.
# D1 has 4 possible atoms; D2 has 3.
# ------------------------------------------------------------------
desc = ["D1","D1","D1","D1","D2","D2","D2"]
atoms_repo = [gc.atom(f"u{i}", desc[i]) for i in range(7)]
atoms_oracle = [o_atom(f"u{i}", desc[i]) for i in range(7)]

oracle_cases = 0
for idxs in powerset_indices(7):
    rr, rg = gc.close_field([atoms_repo[i] for i in idxs])
    oo, og = oracle_close([atoms_oracle[i] for i in idxs])
    assert norm(rr, rg) == norm(oo, og), ("oracle mismatch", idxs)
    oracle_cases += 1
summary["checks"]["oracle_equivalence_all_seed_subsets"] = {
    "cases": oracle_cases,
    "result": "PASS",
}

# ------------------------------------------------------------------
# B. Exhaustive S subset T growth pairs, encoded ternarily:
# 0 absent from both; 1 in S and T; 2 only in T.
# Checks conservativity + incremental == full reclosure.
# ------------------------------------------------------------------
pair_cases = 0
for state in itertools.product((0,1,2), repeat=7):
    Sidx = [i for i,v in enumerate(state) if v == 1]
    Tidx = [i for i,v in enumerate(state) if v in (1,2)]
    Didx = [i for i,v in enumerate(state) if v == 2]

    s_parts, s_gov = gc.close_field([atoms_repo[i] for i in Sidx])
    t_parts, t_gov = gc.close_field([atoms_repo[i] for i in Tidx])
    assert set(s_parts).issubset(set(t_parts)), ("non-monotone complete closure", state)

    inc_parts, inc_gov = gc.close_incremental(s_parts, [atoms_repo[i] for i in Didx])
    assert norm(inc_parts, inc_gov) == norm(t_parts, t_gov), ("incremental mismatch", state)
    pair_cases += 1

summary["checks"]["growth_conservativity_exhaustive_pairs"] = {
    "cases": pair_cases,
    "result": "PASS",
}
summary["checks"]["incremental_equals_batch_exhaustive_pairs"] = {
    "cases": pair_cases,
    "result": "PASS",
}

# ------------------------------------------------------------------
# C. History independence for all 5! singleton ingestion orders.
# ------------------------------------------------------------------
selected = atoms_repo[:5]
batch_parts, batch_gov = gc.close_field(selected)
history_cases = 0
for perm in itertools.permutations(selected):
    cur, gov = gc.close_field([])
    for a in perm:
        cur, gov = gc.close_incremental(cur, [a])
    assert norm(cur, gov) == norm(batch_parts, batch_gov), ("history mismatch", [a["payload"] for a in perm])
    history_cases += 1
summary["checks"]["singleton_ingestion_permutations"] = {
    "cases": history_cases,
    "result": "PASS",
}

# ------------------------------------------------------------------
# D. κ/O1: premise-inscription necessity + counting repair.
# Independent combinatorial model, n=4..9.
# ------------------------------------------------------------------
def admissible_subsets(n):
    items = range(n)
    for m in range(3, n + 1):
        for c in itertools.combinations(items, m):
            yield frozenset(c)

necessity_records = 0
necessity_trials = 0
counting_deletions = 0
for n in range(4, 10):
    derivs = list(admissible_subsets(n))
    all_atoms = set(range(n))
    for r in derivs:
        broke = False
        for d in range(n):
            survivors = all_atoms - {d}
            truth_keep = len(survivors) >= 3
            representative_keep = d not in r
            necessity_trials += 1
            if truth_keep != representative_keep:
                broke = True
                break
        assert broke, ("O1 necessity failed to find witness", n, sorted(r))
        necessity_records += 1

    for mask in range(1 << n):
        D = {i for i in range(n) if mask & (1 << i)}
        truth_keep = len(all_atoms - D) >= 3
        counting_keep = any(dr.isdisjoint(D) for dr in derivs)
        assert truth_keep == counting_keep, ("counting repair mismatch", n, D)
        counting_deletions += 1

summary["checks"]["o1_necessity_independent"] = {
    "representative_records": necessity_records,
    "deletion_trials_until_witnesses": necessity_trials,
    "result": "PASS",
}
summary["checks"]["counting_repair_independent"] = {
    "deletion_subsets": counting_deletions,
    "result": "PASS",
}

# ------------------------------------------------------------------
# E. Unified identity schemas over exhaustive finite functions.
# Injective H should make determination of addr equivalent to π.
# Also ensure we can produce a counterexample if H is NOT injective.
# ------------------------------------------------------------------
E = range(3)
P = range(2)
G = range(2)
schema_cases = 0
for pi_tuple in itertools.product(P, repeat=3):
    pi = {e: pi_tuple[e] for e in E}
    addr = {e: 100 + pi[e] for e in E}  # injective H on P
    for g_tuple in itertools.product(G, repeat=3):
        g = {e: g_tuple[e] for e in E}
        assert determines(g, addr, E) == determines(g, pi, E)
        schema_cases += 1
    for e in E:
        for e2 in E:
            assert ((addr[e] == addr[e2]) == (pi[e] == pi[e2]))

summary["checks"]["unified_identity_finite_models"] = {
    "determination_cases": schema_cases,
    "result": "PASS",
}

# Negative control: non-injective H invalidates unify_iff.
pi = {0: 0, 1: 1}
Hbad = {0: 7, 1: 7}
assert Hbad[pi[0]] == Hbad[pi[1]] and pi[0] != pi[1]
summary["checks"]["unified_injectivity_negative_control"] = {
    "counterexample_found": True,
    "result": "PASS",
}

# ------------------------------------------------------------------
# F. Mutation/negative controls: ensure harness rejects known-bad ideas.
# ------------------------------------------------------------------
a = [gc.atom(f"m{i}", "D1") for i in range(4)]
b3 = gc.max_blocks(a[:3])
b4 = gc.max_blocks(a)
assert not ({x["addr"] for x in b3} <= {x["addr"] for x in b4})
summary["checks"]["negative_control_max_only_is_nonmonotone"] = {"result": "PASS"}

# ------------------------------------------------------------------
# G. Identity edge observation: atom address currently commits payload,
# not descriptor. This is recorded, NOT automatically judged incorrect.
# ------------------------------------------------------------------
x1 = gc.atom("same-payload", "D1")
x2 = gc.atom("same-payload", "D2")
same_addr = x1["addr"] == x2["addr"]
summary["observations"]["same_payload_different_descriptor"] = {
    "same_address": same_addr,
    "D1_addr": x1["addr"],
    "D2_addr": x2["addr"],
    "interpretation_required": (
        "If descriptor is intended to participate in Atom identity, this is a collision-by-design; "
        "if descriptor is intentionally non-identity metadata, it is expected."
    ),
}

outdir = os.environ.get("VERIFY_OUT", "verification-logs")
os.makedirs(outdir, exist_ok=True)
path = os.path.join(outdir, "ai_adversarial_summary.json")
with open(path, "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2, sort_keys=True)

print(json.dumps(summary, indent=2, sort_keys=True))
print("AI_ADVERSARIAL_VERIFICATION: PASS")
