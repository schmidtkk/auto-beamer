---
name: beamer-layout
description: "Use when working with XeLaTeX Beamer slides — from initial theme selection and draft content, through layout optimization, to post-hoc density auditing and grammar checking. Triggers on *.tex files with \\documentclass{beamer}, new slide requests, theme questions, Overfull errors, layout questions, or image-scale concerns."
---

# Beamer Layout — XeLaTeX Slide Design Pipeline

## Prerequisites

### Required Software

| Component | Version | Purpose |
|-----------|---------|---------|
| XeLaTeX | TeX Live ≥ 2022 | Document compiler (required for `fontspec` + `xeCJK`) |
| Python | 3.8+ | Layout optimizer + grammar checker |
| pdftoppm | poppler-utils | PNG screenshot generation |

### LaTeX Packages (auto-installed with TeX Live)

All required packages are standard TeX Live packages:

- `beamer` + `metropolis` theme
- `fontspec`, `unicode-math`, `xeCJK`
- `tcolorbox` (with `skins`, `breakable` libraries)
- `graphicx`, `xcolor`, `adjustbox`
- `booktabs`, `array`, `colortbl`, `multirow`, `tabularx`
- `pifont`, `tikz` (with `positioning`, `calc`)
- `amsmath`, `amssymb`, `etoolbox`, `microtype`
- `appendixnumberbeamer`

### CJK Fonts (User-Managed)

**We do NOT distribute fonts.** The system auto-detects installed fonts:

| Platform | Detected Font | Install Command |
|----------|--------------|-----------------|
| Windows | Microsoft YaHei | Built-in |
| Linux | Noto Sans CJK | `sudo apt-get install fonts-noto-cjk` |
| macOS | PingFang / Noto Sans SC | Built-in or `brew install font-noto-sans-cjk-sc` |

**Custom font override** (before `\input{config.tex}` or `\usepackage{template-lib}`):

```latex
\def\CJKFontPath{/usr/share/fonts/truetype/noto/}
\def\CJKFontName{NotoSansSC-Regular.ttf}
\def\CJKFontBold{NotoSansSC-Bold.ttf}
\input{config.tex}
```

### Installation

**Linux:**

```bash
chmod +x install-linux.sh
./install-linux.sh
```

**Windows:**

Install TeX Live or MiKTeX, then use `build_clean.ps1`.

**macOS:**

Install MacTeX (full) or BasicTeX, then use `build.sh`.

### Build Commands

| Platform | Command |
|----------|---------|
| Windows | `.\build_clean.ps1 [deck-name]` |
| Linux/macOS | `./build.sh [deck-name]` |
| Manual | `xelatex -output-directory=build -interaction=nonstopmode deck.tex` (×2) |

## Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 0: THEME & STYLE — Choose visual identity                │
│  ├─ Step 1: Ask about audience, tone, color preference          │
│  ├─ Step 2: Pick theme from template-lib/themes/                │
│  └─ Output: \usetheme + color palette locked                    │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 1: DRAFT — Generate raw slide content                    │
│  ├─ Step 1: User provides paper text / figures / tables         │
│  ├─ Step 2: Run layout_optimizer.py suggest for each slide      │
│  ├─ Step 3: Populate skeleton with content (no optimization)    │
│  └─ Output: Working .tex with all content, possibly rough       │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 2: OPTIMIZE — Fix layout, scale, balance                 │
│  ├─ Step 1: Compile → check for Overfull \vbox                  │
│  ├─ Step 2: Run check_layout.py --advise                        │
│  ├─ Step 3: Fix DGV (Layer 4) → Geometry (L2) → Density (L3)   │
│  ├─ Step 4: Image scale check → auto_crop.py --dryrun           │
│  └─ Output: Clean .tex with balanced layouts                    │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 3: POLISH — Final audit & visual verification            │
│  ├─ Step 1: Final compile (2 passes)                            │
│  ├─ Step 2: check_layout.py deck.tex build/deck.log --advise    │
│  ├─ Step 3: Generate PNG screenshots (pdftoppm)                 │
│  └─ Output: deck.pdf + per-page PNGs for visual review          │
└─────────────────────────────────────────────────────────────────┘
```

**Rule:** Do NOT skip phases. A user asking "fix this slide" still needs Phase 2. A user asking "build a deck" starts at Phase 0.

---

## Phase 0: Theme & Style Selection

### Step 0.1: Ask Clarifying Questions

Before any code, ask ONE question at a time. Also consult user preferences from `../../memories/repo/user-preferences.md` (relative to this skill file).

1. **Audience:** Academic conference (MICCAI/NeurIPS) or group meeting?
2. **Tone:** Formal (navy + red) or modern (teal/dark)?
3. **Language:** English-only or bilingual (CJK)?
4. **Figures:** Mostly paper screenshots, photos, or diagrams?

**User preference note:** This user prefers modern clean style (Teal) over classic academic, and strongly prefers readability over density.

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

**Font troubleshooting:** If compilation fails with "font not found", check:
1. CJK fonts installed: `fc-list :lang=zh` (Linux/macOS) or check `C:\WINDOWS\Fonts` (Windows)
2. Override fonts in `.tex` preamble before `\input{config.tex}`:
   ```latex
   \def\CJKFontPath{/your/font/path/}
   \def\CJKFontName{YourFont.ttf}
   \def\CJKFontBold{YourFontBold.ttf}
   ```

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
n_img = 0      → text-only	n_img ≥ 2      → image-grid
n_img = 1:
  AR > 1.6     → image-top (\budgetwideimg)
  AR 1.4-1.6   → image-top preferred
  AR ≤ 1.4     → image-left / image-right (SIDE)
    n_card > 2 or has_gold → image-top (overflow risk)
```

