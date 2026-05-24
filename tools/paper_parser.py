#!/usr/bin/env python3
"""
paper_parser.py — PDF paper → structured content for Beamer deck planning
==========================================================================

Extracts text, images, and structural metadata from a PDF academic paper.
Outputs a JSON file that downstream tools (or the AI agent) can use to plan
slides.

Capabilities
────────────
  • Section heading detection (numbered or named academic sections)
  • Full text extraction per page and per section
  • Embedded image extraction (PNG) with bounding boxes
  • Image aspect-ratio reporting (feeds layout_optimizer.py)
  • Page-render to PNG for visual review

Limitations (by design — kept simple)
─────────────────────────────────────
  • No equation OCR — equations are kept as raw text or screenshots
  • No table structure recognition — tables extracted as page-region PNGs
  • No OCR for scanned PDFs — requires text-layer PDFs

Usage
─────
  # Full parse: text + images + metadata → JSON
  python paper_parser.py parse paper.pdf --output slides_assets/paper.json

  # Extract images only
  python paper_parser.py extract-images paper.pdf --output slides_assets/

  # Render pages to PNG (visual review)
  python paper_parser.py render-pages paper.pdf --output slides_assets/pages/

  # Quick summary to console
  python paper_parser.py summary paper.pdf

Dependencies
────────────
  Required: PyMuPDF (fitz), pypdf
  Optional: Pillow (for image processing, usually installed)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    from PIL import Image
except ImportError:
    Image = None


# ─── Section heading patterns ───────────────────────────────────────────────

SECTION_PATTERNS = [
    # Numbered: "1. Introduction", "2.3 Method Details"
    # Excludes page numbers like "3 / 28" or standalone numbers
    (re.compile(r"^(\d+(?:\.\d+)*)\s+(?!\s*/\s*\d)(.{3,})$"), "numbered"),
    # Chinese numbered: "一、引言", "二、方法"
    (re.compile(r"^([一二三四五六七八九十]+)、\s*(.+)$"), "cn_numbered"),
    # Named sections (case-insensitive)
    (re.compile(r"^(Abstract)\s*$", re.IGNORECASE), "named"),
    (re.compile(r"^(Introduction)\s*$", re.IGNORECASE), "named"),
    (re.compile(r"^(Related Work|Background|Preliminaries)\s*$", re.IGNORECASE), "named"),
    (re.compile(r"^(Method(?:ology)?|Approach|Proposed\s+Method)\s*$", re.IGNORECASE), "named"),
    (re.compile(r"^(Experiments?|Results?|Evaluation|Ablation\s+Study)\b", re.IGNORECASE), "named"),
    (re.compile(r"^(Discussion|Conclusion|Conclusions?)\s*$", re.IGNORECASE), "named"),
    (re.compile(r"^(Acknowledg?ments?)\s*$", re.IGNORECASE), "named"),
    (re.compile(r"^(References|Bibliography)\s*$", re.IGNORECASE), "named"),
    (re.compile(r"^(Appendix|Supplementary)\b", re.IGNORECASE), "named"),
]

# Typical academic section order for classification
SECTION_ORDER = [
    "abstract",
    "introduction",
    "related work", "background", "preliminaries",
    "method", "methodology", "approach", "proposed",
    "experiment", "experiments", "results", "evaluation", "ablation",
    "discussion",
    "conclusion", "conclusions",
    "acknowledgment", "acknowledgments",
    "references", "bibliography",
    "appendix", "supplementary",
]


# ─── Data classes ───────────────────────────────────────────────────────────

@dataclass
class ExtractedImage:
    """An image extracted from the PDF."""
    filename: str
    page: int              # 1-based
    width_px: int
    height_px: int
    aspect_ratio: float
    xref: int = 0
    # Bounding box on page (in PDF points), may be None
    bbox_x0: Optional[float] = None
    bbox_y0: Optional[float] = None
    bbox_x1: Optional[float] = None
    bbox_y1: Optional[float] = None


@dataclass
class Section:
    """A detected section in the paper."""
    name: str
    level: int             # 1 = top-level, 2 = subsection, etc.
    start_page: int        # 1-based
    end_page: int          # 1-based (inclusive, filled after full parse)
    text: str = ""


@dataclass
class PaperInfo:
    """Structured paper data."""
    source_pdf: str
    title: str = ""
    authors: str = ""
    num_pages: int = 0
    sections: list[Section] = field(default_factory=list)
    images: list[ExtractedImage] = field(default_factory=list)
    full_text: str = ""
    page_texts: list[str] = field(default_factory=list)


# ─── Core extraction ────────────────────────────────────────────────────────

def check_fitz() -> None:
    """Raise if PyMuPDF is not available."""
    if fitz is None:
        print(
            "Error: PyMuPDF (fitz) is required.\n"
            "  Install with:  pip install PyMuPDF",
            file=sys.stderr,
        )
        sys.exit(1)


def open_pdf(path: str) -> fitz.Document:
    """Open a PDF and return the fitz Document."""
    check_fitz()
    doc = fitz.open(path)
    if doc.is_encrypted:
        print("Warning: PDF is encrypted. Attempting empty password...", file=sys.stderr)
        if not doc.authenticate(""):
            print("Error: Cannot decrypt PDF.", file=sys.stderr)
            sys.exit(1)
    return doc


def extract_title(doc: fitz.Document) -> str:
    """Heuristic: grab the largest-font text block on page 1."""
    page = doc[0]
    blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]

    best_text = ""
    best_size = 0.0

    for block in blocks:
        if block["type"] != 0:  # text block only
            continue
        for line in block["lines"]:
            for span in line["spans"]:
                text = span["text"].strip()
                size = span["size"]
                # Skip very short fragments and non-title sizes
                if len(text) < 5 or size < 12:
                    continue
                if size > best_size:
                    best_size = size
                    best_text = text
                elif size == best_size:
                    best_text += " " + text

    return best_text.strip()


def extract_text_per_page(doc: fitz.Document) -> list[str]:
    """Extract text from each page."""
    texts = []
    for page in doc:
        text = page.get_text("text", flags=fitz.TEXT_PRESERVE_WHITESPACE)
        texts.append(text)
    return texts


def detect_sections(page_texts: list[str]) -> list[Section]:
    """Detect section headings across all pages."""
    sections: list[Section] = []

    for page_idx, text in enumerate(page_texts):
        page_num = page_idx + 1
        for line in text.split("\n"):
            line_stripped = line.strip()
            if not line_stripped:
                continue

            for pattern, kind in SECTION_PATTERNS:
                m = pattern.match(line_stripped)
                if not m:
                    continue

                if kind == "numbered":
                    number = m.group(1)
                    name = m.group(2).strip()
                    level = number.count(".") + 1
                    full_name = f"{number}. {name}"
                elif kind == "cn_numbered":
                    number = m.group(1)
                    name = m.group(2).strip()
                    level = 1
                    full_name = f"{number}、{name}"
                else:
                    full_name = line_stripped
                    level = 1
                    name = line_stripped

                # Avoid duplicates (e.g., header/footer)
                if sections and sections[-1].name == full_name and sections[-1].start_page == page_num:
                    break

                sections.append(Section(
                    name=full_name,
                    level=level,
                    start_page=page_num,
                    end_page=page_num,
                ))
                break  # matched one pattern, stop trying others

    # Fill end_page: each section ends where the next one starts
    for i in range(len(sections) - 1):
        sections[i].end_page = sections[i + 1].start_page
    if sections:
        sections[-1].end_page = len(page_texts)

    return sections


def assign_text_to_sections(
    sections: list[Section], page_texts: list[str]
) -> None:
    """Fill in the text field for each section from page texts."""
    for section in sections:
        parts = []
        for pg in range(section.start_page - 1, min(section.end_page, len(page_texts))):
            parts.append(page_texts[pg])
        section.text = "\n".join(parts)


def extract_images(
    doc: fitz.Document, output_dir: Path, min_size: int = 100
) -> list[ExtractedImage]:
    """
    Extract embedded images from the PDF.

    Args:
        doc: PyMuPDF document.
        output_dir: Directory to save extracted images.
        min_size: Minimum dimension (px) to keep. Filters out tiny icons/logos.

    Returns:
        List of ExtractedImage metadata.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    images: list[ExtractedImage] = []

    for page_idx in range(len(doc)):
        page = doc[page_idx]
        page_images = page.get_images(full=True)

        for img_idx, img_info in enumerate(page_images):
            xref = img_info[0]

            try:
                pix = fitz.Pixmap(doc, xref)
            except Exception:
                continue

            # Skip small images (likely icons, bullets, logos)
            if pix.width < min_size or pix.height < min_size:
                pix = None
                continue

            # Convert CMYK to RGB if needed
            if pix.n >= 5:
                try:
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                except Exception:
                    pix = None
                    continue

            filename = f"paper_p{page_idx + 1}_fig{img_idx + 1}.png"
            filepath = output_dir / filename
            pix.save(str(filepath))

            images.append(ExtractedImage(
                filename=str(filepath),
                page=page_idx + 1,
                width_px=pix.width,
                height_px=pix.height,
                aspect_ratio=round(pix.width / pix.height, 3),
                xref=xref,
            ))

            pix = None  # free memory

    return images


