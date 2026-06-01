---
name: autobeamer-review
description: |
  Use when reviewing, auditing, or quality-checking existing Beamer slide decks.
  Triggers on: "review slides", "audit deck", "check quality", "pedagogy review",
  "proofread", "devils advocate", "excellence review", "find issues in slides".
  Provides structured review with rubric scoring, layout audit with DGV metrics,
  pedagogical validation, and multi-perspective excellence review.
  Do NOT trigger on: creating new slides (use autobeamer-create), build errors (use autobeamer-build).
argument-hint: "review [deck.tex] — starts structured review pipeline"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob", "Agent", "AskUserQuestion"]
---

# AutoBeamer Review — Quality Assurance Actions

> **For deck creation**, see [autobeamer-create](../autobeamer-create/SKILL.md).
> **For layout optimization**, see [autobeamer-layout](../autobeamer-layout/SKILL.md).
> **For build errors**, see [autobeamer-build](../autobeamer-build/SKILL.md).
> **For TikZ quality**, see [autobeamer-tikz](../autobeamer-tikz/SKILL.md).

## Action Index

| Action | Purpose | When to use |
|--------|---------|-------------|
| `proofread` | Grammar, typos, consistency | Final pass before presentation |
| `audit` | Visual layout, spacing, DGV metrics | After drafting or after changes |
| `pedagogy` | Teaching effectiveness, 13 patterns | Content review, journal clubs |
| `excellence` | Multi-perspective parallel review | Pre-submission, important talks |
| `devils-advocate` | Challenge assumptions, find weaknesses | Pre-defense, critical review |

---

## Action: `proofread`

Structured proofreading with categorized report.

### Categories

**1. Grammar & Language**
- Subject-verb agreement
- Article usage (a/an/the)
- Tense consistency (present for facts, past for experiments)
- Parallel structure in lists
- Academic register (no colloquialisms)

**2. Typos & Orthography**
- Spelling errors
- Missing/wrong punctuation
- CJK punctuation in English context (。→ ., ，→ ,, ：→ :)
- Wrong font in math mode

**3. Overflow & Layout**
- Text exceeding slide boundaries
- Content overflowing inside colored boxes
- Tables wider than `\textwidth`
- Images overlapping text or margins
- Frame title bar overlapping content

**4. Consistency**
- Notation: same symbol for same concept throughout
- Terminology: same term for same concept
- Abbreviation: defined on first use, consistent thereafter
- Numbering: figures, tables, equations sequential
- Style: capitalization in titles, bullet style

**5. Academic Quality**
- Claims backed by evidence or citation
- Methods reproducible from description
- Results stated with appropriate precision
- Limitations acknowledged

### Report Format

```
## Proofread Report: [deck-name]

### Summary
- Total slides: N
- Issues found: N
  CRITICAL: N | HIGH: N | MEDIUM: N | LOW: N

### Issues by Category

#### Grammar & Language
- [MEDIUM] Slide 7: "the network learns to generating" → "the network learns to generate"
- ...

#### Typos & Orthography
...

#### Overflow & Layout
...

#### Consistency
...

#### Academic Quality
...
```

---

## Action: `audit`

Visual layout audit. Integrates our `check_layout.py` DGV metrics.

### Step 1: Run Layout Audit Tool

```bash
python tools/check_layout.py deck.tex build/deck.log --advise
```

This outputs per-slide metrics: U (utilization), B (balance), G (gravity), DGV violations.

### Step 2: Visual Density Assessment

For each slide, check:

| Check | Pass criteria |
|-------|--------------|
| Vertical fill | Content fills ≥ 60% of slide height |
| Horizontal fill | No single-word lines at column boundaries |
| Whitespace balance | Roughly equal top/bottom margins |
| Box sizing | All boxes in a row visually same height |
| Image scale | Images ≥ 20% of slide area, no tiny insets |

### Step 3: Spacing-First Fix Principle

When a slide looks wrong, fix in this priority order:

