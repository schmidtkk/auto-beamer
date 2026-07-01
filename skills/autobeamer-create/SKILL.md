---
name: autobeamer-create
description: "Create a new XeLaTeX Beamer deck from scratch in one of three modes — passive-study, active-socratic, or academic-presentation — from papers, notes, books, or ideas."
when_to_use: |
  Use when creating a new deck from source material or an idea.
  Do NOT trigger on editing existing slides (use autobeamer-layout), build errors
  (use autobeamer-build), or review-only tasks (use autobeamer-review).
argument-hint: "create [topic-or-file] -- starts the deck creation pipeline"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob", "Agent", "AskUserQuestion", "TaskCreate", "TaskUpdate", "TaskList", "TaskGet"]
---

# AutoBeamer Create

Create XeLaTeX Beamer decks through a mode-aware pipeline. Keep this file as the router; load only the references needed for the user's deck.

## Execution Model — leader + 3 waves

You (the create skill) act as the **team leader/orchestrator**, not the worker.
Split the pipeline into three waves and assign each to one specialized subagent,
reviewing the handoff between waves.

| Wave | Phases | Subagent | Produces |
|------|--------|----------|----------|
| 1 — Plan | 0–2 | [`autobeamer-planner`](../../agents/autobeamer-planner.md) | structure plan + validated `image_index.json` |
| 2 — Draft+Figures | 3–4 (merged) | [`autobeamer-drafter`](../../agents/autobeamer-drafter.md) | deck `.tex` + resolved image-request log |
| 3 — Polish | 5 | [`autobeamer-finisher`](../../agents/autobeamer-finisher.md) | final PDF + validation/review report |

**Between Wave 2 and Wave 3 the leader runs the anti-drift [alignment check](references/validation/alignment-check.md)** against the Wave-1 plan and the original demands; on drift, bounce back to the Drafter before polishing.

**When to use waves:** for substantial or source-document-driven decks, dispatch the three subagents (by `subagent_type` name) and pass the handoff artifacts (plan, `image_index.json` path, deck path, reports) — each subagent starts cold. For small/simple decks, run the phases inline yourself; the same gates still apply.

**Before any wave**, run the [environment doctor](references/validation/env-doctor.md): it writes `.autobeamer/env_state.json`, which determines whether figure extraction is possible and the figure-confidence ceiling for the whole run.

## Required First Steps

0. **Run the environment doctor first** — the skill needs a runtime it does not control. Probe deps and record this model's visual capability, then branch on the result during planning (see [references/validation/env-doctor.md](references/validation/env-doctor.md)):
   ```bash
   python tools/doctor.py check                                  # exit!=0 ⇒ STOP, report blockers
   python tools/doctor.py set-capability --model <your-model-id>
   ```
   If `check` reports blockers (missing `xelatex`/poppler), stop and tell the user what to install. Otherwise read `.autobeamer/env_state.json` `profile` and let it gate Phase 0 figure extraction and the image-index visual-check method.
1. Read skill memory before planning, resolved at the plugin/repo root: `memories/MEMORY_INDEX.md`, then `memories/repo/user-preferences.md`. If `memories/` is absent (e.g., a fresh public checkout that ships without it), proceed without it and rely on the in-skill defaults — do not fabricate preferences.
2. If source material is provided, inspect it before asking questions.
3. Set exactly one mode: `passive-study`, `active-socratic`, or `academic-presentation`.
4. Load the selected mode reference and [references/validation/mode-gates.md](references/validation/mode-gates.md).
5. If a PDF or source document is provided, load [references/images/source-document-first.md](references/images/source-document-first.md) and extract figures before web search.

## Mode Routing

| Mode | Use when | Load |
|------|----------|------|
| `passive-study` | The learner is entering an unfamiliar field and needs comprehensive, self-contained teaching with background support | [references/modes/passive-study.md](references/modes/passive-study.md) |
| `active-socratic` | The learner wants guided discovery through questions, thought experiments, derivations, and attempt gates | [references/modes/active-socratic.md](references/modes/active-socratic.md) |
| `academic-presentation` | The deck is for a live talk, seminar, defense, journal club, or academic sharing | [references/modes/academic-presentation.md](references/modes/academic-presentation.md) |

Compatibility aliases: "Mentor"/"self-study"/textbook/chapter → `passive-study` (unless Socratic asked); "Socratic"/"derive with me"/"mentor me" → `active-socratic`; "talk"/"seminar"/"defense"/"academic sharing" → `academic-presentation`.

Every structure plan must state the selected mode, loaded references, and mode-specific acceptance gates.

## Chinese (CJK) Deck Creation

When the user requests a Chinese deck ("中文", "Chinese version"):

