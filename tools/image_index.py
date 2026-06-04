#!/usr/bin/env python3
"""
image_index.py — per-deck figure index for AutoBeamer
=====================================================

A lightweight, dependency-free manager for a per-deck JSON image index. It is
NOT a database — one ``image_index.json`` per deck is enough (whole-book
extraction is out of scope). The index records, for every candidate figure:

    id, file, source{document,page,region}, caption, context, key_idea,
    confidence, visual_check{method,verified,notes}, aspect_ratio,
    width_px, height_px, adoption[], provenance{license,url,retrieved}

These fields are what Wave-2 drafting needs to *adopt* the right figure for a
slide (``query --key-idea``) with correct provenance.

Pipeline fit
------------
  paper_parser.py extract-images   → image files + page + bbox + AR
  paper_parser.py parse → paper.json
  image_index.py import-parser paper.json   → seed records (file/page/region/AR)
  markitdown doc > source.md (optional)     → captions/context text
  image_index.py import-markdown source.md  → attach caption/context
  <visual check: read each image>           → image_index.py set <id> ...
  image_index.py validate / query / render-md

Confidence policy
-----------------
A figure's confidence must reflect whether a *visual* check was possible:
  - visual_check.method == "direct-vision" and verified  → may be high
  - "mcp" and verified                                   → may be high
  - "text-only" (no visual modality)                     → capped at 0.5

Usage
-----
  python image_index.py init [--path PATH] [--deck NAME]
  python image_index.py import-parser paper.json [--path PATH] [--document NAME]
  python image_index.py import-markdown source.md [--path PATH]
  python image_index.py set ID [--key-idea ...] [--caption ...] [--context ...]
        [--confidence F] [--visual METHOD] [--verified] [--notes ...]
        [--page N] [--region ...] [--license ...] [--url ...] [--retrieved ...]
  python image_index.py get ID [--path PATH]
  python image_index.py list [--path PATH]
  python image_index.py query --key-idea "TEXT" [--top N] [--path PATH]
  python image_index.py validate [--path PATH]
  python image_index.py unresolved [--path PATH]
  python image_index.py render-md [--out FILE] [--path PATH]
  python image_index.py request-add --slide L --need TEXT [--candidates a,b]
  python image_index.py request-resolve --request RID --image IMGID
        --status {adopted,tikz,external,dropped}
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


SCHEMA_VERSION = 1
DEFAULT_PATH = "slides_assets/image_index.json"
TEXT_ONLY_CONF_CAP = 0.5
VISUAL_METHODS = ("direct-vision", "mcp", "text-only")


# ── core load/save ────────────────────────────────────────────────────────────

def _empty_index(deck: str = "") -> dict:
    return {"version": SCHEMA_VERSION, "deck": deck, "images": [], "requests": []}


def load_index(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise SystemExit(f"image index not found: {path} (run 'init' first)")
    data = json.loads(p.read_text(encoding="utf-8"))
    data.setdefault("version", SCHEMA_VERSION)
    data.setdefault("images", [])
    data.setdefault("requests", [])
    return data


def save_index(path: str, data: dict) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _find(data: dict, image_id: str) -> dict | None:
    return next((im for im in data["images"] if im.get("id") == image_id), None)


def _slug(name: str) -> str:
    stem = Path(name).stem
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", stem).strip("-") or "img"


def _new_record(image_id: str, file: str) -> dict:
    return {
        "id": image_id,
        "file": file,
        "source": {"document": "", "page": None, "region": ""},
        "caption": "",
        "context": "",
        "key_idea": "",
        "confidence": 0.0,
        "visual_check": {"method": "text-only", "verified": False, "notes": ""},
        "aspect_ratio": None,
        "width_px": None,
        "height_px": None,
        "adoption": [],
        "provenance": None,
    }


# ── confidence policy ─────────────────────────────────────────────────────────

def apply_confidence_policy(record: dict) -> list[str]:
    """Clamp confidence to [0,1] and cap text-only/unverified records.
    Returns a list of human-readable adjustment notes."""
    notes: list[str] = []
    conf = record.get("confidence", 0.0)
    try:
        conf = float(conf)
    except (TypeError, ValueError):
        conf = 0.0
    if conf < 0 or conf > 1:
        conf = max(0.0, min(1.0, conf))
        notes.append("confidence clamped to [0,1]")

    vc = record.get("visual_check") or {}
    method = vc.get("method", "text-only")
    verified = bool(vc.get("verified", False))
    if (method == "text-only" or not verified) and conf > TEXT_ONLY_CONF_CAP:
        conf = TEXT_ONLY_CONF_CAP
        notes.append(
            f"confidence capped at {TEXT_ONLY_CONF_CAP} "
            f"(no verified visual check: method={method}, verified={verified})")
    record["confidence"] = round(conf, 3)
    return notes


# ── subcommands ───────────────────────────────────────────────────────────────

def cmd_init(args) -> int:
    p = Path(args.path)
    if p.exists() and not args.force:
        print(f"index already exists: {args.path} (use --force to overwrite)")
        return 1
    save_index(args.path, _empty_index(args.deck or ""))
    print(f"initialized image index: {args.path}")
    return 0


def cmd_import_parser(args) -> int:
    paper = json.loads(Path(args.paper).read_text(encoding="utf-8"))
    data = load_index(args.path) if Path(args.path).exists() else _empty_index()
    document = args.document or Path(paper.get("source_pdf", args.paper)).name
    added = merged = 0
    for img in paper.get("images", []):
        fname = img.get("filename")
        if not fname:
            continue
        image_id = _slug(fname)
        rec = _find(data, image_id)
        if rec is None:
            rec = _new_record(image_id, fname)
            data["images"].append(rec)
            added += 1
        else:
            merged += 1
        # seed objective fields (never overwrite human-entered semantics)
        rec["file"] = fname
        rec["source"]["document"] = document
        rec["source"]["page"] = img.get("page")
        bbox = [img.get(k) for k in ("bbox_x0", "bbox_y0", "bbox_x1", "bbox_y1")]
        if all(v is not None for v in bbox) and not rec["source"].get("region"):
            rec["source"]["region"] = (
                f"bbox=({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]})")
        rec["aspect_ratio"] = img.get("aspect_ratio")
        rec["width_px"] = img.get("width_px")
        rec["height_px"] = img.get("height_px")
    save_index(args.path, data)
    print(f"import-parser: +{added} new, {merged} merged "
          f"({len(data['images'])} total) → {args.path}")
    return 0


_MD_IMG_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
_MD_CAPTION_RE = re.compile(r"^\s*(?:\*{1,2})?\s*(Fig(?:ure)?\.?\s*\d+[.:]?\s*.+)",
                            re.IGNORECASE)


def cmd_import_markdown(args) -> int:
    """Best-effort caption/context attach from a markdown rendering of the
    source (e.g. markitdown output). markitdown is optional; any markdown with
    image refs / 'Figure N:' captions works."""
    data = load_index(args.path)
    md = Path(args.md).read_text(encoding="utf-8", errors="replace")
    lines = md.splitlines()
    by_base = {Path(im["file"]).name: im for im in data["images"]}
    attached = 0
    for i, line in enumerate(lines):
        m = _MD_IMG_RE.search(line)
        if m:
            base = Path(m.group(1)).name
            rec = by_base.get(base)
            if rec:
                # caption = a nearby Figure line; context = surrounding lines
                window = " ".join(lines[max(0, i - 1):i + 3]).strip()
                cap = next((c.group(1).strip() for c in
                            (_MD_CAPTION_RE.match(l) for l in lines[i:i + 3]) if c),
                           "")
                if cap and not rec["caption"]:
                    rec["caption"] = cap[:300]
                if window and not rec["context"]:
                    rec["context"] = re.sub(r"\s+", " ", window)[:500]
                attached += 1
    save_index(args.path, data)
    print(f"import-markdown: attached caption/context to {attached} image(s)")
    return 0


def cmd_set(args) -> int:
    data = load_index(args.path)
    rec = _find(data, args.id)
    if rec is None:
        print(f"no image with id: {args.id}")
        return 1
    if args.key_idea is not None:
        rec["key_idea"] = args.key_idea
    if args.caption is not None:
        rec["caption"] = args.caption
    if args.context is not None:
        rec["context"] = args.context
    if args.region is not None:
        rec["source"]["region"] = args.region
    if args.page is not None:
        rec["source"]["page"] = args.page
    if args.visual is not None:
        if args.visual not in VISUAL_METHODS:
            print(f"--visual must be one of {VISUAL_METHODS}")
            return 1
        rec["visual_check"]["method"] = args.visual
    if args.verified:
        rec["visual_check"]["verified"] = True
    if args.notes is not None:
        rec["visual_check"]["notes"] = args.notes
    if args.confidence is not None:
        rec["confidence"] = args.confidence
    if any(v is not None for v in (args.license, args.url, args.retrieved)):
        prov = rec.get("provenance") or {}
        if args.license is not None:
            prov["license"] = args.license
        if args.url is not None:
            prov["url"] = args.url
        if args.retrieved is not None:
            prov["retrieved"] = args.retrieved
        rec["provenance"] = prov
    notes = apply_confidence_policy(rec)
    save_index(args.path, data)
    print(f"updated {args.id}: confidence={rec['confidence']}")
    for n in notes:
        print(f"  note: {n}")
    return 0


def cmd_get(args) -> int:
    data = load_index(args.path)
    rec = _find(data, args.id)
    if rec is None:
        print(f"no image with id: {args.id}")
        return 1
    print(json.dumps(rec, ensure_ascii=False, indent=2))
    return 0


def cmd_list(args) -> int:
    data = load_index(args.path)
    print(f"# {data.get('deck') or '(deck)'} — {len(data['images'])} image(s)")
    for im in data["images"]:
        pg = im["source"].get("page")
        print(f"  {im['id']:<28} p{pg!s:<4} conf={im['confidence']:<4} "
              f"{(im['key_idea'] or '(no key idea)')[:48]}")
    return 0


def _tokens(*parts: str) -> set[str]:
    text = " ".join(p for p in parts if p).lower()
    return set(re.findall(r"[a-z0-9一-鿿]+", text))


def cmd_query(args) -> int:
    data = load_index(args.path)
    q = _tokens(args.key_idea)
    if not q:
        print("empty query")
        return 1
    scored = []
    for im in data["images"]:
        toks = _tokens(im.get("key_idea", ""), im.get("caption", ""),
                       im.get("context", ""))
        if not toks:
            score = 0.0
        else:
            overlap = len(q & toks)
            # weight key_idea overlap higher
            kscore = len(q & _tokens(im.get("key_idea", "")))
            score = (overlap + 2 * kscore) / (len(q) + 1e-9)
        # confidence acts as a mild tie-breaker / down-weight
        scored.append((score * (0.5 + 0.5 * im.get("confidence", 0.0)), score, im))
    scored.sort(key=lambda t: t[0], reverse=True)
    top = [t for t in scored if t[1] > 0][: args.top]
    if not top:
        print("no candidate figures matched; consider TikZ/redraw or external")
        return 0
    print(f"# candidates for: {args.key_idea}")
    for rank_score, raw, im in top:
        print(f"  [{rank_score:4.2f}] {im['id']:<26} conf={im['confidence']:<4} "
              f"{im['file']}")
        print(f"         key_idea: {im['key_idea'] or '—'}")
    return 0


def _validate_record(im: dict) -> list[str]:
    errs: list[str] = []
    if not im.get("file"):
        errs.append("missing file")
    src = im.get("source") or {}
    if src.get("page") is None and not src.get("region"):
        errs.append("missing source location (page or region)")
    conf = im.get("confidence", 0.0)
    if not isinstance(conf, (int, float)) or conf < 0 or conf > 1:
        errs.append(f"confidence out of range: {conf}")
    vc = im.get("visual_check") or {}
    method = vc.get("method")
    if method not in VISUAL_METHODS:
        errs.append(f"invalid visual_check.method: {method}")
    if (method == "text-only" or not vc.get("verified")) and conf > TEXT_ONLY_CONF_CAP:
        errs.append(
            f"confidence {conf} exceeds {TEXT_ONLY_CONF_CAP} without a verified "
            f"visual check")
    return errs


def cmd_validate(args) -> int:
    data = load_index(args.path)
    hard = 0
    for im in data["images"]:
        errs = _validate_record(im)
        if errs:
            hard += 1
            print(f"FAIL {im.get('id')}: " + "; ".join(errs))
        # soft warning: missing key idea (advisory, not a hard failure)
        if not im.get("key_idea"):
            print(f"warn {im.get('id')}: no key_idea (adoption matching weakened)")
    if hard:
        print(f"validate: {hard} record(s) with errors")
        return 1
    print(f"validate: OK ({len(data['images'])} record(s))")
    return 0


def cmd_unresolved(args) -> int:
    data = load_index(args.path)
    rows = []
    for im in data["images"]:
        vc = im.get("visual_check") or {}
        if (not im.get("key_idea")) or vc.get("method") == "text-only" \
                or not vc.get("verified"):
            rows.append(im)
    print(f"# unresolved: {len(rows)} image(s) need a key idea or visual check")
    for im in rows:
        vc = im.get("visual_check") or {}
        print(f"  {im['id']:<28} key_idea={'Y' if im.get('key_idea') else 'N'} "
              f"visual={vc.get('method')}/verified={vc.get('verified')}")
    return 0


def cmd_render_md(args) -> int:
    data = load_index(args.path)
    out = [f"# Image Index — {data.get('deck') or '(deck)'}", ""]
    out.append("| id | page | key idea | conf | visual | file |")
    out.append("|----|------|----------|------|--------|------|")
    for im in data["images"]:
        vc = im.get("visual_check") or {}
        out.append(
            f"| {im['id']} | {im['source'].get('page')} | "
            f"{(im.get('key_idea') or '—')[:50]} | {im['confidence']} | "
            f"{vc.get('method')}{'✓' if vc.get('verified') else ''} | "
            f"`{im['file']}` |")
    text = "\n".join(out) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(text)
    return 0


def cmd_request_add(args) -> int:
    data = load_index(args.path)
    rid = args.id or f"req-{len(data['requests']) + 1:03d}"
    data["requests"].append({
        "request_id": rid,
        "slide_label": args.slide,
        "need": args.need,
        "candidates": [c for c in (args.candidates or "").split(",") if c],
        "chosen": None,
        "status": "open",
    })
    save_index(args.path, data)
    print(f"added image request {rid} for slide '{args.slide}'")
    return 0


def cmd_request_resolve(args) -> int:
    data = load_index(args.path)
    req = next((r for r in data["requests"]
                if r["request_id"] == args.request), None)
    if req is None:
        print(f"no request: {args.request}")
        return 1
    req["chosen"] = args.image
    req["status"] = args.status
    if args.image:
        rec = _find(data, args.image)
        if rec is not None:
            rec.setdefault("adoption", []).append({
                "slide_label": req["slide_label"],
                "request_id": req["request_id"],
                "status": args.status,
            })
    save_index(args.path, data)
    print(f"resolved {args.request}: {args.status} ({args.image or '—'})")
    return 0


# ── CLI ───────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Per-deck AutoBeamer figure index")
    sub = p.add_subparsers(dest="command", required=True)

    def with_path(sp):
        sp.add_argument("--path", default=DEFAULT_PATH, help="index json path")
        return sp

    s = with_path(sub.add_parser("init", help="create an empty index"))
    s.add_argument("--deck", default="")
    s.add_argument("--force", action="store_true")
    s.set_defaults(func=cmd_init)

    s = with_path(sub.add_parser("import-parser", help="seed from paper_parser json"))
    s.add_argument("paper")
    s.add_argument("--document", default="")
    s.set_defaults(func=cmd_import_parser)

    s = with_path(sub.add_parser("import-markdown", help="attach captions/context"))
    s.add_argument("md")
    s.set_defaults(func=cmd_import_markdown)

    s = with_path(sub.add_parser("set", help="update a record"))
    s.add_argument("id")
    s.add_argument("--key-idea", dest="key_idea")
    s.add_argument("--caption")
    s.add_argument("--context")
    s.add_argument("--confidence", type=float)
    s.add_argument("--visual", choices=VISUAL_METHODS)
    s.add_argument("--verified", action="store_true")
    s.add_argument("--notes")
    s.add_argument("--page", type=int)
    s.add_argument("--region")
    s.add_argument("--license")
    s.add_argument("--url")
    s.add_argument("--retrieved")
    s.set_defaults(func=cmd_set)

    s = with_path(sub.add_parser("get", help="print a record"))
    s.add_argument("id")
    s.set_defaults(func=cmd_get)

    s = with_path(sub.add_parser("list", help="summarize the index"))
    s.set_defaults(func=cmd_list)

    s = with_path(sub.add_parser("query", help="rank candidates for a key idea"))
    s.add_argument("--key-idea", dest="key_idea", required=True)
    s.add_argument("--top", type=int, default=5)
    s.set_defaults(func=cmd_query)

    s = with_path(sub.add_parser("validate", help="schema + confidence checks"))
    s.set_defaults(func=cmd_validate)

    s = with_path(sub.add_parser("unresolved", help="items needing key idea/visual"))
    s.set_defaults(func=cmd_unresolved)

    s = with_path(sub.add_parser("render-md", help="human-readable view"))
    s.add_argument("--out")
    s.set_defaults(func=cmd_render_md)

    s = with_path(sub.add_parser("request-add", help="log a draft image request"))
    s.add_argument("--slide", required=True)
    s.add_argument("--need", required=True)
    s.add_argument("--candidates")
    s.add_argument("--id")
    s.set_defaults(func=cmd_request_add)

    s = with_path(sub.add_parser("request-resolve", help="resolve an image request"))
    s.add_argument("--request", required=True)
    s.add_argument("--image")
    s.add_argument("--status", required=True,
                   choices=["adopted", "tikz", "external", "dropped"])
    s.set_defaults(func=cmd_request_resolve)

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
