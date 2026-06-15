# Reader Profiles — Prescriptive Half

This file is the **prescriptive half** of the shared reader-profile library. The **diagnostic half**
(what each reader Knows / Does-NOT-know / Reads-proofs-how / Target zone / Signature confusions) lives in
the sibling file [`naive-reader-personas.md`](naive-reader-personas.md) and is the source of truth for "what
this reader knows." **Do not restate the diagnostic fields here.** Each profile below is the SAME reader as
the persona of the same number (P1…P6) — these are the extra fields an *author* needs to set scaffolding
depth and per-slide cognitive-load budgets.

Consumers: [autobeamer-calibrate](../../autobeamer-calibrate/SKILL.md) (authoring budgets + load/gradient
audit + `proofread-for`). The diagnostic half is consumed by [naive-reader](../../naive-reader/SKILL.md).

## Consistency rules (so there is exactly one P*, edited in one place)
- `primitive_set` ⊆ the persona's diagnostic **Knows** (a primitive = something they know → cost 0).
- `costly_set` ⊇ the persona's diagnostic **Does NOT know** (must be scaffolded → cost > 0).
- Adding a concept to **Knows** in the diagnostic file automatically makes it primitive here; the two halves
  cannot contradict.

## Fields (all per knowledge **axis**)
A *profile* declares a small set of **axes** (e.g. `ml`, `analysis`, `proof`, `algebra`, `applied`,
`verbal`, `picture`). The same reader tolerates a high rate on one axis and near-zero on another — this is
why budgets are per-axis, not a single scalar.

| Field | Meaning |
|---|---|
| `axes` | The knowledge axes this reader is scored on. |
| `primitive_set` | Per axis: concept *families* manipulated fluently (concept_cost = 0). |
| `costly_set` | Per axis: families needing scaffolding, each tagged cost ∈ {2 = one-line bridge, 4 = worked example/frame, 6 = its own frame}. |
| `anchor_domain` | Ordered list of what to **analogize to**. Every bridge for a costly concept must land here. |
| `teaching_style` | Opening move of each concept's frame group: `code-first` / `intuition-first` / `worked-example-first` / `picture-first` / `formal-OK-if-gap-free`. |
| `abstraction_rate` | Per axis: max comfortable abstraction-level *jump* per consecutive in-path frame (drives the gradient τ). |
| `load_budget L_max` | Per-slide intrinsic-load ceiling (the number §cognitive-load-model scores against), optionally per axis / per frame-type. |
| `scaffolding_obligations` | Hard "before you may use X, do Y" rules for this reader. |

> ## ⚖ Governing teaching tenet (overrides naive "skip" framing)
> The diagnostic field `Reads-proofs-how: skims/skips` describes a **coping symptom of cognitive difficulty,
> NOT a preference.** Applied readers (P1, P4) **need the math more than anyone.** Therefore in the
> prescriptive half: **proofs are IN target zone**; `costly_set[proof/analysis]` means "needs MORE
> scaffolding," never "may be skipped." An under-scaffolded proof is a **real defect** for them.
> `\proofskipnote` / reading-path are first-pass pacing aids, not gap licenses. The load fix for a heavy
> proof frame is to **spread it over more frames with smaller steps** — additive, never delete rigor.
> (Memory: `applied-readers-need-scaffolded-proofs`.)

---

## P1 — AI/ML engineer (码农)

