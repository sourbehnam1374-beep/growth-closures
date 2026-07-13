/-
GrowthClosure.lean — Rung 2: machine-checked proofs.

Formal core of "Monotone Growth of Content-Addressed Rule Closures"
(B. Sour, working paper v1). Self-contained Lean 4 — NO imports, no mathlib,
no `sorry`. Sets are predicates `U → Prop`; the closure K is defined
impredicatively as the intersection of all closed supersets (Knaster–Tarski's
least pre-fixed point), so existence needs no iteration machinery.

Paper ↔ file map
  Lemma A/B (persistence, monotonicity)  ............ hypothesis `Mono Φ`
      (payload-determinism H2 is exactly what *discharges* `Mono` for the
       concrete rule system; taken as the standing hypothesis for the
       abstract sections and DISCHARGED below: RuleFamily.step_mono)
  Theorem 1 (closure operator) ...................... extensive, K_mono, K_idem
  Theorem 2 (conservativity), abstract form ......... conservativity
      (the address layer is the identification of parts with elements of U,
       justified by H4-injectivity, which is assumed, not proved — crypto)
  Galois adjunction K ⊣ ι ........................... galois
  Theorem 3 (incremental closure) ................... incremental
  Theorem 5 (ingestion confluence) .................. ingest_eq, history_independent
  Theorem 6 (continuity in the seed) ................ continuity
  Descent identity (atoms read back) ................ descent
  Theorem 11 (impossibility of payload-determined
      maximality) — fully decidable witness ......... Impossibility.impossibility
  Theorem 4 (semi-naive frontier locality) .......... seminaive_eq,
      seminaive_incremental (over the concrete format `RuleFamily`; the
      frontier-restricted iteration provably reaches the full closure)
  Kleene stages ..................................... stage, stageUnion_eq_K
  H1/H2 discharge ................................... RuleFamily.step_mono,
      RuleFamily.step_finitary (Mono and Finitary are THEOREMS for
      payload-determined, finite-premise rule families)

Axiom report: `#print axioms` lines at the end of the file. Expected:
only Lean's standard kernel axioms (propext, Quot.sound via funext);
no Classical.choice is needed anywhere.
-/

namespace Growth

universe u
variable {U : Type u}

/-! ## Sets as predicates -/

/-- Subset. -/
def sub (A B : U → Prop) : Prop := ∀ u, A u → B u

infixl:50 " ⊑ " => sub

/-- Union. -/
def un (A B : U → Prop) : U → Prop := fun u => A u ∨ B u

infixl:65 " ⊔ " => un

/-- The empty set. -/
def emptyPred : U → Prop := fun _ => False

theorem sub_refl (A : U → Prop) : A ⊑ A := fun _ h => h

theorem sub_trans {A B C : U → Prop} (h₁ : A ⊑ B) (h₂ : B ⊑ C) : A ⊑ C :=
  fun u hu => h₂ u (h₁ u hu)

theorem pred_ext {A B : U → Prop} (h : ∀ u, A u ↔ B u) : A = B :=
  funext fun u => propext (h u)

theorem sub_antisymm {A B : U → Prop} (h₁ : A ⊑ B) (h₂ : B ⊑ A) : A = B :=
  pred_ext fun u => ⟨h₁ u, h₂ u⟩

theorem un_left (A B : U → Prop) : A ⊑ A ⊔ B := fun _ h => Or.inl h

theorem un_right (A B : U → Prop) : B ⊑ A ⊔ B := fun _ h => Or.inr h

theorem un_sub {A B C : U → Prop} (h₁ : A ⊑ C) (h₂ : B ⊑ C) : A ⊔ B ⊑ C :=
  fun u h => h.elim (h₁ u) (h₂ u)

theorem un_assoc (A B C : U → Prop) : (A ⊔ B) ⊔ C = A ⊔ (B ⊔ C) :=
  pred_ext fun _ =>
    ⟨fun h => h.elim (fun h' => h'.elim Or.inl (fun hb => Or.inr (Or.inl hb)))
        (fun hc => Or.inr (Or.inr hc)),
     fun h => h.elim (fun ha => Or.inl (Or.inl ha))
        (fun h' => h'.elim (fun hb => Or.inl (Or.inr hb)) (fun hc => Or.inr hc))⟩

theorem un_empty (A : U → Prop) : A ⊔ emptyPred = A :=
  pred_ext fun _ => ⟨fun h => h.elim id False.elim, Or.inl⟩

/-! ## The closure (Knaster–Tarski, impredicative form) -/

/-- Monotonicity of the one-step operator. In the concrete system this is
DISCHARGED by H2 (payload-determined side conditions) via the persistence
lemma; here it is the standing hypothesis. -/
def Mono (Φ : (U → Prop) → (U → Prop)) : Prop :=
  ∀ ⦃X Y : U → Prop⦄, X ⊑ Y → Φ X ⊑ Φ Y

/-- A set closed under one-step expansion. -/
def Closed (Φ : (U → Prop) → (U → Prop)) (C : U → Prop) : Prop := Φ C ⊑ C

/-- The closure of a seed: intersection of all closed supersets. -/
def K (Φ : (U → Prop) → (U → Prop)) (S : U → Prop) : U → Prop :=
  fun u => ∀ C, S ⊑ C → Closed Φ C → C u

/-- Theorem 1(a): K is extensive. -/
theorem extensive (Φ : (U → Prop) → (U → Prop)) (S : U → Prop) : S ⊑ K Φ S :=
  fun u hu _C hSC _ => hSC u hu

/-- K(S) is least among closed supersets of S. -/
theorem K_least (Φ : (U → Prop) → (U → Prop)) {S C : U → Prop}
    (hSC : S ⊑ C) (hC : Closed Φ C) : K Φ S ⊑ C :=
  fun _u hu => hu C hSC hC

/-- K(S) is itself closed (the Knaster–Tarski step). -/
theorem K_closed (Φ : (U → Prop) → (U → Prop)) (mono : Mono Φ)
    (S : U → Prop) : Closed Φ (K Φ S) := by
  intro u hu C hSC hC
  exact hC u (mono (K_least Φ hSC hC) u hu)

/-- Theorem 1(b) = Theorem 2 (abstract conservativity): K is monotone. -/
theorem K_mono (Φ : (U → Prop) → (U → Prop)) (mono : Mono Φ)
    {S T : U → Prop} (h : S ⊑ T) : K Φ S ⊑ K Φ T :=
  K_least Φ (sub_trans h (extensive Φ T)) (K_closed Φ mono T)

/-- Theorem 2, named form: growth never retracts. The address-stable
embedding is the identification of parts with elements of `U` (H4). -/
theorem conservativity (Φ : (U → Prop) → (U → Prop)) (mono : Mono Φ)
    {S T : U → Prop} (h : S ⊑ T) : K Φ S ⊑ K Φ T :=
  K_mono Φ mono h

/-- Theorem 1(c): K is idempotent. -/
theorem K_idem (Φ : (U → Prop) → (U → Prop)) (mono : Mono Φ)
    (S : U → Prop) : K Φ (K Φ S) = K Φ S :=
  sub_antisymm (K_least Φ (sub_refl _) (K_closed Φ mono S))
    (extensive Φ (K Φ S))

/-- The Galois adjunction K ⊣ ι : for closed C,  K(S) ⊑ C  ↔  S ⊑ C. -/
theorem galois (Φ : (U → Prop) → (U → Prop)) {S C : U → Prop}
    (hC : Closed Φ C) : K Φ S ⊑ C ↔ S ⊑ C :=
  ⟨fun h => sub_trans (extensive Φ S) h, fun h => K_least Φ h hC⟩

/-! ## Theorem 3 — incremental closure -/