1. **Delete spacing** — Remove `\vspace`, `\\[Npt]`, redundant blank lines
2. **Reduce scale** — Lower `max height`, `\resizebox` factor, or image `width`
3. **Shorten text** — Cut words, use abbreviations, remove non-essential bullets
4. **Reflow layout** — Change column ratio, switch layout template
5. **Split frame** — Last resort; create a continuation slide

### Step 4: DGV Grammar Fix

| Code | Rule | Fix |
|------|------|-----|
| GV-1 | Loose text outside box | Wrap in `\begin{goldcall}` or structured layout |
| GV-2 | `goldcall` inside `columns` | Move below `\end{columns}` |
| GV-3 | Multiple `bluecard`s in one column | Split frame or convert to text (max 3 blocks/slide) |
| GV-4 | Wide image (AR>1.5) in SIDE layout | Switch to `\budgetwideimg` |

### Audit Report Format

```
## Layout Audit Report: [deck-name]

### Tool Metrics Summary
| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| DGV violations | 0 | N | ✅/❌ |
| Mean U | [0.80, 0.95] | X.XX | ✅/❌ |
| Min B (column slides) | > 0.80 | X.XX | ✅/❌ |
| Mean G | < 0.15 | X.XX | ✅/❌ |

### Per-Slide Issues
- Slide 3: U=0.72 (sparse) → add content or merge with slide 2
- Slide 7: B=0.63 (unbalanced) → hardcode column heights
- Slide 12: GV-2 (goldcall inside columns) → move outside

### Spacing Issues
- Slide 5: excessive \vspace{12pt} between items → reduce to 4pt
- Slide 9: image scaled to 0.3\textheight (too small) → increase to 0.45

### Recommendations
1. ...
2. ...
```

---

## Action: `pedagogy`

Validate teaching effectiveness using 13 pedagogical patterns.

### 13 Validation Patterns

**Motivation & Context**
1. **Problem-first**: Does the deck state the problem before presenting the solution?
2. **Real-world anchor**: Is there a concrete example or application early on?
3. **Motivation before formalism**: Are concepts motivated before being formally defined?

**Progressive Disclosure**
4. **Scaffolded complexity**: Does complexity increase gradually?
5. **One idea per slide**: Does each slide convey a single clear message?
6. **Concrete→abstract**: Are concrete examples given before abstract formulations?

**Retention & Understanding**
7. **Worked example within 2 slides**: After a definition, is there a worked example within 2 slides?
8. **Visual reinforcement**: Are key concepts supported by diagrams or visual aids?
9. **Recap moments**: Does the deck periodically summarize what was covered?

**Engagement**
10. **Variation in slide types**: Mix of text, math, figures, tables, diagrams?
11. **Audience-appropriate level**: Is the technical depth appropriate for the stated audience?
12. **Clear transitions**: Are section boundaries marked and transitions smooth?

**Closure**
13. **Effective conclusion**: Does the ending reinforce key takeaways rather than just listing "future work"?

### Deck-Level Checks

- **Slide count vs. duration**: ~1 slide per 1.5–2 minutes
- **Text-only slide ratio**: ≤ 30%
- **Formal slide runs**: No more than 4 consecutive formal slides without example/visual
- **Opening strategy**: Does the opening hook the audience?
- **Closing strategy**: Does the ending leave a lasting impression?

### Pedagogy Report Format

```
## Pedagogy Review: [deck-name]

### Pattern Compliance: N/13 passed

| # | Pattern | Status | Notes |
|---|---------|--------|-------|
| 1 | Problem-first | ✅ | Slide 2 states problem clearly |
| 2 | Real-world anchor | ❌ | No concrete example until slide 8 |
| ... | ... | ... | ... |

### Deck-Level Assessment
- Slide count: 15 (target for 20min: 13–18) ✅
- Text-only ratio: 25% ✅
- Longest formal run: 3 slides ✅

### Top 3 Recommendations
1. Add a worked example after the definition on slide 5
2. Insert a visual diagram for the pipeline on slide 9
3. Strengthen opening with a surprising statistic
```

---

## Action: `excellence`

Multi-perspective parallel review for important talks (pre-submission, keynote, defense).

