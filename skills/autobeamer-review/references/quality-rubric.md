# Quality Rubric (canonical, mode-parameterized)

> **Single source of truth for deck scoring.** `CLAUDE.md`,
> `autobeamer-create/references/workflows/full-create-guide.md` (§5c), and the
> `autobeamer-finisher` agent point here instead of restating a table. Language
> and science rows are owned by
> [language-quality-gate.md](language-quality-gate.md); the per-mode review
> rubrics in [rubrics/](rubrics/) add mode-specific pedagogy criteria.

Start at **100**. Deduct per issue. Run `tools/lang_lint.py` and
`tools/check_layout.py` first so the mechanical rows are filled in before judgment.

## Base deductions (all modes)

| Severity | Issue | Deduction |
|----------|-------|-----------|
| Critical | Compilation failure | −100 |
| Critical | Equation/box-interior overflow | −20 |
| Critical | TikZ diagram overflows slide boundary | −15 each |
| Critical | Undefined control sequence / citation | −15 |
| Critical | **Scientific error in a displayed relation** (sign, inequality direction, index, quantifier, dimension — verify EVERY relation) | −15 each |
| Critical | **Foreign-language prose leakage** (English sentence/clause in a Chinese deck; terms & `$...$` exempt) | −10 each |
| Critical | Overfull hbox > 10pt | −10 |
| Major | Content overflow inside a colored box | −10 per box |
| Major | Sparse slide (≤3 text-only bullets, or U < 0.60) | −5 each |
| Major | TikZ label overlap | −5 |
| Major | Missing references slide | −5 |
| Major | Table not centered / `\toprule` merges with title bar | −3 to −5 |
| Major | Notation inconsistency | −3 |
| Major | **AI-flavor filler / empty summary** (tier-1, see gate) | −3 each |
| Major | Mistranslation / clunky-redundant prose (准确度·优雅性) | −3 each |
| Major | `\resizebox`/`\tiny` shrinking body prose below `\scriptsize` | −3 each |
| Minor | `\vspace` overuse (>3/slide) · font-size reduction · tier-2/3 language advisory | −1 each |

## Mode-specific deductions

**`passive-study` / proof-bearing `active-socratic` (P0 — a single one fails review):**

| Issue | Deduction |
|-------|-----------|
| Proof gap — goal unstated; a step unjustified (`thus/hence/clearly/可验证/易证/不难/类似地`); a term used before defined; the easy half of a bound dropped; several logical moves compressed into one line | **−15 each (CRITICAL — P0)** |
| Proof shown as sketch / "omitted" / "similarly" instead of in full (`passive-study`) | **−15 per proof (CRITICAL — P0)** |
| "Understanding-first" breach — gap-free but *purpose-unclear* (目的不明) definition/proof; result with no question/idea/why; multi-frame proof with no map/recall | **−15 each (CRITICAL — P0)** |
| Named result (Farkas/KKT/IFT/…) invoked without its one-line statement + applicability on-frame | −5 each |
| Missing glossary / exercise / bibliographical-notes section | −5 each |

**`academic-presentation`:** missing backup slides −3. **`problem-sheet`:** worked
solutions before `\appendix` (struggle-first breach) −10; missing hints/answer-key −5 each.

## Thresholds

| Mode | Ready | Refine | Must fix |
|------|-------|--------|----------|
| `academic-presentation` | ≥ 90 | 80–89 | < 80 |
| `passive-study` / `problem-sheet` | ≥ 95 | 90–94 | < 90 |

The higher passive-study bar reflects the P0 proof-rigor and understanding-first gates.
