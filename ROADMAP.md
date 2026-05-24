# Roadmap — Beamer Deck Auto

> Living document tracking planned improvements across template system, tooling, and documentation.

---

## Phase 1: Skill Content Upgrade ✅ (Completed 2025-05)

- [x] Audit and align all 7 skill files with `SKILL.md` spec
- [x] Fix `font-config.sty` CJK handling for Windows/macOS/Linux
- [x] Standardize theme color tokens (11 `TL`-prefixed tokens)
- [x] Improve layout optimizer suggestions

## Phase 2: Template Diversity & Stability 🔄 (In Progress)

- [x] **Task 8**: Comparative analysis of external `Noi1r/beamer-skill` template
- [x] **Task 9**: Add semantic inline commands (`\TLpos`, `\TLneg`, `\TLhl`, `\TLmuted`)
- [x] **Task 9**: Update `CATALOG.md` with new command documentation
- [x] **Task 10**: Add acknowledgements to `README.md`
- [ ] **Task 9 follow-up**: Extract `theme-base.sty` to eliminate ~280 lines of boilerplate duplication across 4 theme files

---

## Phase 3: Template System Hardening

**Goal**: Eliminate duplication, add theme variety, ensure all themes compile identically.

### 3.1 Extract `theme-base.sty`

- Move ~70 lines of shared boilerplate (beamer wiring, font setup, footer, `\TLtitlebg`/`\TLresetbg`) into `template-lib/themes/theme-base.sty`
- Each theme file reduces to: `\input{theme-base}` + 11 `\definecolor` lines
- Net reduction: ~210 lines across 4 files → single `theme-base.sty` (~70 lines)

### 3.2 Fifth Theme: `minimal`

- Inspired by Madrid/Default aesthetic from external repos
- Clean, high-contrast, no dark mode assumptions
- Good fallback for non-specialized talks

### 3.3 Theme Validation Script

- Create `tools/test_themes.py` that compiles a minimal deck with each theme
- Verify identical structure (same frames, same layouts)
- Flag any theme-specific compilation warnings

### 3.4 Layout Stress Tests

- Compile every layout with every theme (4×8 = 32 combinations)
- Check for overfull boxes, missing commands, font warnings
- Generate a pass/fail matrix

**Estimated effort**: 2–3 sessions

---

## Phase 4: Testing & CI

**Goal**: Automated quality gate for every commit.

### 4.1 Compilation Test Suite

- `tests/test_smoke.py` — verify each theme compiles a minimal deck
- `tests/test_layouts.py` — verify each layout environment loads
- `tests/test_components.py` — verify each component command is defined
- All tests run with `xelatex -interaction=nonstopmode`

### 4.2 Visual Regression (Optional)

- Screenshot key slides at 1920×1080 after each build
- Pixel-diff against approved baselines
- Flag unexpected visual changes

### 4.3 CI Pipeline

- GitHub Actions workflow: `latex.yml`
- Triggers on push to `main` and on PRs
- Steps: checkout → TeX Live install → theme compile → layout compile → test suite

**Estimated effort**: 2 sessions

---

## Phase 5: Documentation & Community

**Goal**: Make the template library self-documenting and contributor-friendly.

### 5.1 Complete CATALOG.md

- Add usage examples for every command
- Include "When to use" guidance per layout
- Add visual thumbnails (compiled PDF screenshots)

### 5.2 Contribution Guide

- `CONTRIBUTING.md` with theme creation checklist
- Layout authoring guide (step-by-step)
- Component naming conventions (`TL` prefix requirement)

### 5.3 Example Gallery

- `examples/` directory with 4–6 complete decks:
  - `demo-academic.tex` — full academic talk
  - `demo-medical.tex` — medical/biotech talk (teal theme)
  - `demo-poster.tex` — poster-style layout
  - `demo-minimal.tex` — minimal clean talk
- Each example demonstrates different theme + layout + component combinations

**Estimated effort**: 2–3 sessions

---

## Phase 6: Advanced Features (Future)

- **Custom theme generator**: CLI tool that takes a hex palette and generates a complete theme file
- **BibTeX integration**: Auto-generate references slide from `.bib` file
- **Beamer → PPTX bridge**: Export key slides to PowerPoint for collaborators
- **i18n support**: First-class Chinese/Japanese/Korean template variants
- **Dark/light toggle**: Single deck that supports both modes via `\TLtogglelight`/`\TLtoggledark`

---

## Version Milestones

| Version | Phase | Status |
|---------|-------|--------|
| `v0.1` | Phase 1 | ✅ Complete |
| `v0.2` | Phase 2 | 🔄 In progress |
| `v0.3` | Phase 3 | Planned |
| `v0.4` | Phase 4 | Planned |
| `v1.0` | Phase 5 | Planned |
| `v2.0` | Phase 6 | Future |