/-- K(S ∪ D) = K(K(S) ∪ D): never recompute from scratch. -/
theorem incremental (Φ : (U → Prop) → (U → Prop)) (mono : Mono Φ)
    (S D : U → Prop) : K Φ (S ⊔ D) = K Φ (K Φ S ⊔ D) := by
  apply sub_antisymm
  · exact K_mono Φ mono
      (un_sub (sub_trans (extensive Φ S) (un_left (K Φ S) D)) (un_right (K Φ S) D))
  · refine K_least Φ ?_ (K_closed Φ mono (S ⊔ D))
    exact un_sub (K_mono Φ mono (un_left S D))
      (sub_trans (un_right S D) (extensive Φ (S ⊔ D)))

/-! ## Theorem 5 — ingestion confluence / history independence -/

/-- Union of a list of batches. -/
def unionAll : List (U → Prop) → (U → Prop)
  | [] => emptyPred
  | B :: Bs => B ⊔ unionAll Bs

/-- Sequential ingestion: fold incremental closure over a batch list. -/
def ingest (Φ : (U → Prop) → (U → Prop)) : (U → Prop) → List (U → Prop) → (U → Prop)
  | X, [] => X
  | X, B :: Bs => ingest Φ (K Φ (X ⊔ B)) Bs

/-- Ingesting any batch list lands on the closure of the union. -/
theorem ingest_eq (Φ : (U → Prop) → (U → Prop)) (mono : Mono Φ) :
    ∀ (Bs : List (U → Prop)) (S : U → Prop),
      ingest Φ (K Φ S) Bs = K Φ (S ⊔ unionAll Bs)
  | [], S => by
      show K Φ S = K Φ (S ⊔ emptyPred)
      rw [un_empty S]
  | B :: Bs, S => by
      show ingest Φ (K Φ (K Φ S ⊔ B)) Bs = K Φ (S ⊔ (B ⊔ unionAll Bs))
      rw [← incremental Φ mono S B, ingest_eq Φ mono Bs (S ⊔ B),
          un_assoc S B (unionAll Bs)]

/-- Theorem 5: any two ingestion histories with the same total content
produce the identical field. Order and batching are irrelevant. -/
theorem history_independent (Φ : (U → Prop) → (U → Prop)) (mono : Mono Φ)
    (S : U → Prop) {Bs Cs : List (U → Prop)}
    (h : unionAll Bs = unionAll Cs) :
    ingest Φ (K Φ S) Bs = ingest Φ (K Φ S) Cs := by
  rw [ingest_eq Φ mono Bs S, ingest_eq Φ mono Cs S, h]

/-! ## Theorem 6 — continuity in the seed (streaming) -/

/-- Finitarity (H1): every produced element has a finite premise list. -/
def Finitary (Φ : (U → Prop) → (U → Prop)) : Prop :=
  ∀ (X : U → Prop) (u : U), Φ X u →
    ∃ l : List U, (∀ x, x ∈ l → X x) ∧ Φ (fun x => x ∈ l) u

def DirectedFam {ι : Type} (S : ι → U → Prop) : Prop :=
  ∀ i j, ∃ k, S i ⊑ S k ∧ S j ⊑ S k

def iUnion {ι : Type} (S : ι → U → Prop) : U → Prop := fun u => ∃ i, S i u

/-- A finite list inside a directed union sits inside one member. -/
theorem list_subset_directed {ι : Type} [Nonempty ι] {T : ι → U → Prop}
    (hdir : DirectedFam T) :
    ∀ l : List U, (∀ x, x ∈ l → iUnion T x) → ∃ k, ∀ x, x ∈ l → T k x
  | [], _ => by
      cases ‹Nonempty ι› with
      | intro k => exact ⟨k, fun x hx => nomatch hx⟩
  | a :: l, h => by
      have ha : iUnion T a := h a List.mem_cons_self
      cases ha with
      | intro i hi =>
        have hl : ∀ x, x ∈ l → iUnion T x :=
          fun x hx => h x (List.mem_cons_of_mem a hx)
        cases list_subset_directed hdir l hl with
        | intro j hj =>
          cases hdir i j with
          | intro k hk =>
            refine ⟨k, fun x hx => ?_⟩
            cases hx with
            | head => exact hk.1 a hi
            | tail _ hx' => exact hk.2 x (hj x hx')

/-- Theorem 6: K(⋃ᵢ Sᵢ) = ⋃ᵢ K(Sᵢ) for directed families. The field of a
growing corpus is the union of the stage fields; streaming is exact. -/
theorem continuity {ι : Type} [Nonempty ι]
    (Φ : (U → Prop) → (U → Prop)) (mono : Mono Φ) (hfin : Finitary Φ)
    {S : ι → U → Prop} (hdir : DirectedFam S) :
    K Φ (iUnion S) = iUnion (fun i => K Φ (S i)) := by
  have hdirK : DirectedFam (fun i => K Φ (S i)) := by
    intro i j
    cases hdir i j with
    | intro k hk => exact ⟨k, K_mono Φ mono hk.1, K_mono Φ mono hk.2⟩
  apply sub_antisymm
  · refine K_least Φ ?_ ?_
    · intro u hu
      cases hu with
      | intro i hi => exact ⟨i, extensive Φ (S i) u hi⟩
    · intro u hu
      cases hfin _ u hu with
      | intro l hl =>
        cases list_subset_directed hdirK l hl.1 with
        | intro k hk =>
          exact ⟨k, K_closed Φ mono (S k) u (mono (fun x hx => hk x hx) u hl.2)⟩
  · intro u hu
    cases hu with
    | intro i hi => exact K_mono Φ mono (fun x hx => ⟨i, hx⟩) u hi

/-! ## Descent identity — reading the atoms back -/

/-- If no rule outputs atoms, then the atoms of K(S) are exactly S:
descent ∘ ascent = id on seeds, stable under growth. -/
theorem descent (Φ : (U → Prop) → (U → Prop)) (mono : Mono Φ)
    (Atoms : U → Prop) (hno : ∀ (X : U → Prop) (u : U), Φ X u → ¬ Atoms u)
    (S : U → Prop) (hS : S ⊑ Atoms) :
    ∀ u, (K Φ S u ∧ Atoms u) ↔ S u := by
  intro u
  constructor
  · intro h
    have hC : Closed Φ (fun v => S v ∨ (K Φ S v ∧ ¬ Atoms v)) := by
      intro v hv
      refine Or.inr ⟨?_, hno _ v hv⟩
      have hsub : (fun w => S w ∨ (K Φ S w ∧ ¬ Atoms w)) ⊑ K Φ S := by
        intro w hw
        cases hw with
        | inl h' => exact extensive Φ S w h'
        | inr h' => exact h'.1
      exact K_closed Φ mono S v (mono hsub v hv)
    have hin : (fun v => S v ∨ (K Φ S v ∧ ¬ Atoms v)) u :=
      K_least Φ (fun v hv => Or.inl hv) hC u h.1
    cases hin with
    | inl h' => exact h'
    | inr h' => exact absurd h.2 h'.2
  · intro h
    exact ⟨extensive Φ S u h, hS u h⟩

/-! ## Theorem 11 — impossibility of payload-determined maximality

Concrete decidable instance: a 4-element cohort sharing one descriptor,
subsets encoded as bitmasks `m < 16`, admissibility = cardinality ≥ 3
(the m₀ = 3 regime). A payload-determined side condition is a function of
the premise tuple ONLY — here, `φ : Nat → Bool` on the mask, with no access
to the ambient seed. `Exact φ` says φ carves out exactly the ⊆-maximal
admissible bindings at EVERY seed. We refute it with the paper's witness:
the mask 7 = {a₁,a₂,a₃} is maximal at seed 7 but not at seed 15. -/

namespace Impossibility

/-- Popcount of the low 4 bits. -/
def card4 (m : Nat) : Nat := m % 2 + m / 2 % 2 + m / 4 % 2 + m / 8 % 2

