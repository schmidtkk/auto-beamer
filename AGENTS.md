# Beamer Deck Auto — Agent Guidelines

## If You Are an AI Agent

This repo contains a **three-tier Beamer template library** and **layout optimization tools** for XeLaTeX academic slides.

### Before You Start

1. **Check current project state** — read `CLAUDE.md` for project context
2. **For layout questions** — use `skills/beamer-layout/SKILL.md`
3. **For new slides** — run `python tools/layout_optimizer.py suggest --img W:H --cards N`
4. **For overflow issues** — run `python tools/check_layout.py deck.tex build/deck.log --advise`

### Tool Reference

| Tool | When to Use |
|------|-------------|
| `layout_optimizer.py` | Choosing layout template, generating LaTeX skeleton |
| `check_layout.py` | Auditing slide density, column balance, grammar violations |
| `auto_crop.py` | Removing white margins from embedded images |
| `build_clean.ps1` | Compiling deck (supports parameterized builds) |

### Key Constraints

- **Never** use `2*#1\textwidth` in `\dimexpr` — use `#1\textwidth-#1\textwidth` instead
- **Always** wrap `\@ifundefined` with `\makeatletter`/`\makeatother` in `\input`'d files
- **Always** use `\providecommand` in layout/component files to prevent duplicates
- **Hardcode** column heights when inside `\budgetwideimg` or `[shrink=N]` frames

---

## Hard Rules (Non-Negotiable)

These rules apply to ALL Beamer work in this repo. Violations must be fixed before delivery.

### Content Rules

1. **No overlays** — never use `\pause`, `\onslide`, `\only`, `\uncover`. Use multiple slides for progressive builds, color emphasis for attention.
2. **Max 3 colored boxes per slide** — `bluecard`, `eqbox`, `greencard`, `alertcard`, `goldcall` combined. More dilutes emphasis.
3. **Motivation before formalism** — every concept starts with "Why?" before "What?".
4. **Worked example within 2 slides** of every definition.
5. **Telegraphic style** — keyword phrases, not full sentences. Slides are speaker prompts, not manuscripts.
6. **Every slide earns its place** — each slide must contain at least one substantive element (formula, diagram, table, theorem, or algorithm). A slide with only 3 short bullets must be merged or enriched.

### Technical Rules

7. **XeLaTeX only** — never pdflatex. Use `xelatex -interaction=nonstopmode`.
8. **Beamer .tex is the single source of truth** — TikZ diagrams, content, notation all originate here.
9. **Verify after every task** — compile, check warnings, open PDF.
10. **No `\tiny`** — never use `\tiny` for any user-facing content.
11. **Box-interior overflow guard** — boxes add internal padding (~15% less width, ~12-16pt extra height). Limit box content to **one display equation OR 2-3 bullet items**. Beamer suppresses overfull warnings inside blocks — always visually verify.
12. **Columns layout** — use `\begin{columns}[T]` + `\column{W\textwidth}`. Never nest columns. Always top-align.

### Structural Rules

13. **References slide** — second-to-last slide (before Thank You) must be a **References** slide.
14. **Color and contrast** — text-background contrast ≥ 4.5:1 (WCAG AA). Limit palette to 3-5 colors. Never red+green binary contrasts.
15. **Backup slides** — after Thank You, include 3-5 backup slides for anticipated questions. Use `\appendix` before backup section. Backup slides do NOT count toward timing.

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
|---------------|-----------|--------|
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

### How to Invoke a Skill

1. Read the skill's `SKILL.md` for detailed instructions
2. Follow the phase/action steps precisely
3. Cross-reference other skills when the workflow spans concerns
4. Always compile and verify after making changes
