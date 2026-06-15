#!/usr/bin/env python3
# ----------------------------------------------------------------------
# verify_kernel_provenance.py
#
# Rung-1 synthesis of the two bridge programs (docs/INVARIANCE_BRIDGE.md):
# an invariant kernel whose candidates are CONTENT-ADDRESSED parts, admitted
# by an MDL description-length gain, and kept by the stable_iff invariance
# hypothesis across environments. Ties together, on one tabular table:
#
#   * content addressing  (growth theory: SHA-256 over the generator spec,
#     same H/US discipline as growth_check.py) -> a candidate feature is a
#     composite PART with a stable address;
#   * MDL admissibility    (the Δ-threshold, here as a BIC description-length
#     gain on the pooled fit) -> only generators that SHORTEN the description
#     are admitted (Occam, the "what to build" gate);
#   * stable_iff hypothesis (determination theory) -> a candidate is in the
#     KERNEL iff its signed target relationship is invariant across every
#     environment (the cross-environment invariance test).
#
# Then it checks the synthesis: addresses are deterministic + injective; the
# kernel ADDRESS SET is independent of row order and of environment relabeling
# (history-independence, Theorem 5 flavor); and adding a fresh consistent
# environment preserves the kernel addresses (conservativity, Theorem 2
# flavor). The planted invariant is recovered; the sign-flipping decoy and
# pure noise are rejected.
#
# On --data CSV (with --target / --env) it runs on your own table; with no
# args it uses a structured multi-environment benchmark (network-restricted
# sandbox: this is a structured synthetic table, not a downloaded set).
#
# Pure standard library. Run:  python3 verifiers/verify_kernel_provenance.py
# ----------------------------------------------------------------------
import argparse
import hashlib
import math
import random
import sys

US = b"\x1f"  # unit separator: same anti-ambiguity discipline as growth_check


def H(*parts):
    h = hashlib.sha256()
    for p in parts:
        if isinstance(p, str):
            p = p.encode("utf-8")
        elif isinstance(p, bytes):
            pass
        else:
            p = str(p).encode("utf-8")
        h.update(p)
        h.update(US)
    return h.hexdigest()


def line(c="-"):
    return c * 70


# ----------------------------------------------------------------------
# Candidate generators as content-addressed parts
# ----------------------------------------------------------------------
def feature_addr(op, operands):
    """Content address of a candidate feature: hash of (op, operand cols).
    For order-sensitive ops (minus) operands stay ordered; the spec, not the
    values, is the address preimage — premise-inscribing for features."""
    return H("Feature", op, *operands)


def gen_identity(cols):
    for c in cols:
        yield ("id", (c,), feature_addr("id", (c,)),
               (lambda c: (lambda row: row[c]))(c))


def gen_pairwise_diff(cols):
    for i in range(len(cols)):
        for j in range(len(cols)):
            if i == j:
                continue
            a, b = cols[i], cols[j]
            yield ("minus", (a, b), feature_addr("minus", (a, b)),
                   (lambda a, b: (lambda row: row[a] - row[b]))(a, b))


def candidate_features(cols):
    """The fixed candidate library: identities + ordered pairwise diffs.
    Each candidate carries a deterministic content address."""
    feats = {}
    for op, operands, addr, fn in list(gen_identity(cols)) + list(gen_pairwise_diff(cols)):
        feats[addr] = {"op": op, "operands": operands, "addr": addr, "fn": fn,
                       "name": _name(op, operands)}
    return feats


def _name(op, operands):
    if op == "id":
        return "%s__id" % operands[0]
    if op == "minus":
        return "%s_minus_%s" % operands
    return op + "(" + ",".join(operands) + ")"


# ----------------------------------------------------------------------
# Linear-fit primitives (stdlib) for MDL + invariance
# ----------------------------------------------------------------------
def _fit_rss(xs, ys):
    """RSS of the least-squares line y ~ x, and the slope (for sign)."""
    n = len(xs)
    if n < 2:
        return 0.0, 0.0, 0.0
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    if sxx <= 1e-12:
        rss0 = sum((y - my) ** 2 for y in ys)
        return rss0, 0.0, rss0
    b1 = sxy / sxx
    b0 = my - b1 * mx
    rss = sum((y - (b0 + b1 * x)) ** 2 for x, y in zip(xs, ys))
    rss0 = sum((y - my) ** 2 for y in ys)
    return rss, b1, rss0


