#!/usr/bin/env python3
"""
layout_optimizer.py — Beamer slide layout optimizer  (layered design)
=====================================================================
Template selection uses a DECISION TREE (Layer 1), not a scoring function.
Scoring validates the decision; it does not drive it.

Layered design philosophy
─────────────────────────
  Layer 1  Template Decision    Binary decision tree: n_img, AR, n_cards, eq
  Layer 2  Element Constraints  Column balance, natural image height, slot fit
  Layer 3  Content Density      Text fills 60–85% of slot; image AR match
  Layer 4  Grammar Rules (DGV)  Hard rules: GV-1 to GV-4  (must not violate)

AR decision thresholds
──────────────────────
  AR > 1.6  →  \budgetwideimg (TOP layout)
  AR ∈ (1.4, 1.6]  →  TOP preferred; side sub-optimal
  AR ≤ 1.4 + ≤2 cards  →  SIDE layout balanced

Usage
-----
  python layout_optimizer.py rank   [--img w:h] [--img w:h] [--cards N]
                                    [--lines N] [--eq] [--gold]
  python layout_optimizer.py suggest <same flags>   # layered analysis + skeleton
  python layout_optimizer.py iterate               # build PDF, re-pick on overflow

Examples
--------
  # Single wide image (1716×1124) + 2 cards + goldcall
  python layout_optimizer.py rank --img 1716:1124 --cards 2 --gold

  # Three CT images of equal AR + 2 cards
  python layout_optimizer.py suggest --img 512:512 --img 512:512 --img 512:512 --cards 2

  # Equation slide: eqbox + 2 cards
  python layout_optimizer.py suggest --cards 2 --eq
"""

from __future__ import annotations

import argparse
import math
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

# ─────────────────────────────────────────────────────────────────────────────
# Metropolis frame constants (aspectratio=169, 10pt)
# ─────────────────────────────────────────────────────────────────────────────
TEXTHEIGHT_PT  = 198.0   # content height after frametitle strip  (~198 pt)
TEXTWIDTH_PT   = 398.0   # full content width                     (~398 pt = ~140 mm)
LINE_HEIGHT_PT = 13.0    # one body line in footnotesize
HEADER_OVERHEAD_PT = 5.0 # padding between top of frame content and first element


# ─────────────────────────────────────────────────────────────────────────────
# Element types  (LayoutGPT-style structured representation)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Img:
    """An image asset with known pixel dimensions."""
    name: str = "figure.png"
    w: int = 1280
    h: int = 720

    @property
    def ar(self) -> float:          # width / height
        return self.w / max(self.h, 1)

    @property
    def orientation(self) -> Literal["wide", "square", "tall"]:
        if self.ar > 1.6:
            return "wide"
        if self.ar < 0.85:
            return "tall"
        return "square"


@dataclass
class Card:
    kind: Literal["blue", "gold", "eqbox", "plain"] = "blue"
    title: str = ""
    lines: int = 5              # estimated body lines


@dataclass
class SlideSpec:
    """Full description of one slide's content (LayoutGPT-style spec dict)."""
    title: str = ""
    images: list[Img]  = field(default_factory=list)
    cards:  list[Card] = field(default_factory=list)
    equation: bool = False      # has a display equation (separate from eqbox card)

    # ── derived properties ─────────────────────────────────────────────────
    @property
    def n_img(self):  return len(self.images)
    @property
    def n_card(self): return sum(1 for c in self.cards if c.kind != "gold")
    @property
    def has_gold(self): return any(c.kind == "gold" for c in self.cards)
    @property
    def text_lines(self):
        """Estimated total typeset lines for all non-gold cards."""
        return sum(c.lines + (1 if c.title else 0)
                   for c in self.cards if c.kind != "gold")
    @property
    def gold_lines(self):
        return sum(c.lines for c in self.cards if c.kind == "gold")
    @property
    def avg_img_ar(self) -> float:
        if not self.images: return 1.78
        return sum(i.ar for i in self.images) / len(self.images)


# ─────────────────────────────────────────────────────────────────────────────
# Slot spec  (bounding-box representation, LayoutDM-style)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Slot:
    """One rectangular region in a template layout."""
    kind:   Literal["image", "text", "gold", "eq"]
    width:  float   # fraction of textwidth  [0, 1]
    height: float   # fraction of textheight [0, 1]

    @property
    def ar(self) -> float:
        return (self.width * TEXTWIDTH_PT) / max(self.height * TEXTHEIGHT_PT, 1)

    @property
    def area(self) -> float:
        return self.width * self.height


# ─────────────────────────────────────────────────────────────────────────────
# Template catalog  (config.tex macros mapped to slot layouts)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Template:
    name:   str
    macro:  str          # config.tex macro / pattern name
    slots:  list[Slot]
    notes:  str = ""

    @property
    def utilization(self) -> float:
        """Total occupied area fraction (LayoutDM utilization metric)."""
        return sum(s.area for s in self.slots)

    def image_slots(self) -> list[Slot]:
        return [s for s in self.slots if s.kind == "image"]

    def text_slots(self) -> list[Slot]:
        return [s for s in self.slots if s.kind in ("text", "eq")]

    def gold_slot(self) -> Slot | None:
        g = [s for s in self.slots if s.kind == "gold"]
        return g[0] if g else None