/-- Subset of masks. -/
def subm (a b : Nat) : Bool := a &&& b == a

/-- Admissible binding of cohort-seed `s`: a sub-mask of size ≥ 3. -/
def adm (m s : Nat) : Bool := subm m s && Nat.ble 3 (card4 m)

/-- `m` is a ⊆-maximal admissible binding within seed `s` (s < 16, so the
range 16 sweep covers every candidate superset). -/
def maximal (m s : Nat) : Bool :=
  adm m s && (List.range 16).all (fun m' => !(adm m' s && subm m m') || (m' == m))

/-- φ is payload-determined (a function of the mask alone) and extensionally
exact: at every seed it accepts precisely the maximal admissible bindings. -/
def Exact (φ : Nat → Bool) : Prop :=
  ∀ s, s < 16 → ∀ m, m < 16 → adm m s = true →
    (φ m = true ↔ maximal m s = true)

theorem max_7_7 : maximal 7 7 = true := by decide
theorem not_max_7_15 : maximal 7 15 = false := by decide
theorem adm_7_7 : adm 7 7 = true := by decide
theorem adm_7_15 : adm 7 15 = true := by decide

/-- **Theorem 11.** No payload-determined side condition is exact for
maximality at every seed: maximality is irreducibly a property of the
ambient seed. -/
theorem impossibility : ¬ ∃ φ : Nat → Bool, Exact φ := by
  intro h
  cases h with
  | intro φ hφ =>
    have h₁ : φ 7 = true :=
      (hφ 7 (by decide) 7 (by decide) adm_7_7).mpr max_7_7
    have h₂ : maximal 7 15 = true :=
      (hφ 15 (by decide) 7 (by decide) adm_7_15).mp h₁
    rw [not_max_7_15] at h₂
    exact Bool.noConfusion h₂

end Impossibility

/-! ## Rung-2 extension (v1.3): H1+H2 discharged, Kleene stages, Theorem 4

A concrete rule format: each instance fires from a FINITE premise list (H1)
and the firing predicate is a function of the premise payloads ONLY — it
cannot inspect the ambient set (H2, payload-determinism). For this format,
monotonicity and finitarity are THEOREMS, not hypotheses; the Kleene stage
union equals K; and the frontier-restricted semi-naive iteration provably
reaches the full incremental closure (Theorem 4). -/

/-- A payload-determined rule family: `fires ps u` reads the premise list
`ps` only. The ambient set never appears — that is exactly H2. -/
structure RuleFamily (U : Type u) where
  fires : List U → U → Prop

/-- The induced one-step operator: everything some instance derives from
premises available in `X`. -/
def RuleFamily.step (R : RuleFamily U) : (U → Prop) → (U → Prop) :=
  fun X u => ∃ ps : List U, (∀ x, x ∈ ps → X x) ∧ R.fires ps u

/-- **H2 ⇒ Mono.** Payload-determined firing makes the step operator
monotone: enlarging the ambient set can only enable more instances. -/
theorem RuleFamily.step_mono (R : RuleFamily U) : Mono R.step := by
  intro X Y hXY u hu
  cases hu with
  | intro ps h => exact ⟨ps, fun x hx => hXY x (h.1 x hx), h.2⟩

/-- **H1 ⇒ Finitary.** Finite premise lists make the step operator
finitary: the witnessing list is its own finite support. -/
theorem RuleFamily.step_finitary (R : RuleFamily U) : Finitary R.step := by
  intro X u hu
  cases hu with
  | intro ps h => exact ⟨ps, h.1, ⟨ps, fun x hx => hx, h.2⟩⟩

/-! ### Kleene stages -/

/-- Stage iteration from the seed. -/
def stage (Φ : (U → Prop) → (U → Prop)) (S : U → Prop) : Nat → (U → Prop)
  | 0 => S
  | n + 1 => stage Φ S n ⊔ Φ (stage Φ S n)

theorem stage_le (Φ : (U → Prop) → (U → Prop)) (S : U → Prop)
    {m n : Nat} (h : m ≤ n) : stage Φ S m ⊑ stage Φ S n := by
  induction h with
  | refl => exact sub_refl _
  | step _ ih => exact sub_trans ih (fun _ hu => Or.inl hu)

theorem stage_sub_K (Φ : (U → Prop) → (U → Prop)) (mono : Mono Φ)
    (S : U → Prop) : ∀ n, stage Φ S n ⊑ K Φ S
  | 0 => extensive Φ S
  | n + 1 => fun u hu =>
      hu.elim (stage_sub_K Φ mono S n u)
        (fun h => K_closed Φ mono S u (mono (stage_sub_K Φ mono S n) u h))

/-- The stage union IS the closure (Kleene, for monotone finitary Φ). For a
`RuleFamily`, both hypotheses are supplied by the theorems above. -/
theorem stageUnion_eq_K (Φ : (U → Prop) → (U → Prop)) (mono : Mono Φ)
    (hfin : Finitary Φ) (S : U → Prop) :
    iUnion (stage Φ S) = K Φ S := by
  haveI : Nonempty Nat := ⟨0⟩
  apply sub_antisymm
  · intro u hu
    cases hu with
    | intro n hn => exact stage_sub_K Φ mono S n u hn
  · refine K_least Φ (fun u hu => ⟨0, hu⟩) ?_
    intro u hu
    cases hfin _ u hu with
    | intro l hl =>
      have hdir : DirectedFam (stage Φ S) := fun i j =>
        ⟨Nat.max i j, stage_le Φ S (Nat.le_max_left i j), stage_le Φ S (Nat.le_max_right i j)⟩
      cases list_subset_directed hdir l hl.1 with
      | intro k hk =>
        exact ⟨k + 1, Or.inr (mono (fun x hx => hk x hx) u hl.2)⟩

theorem rule_stageUnion_eq_K (R : RuleFamily U) (S : U → Prop) :
    iUnion (stage R.step S) = K R.step S :=
  stageUnion_eq_K R.step R.step_mono R.step_finitary S

/-! ### Theorem 4 — semi-naive frontier locality -/

/-- Constructive list split: if every element satisfies `P ∨ Q`, then either
all satisfy `P` or some element satisfies `Q`. (De Morgan over a finite list,
with no excluded middle: the disjunction is given per element.) -/
theorem list_or_split {P Q : U → Prop} :
    ∀ l : List U, (∀ x, x ∈ l → P x ∨ Q x) →
      (∀ x, x ∈ l → P x) ∨ (∃ x, x ∈ l ∧ Q x)
  | [], _ => Or.inl (fun x hx => nomatch hx)
  | a :: l, h => by
      cases h a List.mem_cons_self with
      | inr qa => exact Or.inr ⟨a, List.mem_cons_self, qa⟩
      | inl pa =>
        cases list_or_split l (fun x hx => h x (List.mem_cons_of_mem a hx)) with
        | inl hall =>
            refine Or.inl (fun x hx => ?_)
            cases hx with
            | head => exact pa
            | tail _ hx' => exact hall x hx'
        | inr hex =>
            cases hex with
            | intro w hw => exact Or.inr ⟨w, List.mem_cons_of_mem a hw.1, hw.2⟩

/-- A finite list whose elements each sit in `P` or in some member of an
ascending ℕ-chain sits, uniformly, in `P` or one single member. -/
theorem list_or_bound {P : U → Prop} {A : Nat → U → Prop}
    (hmono : ∀ {m n : Nat}, m ≤ n → A m ⊑ A n) :
    ∀ l : List U, (∀ x, x ∈ l → P x ∨ ∃ n, A n x) →
      ∃ N, ∀ x, x ∈ l → P x ∨ A N x
  | [], _ => ⟨0, fun x hx => nomatch hx⟩
  | a :: l, h => by
      cases list_or_bound hmono l
          (fun x hx => h x (List.mem_cons_of_mem a hx)) with
      | intro N hN =>
        cases h a List.mem_cons_self with
        | inl pa =>
            refine ⟨N, fun x hx => ?_⟩
            cases hx with
            | head => exact Or.inl pa
            | tail _ hx' => exact hN x hx'
        | inr hea =>
          cases hea with
          | intro n₀ ha =>
            refine ⟨Nat.max n₀ N, fun x hx => ?_⟩
            cases hx with
            | head =>
                exact Or.inr (hmono (Nat.le_max_left n₀ N) a ha)
            | tail _ hx' =>
                cases hN x hx' with
                | inl hp => exact Or.inl hp
                | inr hd =>
                    exact Or.inr (hmono (Nat.le_max_right n₀ N) x hd)

