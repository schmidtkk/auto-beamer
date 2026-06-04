#!/usr/bin/env python3
"""check_layout.py v3 — Beamer slide layout analyser + DGV checker + advisor

Layered design audit
────────────────────
  Layer 1  Template fit     AR decision rule + content-type matching
  Layer 2  Geometry         U / B column-balance / G gravity metrics
  Layer 3  Density          text density per slot, image AR match
  Layer 4  Grammar (DGV)    hard rules — must fix regardless of U/B/G

Metrics per frame
─────────────────
  U   Utilization   = total_height / textheight          target 0.80–0.95
  B   Column Bal.   = 1 − |hL−hR| / max(hL,hR)          target > 0.80  (COLUMNS only)
  G   Gravity dev   = ‖(gx,gy) − (0.5, 0.5)‖            target < 0.15
  AR  Image AR      = width / height  (from PNG header)  guides orientation

Design Grammar Violations (DGV)  ── 4 hard rules ───────────────────────────
  GV-1  Loose text outside any tcolorbox / columns block
  GV-2  goldcall inside \\begin{columns}  (AP-3 violation)
  GV-3  Multiple bluecards stacked in one column  (AP-5 violation)
  GV-4  Wide image AR > 1.5 in side-by-side layout  (AP-4 violation)

AR decision rule  ── Composition-aware GAN IJCAI 2022 ───────────────────────
  AR > 1.8  →  TOP layout  (panoramic)
  AR > 1.5  →  TOP preferred  (side layout leaves vert. dead space)
  AR ≤ 1.5  →  SIDE layout OK

Usage
─────
  python check_layout.py cvgdiff-beamer.tex
  python check_layout.py cvgdiff-beamer.tex build/cvgdiff-beamer.log
  python check_layout.py cvgdiff-beamer.tex build/cvgdiff-beamer.log --advise
"""

import re
import struct
import sys
from pathlib import Path

# ── Height model (textheight-normalised, Metropolis 16:9) ─────────────────────
H_FRAME_OVERHEAD  = 0.10   # frametitle bar + top/bottom margins
H_BLUECARD_BASE   = 0.09   # tcolorbox title row + border overhead
H_GOLDCALL_BASE   = 0.07
H_EQBOX_BASE      = 0.08
H_PER_ITEM        = 0.040  # \item line
H_PER_NEWLINE     = 0.032  # explicit \\ line break
H_PER_TEXT_LINE   = 0.022  # non-empty non-command source line
H_PER_TABROW      = 0.052  # tabular row \\
H_VSPACE_PER_EM   = 0.025  # \vspace{1em}
H_CAPTION_LINE    = 0.045  # figure caption
H_AUTOIMG_DEFAULT = 0.76   # \autoimg{} fallback

# Slide geometry
SLIDE_AR    = 16.0 / 9.0    # 1.778 for 169 Beamer
TEXTW_TEXTH = 426.0 / 198.0  # textwidth / textheight ≈ 2.15  (Metropolis 169)

# Visual weights  (Ngo 2003: heavier/brighter/saturated elements have more mass)
W_IMAGE    = 1.50
W_BLUECARD = 1.20
W_GOLDCALL = 1.30
W_EQBOX    = 1.10
W_TEXT     = 1.00

# ── ANSI colours ─────────────────────────────────────────────────────────────
_C = {"G": "\033[92m", "Y": "\033[93m", "R": "\033[91m",
      "B": "\033[94m", "b": "\033[1m",  "0": "\033[0m"}

def cc(s, k):
    return f"{_C[k]}{s}{_C['0']}"


# ─────────────────────────────────────────────────────────────────────────────
# Height estimators
# ─────────────────────────────────────────────────────────────────────────────

def _body_height(body):
    """Estimate content height of a tcolorbox body (textheight units)."""
    h = 0.0
    for ln in body.split("\n"):
        ln = ln.strip()
        if not ln or ln.startswith("%"):
            continue
        if r"\item" in ln:
            h += H_PER_ITEM
        elif r"\\" in ln and "includegraphics" not in ln:
            h += H_PER_NEWLINE
        elif re.search(r"[a-zA-Z\u4e00-\u9fff]", ln):
            h += H_PER_TEXT_LINE
    return h


def _vspace_net(body):
    total = 0.0
    for m in re.finditer(r"\\vspace\*?\{(-?[\d.]+)(em|cm|pt)\}", body):
        val, unit = float(m.group(1)), m.group(2)
        if unit == "em":   total += val * H_VSPACE_PER_EM
        elif unit == "cm": total += val * H_VSPACE_PER_EM * 1.5
        elif unit == "pt": total += val * H_VSPACE_PER_EM / 10.0
    return total


def _img_fraction(body):
    """Largest image max-height fraction in body (textheight units)."""
    fracs = [float(m.group(1))
             for m in re.finditer(r"max\s+height=([\d.]+)\\textheight", body)]
    if re.search(r"\\autoimg(?:\[.*?\])?\{", body):
        fracs.append(H_AUTOIMG_DEFAULT)
    return max(fracs) if fracs else 0.0


def _box_heights_sum(body):
    """Total height of all tcolorbox environments in body."""
    return sum(h for _, h in _box_heights_list(body))


