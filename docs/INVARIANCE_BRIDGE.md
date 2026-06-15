# Bridge note: closures, determination, and invariant-kernel discovery

This note maps the trilogy's determination/closure theory onto the
**invariant-kernel** program of statistical causal discovery — Invariant
Causal Prediction (ICP; Peters/Bühlmann/Meinshausen 2016), Invariant Risk
Minimization (IRM; Arjovsky et al. 2019), and MDL model selection
(Rissanen). The thesis in one line:

> The repo is the **proof-theory** of *invariance + minimality*; ICP/IRM/MDL
> kernel discovery is the **statistics** of the same two principles. Several
> of our theorems are the algebraic skeletons of conditions those methods
> estimate empirically.

References below are to `lean/GrowthClosure.lean` (declaration names) and to
the paper theorem numbers they carry.

## 0. Dictionary

| Kernel-discovery notion | Repo notion |
|---|---|
| environment (site / era / cohort / scanner / regime) | epoch/era (`Epoch`), cohort (`corpus_cohorts`, the Thm 11 4-atom cohort), seed / growth stage |
| target `y` | a determined quantity `x : E → A` |
| feature relationship | observer knowledge `k : E → K` |
| "relationship invariant across environments" | `Determines k x` (`Unified.Determines`) / `stable_iff` |
| spurious feature (flips across environments) | a payload-/single-context-determined criterion that is not exact across the ambient context |
| kernel = minimal invariant feature set | least fixed point / least closed superset `K` (`K_least_fixpoint`) |
| MDL/BIC minimality gate | MDL admissibility threshold `Δ(s,m) = (m−1)b − o − mr > 0`, `m₀ = ⌊o/b⌋+2` |

## 1. The invariance condition is `Determines` / `stable_iff`

ICP/IRM keep a feature exactly when its signed relationship to the target is
the **same in every environment**. Written as an equality of conditional
relationships, that is precisely the shape of

```
Determines (k : E → K) (x : E → A) : Prop := ∀ e e', k e = k e' → x e = x e'
```

`Unified.dedup_iff` and `Unified.stable_iff` then say invariance of the
*committed address* under a granularity map `g` (resp. a context map `c` —
growth stage, epoch bump, re-ingestion) holds **iff** the underlying
κ-projection is invariant under it. Swap "context map `c`" for "environment
shift" and `stable_iff` is the ICP invariance assumption stated as an
algebraic equivalence rather than a statistical test. The repo *proves* the
equivalence; ICP/IRM *estimate* the left-hand side from finite samples and
accept the feature when it cannot be rejected.

So an empirical cross-environment invariance test (sign-consistency / support
fraction across environments) is a **Rung-1 estimator** of `stable_iff`'s
hypothesis — it slots into the same three-rung ladder this repo already uses
(paper proof / executable check / Lean kernel check).

## 2. "Kernel" = least fixed point = minimal invariant core

The word is a genuine pun that survives formalization.

- In kernel discovery, the **kernel** is the *smallest* feature set closed
  under "add any feature that improves prediction without breaking
  invariance," with MDL/BIC enforcing Occam.
- In the repo, the strengthened variant `K_fixpoint` /
  `K_least_fixpoint` makes the matching object explicit: `K(S)` is the
  **least fixed point** of the inflationary operator `X ↦ S ⊔ Φ(X)` — the
  least set closed under the rule step.

Both are *least objects closed under a monotone enlargement condition*, with
minimality enforced (lattice-leastness here; MDL/BIC there). Kernel discovery
is, structurally, a least-fixpoint computation in feature space; this repo is
the lattice theory of exactly that closure, now with the least-fixpoint
characterization stated and (pending re-run of the toolchain) kernel-checked.

`K_merge` (`K(K(S) ⊔ K(T)) = K(S ⊔ T)`) adds the federation reading: two
independently discovered invariant cores combine by re-closing their join —
the closure analogue of pooling environments before re-selecting the kernel.

## 3. Spurious rejection is Theorem 11 / O1 necessity

Why can't a single environment's correlation be trusted? Because a criterion
that reads only *local* information cannot decide a property that is genuinely
a function of the *ambient context*. That is exactly what the repo proves:

- **Theorem 11** (`Impossibility.impossibility`): no payload-determined side
  condition is exact for maximality at every seed — maximality is irreducibly
  a property of the ambient seed, not of the premise tuple alone.
- **O1 necessity** (`Necessity.necessity`): no representative record yields
  exact record-local deletion; the ambient/cross-context structure is
  necessary.

Read statistically, both say: a decision rule restricted to one
context/record (≈ one environment) provably fails to capture the
cross-context-invariant truth. That is the *theorem* underneath "discard the
feature whose sign flips across environments." The decoy `s1` in a kernel
demo dies for the same reason mask 7 fails to be maximal at seed 15.

## 4. MDL appears on both ends

The repo's admissibility threshold `Δ(s,m) > 0`, `m₀ = ⌊o/b⌋+2`
(`growth_check.py`, Lean `Impossibility` cohort) is a description-length
criterion for *what to build* — which bindings are worth committing. Kernel
discovery uses MDL/BIC for *what to keep* — the smallest invariant set that
does not lose predictive value. Same Occam principle (Rissanen), applied at
opposite ends of the pipeline: admission of generators vs. selection of the
minimal core.

## 5. What is tight vs. loose

- **Tight.** `Determines`/`stable_iff` ↔ the ICP invariance condition;
  `K_least_fixpoint` ↔ minimal-kernel leastness; Thm 11 / O1 ↔
  local-information impossibility. These are structural identities, not
  metaphors.
