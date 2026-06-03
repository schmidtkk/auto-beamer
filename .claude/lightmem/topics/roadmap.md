---
id: roadmap
kind: roadmap
summary: Versioned delivery plan and milestone targets
status: active
tags: []
supersedes: []
superseded_by: null
created_at: 2026-06-03
updated_at: 2026-06-03
---

# Roadmap

## 2026-06-04 Adversarial Skill-Framework Review

Status: done

Objective: adversarially review the AutoBeamer skill framework against current
skill-design best practices, affaan-m/ECC, shanraisshan/claude-code-best-practice,
and the requested three-mode learning philosophy.

### Milestone 1: Memory and Review Setup

Status: done

Acceptance criteria:
- LightMem gateway blocks are installed in `CLAUDE.md` and `AGENTS.md`.
- `.claude/lightmem/index.md` exists and indexes current topics.
- Requested external repositories are cloned for local deep reading.
- A roadmap for the review is recorded in LightMem before deeper review work.
- A git commit records the milestone.

### Milestone 2: Evidence Inventory

Status: done

Acceptance criteria:
- Local skill files, plugin manifests, repo instructions, and template tooling are
  inventoried with line-referenced evidence.
- External best-practice evidence is extracted from cloned repositories, especially
  skill trigger design, progressive disclosure, orchestration, memory, verification,
  and packaging patterns.
- LightMem milestone note records the evidence inventory.
- A git commit records the milestone.

### Milestone 3: Three-Mode Adversarial Review

Status: done

Acceptance criteria:
- The review separately evaluates passive study, active Socratic study, and
  academic presentation modes for both deck creation and deck review.
- The review identifies mode-routing gaps, contradictory constraints, missing
  acceptance gates, and likely agent failure modes.
- The review evaluates image sourcing strategy, including whether source-document
  figure extraction should be preferred over web/CDN retrieval.
- LightMem milestone note records review completion.
- A git commit records the milestone.

### Milestone 4: Remediation Roadmap

Status: done

Acceptance criteria:
- The final report proposes a concrete refactor plan for mode taxonomy,
  skill/reference structure, validation gates, memory routing, and image extraction.
- Recommendations are ranked by severity and implementation order.
- The goal is audited against all explicit user requirements before completion.
- A final git commit records the completed review artifacts and LightMem updates.

## 2026-06-04 Skill-Framework Remediation Implementation

Status: done

Objective: implement the adversarial review's remediation plan with one git commit
per milestone.

### Milestone 1: Validation and Hard-Rule Drift

Status: done

Acceptance criteria:
- Regression tests cover the validation false-pass issues and hard-rule drift.
- Validation guidance requires two XeLaTeX passes, correct 16:9 aspect-ratio
  checks, complete overlay-command detection, and template-lib block counting.
- Create/layout/review guidance enforces the universal three colored-box limit.
- Current authoring guidance no longer prescribes legacy box/image macros.

### Milestone 2: Three-Mode Create/Review Taxonomy

Status: done

Acceptance criteria:
- `autobeamer-create` exposes `passive-study`, `active-socratic`, and
  `academic-presentation` as first-class modes with direct reference links.
- `autobeamer-review` routes each mode to a distinct review rubric.
- Reference files encode the different learning philosophies and acceptance gates.

### Milestone 3: Source-Document-First Image Policy

Status: done

Acceptance criteria:
- Creation guidance extracts and inventories figures from provided PDFs before
  web search or external image lookup.
- A source-document-first reference defines fallback, local-file, and attribution
  rules for external images.
- Review guidance checks image provenance, source-document use, hotlinks, and
  attribution.

### Milestone 4: Plugin Discovery Metadata

Status: done

Acceptance criteria:
- Plugin manifests advertise `passive-study`, `active-socratic`,
  `academic-presentation`, and `source-document-first`.
- Each top-level skill has `agents/openai.yaml` metadata with a default prompt
  that names the skill.
- Regression tests cover metadata discovery.

### Milestone 5: Executable Static Validation Gates

Status: done

Acceptance criteria:
- `tools/validate_deck.py static` rejects banned overlays, including `\uncover`.
- Static validation checks References before Thank You and `\appendix` before backups.
- Mode gates are documented in `references/validation/mode-gates.md` and linked
  from create/validate skills.
- Regression fixtures cover failing and passing static validation cases.

### Milestone 6: Progressive-Disclosure Create Skill

Status: done

Acceptance criteria:
- `autobeamer-create/SKILL.md` is a compact router under 220 lines.
- Detailed creation guidance is preserved in
  `references/workflows/full-create-guide.md`.
- The router directly links mode, image, validation, workflow, layout, build,
  review, and TikZ references.
- Regression tests cover the compact-router requirement.

### Milestone 7: Final Terminology Drift Cleanup

Status: done

Acceptance criteria:
- Top-level AutoBeamer skills no longer use old Presentation/Mentor mode labels
  as active headings.
- Top-level AutoBeamer skills no longer prescribe legacy box/image macros.
- Regression tests cover both drift classes.

### Final Completion Audit

Status: done

Evidence:
- Commits: `65c043b`, `6e3d652`, `739ad53`, `78183b8`, `7f2780a`,
  `b0ad931`, `02d3616`.
- `tests/test_skill_framework.py` covers mode taxonomy, hard-rule drift,
  source-document-first policy, metadata discovery, compact create routing, and
  terminology drift.
- `tests/test_validate_deck.py` covers executable static validation gates,
  including `\uncover`, References before Thank You, `\appendix` before backup
  slides, and a passing academic-presentation fixture.
- `tools/validate_deck.py static` provides the executable validation gate.
- Plugin JSON manifests parse and advertise all three modes plus
  source-document-first.

Known unrelated repository test failures:
- `python3 tests/run_tests.py unit` still fails on pre-existing font-config
  expectations: missing `personal-deck/config.tex` and missing
  `\newfontfamily\notocjk`.
