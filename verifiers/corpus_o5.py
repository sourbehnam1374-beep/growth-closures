#!/usr/bin/env python3
"""
corpus_o5.py — O5: the price of deniability, measured.

(1) Dedup mass forfeited by salting, on the Moby-Dick sentence corpus
    (same extraction pipeline as corpus_cohorts.py).
(2) Source-aware confirmation cost for unsalted address-only tombstones.
(3) Epoch semantics demonstrated on the reference implementation:
    same-era dedup; cross-era freshness (XSTAB fails); re-add after
    removal at a fresh era (READD holds).
"""
import re, math, urllib.request, collections
import growth_check as gc

URL = "https://www.gutenberg.org/files/2701/2701-0.txt"
raw = urllib.request.urlopen(URL, timeout=60).read().decode("utf-8", "replace")
s, e = raw.find("*** START"), raw.find("*** END")
body = raw[raw.find("\n", s):e] if s != -1 and e != -1 else raw
sentences = [t.strip() for t in re.split(r"[.!?]+", body) if len(t.strip()) >= 20]

N = len(sentences)
counts = collections.Counter(sentences)
Udist = len(counts)
dup_mass = N - Udist                       # ingestions unified by dedup
top_dups = [(c, p[:50]) for p, c in counts.most_common(5) if c > 1]

print("== O5 measurement: Moby-Dick sentence corpus ==")
print("ingestions (sentences)        : %d" % N)
print("distinct payloads             : %d" % Udist)
print("dedup mass (unified copies)   : %d  (%.2f%% of ingestions)"
      % (dup_mass, 100.0 * dup_mass / N))
if top_dups:
    print("most-repeated payloads        : " +
          "; ".join("x%d '%s...'" % (c, p) for c, p in top_dups[:3]))
print("source-aware confirmation     : %d hashes to cover corpus "
      "(2^%.2f); per-candidate cost O(1); deniability 0 bits unsalted"
      % (Udist, math.log2(Udist)))
lam = 128
print("salted at lambda=%d           : per-candidate cost x 2^%d; "
      "price = the %d unified copies (%.2f%%) now stored separately"
      % (lam, lam, dup_mass, 100.0 * dup_mass / N))

print()
print("== epoch semantics on the reference implementation ==")
content = "the whale surfaced at dawn"
a1  = gc.atom("era1|" + content, "D1")   # ingestion, era 1
a1b = gc.atom("era1|" + content, "D1")   # duplicate ingestion, same era
a2  = gc.atom("era2|" + content, "D1")   # same content, era 2
same_era_dedup  = (a1["addr"] == a1b["addr"])
cross_era_fresh = (a1["addr"] != a2["addr"])
# 2P removal of the era-1 identity; re-add at era 2 is live
A = {a1["addr"]: a1}; R = {a1["addr"]}
A2 = dict(A); A2[a2["addr"]] = a2
live = {k: v for k, v in A2.items() if k not in R}
parts, _ = gc.close_field(list(live.values()))
readd_live = a2["addr"] in parts and a1["addr"] not in parts
print("same-era duplicate dedups (one address)      :", "PASS" if same_era_dedup else "FAIL")
print("cross-era same content is fresh (XSTAB fails):", "PASS" if cross_era_fresh else "FAIL")
print("removed at era1, re-added era2 -> live (READD):", "PASS" if readd_live else "FAIL")
print("-" * 70)
print("O5 + kappa5 demo:", "ALL PASS" if (same_era_dedup and cross_era_fresh and readd_live) else "FAILURE")