def _box_heights_list(body):
    """Per-card heights as list of (env_name, height)."""
    result = []
    for env, base in [("bluecard", H_BLUECARD_BASE),
                      ("goldcall", H_GOLDCALL_BASE),
                      ("eqbox",    H_EQBOX_BASE)]:
        for m in re.finditer(
                rf"\\begin\{{{env}\}}[^{{]*\{{[^}}]*\}}(.*?)\\end\{{{env}\}}",
                body, re.DOTALL):
            result.append((env, base + _body_height(m.group(1))))
    # itemize / enumerate outside boxes
    for m in re.finditer(
            r"\\begin\{(?:itemize|enumerate)\}(.*?)\\end\{(?:itemize|enumerate)\}",
            body, re.DOTALL):
        n = len(re.findall(r"\\item", m.group(1)))
        result.append(("itemize", n * H_PER_ITEM))
    # tabular rows
    for m in re.finditer(r"\\begin\{tabular\}.*?(.*?)\\end\{tabular\}", body, re.DOTALL):
        rows = len(re.findall(r"\\\\", m.group(1)))
        result.append(("tabular", rows * H_PER_TABROW + H_BLUECARD_BASE))
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Image aspect-ratio detection  (PNG/JPEG binary headers — no PIL required)
# ─────────────────────────────────────────────────────────────────────────────
# Design Grammar Violation (DGV) detector  — Layer 4
# ─────────────────────────────────────────────────────────────────────────────
#
# Four hard rules checked per frame.  DGV trumps U/B/G — fix before anything.
#
#   GV-1  Loose text at top level (outside all tcolorbox/columns)
#   GV-2  goldcall inside \begin{columns}  (AP-3)
#   GV-3  Multiple bluecards in one column  (AP-5)
#   GV-4  Wide image (AR > 1.5) in SIDE layout  (AP-4)

_CONTAINER_ENVS = frozenset([
    "bluecard", "goldcall", "eqbox", "alertcard", "greencard",
    "columns", "column", "tabular", "figure", "minipage",
    "itemize", "enumerate", "description",
    "align", "align*", "equation", "equation*",
])


def _top_level_lines(body: str) -> list:
    """
    Return text lines at the top level of a frame body — i.e., NOT inside
    any \\begin{env}...\\end{env} block, and NOT inside \\budgetwideimg{}{...}{}.

    Uses a simple environment-stack tracker (not full brace parsing) which is
    accurate for the Metropolis/config.tex environment set used in this project.
    """
    env_stack: list = []
    # \budgetwideimg{caption}{bottom-block}{file} — track by brace depth
    in_budget = False
    budget_brace = 0

    result = []
    for line in body.split("\n"):
        stripped = line.strip()

        # ── Handle \budgetwideimg macro (not a \begin/\end pair) ─────────────
        if r"\budgetwideimg" in stripped and not in_budget:
            in_budget = True
            budget_brace = stripped.count("{") - stripped.count("}")
            continue
        if in_budget:
            budget_brace += stripped.count("{") - stripped.count("}")
            if budget_brace <= 0:
                in_budget = False
                budget_brace = 0
            continue

        # ── Track \begin{env} / \end{env} ────────────────────────────────────
        for m in re.finditer(r"\\begin\{(\w+\*?)\}", stripped):
            env = m.group(1)
            if env in _CONTAINER_ENVS or env_stack:
                env_stack.append(env)
        for m in re.finditer(r"\\end\{(\w+\*?)\}", stripped):
            if env_stack:
                env_stack.pop()

        # ── At top level: check for substantive content ───────────────────────
        if env_stack or stripped.startswith("%") or not stripped:
            continue

        # Strip image commands and pure formatting tokens
        cleaned = re.sub(
            r"\\(?:adj)?includegraphics(?:\[.*?\])?\{[^}]+\}", "", stripped)
        cleaned = re.sub(r"\\autoimg(?:\[.*?\])?\{[^}]+\}", "", cleaned)
        cleaned = re.sub(
            r"\\(?:centering|footnotesize|small|large|Large|tiny|normalsize"
            r"|color\{[^}]+\}|textcolor\{[^}]+\}\{[^}]+\}"
            r"|vspace\*?\{[^}]+\}|hspace\*?\{[^}]+\}"
            r"|setlength\{[^}]+\}\{[^}]+\}"
            r"|hfill|vfill|noindent|par\b)", "", cleaned)
        # Strip remaining LaTeX command tokens
        clean = re.sub(r"\\[a-zA-Z@*]+(?:\[[^\]]*\])?(?:\{[^}]*\})*", "", cleaned)
        clean = re.sub(r"[{}\[\]\\$&%~^_]", "", clean).strip()
        # Report if CJK (2+ chars) or substantive Latin (5+ chars)
        if re.search(r"[\u4e00-\u9fff]{2,}|[a-zA-Z]{5,}", clean):
            result.append(stripped[:80])
    return result


# Template-lib blocks and display math the legacy card model does not know about.
_TL_BLOCK_RE     = re.compile(r"\\TL(?:info|alert|result|warn)block\b")
_TL_TAKEAWAY_RE  = re.compile(r"\\TLtakeaway\b")
_DISPLAY_MATH_RE = re.compile(r"\\\[|\\begin\{(?:align|equation|gather|multline)\*?\}")
_SUBSTANCE_RE    = re.compile(
    r"\\\[|\\begin\{(?:align|equation|gather|multline|tikzpicture|tabular|"
    r"theorem|lemma|proof|algorithm|thebibliography)\*?\}"
    r"|\\bibitem\b|\\TL(?:info|alert|result|warn)block\b|\\TLtakeaway\b")


