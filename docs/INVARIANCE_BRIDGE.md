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

## 6. Suggested next steps

1. Treat an invariant-edge test (sign-consistency across environments) as an
   executable Rung-1 witness for `stable_iff`, on real tabular data.
2. Give kernel candidates content-addressed provenance: a candidate is a
   composite part; its admissibility is the MDL `Δ`-threshold; its survival
   across environments is `stable_iff`'s hypothesis.
3. State a finite-sample "approximate `stable_iff`" lemma whose exact limit is
   the Lean theorem, to make the Rung-1 ↔ Rung-2 link precise.
