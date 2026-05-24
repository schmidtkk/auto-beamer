# CvG-Diff Beamer Deck — Project Context

**Project:** CvG-Diff MICCAI 2025 XeLaTeX Beamer Deck  
**Theme:** Academic (navy + red, classic style)  
**Build:** XeLaTeX + Metropolis theme  
**Main source:** `cvgdiff-beamer.tex`  
**Config:** `config.tex` (box macros + theme palettes)  
**Build script:** `build_clean.ps1`

---

## Box Environments (from config.tex)

| Environment | Purpose | Colors |
|-------------|---------|--------|
| `bluecard{title}` | Primary info block | ThemePrimary frame + ThemeTint bg |
| `goldcall` | Alert / key takeaway | ThemeAccent frame + ThemeAccentLight bg |
| `eqbox{title}` | Equations / definitions | ThemePrimary!50 frame + ThemeSurface bg |
| `greencard{title}` | Positive result | PosGreen frame |
| `alertcard{title}` | Warning / limitation | NegRed frame |

All boxes accept optional `[...]` tcolorbox parameters before the title.

---

## Column Height Alignment Rule

### When `equal height group` Works vs. Hardcode

| Context | `equal height group` | Action |
|---------|---------------------|--------|
| Standalone frame, no shrink | ✅ Works after 2 passes | Can use group OR hardcode |
| Frame with `[shrink=N]` | ❌ Fails | **Must hardcode** |
| Inside `\budgetwideimg` / `\budgetwidecontent` | ❌ Fails (inside `\sbox`) | **Must hardcode** |

### Why `equal height group` Fails in Some Contexts

1. **`\sbox` context** (`\budgetwideimg`, `\budgetwidecontent`): tcolorbox writes height info to `.aux` at shipout time, but `\sbox` prevents shipout → no height recorded → group fails.
2. **`[shrink=N]` frames**: Beamer's shrink mechanism rescales the entire frame after typesetting, but `equal height group` heights are computed pre-shrink → mismatch.

### Hardcoding Procedure (always use this)

1. Add `equal height group=TMP` to both boxes (temporary, for measurement only)
2. Build 2 passes: `xelatex ...` × 2
3. Read height: `Select-String "TMP" build\cvgdiff-beamer.aux`
4. Replace with `height=XX.XXXXXpt,valign=top` on BOTH boxes
5. Rebuild and verify

---

## Height Hardcoding Record

| Frame | PDF Page | Context | Box A | Box B | Height Used |
|-------|----------|---------|-------|-------|-------------|
| S3 Radon/FBP | p3 | `[shrink=5]` frame | eqbox "Radon" | eqbox "FBP" | `67.42996pt` |
| S4 稀疏视图 | p4 | `\budgetwidecontent` | bluecard "动机" | bluecard "挑战" | `71.06035pt` |
| S6b 背景扩散 | p7 | `\budgetwideimg` | bluecard "核心思想" | bluecard "代表工作" | `71.40608pt` |
| S8 Cold Diffusion | p10 | Standalone, 2 rows | Row 1: eqbox+bluecard | Row 2: eqbox+bluecard | R1: `61.99364pt`, R2: `75.90117pt` |
| S14 SPDPS | p15 | `\budgetwideimg` | bluecard "Phase 1" | bluecard "Phase 2" | `54.25087pt` (measured, hardcode recommended) |
| S16b 消融解读 | p20 | Standalone frame | bluecard "18-view PSNR" | bluecard "物理解释" | `86.83221pt` |

### Active `equal height group` Entries (current build)

| Group | Frame | Boxes | Resolved Height |
|-------|-------|-------|-----------------|
| `S12top` | S12 EPCT 2/2 | eqbox "Restore Loss" ↔ bluecard "为什么有效？" | `61.43942pt` |
| `S12bot` | S12 EPCT 2/2 | eqbox "Compose Loss" ↔ bluecard "消融验证" | `62.71098pt` |
| `S13top` | S13 顺序采样 | bluecard "①语义错误" ↔ bluecard "核心观察" | `75.03171pt` |
| `S13bot` | S13 顺序采样 | bluecard "②NFE浪费" ↔ goldcall "SPDPS动机" | `70.18864pt` |
| `S14` | S14 SPDPS | bluecard "Phase 1" ↔ bluecard "Phase 2" | `54.25087pt` (inside `\sbox` — may need hardcode) |

---

## Layout Helpers

### `\budgetwideimg{caption}{bottom-block}{imagefile}`

Convenience wrapper for IMAGE_TOP layout:
- Image fills top, auto-capped by remaining height
- Caption below image
- Bottom block (cards, text) at frame bottom
- **Inside `\sbox`**: `equal height group` does NOT work → hardcode heights

### `\budgetwidecontent{top-visual}{caption}{bottom-block}`

General IMAGE_TOP helper for multi-image grids, tables, custom visuals.
- Use `\bbiAvailHt` as height cap in grids
- **Inside `\sbox`**: `equal height group` does NOT work → hardcode heights