- **Fonts auto-detect** (font-config Priority 1.5): Source Han Serif SC if `.fonts/SourceHanSerifSC-Medium.otf` is present, else system Noto Sans CJK; KpMath pairs fine, no math override needed. Font details: [autobeamer-build](../autobeamer-build/SKILL.md) (CJK Fonts).
- **Localize** TikZ node/axis/caption text (keep math mode unchanged); override `\TLtakeaway`'s "Key Takeaway." → `要点。`.
- **Validator keywords.** `validate_deck.py` Socratic gates match English keywords ("question/attempt/hint/reflection") — add bilingual glosses to the "how to use this deck" frame so the check passes with Chinese content.
- **Language gate.** Write Chinese throughout — `lang_lint.py` fails on any English-prose leakage (terms & `$...$` exempt) plus AI-flavor fillers and proof-hedges. See [language-quality-gate.md](../autobeamer-review/references/language-quality-gate.md).

## Pipeline

```
                          ┌─ WAVE 1: PLAN ──────────────────────────────────┐
Phase 0: MATERIAL ANALYSIS  -> read sources, extract figures -> image index
Phase 1: NEEDS INTERVIEW    -> ask only missing content/audience/mode questions
Phase 2: STRUCTURE PLAN     -> detailed outline + planned figures; approval gate
                          └─────────────────────────────────────────────────┘
                          ┌─ WAVE 2: DRAFT + FIGURES (merged) ──────────────┐
Phase 3+4: DRAFT+FIGURES    -> write batches; each figure-needing slide emits an
                               image request and resolves it from the index
                          └─────────────────────────────────────────────────┘
            >>> leader runs the ALIGNMENT CHECK (anti-drift) here <<<
                          ┌─ WAVE 3: POLISH ────────────────────────────────┐
Phase 5: QUALITY LOOP       -> compile, validate, visual-check, review, fix
                          └─────────────────────────────────────────────────┘
```

Phases 3 and 4 are **one wave**: decide a slide's figure while you draft it, not in a separate pass. Do not skip phases. For detailed guidance, load [references/workflows/full-create-guide.md](references/workflows/full-create-guide.md).

## Material Analysis

If papers/materials are provided:
- Read the source thoroughly before interviewing the user.
- Extract contribution, method, theorem/result structure, notation, prerequisites, and slide-worthy figures.
- For PDFs, run:
  ```bash
  python tools/paper_parser.py parse paper.pdf --output slides_assets/paper.json
  python tools/paper_parser.py extract-images paper.pdf --output slides_assets/source_figures/
  ```
- Build the **image index** as the figure inventory — do not keep it ad-hoc. Seed it from the parser, attach captions/context, then visually check each image to set its `key_idea` and `confidence` (confidence is capped when no visual check is possible). See [references/images/image-index.md](references/images/image-index.md):
  ```bash
  python tools/image_index.py init --path slides_assets/image_index.json
  python tools/image_index.py import-parser slides_assets/paper.json --path slides_assets/image_index.json
  python tools/image_index.py validate --path slides_assets/image_index.json
  ```

## Interview Gate

Ask only what cannot be inferred safely:
- Duration or target effort budget.
- Audience/learner level and prior field exposure.
- Mode confirmation when ambiguous.
- Paper-specific scope decisions derived from the source.
- Whether speaker notes are needed for `academic-presentation`.

Avoid generic questionnaires. Use the material to ask concrete choices.

**Map the audience to a reader profile.** Once the audience answer is in, resolve it to a profile via
[autobeamer-calibrate](../autobeamer-calibrate/SKILL.md) `set-profile` (P1 AI engineer · P2 undergrad ·
P3 high-school · P4 biomed · P5 humanities · P6 cross-field grad, or nearest + axis deltas). This drives a
**per-slide cognitive-load budget** instead of the flat "≤5 new symbols" cap, and the per-profile
scaffolding obligations. **Governing tenet:** for applied readers (P1/P4), proofs are *in-zone* and must be
*scaffolded* (more steps), never gated away.

## Structure Plan Gate

Before drafting, present a plan containing:
- Selected mode and loaded references.
- Section list with slide counts.
- Per-section learning objective or narrative purpose.
- Planned figures, tables, TikZ diagrams, or source images.
- New notation and prerequisite reminders.
- **Reader-profile budget card** from [autobeamer-calibrate](../autobeamer-calibrate/SKILL.md) `budget`:
  per-slide `L_max`, abstraction-jump cap `τ`, working-set `W` (recap cadence), `teaching_style` opener,
  `anchor_domain`, and the profile's scaffolding obligations. The planner plans each frame against `L_max`
  and ensures every concept is introduced before use (zero prereq debt).
- Validation gates from [references/validation/mode-gates.md](references/validation/mode-gates.md).

Ask for approval before drafting.

The Wave-2→3 **alignment check** then adds one line: every frame respects the target-profile budget
(run `autobeamer-calibrate load-audit`); added scaffolding that raises load is absorbed by **splitting**,
never shrinking.

## Drafting Rules

