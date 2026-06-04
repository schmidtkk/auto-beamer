#!/usr/bin/env python3
"""
doctor.py — AutoBeamer environment preflight
============================================

The skill needs a runtime it does not control: XeLaTeX, poppler
(pdftoppm/pdfinfo), optionally PyMuPDF + markitdown for figure extraction, CJK
fonts, and a *visual modality* (direct vision or a vision MCP) to inspect
figures. Rather than ship a Docker image, this command **probes** what is present
and writes an environment-state config that the skill reads **in the planning
stage** to choose fallback behavior.

State: `.autobeamer/env_state.json` (env-wide, gitignored). Run before each task.

Dependency classes
-------------------
  hard  : missing -> block the run (non-zero exit). xelatex, pdftoppm, pdfinfo.
  soft  : missing -> degrade a feature.            PyMuPDF, markitdown, CJK fonts.

Agent capability
----------------
A Python script cannot see the agent's own modality or MCP tools, so vision is
resolved from a **model-name lookup table**: the agent self-declares its model id
(which it always knows) and the table maps it to vision support. Unknown ids fall
back to text-only (conservative — caps figure confidence downstream).

Usage
-----
  python doctor.py check                       # probe + write state; exit!=0 if blockers
  python doctor.py set-capability --model ID [--mcp-vision]
  python doctor.py report                       # human-readable summary
"""

from __future__ import annotations

import argparse
import datetime as _dt
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path


STATE_PATH = ".autobeamer/env_state.json"
STATE_VERSION = 1

# ── model → vision capability (prefix match on self-declared model id) ─────────
# Known multimodal model families. Unknown ids are treated as text-only.
VISION_MODEL_PREFIXES = (
    "claude-opus-4", "claude-sonnet-4", "claude-haiku-4",
    "claude-3-5", "claude-3-7", "claude-3",
    "gpt-4o", "gpt-4.1", "gpt-5", "o3", "o4-mini",
    "gemini-1.5", "gemini-2", "gemini-3",
)


def model_has_vision(model_id: str | None) -> bool:
    if not model_id:
        return False
    mid = model_id.strip().lower()
    return any(mid.startswith(p) for p in VISION_MODEL_PREFIXES)


# ── probes ────────────────────────────────────────────────────────────────────

def _binary(name: str) -> tuple[bool, str]:
    path = shutil.which(name)
    if not path:
        return False, ""
    version = ""
    for flag in ("-v", "--version"):
        try:
            out = subprocess.run([name, flag], capture_output=True, text=True,
                                 timeout=10)
            for line in (out.stderr + "\n" + out.stdout).splitlines():
                line = line.strip()
                # Some tools (poppler) treat an unknown flag as a filename and
                # print an I/O error — skip error-looking lines.
                low = line.lower()
                if not line or "error" in low or "couldn't" in low \
                        or "no such file" in low or "usage" in low:
                    continue
                version = line[:80]
                break
            if version:
                break
        except Exception:
            continue
    return True, version


