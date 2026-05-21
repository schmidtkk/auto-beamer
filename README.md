# Beamer Deck Auto

Beamer Deck Auto is a complete slide design system for XeLaTeX Beamer, built on top of a three-tier template library, a four-layer layout optimizer, and a design grammar checker that catches visual problems before they reach your audience.

## Prerequisites

### Required Software

| Component | Version | Purpose |
|-----------|---------|---------|
| XeLaTeX | TeX Live ≥ 2022 | Document compiler (required for `fontspec` + `xeCJK`) |
| Python | 3.8+ | Layout optimizer + grammar checker |
| pdftoppm | poppler-utils | PNG screenshot generation |

### CJK Fonts (User-Managed)

**We do NOT distribute fonts.** The system auto-detects installed fonts:

| Platform | Detected Font | Install Command |
|----------|--------------|-----------------|
| Windows | Microsoft YaHei | Built-in |
| Linux | Noto Sans CJK | `sudo apt-get install fonts-noto-cjk` |
| macOS | PingFang / Noto Sans SC | Built-in or `brew install font-noto-sans-cjk-sc` |

**Custom font override** (before `\input{config.tex}`):

```latex
\def\CJKFontPath{/usr/share/fonts/truetype/noto/}
\def\CJKFontName{NotoSansSC-Regular.ttf}
\def\CJKFontBold{NotoSansSC-Bold.ttf}
\input{config.tex}
```

## Installation

### Linux

```bash
chmod +x install-linux.sh
./install-linux.sh
```

### Windows

