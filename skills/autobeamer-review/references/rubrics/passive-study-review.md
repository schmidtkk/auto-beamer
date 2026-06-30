# Passive-Study Review Rubric

Review `passive-study` decks as self-contained learning artifacts, not live talks.

## Critical Checks

- Background is introduced before it becomes a blocker.
- The deck shields cross-disciplinary learners from avoidable frustration without diluting rigor.
- Definitions and notation are self-contained and followed by worked examples.
- Explanations use complete sentences where a missing speaker would otherwise create ambiguity.
- Exercises have hints and backup solutions, but the main learning path does not depend on guessing.
- **Proofs are gap-free (P0 — a single breach fails the deck).** Every proof: states its goal up front; shows *every* logical step including the "easy"/trivial bound (no "thus / hence / clearly / 可验证 / 易证 / one verifies / 类似地" standing in for a step); defines every term on or before the frame it is first used (e.g. "链/chain", "c-次微分", "normal cone"); keeps one logical move per displayed line; and splits across frames rather than compressing. Every named result (Farkas, KKT, IFT, Rockafellar, …) is stated in one line with why its hypothesis holds here, on the same frame.
- **Understanding-first (P0 — overrides gap-free).** Gap-free is necessary but NOT sufficient: a proof/definition that is logically complete yet *purpose-unclear* (目的不明) fails. Every definition, theorem, and construction states — in plain language, BEFORE the formalism — the question it answers ("为什么需要它 / 它是什么"). A multi-frame proof opens with a strategy/map frame, and each step frame says where it is, what the previous frame bought, and what this frame gets. A polished result with no reasoning path (problem → idea → result) is a breach.
- **Reader working memory ≈ 2–3 frames (P0).** Anything referenced from further back is restated in place (recall), not merely cited. Any displayed equation referenced later carries a VISIBLE deck-local number; source-document equation numbers are not deck anchors.
- **No concept landmines (P0).** No term/notation/named object is used before it is introduced in-deck; the deck never assumes the reader will consult an external page/encyclopedia for a main-path concept. External links are depth-only — the deck is fully understandable with every link unclicked.

## Failure Modes

- Treating the deck like speaker prompts.
- Saying "obvious", "standard", or "trivial" for non-trivial steps.
- Introducing many symbols without glossary or concrete examples.
- Relying on external references for background that the deck promised to teach.
- **Proof gaps (P0):** a term used before its definition; an assertion ("one verifies", "易证") replacing a shown step; a jump from premise to conclusion with the micro-step missing; a named lemma invoked without its statement; several logical moves crammed into one displayed line; the *easy* half of an equivalence/bound silently dropped; or a multi-page source proof compressed to ≤3 lines. **The undergraduate persona P2 (the gap-free-proof arbiter) must be run to surface these — see the skill's proof-rigor gate.**
- **Result-dump / paper-style (P0):** a theorem/definition/step stated with no "what question / what idea / why care" — a polished result without the reasoning that produces it; reads like a paper, not a lesson.
- **Concept landmine (P0):** a term/notation/named object used before its in-deck introduction, or offloaded to an external source the deck promised to teach.
- **Infinite-memory assumption / no recall (P0):** a cross-frame reference (>2–3 frames back) with no in-place restatement; or a "回忆 式 X.Y" whose target has no findable deck-local number (dangling reference to a source-document number).
- **Proof-splitting paradox (P0):** a proof split into gap-free micro-frames that are context-free shards — no strategy/map frame, no per-frame "where are we / what this step buys."
- **Perfunctory motivation:** a frame titled 动机/为何 that lists virtues (marketing) instead of showing what a naive/older approach FAILS to do here.
