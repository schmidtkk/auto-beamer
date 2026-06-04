---
name: cjk-font-setup
description: How CJK fonts are configured in this project — auto-detection chain, Source Han Serif SC install, and math font pairing with KpMath. Use when creating or troubleshooting Chinese decks.
metadata:
  type: reference
---

# CJK Font Setup — Auto-Beamer

**Rule:** Chinese decks use **Source Han Serif SC Medium+Bold** individual OTFs in
`.fonts/`, auto-detected by `font-config.sty` Priority 1.5. The system-default
Noto Sans CJK Regular `.ttc` is too thin for presentation slides and should
never be used for Chinese decks.

**Why:** Noto Sans CJK SC Regular (the Linux `fonts-noto-cjk` default) is a
UI/reading-weight sans-serif designed for body text on screens — it lacks visual
"punch" on slides and looks washed-out next to LaTeX math.

**How to apply:** font-config auto-detects `.fonts/SourceHanSerifSC-Medium.otf`.
No preamble override is needed. See [[autobeamer-build]] for the install
command, and [[user-preferences]] for the font-family rationale.

## Detection Priority (font-config.sty)

| Priority | Source | Typical font |
|----------|--------|-------------|
| 1 | User override: `\def\CJKFontPath{...}` before `\usepackage` | Any |
| **1.5** | **Project-local `.fonts/`** | **Source Han Serif SC Medium+Bold** |
| 2 | Windows system | Microsoft YaHei |
| 3 | Linux system (`fonts-noto-cjk`) | Noto Sans CJK Regular `.ttc` |
| 4 | macOS system | PingFang |
| 5 | Generic fallback | Noto Sans SC common paths |

Priority 1.5 is a new addition (2026-06-05) that checks for
`./.fonts/SourceHanSerifSC-Medium.otf` before falling back to the system `.ttc`.

## Font Files

| File | Weight | Size | Use |
|------|--------|------|-----|
| `SourceHanSerifSC-Medium.otf` | Medium (5th of 7) | ~24 MB | Body text |
| `SourceHanSerifSC-Bold.otf` | Bold (6th of 7) | ~25 MB | Titles, `\textbf` |

Source: Adobe Source Han Serif v2.003R, SIL OFL license.
GitHub: `adobe-fonts/source-han-serif/releases/download/2.003R/09_SourceHanSerifSC.zip`

All 7 weights (ExtraLight through Heavy) are in that zip; only Medium+Bold are
extracted by default. Deploy the other 5 weights if a deck needs additional
typographic range.

## Math Font Pairing

The template default is **KpMath Regular+Bold** (Kepler project), changed from
Latin Modern Math on 2026-06-05. KpMath is a heavier serif math font that pairs
well with Source Han Serif SC CJK — both are serif, similar visual weight.

Available in TeX Live by default; no extra packages needed.
Override per-deck: `\setmathfont{...}` after `\usepackage{template-lib}`.

## Git

`.fonts/` is in `.gitignore` — font binaries (~162 MB for all 7 weights, ~49 MB
for the two needed weights) are not committed. Each developer installs the fonts
locally.

## Related

- [[user-preferences]] — font family / math preference
- [[feedback-split-not-shrink]] — layout rules that still apply
