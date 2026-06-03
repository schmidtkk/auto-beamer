# AutoBeamer Skill Framework Adversarial Review

Date: 2026-06-04

Basis: local skill framework, plugin manifests, LightMem roadmap, local
skill-creator guidance, affaan-m/ECC, and shanraisshan/claude-code-best-practice.
Evidence inventory: `docs/reviews/2026-06-04-skill-framework-evidence.md`.

## Executive Verdict

The current AutoBeamer skill framework is strong as a Beamer layout/build/review
toolkit, but it is not yet a three-mode autonomous learning deck system. The
dominant failure mode is taxonomy drift: the repo now wants passive study,
active Socratic study, and academic presentation, while the current skills still
encode Presentation vs Mentor. That mismatch affects creation, review,
validation, packaging, and image sourcing.

If left unchanged, an agent will often generate a polished deck while missing
the user's intended learning philosophy. In the active Socratic case, it will
likely teach too much and ask too little. In the passive study case, it may
produce dense mentor slides without the explicit frustration-shielding,
background-first pedagogy the mode requires. In the academic presentation case,
it may confuse self-study completeness with scholarly talk economy.

## Critical Findings

### 1. The requested three-mode taxonomy is not implemented

Severity: Critical

Current state:
- Creation asks only for Presentation or Mentor.
- Local project context defines only Presentation Deck vs Mentor Deck.
- Review and validation criteria are also Presentation/Mentor.

Why this is dangerous:
- The active Socratic mode is not a deck-density variant. It is a different
  interaction model: the agent should mentor through questions, exercises,
  thought experiments, checkpoints, and learner-produced work.
- Passive study is also not merely "Mentor mode". It requires an explicit goal:
  reduce frustration for cross-disciplinary readers with weak priors by adding
  context, background, and affective pacing.
- Academic presentation is not equivalent to the current Presentation mode
  unless the skill explicitly enforces scholarly narrative, contribution
  positioning, literature context, precision, timing, and talk-style selectivity.

Required correction:
- Rename and rebase the mode taxonomy around:
  `passive-study`, `active-socratic`, and `academic-presentation`.
- Make mode selection mandatory in both creation and review.
- Treat old `Mentor` and `Presentation` as compatibility aliases only.

### 2. Review mode parity is missing

Severity: Critical

Current state:
- `autobeamer-review` has actions such as proofread, audit, pedagogy,
  excellence, and devils-advocate.
- None of those actions are routed by passive, active Socratic, or academic
  presentation mode.

Why this is dangerous:
- A passive-study deck should be reviewed for prerequisite shielding, concept
  laddering, background richness, enjoyable pacing, and frustration traps.
- An active-Socratic deck should be reviewed for question quality, productive
  struggle, withheld exposition, exercise sequencing, and whether the learner
  must actually do work.
- An academic-presentation deck should be reviewed for talk economy, narrative
  arc, claims-to-evidence precision, related-work positioning, and Q&A readiness.
- A generic "pedagogy" score cannot safely judge all three.

Required correction:
- Add a mode argument to review actions.
- Maintain separate review rubrics:
  - Passive: background map, prerequisite bridges, worked examples, cognitive
    load smoothing, common confusions.
  - Active: question ladder, exercise solvability, checkpoints, answer
    withholding discipline, reflection prompts.
  - Academic: narrative, rigor, contribution framing, timing, citations,
    results clarity, backup slide readiness.

### 3. Active Socratic mode conflicts with the current creation pipeline

Severity: Critical

Current state:
- The create pipeline proceeds material analysis -> interview -> structure plan
  -> drafting -> figures -> quality loop.
- That is a production pipeline for deliverables, not a Socratic learning loop.

Why this is dangerous:
- The active mode should not start by drafting a complete explanatory deck.
  It should first build a question path and require learner engagement.
- If the agent drafts full explanations too early, it destroys the mode's core
  purpose: learners reinvent, internalize, and learn how to explore.

Required correction:
- In active mode, replace "draft slides" with a mentor-loop architecture:
  1. Diagnose learner priors.
  2. Pose a motivating puzzle.
  3. Ask one hard-but-solvable question.
  4. Wait for learner response or produce a worksheet checkpoint.
  5. Reveal hints progressively.
  6. Convert solved insights into slides only after the discovery path is clear.
- The generated deck should preserve the discovery sequence, not flatten it into
  exposition.

