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

# Beamer Deck Auto — Project Context

**Project:** XeLaTeX Beamer Template Library + Layout Optimization Tools  
**Architecture:** Three-tier (Theme → Layout → Component)  
**Build:** XeLaTeX + Metropolis theme + xeCJK  
**Entry Point:** `\usepackage[<theme>]{template-lib}`  
**Build Scripts:** `build_clean.ps1` (Windows), `build.sh` (macOS/Linux)

---

## Three-Tier Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  TIER 1: THEMES (Color + Typography)                        │
│  ├─ academic    Navy #1a3a6b + Brick #b8321a               │
│  ├─ teal        Teal #00796b + Amber #e65100               │
│  ├─ dark        Dark mode, Catppuccin-like                 │
│  ├─ navygold    Navy #1a3a6b + Gold #c9a23a                │
│  └─ minimal     Charcoal #2d2d2d + Silver #6b6b6b          │
├─────────────────────────────────────────────────────────────┤
│  TIER 2: LAYOUTS (Page Structure)                           │
│  ├─ text        Pure text flow                              │
│  ├─ 1img        Single image: left/right/top/bottom         │
│  ├─ 2img        Two images: side-by-side, labeled           │
│  ├─ 3img        Three images: grid, asymmetric              │
│  ├─ eq          Equation-focused: single, compare, deriv    │
│  ├─ table       Table: full-width, side-text                │
│  ├─ imgtop      Image-top with auto-height bottom content   │
│  └─ twocol      Two-column text: equal, divider, pro/con    │
├─────────────────────────────────────────────────────────────┤
│  TIER 3: COMPONENTS (Reusable Blocks)                       │
│  ├─ Title       \TLtitlestandard, \TLtitlecenter, \TLsection│
│  ├─ Blocks      \TLinfoblock, \TLalertblock, \TLresultblock │
│  ├─ Figures     \TLautoimg, \TLimgcap, \TLsubfig           │
│  ├─ Tables      \TLtable, \TLthead, \TLthl                 │
│  ├─ Inline      \TLpos, \TLneg, \TLhl, \TLmuted, \TLterm   │
│  └─ Takeaway    \TLtakeaway                                  │
└─────────────────────────────────────────────────────────────┘
```

### Usage

```latex
\documentclass[aspectratio=169,10pt]{beamer}
\usepackage[teal]{template-lib}  % or academic, dark, navygold, minimal
\uselayout{1img}                 % load specific layout(s)
\uselayout{eq}

\TLsetfoot{Author · Conference 2025}

\begin{document}
\TLtitlestandard[teaser.png]{Title}{Subtitle}{Author}{Institute}{Date}

\begin{frame}{Single Image Layout}
  \TLoneimgleft{image.png}{
    \begin{itemize}
      \item Point 1
      \item Point 2
    \end{itemize}
  }