TEMPLATES: list[Template] = [
    # ── 0: Text-only (two columns of cards) ──────────────────────────────────
    Template(
        "text-only", "\\begin{columns}",
        [Slot("text", 0.48, 0.75), Slot("text", 0.48, 0.75),
         Slot("gold", 1.00, 0.12)],
        notes="No images; 2-col cards + optional goldcall",
    ),
    # ── 1: Image left, cards right (portrait / square images) ────────────────
    Template(
        "image-left", "\\begin{columns}[c] 0.45/0.52",
        [Slot("image", 0.44, 0.75), Slot("text", 0.52, 0.75)],
        notes="Portrait or square image left; 1-col cards right; AP-2 alt",
    ),
    # ── 2: Image right, cards left ────────────────────────────────────────────
    Template(
        "image-right", "\\begin{columns}[c] 0.52/0.44",
        [Slot("text", 0.52, 0.75), Slot("image", 0.44, 0.75)],
        notes="Mirror of image-left",
    ),
    # ── 3: Image top, cards below  (\budgetwideimg) — AP-4 fix ───────────────
    Template(
        "image-top", "\\budgetwideimg",
        [Slot("image", 1.00, 0.55), Slot("text", 0.48, 0.35),
         Slot("text",  0.48, 0.35), Slot("gold", 1.00, 0.10)],
        notes="Wide image top; budget cards below; AP-4 canonical fix",
    ),
    # ── 4: Image-grid top (N images side-by-side) — AP-2 canonical fix ───────
    Template(
        "image-grid", "\\budgetwidecontent (tabular)",
        [Slot("image", 0.31, 0.48), Slot("image", 0.31, 0.48),
         Slot("image", 0.31, 0.48),
         Slot("text",  0.48, 0.35), Slot("text", 0.48, 0.35)],
        notes="3+ side-by-side images on top row; AP-2 canonical fix",
    ),
    # ── 5: Full-bleed single image with caption ───────────────────────────────
    Template(
        "full-bleed", "\\autoimg + caption",
        [Slot("image", 1.00, 0.82), Slot("gold", 1.00, 0.10)],
        notes="Single dominant image; minimal text; demo/result slides",
    ),
    # ── 6: Equation + cards (eqbox left, bluecard right) — AP-1 context ──────
    Template(
        "equation-cards", "\\begin{eqbox} + \\begin{columns}",
        [Slot("eq",   0.54, 0.55), Slot("text", 0.44, 0.55),
         Slot("gold", 1.00, 0.12)],
        notes="LHS eqbox with \\scaleeq; RHS one or two bluecards; AP-1 fix",
    ),
    # ── 7: Three-column cards (tables, ablation) ──────────────────────────────
    Template(
        "three-col-cards", "\\begin{columns} × 3",
        [Slot("text", 0.31, 0.70), Slot("text", 0.31, 0.70),
         Slot("text", 0.31, 0.70), Slot("gold", 1.00, 0.12)],
        notes="3 equal-width cards; ablation / method comparison",
    ),
]


# ─────────────────────────────────────────────────────────────────────────────
# Scoring  (adapted from LayoutDM: utilization + alignment + overlap)
# ─────────────────────────────────────────────────────────────────────────────

def _score_feasibility(t: Template, s: SlideSpec) -> float:
    """Hard-constraint multiplier: 0.0 means completely wrong template."""
    has_img_slot  = bool(t.image_slots())
    has_text_slot = bool(t.text_slots())

    # Images present but no image slot
    if s.n_img > 0 and not has_img_slot:
        return 0.0
    # No images but template has image slot (wastes space)
    if s.n_img == 0 and has_img_slot:
        return 0.3
    # image-grid is designed for 2+ images
    if t.name == "image-grid" and s.n_img < 2:
        return 0.1
    # Multiple images but template only has one image slot
    if s.n_img > 1 and t.name not in ("image-grid",):
        return 0.15 if t.name in ("image-top",) else 0.0
    # Equations prefer equation-cards (eqbox env) over plain text-only
    if s.equation:
        if t.name == "equation-cards": return 1.0
        if t.name == "text-only":      return 0.8   # works but no dedicated eqbox
        return 0.5
    # goldcall needs a full-width slot (AP-3)
    if s.has_gold and t.name in ("image-left", "image-right"):
        return 0.45   # goldcall squeezed in column (AP-3 anti-pattern)
    return 1.0


def _score_image_fit(t: Template, s: SlideSpec) -> float:
    """
    LayoutDM-style AR alignment: exp(-|log(img_ar / slot_ar)|).
    Perfect fit → 1.0; 2× AR mismatch → ~0.5.
    """
    img_slots = t.image_slots()
    if not img_slots or not s.images:
        return 1.0

    if t.name == "image-grid":
        # Each image goes into a sub-slot (~1/3 wide)
        sub_ar = (0.31 * TEXTWIDTH_PT) / (0.48 * TEXTHEIGHT_PT)
        return sum(
            math.exp(-abs(math.log(max(img.ar, 0.1) / max(sub_ar, 0.1))))
            for img in s.images
        ) / len(s.images)

    slot_ar = img_slots[0].ar
    return math.exp(-abs(math.log(max(s.avg_img_ar, 0.1) / max(slot_ar, 0.1))))


def _score_text_density(t: Template, s: SlideSpec) -> float:
    """
    LayoutDM utilization for the text region.
    Gaussian centered at density=0.72 (filling ~72% of text slot).
    Steep cliff at density>1.05 (overflow risk).
    """
    text_slots = t.text_slots()
    if not text_slots:
        # Has cards but no text slot → guaranteed overflow
        return 0.0 if s.text_lines > 0 else 0.5
    avail_pt   = sum(sl.height * TEXTHEIGHT_PT for sl in text_slots)
    line_budget = avail_pt / LINE_HEIGHT_PT
    density = s.text_lines / max(line_budget, 1)

    if density > 1.05:                                  # overflow
        return max(0.0, 1.0 - (density - 1.0) * 6)
    if density < 0.30:                                  # too sparse
        return 0.25 + density
    return math.exp(-0.5 * ((density - 0.72) / 0.18) ** 2)