### 4. Hard-rule drift can make the model violate non-negotiable constraints

Severity: High

Current state:
- `AGENTS.md` caps colored boxes at three per slide.
- `autobeamer-create` and `autobeamer-layout` allow five blocks in Mentor mode.
- `AGENTS.md` says new decks use `template-lib`; multiple skills still instruct
  legacy `bluecard`, `goldcall`, and `eqbox`.

Why this is dangerous:
- When a skill and `AGENTS.md` conflict, agents will inconsistently obey one or
  the other. The result is unstable generation and review.
- Legacy macro guidance will leak into new decks and break the template-library
  boundary.

Required correction:
- Make the hard-rule layer a single source of truth.
- Remove or quarantine legacy macro guidance behind an explicit "legacy deck"
  branch.
- Keep max three colored boxes for every mode, and express passive/active
  richness through slide count, plain text, tables, diagrams, exercises, and
  proof frames rather than extra boxes.

### 5. Validation can falsely pass incorrect decks

Severity: High

Current state:
- `autobeamer-validate` compiles only once.
- The aspect ratio check calls a roughly 4:3 page size "16:9".
- Static overlay checking omits `\uncover`.

Why this is dangerous:
- Beamer layout often needs two passes.
- A false 16:9 check can certify wrong output geometry.
- `\uncover` can slip through despite a hard no-overlays rule.

Required correction:
- Always run two-pass XeLaTeX for `.tex` validation unless explicitly proving no
  aux-dependent layout exists.
- Correct the expected 16:9 page-size ratio.
- Replace ad hoc grep checks with a static validator that parses frames and
  checks all banned overlay commands, block counts, `\tiny`, references order,
  appendix placement, and mode-specific requirements.

## Mode-by-Mode Review

### Passive Study Mode

Purpose:
Teacher-led, comprehensive knowledge delivery for learners entering an unfamiliar
field. The agent should make the experience enjoyable and prevent background
gaps from becoming frustration.

Current fit:
- Partially covered by existing Mentor mode.
- Missing explicit cross-disciplinary prior diagnosis.
- Missing explicit frustration-shielding and weak-field-prior handling.
- Missing mode-specific review rubric.

Creation gaps:
- Needs a prerequisite graph before outline creation.
- Needs "background capsule" slides before formal sections.
- Needs a deliberate concept ladder: intuition -> terminology -> example ->
  formalism -> worked application -> recap.
- Needs a "reader might be stuck here" pass for every major transition.
- Should allow long decks, but not by increasing boxes per slide.

Review gaps:
- Review should flag unexplained field assumptions, jargon jumps, missing
  context, and failure to build intuitions before definitions.
- Review should check for affective pacing: no long runs of unexplained symbols,
  no abrupt proof jumps, no "obvious" language.

Adversarial failure scenario:
An agent creates a dense "Mentor" deck with complete proofs but assumes the
reader already knows measure theory, notation, historical motivation, and why
the problem matters. It is technically complete but pedagogically hostile.

### Active Socratic Study Mode

Purpose:
Mentor-led discovery. The learner works through questions, thought experiments,
and math exercises to reinvent the core ideas.

Current fit:
- Essentially absent.
- "Exercises with hints" in Mentor mode is not enough.

Creation gaps:
- Needs a Socratic question generator, not just a slide generator.
- Needs progressive hint policy.
- Needs checkpoints where the learner must compute, reason, or explain before
  proceeding.
- Needs answer keys separated from prompts, likely in backup slides or a
  companion worksheet.
- Needs "do not reveal too early" constraints.

Review gaps:
- Review should judge whether questions are productive, ordered, and solvable.
- Review should flag slides that answer the question before the learner has had
  a chance to struggle.
- Review should inspect exercise difficulty progression and hint granularity.
- Review should require pen-and-paper tasks for math-heavy material.

Adversarial failure scenario:
An agent labels a passive explanatory deck "Socratic" because it contains a few
questions. The learner is not forced to do any work; all answers are revealed
immediately; curiosity is simulated rather than created.

### Academic Presentation Mode

Purpose:
Formal scholarly communication for conference talks, seminars, journal clubs,
and research sharing. The deck should organize knowledge into a clear narrative,
position contributions in the literature, and maintain rigor and precision.

Current fit:
- Closest to existing Presentation mode.
- Still under-specified for scholarly context and related-work positioning.