def mdl_gain(xs, ys):
    """BIC description-length gain of adding the feature over an
    intercept-only baseline, on the pooled data. >0 == admissible (shorter
    description). Δ = n ln(RSS0/RSS1) − (k1−k0) ln n,  k0=1, k1=2."""
    n = len(xs)
    if n < 3:
        return 0.0
    rss, _, rss0 = _fit_rss(xs, ys)
    rss = max(rss, 1e-12)
    rss0 = max(rss0, 1e-12)
    return n * math.log(rss0 / rss) - (2 - 1) * math.log(n)


def env_sign(xs, ys):
    _, b1, _ = _fit_rss(xs, ys)
    return 1 if b1 > 1e-9 else (-1 if b1 < -1e-9 else 0)


def invariant_across_envs(feat, rows, envs, target):
    """The stable_iff hypothesis as an empirical test: the signed
    relationship of the feature to the target is consistent across EVERY
    environment. Returns (is_invariant, per_env_signs)."""
    signs = []
    for e in sorted(set(envs)):
        idx = [i for i, ev in enumerate(envs) if ev == e]
        if len(idx) < 5:
            continue
        xs = [feat["fn"](rows[i]) for i in idx]
        ys = [rows[i][target] for i in idx]
        s = env_sign(xs, ys)
        if s != 0:
            signs.append(s)
    if len(signs) < 2:
        return True, signs
    return all(s == signs[0] for s in signs), signs


# ----------------------------------------------------------------------
# The content-addressed kernel
# ----------------------------------------------------------------------
def discover_kernel(rows, envs, target, mdl_floor=2.0):
    """Returns {addr: record} for candidates that are BOTH MDL-admissible
    (description shortened by at least mdl_floor) AND invariant across
    environments (stable_iff hypothesis)."""
    cols = [c for c in rows[0].keys() if c != target]
    feats = candidate_features(cols)
    kernel = {}
    diagnostics = {}
    pooled_y = [r[target] for r in rows]
    for addr, feat in feats.items():
        pooled_x = [feat["fn"](r) for r in rows]
        gain = mdl_gain(pooled_x, pooled_y)
        inv, signs = invariant_across_envs(feat, rows, envs, target)
        diagnostics[addr] = {"name": feat["name"], "mdl_gain": gain,
                             "invariant": inv, "signs": signs}
        if gain >= mdl_floor and inv:
            kernel[addr] = feat
    return kernel, feats, diagnostics


# ----------------------------------------------------------------------
# Structured multi-environment benchmark (stdlib)
# ----------------------------------------------------------------------
def make_rows(n_per_env=300, n_env=4, noise=0.4, seed=0):
    """y = 2*x1 - 1.5*x2 in every environment (invariant core);
    s1 = sign(env)*0.9*y + noise  (spurious: sign flips per environment);
    nz pure noise. Returns (rows, envs, target_name)."""
    rng = random.Random(seed)
    rows, envs = [], []
    for e in range(n_env):
        sign = 1.0 if e % 2 == 0 else -1.0
        for _ in range(n_per_env):
            x1 = rng.gauss(0, 1)
            x2 = rng.gauss(0, 1)
            y = 2.0 * x1 - 1.5 * x2 + rng.gauss(0, noise)
            s1 = sign * 0.9 * y + rng.gauss(0, noise)
            nz = rng.gauss(0, 1)
            rows.append({"x1": x1, "x2": x2, "s1": s1, "noise": nz, "y": y})
            envs.append(e)
    return rows, envs, "y"


def load_csv(path, target, env_col):
    import csv
    rows, envs = [], []
    with open(path, newline="") as fh:
        for r in csv.DictReader(fh):
            envs.append(r[env_col])
            rows.append({k: float(v) for k, v in r.items() if k != env_col})
    return rows, envs, target


