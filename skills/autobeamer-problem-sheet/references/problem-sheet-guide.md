# Problem-Sheet Authoring Guide

The law for building a self-study problem sheet. Distilled from a reference
`problem_sheet` skill (Markdown/MathJax) and **re-targeted to XeLaTeX Beamer**, then
fused with this repo's gap-free-proof P0, reader-calibration, and source-first-figure
rules. Read this before drafting any TeX.

> The reader learns by **deriving**, not by reading. Your job is to engineer a chain of
> questions so that each concept feels *inevitable* by the time the reader reaches it.

---

## 1. The logical chain (write it BEFORE any TeX)

A sheet without a chain is a pile of disconnected exercises. Answer these six questions
first, on paper:

1. **Final insight/skill** the reader will hold (one sentence).
2. **Minimal prerequisites** (3–5 items) — anything beyond these must be introduced in-sheet.
3. **The 3–6 conceptual steps** between prereq and insight → these become the **Parts**.
4. For each step: **the key question**, and **what the reader derives**.
5. **The 2–3 most tempting misconceptions** → design `\TLmisconception` traps / counterexample sub-parts around them.
6. **Where figures help** → list source-first figures to adopt (see §8).

**Common chain patterns** (pick one): Definition→Properties→Optimization→Application ·
Motivation→Special case→General case→Edge case · Concrete→Abstract→Concrete.

The chain is the PLAN artifact. Hand it to the reader/leader before drafting.

---

## 2. Parts

- Each Part = **one conceptual step**; output of Part N is the input context for Part N+1.
- 3–6 Parts. More than 6 → split the sheet.
- Open each Part with a `\TLsection{…}` divider **and** a plain-prose background frame
  that names the question this Part answers, connects to the previous Part's conclusion,
  and gives any physical/applied intuition. **No new formal definitions in the background**
  — just the question.
- Every Part **ends with a result the reader is proud of** (an arrival, not a cliffhanger).

---

## 3. Problems

Structure of one problem (one frame; `\TLprobtitle{N}{name}{level}` in the title):

- **Descriptive title** ("谱上界", not "习题 2"). 1–2 sentence setup introducing only the
  notation used in this problem.
- **Sub-parts ≤4**, laddered with `\TLsubq{a}`:
  - **(a)** completable by a careful reader *without* hints — warms up the mechanism.
  - **(b)** = (a) + exactly **one** new idea.
  - **(c)** = generalize / find a counterexample / connect to another concept / reflect.
- Never make one sub-part require **two unrelated new ideas** — split into two problems.

---

## 4. Hint craft (`TLhints` / `\TLhint`)

2–3 hints, auto-numbered 提示 1/2/3, ordered **weak→strong**. The first hint must
**preserve the attempt**.

**DO** — point to the specific tool:
- the lemma/identity/technique: *"用问题 1 的分解"*, *"令 $y=Q^\top x$ 并观察分子分母"*
- the key algebraic move: *"展开交叉项，注意 $m-g$ 是 $\mathcal I$-可测的"*
- the obstruction they'll hit: *"直接求逆会丢对称性，考虑 Cholesky 分解"*

**DON'T**:
- give the answer or the final expression
- hint every sub-part (reserve hints for genuinely hard steps)
- write generic filler (*"仔细想想"*, *"用定义"*).

---

## 5. Concept-introduction protocol (the most-violated rule)

Classify every concept the sheet touches:

| Type | Define? | How |
|------|---------|-----|
| Standard (calculus, linear algebra, basic prob.) | No | use freely |
| Graduate-standard (measure theory, functional analysis) | **Yes, always** | `\TLconcept{term}{formal}{直觉}` |
| Domain-specific (filtration, Rayleigh quotient, scatter matrix) | **Yes, always** | `\TLconcept{…}` |
| New notation introduced mid-problem | **Yes, inline** | one sentence |

`\TLconcept{term}{formal statement}{plain-language gloss}` renders the formal definition
plus a 直觉 line. Place it **immediately after** the sentence that first uses the concept.

**Prohibited** (each is a `目的不明`/concept-landmine P0 risk):
- introducing a concept and using it in the same breath without a note;
- notation before its declaration;
- assuming "filtration / kernel trick / scatter matrix …" is known;
- defining something in Part I, using a related undefined variant in Part IV;
- "recall that …" for anything non-trivial without restating (reader memory ≈ 2–3 frames).

---

## 6. The gap-free answer key (`\appendix`)

This sheet ships full solutions — and **every solution is a gap-free proof (P0)**; a single
breach fails the deck. See [proof-rigor-p0] and the passive-study rubric. A solution is
**gapped** if it: omits its goal; uses *thus / hence / clearly / 可验证 / 易证 / one
verifies / 类似地* for a real step; uses a term before it is defined; invokes a named
result (Farkas/KKT/IFT/Rockafellar) without a one-line statement + why its hypothesis
holds here; compresses several moves onto one displayed line; **drops the easy half** of a
bound/equivalence; or sketches what should be shown in full.