### Process

Run 3 perspectives in parallel (conceptually — one agent reviews all three):

1. **Content Expert** — Technical accuracy, completeness, rigor
2. **Design Reviewer** — Visual quality, layout, readability, contrast
3. **Audience Advocate** — Clarity, pacing, engagement, accessibility

### Perspective 1: Content Expert

- Are all claims accurate and supported?
- Is the methodology clearly described?
- Are results presented with appropriate context?
- Are limitations acknowledged?
- Is notation consistent and standard?

### Perspective 2: Design Reviewer

- Does every slide look intentional (not template-generic)?
- Is there visual hierarchy (scale contrast, not uniform)?
- Are colors used semantically, not decoratively?
- Is there sufficient contrast (WCAG AA)?
- Do hover/focus states exist where applicable?
- Are tables and figures properly integrated?

### Perspective 3: Audience Advocate

- Can a non-expert follow the logical flow?
- Is pacing appropriate (not too fast/slow)?
- Are technical terms defined before use?
- Are there enough visual breaks?
- Is the presentation accessible (color-blind safe, readable fonts)?

### Combined Excellence Report

```
## Excellence Review: [deck-name]

### Overall Score: XX/100

| Perspective | Score | Key Finding |
|-------------|-------|-------------|
| Content | XX/100 | ... |
| Design | XX/100 | ... |
| Audience | XX/100 | ... |

### Critical Issues (must fix)
1. [Content] ...
2. [Design] ...

### Strengths (preserve)
1. ...
2. ...

### Recommended Improvements
1. [Content] ...
2. [Design] ...
3. [Audience] ...
```

---

## Action: `devils-advocate`

Challenge assumptions and find weaknesses. Especially useful for pre-defense or critical review.

### Challenge Questions

**Assumptions:**
- What assumption does this work rely on that the audience might question?
- Where is the weakest link in the argument chain?
- What would a skeptical reviewer say?

**Clarity:**
- Where might the audience get lost?
- What is the most confusing part of the presentation?
- Is there a slide where the message is unclear?

**Completeness:**
- What did you choose not to include that might be expected?
- Are there alternative interpretations of your results?
- What is the most likely tough question from the audience?

**Impact:**
- Does the contribution justify the audience's time?
- Is the improvement over prior work clearly demonstrated?
- What is the one-sentence takeaway — and is it on the slides?

### Report Format

```
## Devil's Advocate Review: [deck-name]

### Top 3 Vulnerabilities
1. [HIGH] Slide 5: Assumption X is stated without justification → audience may challenge
2. [MEDIUM] Slide 9: Alternative Y is not discussed → appears selective
3. [LOW] Slide 12: Result improvement is marginal (0.3%) → needs better framing

### Likely Audience Questions
1. "Why not compare with Method Z?"
2. "How sensitive is this to hyperparameter α?"
3. "What happens when assumption X fails?"

### Recommended Preparations
1. Add backup slide addressing Method Z comparison
2. Add backup slide with sensitivity analysis for α
3. Strengthen slide 5 with brief justification for assumption X
```

---

## Integration with Our Tools

| Tool | Action | Usage |
|------|--------|-------|
| `check_layout.py` | `audit` | DGV metrics, U/B/G/AR per slide |
| `layout_optimizer.py` | `audit` | Re-suggest layouts for problematic slides |
| `build_clean.ps1` / `build.sh` | All | Verify compilation before review |
| `pdftoppm` | `excellence`, `audit` | Generate PNGs for visual inspection |

## Cross-References

| Need | Skill |
|------|-------|
| Create new deck from scratch | [autobeamer-create](../autobeamer-create/SKILL.md) |
| Layout optimization, DGV grammar | [autobeamer-layout](../autobeamer-layout/SKILL.md) |
| Build errors, compilation | [autobeamer-build](../autobeamer-build/SKILL.md) |
| TikZ quality, patterns | [autobeamer-tikz](../autobeamer-tikz/SKILL.md) |
| Automated validation, visual check | [autobeamer-validate](../autobeamer-validate/SKILL.md) |