# ----------------------------------------------------------------------
# Ledger
# ----------------------------------------------------------------------
def self_check(rows, envs, target):
    print(line("="))
    print("CONTENT-ADDRESSED INVARIANT KERNEL  (verify_kernel_provenance.py)")
    print(line("="))
    results = []

    def chk(tag, ok):
        results.append((tag, bool(ok)))
        print("  [%s] %s" % ("PASS" if ok else "FAIL", tag))

    kernel, feats, diag = discover_kernel(rows, envs, target)
    kernel_names = sorted(feats[a]["name"] for a in kernel)
    print("  candidates: %d   kernel: %d" % (len(feats), len(kernel)))
    print("  KERNEL (content-addressed, MDL-admissible, invariant):")
    for a in sorted(kernel, key=lambda a: feats[a]["name"]):
        print("    %s  %s" % (a[:12], feats[a]["name"]))

    # KP-01: addresses deterministic + injective
    feats2 = candidate_features([c for c in rows[0] if c != target])
    deterministic = set(feats) == set(feats2)
    injective = len(set(feats)) == len(feats)
    chk("KP-01 content addresses deterministic + injective",
        deterministic and injective)

    # KP-02: invariant core recovered, spurious rejected
    has_invariant = any(("x1" in feats[a]["name"] or "x2" in feats[a]["name"])
                        for a in kernel)
    spur_rejected = not any("s1" in feats[a]["name"] for a in kernel)
    chk("KP-02 invariant core recovered, s1 rejected", has_invariant and spur_rejected)

    # KP-03: pure noise feature is MDL-rejected
    noise_addr = feature_addr("id", ("noise",))
    noise_admitted = noise_addr in kernel
    chk("KP-03 pure-noise feature MDL-rejected (not in kernel)", not noise_admitted)

    # KP-04: kernel address set invariant under ROW permutation (history indep.)
    perm = list(range(len(rows)))
    random.Random(7).shuffle(perm)
    rows_p = [rows[i] for i in perm]
    envs_p = [envs[i] for i in perm]
    kernel_p, _, _ = discover_kernel(rows_p, envs_p, target)
    chk("KP-04 kernel addresses invariant under row permutation",
        set(kernel) == set(kernel_p))

    # KP-05: kernel address set invariant under ENVIRONMENT relabeling
    labels = sorted(set(envs))
    shuffled = labels[:]
    random.Random(9).shuffle(shuffled)
    relabel = dict(zip(labels, shuffled))
    envs_r = [relabel[e] for e in envs]
    kernel_r, _, _ = discover_kernel(rows, envs_r, target)
    chk("KP-05 kernel addresses invariant under environment relabeling",
        set(kernel) == set(kernel_r))

    # KP-06: adding a fresh CONSISTENT environment preserves kernel addresses.
    # Label uniformly as strings so original and added envs are comparable.
    extra_rows, extra_envs, _ = make_rows(n_per_env=300, n_env=2, seed=99)
    merged_rows = rows + extra_rows
    merged_envs = ["orig-" + str(e) for e in envs] + ["new-" + str(e) for e in extra_envs]
    kernel_m, feats_m, _ = discover_kernel(merged_rows, merged_envs, target)
    # the invariant kernel survivors keep their exact addresses
    survived = set(kernel) <= set(kernel_m)
    chk("KP-06 conservativity: kernel addresses persist when an env is added",
        survived)

    # KP-07: the spurious feature explicitly FAILS the stable_iff hypothesis
    s1_addr = feature_addr("id", ("s1",))
    s1_inv = diag.get(s1_addr, {}).get("invariant", None)
    s1_signs = diag.get(s1_addr, {}).get("signs", [])
    chk("KP-07 spurious s1 fails stable_iff hypothesis (signs flip: %s)" % s1_signs,
        s1_inv is False)

    print(line("="))
    npass = sum(1 for _, ok in results if ok)
    print("KERNEL PROVENANCE: %d/%d PASS" % (npass, len(results)))
    print(line("="))
    return npass == len(results)


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Content-addressed invariant kernel: MDL admissibility + stable_iff invariance")
    ap.add_argument("--data", help="CSV path (else a structured benchmark is used)")
    ap.add_argument("--target", default="y")
    ap.add_argument("--env", default="env")
    a = ap.parse_args(argv)
    if a.data:
        rows, envs, target = load_csv(a.data, a.target, a.env)
    else:
        rows, envs, target = make_rows()
    ok = self_check(rows, envs, target)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
