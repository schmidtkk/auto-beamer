# Alignment Check — Anti-Drift Gate

The final quality loop (Phase 5) catches compile/layout/pedagogy defects, but it
does **not** catch *semantic drift* — a deck that is clean yet no longer matches
the Phase 2 plan or the user's original demands. This gate runs **between waves**
(after Wave 2 drafting, before Wave 3 polish) to guard the mission.

Run by the **leader** (the create skill), not the subagent that produced the
output — an independent check is the point. On any drift, bounce the work back to
the Drafter with specific deltas before approving Wave 3.

## Inputs

- The approved **structure plan** from Wave 1 (sections, per-section objective,
  planned figures, new notation, mode + gates).
- The **original demands**: user's topic, audience/level, mode, duration/effort,
  and any explicit must-haves.
- The **Wave-2 output**: the `.tex` deck, the `image_index.json` (with
  `requests`/`adoption`), and the build/validation reports.

## Checklist

### Coverage & scope
- [ ] Every planned section is present; none silently dropped.
- [ ] No unplanned section/topic added without justification (scope creep).
- [ ] Each section meets its stated learning objective / narrative purpose.
- [ ] Slide count is consistent with the planned duration/effort.

### Figures (uses the image index)
- [ ] Every **planned figure** appears, or its omission is recorded with a reason.
- [ ] Every **image request** in `image_index.json` is resolved
      (`adopted` / `tikz` / `external` / `dropped` — none left `open`).
- [ ] Adopted source figures match their `key_idea`; low-confidence adoptions
      were visually confirmed or replaced by TikZ.
- [ ] External images carry provenance; no build-time hotlinks.

### Fidelity
- [ ] Notation is consistent with the plan and across slides.
- [ ] Mode is preserved (e.g. a `passive-study` deck still teaches background,
      has worked examples, exercises, glossary, references — not telegraphic).
- [ ] Claims/results still trace to the source material; nothing invented.
- [ ] Mode-specific gates from [mode-gates.md](mode-gates.md) are satisfiable.

## Verdict

```
## Alignment Report: <deck>
- Sections planned vs present : N / N   (missing: …, added: …)
- Objectives met              : N / N
- Planned figures used        : N / N   (omitted w/ reason: …)
- Image requests resolved      : N / N   (open: …)
- Notation / mode fidelity     : OK / drift: …

Verdict: ALIGNED  |  DRIFT — return to Drafter with the deltas above
```

Only an **ALIGNED** verdict proceeds to Wave 3. A mid-draft mini-check (sections
so far vs plan) is encouraged for long decks so drift is caught early.
