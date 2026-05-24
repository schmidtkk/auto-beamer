---
name: beamer-create
description: |
  Use when creating a new Beamer slide deck from scratch — converting papers, notes, or ideas
  into a structured XeLaTeX presentation. Triggers on: "create slides", "make a presentation",
  "build a talk", "prepare a lecture", "generate Beamer slides from paper", 论文讲解, 讨论班.
  Covers the full creation pipeline: material analysis → needs interview → structure plan →
  iterative drafting → figure integration → quality loop.
  Do NOT trigger on: editing existing slides (use beamer-layout), build errors (use beamer-build),
  review only (use beamer-review).
argument-hint: "create [topic-or-file] — starts the full deck creation pipeline"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob", "Agent", "AskUserQuestion", "TaskCreate", "TaskUpdate", "TaskList", "TaskGet"]
---

# Beamer Create — Deck Creation Pipeline

> **For layout optimization**, see [beamer-layout](../beamer-layout/SKILL.md).
> **For build errors**, see [beamer-build](../beamer-build/SKILL.md).
> **For review/audit**, see [beamer-review](../beamer-review/SKILL.md).

## Pipeline Overview

```
Phase 0: MATERIAL ANALYSIS  → Read papers, extract key info
Phase 1: NEEDS INTERVIEW    → Duration, audience, scope (MANDATORY)
Phase 2: STRUCTURE PLAN     → Detailed outline (GATE — user must approve)
Phase 3: DRAFT              → Iterative batch writing with compile checks
Phase 4: FIGURES            → TikZ diagrams and data visualization
Phase 5: QUALITY LOOP       → Compile → Review → Score → Fix (max 3 rounds)
```

**Rule:** Do NOT skip phases. Each phase produces output consumed by the next.

---

## Phase 0: Material Analysis (if papers/materials provided)

**Read first, ask later.** Understand the content before asking questions.

- Read the full paper/materials thoroughly
- Extract: core contribution, key techniques, main theorems, comparison with prior work
- Map notation conventions
- Identify the paper's logical structure and which parts are slide-worthy
- Note: prerequisite knowledge, natural section boundaries, what could be skipped or expanded

**Do NOT present results or ask questions yet — proceed directly to Phase 1.**

---

## Phase 1: Needs Interview (MANDATORY — informed by Phase 0)

Conduct a content-driven interview. The questions below are the **minimum required set** — also add paper-specific questions derived from Phase 0.

### Minimum Required Questions (always ask)

1. **Duration**: How long is the presentation?
2. **Audience level**: Who are the listeners?

### Optional Questions (ask for journal club, defense, or when user wants rehearsal)

3. **Speaker notes**: Would you like speaker notes in Presenter View? If yes, `\note{}` blocks per frame with telegraphic talking points. Requires `\setbeameroption{show notes on second screen=right}` in preamble.

### Content-Driven Questions (derive from Phase 0)

- **Prerequisite knowledge**: List concrete technical dependencies. E.g., "The paper builds on sumcheck and polynomial commitments. Should I review these?"
- **Content scope**: Offer the paper's actual components as options. Ask which to emphasize, skip, or briefly mention.
- **Depth vs. breadth**: If the paper has both intuitive overview and detailed constructions, ask which the user prefers.
- **Paper-specific decisions**: E.g., if the paper compares two constructions, ask whether to present both equally or focus on one.

### Guidelines

- Options should come from the paper's actual content, not generic templates.
- 3–6 questions total; don't over-ask, don't under-ask.
- If something is obvious from context, infer rather than ask.

### Slide Count Heuristic

~1 slide per 1.5–2 minutes.

### Timing Allocation Table

