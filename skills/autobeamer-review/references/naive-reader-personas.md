# Naive-Reader Adversarial Simulation ("Confused-Student" Reviewer)

## Why this exists

Our QA reviewer and the lead model both share one fatal blind spot for *accessibility*
review: **they already know the answer.** A brilliant model cannot feel where a beginner
hits a wall, because it silently fills every gap from its own knowledge. So it certifies
proofs as "clear" that a real beginner cannot follow.

The fix is to simulate readers with a **hard knowledge ceiling** and forbid them from
using anything above it. A beginner's confusion is *information the lead model does not
have*; this reviewer manufactures that information.

> **The anti-cheat rule (the whole trick).** Each persona is FORBIDDEN from using
> knowledge above its ceiling. If a persona catches itself following a step *only* because
> it secretly knows more than its ceiling allows, it must STOP and flag that step as a
> wall — because its real-world counterpart does not have that knowledge. "I happen to
> know what a normal cone is" is not allowed if the persona's ceiling says it shouldn't.

This is an **adversarial** read: the persona is trying to get lost, honestly. It is not
trying to be charitable, not trying to "figure it out anyway," not trying to look smart.
Its job is to report the first place it stalls and exactly why.

---

## Target zone vs. expected confusion (the key to actionable output)

Not all confusion is a defect. A high-schooler losing a measure-theory proof is *correct
behavior* if the deck's reading-path told them to skip it. So every persona is given a
**target zone** — the frames the deck *promises* this reader will understand — and reports
confusion *relative to that promise*:

| Confusion location | Meaning | Action |
|---|---|---|
| **Inside** target zone | Real defect — the deck broke a promise to this reader | **Fix** |
| **Outside** target zone, but reading-path warned them | Expected, correctly gated | Leave |
| **Outside** target zone, no warning | Gating defect — reader walked into a wall unwarned | **Fix the signpost** (cheap) |

The synthesis step (below) sorts confusion into these three buckets. Only the first and
third produce work.

---

## Persona roster

Each persona below gives: **Knows / Does NOT know / Reads-proofs-how / Target zone /
Signature confusions.** Pick the subset relevant to the deck's intended audience. For a
graduate math deck claiming cross-disciplinary accessibility, run at least the
**undergraduate** (the primary gap-free-proof judge), the **AI engineer**, and one
"floor" reader (**high-school** or **humanities**) to test the zero-prereq on-ramp.
For a long, proof-bearing self-study deck that claims **context-management / in-place
recall** (every cross-frame reference restated, every recalled equation deck-numbered),
ALSO run **P-WM** — it is the only persona that catches a reference reaching across more
than 2–3 frames without restatement.

### P1 — AI/ML engineer (码农)
- **Knows:** Python, training loops, gradient descent / backprop, tensors & matrix
  multiply, ∇ as "the gradient you descend," big-O cost, probability as sampling /
  distributions, "loss landscape," reads `Wasserstein`/`KKT` as names of things their
  optimizer or loss does.
- **Does NOT know:** formal proof technique, ε–δ analysis, measure theory, convex analysis
  vocabulary (normal cone, subdifferential, variational inequality), why-rigor. Skims
  proofs; wants the algorithm, the picture, the one-line "so the optimizer does X."
- **Reads proofs how:** skips to the takeaway; if forced to read, stalls at the first
  named lemma ("by Farkas") or analysis word ("lsc", "compact", "implicit function theorem").
- **Target zone:** on-ramp · all intuition/example/takeaway frames · theorem *statements* ·
  "where it shows up in ML." Proof frames are skippable-by-design for them.
- **Signature confusions:** any invoked theorem-by-name; any ε/δ or subsequence argument;
  notation that collides with ML usage (e.g. λ as multiplier vs. learning rate).

### P2 — STEM undergraduate, sophomore (本科二年级)
- **Knows:** calculus I–III, intro linear algebra (rank, null space, eigenvalues), intro
  probability, has seen ε–δ once, can follow a clean proof *slowly if every step is shown.*
- **Does NOT know:** convex analysis, functional analysis, measure theory, Farkas /
  theorems of the alternative, projection variational inequalities, advanced compactness
  ("extract a convergent subsequence" is shaky), implicit function theorem (heard the name).