def _module(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except Exception:
        return False


def _cjk_fonts() -> bool:
    if not shutil.which("fc-list"):
        return False
    try:
        out = subprocess.run(["fc-list", ":lang=zh"], capture_output=True,
                             text=True, timeout=10)
        return bool(out.stdout.strip())
    except Exception:
        return False


HARD = ("xelatex", "pdftoppm", "pdfinfo")
HINTS = {
    "xelatex": "Install TeX Live with XeLaTeX (Linux: apt-get install texlive-xetex).",
    "pdftoppm": "Install poppler-utils (Linux: apt-get install poppler-utils).",
    "pdfinfo": "Install poppler-utils (Linux: apt-get install poppler-utils).",
    "pymupdf": "pip install PyMuPDF — enables source-figure extraction (paper_parser).",
    "markitdown": "pip install markitdown — enables caption/context enrichment.",
    "cjk_fonts": "Install Noto Sans CJK (Linux: apt-get install fonts-noto-cjk) — only for bilingual decks.",
}


def probe_deps() -> dict:
    deps: dict = {}
    for name in HARD:
        ok, ver = _binary(name)
        deps[name] = {"kind": "hard", "available": ok, "version": ver,
                      "hint": "" if ok else HINTS[name]}

    pymupdf = _module("fitz")
    deps["pymupdf"] = {"kind": "soft", "available": pymupdf, "version": "",
                       "hint": "" if pymupdf else HINTS["pymupdf"]}

    # markitdown's launcher can exist while the module is uninstalled; require
    # the importable module for it to be usable.
    markitdown_usable = _module("markitdown")
    deps["markitdown"] = {"kind": "soft", "available": markitdown_usable,
                          "version": "", "hint": "" if markitdown_usable else HINTS["markitdown"]}

    cjk = _cjk_fonts()
    deps["cjk_fonts"] = {"kind": "soft", "available": cjk, "version": "",
                         "hint": "" if cjk else HINTS["cjk_fonts"]}
    return deps


# ── profile derivation ────────────────────────────────────────────────────────

def derive_profile(deps: dict, capabilities: dict) -> dict:
    avail = {k: v["available"] for k, v in deps.items()}
    blockers = [k for k in HARD if not avail.get(k)]
    vc_method = capabilities.get("visual_check_method", "text-only")
    return {
        "can_compile": avail.get("xelatex", False),
        "can_render_pdf": avail.get("pdftoppm", False) and avail.get("pdfinfo", False),
        "can_extract_pdf": avail.get("pymupdf", False),
        "can_caption_md": avail.get("markitdown", False),
        "cjk_ready": avail.get("cjk_fonts", False),
        "visual_check_method": vc_method,
        "blockers": blockers,
    }


def _default_capabilities() -> dict:
    return {"model": None, "vision": False, "vision_source": "none",
            "visual_check_method": "text-only"}


# ── state io ──────────────────────────────────────────────────────────────────

def load_state(path: str) -> dict | None:
    p = Path(path)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def save_state(path: str, state: dict) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


# ── commands ──────────────────────────────────────────────────────────────────

def cmd_check(args) -> int:
    prev = load_state(args.path) or {}
    capabilities = prev.get("capabilities") or _default_capabilities()
    deps = probe_deps()
    profile = derive_profile(deps, capabilities)
    state = {
        "version": STATE_VERSION,
        "checked_at": _dt.datetime.now().isoformat(timespec="seconds"),
        "deps": deps,
        "capabilities": capabilities,
        "profile": profile,
    }
    save_state(args.path, state)
    _print_summary(state)
    if profile["blockers"]:
        print(f"\nBLOCKED: missing hard dependencies: {', '.join(profile['blockers'])}")
        for b in profile["blockers"]:
            print(f"  - {b}: {deps[b]['hint']}")
        print("Install the above, then re-run the task.")
        return 1
    return 0


def cmd_set_capability(args) -> int:
    state = load_state(args.path)
    if state is None:
        # allow set-capability before check; build a minimal state
        deps = probe_deps()
        state = {"version": STATE_VERSION,
                 "checked_at": _dt.datetime.now().isoformat(timespec="seconds"),
                 "deps": deps, "capabilities": _default_capabilities(),
                 "profile": {}}
    vision_model = model_has_vision(args.model)
    if vision_model:
        source, method = "model", "direct-vision"
    elif args.mcp_vision:
        source, method = "mcp", "mcp"
    else:
        source, method = "none", "text-only"
    state["capabilities"] = {
        "model": args.model,
        "vision": vision_model or bool(args.mcp_vision),
        "vision_source": source,
        "visual_check_method": method,
    }
    state["profile"] = derive_profile(state["deps"], state["capabilities"])
    save_state(args.path, state)
    print(f"capability set: model={args.model} -> visual_check_method={method}")
    return 0


def _print_summary(state: dict) -> None:
    print(f"# AutoBeamer environment doctor  ({state.get('checked_at','')})")
    for name, d in state["deps"].items():
        mark = "OK " if d["available"] else "-- "
        kind = d["kind"]
        print(f"  [{mark}] {name:<11} ({kind})"
              + (f"  {d['version']}" if d["version"] else "")
              + ("" if d["available"] else f"   -> {d['hint']}"))
    cap = state.get("capabilities", {})
    prof = state.get("profile", {})
    print(f"  visual_check_method : {prof.get('visual_check_method')} "
          f"(model={cap.get('model')}, source={cap.get('vision_source')})")
    print(f"  profile: can_compile={prof.get('can_compile')} "
          f"can_render_pdf={prof.get('can_render_pdf')} "
          f"can_extract_pdf={prof.get('can_extract_pdf')} "
          f"can_caption_md={prof.get('can_caption_md')} "
          f"cjk_ready={prof.get('cjk_ready')}")


def cmd_report(args) -> int:
    state = load_state(args.path)
    if state is None:
        print("no env state yet — run: python tools/doctor.py check")
        return 1
    _print_summary(state)
    if state.get("profile", {}).get("blockers"):
        print(f"  BLOCKERS: {state['profile']['blockers']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="AutoBeamer environment doctor")
    sub = p.add_subparsers(dest="command", required=True)

    def add_path(sp):
        sp.add_argument("--path", default=STATE_PATH, help="env state json path")
        return sp

    s = add_path(sub.add_parser("check", help="probe deps + write state (exit!=0 if blockers)"))
    s.set_defaults(func=cmd_check)

    s = add_path(sub.add_parser("set-capability", help="record agent vision capability"))
    s.add_argument("--model", required=True, help="self-declared model id")
    s.add_argument("--mcp-vision", action="store_true",
                   help="a vision MCP tool is available to the agent")
    s.set_defaults(func=cmd_set_capability)

    s = add_path(sub.add_parser("report", help="print the current env state"))
    s.set_defaults(func=cmd_report)

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
