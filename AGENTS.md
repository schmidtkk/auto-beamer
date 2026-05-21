# Beamer Deck Auto — Agent Guidelines

## If You Are an AI Agent

This repo contains a **three-tier Beamer template library** and **layout optimization tools** for XeLaTeX academic slides.

### Before You Start

1. **Check current project state** — read `CLAUDE.md` for project context
2. **For layout questions** — use `skills/beamer-layout/SKILL.md`
3. **For new slides** — run `python tools/layout_optimizer.py suggest --img W:H --cards N`
4. **For overflow issues** — run `python tools/check_layout.py deck.tex build/deck.log --advise`

### Tool Reference

| Tool | When to Use |
|------|-------------|
| `layout_optimizer.py` | Choosing layout template, generating LaTeX skeleton |
| `check_layout.py` | Auditing slide density, column balance, grammar violations |
| `auto_crop.py` | Removing white margins from embedded images |
| `build_clean.ps1` | Compiling deck (supports parameterized builds) |

### Key Constraints

- **Never** use `2*#1\textwidth` in `\dimexpr` — use `#1\textwidth-#1\textwidth` instead
- **Always** wrap `\@ifundefined` with `\makeatletter`/`
\makeatother` in `\input`'d files
- **Always** use `\providecommand` in layout/component files to prevent duplicates
- **Hardcode** column heights when inside `\budgetwideimg` or `[shrink=N]` frames
