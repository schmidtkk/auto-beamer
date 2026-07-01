# Language-Quality Gate (语言质量门) — canonical

> **Single source of truth for the AutoBeamer language gate.** Every skill that
> judges prose points here instead of restating it: `autobeamer-review`
> (`proofread`, `excellence`), `autobeamer-create` (drafting + quality gate),
> `autobeamer-validate` (the mechanical step), `autobeamer-problem-sheet`, the
> wave agents, and `CLAUDE.md`. Do not duplicate these definitions elsewhere.

The gate has two halves that work together:

| Half | Owner | Catches |
|------|-------|---------|
| **Mechanical** | `tools/lang_lint.py` (deterministic) | foreign-prose leakage, AI-flavor fillers, proof-hedges, connector clusters, intensifier density |
| **Judgment** | the reviewing model | mistranslation, clunky/redundant phrasing, notation drift, scientific correctness of each relation |

Run the mechanical half first, then judge the rest:

```bash
python tools/lang_lint.py lint <deck>.tex --mode <mode>     # add --strict to fail on advisories
```

It is **LaTeX-aware**: every protected span (math, command names, verbatim,
comments, `\ref`/`\cite`/`\label`/path arguments) is stripped before any check,
so the deck's symbols and macros never trip a finding.

---

## Governing principle — 先保信息，再谈风格 (preserve information first)

Borrowed from the 说人话 (shuorenhua) de-AI-flavor method: **clean style is a
fact-preserving operation, never a content overhaul.** When naturalness and
accuracy conflict, accuracy wins — you remove filler and translation-ese, you do
**not** touch the protected spans below. In a teaching deck the stakes are
higher than in chat: a "smoothed" inequality or a dropped index is a scientific
error, not a style nit.

---

## The four axes (语言四性)

Judge prose in the deck's **own** language (a Chinese deck is judged by Chinese
standards, not English grammar rules).

- **流畅性 (fluency).** Reads naturally in the target language; no translation-ese
  (翻译腔) or machine-translated phrasing; sentences cohere and flow.
  **HARD GATE — zero foreign-language prose leakage:** not one English (or other
  non-target) sentence/clause in a Chinese deck. A single pasted English line
  (brief/spec text is the classic offender) is a CRITICAL defect. English
  *terms*/proper nouns (Wasserstein, Prokhorov) and anything inside `$...$` are
  fine; English *prose* is not. **This is the one axis `lang_lint.py` enforces
  mechanically.**
- **准确度 (accuracy).** Faithful to source meaning; the precise word (用词精确 —
  no near-miss / mistranslation); terminology & notation consistent; units and
  symbols correct. *(judgment)*
- **优雅性 (elegance).** Economical and non-redundant (删可删之词); one idea per
  clause; varied sentence structure, not clause-piling; "辞达" first, then polish.
  Flag bloated, clunky, or repetitive phrasing. *(judgment; `lang_lint.py` helps
  via fillers + intensifier density)*
- **科学性 (scientific correctness).** The math/science in BOTH prose and displays
  is correct: verify each equation/inequality's **direction, sign, indices, and
  quantifiers**; check dimensional/notational consistency; claims are supportable.
  Read every relation — do NOT skim — this is where a copied sign slip or a
  flipped inequality is caught. *(judgment — never skip)*

When the deck **is** English, also apply: subject-verb agreement, article usage,
tense consistency, parallel structure, academic register.

---

## Protected spans (never flag, never rewrite)

`lang_lint.py` strips these before linting; a human editor must respect them too.

1. **Math** — `$...$`, `\[...\]`, `\(...\)`, and `equation/align/gather/multline/
   array/cases/...` environments.
2. **Command names & opaque args** — every `\macro` token; the arguments of
   `\label/\ref/\eqref/\cite/\url/\href/\includegraphics/\input/\texttt/\color/...`.
   (Prose *inside* `\textbf{}`, `\emph{}`, `\TLtakeaway{}`, `\deflab{}`,
   `\frametitle{}` is **not** protected — it is linted.)
3. **Verbatim** — `verbatim/lstlisting/minted/\verb`.
4. **Numbers, units, identifiers, file paths, error/log text, quoted titles.**
5. **Terminology** — established English/Latin terms and proper nouns.

