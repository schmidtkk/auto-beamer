---
name: autobeamer-review
description: "Review, audit, and quality-check existing Beamer decks: rubric scoring, DGV layout audit, pedagogy validation, and multi-perspective excellence review."
when_to_use: |
  Triggers on: "review slides", "audit deck", "check quality", "pedagogy review",
  "proofread", "devils advocate", "excellence review", "find issues in slides".
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
| `naive-reader` | Confused-student adversarial simulation: ceiling-bounded personas read in character and report where a *beginner* gets lost | Accessibility decks for cross-disciplinary / mixed-background readers; "students can't follow the proofs"; any time the lead model is too expert to feel beginner confusion |

## Mode-Specific Review Routing

Before any content or pedagogy judgment, identify the deck mode and load the matching rubric:

| Mode | Review rubric |
|------|---------------|
| `passive-study` | [references/rubrics/passive-study-review.md](references/rubrics/passive-study-review.md) |
| `active-socratic` | [references/rubrics/active-socratic-review.md](references/rubrics/active-socratic-review.md) |
| `academic-presentation` | [references/rubrics/academic-presentation-review.md](references/rubrics/academic-presentation-review.md) |

If the deck still uses the old labels, map "Mentor/self-study" to `passive-study` and "Presentation/live talk" to `academic-presentation`. Do not score an `active-socratic` deck as failed merely because it withholds exposition; score whether it asks the right questions and gives adequate attempt gates.

### Proof-rigor is a P0 gate for proof-bearing decks (do not skip)

For any `passive-study` deck (or proof-bearing `active-socratic`), **gap-free proofs are a P0 acceptance gate, not a nicety — a single gap fails the review.** A proof is *gapped* if it: omits its goal; uses "thus / hence / clearly / 可验证 / 易证 / one verifies / 类似地" in place of a shown step; uses a term before it is defined (e.g. "链/chain", "c-次微分", "normal cone"); invokes a named result (Farkas/KKT/IFT/Rockafellar/…) without its one-line statement + why-it-applies on-frame; compresses several logical moves into one displayed line; silently drops the *easy* half of a bound/equivalence; or sketches what the source proves in full.

Because the lead model is usually too expert to *feel* these gaps, **`naive-reader` is MANDATORY (not optional) for these decks** — run it with persona **P2 (the gap-free-proof arbiter)** alongside a floor reader, and treat any in-target-zone "jump I couldn't follow" or "undefined-for-me term" as **P0** (must-fix before sign-off). The `excellence` pass and the create-loop quality score apply the matching −15 (CRITICAL) proof-gap deductions; do not sign off while any remain. Fix by **splitting into more frames** and adding the missing micro-steps — never by deleting the proof.

---

## Action: `proofread`

Structured proofreading with categorized report.

### Categories

**1. Language & Expression quality (语言与表达：流畅性 · 准确度 · 优雅性 · 科学性)**

This category is owned by the canonical
[language-quality-gate.md](references/language-quality-gate.md) — read it; do not
re-derive the axes here. **Run the mechanical half first**, then judge the rest:

```bash
python tools/lang_lint.py lint <deck>.tex --mode <mode>
```

`lang_lint.py` deterministically catches the **HARD GATE — foreign-language prose
leakage** (zero English sentences in a Chinese deck; terms & `$...$` exempt),
tier-1 AI-flavor fillers, proof-hedges (`显然/易证/不难/类似地` — CRITICAL in
passive-study), and connector clusters. Then **you** judge the axes the script
cannot: **准确度** (mistranslation / imprecise wording), **优雅性** (clunky,
redundant, translation-ese prose), and **科学性** (read EVERY displayed relation —
sign, direction, indices, quantifiers, dimensions — do not skim; a copied sign
slip or flipped inequality is CRITICAL). For English decks, also apply
subject-verb agreement, articles, tense, parallel structure, academic register.

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

**6. Image provenance**
- Confirm source-document-first was followed when a PDF or source document was provided.
- Check that extracted source figures have page/source notes.
- Check that external images are local files, license-compatible, and attributed.
- Flag build-time hotlinks, CDN URLs, and unattributed screenshots as HIGH issues.

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

#### Image provenance
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
| GV-1 | Loose text without structure | Keep as plain body text/bullets, or use `\TLtakeaway` only for a true callout |
| GV-2 | Callout block inside `columns` | Move the callout below `\end{columns}` so it spans the frame |
| GV-3 | Multiple info/result blocks in one column | Split frame or convert to text (max 3 colored boxes/slide) |
| GV-4 | Wide image (AR>1.4) in SIDE layout | Switch to image-top (`\TLimgtop` or equivalent template-lib layout). SIDE is only balanced at AR ≤ 1.4 per `layout_optimizer.py`. |

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
- Slide 12: GV-2 (callout inside columns) → move outside

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

- **Slide count vs. duration**: use the canonical table in [autobeamer-validate](../autobeamer-validate/SKILL.md) (§2a) — e.g., 20 min → 14–20 slides. Do not use a separate per-minute formula here; it drifts from the table.
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
- Slide count: 15 (target for 20min: 14–20) ✅
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

