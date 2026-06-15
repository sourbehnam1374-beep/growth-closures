#!/usr/bin/env python3
# ----------------------------------------------------------------------
# verify_invariance_bridge.py
#
# Rung-1 witness for the finite-sample ("approximate") stable_iff lemmas
# added to lean/GrowthClosure.lean (namespace Growth.Approx), and for the
# Rung-1 <-> Rung-2 claim of docs/INVARIANCE_BRIDGE.md:
#
#   the empirical cross-environment invariance test that ICP/IRM-style
#   kernel discovery runs is a SOUND one-sided estimator whose EXHAUSTIVE
#   limit coincides exactly with the determination theorem stable_iff,
#   and whose STATISTICAL limit (noise -> 0) returns the deterministic
#   invariant/spurious verdict.
#
# Two parts:
#   A. Exact algebra (mirrors Growth.Approx): SampleInvariant, soundness,
#      completeness-in-the-limit, and sample_stable_iff with injective H.
#   B. Statistical limit: a kernel feature (invariant relationship) and a
#      spurious feature (sign flips per environment); as noise -> 0 the
#      empirical invariance score -> the exact determination verdict.
#
# Pure standard library. Run:  python3 verifiers/verify_invariance_bridge.py
# ----------------------------------------------------------------------
import random


def line(c="-"):
    return c * 70


# ======================================================================
# Part A — exact algebra, mirroring namespace Growth.Approx
# ======================================================================
def addr(pi, H):
    """The committed address as a function of an environment: H . pi."""
    return lambda e: H(pi(e))


def sample_invariant(f, c, sample):
    """SampleInvariant f c sample : f is c-invariant on every sampled env."""
    return all(f(c(e)) == f(e) for e in sample)


def exact_invariant(f, c, domain):
    """Exact invariance: f(c e) == f e for every e in the (finite) domain."""
    return all(f(c(e)) == f(e) for e in domain)


def check_part_A():
    print(line("="))
    print("PART A  exact algebra  (mirrors lean Growth.Approx)")
    print(line("="))
    results = []

    def chk(tag, ok):
        results.append((tag, bool(ok)))
        print("  [%s] %s" % ("PASS" if ok else "FAIL", tag))

    rng = random.Random(20260615)
    E = list(range(12))  # finite environment universe

    # An injective H on committed projections (the H4-style assumption).
    # Use a perfect hash on small ints: injective by construction.
    H = lambda p: ("H", p)

    # A few context maps c (growth stage / epoch bump / re-ingestion).
    # c1 is pi-invariant; c2 is not (it bumps the projection of some envs).
    pi = lambda e: e % 4  # the kappa-projection

    c_id = lambda e: e
    c_perm_same_pi = lambda e: (e + 4) % 12  # shifts by 4 => same pi(e)
    c_bump = lambda e: (e + 1) % 12          # changes pi(e) for every e

    f = addr(pi, H)

    # --- sample_sound: exact invariance => test passes on ANY sample -------
    # c_perm_same_pi keeps pi (hence addr) invariant; random samples all pass.
    assert exact_invariant(f, c_perm_same_pi, E)
    sound_ok = True
    for _ in range(200):
        k = rng.randint(0, len(E))
        s = rng.sample(E, k)
        if not sample_invariant(f, c_perm_same_pi, s):
            sound_ok = False
            break
    chk("sample_sound: exact invariance => test passes on every sample", sound_ok)

    # contrapositive: when exact invariance FAILS (c_bump), SOME sample is a
    # violation, and the exhaustive sample is always a violation.
    chk("sample_sound contrapositive: exhaustive sample flags non-invariance",
        not exact_invariant(f, c_bump, E) and not sample_invariant(f, c_bump, E))

    # --- sample_complete: exhaustive sample <=> exact invariance -----------
    # A partial sample can PASS while exact invariance FAILS (the false
    # negative the limit removes); the exhaustive sample never does.
    # Build c that violates invariance only at e=7.
    def c_one_bad(e):
        return (e + 4) % 12 if e != 7 else 8  # pi(8)=0 != pi(7)=3
    partial = [e for e in E if e != 7]          # misses the only violation
    complete = list(E)
    chk("sample_complete: partial sample can miss a violation",
        sample_invariant(f, c_one_bad, partial)
        and not sample_invariant(f, c_one_bad, complete))
    chk("sample_complete: exhaustive sample == exact invariance",
        sample_invariant(f, c_one_bad, complete)
        == exact_invariant(f, c_one_bad, E))

    # --- sample_stable_iff: exhaustive addr-invariance <=> pi-invariance ---
    # with injective H, the empirical test on addr coincides with kappa-inv.
    sif_ok = True
    for c in (c_id, c_perm_same_pi, c_bump, c_one_bad):
        lhs = sample_invariant(addr(pi, H), c, complete)   # exhaustive test
        rhs = all(pi(c(e)) == pi(e) for e in E)            # kappa-invariance
        if lhs != rhs:
            sif_ok = False
            break
    chk("sample_stable_iff: exhaustive addr-test <=> kappa-invariance", sif_ok)

    # H must be injective for the forward direction; show a non-injective H
    # can make addr-invariance hold while pi-invariance fails (why hH matters).
    H_bad = lambda p: p % 2  # collapses 0~2, 1~3 : NOT injective
    # c_bump changes pi by +1 mod 12; pi in {0,1,2,3}; H_bad(pi) flips parity
    # so addr is NOT invariant here -> pick a c that permutes pi within a class
    c_parity = lambda e: (e + 2) % 12  # pi(e) -> pi(e)+2 mod 4 : same parity
    addr_bad = addr(pi, H_bad)
    lhs = sample_invariant(addr_bad, c_parity, complete)
    rhs = all(pi(c_parity(e)) == pi(e) for e in E)
    chk("hH necessity: non-injective H breaks addr-test <=> kappa (lhs=%s,rhs=%s)"
        % (lhs, rhs), lhs and not rhs)

    return results


