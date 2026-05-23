<p align="center">
  <img src="assets/teaser/showcase/theme-gallery-2x2.png" alt="Beamer Deck Auto Theme Gallery" width="800">
</p>

<h1 align="center">Beamer Deck Auto</h1>

<p align="center">
  <b>A design-engineered slide system for XeLaTeX Beamer.</b><br>
  Three-tier template library · Four-layer layout optimizer · Design grammar checker · AI agent skills
</p>

<p align="center">
  <a href="#quickstart">Quickstart</a> ·
  <a href="#features">Features</a> ·
  <a href="#showcase">Showcase</a> ·
  <a href="#requirements">Requirements</a>
</p>

---

## Why Beamer Deck Auto?

Building academic slides with LaTeX Beamer usually means:
- **Guessing layouts** — Will this figure fit on the left? Should I use `columns` or `minipage`?
- **Manual tweaking** — Adjusting `\vspace{-2ex}` until the slide stops overflowing
- **No quality gate** — "Looks fine to me" — but the audience sees unbalanced columns and loose text

**Beamer Deck Auto** replaces guesswork with a systematic pipeline:

<p align="center">
  <img src="assets/teaser/pipeline/pipeline-overview.png" alt="4-Phase Pipeline" width="900">
</p>

1. **Parse** — Extract content from PDF papers (text, figures, references)
2. **Optimize** — 4-layer decision tree picks the best layout template automatically
3. **Build** — XeLaTeX + xeCJK with auto font detection, two-pass for perfect alignment
4. **Audit** — U/B/G/DGV metrics catch visual problems before your audience does

> **"Design before density"** — Layout choice first, content second, polish last.

---

## Features

### 🎨 Three-Tier Template Library

| Tier | What | Count | Example |
|------|------|-------|---------|
| **Themes** | Color + typography palettes | 4 | Navy+Red, Teal+Amber, Dark+Gold, Navy+Gold |
| **Layouts** | Page structure patterns | 8 | Text, 1-img, 2-img, 3-img, eq, table, img-top, twocol |
| **Components** | Reusable content blocks | 12+ | Info card, alert, result, equation box, figure helper |

<p align="center">
  <img src="assets/teaser/showcase/theme-navygold.png" width="380">
  <img src="assets/teaser/showcase/theme-teal.png" width="380">
</p>
<p align="center">
  <img src="assets/teaser/showcase/theme-dark.png" width="380">
  <img src="assets/teaser/showcase/theme-academic.png" width="380">
</p>

### 🧠 Four-Layer Layout Optimizer

`layout_optimizer.py` makes layout decisions like a senior designer:

| Layer | Decision | Example |
|-------|----------|---------|
| **L1 Template** | Aspect ratio → layout family | Wide figure → `imgtop` · Square figure → `1img` side |
| **L2 Constraints** | Column balance, natural image height | Prevent 30/70 splits, cap image at 76% frame height |
| **L3 Density** | Text fills 60–85% of slot | Too sparse → add content; too dense → split slide |
| **L4 Grammar** | Hard design rules | No loose text outside boxes · No gold callout in columns · Max 3 blocks/slide |

```bash
# Get layout suggestion for a wide image + 2 takeaway cards
python tools/layout_optimizer.py suggest --img 1716:1124 --cards 2
# → Recommended: imgtop layout, auto-capped height, 2 bluecards bottom
```

### 🔍 Design Grammar Checker

`check_layout.py` measures every frame with 4 metrics:

| Metric | Target | What it catches |
|--------|--------|-----------------|
| **U** Utilization | 0.80–0.95 | Wasted space or overcrowding |
| **B** Column Balance | > 0.80 | Lopsided two-column layouts |
| **G** Gravity Deviation | < 0.15 | Content drifting too high or low |
| **DGV** Grammar Violations | 0 | Loose text, bad block placement, stacked cards |

```bash
# Audit a compiled deck
python tools/check_layout.py deck.tex build/deck.log --advise
```

### 🤖 AI Agent Skills

Pre-built skills for **Claude Code** and **Codex CLI** — your agent knows the pipeline:

| Skill | Triggers On | What It Does |
|-------|-------------|--------------|
| `beamer-layout` | Layout questions, overflow, image scaling | 4-phase design pipeline: theme → draft → optimize → polish |
| `beamer-build` | Compilation errors, font issues, build failures | XeLaTeX wrapper, auto font config, error recovery |

---

## Showcase

### Demo Deck — Fictional Research

<table>
<tr>
<td width="50%">
<b>Hero Slide</b><br>
<small>Title slide with gradient background and institution branding.</small><br>
<img src="assets/teaser/decks/demo-hero.png" width="100%">
</td>
<td width="50%">
<b>Two-Column Layout</b><br>
<small>Side-by-side content with info cards and structured layout.</small><br>
<img src="assets/teaser/decks/demo-twocol.png" width="100%">
</td>
</tr>
<tr>
<td width="50%">
<b>Equation Slide</b><br>
<small>Definition box with display math and key equations.</small><br>
<img src="assets/teaser/decks/demo-equation.png" width="100%">
</td>
<td width="50%">
<b>Results Table</b><br>
<small>Comparison table with highlighted best results.</small><br>
<img src="assets/teaser/decks/demo-results.png" width="100%">
</td>
</tr>
</table>

