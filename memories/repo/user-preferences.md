# User Preferences — Beamer Deck Auto

> **Agent Note**: This file contains CRITICAL preferences that must be respected.
> Before any design/plan task, search `memories/MEMORY_INDEX.md` for keyword tags,
> then read the relevant sections below.
>
> **Keyword Tags**: `theme`, `box`, `block`, `layout`, `mentor deck`, `self-study`,
> `exercise`, `example`, `OT`, `optimal transport`, `Villani`, `pushforward`, `measure`,
> `CJK`, `Chinese`, `font`, `math font`, `serif`

---

## Theme Preference
- **Modern clean style** over classic academic
- Preferred: Teal (`#00796b` + `#e65100`) over Academic (navy + red)
- Dark mode acceptable for cinematic presentations

## CJK Font Preference
- **Source Han Serif SC (思源宋体)** Medium (body) + Bold (titles)
- Never use the system-default Noto Sans CJK Regular — too thin for slides
- Fonts live in project-local `.fonts/` (gitignored); auto-detected by font-config Priority 1.5
- Download from Adobe GitHub:  `09_SourceHanSerifSC.zip` from release 2.003R
- Only 2 files needed: `SourceHanSerifSC-Medium.otf` + `SourceHanSerifSC-Bold.otf`
- No preamble override required — font-config picks them up automatically
- For mixed CJK+English decks, Source Han Serif SC Medium pairs well with KpMath

## Math Font Preference
- **KpMath Regular+Bold** (Kepler project) — template default since 2026-06-05
- Reasons: heavier serif than Latin Modern Math, designed for math typography,
  pairs well with Source Han Serif SC CJK, already in TeX Live
- See `template-lib/template-lib.sty` line 73-74; override per-deck if needed

## Layout Preference
- **Max 3 blocks per slide** — never 4+ blocks
  - Alternative 1: Split into multiple slides
  - Alternative 2: Convert blocks to plain text/body content
  - Blocks reserved for: keynote, theorems, properties, key takeaways
- Prefer `equal height group` for column balance
- `goldcall` must always span full width (outside `columns`)

## Content Density
- Prefer readable over dense
- Image scale ≥ 20% (cap height ≥ 7pt for PDF, ≥ 11pt for screen)
- Wide images (AR > 1.8): use full-screen or split across slides
- Tables with AR > 2.5: typeset as LaTeX `tabular`, not image

## Workflow Preference
- Ask before major structural changes (splitting frames, removing content)
- Preview key pages as PNG before finalizing
- Commit incrementally with detailed messages