def _score_utilization(t: Template, s: SlideSpec) -> float:
    """
    Penalise unused slots: if template has image slot but slide has none.
    Also reward compact layouts that don't have excess empty area.
    """
    canvas = 1.0   # normalised to 1
    used   = sum(sl.area for sl in t.slots if (
        (sl.kind == "image" and s.n_img > 0) or
        (sl.kind in ("text","eq") and s.text_lines > 0) or
        (sl.kind == "gold"  and s.has_gold)
    ))
    ratio = used / canvas
    # Ideal utilisation 0.65-0.85 (not too sparse, not over-packed)
    return math.exp(-0.5 * ((ratio - 0.75) / 0.18) ** 2)


def _score_goldcall(t: Template, s: SlideSpec) -> float:
    """AP-3 rule: goldcall should span full width (slot.width == 1.0)."""
    if not s.has_gold:
        return 1.0
    gslot = t.gold_slot()
    if gslot and gslot.width >= 0.95:
        return 1.0
    return 0.5   # goldcall would be inside a column


def score(t: Template, s: SlideSpec) -> dict:
    """Multi-criterion score, weights tuned to RUITE-style refinement."""
    weights = dict(feasibility=0.40, image_fit=0.22,
                   text_density=0.18, utilization=0.12, goldcall=0.08)
    raw = dict(
        feasibility  = _score_feasibility(t, s),
        image_fit    = _score_image_fit(t, s),
        text_density = _score_text_density(t, s),
        utilization  = _score_utilization(t, s),
        goldcall     = _score_goldcall(t, s),
    )
    total = sum(weights[k] * raw[k] for k in weights)
    return {"template": t.name, "total": round(total, 3),
            "breakdown": {k: round(v, 3) for k, v in raw.items()}}


def rank(s: SlideSpec) -> list[dict]:
    results = [score(t, s) for t in TEMPLATES]
    return sorted(results, key=lambda x: -x["total"])


# ─────────────────────────────────────────────────────────────────────────────
# Layer 1 — Template decision tree
# ─────────────────────────────────────────────────────────────────────────────

def decide_template(s: SlideSpec) -> "tuple[str, str]":
    """
    Layer 1: Template selection via decision tree.

    Returns (template_name, reason_string).

    Design principle: template selection is a DECISION, not an optimisation.
    Choose the one correct template first; then verify constraints (layers 2-4).
    Scoring in rank() is secondary validation to catch edge-case conflicts.
    """
    if s.n_img == 0:
        if s.equation:
            return ("equation-cards",
                    "has equation \u2192 eqbox slot (left 0.54tw / card right 0.44tw)")
        if s.n_card >= 3:
            return ("three-col-cards",
                    f"\u22653 cards, no image \u2192 three equal columns (0.31tw each)")
        return ("text-only",
                "no image \u2192 two-column cards + optional goldcall")

    if s.n_img >= 2:
        return ("image-grid",
                f"{s.n_img} images \u2192 full-width grid (\\budgetwidecontent)")

    # Single image — AR is the primary decision variable
    ar = s.avg_img_ar
    if ar > 1.6:
        return ("image-top",
                f"AR={ar:.2f} > 1.6 (panoramic) \u2192 \\budgetwideimg; "
                f"side layout leaves 40-50% dead vertical space")
    if ar > 1.4:
        return ("image-top",
                f"AR={ar:.2f} \u2208 (1.4, 1.6] \u2192 \\budgetwideimg preferred; "
                f"natural image height < box height in 0.44tw column")
    # AR \u2264 1.4: square / portrait — side layout viable
    if s.n_card > 2 or s.has_gold:
        return ("image-top",
                f"AR={ar:.2f} \u2264 1.4 but {s.n_card} cards"
                + ("+gold" if s.has_gold else "")
                + " \u2192 TOP layout prevents column overcrowding (AP-5)")
    return ("image-left",
            f"AR={ar:.2f} \u2264 1.4 ({s.images[0].orientation}) and \u22642 cards "
            f"\u2192 SIDE layout balanced")


# ─────────────────────────────────────────────────────────────────────────────
# Layer 2 — Element constraints
# ─────────────────────────────────────────────────────────────────────────────

def _element_constraints(template_name: str, s: SlideSpec) -> "list[str]":
    """
    Layer 2: Geometric constraints for the chosen template.
    Returns informational notes (not pass/fail).
    """
    notes = []
    ar = s.avg_img_ar

    if template_name == "image-top":
        # \budgetwideimg sizes image automatically: img_h = textheight − box_h − overhead
        n_cards = max(s.n_card, 1)
        est_box_h_pt = n_cards * 4 * LINE_HEIGHT_PT + (18 if s.has_gold else 0)
        est_img_h_pt = TEXTHEIGHT_PT - est_box_h_pt - HEADER_OVERHEAD_PT
        nat_img_h_pt = TEXTWIDTH_PT / ar  # natural height at full width
        scale = est_img_h_pt / nat_img_h_pt if nat_img_h_pt > 0 else 1.0
        status = "\u2713" if 0.30 <= scale <= 1.10 else "\u26a0"
        notes.append(
            f"  {status} Image: auto-sized by \\budgetwideimg "
            f"\u2192 est. h\u2248{est_img_h_pt:.0f}pt / {est_img_h_pt/TEXTHEIGHT_PT:.0%} textheight "
            f"(nat. at full-width={nat_img_h_pt:.0f}pt, scale\u2248{scale:.2f}\u00d7)")
        if scale > 1.0:
            notes.append(
                f"    \u26a0  Bottom block too tall ({est_box_h_pt:.0f}pt) — "
                f"image will appear tiny; reduce cards or line count")

    elif template_name in ("image-left", "image-right"):
        col_w_pt    = 0.44 * TEXTWIDTH_PT
        nat_h_pt    = col_w_pt / ar
        est_box_h_pt = s.n_card * 4 * LINE_HEIGHT_PT
        denom       = max(nat_h_pt, est_box_h_pt)
        balance     = 1.0 - abs(nat_h_pt - est_box_h_pt) / denom if denom else 1.0
        status      = "\u2713" if balance >= 0.65 else "\u26a0"
        taller      = "image" if nat_h_pt > est_box_h_pt else "text"
        notes.append(
            f"  {status} Col balance: img h\u2248{nat_h_pt:.0f}pt  box h\u2248{est_box_h_pt:.0f}pt "
            f" B\u2248{balance:.2f} ({taller} taller)")
        if balance < 0.65:
            notes.append(
                "    \u26a0  B < 0.65 — add/remove body lines, or switch to TOP layout")

    elif template_name == "equation-cards":
        notes.append("  \u2139 eqbox slot 0.54tw: use \\scaleeq for wide equations")

    elif template_name == "three-col-cards":
        notes.append("  \u2139 3 cols @ 0.31tw: \\footnotesize, \u22644 items/column")

    return notes


