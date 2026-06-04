---
name: autobeamer-doctor
description: "Preflight the AutoBeamer runtime — probe XeLaTeX, poppler, PyMuPDF, markitdown and CJK fonts, record this model's visual capability, and write the env-state that gates create-pipeline fallback behavior."
when_to_use: |
  Triggers on: "beamer doctor", "autobeamer doctor", "check environment",
  "check dependencies", "are my beamer deps installed", "is xelatex installed",
  "preflight", "env state", "why is figure extraction unavailable".
  Run it before a deck task, or whenever a build/extraction step fails on a
  missing tool. Do NOT trigger on actual compile errors of an existing deck
  (use autobeamer-build) or content review (use autobeamer-review).
argument-hint: "doctor [check|report|set-capability] — preflight the beamer runtime"
allowed-tools: ["Read", "Bash", "Grep", "Glob"]
---

# AutoBeamer Doctor — Environment Preflight

The skill needs a runtime it does not control (XeLaTeX, poppler, optionally
PyMuPDF + markitdown, CJK fonts, and a visual modality). This skill probes what is
present and writes `.autobeamer/env_state.json`, which the create pipeline reads
during planning to choose fallback behavior. Tool: `tools/doctor.py`.

## Run it

```bash
python tools/doctor.py check                                  # probe + write state
python tools/doctor.py set-capability --model <your-model-id> # e.g. claude-opus-4-8
python tools/doctor.py report                                 # human-readable summary
```

`check` exits **non-zero** when a hard dependency is missing — that is a
**blocker**; report exactly what to install and stop.

## What it checks

| Dependency | Class | Missing → |
|------------|-------|-----------|
| `xelatex` | **hard** | block — cannot compile |
| `pdftoppm` / `pdfinfo` (poppler) | **hard** | block — cannot render/inspect the PDF |
| `PyMuPDF` (`import fitz`) | soft | degrade — no source-figure extraction |
| `markitdown` | soft | degrade — no caption/context enrichment |
| CJK fonts (`fc-list :lang=zh`) | soft | degrade — bilingual decks only |

Each missing dep prints an install hint.

## Visual capability (model-name table)

A script can't see the agent's modality, so `set-capability --model <id>` maps the
self-declared model id to vision support (multimodal families → `direct-vision`;
unknown → `text-only`; `--mcp-vision` → `mcp`). The resulting
`profile.visual_check_method` sets the figure-confidence ceiling in the image
index (`text-only` caps confidence at 0.5).

## What the result drives

See the full capability → behavior mapping in
[autobeamer-create/references/validation/env-doctor.md](../autobeamer-create/references/validation/env-doctor.md):
`can_extract_pdf`, `can_caption_md`, `cjk_ready`, `visual_check_method`, and
`blockers` determine how the planner mines figures and sets figure confidence.

## Cross-references

| Need | Skill |
|------|-------|
| Build / compile errors, fonts | [autobeamer-build](../autobeamer-build/SKILL.md) |
| Create a deck (runs doctor as Step 0) | [autobeamer-create](../autobeamer-create/SKILL.md) |
