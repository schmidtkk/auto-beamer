---
name: beamer-layout
description: "Use when designing XeLaTeX Beamer slide layouts — choosing templates, placing images, fixing overflows, balancing columns, or auditing slide density. Triggers on layout questions, image-scale concerns, column alignment, layout_optimizer.py usage, or check_layout.py results."
---

# Beamer Layout — Slide Design Pipeline

> **For compilation and build errors**, see [beamer-build](../beamer-build/SKILL.md).
> **For theme/layout reference tables**, see [CATALOG.md](../../template-lib/docs/CATALOG.md).

## Pipeline Overview

```
PHASE 0: THEME → Pick visual identity (audience + tone)
PHASE 1: DRAFT → Generate raw slide content (no optimization)
PHASE 2: OPTIMIZE → Fix layout, scale, balance (this skill's core)
```

**Rule:** Do NOT skip phases. "Fix this slide" → Phase 2. "Build a deck" → Phase 0.

---

## Phase 0: Theme & Style Selection

### Step 0.1: Ask Clarifying Questions

Before any code, ask ONE question at a time. Consult user preferences from `../../memories/repo/user-preferences.md`.

1. **Audience:** Academic conference (MICCAI/NeurIPS) or group meeting?
2. **Tone:** Formal (navy + red) or modern (teal/dark)?
3. **Language:** English-only or bilingual (CJK)?
4. **Figures:** Mostly paper screenshots, photos, or diagrams?

### Step 0.2: Pick Theme

| Theme | File | Best For |
|-------|------|----------|
| Academic | `theme-academic.sty` | Formal conferences, navy + red |
| Teal | `theme-teal.sty` | Modern, clean, tech-forward |
| Dark | `theme-dark.sty` | Dark mode, cinematic |
| NavyGold | `theme-navygold.sty` | Premium, gold accents |

Load: `\RequirePackage{template-lib/template-lib}` then `\uselayout{...}`

### Step 0.3: Verify Theme Assets

- Check `theme-library/` for preview PNGs
- Confirm `config.tex` has matching box macros (`bluecard`, `goldcall`, `eqbox`)
- Verify CJK font setup if bilingual
- If "font not found" → see [beamer-build](../beamer-build/SKILL.md) for font troubleshooting

---

## Phase 1: Draft Content

### Step 1.1: Per-Slide Layout Decision

For each slide, run:

```bash
python tools/layout_optimizer.py suggest \
  --img W:H [--img W:H ...] \
  --cards N \
  [--lines N] [--eq] [--gold]
```

**Decision tree (Layer 1):**

```
n_img = 0      → text-only    n_img ≥ 2      → image-grid
n_img = 1:
  AR > 1.6     → image-top (\budgetwideimg)
  AR 1.4-1.6   → image-top preferred
  AR ≤ 1.4     → image-left / image-right (SIDE)
    n_card > 2 or has_gold → image-top (overflow risk)
```

### Step 1.2: Populate Skeleton

Copy the generated LaTeX skeleton from `layout_optimizer.py` and fill in:
- Slide title, image paths (`\adjincludegraphics`), card content, caption text

**Draft rules:**
- Do NOT optimize yet — get content in first
- Use placeholder images if final assets not ready
- Mark TODOs for figures that need `auto_crop.py`
- **Max 3 blocks per slide** — if layout suggests 4+ blocks, split frame or convert to plain text

### Step 1.3: Draft Compile

Compile to check syntax. See [beamer-build](../beamer-build/SKILL.md) for commands.
Fix only syntax errors (missing `$`, unmatched braces). Ignore layout issues for now.

---

## Phase 2: Optimize Layout

### Step 2.1: Compile & Detect Overflows

Compile with build script (see [beamer-build](../beamer-build/SKILL.md)), then check log for `Overfull \vbox`.

### Step 2.2: Run Layout Audit

```bash
python tools/check_layout.py deck.tex build/deck.log --advise
```

**Fix order (critical — do not reorder):**

| Layer | What | Fix First? |
|-------|------|-----------|
| L4 Grammar (DGV) | GV-1..GV-4 violations | **YES** — blocks reliable assessment |
| L2 Geometry | U > 1.0 overflow, B < 0.55 imbalance | **SECOND** |
| L3 Density | U < 0.6 sparse, text density | **THIRD** |
| L1 Template | AR mismatch, wrong layout choice | **LAST** |

### Step 2.3: Fix DGV (Layer 4 Grammar)

| Code | Rule | Fix |
|------|------|-----|
| GV-1 | Loose text outside box | Wrap in `\begin{goldcall}` |
| GV-2 | `goldcall` inside `columns` | Move below `\end{columns}` |
| GV-3 | Multiple `bluecard`s in one column | **Split frame** or convert to plain text (max 3 blocks/slide) |
| GV-4 | Wide image (AR>1.5) in SIDE layout | Switch to `\budgetwideimg` |

**Block count rule:** Maximum 3 blocks per slide (`bluecard`/`eqbox`/`goldcall`). If 4+: split into 2 frames, or convert non-key blocks to plain text.