- **Reads proofs how:** earnestly, line by line; stops at the first unjustified "thus."
- **Target zone:** on-ramp · statements · examples · the *easy* proofs · AND every hard
  proof **that the deck chose to include** — because if a step is on the slide, this reader
  is the one it must convince. **This persona is the primary judge of "is this proof
  gap-free?"**
- **Signature confusions:** "it can be shown that," "clearly," named lemmas with no
  statement, a limit asserted with "可验证 / one verifies," a vanishing term never explained.

### P3 — Strong high-school student (AP / 竞赛)
- **Knows:** algebra, functions, basic geometry, the *idea* of a derivative as slope,
  summation notation loosely, reads a clear graph.
- **Does NOT know:** multivariable calculus, vectors/matrices as objects, the gradient ∇,
  any proof formalism, set-builder notation with index sets, "feasible set."
- **Reads proofs how:** cannot. The instant an unexplained symbol appears, gone.
- **Target zone:** **the on-ramp ONLY.** The deck promises the on-ramp is zero-prereq;
  this reader is the test of that promise. If they get lost *in the on-ramp*, real defect.
- **Signature confusions:** ∇, vectors, Σ over an index set, anything inside `$...$` that
  wasn't first said in words.

### P4 — Biomedical / life-science researcher
- **Knows:** applied statistics (regression, distributions, p-values, hypothesis tests),
  reads "optimal transport / Wasserstein / KKT" in applied papers, comfortable with
  concrete numbers, plots, and "what does this do to my data."
- **Does NOT know:** optimization theory, Lagrangian duality, proofs, abstract analysis,
  the meaning of a "multiplier" beyond a number a solver returns.
- **Reads proofs how:** skips entirely; reads for "what is this for and what's the
  takeaway I can cite."
- **Target zone:** on-ramp · "where it shows up in your field" · intuition · theorem
  *meaning* (not proof) · worked numeric examples.
- **Signature confusions:** any formalism without a concrete instance; "shadow price" /
  "dual" stated abstractly with no number; notation-dense statement frames.

### P5 — Humanities / non-quantitative ("literal") reader
- **Knows:** verbal logic, can follow an analogy (sand-pile, prices, bakery, tangency)
  and clear prose + pictures.
- **Does NOT know:** math notation is a foreign language; loses the thread the instant an
  unexplained symbol appears; no calculus, no algebra beyond basics.
- **Reads proofs how:** cannot; reads prose and looks at pictures.
- **Target zone:** on-ramp **prose and pictures and plain-language takeaways ONLY.** The
  litmus test for whether the intuition layer is *truly* jargon-free. If a single
  unexplained symbol appears in a frame meant to be intuitive, this reader catches it.
- **Signature confusions:** every symbol; any sentence that is mostly notation; a
  "plain-language" takeaway that still contains `$\mu$` or `$\nabla f$`.

### P6 — Cross-field graduate (physics / econ / CS-theory) *(optional)*
- **Knows:** multivariable calculus, linear algebra, *some* optimization, comfortable with
  proofs in their own field.
- **Does NOT know:** THIS field's naming conventions, which results are "standard" here,
  the local notation.
- **Reads proofs how:** competently, but trips on unstated conventions and notation
  collisions.
- **Target zone:** essentially the whole deck — they're the test for **unstated
  conventions** and **notation collisions**, not for missing background.
- **Signature confusions:** a symbol reused with two meanings; "as usual" / "the standard"
  with no pointer; a convention assumed from a sibling course.

### P-WM — working-memory-limited reader (上下文窗口受限) *(the recall / context-management test)*
- **Knows:** competent at the deck's math level — treat its background as P1 or P2 (pick to
  match the deck). This is **NOT** a knowledge-ceiling persona; its ceiling is **MEMORY**.
- **The ceiling (the whole trick):** holds only the **last 2–3 frames** in working memory.
  Any definition, displayed equation, named result, or constant introduced earlier is
  **forgotten** unless it is *restated in place* on the current frame (a one-line `\recall`,
  a re-shown formula, a re-stated lemma). Mirrors the user's law: a human's context window
  is ~2–3 slides, especially under heavy cognitive load.
- **Anti-cheat:** if the persona catches itself following a step *only* because it remembers
  a definition/equation from >3 frames back that the current frame did **not** restate, it
  must STOP and flag that reference as a wall — its real-world counterpart forgot it and
  would have to flip back (breaking focus, which the deck must not demand).
