---
name: autobeamer-create
description: |
  Use when creating a new Beamer slide deck from scratch — converting papers, notes, or ideas
  into a structured XeLaTeX presentation. Triggers on: "create slides", "make a presentation",
  "build a talk", "prepare a lecture", "generate Beamer slides from paper", 论文讲解, 讨论班.
  Covers the full creation pipeline: material analysis → needs interview → structure plan →
  iterative drafting → figure integration → quality loop.
  Do NOT trigger on: editing existing slides (use autobeamer-layout), build errors (use autobeamer-build),
  review only (use autobeamer-review).
argument-hint: "create [topic-or-file] — starts the full deck creation pipeline"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob", "Agent", "AskUserQuestion", "TaskCreate", "TaskUpdate", "TaskList", "TaskGet"]
---

# AutoBeamer Create — Deck Creation Pipeline

> **For layout optimization**, see [autobeamer-layout](../autobeamer-layout/SKILL.md).
> **For build errors**, see [autobeamer-build](../autobeamer-build/SKILL.md).
> **For review/audit**, see [autobeamer-review](../autobeamer-review/SKILL.md).

## Mode Routing

Before outlining, set exactly one deck mode and load its reference:

| Mode | Use when | Load |
|------|----------|------|
| `passive-study` | The learner is entering an unfamiliar field and needs comprehensive, enjoyable, frustration-shielded teaching | [references/modes/passive-study.md](references/modes/passive-study.md) |
| `active-socratic` | The learner wants guided discovery through questions, thought experiments, pen-and-paper work, and productive struggle | [references/modes/active-socratic.md](references/modes/active-socratic.md) |
| `academic-presentation` | The deck is for a live talk, seminar, defense, journal club, or academic sharing | [references/modes/academic-presentation.md](references/modes/academic-presentation.md) |

Compatibility aliases:
- "Mentor", "self-study", "study deck", or textbook/chapter requests default to `passive-study` unless the user explicitly asks for Socratic discovery.
- "Presentation", "talk", "seminar", "conference", "defense", or "academic sharing" map to `academic-presentation`.
- "Socratic", "active study", "reinvent", "derive with me", or "mentor me with questions" map to `active-socratic`.

Every structure plan must state the selected mode, the loaded reference path, and the mode-specific acceptance gates from [references/validation/mode-gates.md](references/validation/mode-gates.md).

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
- If a provided PDF is available, run source-document-first extraction before planning web or external images:
  ```bash
  python tools/paper_parser.py parse paper.pdf --output slides_assets/paper.json
  python tools/paper_parser.py extract-images paper.pdf --output slides_assets/source_figures/
  ```
- Extract: core contribution, key techniques, main theorems, comparison with prior work
- Map notation conventions
- Identify the paper's logical structure and which parts are slide-worthy
- Note: prerequisite knowledge, natural section boundaries, what could be skipped or expanded
- Inventory extracted source figures with page number, aspect ratio, candidate slide use, and whether each needs redraw, crop, or adaptation.

**Do NOT present results or ask questions yet — proceed directly to Phase 1.**

---

## Phase 1: Needs Interview (MANDATORY — informed by Phase 0)

Conduct a content-driven interview. The questions below are the **minimum required set** — also add paper-specific questions derived from Phase 0.

### Minimum Required Questions (always ask)

1. **Duration**: How long is the presentation?
2. **Audience level**: Who are the listeners?
3. **Deck mode**: `passive-study`, `active-socratic`, or `academic-presentation`?

### Optional Questions (ask for journal club, defense, or when user wants rehearsal)

3. **Speaker notes**: Would you like speaker notes in Presenter View? If yes, `\note{}` blocks per frame with telegraphic talking points. Requires `\setbeameroption{show notes on second screen=right}` in preamble.

### Passive-Study Overrides (apply for `passive-study`; legacy name: "Mentor / self-study")

When the deck is for **self-study** (not a live presentation), override these defaults:

| Aspect | Presentation default | Mentor override |
|--------|---------------------|-----------------|
| Writing style | Telegraphic keywords | **Complete sentences**, self-contained explanations |
| Slide count heuristic | ~1 per 1.5–2 min | **No limit** — completeness over brevity |
| Proofs | Sketch only (≤3 bullets) | **Full proofs**, every step shown |
| Content density | Max 2 equations, 7 bullets, 3 colored boxes | Max **3 equations, 10 bullets, 3 colored boxes** |
| Examples | 1 per concept | **2–3 per concept**, worked step-by-step |
| Exercises | None | **≥3 per chapter**, with hints and answers |
| Bibliography | Optional references slide | **Full bibliographical notes section**, 4–5+ frames |
| Structural elements | Title → Content → Summary | Title → Content → **Glossary** → **Exercises** → **Bibliography** |

