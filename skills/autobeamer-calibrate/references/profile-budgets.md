# Profile Budgets — the one place numbers are tuned

These are the **tunable constants** for the cognitive-load model and gradient checks. They are coarse,
defensible defaults, not measurements — tune them here, not scattered across the skill. Per-profile
qualitative fields (primitive/costly sets, anchor domain, scaffolding obligations) live in
[reader-profiles-prescriptive.md](../../autobeamer-review/references/reader-profiles-prescriptive.md);
this file holds only the **scalars** the scoring needs.

## Per-profile scalars

| Profile | `L_max` default | `L_max` proof/heavy | `τ` (max Δdifficulty / in-path frame) | `W` (working-set: new concepts before a recap is due) | `N` (max consecutive heavy frames w/o relief) |
|---|---|---|---|---|---|
| **P1** AI engineer | 8 | 4 | 4 | 8 (on-axis ML) / 3 (off-axis) | 4 (ML) / 2 (proof) |
| **P2** undergrad | 10 | 7 | 5 | 7 | 4 |
| **P3** high-schooler | 3 | — (on-ramp only) | 2 | 3 | 1 |
| **P4** biomed | 6 | 4 | 3 | 5 | 2 |
| **P5** humanities | 3 | — (on-ramp only) | 1 | 3 | 1 |
| **P6** cross-field grad | 11 | 9 | 5 | 9 | 5 |

## Load-model weights (shared across profiles)
`w_c = 1.0` (new concept) · `w_s = 0.6` (new symbol) · `w_j = 1.5` (inferential jump — highest, an unshown
step is the #1 wall) · `w_r = 0.8` (un-recapped back-ref) · `w_a = 1.0` (abstraction peak).
Symbol collision surcharge: **+2** on top of the base symbol cost.

## Gradient weights (shared)
`g_a = 0.5` (standing abstraction) · `g_p = 2.0` (prereq debt — using a concept before introducing it).

## Concept costs by axis (the {2,4,6} scale)
- **2** = needs a one-line bridge / disambiguation (e.g. a notation collision, a term gloss).
- **4** = needs a worked example or a dedicated paragraph/sub-frame (e.g. Farkas, projection-VI, IFT for P2).
- **6** = needs its own frame, from scratch (e.g. ∇/vectors for P3; any unexplained symbol for P5; measure
  theory for P2).
The per-axis assignment for each profile is in the `costly_set` blocks of the prescriptive profile file.

## Bands (for reporting, not raw floats)
`OK` = L ≤ L_max · `TIGHT` = L_max < L ≤ 1.3·L_max · `OVERLOAD` = L > 1.3·L_max.

## Provenance note
These defaults were seeded from: the flat CLAUDE.md caps (≤5 new symbols ⇒ P2 symbol budget), the
autobeamer-review "≤4 consecutive formal slides" rule (⇒ P2 `N`=4), and the naive-reader run on numopt
(P3/P5 falling off at the first bare-symbol frame ⇒ their `L_max`=3, `τ`=1). Adjust as more decks are
calibrated; record any change here with a one-line reason.