Shared hard rules:
- No overlays: never use `\pause`, `\onslide`, `\only`, or `\uncover`.
- Maximum 3 colored boxes per slide.
- Motivation before formalism.
- Worked example within 2 slides of every definition.
- Every slide needs at least one substantive element.
- New decks use template-lib commands such as `\TLinfoblock`, `\TLalertblock`, `\TLresultblock`, `\TLwarnblock`, and `\TLtakeaway`.

Mode-specific writing:
- `passive-study`: complete sentences, background context, examples, exercises, glossary, bibliographical notes.
- `active-socratic`: one central question/task per learning frame, staged hints, learner attempts before answers.
- `academic-presentation`: telegraphic prompts, time-aware pacing, references before Thank You, backup slides after `\appendix`.

## Figures And Layout (merged into drafting — Wave 2)

Figures are resolved **while drafting**, not in a separate pass. When a slide
needs a figure, log an image request and adopt from the index by key idea:
```bash
python tools/image_index.py request-add --slide "<title>" --need "<key idea>"
python tools/image_index.py query --key-idea "<key idea>"
python tools/image_index.py request-resolve --request <id> --image <imgid> --status adopted
```

Source-document-first precedence (see [references/images/image-index.md](references/images/image-index.md)):
1. Indexed source figure (matched via `query`).
2. Rendered/cropped source page region.
3. Local TikZ, pgfplots, or redrawn figure (prefer this over a low-confidence match).
4. External image only as a local, attributed fallback (record `provenance`).

For image-heavy slides, run `python tools/layout_optimizer.py suggest --img W:H --cards N`. Use [autobeamer-layout](../autobeamer-layout/SKILL.md) for layout and [autobeamer-tikz](../autobeamer-tikz/SKILL.md) for diagrams. Leave no image request `open`.

## Quality Gate

After each draft batch:
```bash
./build.sh deck-name
python tools/validate_deck.py static deck.tex --mode MODE
python tools/lang_lint.py     lint   deck.tex --mode MODE   # language gate (mechanical)
python tools/check_layout.py deck.tex build/deck.log --advise
```
The language gate (foreign-prose leakage, AI-flavor fillers, proof-hedges) is
defined in [language-quality-gate.md](../autobeamer-review/references/language-quality-gate.md);
fix CRITICAL/MAJOR findings before moving on.

**Between Wave 2 and Wave 3** the leader runs the [alignment check](references/validation/alignment-check.md): does the draft still match the plan and the original demands (sections, objectives, planned figures, every image request resolved, mode fidelity)? On drift, return to the Drafter before polishing.

Before delivery (Wave 3):
- Compile with XeLaTeX; confirm zero `Overfull \vbox`.
- Run static validation and layout audit.
- Run [autobeamer-validate](../autobeamer-validate/SKILL.md) `visual-check` on the PDF, especially every frame with blocks.
- Use [autobeamer-review](../autobeamer-review/SKILL.md) with the matching mode rubric.

## Reference Index

| Need | Reference |
|------|-----------|
| Full creation workflow | [references/workflows/full-create-guide.md](references/workflows/full-create-guide.md) |
| Passive-study mode | [references/modes/passive-study.md](references/modes/passive-study.md) |
| Active-Socratic mode | [references/modes/active-socratic.md](references/modes/active-socratic.md) |
| Academic-presentation reference | [references/modes/academic-presentation.md](references/modes/academic-presentation.md) |
| Source-document-first images | [references/images/source-document-first.md](references/images/source-document-first.md) |
| Image index (figure adoption) | [references/images/image-index.md](references/images/image-index.md) |
| Validation mode gates | [references/validation/mode-gates.md](references/validation/mode-gates.md) |
| Environment doctor / dep gating | [references/validation/env-doctor.md](references/validation/env-doctor.md) |
| Anti-drift alignment check | [references/validation/alignment-check.md](references/validation/alignment-check.md) |
| Wave 1 — planner subagent | [agents/autobeamer-planner.md](../../agents/autobeamer-planner.md) |
| Wave 2 — drafter subagent | [agents/autobeamer-drafter.md](../../agents/autobeamer-drafter.md) |
| Wave 3 — finisher subagent | [agents/autobeamer-finisher.md](../../agents/autobeamer-finisher.md) |
| Layout optimization | [autobeamer-layout](../autobeamer-layout/SKILL.md) |
| Build/compile errors | [autobeamer-build](../autobeamer-build/SKILL.md) |
| Review/audit | [autobeamer-review](../autobeamer-review/SKILL.md) |
| Automated validation / visual-check | [autobeamer-validate](../autobeamer-validate/SKILL.md) |
| TikZ diagrams | [autobeamer-tikz](../autobeamer-tikz/SKILL.md) |
| CJK fonts / Chinese deck setup | [autobeamer-build](../autobeamer-build/SKILL.md) (CJK Fonts section) |
