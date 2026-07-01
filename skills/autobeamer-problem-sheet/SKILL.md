---
name: autobeamer-problem-sheet
description: "Create an intensive-math self-study problem sheet as a XeLaTeX Beamer PDF — guided problems with weak→strong hints in the body and gap-free worked solutions in an appendix answer key."
when_to_use: |
  Triggers on: "problem sheet", "exercise set", "习题册", "习题精解", "worksheet",
  "guided problems", "练习题", "self-study problems", "make a problem set for <topic>",
  "turn this into exercises", "problem-sheet mode".
  Use when the deliverable is a sequence of PROBLEMS the reader solves (with hints +
  an answer key), not an expository deck.
  Do NOT trigger on: an expository teaching deck (use autobeamer-create passive-study),
  a live talk (autobeamer-create academic-presentation), pure layout/build/review
  tasks (autobeamer-layout / -build / -review), or editing existing slides.
argument-hint: "<topic or source> — e.g. 'Rayleigh quotient problem sheet' or a chapter PDF"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob", "Agent", "AskUserQuestion"]
---

# AutoBeamer · Problem Sheet

Build a **self-study problem sheet** for an intensive-math (or technical) topic as a
XeLaTeX Beamer **PDF**. The reader *learns by deriving*: a carefully ordered chain of
problems makes each concept feel inevitable. Every problem carries weak→strong **hints**;
every full **worked solution** lives in an `\appendix` **answer key** and must be
**gap-free** (P0 — see the [proof-rigor gate](../autobeamer-review/SKILL.md) and
[quality-rubric.md](../autobeamer-review/references/quality-rubric.md)). This skill **reuses the AutoBeamer ecosystem**
— it is a problem-sheet *mode*, not a parallel pipeline.

This SKILL.md is a thin router. The authoring law is in
`references/problem-sheet-guide.md`; the acceptance gates are in
`references/modes/problem-sheet.md`.

## Default output shape
- **Body**: problem statement → difficulty `\TLdiff{1|2|3}` → 2–3 weak→strong hints
  (`TLhints`) → `\TLtakeaway{考查：…}`. No solution in the body.
- **Answer key**: `\appendix` → one (or more) frame per problem, **gap-free** worked
  solution ending `\TLqed`. Opens with `\TLanswerkeynote` ("struggle first, then check").
- This is the **problems + answer-key appendix** format. Other formats (adjacent
  题面→解答, problems-only) are opt-in; ask the user if unsure.

## Workflow (reuse the create pipeline; do not reinvent)

1. **Intake.** Topic + source material + target reader profile + problem count +
   difficulty mix. If a format/profile is unstated, ask (AskUserQuestion).
2. **PLAN — the logical chain (write it before any TeX).** Answer the six questions in
   `references/problem-sheet-guide.md §Logical chain`: final insight → minimal prereqs →
   3–6 conceptual *Parts* → per-Part key question & what the reader derives → the 2–3
   tempting misconceptions. Map concepts → problems; ladder difficulty ⭐→⭐⭐→⭐⭐⭐.
   - Figures/source: `python tools/paper_parser.py …` + `python tools/image_index.py …`
     (source-first — adopt original figures before drawing). Reader sizing:
     `autobeamer-calibrate set-profile` → `budget`.
3. **DRAFT — body.** One frame per problem. Use `template-lib` exercise components:
   `\TLprobtitle{N}{name}{level}`, `\TLsubq{a}`, `TLhints`/`\TLhint`, `\TLconcept`,
   `\TLmisconception`, `\TLsrcnote`. Diagrams → `autobeamer-tikz`. Default theme:
   `[slatecoral]` (light) or `[rosepine]` (dark).
4. **ANSWER-KEY — `\appendix`.** Gap-free worked solution per problem, `\TLsoltitle`,
   ending `\TLqed`. Split multi-step solutions across frames **with a map/recall line**
   (avoid the proof-splitting paradox — see the guide).
5. **BUILD.** `./build.sh <deck>` (XeLaTeX, 2 passes) — owned by **autobeamer-build**.
6. **VALIDATE.** `python tools/validate_deck.py static <deck>.tex --mode problem-sheet`
   then `python tools/check_layout.py <deck>.tex build/<deck>.log --advise` —
   **autobeamer-validate** / **autobeamer-layout**.
7. **REVIEW (gates).** `autobeamer-review` rubric + **naive-reader P2** as the gap-free
   answer-key arbiter (P0) + `autobeamer-calibrate gradient-audit` for monotone difficulty.

## Environment prerequisites (check first)
| Need | Check | Fix |
|------|-------|-----|
| XeLaTeX + Metropolis + xeCJK | `./build.sh template-lib-demo` builds | run **autobeamer-doctor** / **autobeamer-build** |
| Exercise components | `template-lib/components/comp-exercise.sty` present | (ships with template-lib) |
| Figure tooling (if adopting source figures) | `python tools/doctor.py check` | **autobeamer-doctor** |

## Make a new sheet (套模板 — do NOT rebuild from scratch)
Copy the working preview `design/theme-preview.tex` (title → `\TLconcept` →
`\TLprobtitle`+`TLhints` → `\appendix` `\TLsoltitle`+`\TLqed`) and adapt content.
The numopt / OT decks (`numopt-ch12-constrained-zh.tex`, `ot-qualitative-zh.tex`) are
real worked examples of the format.

## Reference index
| File | What |
|------|------|
| `references/problem-sheet-guide.md` | The authoring law: logical chain, Part/Problem/sub-part ladder, hint craft, concept-introduction protocol, gap-free answer-key standard, anti-patterns |
| `references/modes/problem-sheet.md` | Learning philosophy · authoring rules · acceptance gates (the mode contract) |
| `template-lib/components/comp-exercise.sty` | The exercise macros (`\TLdiff`, `TLhints`, `\TLconcept`, `\TLqed`, …) |
| sibling: **autobeamer-create** | the create pipeline this mode plugs into |
| sibling: **autobeamer-review** / **naive-reader** / **autobeamer-calibrate** | the gates |