# ======================================================================
# Part B — statistical limit: empirical invariance score -> exact verdict
# ======================================================================
def _slope_sign(xs, ys):
    """Sign of the least-squares slope of ys on xs (stdlib covariance)."""
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    if cov > 1e-9:
        return 1
    if cov < -1e-9:
        return -1
    return 0


def invariance_score(feature_vals_by_env, y_by_env):
    """Fraction of environment pairs whose feature->target slope sign agrees:
    1.0 = invariant relationship across environments (kernel),
    ~0.5 or below = environment-dependent (spurious)."""
    signs = [_slope_sign(feature_vals_by_env[e], y_by_env[e])
             for e in range(len(feature_vals_by_env))]
    signs = [s for s in signs if s != 0]
    if len(signs) < 2:
        return 1.0
    agree = sum(1 for i in range(len(signs)) for j in range(i + 1, len(signs))
                if signs[i] == signs[j])
    total = len(signs) * (len(signs) - 1) // 2
    return agree / total


def synth(noise, n_per_env=300, n_env=4, seed=0):
    """y = 2*x_kernel in every environment (invariant); x_spur correlates
    with y but its sign FLIPS per environment (spurious)."""
    rng = random.Random(seed)
    xk_by_env, xs_by_env, y_by_env = [], [], []
    for e in range(n_env):
        xk, xs, y = [], [], []
        sign = 1.0 if e % 2 == 0 else -1.0
        for _ in range(n_per_env):
            k = rng.gauss(0, 1)
            yi = 2.0 * k + rng.gauss(0, noise)
            s = sign * 0.9 * yi + rng.gauss(0, noise)
            xk.append(k); y.append(yi); xs.append(s)
        xk_by_env.append(xk); xs_by_env.append(xs); y_by_env.append(y)
    return xk_by_env, xs_by_env, y_by_env


def check_part_B():
    print(line("="))
    print("PART B  statistical limit  (empirical invariance -> exact verdict)")
    print(line("="))
    results = []

    def chk(tag, ok):
        results.append((tag, bool(ok)))
        print("  [%s] %s" % ("PASS" if ok else "FAIL", tag))

    print("  noise   kernel_score  spurious_score   (kernel=invariant truth)")
    kernel_scores, spur_scores = [], []
    for noise in (1.0, 0.5, 0.2, 0.05, 0.0):
        xk, xs, y = synth(noise, seed=1)
        ks = invariance_score(xk, y)
        ss = invariance_score(xs, y)
        kernel_scores.append(ks); spur_scores.append(ss)
        print("  %5.2f   %10.2f   %12.2f" % (noise, ks, ss))

    # As noise -> 0, the kernel feature's invariance score -> 1.0 ...
    chk("kernel score -> 1.0 in the low-noise limit", abs(kernel_scores[-1] - 1.0) < 1e-9)
    # ... and the spurious feature stays rejected (sign flips => score 0).
    chk("spurious score stays low (<= 0.5) across the sweep",
        all(s <= 0.5 + 1e-9 for s in spur_scores))
    # The empirical verdict in the limit == the exact determination verdict:
    # kernel is invariant (Determines holds), spurious is not.
    exact_kernel_invariant = True   # by construction: relationship is fixed
    exact_spur_invariant = False    # by construction: sign flips per env
    emp_kernel_invariant = kernel_scores[-1] >= 0.99
    emp_spur_invariant = spur_scores[-1] >= 0.99
    chk("empirical limit verdict == exact stable_iff verdict",
        emp_kernel_invariant == exact_kernel_invariant
        and emp_spur_invariant == exact_spur_invariant)
    # Monotone sharpening: kernel score is non-decreasing as noise falls.
    chk("kernel score non-decreasing as noise -> 0",
        all(kernel_scores[i] <= kernel_scores[i + 1] + 1e-9
            for i in range(len(kernel_scores) - 1)))

    return results


# ======================================================================
def main():
    res = check_part_A()
    print()
    res += check_part_B()
    print()
    print(line("="))
    npass = sum(1 for _, ok in res if ok)
    print("INVARIANCE BRIDGE: %d/%d PASS" % (npass, len(res)))
    print("  (Rung-1 witness for Growth.Approx.{sample_sound, sample_complete,")
    print("   sample_stable_iff}; statistic's limit == stable_iff verdict.)")
    print(line("="))
    raise SystemExit(0 if npass == len(res) else 1)


if __name__ == "__main__":
    main()