### Template Library Demo

All 4 themes × 8 layouts × component variations in a single reference deck: `template-lib-demo.tex`

---

## Quickstart

### 1. Install Dependencies

**Windows:**
1. Install [TeX Live](https://tug.org/texlive/) or [MiKTeX](https://miktex.org/)
2. Ensure `xelatex` is in your PATH
3. CJK fonts: Microsoft YaHei (built-in)

**Linux:**
```bash
chmod +x install-linux.sh
./install-linux.sh   # TeX Live + Noto Sans CJK + Python deps
```

**macOS:**
```bash
brew install mactex-no-gui
brew install font-noto-sans-cjk-sc
```

### 2. Build Your First Deck

```bash
# Windows
.\build_clean.ps1 template-lib-demo

# Linux / macOS
./build.sh template-lib-demo
```

Output: `build/template-lib-demo.pdf`

### 3. Design a New Slide

```bash
# Ask the optimizer what layout to use
python tools/layout_optimizer.py suggest --img 1200:800 --cards 2

# It outputs a LaTeX skeleton — paste into your .tex and fill content
```

### 4. Audit Before You Present

```bash
python tools/check_layout.py your-deck.tex build/your-deck.log --advise
```

---

## The Workflow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Parse     │ →  │   Optimize  │ →  │    Build    │ →  │    Audit    │
│  (optional) │    │  (required) │    │  (required) │    │  (required) │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
     │                   │                   │                   │
 paper_parser.py    layout_optimizer.py   build_clean.ps1   check_layout.py
     │                   │                   │                   │
  Extract text      Pick template        XeLaTeX × 2        U/B/G/DGV
  Figures, refs     Generate skeleton    Auto font detect   Grammar check
  Section map       Fix density/balance  PNG screenshots    Fix or flag
```

**Phase -1: Parse** (optional) — Starting from a PDF paper? `paper_parser.py` extracts sections, figures, and text into a structured JSON. Map sections → slides.

**Phase 0: Theme** — Pick audience + tone → lock in a theme from the template library.

**Phase 1: Draft** — Generate raw slide content. The optimizer suggests layouts per slide.

**Phase 2: Optimize** — Compile, run the grammar checker, fix DGV → Geometry → Density in order.

**Phase 3: Polish** — Two-pass XeLaTeX build, generate PNG screenshots, present for review.

---

## Project Structure

```
.
├── README.md                          # This file
├── CLAUDE.md                          # Project context for AI agents
├── AGENTS.md                          # Agent guidelines
├── skills/
│   ├── beamer-layout/SKILL.md         # Claude Code: 4-phase pipeline
│   └── beamer-build/SKILL.md          # Claude Code: compilation skill
├── template-lib/                      # Three-tier template library
│   ├── template-lib.sty               # Master entry point
│   ├── themes/                        # 4 color themes
│   ├── layouts/                       # 8 layout patterns
│   ├── components/                    # Reusable blocks
│   └── docs/CATALOG.md                # Full API reference
├── tools/                             # Layout & audit tools
│   ├── layout_optimizer.py            # 4-layer decision tree
│   ├── check_layout.py                # U/B/G/DGV metrics
│   ├── paper_parser.py                # PDF paper extraction
│   ├── auto_crop.py                   # Image white-margin cropper
│   └── README.md                      # Tool reference
├── theme-library/                     # Minimal theme previews
├── personal-deck/                     # Real academic decks (examples)
└── assets/teaser/                     # Promotional assets
```

---

## Documentation

| Document | Purpose |
|----------|---------|
| [`CLAUDE.md`](CLAUDE.md) | Project context, box macros, height alignment rules, build commands |
| [`AGENTS.md`](AGENTS.md) | Agent guidelines, tool reference, key constraints |
| [`template-lib/docs/CATALOG.md`](template-lib/docs/CATALOG.md) | Full theme/layout/component API reference |
| [`tools/README.md`](tools/README.md) | Tool usage examples and CLI reference |
| [`skills/beamer-layout/SKILL.md`](skills/beamer-layout/SKILL.md) | AI skill: 4-phase design pipeline |
| [`skills/beamer-build/SKILL.md`](skills/beamer-build/SKILL.md) | AI skill: compilation automation |

---

## Requirements

| Component | Version | Notes |
|-----------|---------|-------|
| XeLaTeX | TeX Live ≥ 2022 | Required for `fontspec` + `xeCJK` |
| Python | 3.10+ | For layout optimizer and grammar checker |
| `metropolis` | Beamer theme | Included in TeX Live |
| LaTeX packages | — | `adjustbox`, `tcolorbox`, `booktabs`, `xeCJK`, `unicode-math` |

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Follow the `beamer-layout` skill for new layouts
4. Run `check_layout.py` before submitting
5. Submit a PR with clear description

---

## License

MIT License — see [LICENSE](LICENSE) file for details.

---

<p align="center">
  <i>Built for researchers who care about how their slides look.</i>
</p>