```yaml
axes: [ml, algebra, analysis, proof]
primitive_set:
  ml:      [tensor/matmul, gradient & backprop, ∇ as descent direction, sampling & distributions,
            big-O cost, loss landscape, argmin/argmax, "the optimizer does X"]
  algebra: [vectors as arrays, matrix multiply]
costly_set:
  analysis: { ε–δ / subsequence-compactness: 6, lsc / closed / compact: 6, little-o o(·): 4, limit-asserted-"可验证": 4 }
  proof:    { formal-proof-technique: 4, named-lemma-invoked-by-name: 4,
              variational-inequality / normal-cone / polar-cone / subdifferential: 4,
              implicit-function-theorem / null-space-basis: 4 }
  ml:       { notation-collision (λ mult vs learning-rate; T tangent-cone vs ᵀ transpose; N normal-cone vs batch/dim; 𝒜 active-set vs matrix A): 2 }
anchor_domain: [python/pseudocode, optimizer/training-loop behavior, loss-landscape picture, autograd]
teaching_style: code-first | intuition-first   # then the formal step — NOT instead of it
abstraction_rate: { ml: 2, algebra: 2, analysis: 1, proof: 1 }
load_budget L_max: { default: 8, proof/analysis-heavy frame: 4 }
scaffolding_obligations:
  - "PROOFS ARE IN-ZONE (governing tenet). Every proof/reasoning chain gap-free with EXTRA intermediate
     steps vs a math major; every 'thus/hence/可验证' shows the micro-step."
  - "Every theorem invoked by name gets a one-line 'what it gives you + why its hypothesis holds here' in
     anchor_domain terms, ON the same frame (IFT, Farkas, projection-VI, Rademacher…)."
  - "Every ε/δ or subsequence argument gets an intuition-first sentence (code/optimizer analogy) before the
     formalism; if it still overflows the budget, SPLIT into more frames — do not gate it away."
  - "Disambiguate any symbol that collides with ML usage on first use (λ, T/ᵀ, N/n, 𝒜/A)."
  - "Each formula sits beside its plain-language / code meaning; never a bare displayed equation."
```

## P2 — STEM undergraduate, sophomore (本科二年级)  ·  the gap-free-proof arbiter

```yaml
axes: [analysis, algebra, proof, applied]
primitive_set:
  analysis: [single & multivariable calculus, Taylor expansion, gradients, basic limits]
  algebra:  [rank, null space, eigenvalues, span, linear independence]
costly_set:
  proof:    { Farkas / theorem-of-the-alternative: 4, projection-variational-inequality: 4,
              implicit-function-theorem (name only): 4, convex/functional analysis vocab: 4 }
  analysis: { measure theory: 6, subsequence-compactness (shaky): 4 }
anchor_domain: [a worked numeric example, a 2D picture, a smaller special case (1D/discrete first)]
teaching_style: formal-OK-if-gap-free   # will follow a clean proof slowly; stops at the first skipped step
abstraction_rate: { analysis: 2, algebra: 2, proof: 1 }
load_budget L_max: { default: 10, proof-heavy frame: 7 }
scaffolding_obligations:
  - "Every step on a slide must be justified; a deep idea is fine, a SKIPPED step is a defect."
  - "Name + state (one line) any tool above the ceiling before using it (Farkas, projection-VI, IFT)."
  - "Introduce 1D/discrete special case before the general/continuous statement."
```

## P3 — Strong high-school student (AP / 竞赛)  ·  on-ramp floor test

```yaml
axes: [algebra, picture, symbol]
primitive_set:
  algebra: [algebra, functions, slope-as-derivative idea, loose Σ]
  picture: [reading a labeled graph/diagram]
costly_set:
  symbol:  { ∇ / gradient: 6, vectors & matrices: 6, set-builder + index sets: 6, any unexplained $…$ token: 4 }
  algebra: { multivariable calculus: 6, "feasible set" / formal optimization: 4 }
anchor_domain: [pictures, physical motion, money/everyday objects, one hand-computable number]
teaching_style: picture-first   # never formal-first; never code
abstraction_rate: { algebra: 1, picture: 1, symbol: 0 }   # 0 = no NEW unexplained symbol survives
load_budget L_max: { default: 3, on-ramp frame with a bare symbol: 0 (=fail) }
scaffolding_obligations:
  - "Inside the on-ramp (this reader's ENTIRE target zone) no $…$ token may appear unless its meaning was
     stated in words on an earlier or the same frame."
  - "Every on-ramp claim rides on a picture or a hand-computable number."
  - "Past the on-ramp, losing formal content is EXPECTED — but only if the reading-path warned them."
```