- **Loose.** The repo is *deterministic* (exact equalities over predicates);
  ICP/IRM are *statistical* (equalities up to sampling noise, with
  bootstraps and thresholds). The bridge is "the algebraic limit of the
  estimator," not a claim that the estimator is exact at finite `n`.

## 6. The Rung-1 ↔ Rung-2 link, made precise

Next-step #3 below is now realized. `lean/GrowthClosure.lean` carries a
`Growth.Approx` namespace formalizing the *finite-sample* (approximate) face
of `stable_iff`:

- `SampleInvariant f c sample` — the empirical test: the committed value `f`
  is `c`-invariant on every sampled environment (the ε = 0, finite-sample face
  of invariance, i.e. what the cross-environment check probes).
- `sample_sound` — one-sided **soundness**: exact invariance ⇒ the test passes
  on any sample; contrapositive, a sample violation refutes exact invariance.
- `sample_complete` — **completeness in the limit**: an exhaustive sample makes
  the test exact.
- `sample_stable_iff` — the estimator's **exhaustive limit coincides with
  `stable_iff`**: exhaustive address-invariance ⟺ κ-invariance (needs the
  injective-`H` hypothesis, exactly as `stable_iff` does).

`verifiers/verify_invariance_bridge.py` is the matching Rung-1 ledger
(10/10): Part A reproduces the four facts above exactly (including the
necessity of injective `H`); Part B shows the *statistical* limit — as noise
→ 0 the empirical invariance score of the kernel feature → 1.0 while the
sign-flipping spurious feature stays rejected, so the empirical verdict
converges to the deterministic `stable_iff` verdict.

## 7. The synthesis, realized: content-addressed invariant kernel

The two former next-steps are now one artifact,
`verifiers/verify_kernel_provenance.py` (7/7), which fuses all three threads
on a single tabular table:

- **Content addressing (growth theory).** Each candidate feature is a
  composite *part* whose address is `SHA-256` over its generator spec
  (`op`, operand columns), using the same `H`/unit-separator discipline as
  `growth_check.py`. The address is a pure function of the spec
  (premise-inscribing for features), so it is deterministic and injective
  (KP-01) and identical across datasets that share columns.
- **MDL admissibility (the Δ-threshold, "what to build").** A candidate is
  admitted only if it *shortens the description* — a BIC gain
  `Δ = n ln(RSS₀/RSS₁) − ln n > floor` on the pooled fit. Pure noise is
  rejected (KP-03).
- **`stable_iff` hypothesis (determination theory, "what to keep").** A
  candidate enters the kernel only if its signed target relationship is
  consistent across **every** environment. The sign-flipping decoy `s1`
  fails this explicitly (KP-07, signs e.g. `[1,-1,1,-1]`); the invariant core
  is recovered (KP-02).

The synthesis then exhibits the growth-theory laws on the *kernel itself*:

- **History-independence (Theorem 5 flavor).** The kernel address set is
  invariant under row permutation (KP-04) and under environment relabeling
  (KP-05) — it is a function of the content, not the presentation.
- **Conservativity (Theorem 2 flavor).** Adding a fresh consistent
  environment preserves every kernel address (KP-06): survivors keep their
  exact addresses, exactly as growth never retracts.

Runs on the bundled structured benchmark by default, or on your own table via
`--data table.csv --target y --env site`. (Sandbox note: the default table is
a *structured synthetic*, not a downloaded real-world set — the environment's
network policy blocks fetching public datasets; point `--data` at a real CSV
to exercise it on genuine data.)

## 8. MDL admissibility on Rung 2, and the certified-minimal set

Both items here are now done.

**MDL admissibility lifted to Lean.** `lean/GrowthClosure.lean` gains
`Growth.Mdl`: with rate `r = 0`, a binding of `m` premises shortens the
description iff `o < (m−1)·b` (`Admits b o m`). The closed-form threshold
`m₀ = ⌊o/b⌋ + 2` — previously only checked on `growth_check.py`'s 11×11 grid
(Rung 1) — is proved to be **admissible** (`m0_admits`) and the **least**
admissible premise count (`m0_least`), over ℕ on core `Nat` arithmetic, no
mathlib. That is the "what to build" gate the kernel bridge reuses, now
kernel-checkable.

**Certified-minimal kernel set.** `verify_kernel_provenance.py` adds
`minimal_kernel` (forward selection by BIC gain + ablation, via a stdlib
multivariate OLS), matching the engine's `select_minimal_kernel`. The chosen
set is **certified minimal** — removing any member worsens BIC by at least the
ablation margin (KP-08) — and it is given a content address as a *root part*
binding its sorted members (`kernel_root_addr`), deterministic and order-free
(KP-09).

**An honest asymmetry (the Demo-E phenomenon).** The full invariant kernel is
history-independent (KP-04/05), but the *greedy minimal subset* is
**presentation-dependent**: on a permuted row order it may pick a
tie-equivalent but different set (KP-10 reports `equal=False` on the
benchmark). This is the same split the growth paper already exhibits — the
subsumption-quotient *view* is non-conservative while the *field* is — so
minimality, like the view, is a presentation-sensitive projection of a stable
object. Every minimal selection still lands **inside** the history-independent
kernel (KP-10), which bounds the instability exactly.

## 9. Remaining next steps

1. State the `m₀ = 3 ⟺ o/b ∈ [1,2)` regime characterization in Lean
   (the `Mdl` companion to the grid check), and the general `r > 0` surplus.
2. A canonical tie-break (e.g. by content address) to make the minimal set a
   deterministic function of the data, recovering history-independence at the
   cost of an arbitrary-but-stable choice among equivalent minima.
