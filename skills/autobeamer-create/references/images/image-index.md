# Image Index — Indexed Figure Adoption

Phase 4 (Figures) needs the figures discovered in Phase 0. The **image index** is
the per-deck handoff that makes figure adoption accurate instead of guesswork. It
is a single JSON file per deck — not a database. Whole-book extraction is out of
scope; index only the figures the deck might actually use.

Managed by [`tools/image_index.py`](../../../../tools/image_index.py); default
location `slides_assets/image_index.json`.

## Why it exists

`paper_parser.py` gives only objective facts (file, page, bbox, aspect ratio). To
adopt the *right* figure on the *right* slide you also need the **key idea** it
illustrates, its **caption/context**, its **provenance**, and a **confidence**
that reflects whether you could actually look at the image. The index records all
of these.

## Per-image fields

| Field | Meaning |
|-------|---------|
| `id` | stable slug (from filename) |
| `file` | local image path |
| `source` | `{document, page (1-based), region}` — region is a figure label and/or `bbox=(…)` |
| `caption` | caption text from the source |
| `context` | surrounding / section text |
| `key_idea` | what the figure illustrates — **the field draft matches against** |
| `confidence` | 0–1, governed by the confidence policy below |
| `visual_check` | `{method: direct-vision\|mcp\|text-only, verified, notes}` |
| `aspect_ratio`,`width_px`,`height_px` | from `paper_parser` |
| `adoption` | `[{slide_label, request_id, status}]` — filled during drafting |
| `provenance` | `{license, url, retrieved}` — external images only |

## Build workflow (Phase 0)

```bash
# 1. extract image files + page/bbox/AR
python tools/paper_parser.py parse SOURCE.pdf --output slides_assets/paper.json
python tools/paper_parser.py extract-images SOURCE.pdf --output slides_assets/source_figures/

# 2. seed the index from the parser output
python tools/image_index.py init --path slides_assets/image_index.json --deck "DECK"
python tools/image_index.py import-parser slides_assets/paper.json \
    --path slides_assets/image_index.json --document SOURCE.pdf

# 3. (optional) attach captions/context from a markdown rendering
markitdown SOURCE.pdf > slides_assets/source.md      # optional; see note
python tools/image_index.py import-markdown slides_assets/source.md \
    --path slides_assets/image_index.json
```

> **markitdown is optional.** It is an installed CLI (not an MCP) and may need
> `pip install markitdown` to run. If it is unavailable or its output is weak,
> skip step 3 — `paper_parser` text plus your own visual check is sufficient.
> `import-markdown` accepts *any* markdown containing image refs / "Figure N:"
> captions.

## Visual-check ladder (sets `confidence`)

The method is **determined by the environment doctor**, not guessed per image:
`profile.visual_check_method` in `.autobeamer/env_state.json` (see
[env-doctor.md](../validation/env-doctor.md)) is set from your self-declared model
id. Use that method for every image:

1. **`direct-vision`** — the model is multimodal; read the image directly. Set
   `--visual direct-vision --verified`; high confidence allowed.
2. **`mcp`** — a vision MCP tool inspected it. `--visual mcp --verified`; high
   confidence allowed.
3. **`text-only`** — no visual modality; you inferred meaning from caption/context
   only. Confidence is **capped at 0.5** automatically, the item shows up under
   `unresolved`, and you should **prefer a TikZ redraw** over adopting it unseen.

```bash
python tools/image_index.py set fig_p3_monge \
    --key-idea "Monge map pushes source mass onto the target measure" \
    --visual direct-vision --verified --confidence 0.9
python tools/image_index.py validate     # enforces the confidence policy
python tools/image_index.py unresolved   # items still needing a key idea / visual check
```

## How drafting consumes it (Phase 3+4 merged)

When a slide wants a figure, the drafter logs an **image request** and queries the
index by the key idea it needs:

```bash
python tools/image_index.py request-add --slide "Monge problem" \
    --need "show mass transported from source to target"
python tools/image_index.py query --key-idea "mass transported source to target"
```

Adopt following the source-first ladder (see
[source-document-first.md](source-document-first.md)): indexed source figure →
crop/redraw → TikZ/pgfplots → external (with provenance). Record the outcome:

```bash
python tools/image_index.py request-resolve --request req-001 \
    --image fig_p3_monge --status adopted
```

A low-confidence match (e.g. a `text-only` item) is a signal to look at the image
before committing, or to prefer a TikZ redraw.

## Checklist before leaving Phase 0

- [ ] Every candidate figure has a record with `file` + `source.page`/`region`.
- [ ] Every record a slide might use has a `key_idea`.
- [ ] Each image was visually checked (or explicitly marked `text-only`, capped).
- [ ] External images carry `provenance` (license, url, retrieved).
- [ ] `python tools/image_index.py validate` passes.
