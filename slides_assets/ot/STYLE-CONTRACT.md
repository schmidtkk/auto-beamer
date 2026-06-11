# STYLE CONTRACT — 最优传输定性理论讲义 (Codex 各节必须遵守)

You are drafting **one section fragment** of a Chinese passive-study (导师自学) Beamer
deck on **Villani, _Optimal Transport: Old and New_, Part I**. The commander owns the
master file `ot-qualitative-zh.tex` (preamble, notation, frontmatter) and the style
exemplar `slides_assets/ot/sec0-prelim.tex`. **Read `sec0-prelim.tex` first and match
it exactly** in notation, density, figure style, worked-example habit, and tone.

Your fragment is `\input` into the master. **Do NOT** add `\documentclass`,
`\usepackage`, `\begin{document}`, preamble, or redefine any macro listed below — they
already exist. Your file contains only `\TLsection{...}` (once, at top) + `\begin{frame}…\end{frame}` blocks.

---

## 0. Hard rules (violating any = broken build or rejected diff)

1. **unicode-math brace rule.** ALWAYS brace a sub/superscript whose argument is a
   macro: write `\int_{\X}`, `\sum_{\X}`, never `\int_\X`. Macros `\X \Y \Z \R \N \E \Pp`
   expand to `\mathcal/\mathbb` (unicode-math) and break a bare `_\X`/`^\X`.
2. **No CJK inside math mode.** Chinese characters and Chinese punctuation
   （，。：“”（）！） must stay in **text mode**. Wrap only math symbols in `$…$`.
   Do NOT put Chinese (esp. curly quotes “ ”) inside `\text{…}` in math — it breaks
   xeCJK+unicode-math. If you need a Chinese word next to math, close the math first.
3. **No beamer overlays:** never `\pause`, `\onslide`, `\only`, `\uncover`, `\visible`.
4. **≤ 3 colored template-lib boxes per frame.** Prefer **0–1**. Plain text first.
5. **No `\tiny`.** Smallest allowed is `\scriptsize` (use sparingly, tables/captions).
6. **No external images / `\includegraphics` of web assets.** Every figure is **TikZ**,
   redrawn in teal, Chinese labels, attributed `{\scriptsize 据 Villani 图 x.y 重绘。}`.
7. **No `\section`/`\subsection`/theorem packages.** Use `\TLsection` for the section
   divider and the labels below. amsmath/amssymb/tikz/pgfplots are loaded.
8. Every `\begin{frame}` has a Chinese title. Every frame must have ≥1 substantive
   element (definition, equation, figure, table, worked step). No 3-bullet filler frames.

## 1. Notation macros (ALREADY DEFINED — use, never redefine)

