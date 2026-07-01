# Tools

## Layout Analysis & Optimization

| Tool | Purpose | Example |
|------|---------|---------|
| `check_layout.py` | Parse .tex source, output U/B/G/AR/DGV metrics per frame | `python tools/check_layout.py deck.tex build/deck.log --advise` |
| `layout_optimizer.py` | Four-layer decision tree for best layout template, generate LaTeX skeleton | `python tools/layout_optimizer.py suggest --img 1716:1124 --cards 2` |
| `auto_crop.py` | Auto-crop image white margins for better embedding scale | `python tools/auto_crop.py fig.png --padding 8` |

## Content & Language Validation

| Tool | Purpose | Example |
|------|---------|---------|
| `validate_deck.py` | Static mode gates (overlays, box cap, references/appendix order, per-mode required sections) | `python tools/validate_deck.py static deck.tex --mode passive-study` |
| `lang_lint.py` | LaTeX-aware language-quality gate: foreign-prose leakage, AI-flavor fillers, proof-hedges, connector clusters; protects math/macros/verbatim. See `skills/autobeamer-review/references/language-quality-gate.md` | `python tools/lang_lint.py lint deck.tex --mode passive-study` |
| `concept_load.py` | Per-frame cognitive-load numbers for a reader profile (calibrate companion) | `python tools/concept_load.py deck.tex --profile P4` |
| `doctor.py` | Runtime preflight; writes `.autobeamer/env_state.json` | `python tools/doctor.py check` |

> `check_privacy.py` is a standalone PII scanner (not part of the deck pipeline): `python tools/check_privacy.py <path>`.

## Theme Validation

| Tool | Purpose | Example |
|------|---------|---------|
| `test_themes.py` | Compile-test all themes (+ optional layout stress test) | `python tools/test_themes.py` |
| `test_themes.py --layouts` | Full 5×8 layout stress test (40 compilations) | `python tools/test_themes.py --layouts` |
| `test_themes.py --theme dark` | Test single theme only | `python tools/test_themes.py --theme dark` |

## Quick Build

```powershell
# Compile single deck
.\build_clean.ps1                    # default cvgdiff-beamer
.\build_clean.ps1 template-lib-demo  # compile specific deck
.\build_clean.ps1 all                # compile all .tex files
```