def extract_image_bboxes(doc: fitz.Document) -> dict[int, list[dict]]:
    """
    Get bounding boxes for images on each page.

    Returns:
        {page_1based: [{"xref": int, "bbox": (x0, y0, x1, y1)}, ...]}
    """
    result: dict[int, list[dict]] = {}
    for page_idx in range(len(doc)):
        page = doc[page_idx]
        items = page.get_images(full=True)
        if not items:
            continue

        page_imgs = []
        for item in items:
            xref = item[0]
            # Find all rect annotations for this image on this page
            rects = page.get_image_rects(xref)
            for rect in rects:
                page_imgs.append({
                    "xref": xref,
                    "bbox": (round(rect.x0, 1), round(rect.y0, 1),
                             round(rect.x1, 1), round(rect.y1, 1)),
                })

        if page_imgs:
            result[page_idx + 1] = page_imgs

    return result


# ─── Sub-commands ───────────────────────────────────────────────────────────

def cmd_parse(args: argparse.Namespace) -> None:
    """Full parse: text + images + metadata → JSON."""
    pdf_path = args.pdf
    output_path = args.output
    img_dir = args.img_dir

    if output_path is None:
        output_path = str(Path(pdf_path).with_suffix(".json"))
    if img_dir is None:
        img_dir = str(Path(output_path).parent)

    doc = open_pdf(pdf_path)
    print(f"Parsing: {pdf_path}  ({len(doc)} pages)")

    # Text
    page_texts = extract_text_per_page(doc)
    title = extract_title(doc)

    # Sections
    sections = detect_sections(page_texts)
    assign_text_to_sections(sections, page_texts)

    # Images
    img_output = Path(img_dir)
    images = extract_images(doc, img_output, min_size=args.min_img_size)
    print(f"  Extracted {len(images)} images → {img_output}/")

    # Image bboxes
    bboxes = extract_image_bboxes(doc)
    for img in images:
        page_bboxes = bboxes.get(img.page, [])
        for bb in page_bboxes:
            if bb["xref"] == img.xref:
                img.bbox_x0, img.bbox_y0, img.bbox_x1, img.bbox_y1 = bb["bbox"]
                break

    # Build result
    paper = PaperInfo(
        source_pdf=str(Path(pdf_path).resolve()),
        title=title,
        num_pages=len(doc),
        sections=sections,
        images=images,
        full_text="\n\n".join(page_texts),
        page_texts=page_texts,
    )

    # Serialize (dataclass → dict)
    data = asdict(paper)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n  Title   : {title}")
    print(f"  Sections: {len(sections)}")
    print(f"  Images  : {len(images)}")
    print(f"  Output  : {output_path}")

    doc.close()