`\R \N \E \Prob` · `\X \Y \Z`(spaces) · `\Pp`(P) `\Ppp{p}`(P_p) `\Pac` ·
`\coup{\mu}{\nu}`(=Π(μ,ν)) · `\law \Id \supp \dom` · `\pf{T}{\mu}`(=T_#μ pushforward) ·
`\Wp{p}`(=W_p) `\Wtwo` · `\ctr{\psi}`(=ψ^c, c-transform) `\cctr{\psi}`(=ψ^{cc}) ·
`\inner{a}{b}` `\abs{x}` `\norm{x}` · `\dd`(= \,d) · `\cost`(=c) `\half` `\eps`(=ε)
`\To`(⟶) `\wkto`(⇀ weak conv) `\subjto`(s.t.).
If you truly need a new macro, define it **locally inside the frame**, never globally.

## 2. Command vocabulary (template-lib + deck-local)

- `\TLsection{N \ 标题}` — section divider (your file starts with exactly one).
- `\TLterm{术语}` — first use of a key Chinese term (accent bold).
- `\deflab{定义 5.1（名称）。}` — bold dark-primary inline label for 定义/定理/命题/引理.
  **Default: state theorems/definitions as `\deflab{…}` + plain text + displayed math.**
- Colored blocks — reserve for the ONE central item per frame (keynote/theorem/pitfall):
  `\TLinfoblock{标题}{正文}` (primary) · `\TLresultblock{标题}{正文}` (positive result) ·
  `\TLwarnblock{标题}{正文}` (pitfall/limitation) · `\TLalertblock[标题]{正文}` (alert).
- `\TLtakeaway{…}` — **exactly one per frame**, the slide's 要点 (renders as 要点。).
- Exercises: difficulty `\diffI \diffII \diffIII` (★/★★/★★★); hint line `\hint{…}`.
- Two-column: `\begin{columns}[T] \begin{column}{0.5\textwidth}…\end{column}…\end{columns}`.

## 3. Passive-study pedagogy (acceptance gates)

- **Motivation → formal object → worked example within 2 slides** for every definition.
- Every major theorem: prerequisite reminder + a concrete instance/example.
- Mark beginner pitfalls with `\TLwarnblock`.
- Each section ends with **2–3 exercises** (`\diffI→\diffIII`) with inline `\hint`s;
  full solutions go to the backmatter appendix (Part 6 owns them — you only pose them,
  but ALSO append a `% SOLUTION:` comment after each exercise so Part 6 can collect it).
- Complete sentences; the reader has no speaker.

## 4. Figures (TikZ only, teal palette)

Use theme colors: `TLprimary` (teal lines/boxes), `TLaccent` (orange highlights/arrows),
`TLpos`/`TLneg` (green/red), `TLink`/`TLinkSoft` (text/muted), `TLprimaryTint` (fills).
Arrow tips: `>={Stealth[length=5pt]}`. Always add the `据 Villani 图 x.y 重绘。` caption.
Keep diagrams ≤ ~6cm tall so the frame never overflows. See sec0 figures as templates.

## 5. Density (per frame)

≤ 7 bullets · ≤ 2 displayed equations · ≤ 5 new symbols · ≤ 3 boxes. If exceeded → split
into another frame (NEVER `[shrink=…]`, NEVER `\tiny`). Page count is irrelevant; clarity
and completeness are the only metrics. Splitting a dense topic across more frames is GOOD.

## 6. Validator anchors (Chinese deck)

`validate_deck.py --mode passive-study` greps English substrings. The backmatter (Part 6)
carries the `Glossary/Notation`, `Exercises`, `References/Bibliographical notes` anchors —
but in YOUR section, title the exercise frame e.g. `习题 N · Exercises` so the keyword exists.

## 7. Self-check BEFORE returning (definition of done)

From repo root `/data/weidong/auto-beamer`, run TWO checks. **`exit=0` is NOT enough —
Overfull is a warning, not an error, so the build "succeeds" while frames overflow.**
You MUST grep the log and see ZERO `Overfull` lines. **Run TWO passes** on your
isolated wrapper — a single pass makes the metropolis progress bar overflow (it reads
a stale `\inserttotalframenumber`), producing dozens of FALSE cascading overfulls that
grow ~11.67pt per frame. Two passes fix the total and clear those phantoms:
```bash
xelatex -interaction=nonstopmode -output-directory=build -jobname=_check_secN _check_secN.tex > /dev/null 2>&1
xelatex -interaction=nonstopmode -output-directory=build -jobname=_check_secN _check_secN.tex > /dev/null 2>&1; echo "exit=$?"
grep -n "Overfull" build/_check_secN.log        # MUST be empty (after the 2nd pass)
grep -n -E "^! |Undefined control sequence|Runaway" build/_check_secN.log   # MUST be empty
```
(Do NOT use `-halt-on-error` for the overfull check — it stops before the log records
all overfull boxes. If you see overfulls that grow by a constant ~11.67pt each frame,
that is the progress-bar artifact — run the 2nd pass; do NOT try to "fix" those frames.) If `grep Overfull` prints ANY line, find the offending frame and
**FIX IT** before returning. The whole master must compile AND show zero `Overfull`.

### How to fix an Overfull \vbox (a frame that is too tall)
A `Overfull \vbox (N pt too high) detected at line L` means the frame whose `\end{frame}`
is at/near line L has more content than fits. **House rule: SPLIT, never shrink.**
1. **Split** the frame into two `\begin{frame}...\end{frame}` (e.g. "定理 X" + "定理 X 的证明",
   or "(一)"/"(二)"). This is the preferred fix and is ENCOURAGED — page count is free.
2. Remove `\medskip`/`\vspace`/`\\[..]` padding; merge short lines.
3. NEVER use `[shrink=N]`, `\tiny`, or `\resizebox` on a whole frame to force fit.

Report: changed files, slide count added, compile exit code, the `grep Overfull` output
(should be empty), and any place you simplified the source.

## 8. Faithfulness

The source is the ground truth. Read the assigned `slides_assets/ot/src/chN-*.txt`
extraction (and you may also consult the PDF pages cited). Preserve Villani's theorem
numbers where helpful (e.g. 定义 5.1, 定理 5.10). Where the source "only sketches" a
proof, the mentor deck **shows the steps** (per house style). Never invent results not in
the source; if you must abridge a long technical proof, say so and keep the key ideas +
move the hardest computation to a clearly-labeled backup intent (note it for Part 6).