1. Install [TeX Live](https://tug.org/texlive/) or [MiKTeX](https://miktex.org/)
2. Ensure `xelatex` is in your PATH
3. Install CJK fonts manually if needed

### macOS

1. Install [MacTeX](https://www.tug.org/mactex/) (full) or BasicTeX
2. Install CJK fonts: `brew install font-noto-sans-cjk-sc`

## Quickstart

Give your agent slide superpowers: [Claude Code](#claude-code), [Codex CLI](#codex-cli), [Codex App](#codex-app).

## How it works

It starts the moment you open a `.tex` file with `\documentclass{beamer}`. Instead of guessing which layout to use or manually tweaking `\vspace` until the slide stops overflowing, your agent steps back and asks what you're trying to show.

Once it understands your content — figures, equations, tables, bullet points — it runs the **layout optimizer** to pick the right template from the library. Wide image with two takeaway cards? Image-top layout. Two figures side-by-side with captions? Two-image layout. Equation-heavy derivation? Equation layout with auto-scaling.

After the skeleton is in place, your agent compiles and runs the **design grammar checker**. It measures utilization, column balance, gravity deviation, and checks for grammar violations like loose text outside boxes or gold-callout blocks trapped inside columns. It fixes what it can and flags what needs your eye.

Finally, it runs a two-pass XeLaTeX build (critical for `equal height group` alignment), generates per-page PNG screenshots, and presents the results. The skills trigger automatically — your agent just knows what to do.

### Build Commands

| Platform | Command | Description |
|----------|---------|-------------|
| Windows | `.\build_clean.ps1 [deck-name]` | PowerShell build script |
| Linux/macOS | `./build.sh [deck-name]` | Bash build script |
| All | `xelatex -output-directory=build -interaction=nonstopmode deck.tex` | Manual (run ×2) |

## Agent Installation

Installation differs by harness. Install separately for each one.

### Claude Code

Install the plugin from the marketplace:

```bash
/plugin install beamer-deck-auto@claude-plugins-official
```

Or register this repo directly:

```bash
/plugin marketplace add yourname/beamer-deck-auto
/plugin install beamer-deck-auto@yourname
```

### Codex CLI

Open the plugin search interface:

```bash
/plugins
```

Search for **Beamer Deck Auto** and select `Install Plugin`.

### Codex App

- In the Codex app, click on **Plugins** in the sidebar.
- Find **Beamer Deck Auto** in the Coding section.
- Click the `+` and follow the prompts.

## The Basic Workflow

1. **theme-selection** — Activates when a new deck is started. Asks about audience, tone, and color preference. Locks in a theme from the template library.

2. **draft-content** — Activates with paper text / figures / tables. Runs `layout_optimizer.py suggest` per slide, populates skeleton, marks TODOs for missing assets.

3. **optimize-layout** — Activates after draft compile. Detects Overfull `\vbox`, runs `check_layout.py --advise`, fixes DGV (Layer 4) → Geometry (L2) → Density (L3) in order.

4. **polish-output** — Activates when layout is clean. Two-pass XeLaTeX build, generates PNG screenshots with `pdftoppm`, presents deck for visual review.

**The agent checks for relevant skills before any task.** Mandatory workflows, not suggestions.

## What's Inside

### Three-Tier Template Library (`template-lib/`)

**Themes** (Color + Typography)
- **academic** — Navy + Brick Red, classic conference style
- **teal** — Teal + Amber, modern medical/biotech
- **dark** — Soft Blue + Gold, low-light venues
- **navygold** — Navy + Gold, prestigious/ivy

**Layouts** (Page Structure)
- **text** — Pure text flow, bullet points, discussion
- **1img** — Single image: left, right, top, or bottom
- **2img** — Two images side-by-side with captions
- **3img** — Three-image grid or asymmetric layout
- **eq** — Equation-focused: single, compare, derivation
- **table** — Full-width table or side-text hybrid
- **imgtop** — Image-top with auto-height bottom content
- **twocol** — Two-column text: equal, divider, pro/con

**Components** (Reusable Blocks)
- Title slides: standard, centered, section divider
- Content blocks: info, alert, result, warning, takeaway
- Figure helpers: auto-scale, subfigure, caption
- Text utilities: term highlight, checkmarks, styled lists

### Layout Optimizer (`tools/layout_optimizer.py`)

Four-layer decision tree:
1. **Template Decision** — Aspect-ratio based: wide → top layout, square → side layout
2. **Element Constraints** — Column balance, natural image height
3. **Content Density** — Text fills 60–85% of slot
4. **Grammar Rules** — Hard rules: no loose text, no goldcall in columns, max 3 blocks/slide

### Design Grammar Checker (`tools/check_layout.py`)

Per-frame metrics:
- **U** — Utilization (target 0.80–0.95)
- **B** — Column Balance (target > 0.80)
- **G** — Gravity Deviation (target < 0.15)
- **DGV** — Grammar Violations (must be 0)

### Tools

| Tool | Purpose |
|------|---------|
| `layout_optimizer.py` | Layout decision tree + LaTeX skeleton generator |
| `check_layout.py` | Layout audit + DGV checker |
| `auto_crop.py` | Remove image white margins for better embedding scale |
| `build_clean.ps1` | Parameterized XeLaTeX build script — Windows |
| `build.sh` | Parameterized XeLaTeX build script — Linux/macOS |
| `install-linux.sh` | Linux TeX Live + dependency installer |

## Philosophy

- **Design before density** — Layout choice first, content second, polish last
- **Systematic over ad-hoc** — Four-layer optimizer instead of manual tweaking
- **Evidence over eyeball** — U/B/G/DGV metrics instead of "looks fine"
- **Immutability over mutation** — New `.tex` copies, never in-place edits

## Project Structure

```
.
├── README.md                    # This file
├── LICENSE                      # MIT
├── .claude-plugin/              # Claude Code plugin manifest
│   ├── plugin.json
│   └── marketplace.json
├── .codex-plugin/               # Codex CLI plugin manifest
│   └── plugin.json
├── CLAUDE.md                    # Project context for AI agents
├── AGENTS.md                    # Agent guidelines
├── skills/
│   └── beamer-layout/
│       └── SKILL.md             # Claude Code skill (4-phase pipeline)
├── template-lib/                # Three-tier template library
│   ├── template-lib.sty         # Master entry point
│   ├── themes/                  # 4 color themes
│   ├── layouts/                 # 8 layout patterns
│   ├── components/              # 3 component sets
│   └── docs/
│       └── CATALOG.md           # Full API reference
├── tools/
│   ├── layout_optimizer.py      # Layout decision tree + skeleton gen
│   ├── check_layout.py          # Layout audit + DGV checker
│   ├── auto_crop.py             # Image white-margin cropper
│   └── README.md                # Tool reference
└── theme-library/               # Theme preview gallery (minimal .tex)
```

## Requirements

- MiKTeX / TeX Live with XeLaTeX
- `metropolis` Beamer theme
- Python 3.10+ (for tools)
- `adjustbox`, `tcolorbox`, `booktabs`, `xeCJK`, `unicode-math` LaTeX packages

## Contributing

1. Fork the repository
2. Create a branch for your work
3. Follow the `beamer-layout` skill for creating and testing new layouts
4. Submit a PR with a clear description of the layout or tool change

## License

MIT License — see LICENSE file for details.