/-- Cumulative frontier stages over a base `Old`: stage 0 is the raw delta;
stage n+1 adds ONLY conclusions of instances whose premises lie in
`Old ⊔ stage n` AND that touch at least one stage-n (new) premise.
Instances with all-old premises are never fired. -/
def fstage (R : RuleFamily U) (Old D : U → Prop) : Nat → (U → Prop)
  | 0 => D
  | n + 1 =>
      fstage R Old D n ⊔
        (fun u => ∃ ps : List U,
          (∀ x, x ∈ ps → (Old ⊔ fstage R Old D n) x) ∧
          (∃ x, x ∈ ps ∧ fstage R Old D n x) ∧
          R.fires ps u)

theorem fstage_le (R : RuleFamily U) (Old D : U → Prop)
    {m n : Nat} (h : m ≤ n) : fstage R Old D m ⊑ fstage R Old D n := by
  induction h with
  | refl => exact sub_refl _
  | step _ ih => exact sub_trans ih (fun _ hu => Or.inl hu)

/-- Soundness: every frontier stage lies inside the full closure. -/
theorem fstage_sub_K (R : RuleFamily U) (Old D : U → Prop) :
    ∀ n, fstage R Old D n ⊑ K R.step (Old ⊔ D)
  | 0 => fun u hu => extensive R.step (Old ⊔ D) u (Or.inr hu)
  | n + 1 => fun u hu =>
      hu.elim (fstage_sub_K R Old D n u)
        (fun h => by
          cases h with
          | intro ps h' =>
            refine K_closed R.step R.step_mono (Old ⊔ D) u ⟨ps, ?_, h'.2.2⟩
            intro x hx
            cases h'.1 x hx with
            | inl ho => exact extensive R.step (Old ⊔ D) x (Or.inl ho)
            | inr hd => exact fstage_sub_K R Old D n x hd)

/-- **Theorem 4 (semi-naive frontier locality).** Over a closed base `Old`,
the frontier-restricted iteration — which never fires an instance whose
premises are all old — already reaches the full closure of `Old ⊔ D`:
all-old instances are sound to skip, because their conclusions are in `Old`. -/
theorem seminaive_eq (R : RuleFamily U) {Old D : U → Prop}
    (hOld : Closed R.step Old) :
    Old ⊔ iUnion (fstage R Old D) = K R.step (Old ⊔ D) := by
  apply sub_antisymm
  · refine un_sub (sub_trans (un_left Old D) (extensive R.step (Old ⊔ D))) ?_
    intro u hu
    cases hu with
    | intro n hn => exact fstage_sub_K R Old D n u hn
  · refine K_least R.step ?_ ?_
    · exact un_sub (fun u hu => Or.inl hu) (fun u hu => Or.inr ⟨0, hu⟩)
    · intro u hu
      cases hu with
      | intro ps h =>
        cases list_or_split (P := Old) (Q := iUnion (fstage R Old D)) ps
            (fun x hx => h.1 x hx) with
        | inl hall => exact Or.inl (hOld u ⟨ps, hall, h.2⟩)
        | inr hex =>
          cases hex with
          | intro w hw =>
            cases hw.2 with
            | intro n₀ hw₀ =>
              cases list_or_bound (P := Old) (A := fstage R Old D)
                  (fun {m n} hmn => fstage_le R Old D hmn) ps
                  (fun x hx => h.1 x hx) with
              | intro N hN =>
                refine Or.inr ⟨Nat.max n₀ N + 1, Or.inr ⟨ps, ?_, ?_, h.2⟩⟩
                · intro x hx
                  cases hN x hx with
                  | inl hp => exact Or.inl hp
                  | inr hd =>
                      exact Or.inr (fstage_le R Old D
                        (Nat.le_max_right n₀ N) x hd)
                · exact ⟨w, hw.1, fstage_le R Old D
                    (Nat.le_max_left n₀ N) w hw₀⟩

/-- Theorem 4 + Theorem 3 combined: starting from the prior field `K S`,
the frontier iteration computes `K (S ⊔ D)` exactly. -/
theorem seminaive_incremental (R : RuleFamily U) (S D : U → Prop) :
    K R.step S ⊔ iUnion (fstage R (K R.step S) D) = K R.step (S ⊔ D) := by
  rw [incremental R.step R.step_mono S D]
  exact seminaive_eq R (K_closed R.step R.step_mono S)


end Growth

/-! ## Axiom audit — kernel-checked, printed at compile time -/

#print axioms Growth.K_idem
#print axioms Growth.conservativity
#print axioms Growth.galois
#print axioms Growth.incremental
#print axioms Growth.ingest_eq
#print axioms Growth.history_independent
#print axioms Growth.continuity
#print axioms Growth.descent
#print axioms Growth.Impossibility.impossibility
#print axioms Growth.RuleFamily.step_mono
#print axioms Growth.RuleFamily.step_finitary
#print axioms Growth.stageUnion_eq_K
#print axioms Growth.seminaive_eq
#print axioms Growth.seminaive_incremental


/-! ## Deletion: lattice-level theory (sequel paper, kernel-checked core)

The derivation-level cone theorem `K(S\D) = K(S) \ Up(D)` needs the
premise-inscribing structure of the concrete rules and lives in the
paper + reference implementation. Everything at the lattice level —
survivor stability, the two-phase (2P) product order, remove-wins
order-freedom, tombstone permanence — is proved here, constructively,
on the same base as the growth theory. -/

namespace Growth

namespace Deletion

variable {U : Type}

/-- Set difference on predicates: the live part of `A` after removals `R`. -/
def diff (A R : U → Prop) : U → Prop := fun u => A u ∧ ¬ R u

/-- The singleton predicate. -/
def single (a : U) : U → Prop := fun u => u = a

theorem diff_sub (A R : U → Prop) : diff A R ⊑ A :=
  fun _ h => h.1

/-- Deletion never disturbs survivors: `K(S\D) ⊑ K(S)`, and in the
content-addressed reading every surviving part keeps its exact address
(conservativity, Theorem 2, instantiated downward). -/
theorem survivor_stability (Φ : (U → Prop) → (U → Prop)) (mono : Mono Φ)
    (S D : U → Prop) : K Φ (diff S D) ⊑ K Φ S :=
  conservativity Φ mono (diff_sub S D)

/-- The 2P product order: adds compared by `⊑`, removes by `⊒`. -/
theorem diff_mono {A A' R R' : U → Prop}
    (hA : A ⊑ A') (hR : R' ⊑ R) : diff A R ⊑ diff A' R' :=
  fun u h => ⟨hA u h.1, fun hr' => h.2 (hR u hr')⟩

/-- 2P-monotonicity of the live store: the closure is monotone over
`(adds, ⊑) × (removes, ⊒)` — the CALM-style escape for deletion. -/
theorem twoP_mono (Φ : (U → Prop) → (U → Prop)) (mono : Mono Φ)
    {A A' R R' : U → Prop} (hA : A ⊑ A') (hR : R' ⊑ R) :
    K Φ (diff A R) ⊑ K Φ (diff A' R') :=
  K_mono Φ mono (diff_mono hA hR)

