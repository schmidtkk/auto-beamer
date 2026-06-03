# Mode Gates

Use this reference during creation planning and validation. These gates are enforced by `tools/validate_deck.py static` where a source-level check is possible, and reviewed manually where visual or pedagogical judgment is required.

## Shared Hard Gates

- Banned overlays are absent: `\pause`, `\onslide`, `\only`, `\uncover`.
- No user-facing `\tiny`.
- No frame has more than 3 colored template-lib boxes.
- If a Thank You slide exists, References is the slide immediately before it.
- If backup slides exist, `\appendix` appears before the first backup slide.

## `passive-study`

- Background and prerequisite reminders precede formalism.
- Definitions include motivation and worked examples.
- Glossary or notation section is present.
- Exercise frames are present, with hints or backup solutions.
- References or bibliographical notes are present.

## `active-socratic`

- Question frames appear before explanatory answer frames.
- Learner-work attempt gates are present.
- Hints are separated from final answers.
- Solution or reflection frames close each major question ladder.
- The deck does not reveal the core answer before asking for an attempt.

## `academic-presentation`

- Audience and timing are reflected in slide count and density.
- References is second-to-last before Thank You.
- Backup slides appear after Thank You and after `\appendix`.
- Claims have evidence, citations, or backup support.
- Closing has a concrete takeaway, not only future work.