### Step 1.2: Populate Skeleton

Copy the generated LaTeX skeleton from `layout_optimizer.py` and fill in:
- Slide title
- Image paths (use `\adjincludegraphics`)
- Card content (bullet points, equations)
- Caption text

**Draft rules:**
- Do NOT optimize yet — get content in first
- Use placeholder images if final assets not ready
- Mark TODOs for figures that need `auto_crop.py`
- **Max 3 blocks per slide** — if layout suggests 4+ blocks, split frame or convert blocks to plain text

### Step 1.3: Draft Compile

```bash
xelatex -output-directory=build -interaction=nonstopmode deck.tex
```

Expect errors. Fix only syntax errors (missing `$`, unmatched braces). Ignore layout issues for now.

---

## Phase 2: Optimize Layout

### Step 2.1: Compile & Detect Overflows

```bash
# Clean build (2 passes)
.\build_clean.ps1 deck

# Check log
Select-String -Path "build\deck.log" -Pattern "Overfull \\vbox|! |Missing \\$"
```

**Overfull \vbox fix priority:**
1. Reduce `max height=N\textheight` by 0.06–0.08
2. Delete `\vspace` or `\\[Npt]` spacing
3. `\scriptsize` + `\setlength\tabcolsep{4pt}` for tables
4. Still overflow → split frame

**Note:** Line number in error is `\end{frame}`. Search backwards for `\begin{frame}`.

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

**Block count rule (user preference):**
- **Maximum 3 blocks per slide** (`bluecard`/`eqbox`/`goldcall` count as blocks)
- If draft has 4+ blocks: split into 2 frames, or convert non-key blocks to plain text
- Blocks reserved for: keynote, theorems, properties, key takeaways

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
- Vertically centers content block

### Step 2.5: Fix Density & Scale (Layer 3)

**Image scale check — BEFORE embedding:**

```python
# fit-to-width  scale = 398 / img_width_pt
# fit-to-height scale = bbiAvailHt / img_height_pt
# Rendered scale = min(fit-to-width, fit-to-height)
```

| Scale | Verdict | Action |
|-------|---------|--------|
| ≥ 0.20 | ✓ OK | Text readable |
| < 0.20, height-binding | ⚠ Too small | Crop margins, remove bottom block, or switch layout |
| < 0.20, **width-binding** | ✗ Cannot fix | **Typeset as LaTeX `tabular`** |

**Cap-height readability:**
- ≥ 11 pt: screen-readable
- ≥ 7 pt: PDF-readable
- < 7 pt: **too small** — must re-typeset

**Auto-crop workflow:**

```bash
# Preview scale after crop
python tools/auto_crop.py input.png --dryrun

# Execute crop
python tools/auto_crop.py input.png output.png --padding 8
```

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
- DGV = 0 (no grammar violations)
- U ∈ [0.80, 0.95] (not sparse, not overflowing)
- B > 0.80 (columns balanced) or N/A (non-column layouts)
- G < 0.15 (visual center near geometric center)
- **Block count ≤ 3 per slide** (user preference — see Phase 1.2)

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