theorem diff_diff (S D₁ D₂ : U → Prop) :
    diff (diff S D₁) D₂ = diff S (D₁ ⊔ D₂) := by
  apply pred_ext; intro u
  constructor
  · intro h
    exact ⟨h.1.1, fun hd => Or.elim hd (fun h1 => h.1.2 h1) (fun h2 => h.2 h2)⟩
  · intro h
    exact ⟨⟨h.1, fun h1 => h.2 (Or.inl h1)⟩, fun h2 => h.2 (Or.inr h2)⟩

/-- Deleting twice is deleting once. -/
theorem deletion_idem (Φ : (U → Prop) → (U → Prop)) (S D : U → Prop) :
    K Φ (diff (diff S D) D) = K Φ (diff S D) := by
  have h : diff (diff S D) D = diff S D := by
    apply pred_ext; intro u
    exact ⟨fun h => h.1, fun h => ⟨h, h.2⟩⟩
  rw [h]

/-- Sequential deletions commute and equal the union deletion. -/
theorem deletion_commute (Φ : (U → Prop) → (U → Prop)) (S D₁ D₂ : U → Prop) :
    K Φ (diff (diff S D₁) D₂) = K Φ (diff (diff S D₂) D₁) := by
  rw [diff_diff, diff_diff]
  have h : (D₁ ⊔ D₂) = (D₂ ⊔ D₁) := by
    apply pred_ext; intro u
    exact ⟨fun h => h.elim Or.inr Or.inl, fun h => h.elim Or.inr Or.inl⟩
  rw [h]

/-- Tombstone permanence: re-adding a removed atom is a no-op. -/
theorem tombstone_permanence (Φ : (U → Prop) → (U → Prop))
    (A R : U → Prop) (a : U) (ha : R a) :
    K Φ (diff (A ⊔ single a) R) = K Φ (diff A R) := by
  have h : diff (A ⊔ single a) R = diff A R := by
    apply pred_ext; intro u
    constructor
    · intro h
      refine ⟨?_, h.2⟩
      cases h.1 with
      | inl hA => exact hA
      | inr he => exact absurd (he ▸ ha) h.2
    · intro h
      exact ⟨Or.inl h.1, h.2⟩
  rw [h]

/-! ### Two-phase ingestion over operation logs (order-freedom) -/

/-- An operation log entry: a batch of adds or a batch of removes. -/
inductive Op (U : Type) where
  | add    : (U → Prop) → Op U
  | remove : (U → Prop) → Op U

/-- The grow-only add projection of a log. -/
def addsOf : List (Op U) → (U → Prop)
  | []                  => emptyPred
  | (Op.add A)    :: t  => A ⊔ addsOf t
  | (Op.remove _) :: t  => addsOf t

/-- The grow-only remove projection of a log. -/
def removesOf : List (Op U) → (U → Prop)
  | []                  => emptyPred
  | (Op.add _)    :: t  => removesOf t
  | (Op.remove R) :: t  => R ⊔ removesOf t

/-- The 2P live store of a log: close the adds minus the removes. -/
def live (Φ : (U → Prop) → (U → Prop)) (ops : List (Op U)) : U → Prop :=
  K Φ (diff (addsOf ops) (removesOf ops))

theorem un_comm (A B : U → Prop) : A ⊔ B = B ⊔ A := by
  apply pred_ext; intro u
  exact ⟨fun h => h.elim Or.inr Or.inl, fun h => h.elim Or.inr Or.inl⟩

theorem addsOf_append (l₁ l₂ : List (Op U)) :
    addsOf (l₁ ++ l₂) = addsOf l₁ ⊔ addsOf l₂ := by
  induction l₁ with
  | nil => simp [addsOf, List.nil_append]; rw [un_comm, un_empty]
  | cons h t ih =>
    cases h with
    | add A    => simp [addsOf, List.cons_append]; rw [ih, un_assoc]
    | remove R => simp [addsOf, List.cons_append]; rw [ih]

theorem removesOf_append (l₁ l₂ : List (Op U)) :
    removesOf (l₁ ++ l₂) = removesOf l₁ ⊔ removesOf l₂ := by
  induction l₁ with
  | nil => simp [removesOf, List.nil_append]; rw [un_comm, un_empty]
  | cons h t ih =>
    cases h with
    | add A    => simp [removesOf, List.cons_append]; rw [ih]
    | remove R => simp [removesOf, List.cons_append]; rw [ih, un_assoc]

/-- Remove-wins order-freedom: swapping any two segments of the log
leaves the live store unchanged. Adjacent transpositions generate every
permutation, so the live store is a function of the multiset of
operations only — the deletion analogue of history independence. -/
theorem live_swap (Φ : (U → Prop) → (U → Prop)) (l₁ l₂ : List (Op U)) :
    live Φ (l₁ ++ l₂) = live Φ (l₂ ++ l₁) := by
  unfold live
  rw [addsOf_append, removesOf_append, addsOf_append, removesOf_append,
      un_comm (addsOf l₁), un_comm (removesOf l₁)]

end Deletion

end Growth

#print axioms Growth.Deletion.survivor_stability
#print axioms Growth.Deletion.twoP_mono
#print axioms Growth.Deletion.deletion_idem
#print axioms Growth.Deletion.deletion_commute
#print axioms Growth.Deletion.tombstone_permanence
#print axioms Growth.Deletion.live_swap

