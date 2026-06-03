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

Status: in progress

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

Status: planned

Acceptance criteria:
- The final report proposes a concrete refactor plan for mode taxonomy,
  skill/reference structure, validation gates, memory routing, and image extraction.
- Recommendations are ranked by severity and implementation order.
- The goal is audited against all explicit user requirements before completion.
- A final git commit records the completed review artifacts and LightMem updates.