# ─────────────────────────────────────────────────────────────────────────────
# Layer 3 — Content density check
# ─────────────────────────────────────────────────────────────────────────────

def _density_check(template_name: str, s: SlideSpec) -> "list[str]":
    """
    Layer 3: Check if content density is appropriate for the chosen template.
    Target text_density \u2208 [0.60, 0.85].
    """
    tmpl = next((t for t in TEMPLATES if t.name == template_name), None)
    if tmpl is None:
        return [f"  Unknown template {template_name!r}"]

    notes = []
    text_slots = tmpl.text_slots()
    if text_slots and s.text_lines > 0:
        avail_pt    = sum(sl.height * TEXTHEIGHT_PT for sl in text_slots)
        line_budget = avail_pt / LINE_HEIGHT_PT
        density     = s.text_lines / max(line_budget, 1)
        if density > 1.0:
            notes.append(
                f"  \u2717 OVERFLOW  text_density={density:.2f}  ({s.text_lines} lines "
                f"> {line_budget:.0f} line budget) \u2192 remove content or wider template")
        elif density > 0.90:
            notes.append(
                f"  \u26a0 TIGHT     text_density={density:.2f}  \u2192 reduce by 1\u20132 lines")
        elif density < 0.45:
            notes.append(
                f"  \u26a0 SPARSE    text_density={density:.2f}  \u2192 add content or narrower template")
        else:
            notes.append(
                f"  \u2713 text density={density:.2f}  (target 0.60\u20130.85)")
    else:
        notes.append("  \u2139 (no text slots to check)")

    if s.images and tmpl.image_slots():
        slot_ar   = tmpl.image_slots()[0].ar
        ar_match  = math.exp(-abs(math.log(max(s.avg_img_ar, 0.1) / max(slot_ar, 0.1))))
        if ar_match < 0.60:
            notes.append(
                f"  \u26a0 Image AR mismatch  img={s.avg_img_ar:.2f}  slot\u2248{slot_ar:.2f}  "
                f"match={ar_match:.2f}  \u2192 letterboxing / pillarboxing likely")
        else:
            notes.append(
                f"  \u2713 image AR match={ar_match:.2f}  (img={s.avg_img_ar:.2f})")

    return notes


# ─────────────────────────────────────────────────────────────────────────────
# Layer 4 — Design grammar rules
# ─────────────────────────────────────────────────────────────────────────────

def _grammar_check(template_name: str, s: SlideSpec) -> "list[str]":
    """
    Layer 4: Hard design-grammar rules.
    Returns list of violation strings (empty list = all clear).
    """
    violations = []

    # GV-2: goldcall must span full width (AP-3)
    if s.has_gold and template_name in ("image-left", "image-right"):
        violations.append(
            "GV-2  goldcall would be inside a side column (AP-3) "
            "\u2192 place goldcall BELOW \\end{columns}")

    # GV-3: \u22641 bluecard per column (AP-5)
    if s.n_card > 2 and template_name in ("image-left", "image-right"):
        violations.append(
            f"GV-3  {s.n_card} bluecards in one column (AP-5 equal-height impossible) "
            f"\u2192 use image-top to spread cards across full width")

    # GV-4: wide image must use TOP layout (AP-4)
    if (s.n_img == 1 and s.avg_img_ar > 1.5
            and template_name in ("image-left", "image-right")):
        violations.append(
            f"GV-4  AR={s.avg_img_ar:.2f} > 1.5 in SIDE layout (AP-4) "
            f"\u2192 image shrinks to narrow column; use \\budgetwideimg")

    return violations


# ─────────────────────────────────────────────────────────────────────────────
# LaTeX skeleton generation
# ─────────────────────────────────────────────────────────────────────────────

_CARD_ITEMS = r"""          \begin{itemize}\setlength\itemsep{2pt}
            \item ...
          \end{itemize}"""


def _two_bluecards(n: int = 2) -> str:
    cols = "\n".join(
        f"      \\begin{{column}}{{0.{48 if n==2 else 31}\\textwidth}}\n"
        f"        \\begin{{bluecard}}{{Card {i+1}}}\n"
        f"          \\footnotesize\n{_CARD_ITEMS}\n"
        f"        \\end{{bluecard}}\n"
        f"      \\end{{column}}"
        for i in range(n)
    )
    return (
        "  \\begin{columns}[T,onlytextwidth]\n"
        + cols + "\n"
        + "  \\end{columns}"
    )