/- ====================================================================
   κ-correspondence, O1: NECESSITY of premise inscription.

   Model the κ'-store on one 4-atom cohort (atoms = bits of mask 15):
   omitting premises from the commitment set collapses every admissible
   binding to ONE part. A "representative record" r is whichever
   admissible premise list the store retained for that part. Record-
   local cone excision keeps the part after deleting atom-mask d iff
   r ∩ d = ∅. Ground truth (re-closure) keeps it iff some admissible
   subset of the survivors exists.

   `necessity`     : NO representative record is correct for all
                     deletions — premise inscription is necessary for
                     record-local exact deletion (converse of the
                     deletion paper's single-derivation lemma).
   `counting_exact`: retaining ALL derivations and testing survival
                     (the counting/DRed regime) IS exact — the repair
                     and its cost are real.
   ==================================================================== -/
namespace Growth
namespace Necessity

open Impossibility  -- card4, subm, adm

/-- Ground truth: after deleting `d ⊆ 15`, the κ'-block survives iff some
admissible binding exists inside the survivor mask `15 ^^^ d`. -/
def truthKeep (d : Nat) : Bool :=
  (List.range 16).any (fun m => adm m (15 ^^^ d))

/-- Record-local excision under representative record `r`. -/
def exciseKeep (r d : Nat) : Bool := r &&& d == 0

/-- Counting/DRed regime: keep iff ANY derivation (admissible subset of
the full cohort) is disjoint from the deletion. -/
def countKeep (d : Nat) : Bool :=
  (List.range 16).any (fun m => adm m 15 && (m &&& d == 0))

/-- `r` is a correct representative: excision agrees with re-closure on
every deletion. -/
def Correct (r : Nat) : Prop :=
  ∀ d, d < 16 → subm d 15 = true → exciseKeep r d = truthKeep d

instance (r : Nat) : Decidable (Correct r) :=
  Nat.decidableBallLT 16 (fun d _ => _)

/-- **O1 (necessity).** No admissible representative record yields exact
record-local deletion: for every `r` there is a breaking deletion. -/
theorem necessity :
    ∀ r, r < 16 → adm r 15 = true → ¬ Correct r := by decide

/-- Concrete face: record {a₁,a₂,a₃} (mask 7), delete a₁ (mask 1):
excision drops the part, re-closure keeps it — over-deletion. -/
theorem witness_overdelete :
    exciseKeep 7 1 = false ∧ truthKeep 1 = true := by decide

/-- **Repair.** The counting regime is exact on every deletion. -/
theorem counting_exact :
    ∀ d, d < 16 → subm d 15 = true → countKeep d = truthKeep d := by decide

end Necessity
end Growth

#print axioms Growth.Necessity.necessity
#print axioms Growth.Necessity.counting_exact
#print axioms Growth.Necessity.witness_overdelete

/- ====================================================================
   κ-correspondence, κ5: the epoch (tag) row.

   Era-tagged identity: parts are (era, content). Pairing:
   `tombstone_permanence` (already above) says removal is permanent at a
   FIXED identity; `epoch_readd` says the same CONTENT returns live at a
   fresh era; `epoch_fresh` says cross-era identity is never stable —
   re-addability is bought exactly by giving up cross-era address
   stability and cross-era deduplication. Endpoints of the dial:
   constant era = κ₀ (tombstone permanence governs; no re-add);
   era injective per ingestion = the nonce vertex of the erasure
   triangle (no two ingestions ever share identity).
   ==================================================================== -/
namespace Growth
namespace Epoch

variable {U : Type}

open Deletion

/-- κ5, re-addability: with era ∈ κ, re-ingesting removed content at a
fresh era (e', u) ∉ R lands in the live store — by extensivity alone. -/
theorem epoch_readd (Φ : ((Nat × U) → Prop) → ((Nat × U) → Prop))
    (A R : (Nat × U) → Prop) (e' : Nat) (u : U)
    (hnr : ¬ R (e', u)) :
    K Φ (Deletion.diff (A ⊔ Deletion.single (e', u)) R) (e', u) :=
  extensive Φ _ (e', u) ⟨Or.inr rfl, hnr⟩

/-- κ5, instability: the same content at different eras is a different
part. Read forward: re-addability exists; read backward: cross-era
address stability (XSTAB) and cross-era deduplication fail by
construction. -/
theorem epoch_fresh (e e' : Nat) (u : U) (h : e ≠ e') :
    (e, u) ≠ (e', u) :=
  fun heq => h (congrArg Prod.fst heq)

end Epoch
end Growth

#print axioms Growth.Epoch.epoch_readd
#print axioms Growth.Epoch.epoch_fresh

/- ====================================================================
   κ-correspondence: THE DETERMINATION THEOREM (unified statement).

   An identity scheme is addr = H ∘ π: π the κ-projection of ingestion
   events, H injective on committed projections (the H4-style
   assumption, hypothesis hH). `Determines k x`: knowledge k fixes x.
   Schemas: unify_iff (core), dedup_iff (κ2/κ3/κ5 granularity lever),
   stable_iff (CONS / XSTAB), confirm_of_det (κ6/audit).
   Two-observer identity: DEDUP and ¬DEN are the same predicate,
   `Determines k addr`, at two stations; the erasure triangle's
   impossibility edge is its corollary (triangle_edge).
   The recursive clause (premises ∈ κ ⟺ exact record-local deletion)
   does NOT reduce to these schemas — that is O1 / Growth.Necessity.
   ==================================================================== -/
namespace Growth
namespace Unified

variable {E P A K G : Type}

/-- Observer-knowledge `k` determines quantity `x`. -/
def Determines (k : E → K) (x : E → A) : Prop :=
  ∀ e e', k e = k e' → x e = x e'

/-- The committed address: hash of the κ-projection. -/
def addr (π : E → P) (H : P → A) : E → A := fun e => H (π e)

/-- **Core.** Unification ⟺ committed projections agree. -/
theorem unify_iff (π : E → P) (H : P → A)
    (hH : ∀ p p', H p = H p' → p = p') (e e' : E) :
    addr π H e = addr π H e' ↔ π e = π e' :=
  ⟨fun h => hH _ _ h, fun h => congrArg H h⟩

/-- **Dedup schema.** g-granular dedup ⟺ the commitment is
g-determined. g = content: κ2. Committed nonce: fails below event
granularity (κ3). Committed epoch: holds within eras (κ5). -/
theorem dedup_iff (π : E → P) (H : P → A)
    (hH : ∀ p p', H p = H p' → p = p') (g : E → G) :
    Determines g (addr π H) ↔ Determines g π :=
  ⟨fun h e e' hg => hH _ _ (h e e' hg),
   fun h e e' hg => congrArg H (h e e' hg)⟩

/-- **Stability schema.** Address invariance under a context map c
(growth stage, epoch bump, re-ingestion) ⟺ κ-invariance under c.
Growth: derivation content unchanged ⟹ conservativity's identity half.
Epoch bump: committed era changes ⟹ XSTAB fails (κ5). -/
theorem stable_iff (π : E → P) (H : P → A)
    (hH : ∀ p p', H p = H p' → p = p') (c : E → E) :
    (∀ e, addr π H (c e) = addr π H e) ↔ (∀ e, π (c e) = π e) :=
  ⟨fun h e => hH _ _ (h e), fun h e => congrArg H (h e)⟩

/-- **Confirmation schema.** If k determines the commitment, k decides
membership of any retained address set (audit predicate). -/
theorem confirm_of_det (π : E → P) (H : P → A) (k : E → K)
    (hdet : Determines k π) (Ret : A → Prop) :
    ∀ e e', k e = k e' → (Ret (addr π H e) ↔ Ret (addr π H e')) :=
  fun e e' hk => by
    rw [show addr π H e = addr π H e' from congrArg H (hdet e e' hk)]

/-- **Two-observer identity.** Store-side deduplication and adversary-
side confirmability are the SAME determination at two stations. -/
theorem dedup_is_confirmability (π : E → P) (H : P → A)
    (hH : ∀ p p', H p = H p' → p = p') (k : E → K) :
    Determines k (addr π H) ↔ Determines k π :=
  dedup_iff π H hH k

/-- **Triangle edge, derived.** DEDUP + AUDIT ⟹ a content-holding
adversary confirms removals (¬DEN): the erasure triangle's
impossibility edge as a corollary of the schemas. -/
theorem triangle_edge (π : E → P) (H : P → A) (content : E → K)
    (hDEDUP : Determines content π) (Ret : A → Prop) :
    ∀ e e', content e = content e' →
      (Ret (addr π H e) ↔ Ret (addr π H e')) :=
  confirm_of_det π H content hDEDUP Ret

end Unified
end Growth

#print axioms Growth.Unified.unify_iff
#print axioms Growth.Unified.dedup_iff
#print axioms Growth.Unified.stable_iff
#print axioms Growth.Unified.confirm_of_det
#print axioms Growth.Unified.dedup_is_confirmability
#print axioms Growth.Unified.triangle_edge

/- ====================================================================
   STRENGTHENED VARIANTS (stronger-variant branch).

   Every statement below strictly strengthens or generalizes a theorem
   of the development above, on the same constructive base (no imports,
   no mathlib, no Classical.choice):

   K_fixpoint / K_least_fixpoint  strengthen Theorem 1: K(S) is not
       merely the least CLOSED superset of S — it is the least FIXED
       POINT of the inflationary operator X ↦ S ⊔ Φ(X). The closure-
       operator laws are corollaries of this sharper identity.
   K_merge  strengthens Theorem 3 (incremental closure) to replica
       merge: the closure of the join of two independently grown
       fields is the field of the joined seeds — federation needs no
       recomputation from raw seeds.
   ingest_extends  strengthens Theorem 5 (history independence) with
       the extension half: PROLONGING an ingestion history can only
       grow the field; streams never retract (CALM, growth side).
   tombstone_permanence_set  generalizes tombstone permanence from a
       single re-added atom to an arbitrary re-added SET of removed
       content.
   live_extend_adds / live_extend_removes  the 2P CALM sandwich over
       operation logs: an add-only suffix grows the live store, a
       remove-only suffix shrinks it — the two monotone halves of
       2P-monotonicity (twoP_mono), at the log level.
   live_replay  replaying an entire log is a no-op: at-least-once
       delivery is free under 2P (with live_swap: any shuffled
       replay).
   ==================================================================== -/
namespace Growth

universe v
variable {U : Type v}

/-- Idempotence of union. -/
theorem un_idem (A : U → Prop) : A ⊔ A = A :=
  pred_ext fun _ => ⟨fun h => h.elim id id, Or.inl⟩

/-- The empty set is a left unit of union. -/
theorem empty_un (A : U → Prop) : emptyPred ⊔ A = A :=
  pred_ext fun _ => ⟨fun h => h.elim False.elim id, Or.inr⟩

/-- **Theorem 1, strengthened.** K(S) is a FIXED POINT of the
inflationary operator X ↦ S ⊔ Φ(X), not merely a closed superset:
the field is exactly the seed together with the one-step image of the
field. (⊒ is extensivity + closedness; ⊑ is the new content: the seed
joined with the one-step image of the field is already closed.) -/
theorem K_fixpoint (Φ : (U → Prop) → (U → Prop)) (mono : Mono Φ)
    (S : U → Prop) : K Φ S = S ⊔ Φ (K Φ S) := by
  apply sub_antisymm
  · refine K_least Φ (un_left S (Φ (K Φ S))) ?_
    intro u hu
    exact Or.inr (mono (un_sub (extensive Φ S) (K_closed Φ mono S)) u hu)
  · exact un_sub (extensive Φ S) (K_closed Φ mono S)

/-- **Theorem 1, strengthened (minimality).** K(S) is LEAST among all
fixed points of X ↦ S ⊔ Φ(X): any store that already contains its seed
and its own one-step consequences contains the field. With
`K_fixpoint`, K(S) is THE least fixed point. -/
theorem K_least_fixpoint (Φ : (U → Prop) → (U → Prop))
    {S X : U → Prop} (hX : X = S ⊔ Φ X) : K Φ S ⊑ X := by
  refine K_least Φ (fun u hu => ?_) (fun u hu => ?_)
  · rw [hX]; exact Or.inl hu
  · rw [hX]; exact Or.inr hu

/-- **Theorem 3, strengthened (replica merge).** Two independently
closed fields merge by closing their JOIN — identical to the field of
the joined seeds. Incremental closure (Theorem 3) is the special case
T := D with K(D) replaced by D via idempotence. -/
theorem K_merge (Φ : (U → Prop) → (U → Prop)) (mono : Mono Φ)
    (S T : U → Prop) : K Φ (K Φ S ⊔ K Φ T) = K Φ (S ⊔ T) := by
  apply sub_antisymm
  · exact K_least Φ
      (un_sub (K_mono Φ mono (un_left S T)) (K_mono Φ mono (un_right S T)))
      (K_closed Φ mono (S ⊔ T))
  · exact K_mono Φ mono
      (un_sub (sub_trans (extensive Φ S) (un_left (K Φ S) (K Φ T)))
        (sub_trans (extensive Φ T) (un_right (K Φ S) (K Φ T))))

theorem unionAll_append : ∀ (Bs Cs : List (U → Prop)),
    unionAll (Bs ++ Cs) = unionAll Bs ⊔ unionAll Cs
  | [], Cs => by
      show unionAll Cs = emptyPred ⊔ unionAll Cs
      rw [empty_un]
  | B :: Bs, Cs => by
      show B ⊔ unionAll (Bs ++ Cs) = (B ⊔ unionAll Bs) ⊔ unionAll Cs
      rw [unionAll_append Bs Cs, un_assoc]

/-- **Theorem 5, strengthened (history extension).** Prolonging an
ingestion history can only grow the field: every part of the shorter
history's field persists — at its exact address — through any further
batches. The CALM growth half, at the level of histories. -/
theorem ingest_extends (Φ : (U → Prop) → (U → Prop)) (mono : Mono Φ)
    (S : U → Prop) (Bs Cs : List (U → Prop)) :
    ingest Φ (K Φ S) Bs ⊑ ingest Φ (K Φ S) (Bs ++ Cs) := by
  rw [ingest_eq Φ mono Bs S, ingest_eq Φ mono (Bs ++ Cs) S, unionAll_append]
  exact K_mono Φ mono
    (un_sub (un_left S (unionAll Bs ⊔ unionAll Cs))
      (fun u hu => Or.inr (Or.inl hu)))

end Growth

namespace Growth
namespace Deletion

variable {U : Type}

/-- **Tombstone permanence, strengthened.** Re-adding an arbitrary SET
of removed content is a no-op — `tombstone_permanence` is the
singleton instance `A' := single a`. -/
theorem tombstone_permanence_set (Φ : (U → Prop) → (U → Prop))
    (A R A' : U → Prop) (hA' : A' ⊑ R) :
    K Φ (diff (A ⊔ A') R) = K Φ (diff A R) := by
  have h : diff (A ⊔ A') R = diff A R := by
    apply pred_ext; intro u
    constructor
    · intro h
      refine ⟨?_, h.2⟩
      cases h.1 with
      | inl hA => exact hA
      | inr ha' => exact absurd (hA' u ha') h.2
    · intro h
      exact ⟨Or.inl h.1, h.2⟩
  rw [h]

/-- A log segment consisting of adds only. -/
def AddOnly : List (Op U) → Prop
  | [] => True
  | Op.add _ :: t => AddOnly t
  | Op.remove _ :: t => False

/-- A log segment consisting of removes only. -/
def RemoveOnly : List (Op U) → Prop
  | [] => True
  | Op.add _ :: t => False
  | Op.remove _ :: t => RemoveOnly t

theorem removesOf_addOnly :
    ∀ l : List (Op U), AddOnly l → removesOf l = emptyPred
  | [], _ => rfl
  | Op.add _ :: t, h => removesOf_addOnly t h
  | Op.remove _ :: t, h => False.elim h

theorem addsOf_removeOnly :
    ∀ l : List (Op U), RemoveOnly l → addsOf l = emptyPred
  | [], _ => rfl
  | Op.add _ :: t, h => False.elim h
  | Op.remove _ :: t, h => addsOf_removeOnly t h

/-- **2P CALM sandwich, growth half.** Extending a log with add-only
operations can only grow the live store — even when the appended adds
re-introduce removed content (remove-wins silently absorbs those). -/
theorem live_extend_adds (Φ : (U → Prop) → (U → Prop)) (mono : Mono Φ)
    (l ext : List (Op U)) (hext : AddOnly ext) :
    live Φ l ⊑ live Φ (l ++ ext) := by
  show K Φ (diff (addsOf l) (removesOf l)) ⊑
       K Φ (diff (addsOf (l ++ ext)) (removesOf (l ++ ext)))
  rw [addsOf_append, removesOf_append, removesOf_addOnly ext hext, un_empty]
  exact twoP_mono Φ mono (un_left (addsOf l) (addsOf ext))
    (sub_refl (removesOf l))

/-- **2P CALM sandwich, deletion half.** Extending a log with
remove-only operations can only shrink the live store. -/
theorem live_extend_removes (Φ : (U → Prop) → (U → Prop)) (mono : Mono Φ)
    (l ext : List (Op U)) (hext : RemoveOnly ext) :
    live Φ (l ++ ext) ⊑ live Φ l := by
  show K Φ (diff (addsOf (l ++ ext)) (removesOf (l ++ ext))) ⊑
       K Φ (diff (addsOf l) (removesOf l))
  rw [addsOf_append, removesOf_append, addsOf_removeOnly ext hext, un_empty]
  exact twoP_mono Φ mono (sub_refl (addsOf l))
    (un_left (removesOf l) (removesOf ext))

/-- **Replay idempotence.** Replaying an entire log is a no-op: the
live store is a function of the SET of operations, so at-least-once
delivery is free under 2P. With `live_swap`, any shuffled replay of
any prefix is likewise absorbed. -/
theorem live_replay (Φ : (U → Prop) → (U → Prop)) (l : List (Op U)) :
    live Φ (l ++ l) = live Φ l := by
  show K Φ (diff (addsOf (l ++ l)) (removesOf (l ++ l)))
     = K Φ (diff (addsOf l) (removesOf l))
  rw [addsOf_append, removesOf_append, un_idem, un_idem]

end Deletion
end Growth

#print axioms Growth.K_fixpoint
#print axioms Growth.K_least_fixpoint
#print axioms Growth.K_merge
#print axioms Growth.ingest_extends
#print axioms Growth.Deletion.tombstone_permanence_set
#print axioms Growth.Deletion.live_extend_adds
#print axioms Growth.Deletion.live_extend_removes
#print axioms Growth.Deletion.live_replay

/- ====================================================================
   THE RUNG-1 ↔ RUNG-2 LINK: finite-sample (approximate) stable_iff.

   `stable_iff` (Unified) equates exact address-invariance under a context
   map c with κ-invariance under c. An empirical invariant-kernel test
   (ICP/IRM-style: check that a feature's relationship is invariant across a
   FINITE SAMPLE of environments) estimates the left-hand side. This block
   states that estimator's exact properties on the same constructive base:

   `SampleInvariant f c sample`  — the empirical test: the committed value f
       is c-invariant on every sampled environment (the ε = 0, finite-sample
       face of invariance — what the cross-environment check actually probes).
   `sample_sound`     — SOUNDNESS (one-sided): exact invariance ⇒ the test
       passes on ANY sample; contrapositive, a sample violation refutes exact
       invariance. A flagged spurious feature is genuinely non-invariant.
   `sample_complete`  — COMPLETENESS IN THE LIMIT: if the sample exhausts the
       environments, sample-invariance IS exact invariance. More environments
       only sharpen the test; full coverage makes it exact.
   `sample_stable_iff`— the estimator's exhaustive limit coincides with
       `stable_iff`: exhaustive-sample address-invariance ⟺ κ-invariance.
       This is the precise sense in which the Rung-1 statistic's limit is the
       Rung-2 theorem.
   ==================================================================== -/
namespace Growth
namespace Approx

variable {E P A : Type}

open Unified

/-- The empirical invariance test on a finite environment sample: the
committed value `f` agrees under the context map `c` on every sampled
environment. The ε = 0, finite-sample face of address-invariance. -/
def SampleInvariant (f : E → A) (c : E → E) (sample : List E) : Prop :=
  ∀ e, e ∈ sample → f (c e) = f e

/-- **Soundness (one-sided).** Exact c-invariance implies the test passes on
ANY sample; contrapositive: a sample violation refutes exact invariance. The
empirical test never falsely flags an invariant relationship. -/
theorem sample_sound (f : E → A) (c : E → E) (sample : List E)
    (hinv : ∀ e, f (c e) = f e) : SampleInvariant f c sample :=
  fun e _ => hinv e

/-- **Completeness in the limit.** If the sample exhausts the environments,
the finite-sample test is exact invariance — the estimator's coverage limit. -/
theorem sample_complete (f : E → A) (c : E → E) (sample : List E)
    (hcov : ∀ e, e ∈ sample) (hs : SampleInvariant f c sample) :
    ∀ e, f (c e) = f e :=
  fun e => hs e (hcov e)

/-- **The Rung-1 ↔ Rung-2 link.** On an exhaustive environment sample, the
empirical invariance test on the committed address coincides EXACTLY with
`stable_iff`: sample address-invariance ⟺ κ-invariance under `c`. The
statistic's coverage limit is the determination theorem. -/
theorem sample_stable_iff (π : E → P) (H : P → A)
    (hH : ∀ p p', H p = H p' → p = p') (c : E → E)
    (sample : List E) (hcov : ∀ e, e ∈ sample) :
    SampleInvariant (addr π H) c sample ↔ (∀ e, π (c e) = π e) :=
  ⟨fun hs => (stable_iff π H hH c).mp (fun e => hs e (hcov e)),
   fun hk => fun e _ => (stable_iff π H hH c).mpr hk e⟩

end Approx
end Growth

#print axioms Growth.Approx.sample_sound
#print axioms Growth.Approx.sample_complete
#print axioms Growth.Approx.sample_stable_iff

/- ====================================================================
   MDL ADMISSIBILITY (the Δ-threshold), Rung-2.

   The growth admissibility gate with rate r = 0: a binding of `m` premises
   under code parameters (b, o) shortens the description iff the MDL surplus
   Δ = (m−1)·b − o is positive, i.e. `o < (m−1)·b`. `growth_check.py` checks
   the closed form `m₀ = ⌊o/b⌋ + 2` and the regime `m₀ = 3 ⟺ o/b ∈ [1,2)`
   on an 11×11 grid (Rung 1). Here that closed form is the LEAST admissible
   premise count, proved over ℕ on the same constructive base (only core
   `Nat` arithmetic; no mathlib). This is the "what to build" gate that the
   invariant-kernel bridge (docs/INVARIANCE_BRIDGE.md §4, §7) reuses as the
   admission criterion for content-addressed feature generators. -/
namespace Growth
namespace Mdl

/-- MDL admissibility with r = 0: `m` premises shorten the description under
code parameters (b, o) iff the surplus Δ = (m−1)·b − o is positive. -/
def Admits (b o m : Nat) : Prop := o < (m - 1) * b

/-- The closed-form threshold `m₀ = ⌊o/b⌋ + 2` is admissible (b ≥ 1). -/
theorem m0_admits (b o : Nat) (hb : 1 ≤ b) : Admits b o (o / b + 2) := by
  unfold Admits
  have hbpos : 0 < b := by omega
  have h := Nat.lt_div_mul_add (a := o) hbpos
  have hs : ∀ q : Nat, q + 2 - 1 = q + 1 := by
    intro q
    omega
  rw [hs (o / b), Nat.add_mul, Nat.one_mul]
  exact h

/-- `m₀ = ⌊o/b⌋ + 2` is the LEAST admissible premise count: any admissible
`m` is at least the threshold (b ≥ 1). With `m0_admits`, m₀ is exactly the
least element of the admissible set — the MDL design floor. -/
theorem m0_least (b o m : Nat) (hb : 1 ≤ b) (hm : Admits b o m) :
    o / b + 2 ≤ m := by
  unfold Admits at hm
  have hbpos : 0 < b := by omega
  have hdiv : o / b < m - 1 := (Nat.div_lt_iff_lt_mul hbpos).2 hm
  have step : ∀ q n : Nat, q < n - 1 → q + 2 ≤ n := by
    intro q n h
    omega
  exact step (o / b) m hdiv

/-- Regime characterization: the MDL threshold is exactly 3 iff the
overhead/benefit ratio o/b lies in [1, 2), i.e. `b ≤ o < 2b`. This is the
`m₀ = 3` cell of `growth_check.py`'s grid (the design floor m ≥ 3), proved
over ℕ on core arithmetic. -/
theorem m0_eq_three (b o : Nat) (hb : 1 ≤ b) :
    o / b + 2 = 3 ↔ (b ≤ o ∧ o < 2 * b) := by
  have hbpos : 0 < b := by omega
  constructor
  · intro h3
    have hq : o / b = 1 := by omega
    have hge : b ≤ o := (Nat.one_le_div_iff hbpos).1 (by omega)
    have hlt : o < 2 * b := (Nat.div_lt_iff_lt_mul hbpos).1 (by omega)
    exact ⟨hge, hlt⟩
  · intro hbo
    obtain ⟨hge, hlt⟩ := hbo
    have hq : o / b = 1 := Nat.div_eq_of_lt_le (by simpa using hge) (by simpa using hlt)
    omega

end Mdl
end Growth

#print axioms Growth.Mdl.m0_admits
#print axioms Growth.Mdl.m0_least
#print axioms Growth.Mdl.m0_eq_three