---

## De-AI-flavor taxonomy (说人话, tuned for academic teaching Chinese)

Severity follows the shuorenhua tier model. `[auto]` = enforced by `lang_lint.py`;
`[judge]` = model judgment.

### Tier 1 — always flag `[auto]` (MAJOR; fails the default gate)
Empty openers/summaries and vague-significance filler:
`值得注意的是` · `需要(注意/指出/强调)的是` · `综上所述` · `总(的来说/而言之)` ·
`一言以蔽之` · `归根结底` · `众所周知` · `正如我们所知` · `随着…的发展` ·
`在…的今天` · `起着至关重要的作用` · `扮演着重要的角色` · `具有重要意义` ·
`不容忽视` · `赋能` · `助力` · `一站式/全方位/保姆级`.
→ Fix: delete the wrapper and state the point directly.

### Proof-hedges — `[auto]`, mode-gated severity
`显然` · `易证/易知/易见` · `不难发现/看出/证明` · `可验证` · `类似地` ·
`同理可证` · `读者自证`. These double as **proof-gap smells**: CRITICAL in
`passive-study`/`problem-sheet` (the P0 proof-rigor gate — supply the step, do not
hedge), advisory elsewhere (sketches allowed in a talk).

### Tier 2 — cluster flag `[auto]` (MINOR; ≥2 in one frame)
Connector pile-ups `然而/因此/此外/从而/进而/于是`; light-verb translation-ese
`进行(了)…`. → Keep one connector, cut the rest; replace 进行 with a real verb.

### Tier 3 — density flag `[auto]` (MINOR; deck-wide over-use)
`重要/优化/深刻/深远/极大/极其/十分/非常`. → Most occurrences delete or replace
with a concrete statement.

### Structural anti-patterns `[auto]` + `[judge]`
- **不是X，而是Y** stacked (≥2/frame) — say Y directly. *(also: 二元对立陷阱)*
- **首先…其次…然后…最后** mechanical chains — use logical transitions.
- `[judge]` only: rhetorical-setup ("试想…如果…"), negation-list openers, the
  trilogy habit (三连排比), unsourced "研究表明" without a cite.

---

## Two-pass procedure (for a human/model pass beyond the script)

1. **Protect.** Mark the spans above; everything else is editable.
2. **Rewrite around them.** Delete fillers/empty summaries; de-translationese;
   tighten redundancy — without altering any protected span.
3. **Fact pass.** Re-read every displayed relation for 科学性 (sign/direction/
   indices/quantifiers/dimensions). A "smoothing" that changed a symbol is a bug.
4. **Residual audit.** Re-run `lang_lint.py`; confirm zero CRITICAL/MAJOR, and
   that the meaning is unchanged.

---

## Rubric deductions (canonical numbers — the rubric cites these)

| Finding | Severity | Deduction |
|---------|----------|-----------|
| Foreign-language prose leakage (English sentence/clause in a Chinese deck) | CRITICAL | **−10 each** |
| Scientific error in a displayed relation (sign/inequality/index/quantifier/dimension) | CRITICAL | **−15 each** |
| Proof-hedge replacing a step (`passive-study`/`problem-sheet`) | CRITICAL — P0 | **−15 each** |
| Tier-1 AI-flavor filler / empty summary | MAJOR | −3 each |
| Mistranslation / clunky-redundant prose (准确度·优雅性) | MAJOR | −3 each |
| Tier-2 cluster / Tier-3 density / structural | MINOR | −1 each |

---

## Adjudication notes (avoid false hard-fails)

- A proof-hedge **token in a rhetorical title** (e.g. "为什么…不是*显然*的？") is not a
  gap — `lang_lint.py` surfaces it as a candidate; the reviewer dismisses it.
- `显然/易证` are CRITICAL *candidates* in teaching modes: confirm the step is
  actually skipped before counting the −15. The script finds; the model judges.
- Tier-2/Tier-3 are advisory — they fail the gate only under `--strict`.

## Provenance

Taxonomy adapted from **说人话 (shuorenhua)** — `github.com/MrGeDiao/shuorenhua`:
protected spans, severity tiers, phrase/structure blacklists, two-pass fact+residual
audit — re-tuned from chat/marketing register to academic teaching-deck Chinese.