### `\autoimg[opts]{file}`

Fill column width, cap at 76% frame height. Use inside columns.

### `\scaleeq{math}`

Scales a display equation to fit `\linewidth`. Use inside narrow columns.

---

## Custom Commands

| Command | Purpose |
|---------|---------|
| `\deltapos{+X dB}` | Green bold positive delta |
| `\deltaneg{$-$X dB}` | Red bold negative delta |
| `\cnum{①}` | CJK number in non-CJK font |
| `\thetaEMA` | `\theta^{\mathrm{EMA}}` shorthand |
| `\hlrow` | Highlight row color (ThemeLight) |

---

## File Locations

| File | Path |
|------|------|
| Main source | `cvgdiff-beamer.tex` |
| Box macros + theme | `config.tex` |
| Build script | `build_clean.ps1` |
| Assets | `slides_assets/` |
| Backup | `cvgdiff-beamer.tex.bak.20260520` |

---

## Build Command

```powershell
# From project root
xelatex -interaction=nonstopmode -output-directory=build cvgdiff-beamer.tex
```

Run **twice** when using `equal height group` (first pass writes .aux, second pass reads it).

---

## Writing Style Guide

### Telegraphic Style

Slides are **speaker prompts**, not manuscripts:
- Use keyword phrases, not full sentences
- Every slide must have a clear **takeaway** — the one thing the audience should remember
- No conversational hedging ("we might consider", "it could be argued")
- Use `\textbf{}` for key terms on first introduction

### Formula + Analysis Interleave

Never present a bare equation without context:
1. **Motivation first**: 1-line informal statement before formalism
2. **Equation**: displayed math in `eqbox` or standalone
3. **Analysis**: 1-2 bullet points interpreting the result

### Opening Strategies (choose one)

| Strategy | When to Use |
|----------|-------------|
| Surprising statistic | "90% of CT reconstructions suffer from..." |
| Provocative question | "Why do state-of-the-art methods still fail on..." |
| Real-world failure case | Show a failed reconstruction, then ask "What went wrong?" |
| Visual demonstration | Side-by-side good vs. bad result |

### Closing Strategies (use ≥1)

- **Call-back**: reference the opening question/statistic with the answer
- **3 takeaways**: the only things to remember (use `goldcall` box)
- **Open question**: what remains unsolved → future work

---

## Slide Design Patterns

### Definition Slide

```
[Motivation: 1-line informal "Why we need this"]
[Formal definition in eqbox or displayed math]
[Worked example within 2 slides]
```

### Algorithm / Method Slide

```
[Problem statement (1-2 lines)]
[Algorithm steps — max 10 lines of pseudocode]
[Highlight critical step with color]
[Input/output clearly labeled]
```

### Comparison Slide

```
[Side-by-side table or columns: prior vs. this work]
[1-2 lines highlighting the key difference]
```

### Theorem / Proof Slide

- **Never** cram theorem + proof on one slide
- Theorem slide: informal framing → `\begin{theorem}` → key implication
- Proof on **next** slide; for long proofs, show proof sketch + full proof in backup
- Use `\begin{proof}[Proof sketch]` for abbreviated proofs

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
| Colored boxes (`bluecard`/`eqbox`/`goldcall`/`greencard`/`alertcard` combined) | 3 | Redistribute content |

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
- **Spacing after title**: insert `\vspace{4pt}` between frame title and first `\toprule` (prevents visual merge with title bar — compiler emits zero warnings for this)
- **Always use `booktabs`**: `\toprule`, `\midrule`, `\bottomrule` — never vertical lines (`|`)
- **Column alignment**: numbers → `r`, text → `l`, short labels → `c`
- **Max dimensions**: 6-7 columns, 8-10 rows per slide; more → paginate
- **Pagination rules**: repeat full header on each page, append "(cont'd)" to frame title, split at logical boundaries, last page must have ≥3 data rows
- **Highlight key cells**: `\cellcolor{ThemeLight}` or `\textbf{}` — draw the eye to the result
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
| **Critical** | Overfull hbox > 10pt | −10 |
| **Major** | Content overflow inside colored box | −10 per box |
| **Major** | Sparse slide (≤3 items, no math/diagram) | −5 per slide |
| **Major** | TikZ label overlap | −5 |
| **Major** | Missing references slide | −5 |
| **Major** | Table not centered | −3 per table |
| **Major** | Table `\toprule` merges with title bar | −5 per slide |
| **Major** | Notation inconsistency | −3 |
| **Minor** | `\vspace` overuse (>3 per slide) | −1 |
| **Minor** | Font size reduction (`\footnotesize`) | −1 per slide |

**Thresholds:**
- **≥ 90**: Ready to deliver
- **80–89**: Acceptable with caveats
- **< 80**: Must fix before delivery

---

## Pending Work (from HANDOFF.md)

See `HANDOFF.md` for detailed user-requested fixes and troubleshooting notes.