\end{frame}
\end{document}
```

---

## Color Token System (11 TL-Prefixed Tokens)

All themes define these 11 tokens. Components reference tokens, never hardcode colors.

| Token | Role | Example (academic) |
|-------|------|-------------------|
| `TLprimary` | Brand primary | Navy #1a3a6b |
| `TLprimaryDark` | Title bg, emphasis | Dark navy #0d1f3e |
| `TLprimaryLight` | Subtle accents | Light navy #c8d8ee |
| `TLprimaryTint` | Block backgrounds | Very light #e8eff8 |
| `TLaccent` | Callouts, alerts | Brick red #b8321a |
| `TLaccentLight` | Highlight backgrounds | Light brick #fbe8e3 |
| `TLink` | Body text | Near black #1a1a2e |
| `TLinkSoft` | Secondary text, captions | Soft gray #5a5a7e |
| `TLsurface` | Canvas off-white | #f7f8fb |
| `TLpos` | Positive/green | #2E7D32 |
| `TLneg` | Negative/red | #C62828 |

Plus 2 semantic aliases per theme: `TLcanvas` (slide bg), `TLblockbody` (block interior).

---

## Component Reference

### Block Components (`comp-block.sty`)

| Command | Purpose | Colors |
|---------|---------|--------|
| `\TLinfoblock{title}{content}` | Primary info block | `TLprimary` frame + `TLprimaryTint` bg |
| `\TLalertblock[title]{content}` | Alert / warning | `TLaccent` frame + `TLaccentLight` bg |
| `\TLresultblock{title}{content}` | Positive result | `TLpos` frame + `TLpos!10` bg |
| `\TLwarnblock{title}{content}` | Warning / limitation | `TLneg` frame + `TLneg!8` bg |
| `\TLtakeaway{content}` | Key takeaway inline | `TLaccentLight` bg, full width |
| `\TLterm{text}` | Inline term highlight | `TLaccent` bold |

### Semantic Inline (`comp-block.sty`)

| Command | Purpose | Example |
|---------|---------|---------|
| `\TLpos{text}` | Positive emphasis (green bold) | `\TLpos{+2.3 dB}` |
| `\TLneg{text}` | Negative emphasis (red bold) | `\TLneg{−15\%}` |
| `\TLhl{text}` | Highlight background | `\TLhl{key result}` |
| `\TLmuted{text}` | De-emphasized (gray) | `\TLmuted{optional}` |

### Figure Components (`comp-fig.sty`)

| Command | Purpose |
|---------|---------|
| `\TLautoimg[opts]{file}` | Auto-scale to column width, cap at 72% frame height |
| `\TLimgcap[opts]{file}{caption}` | Image with caption below |
| `\TLsubfig[width]{img1}{img2}{caption}` | Side-by-side images |
| `\TLtable{cols}` | Environment: centered, small, booktabs-ready |
| `\TLthead` | Styled header row (primary bg, white text) |
| `\TLthl` | Row highlight (primary tint bg) |

### Title Components (`comp-title.sty`)

| Command | Purpose |
|---------|---------|
| `\TLtitlestandard[img]{title}{sub}{author}{inst}{date}` | Left text, right image |
| `\TLtitlecenter{title}{sub}{author}{date}` | Centered, no image |
| `\TLsection{Title}` | Section divider slide |

### Problem-Sheet Components (`comp-exercise.sty`)

For self-study problem sheets (see the **autobeamer-problem-sheet** skill). One unified
difficulty convention; theme-agnostic.

| Command | Purpose |
|---------|---------|
| `\TLdiff{1\|2\|3}` | Difficulty stars ⭐ calc / ⭐⭐ verify / ⭐⭐⭐ insight (`\hfill\TLdiff{n}` in title) |
| `\TLprobtitle{N}{name}{level}` | Problem frame title: `习题 N · name  ★★` |
| `\TLsubq{a}` | Sub-question label `(a)` |
| `TLhints` env + `\TLhint{…}` | Auto-numbered weak→strong 提示 1/2/3 |
| `\TLconcept{term}{formal}{直觉}` | Concept note (formal + intuition gloss) |
| `\TLmisconception{…}` | 常见误区 warning callout |
| `\TLsoltitle{N}{name}` · `\TLqed` | `\appendix` answer-key frame title · QED box |
| `\TLanswerkeynote` · `\TLsrcnote{…}` | Struggle-first reminder · source trace |

### Themes (2026-06 update)

13 palettes via `\usepackage[<theme>]{template-lib}`. **Default light = `slatecoral`**
(Slate + Coral, auto-selects the **Moloch** chrome); **default dark = `rosepine`**.
New light: `slatecoral plum claret terracotta forestbrass`. New dark: `rosepine
catppuccin midnightamber`. Legacy: `academic teal dark navygold minimal`. Chrome is an
orthogonal option: `moloch` (de-filled title + accent rule) vs `metropolis` (filled bar),
e.g. `[claret,moloch]`. See `design/theme-gallery.html`.

---

## Legacy vs. New Command Mapping

Old `personal-deck/` commands (CvG-Diff era) → New `template-lib` commands:

| Old (config.tex) | New (template-lib) | Notes |
|------------------|-------------------|-------|
| `bluecard{title}` | `\TLinfoblock{title}{...}` | Primary info block |
| `goldcall` | `\TLalertblock{title}{...}` or `\TLtakeaway{...}` | Alert / takeaway |
| `eqbox{title}` | `\begin{tcolorbox}[title=...]` or plain math | Equation box |
| `greencard{title}` | `\TLresultblock{title}{...}` | Positive result |
| `alertcard{title}` | `\TLwarnblock{title}{...}` | Warning |
| `\deltapos{+X}` | `\TLpos{+X}` | Green bold delta |
| `\deltaneg{−X}` | `\TLneg{−X}` | Red bold delta |
| `\autoimg{file}` | `\TLautoimg{file}` | Auto-scale image |
| `\budgetwideimg` | `\TLimgtop` (in `layout-imgtop.sty`) | Image-top layout |
| `\scaleeq{math}` | `\resizebox{\linewidth}{!}{$...$}` | Scale equation |

**Rule:** New decks should use `template-lib` commands. Legacy `personal-deck/` files retain old commands for backward compatibility.

---

## Column Height Alignment Rule

### When `equal height group` Works vs. Hardcode

| Context | `equal height group` | Action |
|---------|---------------------|--------|
| Standalone frame, no shrink | ✅ Works after 2 passes | Can use group OR hardcode |
| Frame with `[shrink=N]` | ❌ Fails | **Must hardcode** |
| Inside `\sbox` (custom wrappers) | ❌ Fails | **Must hardcode** |

### Why `equal height group` Fails in Some Contexts

1. **`\sbox` context**: tcolorbox writes height info to `.aux` at shipout time, but `\sbox` prevents shipout → no height recorded → group fails.
2. **`[shrink=N]` frames**: Beamer's shrink mechanism rescales the entire frame after typesetting, but `equal height group` heights are computed pre-shrink → mismatch.

### Hardcoding Procedure (always use this)

1. Add `equal height group=TMP` to both boxes (temporary, for measurement only)
2. Build 2 passes: `xelatex ...` × 2
3. Read height: `Select-String "TMP" build\deck.aux`
4. Replace with `height=XX.XXXXXpt,valign=top` on BOTH boxes
5. Rebuild and verify

---

## File Locations

| File | Path | Purpose |
|------|------|---------|
| Template library entry | `template-lib/template-lib.sty` | Master package, theme selection |
| Themes | `template-lib/themes/theme-*.sty` | 5 color palettes + base boilerplate |
| Layouts | `template-lib/layouts/layout-*.sty` | 8 page structure patterns |
| Components | `template-lib/components/comp-*.sty` | Blocks, figures, titles |
| Font config | `template-lib/font-config.sty` | Cross-platform CJK auto-detection |
| Catalog | `template-lib/docs/CATALOG.md` | Full API reference with examples |
| Legacy config | `personal-deck/config.tex` | Old CvG-Diff box macros (backward compat) |
| Legacy deck | `personal-deck/cvgdiff-beamer.tex` | Example real-world deck |
| Build script (Win) | `build_clean.ps1` | PowerShell build wrapper |
| Build script (Unix) | `build.sh` | Bash build wrapper |

---

## Build Commands

```powershell
# Windows — compile single deck
xelatex -interaction=nonstopmode -output-directory=build deck.tex