**Key rule for passive-study mode**: "Content must be MORE detailed than the source, not less." If the source says "proofs will only be sketched", the passive-study deck shows every step.

### Active-Socratic Overrides (apply for `active-socratic`)

In active study, the deck does not primarily teach by exposition. It creates a guided path for the learner to reconstruct the ideas.

| Aspect | Rule |
|--------|------|
| Slide role | One carefully chosen question, task, or thought experiment per frame |
| Exposition | Minimal; only enough context to make the next attempt possible |
| Learner work | Include pen-and-paper derivations, small numerical examples, and prediction prompts |
| Hints | Stage hints from weak to strong; do not reveal the final answer before an attempt gate |
| Solutions | Put complete solutions in backup or delayed reveal frames, not immediately after the question |
| Frustration control | Productive struggle only; add prerequisite reminders before impossible jumps |

Use [references/modes/active-socratic.md](references/modes/active-socratic.md) for the full gate list.

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

## Book / Textbook Reading-Group Decks

A chapter from a math textbook (e.g., Villani, Brenier, Evans, Rudin) is never a live presentation by default — **always default to `passive-study`** unless the user asks for `active-socratic`. The reader has no speaker; the deck *is* the lecture.

### 2.1 Content Ladder (mandatory structure per chapter)

Every book deck chapter follows this ladder in order. Skipping a rung produces confusion for self-study readers.

| Rung | Slides | Purpose |
|------|--------|---------|
| Chapter overview | 1–2 | State what this chapter proves and why it matters. Connect to previous chapter's result. |
| Prerequisite reminder | 1–2 | List results and notation carried forward. Readers who forgot can stop here and review. |
| Core definitions | 2–4 slides per definition | Motivation → formal statement → example → key properties. Never bare definition without motivation. |
| Main theorems | 3–10 slides per theorem | Informal statement → formal statement → full proof (every step) → geometric intuition |
| Worked examples | 2–3 per concept | Concrete, small-scale. Walk through applying the definition/theorem step by step. |
| Exercises | 3+ per chapter | Graded difficulty. Include hint (collapsed) and solution in backup slides. |
| Bibliographical notes | 4–5 slides | Original sources, historical context, alternative proofs, related work. |
| Glossary / notation | 1–2 | All symbols used in the chapter. Bilingual if the reading group mixes languages. |

### 2.2 Visual Intuition for Each Key Object

**Rule: every abstract mathematical object must get a 2D visual.** Without a picture, measure-theory readers lose spatial intuition within 3 slides.

| Object class | Required visual |
|---|---|
| Measure / distribution | A density curve or probability mass shown over a domain |
| Joint distribution / coupling | A 2D grid or scatter plot showing the joint mass |
| Map / push-forward | Source density → arrow → deformed target density |
| Deterministic transport (Monge map) | Each source point with a single arrow to its destination |
| Wasserstein / metric ball | A "ball" of measures around a center measure in a schematic space |
| Convex function | Graph + epigraph + tangent line |
| Set / constraint | Highlighted region in 2D with boundary annotated |

Do not write a formal definition slide until the visual has been shown.

### 2.3 Figure Selection Protocol for Pure Math

1. **Is there a canonical, publication-quality diagram in the literature?**
   - Check: POT library examples (Python Optimal Transport), Wikimedia Commons, arXiv paper figures (CC license), standard textbook illustrations
2. **If yes and high quality** → use the external image with attribution. Label it in the slide footer.
3. **If no exact match, or the setup is specific** (particular function values, dual CDF visualization, specific coordinate system) → build TikZ.

**Empirical baseline**: in a standard measure-theory / OT chapter, roughly 2 out of 5 custom figures can be replaced with external images. Accept this ratio; do not force external images where TikZ is more precise.

When keeping TikZ for a specific setup, document *why* in a comment so the decision is clear on revisit.

### 2.4 Symbol Introduction Discipline

Every new symbol must appear in three roles:
1. **Display math** — formal definition
2. **Intuitive sentence** — "this measures the cost of moving one unit of mass from x to y"
3. **Connecting example** — apply it to a concrete small case (e.g., two-point distribution)

**Max 3 new symbols per slide.** If a theorem introduces 5+ new symbols, break the introduction over multiple slides before stating the theorem.

### 2.5 Proof Granularity in Passive-Study Mode

For analysis / measure theory proofs:
- Each **inequality step** = one bullet with justification (e.g., "by Jensen's inequality")
- Each **application of a theorem** = one bullet citing the theorem by name
- Each **approximation / limit argument** = its own slide
- Major theorem proof: plan **4–8 slides** for a non-trivial result; **8–15 slides** for a core theorem like Brenier or Kantorovich duality

