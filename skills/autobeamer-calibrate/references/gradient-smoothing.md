# Difficulty-Gradient Smoothing (across the deck)

Per-slide load (see [cognitive-load-model.md](cognitive-load-model.md)) tells you which *single* frames
overload a reader. This file is about **sequence**: arranging frames so difficulty rises *gently*, with no
overload spikes and no concept used before it's introduced. This is the dimension the user named —
"怎么编排让学习难度更加平滑" (how to arrange so the learning difficulty is smoother).

## Per-frame difficulty score

Difficulty ≠ load. Difficulty adds **position-relative** terms to the intrinsic load:

```
D(f, P) = L(f, P)                          # intrinsic load (this frame)
        + g_a · abstraction_level(f, P)    # STANDING abstraction (not just new this frame)
        + g_p · prereq_debt(f, P)          # concepts USED here but never introduced earlier in the path
```

Defaults: `g_a = 0.5, g_p = 2.0` (prereq debt is heavily penalized — using a concept before defining it is
the harshest gradient violation). Compute D **only along the in-path frame sequence for P** — frames outside
P's target zone (e.g. a backup proof a reader was explicitly told to skip) are not gradient violations.
**Governing-tenet caveat:** for applied readers (P1/P4) proofs are *in-path*, so an under-scaffolded proof
DOES count toward the gradient — you may not exclude it by calling it "skippable."

## The four checks

### (a) Spike detection
For consecutive in-path frames, `Δ = D(f_{i+1}) − D(f_i)`. Flag `Δ > τ_P` (τ_P from
[profile-budgets.md](profile-budgets.md), derived from `abstraction_rate`). A spike → **insert a bridge**
between the two frames. Recommend *which* by the spike's dominant cause:
- concept-driven → a **worked example** / smaller special case.
- abstraction-driven → an **intuition bridge** in the profile's `anchor_domain`.
- back-ref-driven → a **recap** of the referenced result.

### (b) Intro→first-use distance (per symbol/concept)
Using the script's first-seen map:
- **Used-before-introduced** (`prereq_debt > 0`): **always a defect** → move the introduction earlier, or add
  an inline definition at the use site.
- **Stale introduction** (introduced on frame 4, first *used* on frame 22, no recap between): flag → add a
  one-line recall cue at the use site. Threshold: **> 6 in-path frames** without an intervening recap.

### (c) Long formal/heavy runs (generalized by load, not slide-type)
The existing rule "≤4 consecutive formal slides without example/visual" is replaced by:
**"≤ N_P consecutive frames with `D > 0.7·L_max` and no example/picture/recap,"** where `N_P` is per-profile
(P1 tolerates longer on-axis ML runs; P3/P5 ≈ 1). This catches load-heavy *prose* runs the slide-type rule
misses. On a run violation → insert an example/visual/recap to break it.

### (d) Recap / consolidation placement
Recommend a consolidation frame when **cumulative new-concept count since the last recap** exceeds the
profile's working-set size (`W_P`: P2≈7, P1≈8 on-axis, P3/P5≈3 — see profile-budgets), OR right after any
spike that was bridged, OR just before a frame whose `prereq_debt` would otherwise be high (pre-load the
prerequisites so the later frame's debt is zero).

## Script vs. model for the gradient

| Check | Script | Model |
|---|---|---|
| Δ series, spike list (once D known) | **Yes** | choose bridge *type* |
| first-seen map, used-before-introduced, intro→use distance | **Yes** | concept-level intro tracking |
| cumulative-new-since-recap, recap-candidate frames | **Yes** | confirm a frame really IS a recap |
| long-run by D-threshold | **Yes** | confirm "no example/visual on the run" |

The gradient report is **almost fully script-computable once per-frame D exists**; D's only non-mechanical
input is the per-frame concept annotation the model already produced for the load model. **One annotation
pass feeds both load and gradient.**

## Output (gradient-audit)
```
## Gradient audit — <deck> for <P>
Spikes:        frame i→i+1, Δ=…, cause=<concept|abstraction|backref> → insert <bridge type>
Used-before-introduced (DEFECTS): <symbol/concept> used @frame X, introduced @frame Y>X (or never)
Stale intros:  <concept> introduced @4, first used @22, no recap → add recall cue @22
Long heavy runs: frames a..b all D>0.7·Lmax, no example → break with example/recap
Recap suggestions: after frame k (cumulative new = W_P+) ; before frame m (pre-load prereqs)
```
