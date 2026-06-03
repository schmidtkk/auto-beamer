<!-- LIGHTMEM:GATEWAY:START -->
## Project Memory (LightMem)

Memory database: `.claude/lightmem/topics/`

When you start work on this repo:
- Read `.claude/lightmem/topics/mission.md` for project purpose
- Check `.claude/lightmem/topics/constraints/` for non-negotiables
- Check `.claude/lightmem/topics/decisions/` for ADR-style decisions
- See `.claude/lightmem/index.md` for the full topic list

When you make a durable decision, add or supersede an entry under `topics/decisions/`.
When you learn a constraint or gotcha, add to the matching topic.
Use `/lightmem:update` to be guided through this.

<!-- LIGHTMEM:GATEWAY:END -->

# Beamer Deck Auto — Agent Guidelines

## If You Are an AI Agent

This repo contains a **three-tier Beamer template library** and **layout optimization tools** for XeLaTeX academic slides.

### Before You Start

1. **Search memory index** — read `memories/MEMORY_INDEX.md` for keyword lookup
2. **Load relevant preferences** — read `memories/repo/user-preferences.md` (MANDATORY for design/plan tasks)
3. **Check current project state** — read `CLAUDE.md` for project context
4. **For layout questions** — use `skills/beamer-layout/SKILL.md`
5. **For new slides** — run `python tools/layout_optimizer.py suggest --img W:H --cards N`
6. **For overflow issues** — run `python tools/check_layout.py deck.tex build/deck.log --advise`

---

## Memory-Aware Agent Workflow

### Three-Phase Memory Injection

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   PLAN      │────→│  EXECUTE    │────→│   REVIEW    │
│  (计划)      │     │  (执行)      │     │  (审查)      │
└─────────────┘     └─────────────┘     └─────────────┘
      │                   │                   │
      ▼                   ▼                   ▼
  Read MEMORY_INDEX   Check CRITICAL      Verify compliance
  Read user-pref      preferences         Update session mem
  Incorporate into    before each edit
  plan
```

### Phase 1: Plan — Memory Search (MANDATORY)

**Rule**: Before generating any implementation plan, the agent MUST:

1. **Read `memories/MEMORY_INDEX.md`** — Search for keywords matching the user's request
2. **Read `memories/repo/user-preferences.md`** — Load all relevant preference sections
3. **Identify CRITICAL constraints** — Mark rules that cannot be violated:
   - Box philosophy: "plain text first, boxes as exceptions"
   - Content density: "mentor deck = dense, self-contained"
   - Theme: "teal over academic"
   - Any domain-specific rules (e.g., OT Chapter 1 supplement ladder)
4. **Incorporate into plan** — Reference specific preference sections in the plan

**Example plan snippet with memory integration:**
```markdown
## Plan: Redesign OT Chapter 1 Deck

### Constraints from user-preferences.md
- [Box Philosophy] Plain text first; use \TLinfoblock only for key theorems
- [Content Density] Mentor deck: dense, complete sentences, ≥3 exercises
- [Theme] Use teal theme
- [OT Chapter 1] Follow supplement ladder: coupling → measure → pushforward → OT