Apply 3 distinct review perspectives. By default you adopt each perspective in
turn within one pass; only spin up parallel subagents (via the `Agent` tool) if
the user explicitly asks for a multi-agent review. Report all three regardless.

1. **Content Expert** — Technical accuracy, completeness, rigor
2. **Design Reviewer** — Visual quality, layout, readability, contrast
3. **Audience Advocate** — Clarity, pacing, engagement, accessibility

### Perspective 1: Content Expert

- Are all claims accurate and supported?
- **Scientific correctness, per relation.** Read every displayed equation/inequality and verify its direction, sign, indices, and quantifiers — do not skim. A flipped inequality, a sign slip, or an off-by-one index is a CRITICAL content defect even if it compiles. (Machine-generated or copied derivations are the usual source.)
- **Language purity & expression.** Run `python tools/lang_lint.py lint <deck>.tex --mode <mode>` for the mechanical pass (foreign-prose leakage, fillers, proof-hedges), then judge 准确度/优雅性/科学性. Full definitions: [language-quality-gate.md](references/language-quality-gate.md).
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

## Action: `naive-reader`

Confused-student adversarial simulation. Use when the deck claims cross-disciplinary
accessibility, when readers report "the proofs jump / I can't follow," or any time the
reviewer is **too expert to feel a beginner's confusion** — which is always, for a strong
model. The QA and pedagogy actions check whether the deck is *correct and well-structured*;
this action checks whether a reader with a **bounded knowledge ceiling** can actually
follow it.

> **Also available as the standalone command [`/naive-reader`](../naive-reader/SKILL.md).**
> Same capability and shared persona library; invoke `/naive-reader [deck] [personas]` directly,
> or run it here as part of a broader review. The prescriptive counterpart that *calibrates*
> scaffolding + per-slide cognitive load to a profile is [autobeamer-calibrate](../autobeamer-calibrate/SKILL.md).

### The principle

A brilliant model silently fills every gap from its own knowledge, so it certifies as
"clear" proofs a beginner cannot follow. To get the missing information, simulate readers
with a **hard knowledge ceiling** and an **anti-cheat rule**: a persona is forbidden from
using knowledge above its ceiling, and if it catches itself following a step only because
it secretly knows more, it flags that step as a wall. A beginner's confusion is data the
lead model does not have; this action manufactures it.

Full persona roster, anti-cheat rule, target-zone logic, and report schemas:
[references/naive-reader-personas.md](references/naive-reader-personas.md). **Read that
file before running.**

### Procedure

1. **Identify the deck's claimed audience** and pick ≥3 personas from the roster (P1 AI
   engineer · P2 undergraduate · P3 high-school · P4 biomed · P5 humanities · P6
   cross-field grad). Always include **P2** (the gap-free-proof arbiter) and one **floor
   reader** (P3 or P5) to test the zero-prereq on-ramp.
2. **Assign each persona a target zone** — the frames the deck *promises* this reader will
   understand. Confusion *inside* the zone is a defect; outside-and-warned is expected.
3. **Prepare the deck** for reading: flatten if it `\input`s sections, and extract the
   **macro legend** from the preamble (e.g. `\grad`→∇, `\T`→transpose, `\xs`→x*) so
   personas read the math as rendered, not as LaTeX noise. (High-fidelity option: 2-pass
   build → read PDF page images.)
4. **Spawn one subagent per persona, in parallel** (single message, multiple `Agent`
   calls). Each gets: its persona block verbatim, the anti-cheat rule, its target zone, the
   deck text + macro legend, and the per-persona report schema. Personas never see each
   other's output. Use `general-purpose` agents.
5. **Synthesize** into the confusion heatmap + ranked defects (schema in the reference),
   sorting confusion into: real defects (fix), gating defects (cheap signpost fix), and
   expected confusion (leave). The ranked worklist feeds the gap-fill.

### Health check (did the simulation work?)

- If every persona "understood everything," the run is **broken** — a subagent cheated.
  A healthy run has floor readers (P3/P5) stopping early on proof frames; the signal is
  *in-target-zone* failures, not raw failure count.
- Findings must be **frame-specific and token-specific** ("Frame 18: `Z` spanning the null
  space was never defined"), not vague ("proofs are hard"). Re-prompt subagents that return
  mush.
- A legitimately *hard* step is not a defect; an *unjustified* step is. P2 arbitrates the
  difference: "skipped a step" ≠ "deep idea."

### Relation to other actions

`pedagogy` judges structure against 13 patterns from the expert's chair; `naive-reader`
judges *felt* comprehension from the beginner's chair. Run `naive-reader` to find the
walls, then `pedagogy`/gap-fill to fix them. They are complementary, not redundant.

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
| Confused-student simulation (standalone command) | [naive-reader](../naive-reader/SKILL.md) |
| Calibrate scaffolding + per-slide cognitive load to a reader profile | [autobeamer-calibrate](../autobeamer-calibrate/SKILL.md) |
