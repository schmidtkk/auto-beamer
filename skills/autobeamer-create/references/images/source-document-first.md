# Source-Document-First Image Policy

Use this policy whenever the user provides a PDF, paper, report, textbook chapter, or source document. The policy name is `source-document-first`.

## Priority Order

1. Mine the provided PDF before web search. Run:
   ```bash
   python tools/paper_parser.py parse paper.pdf --output slides_assets/paper.json
   python tools/paper_parser.py extract-images paper.pdf --output slides_assets/source_figures/
   ```
2. Inventory source figures from `paper.json`: page, filename, aspect ratio, caption or nearby text, and candidate slide use.
3. Prefer extracted source figures when they directly support the deck's argument.
4. Redraw, crop, simplify, or split dense source figures locally when the original is too hard to read.
5. Use TikZ or pgfplots when the figure must match the deck's notation, exact coordinates, or proof structure.
6. Use an external image only as a fallback when the provided PDF has no suitable visual.

## External Image Fallback Rules

- External image assets must be downloaded or generated into a local project directory before compilation.
- Never hotlink images from a website, CDN, arXiv page, or remote repository in the TeX source.
- Every external image needs attribution in the slide footer, caption, references slide, or asset manifest.
- Record license/source URL and retrieval date when the source is not the user's own document.
- Prefer stable primary sources over search-result thumbnails or social-media mirrors.

## Review Checklist

- Did the agent inspect the provided PDF before web search?
- Does each source figure have provenance: page number or file path?
- Does each external image have attribution and a local file path?
- Is the figure readable at slide scale after crop/adaptation?
- Is the visual actually necessary, or would a local TikZ diagram be clearer?
