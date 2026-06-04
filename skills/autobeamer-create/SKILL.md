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

## Required First Steps

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

Compatibility aliases:
- "Mentor", "self-study", "study deck", or textbook/chapter requests map to `passive-study` unless the user asks for Socratic discovery.
- "Socratic", "active study", "reinvent", "derive with me", or "mentor me with questions" map to `active-socratic`.
- "Presentation", "talk", "seminar", "conference", "defense", or "academic sharing" map to `academic-presentation`.

Every structure plan must state the selected mode, loaded references, and mode-specific acceptance gates.

## Pipeline

```
Phase 0: MATERIAL ANALYSIS  -> read sources, extract figures, map notation
Phase 1: NEEDS INTERVIEW    -> ask only missing content/audience/mode questions
Phase 2: STRUCTURE PLAN     -> detailed outline; user approval gate
Phase 3: DRAFT              -> write in 5-10 slide batches with compile checks
Phase 4: FIGURES            -> source figures, TikZ, pgfplots, layout optimization
Phase 5: QUALITY LOOP       -> compile, validate, visual-check, review, fix
```

Do not skip phases. For detailed phase guidance, load [references/workflows/full-create-guide.md](references/workflows/full-create-guide.md).

## Material Analysis

If papers/materials are provided:
- Read the source thoroughly before interviewing the user.
- Extract contribution, method, theorem/result structure, notation, prerequisites, and slide-worthy figures.
- For PDFs, run:
  ```bash
  python tools/paper_parser.py parse paper.pdf --output slides_assets/paper.json
  python tools/paper_parser.py extract-images paper.pdf --output slides_assets/source_figures/
  ```
- Inventory extracted figures with page number, aspect ratio, candidate slide use, and whether they need redraw/crop/adaptation.

## Interview Gate

Ask only what cannot be inferred safely:
- Duration or target effort budget.
- Audience/learner level and prior field exposure.
- Mode confirmation when ambiguous.
- Paper-specific scope decisions derived from the source.
- Whether speaker notes are needed for `academic-presentation`.

Avoid generic questionnaires. Use the material to ask concrete choices.

## Structure Plan Gate

Before drafting, present a plan containing:
- Selected mode and loaded references.
- Section list with slide counts.
- Per-section learning objective or narrative purpose.
- Planned figures, tables, TikZ diagrams, or source images.
- New notation and prerequisite reminders.
- Validation gates from [references/validation/mode-gates.md](references/validation/mode-gates.md).

Ask for approval before drafting.

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

## Figures And Layout

Use source-document-first precedence:
1. Extracted source figure.
2. Rendered/cropped source page region.
3. Local TikZ, pgfplots, or redrawn figure.
4. External image only as local, attributed fallback.

For image-heavy slides, run:
```bash
python tools/layout_optimizer.py suggest --img W:H --cards N
```

Use [autobeamer-layout](../autobeamer-layout/SKILL.md) for layout optimization and [autobeamer-tikz](../autobeamer-tikz/SKILL.md) for diagrams.

## Quality Gate

After each draft batch:
```bash
./build.sh deck-name
python tools/validate_deck.py static deck.tex --mode MODE
python tools/check_layout.py deck.tex build/deck.log --advise
```

Before delivery:
- Compile with XeLaTeX.
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
| Validation mode gates | [references/validation/mode-gates.md](references/validation/mode-gates.md) |
| Layout optimization | [autobeamer-layout](../autobeamer-layout/SKILL.md) |
| Build/compile errors | [autobeamer-build](../autobeamer-build/SKILL.md) |
| Review/audit | [autobeamer-review](../autobeamer-review/SKILL.md) |
| Automated validation / visual-check | [autobeamer-validate](../autobeamer-validate/SKILL.md) |
| TikZ diagrams | [autobeamer-tikz](../autobeamer-tikz/SKILL.md) |
