---
name: autobeamer-build
description: "Use when compiling XeLaTeX Beamer decks, troubleshooting build errors, setting up TeX environment, or managing fonts. Triggers on xelatex commands, Overfull errors, font-not-found errors, build script questions, TeX Live installation, or PDF generation."
---

# AutoBeamer Build — Compilation & Troubleshooting

## Prerequisites

### Required Software

| Component | Version | Purpose |
|-----------|---------|---------|
| XeLaTeX | TeX Live ≥ 2022 | Document compiler (`fontspec` + `xeCJK`) |
| Python | 3.8+ | Layout optimizer + grammar checker |
| pdftoppm | poppler-utils | PNG screenshot generation |

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
pdftoppm -png -r 200 build/deck.pdf slides_png
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