**Common syntax fixes:**
- CJK/ASCII: `\footnotesize\raggedright` inside tcolorbox
- Math mode: `$\to$` never bare `\to`

### Step 2.4: Fix Geometry (Layer 2)

**Column height balance:**
- Standalone frame: `equal height group=name` on both boxes, compile ×2
- `[shrink=N]` or inside `\budgetwideimg`: **must hardcode**
  - Temp group → build 2× → read .aux → replace with `height=XXpt,valign=top`

**Wide image bottom whitespace:**
- Add `[c]` to frame options: `\begin{frame}[c]{Title}`

### Step 2.5: Fix Density & Scale (Layer 3)

For image scale thresholds and auto-crop workflow, see [references/scale-tables.md](references/scale-tables.md).

**Typeset as tabular (AR > 2.5):**

```latex
\begin{frame}{Results}
  \vspace{0.3em}
  {\centering\footnotesize
  \setlength{\tabcolsep}{4pt}%
  \begin{tabular}{@{}l r r r r@{}}
    \toprule
    \textbf{Method} & \textbf{NFE} & \textbf{18-view} \\
    \midrule
    Baseline  & 1    & 34.02 \\
    \rowcolor{ThemeLight}
    \textbf{Ours} & \textbf{10} & \textbf{38.34} \\
    \bottomrule
  \end{tabular}\par}
\end{frame}
```

---

## Phase 3: Polish & Verify

### Step 3.1: Final Compile

```bash
# Full clean build (Windows)
.\build_clean.ps1 deck

# Linux/macOS
./build.sh deck
```

Verify: zero errors, no Overfull \vbox.

### Step 3.2: Final Audit

```bash
python tools/check_layout.py deck.tex build/deck.log --advise
```

**Acceptance criteria:**

Presentation mode:
- DGV = 0 (no grammar violations)
- U ∈ [0.80, 0.95] (not sparse, not overflowing)
- B > 0.80 (columns balanced) or N/A (non-column layouts)
- G < 0.15 (visual center near geometric center)
- **Block count ≤ 3 per slide**

Mentor mode:
- DGV = 0
- U ∈ [0.75, 0.98] (denser is acceptable; < 0.60 is still sparse)
- B > 0.70
- G < 0.20
- **Block count ≤ 5 per slide**

**Critical:** Any frame with U < 0.60 or containing only 1 block with no math/diagram must be flagged as sparse.

### Step 3.3: Visual Verification

```bash
# Generate per-page PNGs
pdftoppm -r 150 -png build\deck.pdf _slides_png\slide
```

Spot-check:
- [ ] All text readable (no blurry sub-7pt text)
- [ ] Columns visually balanced
- [ ] No cropped equations or images
- [ ] Color contrast adequate
- [ ] **No sparse slides** — every frame has ≥1 substantive element (formula, diagram, table, theorem, proof step, or worked example)
- [ ] **No block-interior overflow** — visually inspect every `\TLinfoblock`, `\TLalertblock`, and tcolorbox for truncated content

**Sparse-slide detection:**
| Indicator | Severity | Fix |
|-----------|----------|-----|
| Frame with only 1 `\TLtakeaway` and nothing else | CRITICAL | Merge into preceding frame or add derivation |
| Frame > 50% empty vertical space | WARNING | Merge with adjacent frame or add content |
| Frame with text-only bullets, no math/diagram | WARNING | Add a formula, diagram, or table; or merge |
| Consecutive sparse frames (>2 in a row) | CRITICAL | Restructure section

---

## User Preferences

Stored in `../../memories/repo/user-preferences.md` (relative to this skill file):

| Preference | Value |
|-----------|-------|
| Theme | Modern clean (Teal) > Academic (navy+red) |
| Max blocks/slide | **3** — split frame or convert to text if exceeded |
| Block purpose | Keynote, theorems, properties, key takeaways only |
| Image scale | ≥ 20% (cap height ≥ 7pt PDF, ≥ 11pt screen) |
| Density | Prefer readable over dense |
| Workflow | Ask before major structural changes; preview PNGs before finalizing |

## Tool Reference

| Tool | Phase | Command | Purpose |
|------|-------|---------|---------|
| `layout_optimizer.py` | 1, 2 | `suggest --img W:H --cards N` | Template decision + skeleton |
| `check_layout.py` | 2, 3 | `deck.tex build/deck.log --advise` | U/B/G/AR/DGV audit |
| `auto_crop.py` | 2 | `input.png --dryrun` | Preview scale; remove margins |
| `build_clean.ps1` | 1, 2, 3 | `deck-name` | Clean compile — Windows |
| `build.sh` | 1, 2, 3 | `deck-name` | Clean compile — Linux/macOS |

## Geometry Reference

| Value | Approx |
|-------|--------|
| `\textheight` | 198 pt |
| `\textwidth` | 398 pt |
| Usable content | ~144 pt |
| `max height=0.50\textheight` | 99 pt |
| `\textwidth / \textheight` | ~2.0 |
| Width-binding threshold | AR > ~2.8 |