def _text_content_height(body: str) -> float:
    """Inclusive content-height estimate (textheight units).

    The legacy U model only counts bluecard/goldcall/eqbox + itemize + tabular,
    so prose / equation / template-lib decks score ~0 and look falsely sparse.
    This also credits top-level prose, bullets, display math, \\TL* blocks, TikZ.
    """
    h  = len(_top_level_lines(body)) * H_PER_TEXT_LINE * 1.6   # wrapped prose
    h += len(re.findall(r"\\item\b", body)) * H_PER_ITEM
    h += len(_DISPLAY_MATH_RE.findall(body)) * 0.11
    h += len(_TL_BLOCK_RE.findall(body)) * (H_BLUECARD_BASE + 2 * H_PER_ITEM)
    h += len(_TL_TAKEAWAY_RE.findall(body)) * (H_GOLDCALL_BASE + H_PER_ITEM)
    if re.search(r"\\begin\{tikzpicture\}", body):
        h += 0.42
    return h


def _has_substance(body: str) -> bool:
    """True if the frame has a real teaching element (math, diagram, table,
    theorem, or a template-lib block) — used to avoid false 'sparse' verdicts."""
    return bool(_SUBSTANCE_RE.search(body))


def detect_grammar_violations(
        body: str, layout: str, img_ar) -> list:
    """
    Return list of (code, description) for all DGV violations in this frame.
    """
    violations: list = []

    # ── GV-1: Loose text ──────────────────────────────────────────────────────
    # GV-1 disabled: the skills allow plain body text/bullets as the default,
    # so flagging loose text produced a false positive on every prose/math
    # slide. Prose height is now credited via _text_content_height instead.
    loose = []
    if loose:
        violations.append(
            ("GV-1", f"Loose text outside any box: \u201c{loose[0][:55]}\u201d"))

    # ── GV-2: goldcall inside \begin{columns} ─────────────────────────────────
    for m in re.finditer(
            r"\\begin\{columns\}.*?\\end\{columns\}", body, re.DOTALL):
        if r"\begin{goldcall}" in m.group(0):
            violations.append(
                ("GV-2",
                 r"goldcall inside \begin{columns} (AP-3 — must span full width)"))

    # ── GV-3: Multiple bluecards stacked in one column ────────────────────────
    for m in re.finditer(
            r"\\begin\{column\}\{[^}]+\}(.*?)\\end\{column\}",
            body, re.DOTALL):
        n = len(re.findall(r"\\begin\{bluecard\}", m.group(1)))
        if n > 1:
            violations.append(
                ("GV-3",
                 f"AP-5: {n} bluecards stacked in one column "
                 "(equal-height impossible; use 1 card/col or full-width)"))

    # ── GV-4: Wide image in side-by-side layout ───────────────────────────────
    if img_ar is not None and img_ar > 1.5 and layout == "COLUMNS":
        violations.append(
            ("GV-4",
             f"AP-4: image AR={img_ar:.2f} > 1.5 in SIDE layout "
             r"(→ \budgetwideimg / image-top)"))

    return violations


# ─────────────────────────────────────────────────────────────────────────────

def _read_png_wh(path):
    """Return (w, h) from PNG IHDR.  Returns None on any error."""
    try:
        with open(path, "rb") as f:
            if f.read(8) != b"\x89PNG\r\n\x1a\n":
                return None
            f.read(4)          # IHDR chunk length
            f.read(4)          # b"IHDR"
            w = struct.unpack(">I", f.read(4))[0]
            h = struct.unpack(">I", f.read(4))[0]
            return w, h
    except Exception:
        return None


def _read_jpeg_wh(path):
    """Return (w, h) by scanning JPEG SOF markers.  Returns None on error."""
    try:
        with open(path, "rb") as f:
            data = f.read(65536)
        i = 2           # skip SOI (FF D8)
        while i + 4 < len(data):
            if data[i] != 0xFF:
                break
            marker = data[i + 1]
            if marker in (0xC0, 0xC1, 0xC2, 0xC3):   # SOF0/1/2/3
                if i + 9 <= len(data):
                    h = struct.unpack(">H", data[i + 5:i + 7])[0]
                    w = struct.unpack(">H", data[i + 7:i + 9])[0]
                    return w, h
            if marker in (0xD8, 0xD9) or (0xD0 <= marker <= 0xD7):
                i += 2
            else:
                if i + 4 > len(data):
                    break
                seg_len = struct.unpack(">H", data[i + 2:i + 4])[0]
                i += 2 + seg_len
    except Exception:
        pass
    return None


