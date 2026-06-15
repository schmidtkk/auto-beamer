# Cognitive-Load Model (per slide, profile-relative)

## What this measures — and what it does NOT

`tools/check_layout.py` answers **"does the ink fit the box?"** (visual density: U/B/G/AR). This model
answers **"can THIS reader's working memory absorb this frame?"** They are **orthogonal**: a frame can be
visually sparse (U=0.55) yet cognitively overloaded (5 new proof-theory concepts in 3 lines), and vice-versa.

> **Never fold U/B/G into load `L`.** Keep the axes separate so a frame can be "fits fine, overloaded" and
> the fix (split for cognition) differs from the visual fix (rescale image).

## The intrinsic-load score

For frame *f* and target profile *P* (profiles + per-axis costs: see
[reader-profiles-prescriptive.md](../../autobeamer-review/references/reader-profiles-prescriptive.md)):

```
L(f, P) =  w_c · Σ concept_cost(c, P)        # new concepts on the frame
         + w_s · Σ symbol_cost(s, P)         # new symbols
         + w_j · (#inferential jumps)        # un-shown "thus / hence / clearly / 可验证" steps
         + w_r · (#back-references not recapped on-frame)
         + w_a · max_abstraction_level(f, P) # peak abstraction on the frame
```

**Default weights** (coarse on purpose — see Risks): `w_c=1.0, w_s=0.6, w_j=1.5, w_r=0.8, w_a=1.0`. Jumps
carry the highest weight because an *unshown step* is the #1 wall personas report.

### Per-occurrence costs (profile-keyed)
- `concept_cost(c,P)` = **0** if c's family ∈ `P.primitive_set`; else the `costly_set` weight (2/4/6) for c's
  axis. A concept already introduced earlier in the deck costs 0 (no longer *new*) **unless** used in a new way.
- `symbol_cost(s,P)` = 0 for a primitive-domain symbol (e.g. `∇` for P1); 1 for an ordinary new symbol;
  **+2 surcharge** if it **collides** with a primitive meaning (λ-mult-vs-learning-rate, T-tangent-vs-ᵀ).
  Collisions are disproportionately costly — they match the personas' "signature confusions."
- `abstraction_level` is an ordinal: **0** concrete number → **1** named object → **2** general
  statement/family → **3** statement-about-statements / functional / measure-theoretic. Score the **peak**.

### The OVERLOAD verdict
A frame with `L(f,P) > P.L_max` (from [profile-budgets.md](profile-budgets.md)) is **OVERLOAD for P**.
Always **name the dominant term** — that is the actionable part:
- dominated by `w_c` (costly concepts) → **split** the frame / introduce concepts across frames.
- dominated by `w_j` (jumps) → **show the skipped steps** (this is the proof-scaffolding fix, governing tenet).
- dominated by `w_s` collisions → **add a one-line disambiguation** at first use.
- dominated by `w_a` → **add an intuition/anchor bridge** before the abstract statement.

### How this generalizes the flat "≤5 new symbols" rule (CLAUDE.md)
1. Symbols are **weighted, not counted** (5 primitive symbols for P1 ≈ 0; 2 colliding ones = 6).
2. Symbols are **one term of five** — a frame may carry more symbols if it has zero jumps and no new concepts.
3. The ceiling is **per-profile** (`L ≤ P.L_max`). Set every cost to 1 and `L_max=5` → you recover the old
   symbol-only rule as the P2 special case. Backward-compatible, strictly more expressive.

## Countable by script vs. needs model judgment (the honesty boundary)

`tools/concept_load.py` computes the **mechanical lower bound only**; the model supplies the rest. Never
present a load number as "magically computed" — it is **"model-annotated concepts, script-totaled."**

| Feature | Script (deterministic) | Model judgment |
|---|---|---|
| New symbols (first `$…$` occurrence of a token, tracked across frames) | **Yes** | classify axis / "new *use* of old symbol" |
| Symbol↔meaning collisions | flag reused token | confirm it's a *semantic* collision |
| New vs. already-introduced **concept** | **No** (not lexable) | **Yes** — tag each frame's concepts + axis |
| Inferential jumps (`thus/hence/clearly/obvious/可验证/易证/it can be shown`) | **flag candidates** (trigger list) | **Yes** — decide if the step is actually skipped |
| Back-references (`\ref`,`\hyperlink`,`recall`,"as shown") | **Yes** | judge whether recapped on-frame |
| Abstraction peak | weak proxy (math-env depth) | **Yes** — assign 0–3 |

**Procedure:** the script emits a per-frame row (mechanical lower bound); the model annotates a tiny
concept table per frame (`frame · concept · axis · new?`); then totalling is arithmetic and reproducible.

## Worked example (target = P1, AI engineer)

> **Frame:** "KKT for the entropic OT dual" — states the Lagrangian, asserts "by strong duality the gap is
> zero," introduces λ (multiplier), μ, ν (marginals), the normal-cone optimality condition, concludes
> "hence the optimal plan is the Gibbs kernel — one verifies the marginals match."

| Term | Items | Cost | Subtotal |
|---|---|---|---|
| concepts | strong-duality (proof,4), normal-cone-optimality (proof,4), entropic-dual=Gibbs (ml,2) | 10 | 10·1.0 = **10** |
| symbols | λ (collides → 1+2=3), μ, ν (distributions, primitive → 0) | 3 | 3·0.6 = **1.8** |
| jumps | "by strong duality the gap is zero" (unshown), "one verifies the marginals match" (unshown) | 2 | 2·1.5 = **3.0** |
| back-refs | Lagrangian from earlier, not recapped | 1 | 1·0.8 = **0.8** |
| abstraction | normal-cone optimality = level 3 | 3 | 3·1.0 = **3.0** |
| **L(f,P1)** | | | **≈ 18.6** |

P1's `L_max` on a proof-heavy frame = **4** → **OVERLOAD ×4.6**, dominated by `w_c` + `w_j`. Prescription:
split into 3 frames; **scaffold** strong-duality + normal-cone (governing tenet — in-zone for P1, so show the
steps, don't gate); add "λ here is the OT multiplier, not a learning rate"; replace "one verifies" with the
two-line marginal check.
For **P2** the same frame scores ≈11 (proof costs lower, no λ-collision) — still over, but the fix is "show
the two skipped steps," not "remove concepts." **Same frame, different prescription per profile** — the whole
value proposition.

## Reporting discipline (avoid false precision)
- Report `L` as a **band** — `OK` (≤ L_max), `TIGHT` (L_max … 1.3·L_max), `OVERLOAD` (> 1.3·L_max) — plus the
  dominant term. Never a bare float as if it were a measurement.
- The **ranking** of frames by load is robust even when the absolute number isn't — lean on ranking.
- Always tag "(model-annotated concepts, script-totaled)" and link the per-frame concept table.