| Duration | Total slides | Intro/Motivation | Methods/Background | Core content | Summary |
|----------|-------------|------------------|-------------------|-------------|---------|
| 5min (lightning) | 5–7 | 1–2 | 0–1 | 2–3 | 1 |
| 10min (short) | 8–12 | 2 | 1–2 | 4–5 | 1 |
| 15min (conference) | 10–15 | 2–3 | 2–3 | 5–7 | 1–2 |
| 20min (seminar) | 13–18 | 3 | 2–3 | 6–9 | 2 |
| 45min (keynote) | 22–30 | 4–5 | 5–7 | 10–14 | 2–3 |
| 90min (lecture) | 45–60 | 5–6 | 8–12 | 25–35 | 3–4 |

### Talk-Type Tips

| Talk type | Key emphasis | Common mistake |
|-----------|-------------|----------------|
| Lightning (5min) | One core message, no background | Cramming a full talk into 5 minutes |
| Conference (10–20min) | 1–2 key results, fast methods overview | Too much detail, no big picture |
| Seminar (45min) | Deep dive OK, need visual rhythm | Wall-to-wall formulas without examples |
| Defense/Thesis | Mastery demonstration, systematic coverage | Skipping motivation, rushing results |
| Journal club | Critical analysis, facilitate discussion | Summarizing without evaluating |
| Grant pitch | Significance → feasibility → impact | Too technical, not enough "why" |

**Time distribution**: 40–50% on core content. Max 3–4 consecutive theory-heavy slides before a worked example or visual break.

---

## Phase 2: Structure Plan (GATE — user must approve before drafting)

Produce a **detailed outline**. For each section:
- Section title
- Number of slides allocated
- Key content points per slide (1–2 lines each)
- TikZ diagrams or figures planned (brief description)
- Notation to introduce

**Present the plan to the user.** Ask: structure OK? Expand/shrink/cut anything?

**Do NOT proceed to drafting until user approves.**

---

## Phase 3: Draft (iterative, batched)

### 3a. Writing Style

- **Telegraphic keywords**, not full sentences. Exception: one framing sentence per slide to set context.
- **Formulas and analysis interleave tightly** — define a quantity, then immediately state its cost/property/implication.
- **No conversational hedging** — never write "wait, not exactly" or "actually, let me clarify".
- **Use `\textbf{}` for key terms** on first introduction; use semantic colors for positive/negative/highlight.

### 3b. Opening and Closing Strategies

**Opening slide (pick one):**

| Strategy | When to use |
|----------|-------------|
| Surprising statistic | Counter-intuitive number available |
| Provocative question | Audience can't immediately answer |
| Real-world failure/problem | "System X failed because..." |
| Visual demonstration | Show the phenomenon before explaining |

**Closing strategies (never end on bare "Thank You"):**

| Strategy | When to use |
|----------|-------------|
| Call-back to opening | Revisit opening question, now answered |
| 3 key takeaways | Numbered, telegraphic, one slide |
| Open question / future direction | Invites Q&A naturally |

The second-to-last content slide delivers the lasting impression.

### 3c. Mathematical Slide Patterns

**Definition slide:**
```
[Framing sentence: why this definition matters]
[Formal definition in display math]
[Key properties / immediate consequences as 2–3 bullets]
```

**Construction/Algorithm slide:**
```
[One-line goal statement]
[Core equation / algorithm steps]
[Complexity analysis: cost, soundness, etc.]
```

**Comparison slide:**
```
[Side-by-side table: prior work vs this work]
[1–2 lines highlighting the key difference]
```

**Insight/Remark slide:**
```
[Observation the paper doesn't emphasize]
[Why this matters / what it implies]
```

**Theorem/Proof slide:**
```
[Framing sentence: informal statement]
\begin{theorem}[Optional name]
  [Formal statement]
\end{theorem}
[Key implication as 1–2 bullets]
```
- Proof on the **next** slide (never cram theorem + proof on one slide).
- For long proofs: show proof sketch only, full proof in backup slides.

### 3d. Content Density Constraints

**Upper bounds (per slide):**
- ≤ 7 bullet points
- ≤ 2 displayed equations
- ≤ 5 new symbols introduced
- ≤ 3 colored boxes (our convention; external says 2)