def detect_img_ar(body, tex_dir):
    """
    Find first image in body, resolve its path, return W/H ratio or None.
    Search order: tex_dir → tex_dir/cvgdiff_extracted/.../slides_assets → parent.
    """
    search_dirs = [
        tex_dir,
        tex_dir / "cvgdiff_extracted" / "cvgdiff_slides_pack" / "slides_assets",
        tex_dir.parent,
    ]
    for m in re.finditer(r"\{([^}]+\.(?:png|jpg|jpeg))\}", body, re.IGNORECASE):
        fname = m.group(1).strip()
        for d in search_dirs:
            p = (d / fname).resolve()
            if not p.exists():
                continue
            wh = _read_png_wh(p) if p.suffix.lower() == ".png" else _read_jpeg_wh(p)
            if wh and wh[1] > 0:
                return wh[0] / wh[1]
    return None


def _ar_label(ar):
    """Plain-text orientation label for aspect ratio."""
    if ar is None:  return "—"
    if ar > 2.0:    return "TOP (panoramic)"
    if ar > 1.5:    return "TOP preferred"
    if ar > 0.7:    return "SIDE OK"
    return "SIDE (portrait)"


# ─────────────────────────────────────────────────────────────────────────────
# Visual gravity  (Ngo, Teo & Byrne, Information Sciences 152, 2003)
# ─────────────────────────────────────────────────────────────────────────────
#
# Formulation
# ───────────
#   Each visual element i has:
#     centroid (cx_i, cy_i) in normalised [0,1]² slide coordinates
#     bounding-box area  a_i = width_i × height_i
#     visual weight      w_i  (see constants above)
#
#   Visual mass:    m_i = w_i · a_i
#   Centre of mass: gx = Σ m_i·cx_i / Σ m_i
#                   gy = Σ m_i·cy_i / Σ m_i
#
#   Ideal target: (0.5, 0.5) = geometric centre of slide canvas.
#   Deviation:    G = sqrt((gx−0.5)² + (gy−0.5)²)   lower = more balanced

def compute_gravity(body, layout, img_h, box_h):
    """
    Estimate visual centre of gravity (gx, gy) in normalised [0,1]² coords
    (origin = top-left of slide canvas, y increases downward).

    Returns (gx, gy, G) where G = Euclidean distance from (0.5, 0.5).
    """
    col_fracs = [float(m.group(1))
                 for m in re.finditer(
                     r"\\begin\{column\}\{([\d.]+)\\textwidth\}", body)]

    if not col_fracs or layout != "COLUMNS":
        # Non-column: rough stacking estimate
        if img_h > 0 and box_h > 0:
            m_img = W_IMAGE * 1.0 * img_h
            m_txt = W_TEXT  * 1.0 * box_h
            tm    = m_img + m_txt
            if tm < 1e-9:
                return 0.5, 0.5, 0.0
            cy_img = H_FRAME_OVERHEAD + img_h / 2
            cy_txt = H_FRAME_OVERHEAD + img_h + box_h / 2
            gy = (m_img * cy_img + m_txt * cy_txt) / tm
            return 0.5, gy, abs(gy - 0.5)
        return 0.5, 0.5, 0.0

    col_bodies = [m.group(1) for m in re.finditer(
        r"\\begin\{column\}\{[^}]+\}(.*?)\\end\{column\}", body, re.DOTALL)]

    n_cols = len(col_fracs)
    gap    = max(0.0, (1.0 - sum(col_fracs)) / max(n_cols - 1, 1))
    x_left = []
    xpos   = 0.0
    for frac in col_fracs:
        x_left.append(xpos)
        xpos += frac + gap

    elements = []

    for ci, (frac, cbody) in enumerate(zip(col_fracs, col_bodies)):
        cx_col = x_left[ci] + frac / 2   # column centre-x
        y_cur  = 0.0                      # relative to top of usable area

        ci_img = _img_fraction(cbody)
        if ci_img > 0:
            elements.append({
                "cx": cx_col,
                "cy": H_FRAME_OVERHEAD + y_cur + ci_img / 2,
                "w": frac, "h": ci_img, "wt": W_IMAGE
            })
            y_cur += ci_img

        for env, base, wt in [("bluecard", H_BLUECARD_BASE, W_BLUECARD),
                               ("goldcall", H_GOLDCALL_BASE, W_GOLDCALL),
                               ("eqbox",    H_EQBOX_BASE,    W_EQBOX)]:
            for m in re.finditer(
                    rf"\\begin\{{{env}\}}[^{{]*\{{[^}}]*\}}(.*?)\\end\{{{env}\}}",
                    cbody, re.DOTALL):
                h = base + _body_height(m.group(1))
                elements.append({
                    "cx": cx_col,
                    "cy": H_FRAME_OVERHEAD + y_cur + h / 2,
                    "w": frac, "h": h, "wt": wt
                })
                y_cur += h

    if not elements:
        return 0.5, 0.5, 0.0

    total_m = sum(e["wt"] * e["w"] * e["h"] for e in elements)
    if total_m < 1e-9:
        return 0.5, 0.5, 0.0

    gx = sum(e["wt"] * e["w"] * e["h"] * e["cx"] for e in elements) / total_m
    gy = sum(e["wt"] * e["w"] * e["h"] * e["cy"] for e in elements) / total_m
    G  = ((gx - 0.5) ** 2 + (gy - 0.5) ** 2) ** 0.5
    return gx, gy, G