# Or use the wrapper
.\build_clean.ps1              # default: compile all .tex
.\build_clean.ps1 deckname    # compile specific deck

# macOS / Linux
./build.sh deckname
```

Run **twice** when using `equal height group` (first pass writes .aux, second pass reads it).

---

## Writing Style Guide

### Two Modes: Presentation Deck vs. Mentor Deck

| Aspect | Presentation Deck | Mentor Deck (self-study) |
|--------|------------------|--------------------------|
| **Audience** | Live listeners | Solo reader |
| **Density** | Sparse, high impact | Dense, comprehensive |
| **Style** | Telegraphic, keywords | Complete sentences, explanatory |
| **Examples** | Minimal (1 per concept) | Extensive (2-3 per concept, worked) |
| **Exercises** | None | ≥3 per chapter, with hints |
| **Proofs** | Sketch only (≤3 bullets) | **Full proofs**, every step shown (not "sketched") |
| **Takeaways** | 1 per slide | Summary + "check your understanding" |

### Telegraphic Style (Presentation Mode)

Slides are **speaker prompts**, not manuscripts:
- Use keyword phrases, not full sentences
- Every slide must have a clear **takeaway**
- No conversational hedging ("we might consider", "it could be argued")
- Use `\TLterm{}` or `\textbf{}` for key terms on first introduction

### Mentor Deck Style (Self-Study Mode)

- **Complete explanations**: reader has no speaker to fill gaps
- **Worked examples**: concrete numbers, step-by-step, reproducible
- **Progressive difficulty**: 1D/discrete first, then continuous/high-D
- **Common pitfalls**: use `\TLwarnblock` for mistakes beginners make
- **Exercises**: ⭐ calculation → ⭐⭐ verification → ⭐⭐⭐ insight
- **Hints**: 2-3 per exercise, answers in backup slides
- **Page count is irrelevant**: completeness and pedagogical clarity are the only metrics; "i don't care if you use 100 or 200 pages"
- **Every equation gets its own frame** (or a shared frame with its derivation); never cram multiple unrelated equations on one slide
- **Every assumption explicitly stated** with physical/mathematical intuition; never say "obviously" or "it is well known"
- **Proof steps shown explicitly**, not "sketched" — even if the source text says "proofs will only be sketched"
- **Bibliographical notes are a full section**, 4–5+ frames, not an optional afterthought
- **Content must be MORE detailed than the source**, not less; the deck supplements background the source assumes

### Formula + Analysis Interleave

Never present a bare equation without context:
1. **Motivation first**: 1-line informal statement before formalism
2. **Equation**: displayed math in `tcolorbox` or standalone
3. **Analysis**: 1-2 bullet points interpreting the result

---

## Slide Design Patterns

### Definition Slide

```
[Motivation: 1-line informal "Why we need this"]
[Formal definition in \TLinfoblock or displayed math]
[Worked example within 2 slides]
```

### Algorithm / Method Slide

```
[Problem statement (1-2 lines)]
[Algorithm steps — max 10 lines of pseudocode]
[Highlight critical step with \TLterm or color]
[Input/output clearly labeled]
```

### Comparison Slide

```
[Side-by-side table or columns: prior vs. this work]
[1-2 lines highlighting the key difference]
```

### Theorem / Proof Slide

- **Never** cram theorem + proof on one slide
- Theorem slide: informal framing → formal statement → key implication
- Proof on **next** slide; for long proofs, show proof sketch + full proof in backup
- Use `\begin{proof}[Proof sketch]` for abbreviated proofs

### Exercise Slide (Mentor Deck)

```
[Problem statement, clearly labeled Exercise N.M]
[Difficulty: ⭐ / ⭐⭐ / ⭐⭐⭐]
[Hints (2-3 bullets, progressively revealing)]
[\TLtakeaway{Key concept tested}]
```

### Cross-Referencing Between Slides

- Label key slides: `\label{slide:construction}` inside frame
- Reference: `see Slide~\ref{slide:construction}` or `\hyperlink{...}{\beamerbutton{...}}`
- In backup slides, always hyperlink back to the motivating main slide

---

## Content Density Rules

### Upper Bounds (per slide)

| Element | Max | Action if Exceeded |
|---------|-----|--------------------|
| Bullet points | 7 | Split slide |
| Displayed equations | 2 | Split slide |
| New symbols introduced | 5 | Introduce over multiple slides |
| Colored blocks (`\TLinfoblock`/etc.) combined | 3 | Redistribute content |

### Lower Bounds (per slide)

- Every slide MUST contain ≥1 **substantive element**: formula, diagram, table, theorem, or algorithm
- A slide with only ≤3 short text-only bullets is **too sparse** — merge or enrich
- Pure text-only bullet slides should be ≤30% of the total deck

### Density Self-Check

After each batch of 5-10 slides:
1. Count slides with zero formulas/diagrams/tables → flag if >30% of batch
2. Count slides with ≤3 short items and no math → candidates for merging

---

## Table Best Practices

- **Always center**: wrap standalone tables in `\begin{center}...\end{center}`
- **Spacing after title**: insert `\vspace{4pt}` between frame title and first `\toprule`
- **Always use `booktabs`**: `\toprule`, `\midrule`, `\bottomrule` — never vertical lines (`|`)
- **Column alignment**: numbers → `r`, text → `l`, short labels → `c`
- **Max dimensions**: 6-7 columns, 8-10 rows per slide; more → paginate
- **Pagination rules**: repeat full header on each page, append "(cont'd)" to frame title
- **Highlight key cells**: `\TLthl` or `\textbf{}` — draw the eye to the result
- **For comparison tables**: bold the best result in each row/column
- **`\resizebox` only as last resort** — prefer reducing columns/rows first

---

## Quality Rubric

Start at **100**. Deduct for issues:

| Severity | Issue | Deduction |
|----------|-------|-----------|
| **Critical** | Compilation failure | −100 |
| **Critical** | Equation overflow (slide or box-interior) | −20 |
| **Critical** | TikZ diagram overflows slide boundary | −15 per diagram |
| **Critical** | Undefined control sequence / citation | −15 |
| **Critical** | Proof gap (mentor/passive-study): unstated goal, unjustified step ("thus/可验证/易证/one verifies"), term used before defined, easy half of a bound dropped, or sketch-not-full | −15 per proof |
| **Critical** | 科学性: scientific error in a displayed relation — wrong sign, flipped inequality, off-by-one index, wrong quantifier, dimensional mismatch (verify EVERY relation, don't skim) | −15 each |
| **Critical** | 流畅性: foreign-language prose leakage (e.g. an English sentence in a Chinese deck; spec text pasted verbatim). English terms & `$...$` exempt | −10 each |
| **Critical** | 目的不明 (mentor/passive-study): a gap-free but purpose-unclear definition/proof; result with no question/idea/why; multi-frame proof lacking map+recall | −15 each |
| **Critical** | Overfull hbox > 10pt | −10 |
| **Major** | Content overflow inside colored box | −10 per box |
| **Major** | Sparse slide (≤3 items, no math/diagram) | −5 per slide |
| **Major** | TikZ label overlap | −5 |
| **Major** | Missing references slide | −5 |
| **Major** | Table not centered | −3 per table |
| **Major** | Table `\toprule` merges with title bar | −5 per slide |
| **Major** | Notation inconsistency | −3 |
| **Major** | 准确度/优雅性: mistranslation, translation-ese, or clunky/redundant prose | −3 each |
| **Major** | `\resizebox`/`\tiny` shrinking body prose below `\scriptsize` to force fit (split instead) | −3 each |
| **Minor** | `\vspace` overuse (>3 per slide) | −1 |
| **Minor** | Font size reduction (`\footnotesize`) | −1 per slide |

**Thresholds:**
- **≥ 90**: Ready to deliver
- **80–89**: Acceptable with caveats
- **< 80**: Must fix before delivery

---

## User Preferences

**CRITICAL**: Before any design or planning task, read `memories/repo/user-preferences.md` and `memories/MEMORY_INDEX.md`.

See `memories/repo/user-preferences.md` for:
- Theme preference (teal over academic)
- Box philosophy (plain text first, boxes as exceptions)
- Mentor deck standards (worked examples, exercises, self-contained)
- Reader cognitive baseline (what math background to assume)
- Measure theory bridging strategy (how to explain technical terms)
- Domain-specific rules (e.g., OT Chapter 1 supplement ladder)

See `memories/MEMORY_INDEX.md` for:
- Keyword lookup table to quickly locate relevant preference sections
- Agent workflow phases (Plan → Execute → Review)
- Priority levels for different preference categories