**Lower bounds (per slide):**
- Each slide MUST contain at least one substantive element
- A slide with only ≤ 3 short text-only bullets is too sparse — merge or enrich
- Pure text-only bullet slides ≤ 30% of total deck

**Density self-check after each batch:**
- Count slides with zero formulas/diagrams/tables → flag if > 30%
- Count slides with ≤ 3 short items and no math → candidates for merging

### 3e. Batch Workflow

- Work in batches of 5–10 slides, following the approved structure
- After each batch, **compile** to catch errors early:
  ```bash
  # Windows
  .\build_clean.ps1 deck-name
  # Linux/macOS
  ./build.sh deck-name
  ```
  See [beamer-build](../beamer-build/SKILL.md) for compilation details.
- After each batch: self-check notation consistency, density constraints, motivation-before-formalism
- Continue to next batch only after current batch compiles cleanly and passes self-check
- Fixing 2 issues in a 10-slide batch is far cheaper than fixing 12 issues in a 40-slide deck

### 3f. Table Best Practices

- **Always center tables** — wrap standalone tables in `\begin{center}...\end{center}`.
- **Never place a table immediately after the frame title** — insert `\vspace{4pt}` or introductory text between title and first `\toprule`. The compiler emits zero warnings for this; only visual inspection catches it.
- Always use `booktabs` (`\toprule`, `\midrule`, `\bottomrule`) — never vertical lines.
- Numbers right-aligned, text left-aligned, short labels centered.
- Max 6–7 columns, 8–10 rows per slide. More → split across slides:
  - Each continuation repeats the full header row.
  - Append " (cont'd)" to the frame title.
  - Split at logical row group boundaries.
  - Last page must have ≥ 3 data rows.
- Use `\resizebox{\textwidth}{!}{...}` only as last resort.
- Highlight key cells with `\cellcolor{...!15}` or `\textbf{}`.
- For comparison tables: bold the best result in each row/column.

### 3g. Algorithm and Code Display

- Pseudocode ≤ 10 lines per slide.
- Highlight the critical line(s) via `escapeinside` or `\colorbox`.
- Input/output clearly stated at top.
- For code (not pseudocode): `\ttfamily\small`, syntax highlighting via listings.

---

## Phase 4: Figures

### TikZ Diagrams

- TikZ diagrams in Beamer source (single source of truth)
- Apply TikZ quality standards — see [beamer-tikz](../beamer-tikz/SKILL.md)

### Data Visualization Guidelines

Journal figures ≠ slide figures. Adapt for projection:

- **Simplify ruthlessly** — remove minor gridlines, detailed legends. Show only supporting data.
- **Enlarge everything** — axis labels ≥ 18pt, line width 2–4pt, marker size 8–12pt.
- **Direct labeling** — label lines/bars directly instead of separate legend.
- **One message per figure** — split multi-panel journal figures across slides.
- **Highlight the result** — key data in bold saturated color, comparison in muted gray.
- **Color-blind safe palette** — blue+orange over red+green. Add line style differences.
- **Subfigures** — use `\begin{subfigure}{0.48\textwidth}` for side-by-side. Max 2 per slide.

### pgfplots for Data-Driven Figures

```latex
% Bar chart
\begin{axis}[ybar, bar width=12pt, xlabel={Method}, ylabel={Accuracy (\%)},
  symbolic x coords={Baseline, Ours, Oracle}, xtick=data, nodes near coords]
  \addplot coordinates {(Baseline,72) (Ours,89) (Oracle,95)};
\end{axis}
```

```latex
% Line plot from CSV
\begin{axis}[xlabel={Epoch}, ylabel={Loss}, legend pos=north east, grid=major]
  \addplot table[x=epoch, y=train_loss, col sep=comma] {data/results.csv};
  \addplot table[x=epoch, y=val_loss, col sep=comma] {data/results.csv};
  \legend{Train, Validation}
\end{axis}
```

Always set explicit `width` and `height` to prevent overflow.

### Image Integration with Layout Optimizer

For each slide with images, run:

```bash
python tools/layout_optimizer.py suggest --img W:H --cards N
```

