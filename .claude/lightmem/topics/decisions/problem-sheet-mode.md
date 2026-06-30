# Decision: problem-sheet mode + unified exercise component + theme refresh

Status: active · Date: 2026-06-30 · Branch: problem-sheet-design

## Context
Need a self-study **problem-sheet** deliverable (intensive-math: guided problems + hints +
gap-free answer key) as Beamer PDF, built on the existing AutoBeamer ecosystem. Exercise
macros were re-invented per deck with two competing star conventions. Separately, the
teal/navy default themes were judged unimaginative.

## Decisions
1. **New skill `autobeamer-problem-sheet`** — a problem-sheet *mode* that reuses the create
   pipeline (plan→draft→answer-key→build→validate→review), not a parallel system. Default
   output: problems + hints in the body, **gap-free worked solutions in `\appendix`**.
   Distilled from a pasted Markdown reference skill, re-targeted to Beamer, fused with
   [proof-rigor-p0] (answer key is P0 gap-free, gated by naive-reader P2).
2. **Unified exercise component `template-lib/components/comp-exercise.sty`** — one
   difficulty convention `\TLdiff{1|2|3}` (⭐ calc / ⭐⭐ verify / ⭐⭐⭐ insight); macros
   `\TLprobtitle \TLsubq TLhints \TLhint \TLconcept \TLmisconception \TLsoltitle \TLqed
   \TLanswerkeynote \TLsrcnote`. Existing decks keep their local macros (no migration).
3. **Validator** gains `--mode problem-sheet` (accepts the comp-exercise macros OR literal
   习题/提示/解答; requires `\appendix`; solutions must follow `\appendix`).
4. **Theme refresh** — 8 new palettes + an orthogonal **chrome** option (`moloch`/`metropolis`).
   Default light = `slatecoral` (auto-Moloch); default dark = `rosepine`. Chrome wiring +
   dark-mode fixes (title-page secondary text `TLtitlesub`, table header `TLtheadfg`, dark
   result/warn fills `TLposfill`/`TLnegfill`, `text=TLink` on all block nodes) live in
   `theme-base.sty`/`comp-*` and are non-breaking (light defaults identical).

## Why
Reuse over reinvention; gap-free answer keys are non-negotiable; one star convention ends
the per-deck drift; the theme system already supported drop-in palettes (one DeclareOption
each), so the refresh is low-risk and fully switchable.
