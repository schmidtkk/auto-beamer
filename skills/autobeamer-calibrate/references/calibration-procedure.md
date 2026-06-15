# Calibration Procedure

The step-by-step for both lifecycle stages. Authoring = *prescribe* budgets before drafting; Review =
*audit* a finished deck against a profile.

## Shared step 0 — resolve the profile (`set-profile`)
1. Get the target reader (from the user, the deck's stated audience, or autobeamer-create's interview).
2. Map to a roster profile P1–P6. If the described reader isn't an exact match, pick the **nearest** and
   record **axis deltas** (e.g. "quant analyst ≈ P6, add `applied` axis, lower `costly_set[proof]`"). Do not
   invent a bespoke profile.
3. Load the profile's qualitative fields from
   [reader-profiles-prescriptive.md](../../autobeamer-review/references/reader-profiles-prescriptive.md) and
   scalars from [profile-budgets.md](profile-budgets.md): `L_max`, `τ`, `W`, `N`, weights.
4. Echo the resolved profile + the governing tenet (proofs in-zone for applied readers) before proceeding.

---

## Authoring path (before/with autobeamer-create)

### `budget [profile]` — emit the authoring budget card
Produce a compact card the planner/drafter plans against, **replacing the flat ≤5-symbols rule**:
```
BUDGET CARD — <profile>
  per-slide load ceiling L_max: <default> (proof/heavy: <proof>)
  abstraction jump cap τ: <τ> per in-path frame
  working set W (recap due after): <W> new concepts
  teaching_style opener: <code|intuition|worked-example|picture>-first
  anchor_domain (analogize to): <list>
  scaffolding obligations (HARD):
    - <each obligation from the profile, incl. the proofs-in-zone tenet for P1/P4>
```
Hand this to autobeamer-create's **Structure-Plan Gate**; each planned frame must respect `L_max`, each
concept must be introduced before use (zero prereq debt), and proof frames for applied profiles must carry
the extra-scaffolding obligation.

---

## Review path (finished deck)

### `load-audit [deck] [profile]`
1. Run the script: `python tools/concept_load.py <deck> --profile <P>` → per-frame mechanical row
   (new-symbols, jump-candidates, back-refs, abstraction proxy).
2. **Model annotation pass:** for each frame, list its concepts (`concept · axis · new?`). Cross-check the
   "new symbols" against the script. This is the only non-mechanical input — label it as such.
3. Total `L(f,P)` per the [load model](cognitive-load-model.md); assign band; name the dominant term.
4. Output the ranked OVERLOAD list with per-frame prescriptions.

### `gradient-audit [deck] [profile]`
1. `python tools/concept_load.py <deck> --profile <P> --gradient` → first-seen map, used-before-introduced,
   intro→use distances, recap candidates, long-run candidates.
2. Compute D per frame (load + standing abstraction + prereq debt) along the in-path sequence.
3. Run the four checks ([gradient-smoothing.md](gradient-smoothing.md)); output spikes + bridge types,
   used-before-introduced defects, stale intros, long heavy runs, recap suggestions.

### `proofread-for [deck] [profile]` — the composite (headline action)
Fuse three lenses; each catches what the others miss:
1. **Confusion (felt walls):** run [naive-reader](../../naive-reader/SKILL.md) for this profile (+ always
   P2 + a floor reader for triangulation). Answers *"where does this reader stall?"*
2. **Overload (quantified):** `load-audit`. Answers *"which frames exceed this reader's per-slide budget?"*
3. **Scaffolding-adequacy (ordering + style):** `gradient-audit` + check every `scaffolding_obligation` and
   that bridges land in `anchor_domain` in the `teaching_style` order. Answers *"is the background present
   before it's needed, in the right domain, in the right order?"*

**Synthesis** reuses the naive-reader target-zone buckets:
- flagged by **all three** → **guaranteed fix** (top of the worklist).
- **load-only inside a gated zone** → signpost/pace, not a rewrite. *(But remember: for P1/P4, proof frames
  are NOT a gated zone — the governing tenet makes an under-scaffolded proof a real defect.)*
- **sim-only** → wording/gloss fix.

Deliver one ranked, frame-specific worklist. At review time **stop and present for adoption** before editing.

## After fixing
Re-run `proofread-for` (or at least the naive-reader sim + load-audit) to confirm in-zone walls cleared and
no frame regressed into OVERLOAD from added scaffolding (added steps raise load — absorb by **splitting**,
never by shrinking).