Then populate the generated skeleton. See [beamer-layout](../beamer-layout/SKILL.md) for full layout pipeline.

---

## Phase 5: Quality Loop (MANDATORY — iterative)

```
┌─→ 5a. Compile (2-pass XeLaTeX)
│   5b. Self-Review (structure + content + visual)
│   5c. Score (apply rubric below)
│   5d. Fix all issues found
└── If score < 90 and round < 3: loop back to 5a
    If score ≥ 90 or round = 3: report to user
```

### 5a. Compilation

```bash
# Windows
.\build_clean.ps1 deck-name
# Linux/macOS
./build.sh deck-name
```

Check: errors, overfull hbox, undefined references.

### 5b. Self-Review Checklist

**Structure:**
- [ ] Slide count matches plan (±2 tolerance)
- [ ] Logical flow: motivation → background → technique → results → summary
- [ ] No section has >4 consecutive formal slides without example or visual break
- [ ] Transition sentences between major sections

**Content density:**
- [ ] No slide has only ≤3 short bullets with no math/diagram
- [ ] Pure text-only slides ≤ 30%
- [ ] No slide exceeds upper bounds (7 bullets, 2 equations, 5 symbols, 3 boxes)

**TikZ and visuals:**
- [ ] No label-label or label-curve overlaps
- [ ] No content overflowing slide boundary
- [ ] No content overflowing inside colored boxes (visually verify every box)
- [ ] TikZ diagrams fit within remaining slide space
- [ ] Tables fit within slide width and are centered

**Notation:**
- [ ] Same symbol used consistently
- [ ] Every symbol defined before use

**Layout metrics** (run our tools):
```bash
python tools/check_layout.py deck.tex build/deck.log --advise
```

Target: DGV=0, U∈[0.80,0.95], B>0.80, G<0.15, Block≤3.
See [beamer-layout](../beamer-layout/SKILL.md) for full acceptance criteria.

### 5c. Quality Score Rubric

Start at 100, deduct per issue:

| Issue type | Deduction |
|-----------|-----------|
| Compilation error | −10 each |
| Overfull hbox > 10pt | −5 each |
| Undefined reference | −3 each |
| Box overflow (visual) | −5 each |
| Sparse slide (≤3 text-only bullets) | −3 each |
| Text-only slide ratio > 30% | −5 (total) |
| >4 consecutive formal slides | −3 per run |
| TikZ label overlap | −5 each |
| Notation inconsistency | −3 each |
| Missing motivation before definition | −3 each |
| Missing backup slides | −3 |
| No references slide | −5 |

**Score ≥ 90**: Ready to present.
**Score 80–89**: Minor refinements needed.
**Score < 80**: Significant revision required.

### 5d. Fix

Fix all critical and major issues. Re-compile. Max 3 rounds.

### Post-Creation Checklist (final gate)

```
[ ] Compiles without errors
[ ] No overfull hbox > 10pt
[ ] All citations resolve
[ ] Score ≥ 90
[ ] Every definition has motivation + worked example
[ ] Max 3 colored boxes per slide
[ ] No sparse slides
[ ] TikZ diagrams visually verified
[ ] Tables centered and separated from title bar
[ ] No content overflow inside colored boxes
[ ] References slide present (second-to-last)
[ ] Backup slides present (after Thank You)
[ ] check_layout.py: DGV=0, U∈[0.80,0.95], B>0.80
```

---

## Cross-References

| Need | Skill |
|------|-------|
| Layout optimization, column balance, DGV metrics | [beamer-layout](../beamer-layout/SKILL.md) |
| Build errors, font issues, compilation | [beamer-build](../beamer-build/SKILL.md) |
| Review, audit, pedagogy, excellence | [beamer-review](../beamer-review/SKILL.md) |
| TikZ quality, patterns, accuracy | [beamer-tikz](../beamer-tikz/SKILL.md) |
| Automated validation, visual check | [beamer-validate](../beamer-validate/SKILL.md) |