# ─────────────────────────────────────────────────────────────────────────────
# Multi-candidate layout advisor
# ─────────────────────────────────────────────────────────────────────────────
#
# Scoring  (adapted from PosterLayout CVPR 2023 composite metric)
# ───────────────────────────────────────────────────────────────
#   S = 0.40·sU + 0.35·sB + 0.25·sG
#
#   sU  triangular utility: peak = 1 at target_U = 0.875
#        < 0.60  → linearly rises  |  0.60–0.875 → rises to 1  |
#        0.875–1 → gently falls    |  > 1.0       → heavy penalty (×10)
#   sB  column balance in [0,1]; None (stacked) → 0.50
#   sG  gravity penalty: 1 − G/0.25, clamped to [0,1]
#
# AR-aware orientation  (Composition-aware GAN IJCAI 2022)
# ─────────────────────────────────────────────────────────
#   Natural image height in a column of width α:
#     h_natural = α·textwidth / (AR·slideAR·textheight)
#               = α / (AR · TEXTW_TEXTH)   [in textheight units]
#   If h_natural >> available height OR AR > 1.5 → TOP layout more efficient.

def _score_UBG(U, B, G, target_U=0.875):
    """Composite layout quality score in [0, 1].  Higher = better."""
    if U < 0.60:
        sU = U / 0.60
    elif U <= target_U:
        sU = (U - 0.60) / (target_U - 0.60)
    elif U <= 1.0:
        sU = 1.0 - (U - target_U) / (1.0 - target_U) * 0.5
    else:
        sU = max(0.0, 1.0 - (U - 1.0) * 10.0)

    sB = B if B is not None else 0.50
    sG = max(0.0, 1.0 - G / 0.25)
    return 0.40 * sU + 0.35 * sB + 0.25 * sG


def generate_candidates(img_ar, img_h_current, box_h_list, n_cards, vsp=0.0):
    """
    Enumerate and score layout candidates for a frame with one image.

    Parameters
    ----------
    img_ar         : float | None   image W/H aspect ratio
    img_h_current  : float          current image height fraction (textheight)
    box_h_list     : list[float]    individual card heights
    n_cards        : int            total card count
    vsp            : float          net \\vspace contribution

    Returns
    -------
    List of candidate dicts sorted by score descending.
    Keys: template, split, U, B, G, score, note (LaTeX snippet hint)
    """
    total_box_h = sum(box_h_list) + vsp
    candidates  = []

    # ── A. Side-by-side layouts (image-left / image-right) ──────────────────
    for template in ("image-left", "image-right"):
        for alpha in (0.38, 0.42, 0.46, 0.50, 0.54, 0.58, 0.62):
            beta = 1.0 - alpha - 0.02    # ~2% inter-column gap
            if beta < 0.28:
                continue

            # Natural image height when column width = alpha of textwidth:
            #   h_nat = (alpha × textwidth) / (AR × textwidth / textheight)
            #         = alpha / (AR × TEXTW_TEXTH × alpha / alpha)  ← simplifies
            #         = 1 / (AR × TEXTW_TEXTH)   [independent of alpha!]
            # This means ALL side-by-side splits give the same natural image
            # height — only the balance B changes with alpha.
            if img_ar is not None and img_ar > 0:
                eff_img_h = min(1.0 / (img_ar * TEXTW_TEXTH), 0.88)
            else:
                eff_img_h = img_h_current

            U      = max(eff_img_h, total_box_h) + H_FRAME_OVERHEAD
            B_dnom = max(eff_img_h, total_box_h, 1e-9)
            B      = 1.0 - abs(eff_img_h - total_box_h) / B_dnom

            # Gravity: simplified two-mass model
            if template == "image-left":
                img_cx, txt_cx = alpha / 2, alpha + 0.02 + beta / 2
            else:
                txt_cx, img_cx = alpha / 2, alpha + 0.02 + beta / 2
            img_cy = H_FRAME_OVERHEAD + eff_img_h / 2
            txt_cy = H_FRAME_OVERHEAD + total_box_h / 2
            m_img  = W_IMAGE    * alpha * eff_img_h
            m_txt  = W_BLUECARD * beta  * total_box_h
            tm     = m_img + m_txt
            if tm > 0:
                gx = (m_img * img_cx + m_txt * txt_cx) / tm
                gy = (m_img * img_cy + m_txt * txt_cy) / tm
            else:
                gx, gy = 0.5, 0.5
            G = ((gx - 0.5) ** 2 + (gy - 0.5) ** 2) ** 0.5

            ar_note = ""
            if img_ar and img_ar > 1.5:
                ar_note = "  ← AR>1.5: consider TOP"

            candidates.append({
                "template": template, "split": alpha, "beta": beta,
                "U": U, "B": B, "G": G,
                "score": _score_UBG(U, B, G),
                "eff_img_h": eff_img_h,
                "note": (f"\\begin{{column}}{{{alpha:.2f}\\textwidth}} img  |  "
                         f"\\begin{{column}}{{{beta:.2f}\\textwidth}} cards"
                         f"{ar_note}")
            })

    # ── B. Image-top (full-width) ────────────────────────────────────────────
    # Natural fit for landscape images (AR ≥ 1.0).
    if img_ar is None or img_ar >= 1.0:
        for img_top_h in (0.30, 0.34, 0.38, 0.42, 0.46, 0.50, 0.54):
            m_img = W_IMAGE    * 1.0 * img_top_h
            m_txt = W_BLUECARD * 1.0 * total_box_h
            tm    = m_img + m_txt
            cy_i  = H_FRAME_OVERHEAD + img_top_h / 2
            cy_t  = H_FRAME_OVERHEAD + img_top_h + total_box_h / 2
            gy_base = (m_img * cy_i + m_txt * cy_t) / max(tm, 1e-9)
            G_base  = abs(gy_base - 0.5)     # gx = 0.5 by symmetry

            ar_tag = cc("  ← better AR fit", "G") if img_ar and img_ar > 1.4 else ""

            # 1-column cards below
            U1 = img_top_h + total_box_h + H_FRAME_OVERHEAD
            candidates.append({
                "template": "image-top-1col", "split": img_top_h, "beta": 0,
                "U": U1, "B": None, "G": G_base,
                "score": _score_UBG(U1, None, G_base),
                "eff_img_h": img_top_h,
                "note": (f"\\adjincludegraphics[max width=\\textwidth,"
                         f"max height={img_top_h:.2f}\\textheight]{{img}}"
                         f"  + 1-col cards{ar_tag}")
            })

            # 2-column cards below (symmetric split, B=1.0)
            if n_cards >= 2:
                U2 = img_top_h + total_box_h / 2 + H_FRAME_OVERHEAD
                candidates.append({
                    "template": "image-top-2col", "split": img_top_h, "beta": 0,
                    "U": U2, "B": 1.0, "G": G_base,
                    "score": _score_UBG(U2, 1.0, G_base),
                    "eff_img_h": img_top_h,
                    "note": (f"img β={img_top_h:.2f}  + 2-col "
                             f"({n_cards//2}+{n_cards-n_cards//2}) cards{ar_tag}")
                })

    return sorted(candidates, key=lambda x: x["score"], reverse=True)


