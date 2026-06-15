---
name: autobeamer-calibrate
description: "Calibrate a deck's background-scaffolding depth AND per-slide cognitive load / difficulty-gradient to a target reader profile — the reader-aware density model the toolkit's flat rules lack."
when_to_use: |
  Triggers on: "calibrate", "how much per slide", "cognitive load", "is this too dense for <role>",
  "smooth the difficulty", "scaffold for <background>", "proofread for an AI engineer / undergrad / ...",
  "what background to assume", "reader profile", "per-slide overload", "difficulty gradient".
  Use at AUTHORING time to set per-profile budgets for autobeamer-create, and at REVIEW time to audit an
  existing deck's load/density/scaffolding for a chosen reader.
  Do NOT trigger on: visual layout geometry / overflow (use autobeamer-layout), pure confusion simulation
  (use naive-reader), structural pedagogy scoring (use autobeamer-review).
argument-hint: "[action] [deck.tex] [profile P1..P6] — calibrate or audit scaffolding + cognitive load"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob", "Agent", "AskUserQuestion"]
---

# AutoBeamer Calibrate — Reader-Profile Scaffolding & Cognitive-Load Calibration

The toolkit's density rules are **reader-agnostic**: "≤5 new symbols," U/B/G geometry, "≤4 formal slides" —
the same regardless of who reads. But *how much a slide can carry* and *how much background to pre-lay*
depend entirely on the reader: an AI engineer absorbs many ML-adjacent concepts per slide but few
proof-theory ones; a high-schooler the opposite. This skill closes that gap. It is the **prescriptive**
counterpart to the **diagnostic** [naive-reader](../naive-reader/SKILL.md) simulation, and they share one
reader-profile library.

It adds the dimension the user named: **per-slide cognitive-load ceiling** ("一页 slide 要多少内容才不会让学生思维过载")
and **difficulty-gradient smoothing** ("怎么编排让学习难度更加平滑").

> ## ⚖ Governing teaching tenet
> **"Skips proofs" is a coping symptom, not a preference.** Applied readers (AI engineers, biomed) **need
> the math more than anyone.** Proofs are **in their target zone**; the fix for a hard proof is **more
> scaffolding and smaller steps**, never routing them around it. `\proofskipnote` is a pacing aid, not a gap
> license. An under-scaffolded proof is a **real defect**. The load fix is to **spread over more frames** —
> additive, never delete rigor. (Memory: `applied-readers-need-scaffolded-proofs`.)

## Two orthogonal axes (do not conflate)
- **Visual density** — "does the ink fit the box?" → `check_layout.py` (U/B/G/AR), autobeamer-layout.
- **Cognitive load** — "can this reader's working memory absorb it?" → THIS skill. A frame can fit visually
  yet overload cognitively, and vice-versa; the fixes differ.

## Reader-profile library (shared, one source of truth)
- **Diagnostic half** (Knows / Does-NOT-know / Target zone / Signature confusions): [naive-reader-personas.md](../autobeamer-review/references/naive-reader-personas.md).
- **Prescriptive half** (primitive/costly sets per axis, anchor_domain, teaching_style, abstraction_rate,
  L_max, scaffolding_obligations): [reader-profiles-prescriptive.md](../autobeamer-review/references/reader-profiles-prescriptive.md).
- Consistency is mechanical: `primitive ⊆ Knows`, `costly ⊇ Does-NOT-know` → exactly one P*, edited once.

## Action index

| Action | Purpose | Stage |
|--------|---------|-------|
| `set-profile [deck/plan] [profile]` | Resolve the target reader to P1–P6 (+ axis deltas); load budgets/scalars. Gate for everything else. | both |
| `budget [profile]` | Emit the authoring **budget card** for autobeamer-create (per-slide L_max, τ, W, teaching_style, anchor_domain, scaffolding obligations). | authoring |
| `load-audit [deck] [profile]` | Per-frame cognitive load `L(f,P)`, OVERLOAD band + dominant term + fix. Runs `concept_load.py`. | review |
| `gradient-audit [deck] [profile]` | Difficulty-gradient: spikes, used-before-introduced, stale intros, long heavy runs, recap placement. | review |
| `proofread-for [deck] [profile]` | **Composite** — fuse naive-reader confusion + load-audit + scaffolding-adequacy into one ranked, frame-specific worklist. | review |

## How to run
Read [calibration-procedure.md](references/calibration-procedure.md) for the step-by-step. The three
reference models:
- [cognitive-load-model.md](references/cognitive-load-model.md) — the `L` score, costs, weights, the
  script-vs-judgment boundary, a worked example.
- [gradient-smoothing.md](references/gradient-smoothing.md) — the `D` score and the four gradient checks.
- [profile-budgets.md](references/profile-budgets.md) — the tunable scalars (L_max, τ, W, N, weights).

Companion tool (reproducible mechanical numbers): `python tools/concept_load.py <deck> --profile <P>
[--gradient] [--json]`. It computes only the deterministic lower bound (new-symbol first-seen, jump
candidates, back-refs, intro→use distances) and reuses `check_layout.py`'s frame parser; the model annotates
concepts. **Numbers are "model-annotated concepts, script-totaled" — never a bare float.**

## Reporting discipline
Report load/difficulty as **bands** (OK / TIGHT / OVERLOAD) + the **dominant term** (the actionable part),
never false-precision floats. Lean on the **ranking** of frames by load, which is robust. Keep load strictly
separate from visual U/B/G.

## Integration with the lifecycle
- **autobeamer-create** — Interview Gate maps the audience answer → profile (`set-profile`); the Structure-Plan
  Gate + Wave-2→3 alignment check adopt the `budget` card as acceptance gates (replacing the flat caps).
- **autobeamer-review / naive-reader** — `proofread-for` delegates the confusion lens to `naive-reader` and
  reuses review's target-zone buckets; this skill adds the load + scaffolding-adequacy lenses.

## Cross-references
| Need | Skill |
|------|-------|
| Confused-student confusion simulation | [naive-reader](../naive-reader/SKILL.md) |
| Structural pedagogy (13 patterns), rubric scoring | [autobeamer-review](../autobeamer-review/SKILL.md) |
| Visual layout / density geometry (U/B/G) | [autobeamer-layout](../autobeamer-layout/SKILL.md) |
| Create a deck (consumes the budget card) | [autobeamer-create](../autobeamer-create/SKILL.md) |