### Steps
1. ...
```

### Phase 2: Execute — Preference Guard

**Rule**: Before each file edit/create operation, verify:

- [ ] Does this violate any CRITICAL preference? (Block if yes)
- [ ] Does this match the established box philosophy?
- [ ] Does this match the content density standard?
- [ ] Does this use the correct theme?

### Phase 3: Review — Compliance Check

**Rule**: After completing changes, verify:

- [ ] All CRITICAL preferences are respected
- [ ] Consistent with existing codebase patterns
- [ ] Update session memory with decisions made

---

## Tool Reference

| Tool | When to Use | Example |
|------|-------------|---------|
| `layout_optimizer.py` | Choosing layout template, generating LaTeX skeleton | `python tools/layout_optimizer.py suggest --img 1716:1124 --cards 2` |
| `check_layout.py` | Auditing slide density, column balance, grammar violations | `python tools/check_layout.py deck.tex build/deck.log --advise` |
| `auto_crop.py` | Removing white margins from embedded images | `python tools/auto_crop.py fig.png --padding 8` |
| `test_themes.py` | Compile-test all 5 themes (+ optional layout stress test) | `python tools/test_themes.py` or `--layouts` for full 5×8 matrix |
| `paper_parser.py` | Extract text/figures/references from PDF papers | `python tools/paper_parser.py paper.pdf --output paper.json` |
| `build_clean.ps1` | Compiling deck (Windows, parameterized) | `.\build_clean.ps1 deckname` |
| `build.sh` | Compiling deck (macOS/Linux) | `./build.sh deckname` |

---

## Key Constraints

- **Never** use `2*#1\textwidth` in `\dimexpr` — use `#1\textwidth-#1\textwidth` instead
- **Always** wrap `\@ifundefined` with `\makeatletter`/`\makeatother` in `\input`'d files
- **Always** use `\providecommand` in layout/component files to prevent duplicates
- **Hardcode** column heights when inside `\sbox` contexts or `[shrink=N]` frames
- **New decks** use `template-lib` commands (`\TLinfoblock`, etc.); legacy decks use `config.tex`

---

## Hard Rules (Non-Negotiable)

These rules apply to ALL Beamer work in this repo. Violations must be fixed before delivery.

### Content Rules

1. **No overlays** — never use `\pause`, `\onslide`, `\only`, `\uncover`. Use multiple slides for progressive builds, color emphasis for attention.
2. **Max 3 colored boxes per slide** — `\TLinfoblock`, `\TLalertblock`, `\TLresultblock`, `\TLwarnblock`, `\TLtakeaway` combined. More dilutes emphasis.
3. **Motivation before formalism** — every concept starts with "Why?" before "What?".
4. **Worked example within 2 slides** of every definition.
5. **Telegraphic style** — keyword phrases, not full sentences. Slides are speaker prompts, not manuscripts. **Exception:** Mentor Deck mode (self-study) uses complete sentences and self-contained explanations.
6. **Every slide earns its place** — each slide must contain at least one substantive element (formula, diagram, table, theorem, or algorithm). A slide with only 3 short bullets must be merged or enriched.

### Technical Rules

7. **XeLaTeX only** — never pdflatex. Use `xelatex -interaction=nonstopmode`.
8. **Beamer .tex is the single source of truth** — TikZ diagrams, content, notation all originate here.
9. **Verify after every task** — compile, check warnings, open PDF.
10. **No `\tiny`** — never use `\tiny` for any user-facing content.
11. **Box-interior overflow guard** — boxes add internal padding (~15% less width, ~12-16pt extra height). Limit box content to **one display equation OR 2-3 bullet items**. Beamer suppresses overfull warnings inside blocks — **log grep is insufficient; run `visual-check` on every frame containing blocks.**
12. **Columns layout** — use `\begin{columns}[T]` + `\column{W\textwidth}`. Never nest columns. Always top-align.

### Structural Rules

13. **References slide** — second-to-last slide (before Thank You) must be a **References** slide.
14. **Color and contrast** — text-background contrast ≥ 4.5:1 (WCAG AA). Limit palette to 3-5 colors. Never red+green binary contrasts.
15. **Backup slides** — after Thank You, include 3-5 backup slides for anticipated questions. Use `\appendix` before backup section. Backup slides do NOT count toward timing.

### Mode Rules

16. **Deck mode must be explicitly set** — before creation, ask "Presentation (live talk) or Mentor (self-study)?". Mentor mode overrides Presentation-mode defaults (telegraphic style, duration limits, proof sketches). See `CLAUDE.md` for full mode comparison.
17. **Sparse slides are Critical issues** — any frame with <30% vertical fill, or containing only 1 block with no math/diagram/table/theorem, must be merged or enriched. Run `check_layout.py` to detect automatically.

---

## Skill Reference