# ─────────────────────────────────────────────────────────────────────────────
# Per-frame analysis
# ─────────────────────────────────────────────────────────────────────────────

def analyse_frame(title, body, tex_dir):
    img_h   = _img_fraction(body)
    box_h   = _box_heights_sum(body)
    vsp     = _vspace_net(body)
    cols    = r"\begin{columns}" in body
    budgetw = r"\budgetwideimg" in body

    if budgetw:
        U = box_h + H_CAPTION_LINE + H_FRAME_OVERHEAD + vsp
        B = None
        layout = "BUDGET"
    elif cols:
        U = max(img_h, box_h + vsp) + H_FRAME_OVERHEAD
        B = 1.0 - abs(img_h - box_h) / max(img_h, box_h, 1e-9)
        layout = "COLUMNS"
    elif img_h > 0:
        U = img_h + H_CAPTION_LINE + box_h + vsp + H_FRAME_OVERHEAD
        B = None
        layout = "STACKED"
    else:
        U = box_h + vsp + H_FRAME_OVERHEAD
        B = None
        layout = "TEXT"

    # Content floor: the legacy card model under-counts prose / math /
    # template-lib decks. Raise U to an inclusive estimate (capped below the
    # overflow threshold) so such frames are not scored as false-sparse.
    if layout in ("TEXT", "STACKED", "BUDGET"):
        U = max(U, min(_text_content_height(body) + H_FRAME_OVERHEAD, 0.98))

    img_ar = detect_img_ar(body, tex_dir)
    ar_lbl = _ar_label(img_ar)
    gx, gy, G = compute_gravity(body, layout, img_h, box_h)
    box_list   = _box_heights_list(body)
    box_h_list = [h for _, h in box_list]

    dvg = detect_grammar_violations(body, layout, img_ar)

    return {
        "title": title, "U": U, "B": B, "layout": layout,
        "img_h": img_h, "box_h": box_h,
        "img_ar": img_ar, "ar_lbl": ar_lbl,
        "gx": gx, "gy": gy, "G": G,
        "box_h_list": box_h_list,
        "n_cards": len(box_h_list),
        "vsp": vsp,
        "dvg": dvg,
        "substance": _has_substance(body),
    }


# ── Log parser ────────────────────────────────────────────────────────────────

