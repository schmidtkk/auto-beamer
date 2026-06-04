---
name: autobeamer-build
description: "Compile XeLaTeX Beamer decks, troubleshoot build errors, set up the TeX environment, and manage CJK fonts."
when_to_use: "Triggers on xelatex commands, Overfull errors, font-not-found errors, build-script questions, TeX Live installation, or PDF generation."
argument-hint: "build [deck-name] — compile a deck and troubleshoot build errors"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
---

# AutoBeamer Build — Compilation & Troubleshooting

## Prerequisites

### Action: `doctor` — preflight the environment

> For a standalone preflight ("beamer doctor", "check dependencies"), use the
> dedicated [autobeamer-doctor](../autobeamer-doctor/SKILL.md) skill — it wraps
> the same tool below.

Before a build (and at the start of every create task), probe what is installed:

```bash
python tools/doctor.py check      # writes .autobeamer/env_state.json; exit!=0 if blocked
python tools/doctor.py report     # human-readable summary
```

- **Hard deps** (`xelatex`, `pdftoppm`, `pdfinfo`) — missing ⇒ `check` exits
  non-zero and the deck task is **blocked**; install before retrying.
- **Soft deps** (`PyMuPDF`, `markitdown`, CJK fonts) — missing only **degrades**
  a feature (figure extraction, caption enrichment, bilingual text). Each missing
  dep prints its install hint. The create skill reads this state during planning
  to pick fallback behavior — see `autobeamer-create/references/validation/env-doctor.md`.

### Required Software

| Component | Version | Purpose |
|-----------|---------|---------|
| XeLaTeX | TeX Live ≥ 2022 | Document compiler (`fontspec` + `xeCJK`) |
| Python | 3.8+ | Layout optimizer + grammar checker |
| pdftoppm / pdfinfo | poppler-utils | PNG screenshots + page/size checks |

### LaTeX Packages (auto-installed with TeX Live)

`beamer` + `metropolis`, `fontspec`, `unicode-math`, `xeCJK`, `tcolorbox` (skins, breakable), `graphicx`, `xcolor`, `adjustbox`, `booktabs`, `array`, `colortbl`, `multirow`, `tabularx`, `pifont`, `tikz` (positioning, calc), `amsmath`, `amssymb`, `etoolbox`, `microtype`, `appendixnumberbeamer`

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

| Platform | Steps |
|----------|-------|
| Linux | `chmod +x install-linux.sh && ./install-linux.sh` |
| Windows | Install TeX Live or MiKTeX, then use `build_clean.ps1` |
| macOS | Install MacTeX (full) or BasicTeX, then use `build.sh` |

---

## Build Commands

| Platform | Command |
|----------|---------|
| Windows | `.\build_clean.ps1 [deck-name]` |
| Linux/macOS | `./build.sh [deck-name]` |
| Manual | `xelatex -output-directory=build -interaction=nonstopmode deck.tex` (×2) |
| Build all | `.\build_clean.ps1 all` or `./build.sh all` |

**Why 2 passes?** First pass writes `.aux` files (cross-references, `equal height group` data). Second pass reads them for correct layout.

### Where your deck file must live

`\usepackage[<theme>]{template-lib/template-lib}` is a **relative** package path, so
XeLaTeX only finds it when the deck `.tex` sits at the repository root (next to the
`template-lib/` directory). To keep a deck anywhere else, point TeX at the library:

```bash
TEXINPUTS=".:/path/to/auto-beamer//:" xelatex -output-directory=build deck.tex
```

The trailing `//` makes the search recursive. A "File `template-lib/template-lib.sty`
not found" error almost always means the deck is in the wrong directory or `TEXINPUTS`
is unset.

---

## Compilation Workflow

### Step 1: Clean Build (Recommended)

Use the build script — it cleans intermediates, runs 2 passes, copies PDF to root, and checks for overflows:

```bash
# Windows
.\build_clean.ps1 deck-name

# Linux/macOS
./build.sh deck-name
```

### Step 2: Check for Errors

```bash
# Windows
Select-String -Path "build\deck.log" -Pattern "Overfull \\vbox|! |Missing \\$"

# Linux/macOS
grep -E "Overfull \\\\vbox|^!" build/deck.log
```

### Step 3: Generate PNG Screenshots (Visual Review)

```bash
pdftoppm -png -r 200 build/deck.pdf _slides_png/slide
```

---

## Error Troubleshooting

### Overfull \vbox

The most common layout error. The line number points to `\end{frame}` — search backwards for the matching `\begin{frame}`.

**Fix priority:**
1. Reduce `max height=N\textheight` by 0.06–0.08
2. Delete `\vspace` or `\\[Npt]` spacing
3. `\scriptsize` + `\setlength\tabcolsep{4pt}` for tables
4. Still overflows → split frame

### Font Not Found

1. Check installed fonts: `fc-list :lang=zh` (Linux/macOS) or `C:\WINDOWS\Fonts` (Windows)
2. Override fonts in preamble (see CJK Fonts section above)
3. Confirm `fontspec` can find the font: `xelatex -interaction=nonstopmode` with `\font\test="Noto Sans CJK SC"\test`

### Common Syntax Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Missing $` | Bare math command in text mode | Wrap in `$...$` |
| `Undefined control sequence` | Unknown command / typo | Check package loaded, correct spelling |
| `Too many }'s` | Unmatched brace | Count `{` vs `}` in frame |
| `tcolorbox` errors | Box inside `\sbox` / wrong nesting | Check box nesting; avoid boxed measurement/image-top contexts |

---

## Clean Intermediate Files

The build scripts auto-clean these extensions: `aux`, `nav`, `snm`, `toc`, `log`, `out`, `fls`, `fdb_latexmk`, `xdv`

Manual clean:

```bash
# Windows
Remove-Item build\*.aux, build\*.nav, build\*.snm, build\*.toc, build\*.log

# Linux/macOS
rm -f build/*.{aux,nav,snm,toc,log}
```