## P4 — Biomedical / life-science researcher

```yaml
axes: [applied, stats, ml, proof]
primitive_set:
  stats:   [regression, distributions, p-values, hypothesis tests]
  applied: [concrete numbers, plots, "what it does to my data", reads OT/Wasserstein/KKT in papers]
costly_set:
  proof:   { any-formal-proof: 6, Lagrangian-duality-as-math: 4, abstract analysis: 6 }
  ml:      { optimization theory: 4, "multiplier" beyond "a number the solver returns": 4 }
anchor_domain: [lab protocols, a dataset/measurement, "which constraint in MY study is binding", plots]
teaching_style: worked-example-first   # number first, meaning second, formalism last
abstraction_rate: { applied: 2, stats: 2, ml: 1, proof: 1 }
load_budget L_max: { default: 6, proof-heavy frame: 4 }
scaffolding_obligations:
  - "No formal statement without a CONCRETE numeric instance within 1 frame."
  - "Every abstract payoff (shadow price, dual, multiplier) shown with an actual number tied to a use case."
  - "PROOFS ARE IN-ZONE per the governing tenet — scaffold via worked numbers, do not route around."
  - "Each theorem answers 'what does this let me DO' explicitly."
```

## P5 — Humanities / non-quantitative ("literal") reader  ·  jargon-free litmus

```yaml
axes: [verbal, picture, symbol]
primitive_set:
  verbal:  [analogy, plain-language logic, narrative cause→effect]
  picture: [reading a labeled diagram, before/after pictures]
costly_set:
  symbol:  { any-unexplained-symbol: 6, sentence-mostly-notation: 6, Σ / ∇ / μ / subscript-index: 6 }
  picture: { unlabeled diagram: 4 }
anchor_domain: [everyday objects, money/prices, sand-pile/bakery, physical motion]
teaching_style: picture-first   # never formal, never code
abstraction_rate: { verbal: 1, picture: 1, symbol: 0 }
load_budget L_max: { default: 3, any frame with a bare symbol in a "plain" box: 0 (=fail) }
scaffolding_obligations:
  - "On-ramp prose + pictures + plain-language takeaways are the ENTIRE target zone; no $…$ token there
     unless its meaning is stated in words on the same frame."
  - "A 'plain-language takeaway' (要点) containing μ, ∇, x*, Ω, Σ, or any subscript is a defect."
  - "Every claim rides on an analogy in anchor_domain; no claim stated only formally."
```

## P6 — Cross-field graduate (physics / econ / CS-theory) *(optional; convention/collision auditor)*

```yaml
axes: [proof, analysis, algebra, conventions]
primitive_set:
  proof:    [proof technique in their own field]
  analysis: [multivariable calculus, real analysis basics]
  algebra:  [linear algebra, some optimization]
costly_set:
  conventions: { this-field's-naming: 2, "standard"/"as usual" with no pointer: 2,
                 symbol reused with two meanings: 4, convention assumed from a sibling course: 2 }
anchor_domain: [the equivalent object in their home field, an explicit statement of the local convention]
teaching_style: formal-OK-if-gap-free
abstraction_rate: { proof: 2, analysis: 2, conventions: 1 }
load_budget L_max: { default: 11 }
scaffolding_obligations:
  - "State every local convention explicitly; no 'as usual' / 'the standard' without a pointer."
  - "Flag any symbol reused with two meanings; one symbol = one meaning per deck."
```

---

## Mapping a described reader to a profile
If the user names a background not in the roster, map to the **nearest profile** and record **axis deltas**
(e.g. "quant-finance analyst ≈ P6 with `costly_set[proof]` lowered, `applied` axis added"). Do not mint a
bespoke per-deck profile; the roster is fixed at P1–P6 + nearest-profile-plus-delta.