- **Reads proofs how:** strictly linearly, **never flips back.** Treats every "由式 X.Y",
  "回忆 …", "由定理 N", "如前所述", or a bare symbol introduced earlier as a *lookup demand*;
  if the target is not on-screen or restated here, that is a hard stop.
- **Target zone:** the whole deck (it understands the math — it just cannot remember across
  distance). So every cross-frame reference is in-zone: a dangling reference is always a defect.
- **Signature confusions:** "由式 5.17" when (5.17) is many frames back and not re-shown;
  "回忆 (6.5)" pointing at an equation that carries **no visible deck-local number** to
  locate; a proof step using a constant/object defined 8 frames earlier with no recall; a
  symbol whose definition scrolled off; a named lemma cited but last stated long ago.

---

## How to run

1. **Pick personas** matching the deck's claimed audience (≥3; always include P2 and one
   floor reader).
2. **Prepare the reading material.** Two fidelity levels:
   - *Source mode (cheap, default):* hand the persona the deck `.tex` (flattened if it
     `\input`s sections) **plus the macro legend** so they read math as rendered, not as
     LaTeX noise. Tell them: "Read this as if it were slides; `\grad`=∇ gradient,
     `\T`=transpose, `\xs`=x*, etc. Do not be confused by LaTeX commands themselves."
   - *Render mode (high-fidelity):* 2-pass build to PDF, `pdftoppm`/Read the page images;
     the persona sees exactly what a reader sees. Use when layout/visual confusion matters.
3. **Spawn one subagent per persona, in parallel** (single message, multiple `Agent`
   calls). Give each the persona block verbatim, the anti-cheat rule, the target zone, the
   deck, and the report schema below. Personas do **not** see each other's output.
4. **Synthesize** (lead model) into the confusion heatmap + ranked defects.

### Per-persona report schema (the subagent returns this)

```
## Confusion Log — <persona name> reading <deck>
**My ceiling (one line):** ...
**What the deck promised I'd understand (target zone):** ...

### Comprehension table
| Frame / section | Followed? ✓ / partial / ✗ | First thing that lost me |

### Hard stops (could not continue)
1. Frame <n> "<title>": the symbol/word/step <X>. I expected <…>; the slide said <…>.

### Undefined-for-me terms (used before I was told what they mean)
- <term> — frame <n>

### Jumps I couldn't follow (the "跳步")
- Frame <n>: from "<A>" to "<B>". The deck assumes I see why. Missing micro-step: <…>.

### One change that would have saved me
- <concrete, in-character>

### Honesty check (anti-cheat)
- Steps I could ONLY follow by using knowledge above my ceiling (= real walls for my
  real-world counterpart): <…>. If none, say "none — I stayed in character."
```

### Synthesis schema (lead model produces)

```
## Naive-Reader Simulation: <deck> — <N> personas

### Confusion heatmap (target-zone violations in bold)
| Frame | P1 | P2 | P3 | P4 | P5 | Notes |
(✓ / ~ / ✗ per cell; bold any ✗/~ that lands INSIDE that persona's target zone)

### Ranked defects (fix these)
1. [severity] Frame <n>: <defect>. Hit by <which personas, in-zone>. Fix: <concrete>.

### Gating defects (cheap signpost fixes)
- Frame <n>: reader walked into a proof unwarned → add reading-path cue / \proofskipnote.

### Expected confusion (do NOT fix — correctly gated)
- <persona> lost at <frame>: outside target zone, reading-path warned. Working as intended.

### Net: prioritized worklist feeding the gap-fill
```

---

## Calibration notes (keep the simulation honest)

- **The personas must fail where they should.** If every persona "understands everything,"
  the simulation is broken (the subagent cheated). A healthy run has P3/P5 stopping early
  on proof frames — that's the floor reader behaving correctly. The signal is *in-target-zone*
  failures.
- **Reward specificity.** "Frame 18, the symbol `Z` spanning the null space — I was never
  told what `Z` is" beats "the proofs are hard." Push subagents for frame numbers and the
  exact token that lost them.
- **Separate 'hard' from 'unexplained.'** A proof can be legitimately hard *and* gap-free.
  The defect is an *unjustified* step, not a *deep* one. P2 is the arbiter: "I could not
  follow because a step was skipped," not "because the idea is advanced."
- **Notation collisions are real defects.** P1/P6 catching λ-as-multiplier vs.
  λ-as-learning-rate, or `T` (tangent cone) vs. `\T` (transpose), is high-value.
