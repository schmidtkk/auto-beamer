---
name: naive-reader
description: "Confused-student adversarial simulation: ceiling-bounded reader personas read a deck in character (anti-cheat) and report exactly where a beginner gets lost — confusion the expert model can't feel on its own."
when_to_use: |
  Triggers on: "naive reader", "confused student", "stupid student simulation",
  "can a beginner follow this", "where will students get lost", "read this as a <role>",
  "accessibility check from the reader's chair", "test the on-ramp".
  Use whenever a deck claims cross-disciplinary accessibility, when readers report "I can't
  follow the proofs / it jumps", or any time the reviewer is too expert to feel a beginner's
  confusion (which is always, for a strong model).
  Do NOT trigger on: structural pedagogy scoring (use autobeamer-review pedagogy), layout/density
  geometry (use autobeamer-layout), prescriptive scaffolding+load calibration (use autobeamer-calibrate).
argument-hint: "[deck.tex] [personas: P1..P6 or roles] — run the confused-student simulation"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob", "Agent", "AskUserQuestion"]
---

# Naive Reader — Confused-Student Adversarial Simulation

A strong model cannot feel where a beginner hits a wall: it silently fills every gap from its own
knowledge, so it certifies as "clear" proofs a beginner cannot follow. This command manufactures the
missing information by simulating readers with a **hard knowledge ceiling** who are **forbidden from
using anything above it**.

> **The anti-cheat rule (the whole trick).** If a persona catches itself following a step *only* because
> it secretly knows more than its ceiling allows, it STOPS and flags that step as a wall — because its
> real-world counterpart does not have that knowledge.

This is the **diagnostic** reviewer. For the **prescriptive** counterpart (calibrate a deck's scaffolding
depth + per-slide cognitive load to a target profile), use [autobeamer-calibrate](../autobeamer-calibrate/SKILL.md).
Both share one reader-profile library.

## Canonical reference (read before running)

The persona roster (P1 AI engineer · P2 undergraduate · P3 high-schooler · P4 biomed · P5 humanities ·
P6 cross-field grad), the anti-cheat rule, the **target-zone** logic, and the per-persona + synthesis
report schemas live in:

**[../autobeamer-review/references/naive-reader-personas.md](../autobeamer-review/references/naive-reader-personas.md)**

Read that file first. This SKILL.md is only the run procedure.

## Procedure

1. **Identify the deck's claimed audience** and pick ≥3 personas (always include **P2**, the gap-free-proof
   arbiter, and one **floor reader** P3/P5 to test the zero-prereq on-ramp). If the user names a single
   background (e.g. "AI engineer"), still add P2 + a floor reader unless told otherwise — one persona alone
   can't tell you whether a wall is reader-specific or universal.
2. **Assign each persona a target zone** — the frames the deck *promises* this reader will understand.
   Confusion *inside* the zone is a defect; outside-and-warned is expected. **Governing tenet:** for applied
   readers (P1/P4) proofs are NOT auto-"skippable" — an under-scaffolded proof is a real defect, because
   they need the math, just scaffolded (see [autobeamer-calibrate](../autobeamer-calibrate/SKILL.md) and
   the memory `applied-readers-need-scaffolded-proofs`).
3. **Prepare the deck.** Flatten if it `\input`s sections. Extract the **macro legend** from the preamble
   (e.g. `\grad`→∇, `\T`→transpose, `\xs`→x*) and hand it to every persona so they read math as *rendered*,
   not as LaTeX noise. High-fidelity option: 2-pass build → read PDF page images.
4. **Spawn one `general-purpose` subagent per persona, in parallel** (single message, multiple `Agent`
   calls). Give each: its persona block verbatim, the anti-cheat rule, its target zone, the deck + macro
   legend, and the per-persona report schema. Personas never see each other's output.
5. **Synthesize** into the confusion heatmap + ranked defects (schema in the reference), sorting findings
   into real defects (fix) / gating defects (cheap signpost) / expected confusion (leave). The ranked
   worklist is the deliverable.

## Health check (did the simulation work?)

- If every persona "understood everything," the run is **broken** — a subagent cheated. A healthy run has
  floor readers stopping early; the signal is *in-target-zone* failures, not raw failure count.
- Findings must be **frame-specific and token-specific** ("Frame 18: `Z` spanning the null space was never
  defined"), never vague ("proofs are hard"). Re-prompt subagents that return mush.
- A legitimately *hard* step is not a defect; an *unjustified/skipped* step is. P2 arbitrates the difference.

## Cross-references

| Need | Skill |
|------|-------|
| Structural pedagogy (13 patterns), rubric scoring | [autobeamer-review](../autobeamer-review/SKILL.md) |
| Prescriptive scaffolding + cognitive-load calibration | [autobeamer-calibrate](../autobeamer-calibrate/SKILL.md) |
| Visual layout / density geometry (U/B/G) | [autobeamer-layout](../autobeamer-layout/SKILL.md) |
