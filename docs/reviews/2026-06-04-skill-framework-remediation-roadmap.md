# AutoBeamer Skill Framework Remediation Roadmap

Date: 2026-06-04

Companion artifacts:
- `docs/reviews/2026-06-04-skill-framework-evidence.md`
- `docs/reviews/2026-06-04-skill-framework-adversarial-review.md`

## Severity Ranking

### P0: Mode taxonomy and review parity

Problem:
The framework currently uses Presentation vs Mentor, but the requested product
contract is passive study, active Socratic study, and academic presentation.

Required changes:
1. Update `autobeamer-create` to require one of:
   - `passive-study`
   - `active-socratic`
   - `academic-presentation`
2. Update `autobeamer-review` so every review action accepts or infers a mode.
3. Treat old Presentation/Mentor terms as compatibility aliases only:
   - Mentor -> passive-study unless the user explicitly asks for Socratic.
   - Presentation -> academic-presentation.
4. Add mode-specific acceptance gates for creation, review, and validation.

Acceptance test:
Given the prompt "make a Socratic deck", the skill must not produce a fully
expository deck first. It must create a question path and learner-work checkpoints.

### P0: Hard-rule single source of truth

Problem:
Hard rules in `AGENTS.md` conflict with skill content.

Required changes:
1. Remove five-block Mentor allowance from create/layout/validate guidance.
2. Keep the max-three-colored-box rule universal.
3. Replace legacy `bluecard`, `goldcall`, and `eqbox` guidance with
   `template-lib` commands for new decks.
4. Move legacy macro guidance into a clearly labeled legacy-only reference.

Acceptance test:
Static search of `skills/autobeamer-*` should find no legacy macro instruction
outside a legacy-only section or file.

### P0: Validation false-pass fixes

Problem:
Validation can certify wrong geometry or illegal overlays.

Required changes:
1. Use two-pass XeLaTeX for `.tex` validation.
2. Correct the 16:9 page-size expectation.
3. Include all banned overlay commands: `\pause`, `\onslide`, `\only`,
   `\uncover`.
4. Add static checks for:
   - colored box count per frame
   - `\tiny`
   - References slide second-to-last before Thank You
   - `\appendix` before backup slides
   - mode-specific required sections

Acceptance test:
A fixture containing `\uncover` must fail validation.

### P1: Source-document-first image policy

Problem:
The framework has a PDF parser but does not make source-document extraction the
default image strategy.

Required changes:
1. In create mode, run `paper_parser.py parse` or `extract-images` whenever the
   user provides a PDF.
2. Add a figure precedence policy:
   - extracted source figure
   - rendered/cropped source page region
   - custom TikZ or redrawn figure
   - external canonical image with attribution
3. Ban build-time CDN dependencies. External assets must be downloaded and stored
   locally with attribution metadata.
4. Add review checks for source fidelity and attribution.

Acceptance test:
Given a PDF with embedded figures, the creation plan should reference extracted
figure files before suggesting web search.

### P1: Progressive disclosure restructure

Problem:
`autobeamer-create` is too monolithic and carries variant-specific detail in the
main skill body.

Required changes:
1. Keep `SKILL.md` as a compact router.
2. Add mode references:
   - `references/modes/passive-study.md`
   - `references/modes/active-socratic.md`
   - `references/modes/academic-presentation.md`
3. Add image reference:
   - `references/images/source-document-first.md`
4. Add validation reference:
   - `references/validation/mode-gates.md`
5. Keep each reference directly linked from `SKILL.md`.

Acceptance test:
`autobeamer-create/SKILL.md` should explain when to load each reference and
should be short enough to scan without crowding out the actual user task.

### P1: Plugin and skill discovery metadata

Problem:
Plugin default prompts and skill metadata do not expose the three modes.

Required changes:
1. Update plugin default prompts to include all three modes.
2. Add `agents/openai.yaml` for each skill where supported by the harness.
3. Use trigger wording that maps user requests to the correct mode.
4. Consider `context: fork` or subagent routing for heavyweight review and
   evidence-gathering passes where supported.

Acceptance test:
Plugin metadata should expose mode-specific default prompts such as passive
study, active Socratic study, and academic presentation review.

## Proposed Implementation Order

1. Patch validation false-pass issues first.
   Reason: wrong validation can hide every other regression.
2. Refactor mode taxonomy in `autobeamer-create` and `autobeamer-review`.
   Reason: this is the product contract.
3. Add mode-specific references and rubrics.
   Reason: keeps the main skills concise and aligns with progressive disclosure.
4. Replace legacy macro guidance with template-lib guidance.
   Reason: prevents new-deck drift while preserving legacy compatibility.
5. Add source-document-first image policy.
   Reason: improves fidelity and reduces external dependency risk.
6. Update plugin/skill metadata.
   Reason: makes the behavior discoverable once the underlying rules are true.
7. Add fixtures and tests for validation and mode-gate behavior.
   Reason: prevents future regression.

## Mode-Specific Acceptance Gates

### Passive Study

- Prerequisite map exists.
- Background context precedes formalism.
- Every major concept follows intuition -> terminology -> example -> formalism.
- Worked examples appear within two slides of definitions.
- Review flags field-prior assumptions and frustration traps.

### Active Socratic

- Question path exists before explanatory slides.
- Learner-work checkpoints are present.
- Hints are progressive and separated from final answers.
- Answers are not revealed before the learner has a task.
- Review flags exposition that preempts discovery.

### Academic Presentation

- Narrative spine states problem, contribution, method, evidence, and takeaway.
- Related-work positioning is explicit.
- Claims are citation-backed or evidence-backed.
- Timing and slide count match talk type.
- Backup slides address likely scholarly questions.

## Completion Audit Against User Objective

| Requirement | Evidence | Status |
|---|---|---|
| Clone and deep-read affaan-m/ECC | Local clone at `/tmp/auto-beamer-review/ECC`; evidence extracted in `2026-06-04-skill-framework-evidence.md`. | Satisfied |
| Clone and deep-read claude-code-best-practice | Local clone at `/tmp/auto-beamer-review/claude-code-best-practice`; evidence extracted in evidence artifact. | Satisfied |
| Read best skill practices | Local `skill-creator` guidance used and cited in evidence artifact. | Satisfied |
| Propose roadmap in LightMem before proceeding | `.claude/lightmem/topics/roadmap.md` contains review roadmap; committed in `c397fda`. | Satisfied |
| Keep LightMem updated at milestones | Roadmap statuses updated for milestones 1-4; inbox notes recorded for milestone events. | Satisfied |
| Commit each milestone | Commits: `c397fda`, `2b6b266`, `94eb618`, plus the final remediation commit containing this artifact. | Satisfied |
| Review all three learning modes | Adversarial review covers passive study, active Socratic study, and academic presentation. | Satisfied |
| Address creation and review | Review artifact covers creation gaps and review gaps for each mode. | Satisfied |
| Evaluate image sourcing strategy | Review and remediation artifacts recommend source-document-first image extraction over web/CDN defaults. | Satisfied |
| Produce adversarial review of framework and content | Evidence, adversarial review, and remediation roadmap artifacts created. | Satisfied |

## Final Note

The most important implementation principle is to separate learning philosophy
from Beamer mechanics. AutoBeamer already has useful mechanics. The next
upgrade should make the educational contract explicit, testable, and reviewable.
