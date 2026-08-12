#!/usr/bin/env python3
"""bench_growth.py — Empirical figure 1: incremental vs batch closure cost.

Cohort-capped random corpora (every descriptor cohort <= 5 atoms, so the
complete closure stays linear-ish); fixed delta of 20 atoms; growing base.
Measures median-of-5 wall time for (a) batch reclosure of S u D from scratch
vs (b) frontier-local incremental closure from the precomputed K(S).
Pure measurement of the reference implementation; no indexing optimizations.
"""
import time, random, statistics, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import growth_check as gc

COHORT_CAP = 5
DELTA_N = 20
BASES = [250, 500, 1000, 2000, 4000, 8000]
REPS = 5

def make_atoms(n, start, rnd):
    out = []
    for i in range(start, start + n):
        d = "D%d" % (i // COHORT_CAP)          # consecutive ids -> cohorts of 5
        out.append(gc.atom("p%d" % i, d))
    return out

def main():
    rows = []
    rnd = random.Random(0)
    for nb in BASES:
        base = make_atoms(nb, 0, rnd)
        delta = make_atoms(DELTA_N, nb, rnd)   # fresh descriptors for the delta
        # spread half the delta into existing cohorts to exercise absorption
        for j in range(DELTA_N // 2):
            delta[j]["descriptor"] = "D%d" % rnd.randrange(nb // COHORT_CAP)
        pS, _ = gc.close_field(base)           # outside the timer
        tb, ti = [], []
        for _ in range(REPS):
            t0 = time.perf_counter(); gc.close_field(base + delta);      tb.append(time.perf_counter() - t0)
            t0 = time.perf_counter(); gc.close_incremental(pS, delta);   ti.append(time.perf_counter() - t0)
        # equality check once per size
        ip, ig = gc.close_incremental(pS, delta)
        bp, bg = gc.close_field(base + delta)
        assert gc.canonical(ip, ig)[0] == gc.canonical(bp, bg)[0]
        rows.append((nb, len(bp), statistics.median(tb), statistics.median(ti)))
        print("base=%5d  parts=%6d  batch=%7.3fs  incremental=%7.3fs  speedup=%5.1fx"
              % (nb, len(bp), rows[-1][2], rows[-1][3], rows[-1][2] / rows[-1][3]))
    xs = [r[0] for r in rows]
    fig, ax = plt.subplots(figsize=(6.0, 3.6))
    ax.plot(xs, [r[2] for r in rows], "o-", color="#1a3a5c", label="batch reclosure of $K(S\\cup D)$")
    ax.plot(xs, [r[3] for r in rows], "s-", color="#b25b1e", label="incremental $K(K(S)\\cup D)$ (Thm 3/4)")
    ax.set_xlabel("base corpus size $|S|$ (atoms; cohorts $\\leq$ 5)")
    ax.set_ylabel("median wall time (s)")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_title("Delta integration cost, $|D|=20$ fixed", fontsize=10)
    ax.legend(fontsize=8); ax.grid(True, which="both", alpha=0.25)
    fig.tight_layout(); fig.savefig("fig_benchmark.pdf"); fig.savefig("fig_benchmark.png", dpi=160)
    json.dump(rows, open("bench_rows.json", "w"))
    print("saved fig_benchmark.{pdf,png}")

if __name__ == "__main__":
    main()
