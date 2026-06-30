# Problem-Sheet Mode

Use `problem-sheet` when the deliverable is a sequence of **problems the reader solves** to construct a topic themselves — intensive-math self-study with hints in the body and a gap-free answer key in the `\appendix`. It is the worksheet sibling of `active-socratic`: socratic *teaches by asking inside an exposition*; problem-sheet *is the exercises*, with solutions deferred.

## Learning Philosophy

The reader learns by deriving, not by reading. A problem sheet is an engineered chain of questions in which each definition, theorem, and formula feels *inevitable* by the time it appears, because the preceding problems built the intuition. Motivation precedes formalism; no concept is used before it is introduced; if a result can be derived, it is a problem, not a declaration. Solutions exist to *check against* after an honest attempt — never to replace the struggle.

## Authoring Rules

- Organize into 3–6 **Parts**, each one conceptual step; the result of Part N is the context for Part N+1. Open each Part with plain-prose background naming the question it answers.
- Each problem has a descriptive title and ≤4 sub-parts: (a) accessible without hints; (b) (a) + one new idea; (c) generalize / counterexample / reflect. Never jump two conceptual levels in one sub-part — split instead.
- Difficulty is the unified `\TLdiff{1|2|3}` (⭐ calculation / ⭐⭐ verification / ⭐⭐⭐ insight); difficulty rises monotonically within each Part.
- Hints are 2–3, weak→strong (`TLhints`); the first preserves the attempt (points to a tool, never the answer); reserve hints for genuinely hard steps.
- Every non-standard concept gets a `\TLconcept` note (formal + 直觉 gloss) before first use; design `\TLmisconception` traps for the 2–3 most tempting errors.
- Body shows no full solution. Worked solutions go in `\appendix`, opened by `\TLanswerkeynote`, one (or more) frame per problem, ending `\TLqed`.

## Acceptance Gates

- The Parts form a visible chain and the last Part delivers the insight promised in the introduction; no Part is a dead end.
- Every answer-key solution is **gap-free (P0)**: states its goal, shows every step (no 易证/可验证/thus standing in for a move), keeps the easy half of each bound, states any named result inline with why it applies; multi-frame solutions carry a map/recall line. A single breach fails the sheet — gate with **naive-reader P2**.
- Every concept and every piece of notation is introduced before use; external links are depth-only.
- Difficulty is monotone (no spikes) per `autobeamer-calibrate gradient-audit`; sub-part (a) of each problem is solvable hint-free.
- The static validator passes `--mode problem-sheet` (answer key after `\appendix`; hints not in the same frame as solutions; back-matter carries the `Exercises`/`Appendix` keyword anchors).
