#!/usr/bin/env python3
"""
verify_unified.py — the Determination Theorem's schemas, instantiated on
the reference implementation. Each check is the concrete face of one
kernel-checked schema in Growth.Unified.
"""
import random
import growth_check as gc

ok = {}

# (a) unify_iff: unification <=> committed projections agree.
# FINDING: the implementation's atom commitment is (kind, payload) ONLY —
# the descriptor argument is NOT in the preimage. Same payload unifies
# even across descriptor arguments; the paper's invariant "descriptor is
# a payload field" is the discipline that makes this safe. Composites DO
# commit the sign. Caught by instantiating the schema.
a1 = gc.atom("the whale", "D1"); a2 = gc.atom("the whale", "D1")
a3 = gc.atom("the whale", "D2"); a4 = gc.atom("the squid", "D1")
ok["a unify_iff (atom kappa = kind+payload)"] = (
    a1["addr"] == a2["addr"] and a1["addr"] == a3["addr"]   # descriptor uncommitted
    and a1["addr"] != a4["addr"])
cd1 = gc.composite("Block", "bind", "D1", [a1["addr"], a4["addr"], gc.atom("z","D1")["addr"]])
cd2 = gc.composite("Block", "bind", "D2", [a1["addr"], a4["addr"], gc.atom("z","D1")["addr"]])
ok["a unify_iff (composite commits sign)"] = cd1["addr"] != cd2["addr"]

# (b) dedup_iff at three granularities
#     content granularity (kappa0 content-determined): dedup holds
b_content = gc.atom("x", "D1")["addr"] == gc.atom("x", "D1")["addr"]
#     nonce in kappa: dedup fails below event granularity
n1 = gc.atom("nonce:%030x|x" % random.getrandbits(120), "D1")
n2 = gc.atom("nonce:%030x|x" % random.getrandbits(120), "D1")
b_nonce = n1["addr"] != n2["addr"]
#     epoch in kappa: dedup within eras only
e_same = gc.atom("era7|x", "D1")["addr"] == gc.atom("era7|x", "D1")["addr"]
e_diff = gc.atom("era7|x", "D1")["addr"] != gc.atom("era8|x", "D1")["addr"]
ok["b dedup_iff (content / nonce / epoch)"] = b_content and b_nonce and e_same and e_diff

# (c) stable_iff with c = growth: committed projections (derivation
#     content) unchanged by ambient growth => identical addresses.
seed  = [gc.atom("s%d" % i, "D1") for i in range(4)]
delta = [gc.atom("d%d" % i, "D2") for i in range(3)]
pS, _  = gc.close_field(seed)
pSD, _ = gc.close_field(seed + delta)
ok["c stable_iff (growth invariance)"] = all(
    a in pSD and (pS[a]["kind"], pS[a].get("rule"), pS[a].get("sign"),
                  pS[a]["children"]) ==
                 (pSD[a]["kind"], pSD[a].get("rule"), pSD[a].get("sign"),
                  pSD[a]["children"])
    for a in pS)
#     c = era bump: committed projection changes => addresses change
ok["c stable_iff (era bump breaks)"] = all(
    gc.atom("era1|" + p, "D1")["addr"] != gc.atom("era2|" + p, "D1")["addr"]
    for p in ("u", "v", "w"))

# (d) confirm_of_det / triangle_edge: content-holding adversary decides
#     membership of a retained set; nonce removes that power.
removed_plain = {gc.atom("secret sentence", "D1")["addr"]}
adv_confirms  = gc.atom("secret sentence", "D1")["addr"] in removed_plain
salted_addr   = gc.atom("nonce:%030x|secret sentence" % random.getrandbits(120),
                        "D1")["addr"]
removed_salted = {salted_addr}
adv_guess = gc.atom("nonce:%030x|secret sentence" % random.getrandbits(120),
                    "D1")["addr"] in removed_salted
ok["d triangle_edge (confirm plain / fail salted)"] = adv_confirms and not adv_guess

# (e) recursive clause is NOT schema-reducible: premises feed back into
#     addresses. Composite address changes when any child does — the
#     recursion the flat schemas cannot see (O1's home).
c1 = gc.composite("Block", "bind", "D1", [a1["addr"], a3["addr"], a4["addr"]])
c2 = gc.composite("Block", "bind", "D1", [a1["addr"], a3["addr"], n1["addr"]])
ok["e recursive clause (child change reflows)"] = c1["addr"] != c2["addr"]

for k, v in ok.items():
    print("[%s] %s" % ("PASS" if v else "FAIL", k))
print("-" * 70)
print("DETERMINATION SCHEMAS:", "ALL PASS" if all(ok.values()) else "FAILURE")