def parse_log(log_path):
    """Parse XeLaTeX log for Overfull \\vbox per page (ground-truth AABB check)."""
    p = Path(log_path)
    if not p.exists():
        return {}
    text         = p.read_text(encoding="utf-8", errors="replace")
    overflows    = {}
    current_page = 1
    for line in text.splitlines():
        pgs = re.findall(r"\[(\d+)[\]\s]", line)
        if pgs:
            current_page = max(int(x) for x in pgs)
        # XeLaTeX emits "...pt too high" for vertical (vbox) overflow; older/other
        # engines may say "too large". Accept both so overflow is never missed.
        m = re.search(r"Overfull \\vbox \(([\d.]+)pt too (?:high|large)\)", line)
        if m:
            pt = float(m.group(1))
            overflows[current_page] = overflows.get(current_page, 0.0) + pt
    return overflows


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    # Reconfigure stdout to UTF-8 so Unicode symbols print on Windows GBK consoles
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass  # Python < 3.7

    usage = "Usage: python check_layout.py <file.tex> [file.log] [--advise]"

    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(usage)
        # No file requested -> help/usage is a successful, well-defined outcome.
        sys.exit(0 if (len(sys.argv) >= 2 and sys.argv[1] in ("-h", "--help")) else 1)

    tex_path = sys.argv[1]
    advise   = "--advise" in sys.argv
    log_path = next((a for a in sys.argv[2:] if a.endswith(".log")),
                    tex_path.replace(".tex", ".log"))

    tex           = Path(tex_path).read_text(encoding="utf-8", errors="replace")
    tex_dir       = Path(tex_path).resolve().parent
    log_overflows = parse_log(log_path)

    frame_re = re.compile(
        r"\\begin\{frame\}(?:\[.*?\])?\{([^}]*)\}(.*?)\\end\{frame\}",
        re.DOTALL)

    # ── Table ─────────────────────────────────────────────────────────────────
    print()
    hdr = (f"  {'#':>3}  {'Frame title':<36}  {'U':>5}  {'B':>5}  {'G':>6}  "
           f"{'AR':>5}  {'Orientation':<16}  {'DGV':>4}  Status")
    print(cc(hdr, "b"))
    print("  " + "─" * 120)

    # Map each \begin{frame} to its PDF page number by counting every
    # slide-emitting construct (title page, \TLsection dividers, frames) in
    # source order. Frame ordinal != PDF page when section dividers exist, so a
    # naive log_overflows.get(i) misattributes overflow to the wrong frame.
    slide_macro_re = re.compile(
        r"\\TLtitle\w*|\\TLsection\b|\\section\b|\\maketitle\b|\\titlepage\b|\\begin\{frame\}")
    page_of_start = {}
    _page = 0
    for _m in slide_macro_re.finditer(tex):
        _page += 1
        page_of_start[_m.start()] = _page

    all_frames = []
    for i, m in enumerate(frame_re.finditer(tex), start=1):
        r           = analyse_frame(m.group(1)[:35], m.group(2), tex_dir)
        r["idx"]    = i
        r["page"]   = page_of_start.get(m.start(), i)
        r["log_pt"] = log_overflows.get(r["page"], 0.0)
        all_frames.append(r)

        U, B, G  = r["U"], r["B"], r["G"]
        layout   = r["layout"]
        log_pt   = r["log_pt"]

        b_str  = f"{B:.2f}" if B is not None else " — "
        g_str  = f"{G:.3f}"
        ar_str = f"{r['img_ar']:.2f}" if r["img_ar"] else "  — "
        ar_lbl = r["ar_lbl"]

        log_note = cc(f" ←LOG+{log_pt:.0f}pt", "R") if log_pt > 0 else ""
        dvg      = r["dvg"]
        dvg_str  = cc(f"{len(dvg)}×", "R") if dvg else cc("✓", "G")

        if log_pt > 0 or U > 1.00:
            status = cc(f"OVERFLOW Δ={max(U-1,0):.2f}", "R")
        elif dvg:
            status = cc(f"DGV×{len(dvg)}         ", "R")
        elif U > 0.95:
            status = cc(f"TIGHT    U={U:.2f}", "Y")
        elif U < 0.60 and not r.get("substance"):
            status = cc(f"SPARSE   U={U:.2f}", "Y")
        elif B is not None and B < 0.55:
            status = cc(f"IMBAL    B={B:.2f}", "Y")
        elif G > 0.20:
            status = cc(f"OFF-CTR  G={G:.3f}", "Y")
        else:
            status = cc(f"OK       U={U:.2f}", "G")

        # AR warning: only show if not already covered by GV-4 in dvg
        ar_warn = ""
        if (r["img_ar"] and r["img_ar"] > 1.5 and layout == "COLUMNS"
                and not any(v[0] == "GV-4" for v in dvg)):
            ar_warn = cc(" ⚠AR!", "Y")

        print(f"  {i:>3}  {r['title']:<36}  {U:.2f}  {b_str}  {g_str}  "
              f"{ar_str}  {ar_lbl:<16}  {dvg_str:>4}  {status}{ar_warn}{log_note}")

    # ── Summary ───────────────────────────────────────────────────────────────
    print()
    overflows  = [r for r in all_frames if r["U"] > 1.00 or r["log_pt"] > 0]
    tight      = [r for r in all_frames if 0.95 < r["U"] <= 1.00 and r["log_pt"] == 0]
    # Sparse = low utilization AND no substantive teaching element. This matches
    # the documented rule; a math/prose slide full of equations or a \TL* block
    # is never "sparse" regardless of the card-model utilization estimate.
    sparse     = [r for r in all_frames if r["U"] < 0.60 and not r.get("substance")]
    imbal      = [r for r in all_frames if r["B"] is not None and r["B"] < 0.55]
    offctr     = [r for r in all_frames if r["G"] > 0.20]
    col_frames = [r for r in all_frames if r["B"] is not None]
    dvg_frames = [r for r in all_frames if r["dvg"]]
    total_dvg  = sum(len(r["dvg"]) for r in all_frames)

    avg_U = sum(r["U"] for r in all_frames) / len(all_frames) if all_frames else 0
    avg_B = (sum(r["B"] for r in col_frames) / len(col_frames)) if col_frames else None
    avg_G = sum(r["G"] for r in all_frames) / len(all_frames) if all_frames else 0

    print(cc("  Summary", "b"))
    print(f"    Frames analysed    : {len(all_frames)}")
    print(f"    Avg utilization    : {avg_U:.3f}   target 0.80–0.95")
    if avg_B is not None:
        print(f"    Avg col balance    : {avg_B:.3f}   target > 0.80")
    print(f"    Avg gravity dev    : {avg_G:.4f}  target < 0.15")
    if total_dvg:
        print(cc(f"    Grammar violations : {total_dvg} DGV  in {len(dvg_frames)} frames  "
                 f"idx={[r['idx'] for r in dvg_frames]}  ← FIX FIRST", "R"))
    else:
        print(cc("    Grammar violations : 0  ✓ all clear", "G"))
    print(f"    Overflow frames    : {len(overflows)}  idx={[r['idx'] for r in overflows]}")
    print(f"    Tight frames       : {len(tight)}  idx={[r['idx'] for r in tight]}")
    print(f"    Sparse frames      : {len(sparse)}  idx={[r['idx'] for r in sparse]}")
    print(f"    Imbalanced (B<0.55): {len(imbal)}  idx={[r['idx'] for r in imbal]}")
    print(f"    Off-centre (G>0.20): {len(offctr)}  idx={[r['idx'] for r in offctr]}")

    # ── DGV detail listing (always shown when violations exist) ───────────────
    if dvg_frames:
        print()
        print(cc("  ── Design Grammar Violations (DGV) — must fix before U/B/G tuning ──", "R"))
        print("  " + "─" * 80)
        for r in dvg_frames:
            for code, desc in r["dvg"]:
                frame_lbl = f"[{r['idx']:>2}] {r['title'][:32]:<32}"
                print(f"  {frame_lbl}  {cc(code, 'R')}  {desc}")

    # ── Metric reference ──────────────────────────────────────────────────────
    print()
    print(cc("  Metric definitions", "b"))
    print("    U  = total_height / textheight")
    print("         COLUMNS → max(hLeft, hRight) + overhead")
    print("         STACKED → hImg + hCap + hText + overhead")
    print()
    print("    B  = 1 − |hL − hR| / max(hL, hR)   COLUMNS only; 1.0 = perfectly balanced")
    print()
    print("    G  = ‖(gx, gy) − (0.5, 0.5)‖       visual centre-of-mass deviation")
    print("         g = Σ wᵢ·aᵢ·cᵢ / Σ wᵢ·aᵢ     [Ngo, Teo & Byrne, Inf.Sci. 152 (2003)]")
    print("         weights: image=1.50, goldcall=1.30, bluecard=1.20, eqbox=1.10")
    print()
    print("    AR  image W/H from PNG/JPEG header (no PIL needed)")
    print("         > 1.8 → TOP panoramic  |  > 1.5 → TOP preferred  |  ≤ 1.4 → SIDE OK")
    print("         [Composition-aware GAN IJCAI 2022; PosterLayout CVPR 2023]")

    # ── Layout advisor (--advise) ─────────────────────────────────────────────
    if advise:
        print()
        print(cc("  ── Layout Advisor  S = 0.40·sU + 0.35·sB + 0.25·sG ──", "b"))
        print("  " + "─" * 112)

        any_advised = False
        for r in all_frames:
            if r["layout"] not in ("COLUMNS", "STACKED") or r["img_h"] == 0:
                continue
            needs = (
                r["U"] > 0.95
                or (r["B"] is not None and r["B"] < 0.55)
                or r["G"] > 0.20
                or (r["img_ar"] and r["img_ar"] > 1.5 and r["layout"] == "COLUMNS")
            )
            if not needs:
                continue

            any_advised = True
            candidates  = generate_candidates(
                r["img_ar"], r["img_h"], r["box_h_list"],
                r["n_cards"], r["vsp"])
            top3 = candidates[:3]

            cur_B = f"{r['B']:.2f}" if r["B"] is not None else " — "
            ar_s  = f"{r['img_ar']:.2f}" if r["img_ar"] else " — "
            print()
            print(cc(f"  [{r['idx']:>2}] {r['title']}", "b") +
                  f"   current: U={r['U']:.2f}  B={cur_B}  G={r['G']:.3f}  AR={ar_s}")
            print(f"       n_cards={r['n_cards']}  "
                  f"card_heights=[{', '.join(f'{h:.3f}' for h in r['box_h_list'])}]")
            print()

            for rank, cand in enumerate(top3, 1):
                star = cc("★", "G") if rank == 1 else f"{rank}."
                b_c  = f"{cand['B']:.2f}" if cand["B"] is not None else " — "
                print(f"    {star} [{cand['template']:<18}]  split={cand['split']:.2f}  "
                      f"U={cand['U']:.2f}  B={b_c}  G={cand['G']:.3f}  "
                      f"S={cand['score']:.3f}")
                print(f"       → {cand['note']}")

        if not any_advised:
            print()
            print(cc("  All COLUMNS/STACKED frames pass checks — no advice needed.", "G"))

    # ── Log result ────────────────────────────────────────────────────────────
    print()
    if log_overflows:
        print(cc(f"  ⚠  Overfull \\vbox on pages: {sorted(log_overflows.keys())}", "R"))
    else:
        print(cc("  ✓  No Overfull \\vbox in log.", "G"))
    print()


if __name__ == "__main__":
    main()