| Skill | Purpose | Key Actions |
|-------|---------|-------------|
| **beamer-create** | Full deck creation pipeline | Material analysis → Interview → Structure → Draft → Figures → Quality loop |
| **beamer-review** | Content & pedagogy review | `proofread`, `audit`, `pedagogy`, `excellence`, `devil's-advocate` |
| **beamer-layout** | Layout optimization, DGV grammar | Theme → Draft → Optimize pipeline |
| **beamer-build** | Compilation & error fixing | XeLaTeX compilation, prerequisites, error troubleshooting |
| **beamer-tikz** | TikZ diagram quality | Accuracy rules, 6 patterns, iterative review |
| **beamer-validate** | Automated quantitative checks | `validate`, `visual-check`, `check` |

### Quick Dispatch

| User says... | Use skill | Action |
|--------------|-----------|--------|
| "Create a new deck" / "Make slides for..." | beamer-create | Full pipeline |
| "Proofread" / "Check for typos" | beamer-review | `proofread` |
| "Audit layout" / "Fix overflow" | beamer-review | `audit` |
| "Is the pedagogy sound?" | beamer-review | `pedagogy` |
| "Full quality check" | beamer-review | `excellence` |
| "Challenge my design" | beamer-review | `devil's-advocate` |
| "Choose a layout" / "DGV grammar" | beamer-layout | — |
| "Compile fails" / "Build error" | beamer-build | — |
| "Fix TikZ diagram" | beamer-tikz | — |
| "Validate" / "How many slides?" | beamer-validate | `validate` |
| "Visual check" / "Check the PDF" | beamer-validate | `visual-check` |
| "Full health check" | beamer-validate | `check` |
| **"Update memory" / "Remember this" / "Save preference"** | **memory** | **Write to `memories/repo/user-preferences.md`** |

### How to Invoke a Skill

1. **Read the skill's `SKILL.md`** for detailed instructions
2. **Search memory** — Before invoking, check `memories/MEMORY_INDEX.md` for relevant constraints
3. **Follow the phase/action steps** precisely
4. **Cross-reference other skills** when the workflow spans concerns
5. **Always compile and verify** after making changes

---

## Memory Update Protocol

### When to Update Memory

| Trigger | Action | File |
|---------|--------|------|
| User states a preference | Append to relevant section | `memories/repo/user-preferences.md` |
| New domain knowledge (e.g., OT Chapter 2) | Add new section | `memories/repo/user-preferences.md` |
| New keyword patterns identified | Update lookup table | `memories/MEMORY_INDEX.md` |
| Workflow improvement discovered | Update this file | `AGENTS.md` |

### How to Update `user-preferences.md`

1. Read existing file to understand structure
2. Append new preference under appropriate heading
3. Use consistent markdown formatting
4. Include rationale if non-obvious

### How to Update `MEMORY_INDEX.md`

1. Identify new keyword → memory mapping
2. Add row to Quick Lookup Table
3. Assign priority (P0/P1/P2)
4. Update Last Updated timestamp

---

## Mentor Deck Mode (Self-Study Slides)

When the user indicates they are building a **mentor deck** (self-study material, not a live presentation):

### Content Differences

| Aspect | Presentation | Mentor Deck |
|--------|-------------|-------------|
| Style | Telegraphic | Complete sentences |
| Examples | 1 per concept | 2-3 per concept, worked |
| Exercises | None | ≥3 per chapter, with hints |
| Proofs | Sketch only | Key idea + backup details |
| Density | Sparse | Dense, comprehensive |

### Mentor Deck Rules

1. **Self-contained** — never assume reader has external references
2. **Worked examples** — concrete numbers, step-by-step, reproducible
3. **Progressive difficulty** — 1D/discrete first, then continuous/high-D
4. **Exercises with hints** — 2-3 hints per exercise, answers in backup
5. **Common pitfalls** — use `\TLwarnblock` for beginner mistakes
6. **No "obviously" / "trivially"** — explain everything

See `memories/repo/user-preferences.md` for full mentor deck standards.
