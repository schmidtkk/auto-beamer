# Environment Doctor — Dependency-State Gating

The skill needs a runtime it does not control (XeLaTeX, poppler, optionally
PyMuPDF + markitdown, CJK fonts, and a visual modality). Instead of a Docker
image, run the **doctor** first; it probes what is present and writes
`.autobeamer/env_state.json`, which the planner reads to choose fallback
behavior. Tool: [`tools/doctor.py`](../../../../tools/doctor.py).

## Run it (start of every task, Wave 1)

```bash
python tools/doctor.py check                                   # probe + write state
python tools/doctor.py set-capability --model <your-model-id>  # e.g. claude-opus-4-8
python tools/doctor.py report                                  # human-readable summary
```

`check` exits **non-zero** when a hard dependency is missing — that is a
**blocker**: stop and tell the user what to install before retrying.

## Dependency classes

| Dependency | Class | Probe | Missing → |
|------------|-------|-------|-----------|
| `xelatex` | **hard** | binary on PATH | **block** — cannot compile a deck |
| `pdftoppm` / `pdfinfo` (poppler) | **hard** | binaries on PATH | **block** — cannot render/inspect the PDF |
| `PyMuPDF` (`import fitz`) | soft | python module | degrade — no source-figure extraction |
| `markitdown` | soft | python module | degrade — no caption/context enrichment |
| CJK fonts | soft | `fc-list :lang=zh` | degrade — bilingual decks only |

## Agent capability via model-name table

A script cannot see the agent's modality, so vision is resolved from the
**self-declared model id**. `set-capability --model <id>` matches the id against
a table of multimodal families (`claude-opus-4`, `claude-sonnet-4`,
`claude-haiku-4`, `claude-3*`, `gpt-4o`, `gpt-5`, `gemini-2`, …). Unknown ids →
`text-only` (conservative). A vision MCP can be declared explicitly with
`--mcp-vision`. The result is `profile.visual_check_method` ∈
`{direct-vision, mcp, text-only}`.

## Capability → behavior mapping (read in the planning stage)

| `env_state.profile` | Planning behavior |
|---------------------|-------------------|
| `blockers != []` | **STOP** — report exactly what to install; do not start the task |
| `can_extract_pdf = false` | Skip `paper_parser` source-figure mining; ask the user for figures or go TikZ-first; seed the image index manually |
| `can_caption_md = false` | Skip `image_index import-markdown`; rely on `paper_parser` text for context |
| `cjk_ready = false` | Avoid bilingual/CJK content or warn; see `autobeamer-build` font setup |
| `visual_check_method = text-only` | Every figure `confidence` is capped at 0.5 (enforced by `image_index`); **prefer a TikZ redraw over adopting an unseen source figure** |
| `visual_check_method = direct-vision` / `mcp` | Read each image to set its `key_idea` and a high `confidence` |

The visual-check method flows straight into the [image index](../images/image-index.md):
the planner records each figure's `visual_check.method` from
`profile.visual_check_method`, and `image_index.py` auto-caps confidence when it
is `text-only`.

## Notes
- State is env-wide and gitignored (`.autobeamer/`); re-run `check` per task.
- `set-capability` trusts the model's own id; spoofed/unknown ids degrade safely.
- Hard-dep blocking is intentional: a deck you cannot compile or render is not
  deliverable. Soft deps only degrade figure features.
