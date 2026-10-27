#!/usr/bin/env python3
"""corpus_cohorts.py — Empirical figure 2: descriptor-cohort sizes on a real corpus.

Reproducible natural-language stress proxy for Prop 10: atoms = sentences of
Moby-Dick (Project Gutenberg #2701); descriptor of a sentence = its most
frequent non-stopword token of length >= 3 (ties broken alphabetically).
Measures the cohort-size distribution and the implied storage cost of the
complete bind semantics vs the quotient-view / cohort-object alternatives.
"""
import math, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from corpus_fixture import load_corpus, extract_sentences, descriptor_cohorts

def main():
    raw, manifest = load_corpus()
    coh = descriptor_cohorts(extract_sentences(raw))
    print("corpus snapshot        : " + manifest["snapshot_id"])
    print("source SHA-256         : " + manifest["sha256"])
    sizes = sorted(coh.values(), reverse=True)
    n_atoms, n_desc = sum(sizes), len(sizes)
    bindable = [n for n in sizes if n >= 3]
    # complete-semantics block count: sum_d (2^n - 1 - n - C(n,2)); report log10
    log10_total = None
    acc = 0.0
    for n in bindable:
        cnt = 2**n - 1 - n - n*(n-1)//2
        acc += cnt
    log10_total = math.log10(acc) if acc > 0 else 0.0
    nmax = sizes[0]
    top10 = sorted(coh.items(), key=lambda kv: -kv[1])[:10]
    print("atoms (sentences)      : %d" % n_atoms)
    print("descriptors (cohorts)  : %d" % n_desc)
    print("bindable cohorts (n>=3): %d   atoms covered: %d (%.1f%%)"
          % (len(bindable), sum(bindable), 100*sum(bindable)/n_atoms))
    print("max cohort             : n=%d ('%s')" % (nmax, top10[0][0]))
    print("top-10 cohorts         : " + ", ".join("%s:%d" % kv for kv in top10))
    print("complete-semantics blocks: ~10^%.1f   (max cohort alone: ~10^%.1f)"
          % (log10_total, nmax*math.log10(2)))
    print("quotient-view blocks   : %d (= bindable cohorts)" % len(bindable))
    print("cohort-object records  : %d (= descriptors)" % n_desc)
    fig, ax = plt.subplots(figsize=(6.0, 3.6))
    ax.loglog(range(1, len(sizes)+1), sizes, ".", ms=3, color="#1a3a5c")
    ax.axhline(3, color="#b25b1e", lw=1, ls="--")
    ax.text(1.3, 3.4, "bind threshold $m_0{=}3$", fontsize=8, color="#b25b1e")
    ax.set_xlabel("descriptor rank"); ax.set_ylabel("cohort size $n_d$")
    ax.set_title("Moby-Dick descriptor cohorts (%d sentences, %d descriptors)"
                 % (n_atoms, n_desc), fontsize=10)
    ax.grid(True, which="both", alpha=0.25)
    fig.tight_layout(); fig.savefig("fig_cohorts.pdf"); fig.savefig("fig_cohorts.png", dpi=160)
    json.dump({"atoms": n_atoms, "desc": n_desc, "bindable": len(bindable),
               "covered": sum(bindable), "nmax": nmax, "log10_total": log10_total,
               "top10": top10, "snapshot_id": manifest["snapshot_id"],
               "source_sha256": manifest["sha256"]}, open("corpus_stats.json", "w"))
    print("saved fig_cohorts.{pdf,png}")

if __name__ == "__main__":
    main()