def cmd_extract_images(args: argparse.Namespace) -> None:
    """Extract images only from PDF."""
    pdf_path = args.pdf
    output_dir = args.output or "slides_assets"

    doc = open_pdf(pdf_path)
    out = Path(output_dir)
    images = extract_images(doc, out, min_size=args.min_img_size)

    print(f"Extracted {len(images)} images from {pdf_path}")
    for img in images:
        ar_label = "wide" if img.aspect_ratio > 1.5 else ("tall" if img.aspect_ratio < 0.8 else "square")
        print(f"  p{img.page:>2d}  {Path(img.filename).name:<35s}  {img.width_px}×{img.height_px}  AR={img.aspect_ratio:.2f} ({ar_label})")

    doc.close()


def cmd_render_pages(args: argparse.Namespace) -> None:
    """Render PDF pages to PNG for visual review."""
    pdf_path = args.pdf
    output_dir = args.output or "slides_assets/pages"
    dpi = args.dpi or 200

    doc = open_pdf(pdf_path)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    for page_idx in range(len(doc)):
        page = doc[page_idx]
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat)
        filename = f"page_{page_idx + 1:03d}.png"
        pix.save(str(out / filename))
        print(f"  {filename}  ({pix.width}×{pix.height})")

    print(f"Rendered {len(doc)} pages → {out}/")
    doc.close()