def _goldcall_block() -> str:
    return (
        "  \\vspace{0.3em}\n"
        "  \\begin{goldcall}\n"
        "    \\centering\\small ...\n"
        "  \\end{goldcall}"
    )


def generate_skeleton(template_name: str, s: SlideSpec) -> str:
    imgs  = s.images or [Img()]
    n_img = len(imgs)
    frame_opts = ""

    if template_name == "text-only":
        body = _two_bluecards(s.n_card or 2)
        if s.has_gold:
            body += "\n" + _goldcall_block()

    elif template_name in ("image-left", "image-right"):
        img_col  = f"    \\autoimg{{{imgs[0].name}}}"
        text_col = (
            "    \\begin{bluecard}{Cards}\n"
            "      \\footnotesize\n"
            f"{_CARD_ITEMS}\n"
            "    \\end{bluecard}"
        )
        if template_name == "image-left":
            left, right = img_col, text_col
            lw, rw = "0.44", "0.52"
        else:
            left, right = text_col, img_col
            lw, rw = "0.52", "0.44"
        body = (
            "  \\begin{columns}[c]\n"
            f"    \\begin{{column}}{{{lw}\\textwidth}}\n{left}\n    \\end{{column}}\n"
            f"    \\begin{{column}}{{{rw}\\textwidth}}\n{right}\n    \\end{{column}}\n"
            "  \\end{columns}"
        )
        if s.has_gold:
            body += "\n" + _goldcall_block()

    elif template_name == "image-top":
        bottom = _two_bluecards(s.n_card or 2)
        if s.has_gold:
            bottom += "\n" + _goldcall_block()
        body = (
            f"  \\budgetwideimg{{}}{{%\n"
            f"    % AP-4: \\budgetwideimg measures bottom block, sizes image automatically\n"
            + bottom.replace("\n", "\n    ")
            + f"\n  }}{{{imgs[0].name}}}"
        )

    elif template_name == "image-grid":
        img_entries = "".join(
            f"      \\adjincludegraphics[max width=0.31\\textwidth,%%\n"
            f"        max height=\\dimexpr\\bbiAvailHt-1.8em\\relax]{{{img.name}}}"
            + (" &\n" if i < n_img - 1 else " \\\\\n")
            for i, img in enumerate(imgs[:3])
        )
        label_row = " & ".join(f"\\small\\textbf{{Fig {i+1}}}" for i in range(min(n_img, 3)))
        tabular = (
            "    \\begin{tabular}{@{}c@{\\hspace{6pt}}c@{\\hspace{6pt}}c@{}}\n"
            + img_entries
            + f"      {label_row}\\\\\n"
            + "    \\end{tabular}%"
        )
        bottom = _two_bluecards(s.n_card or 2)
        body = (
            "  \\budgetwidecontent{%\n"
            f"  % AP-2: \\budgetwidecontent with full-width image grid\n"
            + tabular + "\n"
            + "  }{Caption text}{%\n"
            + bottom + "\n"
            + "  }"
        )

    elif template_name == "full-bleed":
        body = (
            f"  \\centering\n"
            f"  \\adjincludegraphics[max width=\\textwidth,"
            f"max height=0.82\\textheight]{{{imgs[0].name}}}\n"
        )
        if s.has_gold:
            body += _goldcall_block()

    elif template_name == "equation-cards":
        body = (
            "  \\begin{columns}[T]\n"
            "    \\begin{column}{0.54\\textwidth}\n"
            "      \\begin{eqbox}{Equation Title}\n"
            "        % AP-1: use \\scaleeq for long equations\n"
            "        \\scaleeq{f(x) = \\int_{-\\infty}^{+\\infty} \\hat{f}(\\xi)\\,e^{2\\pi i\\xi x}\\,d\\xi}\n"
            "      \\end{eqbox}\n"
            "    \\end{column}\n"
            "    \\begin{column}{0.44\\textwidth}\n"
            "      \\begin{bluecard}{Key Properties}\n"
            f"{_CARD_ITEMS}\n"
            "      \\end{bluecard}\n"
            "    \\end{column}\n"
            "  \\end{columns}"
        )
        if s.has_gold:
            body += "\n" + _goldcall_block()

    elif template_name == "three-col-cards":
        body = (
            "  \\begin{columns}[T]\n"
            + "".join(
                f"    \\begin{{column}}{{0.31\\textwidth}}\n"
                f"      \\begin{{bluecard}}{{Card {i+1}}}\n"
                f"        \\footnotesize\n{_CARD_ITEMS}\n"
                f"      \\end{{bluecard}}\n"
                f"    \\end{{column}}\n"
                for i in range(3)
            )
            + "  \\end{columns}"
        )
        if s.has_gold:
            body += "\n" + _goldcall_block()

    else:
        body = "  % TODO: fill layout"

    title = s.title or "Frame Title"
    return (
        f"\\begin{{frame}}{frame_opts}{{{title}}}\n"
        + body + "\n"
        + "\\end{frame}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Iterative build loop  (run xelatex, detect Overfull \vbox, re-pick template)
# ─────────────────────────────────────────────────────────────────────────────

def detect_overflows(log_path: Path) -> list[str]:
    """Parse xelatex log for Overfull \\vbox entries."""
    if not log_path.exists():
        return []
    pattern = re.compile(r"Overfull \\vbox \((\d+(?:\.\d+)?)pt too high\)")
    return pattern.findall(log_path.read_text(errors="replace"))


def iterate_build(tex_file: str, max_passes: int = 3) -> None:
    """
    Iterative improvement loop (RUITE-style feedback):
      1. Run xelatex
      2. Parse log for Overfull \\vbox
      3. Print overflow locations so the user can re-pick template
    This loop does NOT auto-patch the .tex; it reports + suggests.
    """
    tex = Path(tex_file)
    log = tex.parent / "build" / (tex.stem + ".log")

    for pass_n in range(1, max_passes + 1):
        print(f"\n{'='*60}")
        print(f"Pass {pass_n}: compiling {tex.name} ...")
        result = subprocess.run(
            ["xelatex", "-output-directory=build",
             "-interaction=nonstopmode", str(tex)],
            capture_output=True, text=True
        )
        overflows = detect_overflows(log)
        if not overflows:
            print("✓ No Overfull \\vbox detected. Build clean.")
            break
        print(f"⚠ {len(overflows)} overflow(s) detected:")
        for ov in overflows:
            print(f"    {ov} pt too high")
        print("→ Run `python layout_optimizer.py suggest` with your slide's")
        print("  content spec to get a less dense template, then re-edit.")
        if pass_n == max_passes:
            print("Max passes reached. Manual intervention needed.")


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def parse_spec(args) -> SlideSpec:
    images = []
    for img_str in (args.img or []):
        if ":" in img_str:
            parts = img_str.split(":")
            w, h  = int(parts[0]), int(parts[1])
            name  = parts[2] if len(parts) > 2 else "figure.png"
        else:
            w, h, name = 1280, 720, img_str
        images.append(Img(name=name, w=w, h=h))

    cards = [Card(kind="blue", lines=args.lines) for _ in range(args.cards)]
    if args.gold:
        cards.append(Card(kind="gold", lines=2))

    return SlideSpec(
        title=args.title or "Frame Title",
        images=images,
        cards=cards,
        equation=args.eq,
    )


def cmd_rank(args):
    s = parse_spec(args)
    dt_name, dt_reason = decide_template(s)
    results = rank(s)
    dt_rank  = next((i + 1 for i, r in enumerate(results)
                     if r["template"] == dt_name), None)

    print(f"\nSlide spec: {s.n_img} image(s)  {s.n_card} card(s)  "
          f"~{s.text_lines} lines  gold={s.has_gold}  eq={s.equation}")
    print(f"avg image AR={s.avg_img_ar:.2f}  "
          f"(>1.6=wide | 0.85-1.6=square | <0.85=tall)")
    print()
    print(f"\u2605 Layer 1 decision: {dt_name}  ({dt_reason})")
    print()
    print(f"{'Rank':<5} {'Template':<20} {'Score':>6}  DT  Breakdown")
    print("-" * 80)
    for i, r in enumerate(results):
        bd   = "  ".join(f"{k}={v:.2f}" for k, v in r["breakdown"].items())
        flag = "\u2605" if r["template"] == dt_name else " "
        print(f"  {i+1:<4} {r['template']:<20} {r['total']:>6.3f}  {flag}   {bd}")
    print()
    if dt_rank and dt_rank > 1:
        print(f"  Note: DT decision '{dt_name}' scored #{dt_rank} by scorer "
              f"(scorer uses flat weights; DT uses content-type rules)")


def cmd_suggest(args):
    s = parse_spec(args)

    # ── Layer 1: Template Decision (← primary selection) ──────────────────────
    dt_name, dt_reason = decide_template(s)
    tmpl = next((t for t in TEMPLATES if t.name == dt_name), None)
    results = rank(s)
    scorer_name = results[0]["template"]
    scorer_score = results[0]["total"]

    print(f"\n{'='*60}")
    print(f"  Slide spec: {s.n_img} img  {s.n_card} card  "
          f"{s.text_lines} lines  gold={s.has_gold}  eq={s.equation}  "
          f"AR={s.avg_img_ar:.2f}")
    print(f"{'='*60}")

    print(f"\n\u2500\u2500 Layer 1: Template Decision \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500")
    print(f"  \u2605 Decision tree : {dt_name}")
    print(f"    Reason       : {dt_reason}")
    print(f"    Macro        : {tmpl.macro if tmpl else '?'}")
    if scorer_name != dt_name:
        dt_score = next((r["total"] for r in results if r["template"] == dt_name), 0)
        print(f"    Scorer top-1 : {scorer_name} (score={scorer_score:.3f})  "
              f"vs DT choice {dt_name} (score={dt_score:.3f})")
        print(f"    \u2192 DT choice takes precedence (scorer uses flat weights)")

    print(f"\n\u2500\u2500 Layer 2: Element Constraints \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500")
    for note in _element_constraints(dt_name, s):
        print(note)

    print(f"\n\u2500\u2500 Layer 3: Content Density \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500")
    for note in _density_check(dt_name, s):
        print(note)

    print(f"\n\u2500\u2500 Layer 4: Grammar Rules \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500")
    violations = _grammar_check(dt_name, s)
    if violations:
        for v in violations:
            print(f"  \u2717 {v}")
    else:
        print("  \u2713 No grammar violations")

    print(f"\n\u2500\u2500 LaTeX Skeleton \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500")
    print(generate_skeleton(dt_name, s))
    print("\u2500" * 60)


def cmd_iterate(args):
    iterate_build(args.tex or "cvgdiff-beamer.tex")


# ─────────────────────────────────────────────────────────────────────────────
# .tex parser — extract frames → SlideSpec
# ─────────────────────────────────────────────────────────────────────────────

def _read_img_ar(fname: str, tex_dir: Path) -> float | None:
    """Return W/H of an image file, searching standard asset dirs."""
    search = [
        tex_dir,
        tex_dir / "cvgdiff_extracted" / "cvgdiff_slides_pack" / "slides_assets",
        tex_dir.parent,
    ]
    for d in search:
        p = (d / fname).resolve()
        if not p.exists():
            continue
        try:
            import struct
            with open(p, "rb") as f:
                header = f.read(24)
            # PNG: magic(8) | chunk_len(4) | "IHDR"(4) | width(4) | height(4)
            if header[:8] == b"\x89PNG\r\n\x1a\n":
                if len(header) >= 24:
                    w = struct.unpack(">I", header[16:20])[0]
                    h = struct.unpack(">I", header[20:24])[0]
                    return w / h if h else None
            # JPEG: scan SOF markers
            if header[:2] == b"\xff\xd8":
                with open(p, "rb") as f:
                    data = f.read(65536)
                i = 2
                while i + 4 < len(data):
                    if data[i] != 0xFF:
                        break
                    mk = data[i + 1]
                    if mk in (0xC0, 0xC1, 0xC2, 0xC3) and i + 9 <= len(data):
                        h = struct.unpack(">H", data[i + 5:i + 7])[0]
                        w = struct.unpack(">H", data[i + 7:i + 9])[0]
                        return w / h if h else None
                    if mk in (0xD8, 0xD9) or (0xD0 <= mk <= 0xD7):
                        i += 2
                    else:
                        seg = struct.unpack(">H", data[i + 2:i + 4])[0]
                        i += 2 + seg
        except Exception:
            pass
    return None


def _spec_from_body(title: str, body: str, tex_dir: Path) -> SlideSpec:
    """
    Build a SlideSpec by statically parsing a frame body.

    Detection heuristics (conservative — false negatives are fine):
      Images   : any {filename.ext} where ext is png/jpg/jpeg
      bluecards: \\begin{bluecard}
      goldcalls: \\begin{goldcall}
      eqboxes  : \\begin{eqbox} or \\begin{align} or \\[...\\] or \\begin{equation}
      lines    : \\item lines (×1) + non-blank non-command lines inside boxes
    """
    # ── images ──────────────────────────────────────────────────────────────
    img_names = re.findall(r"\{([^}]+\.(?:png|jpg|jpeg))\}", body, re.IGNORECASE)
    seen: set = set()
    images = []
    for fn in img_names:
        fn = fn.strip()
        if fn in seen:
            continue
        seen.add(fn)
        ar = _read_img_ar(fn, tex_dir)
        w, h = (int(ar * 100), 100) if ar else (1280, 720)
        images.append(Img(name=fn, w=w, h=h))

    # ── cards ────────────────────────────────────────────────────────────────
    cards: list[Card] = []
    for m in re.finditer(
            r"\\begin\{bluecard\}[^{]*\{[^}]*\}(.*?)\\end\{bluecard\}",
            body, re.DOTALL):
        cbody = m.group(1)
        lines = len(re.findall(r"\\item", cbody)) + \
                sum(1 for ln in cbody.split("\n")
                    if ln.strip() and not ln.strip().startswith("%")
                    and re.search(r"[a-zA-Z\u4e00-\u9fff]", ln)
                    and r"\item" not in ln and r"\begin" not in ln)
        cards.append(Card(kind="blue", lines=max(lines, 2)))

    for m in re.finditer(
            r"\\begin\{goldcall\}(.*?)\\end\{goldcall\}", body, re.DOTALL):
        lines = max(1, len(re.findall(r"\\\\", m.group(1))) + 1)
        cards.append(Card(kind="gold", lines=lines))

    for m in re.finditer(
            r"\\begin\{eqbox\}[^{]*\{[^}]*\}(.*?)\\end\{eqbox\}", body, re.DOTALL):
        cards.append(Card(kind="eqbox", lines=3))

    # ── equation flag ────────────────────────────────────────────────────────
    has_eq = bool(
        re.search(r"\\begin\{(?:align\*?|equation\*?)\}", body) or
        re.search(r"(?<!\\)\\\[", body) or
        re.search(r"\\begin\{eqbox\}", body)
    )

    return SlideSpec(title=title, images=images, cards=cards, equation=has_eq)


def _detect_current_layout(body: str) -> str:
    """Heuristic: what macro/structure is this frame actually using?"""
    if r"\budgetwideimg"   in body: return "\\budgetwideimg (image-top)"
    if r"\budgetwidecontent" in body: return "\\budgetwidecontent (image-grid)"
    if r"\autoimg"         in body and r"\begin{columns}" not in body:
        return "\\autoimg full-bleed"
    if r"\begin{columns}"  in body and re.search(
            r"\{[0-9.]+\\textwidth\}\s*\\adjincludegraphics|\{[0-9.]+\\textwidth\}\s*\\autoimg",
            body):
        # columns with an image inside — side layout
        col_fracs = re.findall(r"\\begin\{column\}\{([0-9.]+)\\textwidth\}", body)
        if col_fracs:
            return f"\\begin{{columns}} SIDE (cols: {', '.join(col_fracs)}tw)"
        return "\\begin{columns} SIDE"
    if r"\begin{columns}"  in body and r"\begin{eqbox}" in body:
        return "\\begin{eqbox} equation-cards in columns"
    if r"\begin{columns}"  in body: return "\\begin{columns} text-only"
    if r"\begin{eqbox}"    in body: return "\\begin{eqbox} equation-cards"
    if r"\adjincludegraphics" in body or r"\includegraphics" in body:
        return "inline image (no macro)"
    return "text-only"


def cmd_parse(args):
    """
    Parse every frame in a .tex file and run all 4 design layers.

    For each frame prints:
      - Current layout (detected)  vs  DT recommendation
      - Layer 1: template decision + reason
      - Layer 2: element constraints
      - Layer 3: content density
      - Layer 4: grammar violations
    """
    tex_path = Path(args.tex)
    if not tex_path.exists():
        print(f"Error: {tex_path} not found", file=sys.stderr)
        sys.exit(1)

    src = tex_path.read_text(encoding="utf-8", errors="replace")
    tex_dir = tex_path.parent

    # Extract frame bodies (strip comments first to simplify regex)
    src_nc = re.sub(r"(?m)^\s*%.*$", "", src)   # strip full-line comments
    src_nc = re.sub(r"(?<!\\)%[^\n]*", "", src_nc)   # strip inline comments

    frames = list(re.finditer(
        r"\\begin\{frame\}(?:\[[^\]]*\])?\{([^}]*)\}(.*?)\\end\{frame\}",
        src_nc, re.DOTALL))

    if not frames:
        print("No \\begin{frame}{title}...\\end{frame} found.", file=sys.stderr)
        sys.exit(1)

    # ── summary accumulators ─────────────────────────────────────────────────
    mismatch_frames: list[str] = []
    violation_frames: list[str] = []

    print(f"\n{'═'*72}")
    print(f"  layout_optimizer  parse  ·  {tex_path.name}  ·  {len(frames)} frames")
    print(f"{'═'*72}")

    for idx, m in enumerate(frames, start=1):
        title = m.group(1).strip()
        body  = m.group(2)

        spec     = _spec_from_body(title, body, tex_dir)
        dt_name, dt_reason = decide_template(spec)
        current  = _detect_current_layout(body)

        # compact title (truncate CJK-heavy titles)
        short_title = title[:46] + ("…" if len(title) > 46 else "")

        # ── mismatch detection ────────────────────────────────────────────────
        dt_keyword  = dt_name.replace("image-top",  "budgetwideimg") \
                              .replace("image-left", "columns") \
                              .replace("image-right","columns") \
                              .replace("text-only",  "columns") \
                              .replace("image-grid", "budgetwidecontent") \
                              .replace("full-bleed", "autoimg") \
                              .replace("equation-cards", "eqbox") \
                              .replace("three-col-cards","columns")
        mismatch = dt_keyword not in current.lower().replace("\\", "").replace("{","").replace("}","")

        # ── grammar violations (layer 4) ──────────────────────────────────────
        violations = _grammar_check(dt_name, spec)

        flag = ""
        if violations: flag += " ⚠DGV"
        if mismatch:   flag += " ↔MISMATCH"

        print(f"\n  [{idx:>2}] {short_title}{flag}")
        print(f"        Current layout : {current}")
        print(f"        DT recommends  : {dt_name}  ({'matches' if not mismatch else 'DIFFERENT'})")

        if args.verbose or mismatch or violations:
            # Layer 1
            print(f"\n        ── Layer 1: Template Decision")
            print(f"             {dt_reason}")

            # Layer 2
            l2 = _element_constraints(dt_name, spec)
            if l2:
                print(f"        ── Layer 2: Constraints")
                for n in l2: print(f"        {n}")

            # Layer 3
            l3 = _density_check(dt_name, spec)
            if l3:
                print(f"        ── Layer 3: Density")
                for n in l3: print(f"        {n}")

            # Layer 4
            print(f"        ── Layer 4: Grammar")
            if violations:
                for v in violations: print(f"          ✗ {v}")
            else:
                print(f"          ✓ No violations")

        if mismatch:
            mismatch_frames.append(f"[{idx}] {short_title}")
        if violations:
            violation_frames.append(f"[{idx}] {short_title}  ({', '.join(c for c,_ in [(v.split()[0],v) for v in violations])})")

    # ── summary ───────────────────────────────────────────────────────────────
    print(f"\n{'═'*72}")
    print(f"  SUMMARY")
    print(f"{'═'*72}")
    print(f"  Total frames    : {len(frames)}")
    print(f"  DT mismatches   : {len(mismatch_frames)}")
    for f in mismatch_frames:  print(f"    {f}")
    print(f"  DGV violations  : {len(violation_frames)}")
    for f in violation_frames: print(f"    {f}")
    if not mismatch_frames and not violation_frames:
        print("  ✓ All frames match DT recommendation, no grammar violations.")
    print()


def main():
    p = argparse.ArgumentParser(
        description="Beamer slide layout optimizer — layered design: decide \u2192 constrain \u2192 density \u2192 grammar")
    sub = p.add_subparsers(dest="cmd", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--img",   action="append", metavar="W:H[:name]",
                        help="Image spec, e.g. 1280:720:fig.png  (repeat for multiple images)")
    common.add_argument("--cards", type=int, default=2,
                        help="Number of bluecard elements (default: 2)")
    common.add_argument("--lines", type=int, default=5,
                        help="Estimated lines per card (default: 5)")
    common.add_argument("--eq",   action="store_true", help="Has display equation")
    common.add_argument("--gold", action="store_true", help="Has goldcall summary box")
    common.add_argument("--title", default="", help="Slide title (for skeleton output)")

    rank_p = sub.add_parser("rank",    parents=[common], help="Show ranked templates")
    rank_p.set_defaults(func=cmd_rank)

    sugg_p = sub.add_parser("suggest", parents=[common], help="Show best template + LaTeX skeleton")
    sugg_p.set_defaults(func=cmd_suggest)

    iter_p = sub.add_parser("iterate", help="Run xelatex build loop, detect overflows")
    iter_p.add_argument("--tex", default="cvgdiff-beamer.tex")
    iter_p.set_defaults(func=cmd_iterate)

    parse_p = sub.add_parser("parse", help="Parse .tex, run 4-layer analysis on every frame")
    parse_p.add_argument("tex", nargs="?", default="cvgdiff-beamer.tex",
                         help="Path to .tex file (default: cvgdiff-beamer.tex)")
    parse_p.add_argument("-v", "--verbose", action="store_true",
                         help="Show all 4 layers for every frame, not just mismatches")
    parse_p.set_defaults(func=cmd_parse)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