Mechanics:
- `\appendix` opens the answer key; first frame carries `\TLanswerkeynote` (struggle-first).
- One problem per `\TLsoltitle{N}{name}` frame; close with `\TLqed`.
- **Split** long solutions across frames — but avoid the **proof-splitting paradox**:
  every continuation frame opens with a one-line *map/recall* ("上一帧得到 X，本帧用它证 Y").
  Splitting into context-free shards is itself a P0 breach.
- **Fix gaps by adding micro-steps / more frames, never by deleting the proof.**
- **Source traceability**: `\TLsrcnote{对应《…》第 N 题}`, and **verify the statement
  matches its solution** — exercise-citation drift is a known failure (drop false `#N`).

---

## 7. Difficulty & pacing

- `\TLdiff{1|2|3}` = ⭐ calculation / ⭐⭐ verification / ⭐⭐⭐ insight (the one true convention).
- Difficulty **rises monotonically** within each Part; Part I is confidence-building, the
  final Part is stretch/synthesis. Order problems so a reader never hits a spike.
- Every abstract definition has a concrete worked instance nearby (a sub-part or the
  background prose).
- Calibrate to a reader profile: `autobeamer-calibrate set-profile <P>` → `budget` sizes
  hint depth and per-frame load; `gradient-audit` confirms the monotone ramp.

---

## 8. Figures (source-first)

Adopt original figures from the source PDF **first** (`tools/paper_parser.py
extract-images` / `render-pages`, then `tools/image_index.py`); hand-drawn TikZ
(`autobeamer-tikz`) is the last rung, for diagrams the source lacks. A problem that needs
a picture (a region, a tree, a plot) should *show* it, not describe it.

---

## 9. Anti-patterns

| Anti-pattern | Why it fails | Correction |
|--------------|--------------|------------|
| Open with a formal definition | reader has no reason to care | open with the motivating question |
| `\TLconcept`-less use of $L^2(\Omega,\mathcal F,\mathbb P)$ | alienates non-experts | define it, or say "有限方差的随机变量" |
| Hint = answer | reader learns nothing | hint points to the step, not the result |
| 6-sub-part problem | exhausting, unfocused | split; one main takeaway per problem |
| Part IV uses a Part I concept with no reminder | reader has forgotten | inline recall: "由问题 2，…" |
| Sheet ends on a hard open problem | reader feels defeated | put open extensions in an optional 延伸 section |
| Solution compressed onto one line / "易证" | gap-free P0 breach | split into micro-steps across frames |
| Micro-frames with no map/recall | proof-splitting paradox (P0) | each continuation states what it inherits and gets |

---

## 10. Quality checklist (before delivery)

**Chain** — Parts form a chain; final Part delivers the promised insight; no dead ends.
**Concept hygiene** — every non-standard concept/notation defined before use; counterexamples for the tempting misconceptions.
**Problems** — descriptive titles; (a) hint-free; hints point to specific tools; no sub-part needs two new ideas.
**Answer key** — gap-free (no 易证/thus); easy halves kept; named results stated inline; multi-frame solutions carry map/recall; ends `\TLqed`.
**Pacing** — monotone difficulty; every abstraction has a concrete anchor.
**Beamer** — compiles 2-pass; no Overfull > 10pt; validator passes `--mode problem-sheet`; `check_layout` clean.

---

## 11. Beamer mechanics (cheat sheet)

```latex
\usepackage[slatecoral]{template-lib/template-lib}  % or [rosepine] for dark
% components auto-loaded: comp-exercise gives the macros below.

\begin{frame}{\TLprobtitle{2}{谱上界}{2}}          % 习题 2 · 谱上界  ★★
  证明 \TLsubq{a} $R(x)\le\lambda_{\max}$，并 \TLsubq{b} 指出取等方向。
  \begin{TLhints}
    \TLhint{正交对角化 $A=Q\Lambda Q^\top$，令 $y=Q^\top x$。}
    \TLhint{把 $R$ 写成 $\lambda_i$ 的凸组合。}
  \end{TLhints}
  \TLtakeaway{考查：谱定理 + 凸组合上界。}
  \TLsrcnote{对应《习题集》第 2 题。}
\end{frame}

\appendix
\begin{frame}{附录 · 习题解答}\TLanswerkeynote\end{frame}
\begin{frame}{\TLsoltitle{2}{谱上界}}
  \TLsubq{a} … 每一步都写出 …  \TLqed
\end{frame}
```

Build: `./build.sh <deck>` (2 passes). Validate:
`python tools/validate_deck.py static <deck>.tex --mode problem-sheet`. Gate the answer
key with **naive-reader P2**.