Creation gaps:
- Needs talk-type routing: conference, seminar, journal club, defense, reading
  group, or invited lecture.
- Needs contribution/context/result narrative spine.
- Needs explicit literature-positioning slides and citation discipline.
- Needs "what is the audience supposed to remember?" gates.
- Needs backup-slide generation focused on anticipated scholarly questions.

Review gaps:
- Review should judge claim precision, evidence, citation placement, novelty
  framing, scope control, timing, and Q&A risk.
- Review should not apply passive-study completeness standards blindly; academic
  talks need selective compression.

Adversarial failure scenario:
An agent produces a self-study explainer for a 20-minute conference slot. It is
accurate and rich, but it fails as a talk because it buries contribution,
overloads background, and exceeds timing.

## Image Sourcing Review

Current state:
- The repo already has `paper_parser.py`, which extracts embedded PDF images,
  image dimensions, aspect ratios, bounding boxes, sections, full text, and
  source PDF metadata.
- The create skill still recommends external sources for pure math visuals:
  POT examples, Wikimedia Commons, arXiv figures, and textbook illustrations.

Adversarial assessment:
- External web/CDN retrieval is a weak default for user-provided documents.
  It can introduce visual mismatch, license ambiguity, dead links, CDN
  dependence, and figures that do not match the source argument.
- Source-document extraction has higher fidelity, lower dependency risk, better
  attribution, and better alignment with the user's material.
- External images still have value for canonical concepts or when the input
  document lacks usable visuals, but they should be fallback, not default.

Required precedence rule:
1. Extract figures directly from user-provided PDFs with `paper_parser.py`.
2. If a concept needs a visual but the PDF figure is unsuitable, render/crop the
   relevant PDF page region or create a precise TikZ diagram.
3. Use external images only when the source material lacks a suitable visual and
   the external source is canonical, stable, licensed/attributable, and improves
   learning or communication.
4. Never depend on CDN URLs at build time. Download, attribute, and store assets
   locally under the deck's asset directory.

Mode-specific image policy:
- Passive study: prefer source figures plus explanatory overlays/TikZ redraws to
  reduce unfamiliarity.
- Active Socratic: prefer diagrams that can be progressively reasoned about;
  avoid figures that reveal the answer too early.
- Academic presentation: prefer source paper figures or faithful simplified
  redraws; never substitute generic stock-like visuals for contribution figures.

## Best-Practice Alignment Score

| Area | Score | Rationale |
|---|---:|---|
| Trigger/discovery metadata | 5/10 | Descriptions exist, but no three-mode triggers or `agents/openai.yaml`. |
| Progressive disclosure | 4/10 | Only one reference file; create skill is too monolithic. |
| Workflow separation | 5/10 | Six skills exist, but no command/agent orchestration for mode routing. |
| Verification integrity | 5/10 | Visual check is strong; static checks and aspect ratio are weak. |
| Memory hygiene | 5/10 | LightMem now exists; older `memories/` references still conflict. |
| Mode fidelity | 2/10 | Requested three modes are not first-class. |
| Image fidelity | 6/10 | Parser exists; skills do not prioritize it enough. |

## Recommended Refactor Shape

The next version should use a thin routing skill plus mode references:

```text
skills/autobeamer-create/
  SKILL.md
  references/
    modes/passive-study.md
    modes/active-socratic.md
    modes/academic-presentation.md
    images/source-document-first.md
    validation/mode-gates.md
  agents/openai.yaml

skills/autobeamer-review/
  SKILL.md
  references/
    rubrics/passive-study-review.md
    rubrics/active-socratic-review.md
    rubrics/academic-presentation-review.md
  agents/openai.yaml
```

The create skill should do only this:
1. Determine mode.
2. Load the matching mode reference.
3. Parse source documents and extract figures first.
4. Produce an outline or Socratic path.
5. Gate before drafting.
6. Draft in batches.
7. Validate with mode-specific gates.

The review skill should do only this:
1. Determine artifact type and mode.
2. Load the matching rubric.
3. Compile/visual-check if source is available.
4. Report findings by severity.
5. Propose targeted fixes, not generic advice.

## Bottom Line

AutoBeamer has good raw components: XeLaTeX build discipline, layout tools,
visual validation, TikZ standards, and a PDF parser. The weak point is the skill
framework's learning philosophy layer. The current system can make slides; it
cannot yet reliably choose and enforce the right educational contract.