def cmd_summary(args: argparse.Namespace) -> None:
    """Print a quick summary to console (no files written)."""
    pdf_path = args.pdf

    doc = open_pdf(pdf_path)
    page_texts = extract_text_per_page(doc)
    title = extract_title(doc)
    sections = detect_sections(page_texts)

    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"  Pages: {len(doc)}")
    print(f"{'='*60}\n")

    if sections:
        print("Sections:")
        for sec in sections:
            indent = "  " * sec.level
            pages = f"p{sec.start_page}"
            if sec.end_page != sec.start_page:
                pages += f"–p{sec.end_page}"
            print(f"  {indent}• {sec.name}  ({pages})")
    else:
        print("  (No sections detected)")

    # Image count
    total_imgs = 0
    for page_idx in range(len(doc)):
        page = doc[page_idx]
        total_imgs += len(page.get_images(full=True))

    print(f"\n  Embedded images: {total_imgs}")
    print(f"  Run 'extract-images' to save them.\n")

    doc.close()


# ─── CLI ────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="PDF paper → structured content for Beamer slide planning",
    )
    sub = parser.add_subparsers(dest="command")

    # --- parse ---
    p_parse = sub.add_parser("parse", help="Full parse: text + images → JSON")
    p_parse.add_argument("pdf", help="Path to PDF paper")
    p_parse.add_argument("--output", "-o", help="Output JSON path (default: <pdf>.json)")
    p_parse.add_argument("--img-dir", help="Directory for extracted images (default: same as output)")
    p_parse.add_argument("--min-img-size", type=int, default=100,
                         help="Min dimension (px) to keep an image (default: 100)")

    # --- extract-images ---
    p_imgs = sub.add_parser("extract-images", help="Extract images from PDF")
    p_imgs.add_argument("pdf", help="Path to PDF paper")
    p_imgs.add_argument("--output", "-o", default="slides_assets",
                        help="Output directory (default: slides_assets)")
    p_imgs.add_argument("--min-img-size", type=int, default=100,
                        help="Min dimension (px) to keep an image (default: 100)")

    # --- render-pages ---
    p_render = sub.add_parser("render-pages", help="Render PDF pages to PNG")
    p_render.add_argument("pdf", help="Path to PDF paper")
    p_render.add_argument("--output", "-o", default=None,
                          help="Output directory (default: slides_assets/pages)")
    p_render.add_argument("--dpi", type=int, default=200,
                          help="Render DPI (default: 200)")

    # --- summary ---
    p_summary = sub.add_parser("summary", help="Print paper summary to console")
    p_summary.add_argument("pdf", help="Path to PDF paper")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    commands = {
        "parse": cmd_parse,
        "extract-images": cmd_extract_images,
        "render-pages": cmd_render_pages,
        "summary": cmd_summary,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
