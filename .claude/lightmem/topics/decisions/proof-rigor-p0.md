---
id: proof-rigor-p0
kind: decision
summary: Gap-free proofs are a P0 acceptance gate for mentor (passive-study) decks; the QA gates now enforce it
status: active
tags: [proof, rigor, gap-free, passive-study, review, naive-reader, p0]
supersedes: []
superseded_by: null
created_at: 2026-06-17
updated_at: 2026-06-17
---

# Proof rigor is a P0 gate for mentor decks

## Context

A passive-study (mentor) deck shipped with sketch-proofs: the upper bound was dropped, the
goal of the proof was never stated, the term "链/chain" was used undefined, and a multi-step
argument was compressed into 2–3 lines. The user flagged this as a P0 flaw that frustrates
readers. Root cause: the *infrastructure to catch it already existed but was optional* — the
naive-reader **P2 persona is the "gap-free-proof arbiter"** and the cognitive-load model
weights un-shown "jumps" highest, but neither runs by default; the only enforced create-loop
rubric docked merely −10 (MAJOR) for a "proof sketch" with no detection sub-rules.

## Decision

Gap-free proofs are **P0 (a single gap fails review)** for `passive-study` and proof-bearing
`active-socratic` decks. A proof is *gapped* if it: omits its goal; uses
"thus/hence/clearly/可验证/易证/one verifies/类似地" for a real step; uses a term before it is
defined; invokes a named result (Farkas/KKT/IFT/Rockafellar) without its one-line statement +
applicability on-frame; compresses several logical moves into one displayed line; drops the
*easy* half of a bound/equivalence; or sketches what the source proves in full. Fix by
**splitting into more frames + adding micro-steps**, never by deleting the proof.

## Consequences (edits made 2026-06-17)

1. `skills/autobeamer-review/references/rubrics/passive-study-review.md` — added P0 proof-rigor
   critical check + failure mode.
2. `skills/autobeamer-review/SKILL.md` — added a "Proof-rigor is a P0 gate" section making
   **`naive-reader` with persona P2 MANDATORY** for proof-bearing mentor decks.
3. `skills/autobeamer-create/references/workflows/full-create-guide.md` — elevated proof-gap to
   **−15 CRITICAL** with detection sub-rules; added a PROOF-RIGOR GATE to the passive-study
   acceptance checklist.
4. `CLAUDE.md` quality rubric — added a Critical "Proof gap (mentor)" −15 row.

Related: see auto-memory `applied-readers-need-scaffolded-proofs` and `ot-proofs-must-be-gapfree`.