Never write "by standard arguments" or "it follows" in `passive-study`. If a step is non-trivial, show it.

### 2.6 Bilingual Notation Convention (Chinese/English reading groups)

- **First occurrence**: `English term (中文术语)` — parenthetical on first use in body text
- **Glossary slide**: bilingual table `English | 中文 | Symbol | Definition`
- **Italic** for English terms embedded in Chinese sentences: `测度 $\mu$ 是 \textit{push-forward} 的...`
- Chapter title slide: subtitle in Chinese (读书报告 · 第 N 章)
- Section headings: English primary, Chinese subtitle (optional)

### 2.7 Prerequisite Scaffolding

Start every major theorem section with a **"What we need from before"** slide (1 slide):

```latex
\begin{frame}{Prerequisites for This Section}
  \begin{itemize}
    \item [Result/definition we rely on, with reference to earlier chapter]
    \item ...
  \end{itemize}
\end{frame}
```

Never assume the reader remembers results from a previous chapter. Explicit forward-references reduce cognitive load for self-study.

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

**Academic-presentation mode:**
- **Telegraphic keywords**, not full sentences. Exception: one framing sentence per slide to set context.
- **Formulas and analysis interleave tightly** — define a quantity, then immediately state its cost/property/implication.
- **No conversational hedging** — never write "wait, not exactly" or "actually, let me clarify".
- **Use `\textbf{}` for key terms** on first introduction; use semantic colors for positive/negative/highlight.

**Passive-study mode:**
- **Complete sentences** — the reader has no speaker to fill gaps.
- **Motivation before every formal statement** — explain "why" before "what", even for lemmas.
- **Explain every symbol** — no "obviously" or "it is well known"; define everything.
- **Paraphrase, don't quote** — translate dense mathematical prose into accessible explanations (see `CLAUDE.md` Mentor Deck Style).

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

Academic-presentation mode:
```
[Framing sentence: informal statement]
\begin{theorem}[Optional name]
  [Formal statement]
\end{theorem}
[Key implication as 1–2 bullets]
```
- Proof on the **next** slide (never cram theorem + proof on one slide).
- For long proofs: show proof sketch only, full proof in backup slides.

Passive-study mode:
```
[Framing sentence: informal statement + why this matters]
\begin{theorem}[Optional name]
  [Formal statement, ALL assumptions listed]
\end{theorem}
[Physical/geometric intuition if applicable]
```
- Proof on the **next** slide(s); for long proofs, use **multiple consecutive slides** showing every step.
- Never say "proof sketch" or "proof omitted" in `passive-study` — show **every intermediate step**.
- Each proof step gets its own frame if the algebra is dense.

### 3d. Content Density Constraints

**Academic-presentation mode:**

| Element | Max per slide | Action if exceeded |
|---------|---------------|-------------------|
| Bullet points | 7 | Split slide |
| Displayed equations | 2 | Split slide |
| New symbols | 5 | Introduce over multiple slides |
| Colored boxes | 3 | Redistribute content |

**Lower bounds (academic-presentation):**
- Each slide MUST contain at least one substantive element
- A slide with only ≤ 3 short text-only bullets is too sparse — merge or enrich
- Pure text-only bullet slides ≤ 30% of total deck

**Passive-study mode:**

| Element | Max per slide | Rationale |
|---------|---------------|-----------|
| Bullet points | 10 | Complete sentences need more room |
| Displayed equations | 3 | Derivations are the content |
| New symbols | 8 | Background supplement introduces more notation |
| Colored boxes | 3 | Universal hard rule; use plain text, tables, or split frames for additional material |

**Lower bounds (passive-study):**
- Every slide MUST contain ≥1 substantive element (formula, diagram, table, theorem, proof step, or worked example)
- A slide with only ≤ 3 short text-only bullets is too sparse — merge or enrich
- **Pure text-only bullet slides ≤ 20%** of total deck (stricter than Presentation)

**Density self-check after each batch:**
- Count slides with zero formulas/diagrams/tables → flag if > 30% (`academic-presentation`) or > 20% (`passive-study`)
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
  See [autobeamer-build](../autobeamer-build/SKILL.md) for compilation details.
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

### Source-Document-First Image Policy

Load [references/images/source-document-first.md](references/images/source-document-first.md) whenever the user provides a PDF, paper, report, or source document.

Priority order:
1. Extract from the provided PDF or source document with `paper_parser.py parse` and `paper_parser.py extract-images`.
2. Redraw or adapt source figures locally when the original is too dense for slides.
3. Use TikZ/pgfplots for exact mathematical setups, derivations, or notation-specific diagrams.
4. Use external images only as a fallback when the source document has no suitable visual and the external asset is locally saved, attributed, and license-compatible.

### TikZ Diagrams

- TikZ diagrams in Beamer source (single source of truth)
- Apply TikZ quality standards — see [autobeamer-tikz](../autobeamer-tikz/SKILL.md)

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

Then populate the generated skeleton. See [autobeamer-layout](../autobeamer-layout/SKILL.md) for full layout pipeline.

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
- [ ] **passive-study**: Glossary slide present, exercise slides present, bibliographical notes section present

**Content density:**
- [ ] No slide has only ≤3 short bullets with no math/diagram
- [ ] Pure text-only slides ≤ 30% (`academic-presentation`) or ≤ 20% (`passive-study`)
- [ ] No slide exceeds upper bounds (`academic-presentation`: 7 bullets / 2 eq / 5 symbols / 3 boxes; `passive-study`: 10 / 3 / 8 / 3)

**TikZ and visuals:**
- [ ] No label-label or label-curve overlaps
- [ ] No content overflowing slide boundary
- [ ] No content overflowing inside colored boxes (visually verify **every** box)
- [ ] TikZ diagrams fit within remaining slide space
- [ ] Tables fit within slide width and are centered

**Notation:**
- [ ] Same symbol used consistently
- [ ] Every symbol defined before use

**Layout metrics** (run our tools — **mandatory**):
```bash
python tools/check_layout.py deck.tex build/deck.log --advise
```

| Mode | U (utilization) | B (balance) | G (gravity) | DGV |
|------|-----------------|-------------|-------------|-----|
| academic-presentation | [0.80, 0.95] | >0.80 | <0.15 | 0 |
| passive-study | [0.75, 0.98] | >0.70 | <0.20 | 0 |

- **U < 0.60** in any frame → sparse slide, must merge or enrich
- **U > 1.00** in any frame → overflow, must split

See [autobeamer-layout](../autobeamer-layout/SKILL.md) for full acceptance criteria.

### 5c. Quality Score Rubric

Start at 100, deduct per issue:

| Issue type | Deduction |
|-----------|-----------|
| Compilation error | −10 each |
| Overfull hbox > 10pt | −5 each |
| Undefined reference | −3 each |
| Box overflow (visual) | −5 each |
| Sparse slide (≤3 text-only bullets, or U < 0.60) | −5 each |
| Text-only slide ratio > 30% (`academic-presentation`) or > 20% (`passive-study`) | −5 (total) |
| >4 consecutive formal slides | −3 per run |
| TikZ label overlap | −5 each |
| Notation inconsistency | −3 each |
| Missing motivation before definition | −3 each |
| Missing backup slides | −3 |
| No references slide | −5 |
| **passive-study only**: Proof sketch instead of full proof | −10 each |
| **passive-study only**: Missing glossary or exercise section | −5 each |
| **passive-study only**: Missing bibliographical notes section | −5 |

**academic-presentation thresholds:**
- **Score ≥ 90**: Ready to deliver
- **Score 80–89**: Acceptable with caveats
- **Score < 80**: Must fix before delivery

**passive-study thresholds:**
- **Score ≥ 95**: Ready to deliver
- **Score 90–94**: Minor refinements needed
- **Score < 90**: Must fix before delivery

### 5d. Fix

Fix all critical and major issues. Re-compile. Max 3 rounds.

### Post-Creation Checklist (final gate)

**academic-presentation:**
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

**passive-study (additional / override):**
```
[ ] Score ≥ 95
[ ] Every proof shown in full (no "sketch" or "omitted")
[ ] Glossary slide present (术语速查)
[ ] Exercise slides present (≥3 per chapter)
[ ] Bibliographical notes section present (4–5+ frames)
[ ] Every assumption stated with intuition
[ ] check_layout.py: DGV=0, U∈[0.75,0.98], B>0.70
[ ] Visual-check: every frame with blocks inspected for interior overflow
[ ] No frame with only 1 block and zero math/diagram
```

---

## Cross-References

| Need | Skill |
|------|-------|
| Layout optimization, column balance, DGV metrics | [autobeamer-layout](../autobeamer-layout/SKILL.md) |
| Build errors, font issues, compilation | [autobeamer-build](../autobeamer-build/SKILL.md) |
| Review, audit, pedagogy, excellence | [autobeamer-review](../autobeamer-review/SKILL.md) |
| TikZ quality, patterns, accuracy | [autobeamer-tikz](../autobeamer-tikz/SKILL.md) |
| Automated validation, visual check | [autobeamer-validate](../autobeamer-validate/SKILL.md) |
