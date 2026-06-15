#!/usr/bin/env python3
"""
concept_load.py — per-frame COGNITIVE-LOAD lower bound for a target reader profile.

Companion to autobeamer-calibrate. This is the MECHANICAL HALF of the cognitive-load
model (skills/autobeamer-calibrate/references/cognitive-load-model.md): it counts only
what is deterministically lexable from the .tex — new symbols (first-seen across frames),
inferential-jump candidates, back-references, and an abstraction proxy — and totals a
LOWER BOUND  L_mech  for the chosen profile. The NEW-CONCEPT term (w_c·Σ concept_cost) is
NOT countable from source; the model annotates concepts per frame and adds it to get the
full L. So every number here is a lower bound: "if even L_mech > L_max, the frame is
already OVERLOAD."  Numbers are reproducible (pure lexical/arithmetic); same input → same
output.

It is ORTHOGONAL to check_layout.py (visual density U/B/G). Do not merge them.

Frame and page regexes below are kept IDENTICAL to check_layout.py main() for parity.

Usage:
  python concept_load.py deck.tex --profile P1
  python concept_load.py deck.tex --profile P1 --gradient
  python concept_load.py deck.tex --profile P1 --json
"""
import sys, re, json, argparse
from pathlib import Path

# ── shared load-model weights (mirror profile-budgets.md) ────────────────────
W_S, W_J, W_R, W_A = 0.6, 1.5, 0.8, 1.0          # symbol, jump, back-ref, abstraction
COLLISION_SURCHARGE = 2.0

# ── per-profile scalars + primitive/collision symbol hints ───────────────────
# Mirrors profile-budgets.md + reader-profiles-prescriptive.md. Symbol sets are
# approximate; the model refines collisions/axes. L_max drives the OVERLOAD flag.
PROFILES = {
    "P1": {  # AI/ML engineer
        "name": "AI/ML engineer",
        "L_max": 8.0, "L_max_proof": 4.0,
        "primitive": {r"\nabla", r"\grad", "x", "y", "d", r"\partial", "f", "g"},
        "collide":   {r"\lambda", "T", "N", r"\mathcal{A}", "A"},  # λ/lr, T/transpose, N/dim, 𝒜/matrix
    },
    "P2": {  # STEM undergraduate
        "name": "STEM undergraduate",
        "L_max": 10.0, "L_max_proof": 7.0,
        "primitive": {r"\nabla", r"\grad", "x", "y", "z", "d", "f", "g", r"\partial", "A", "Z"},
        "collide":   set(),
    },
    "P3": {  # high-schooler — almost everything in math mode is costly
        "name": "high-school student",
        "L_max": 3.0, "L_max_proof": 3.0,
        "primitive": {"x", "y"},
        "collide":   {r"\nabla", r"\lambda", r"\sum", r"\mathcal{A}"},
    },
    "P4": {  # biomedical researcher
        "name": "biomedical researcher",
        "L_max": 6.0, "L_max_proof": 4.0,
        "primitive": {"x", "y", "p"},
        "collide":   {r"\lambda", r"\nabla"},
    },
    "P5": {  # humanities — any bare symbol is costly
        "name": "humanities reader",
        "L_max": 3.0, "L_max_proof": 3.0,
        "primitive": set(),
        "collide":   set(),
    },
    "P6": {  # cross-field grad
        "name": "cross-field graduate",
        "L_max": 11.0, "L_max_proof": 9.0,
        "primitive": {r"\nabla", "x", "y", "z", "d", "f", "g", "A", "Z", r"\partial", r"\lambda"},
        "collide":   set(),
    },
}

# inferential-jump trigger words (a step likely skipped on the slide)
JUMP_TRIGGERS = [
    r"\bthus\b", r"\bhence\b", r"\bclearly\b", r"\bobvious(?:ly)?\b", r"\bevidently\b",
    r"\bit follows\b", r"\bit can be shown\b", r"\bone verifies\b", r"\bwe verify\b",
    r"\btrivial(?:ly)?\b", r"\bof course\b",
    "可验证", "易证", "易见", "显然", "不难(?:看出|得到|证明)", "可证",
]
# back-reference markers (a result used but not recapped on-frame)
BACKREF_TRIGGERS = [r"\\ref\b", r"\\eqref\b", r"\\autoref\b", r"\\hyperlink\b",
                    r"\brecall\b", r"as shown", r"as we saw", "回顾", "如前", "前述", "之前(?:的)?"]
# abstraction-proxy markers, ascending
ABS_L2 = [r"\\forall", r"\\exists", r"\\sup", r"\\inf", r"\\max", r"\\min", r"\\lim"]
ABS_L3 = [r"\\mathcal", r"\\int", r"\\mu", r"\\nu", r"\\sigma", r"\\mathbb",
          "measure", "functional", "测度", "泛函"]

# math-symbol token: a backslash-macro (optionally \mathcal{X}) or a single letter
SYM_RE = re.compile(r"\\mathcal\{[A-Za-z]\}|\\[A-Za-z]+|(?<![A-Za-z\\])[A-Za-z](?![A-Za-z])")
MATH_RE = re.compile(r"\$[^$]*\$|\\\[(.*?)\\\]|\\\((.*?)\\\)", re.DOTALL)

# frame + page regexes — IDENTICAL to check_layout.py for parity
FRAME_RE = re.compile(r"\\begin\{frame\}(?:\[.*?\])?\{([^}]*)\}(.*?)\\end\{frame\}", re.DOTALL)
SLIDE_MACRO_RE = re.compile(
    r"\\TLtitle\w*|\\TLsection\b|\\section\b|\\maketitle\b|\\titlepage\b|\\begin\{frame\}")


def inline_inputs(tex: str, base: Path, depth: int = 0) -> str:
    """Minimal \\input/\\include inliner so decks split into section files work."""
    if depth > 8:
        return tex
    def repl(m):
        name = m.group(1).strip()
        for cand in (name, name + ".tex"):
            p = (base / cand)
            if p.exists():
                return inline_inputs(p.read_text(encoding="utf-8", errors="replace"), base, depth + 1)
        return ""  # unresolved input → drop (matches "validate a flattened copy" note)
    return re.sub(r"\\(?:input|include)\{([^}]+)\}", repl, tex)


def math_segments(body: str):
    for m in MATH_RE.finditer(body):
        yield m.group(0)


def symbols_in(body: str):
    out = []
    for seg in math_segments(body):
        out.extend(SYM_RE.findall(seg))
    return out


def count_any(patterns, text):
    return sum(len(re.findall(p, text)) for p in patterns)


def symbol_cost(sym, prof):
    if sym in prof["primitive"]:
        return 0.0
    base = 1.0
    if sym in prof["collide"]:
        base += COLLISION_SURCHARGE
    return base


def abstraction_proxy(body):
    if count_any(ABS_L3, body):
        return 3
    if count_any(ABS_L2, body):
        return 2
    # named object with subscript vs. bare number
    if re.search(r"_\{?[A-Za-z0-9]", body) or re.search(r"[A-Za-z]\(", body):
        return 1
    return 0


def is_proof_frame(title):
    return bool(re.search(r"证明|推导|proof|lemma|引理|定理|theorem", title, re.I))


def analyse(tex, profile):
    prof = PROFILES[profile]
    seen = {}          # symbol -> frame idx first introduced
    uses = {}          # symbol -> sorted list of frame indices where it appears
    frames = []

    # page mapping (parity with check_layout)
    page_of_start, _page = {}, 0
    for _m in SLIDE_MACRO_RE.finditer(tex):
        _page += 1
        page_of_start[_m.start()] = _page

    for i, m in enumerate(FRAME_RE.finditer(tex), start=1):
        title, body = m.group(1), m.group(2)
        syms = symbols_in(body)
        new_syms, sym_load = [], 0.0
        for s in syms:
            if s not in seen:
                seen[s] = i
                new_syms.append(s)
                sym_load += symbol_cost(s, prof)
            us = uses.setdefault(s, [])
            if not us or us[-1] != i:
                us.append(i)

        jumps   = count_any(JUMP_TRIGGERS, body)
        backref = count_any(BACKREF_TRIGGERS, body)
        absx    = abstraction_proxy(body)
        l_mech  = W_S * sym_load + W_J * jumps + W_R * backref + W_A * absx
        lmax    = prof["L_max_proof"] if is_proof_frame(title) else prof["L_max"]

        flag = "OK"
        if l_mech > lmax:
            flag = "OVERLOAD"            # lower bound alone already exceeds ceiling
        elif l_mech > 0.7 * lmax:
            flag = "TIGHT"

        frames.append({
            "idx": i, "page": page_of_start.get(m.start(), i),
            "title": title.strip()[:36],
            "new_sym": len(new_syms), "new_sym_list": new_syms,
            "sym_load": round(sym_load, 1), "jumps": jumps, "backref": backref,
            "abs": absx, "L_mech": round(l_mech, 1), "L_max": lmax,
            "is_proof": is_proof_frame(title), "flag": flag,
        })
    return frames, seen, uses


def gradient_report(frames, seen, uses):
    spikes, stale = [], []
    for a, b in zip(frames, frames[1:]):
        d = b["L_mech"] - a["L_mech"]
        if d >= 4.0:                    # coarse spike threshold on the mechanical lower bound
            spikes.append((a["idx"], b["idx"], round(d, 1), b["title"]))
    # stale: a symbol whose LARGEST gap between consecutive uses exceeds 6 frames
    # (introduced/used, then absent for a long stretch, then resurfaces — a recall cue is due).
    for s, idxs in uses.items():
        if len(idxs) < 2:
            continue
        gaps = [(idxs[k + 1] - idxs[k], idxs[k], idxs[k + 1]) for k in range(len(idxs) - 1)]
        maxgap, before, after = max(gaps)
        if maxgap > 6:
            stale.append((s, before, after, maxgap))
    stale.sort(key=lambda t: -t[3])
    return {"spikes": spikes, "stale_intros": stale}


def main():
    ap = argparse.ArgumentParser(description="Per-frame cognitive-load lower bound for a reader profile.")
    ap.add_argument("tex")
    ap.add_argument("--profile", default="P1", choices=list(PROFILES))
    ap.add_argument("--gradient", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

    path = Path(a.tex)
    tex = inline_inputs(path.read_text(encoding="utf-8", errors="replace"), path.resolve().parent)
    frames, seen, uses = analyse(tex, a.profile)
    grad = gradient_report(frames, seen, uses) if a.gradient else None

    if a.json:
        print(json.dumps({"profile": a.profile, "frames": frames, "gradient": grad},
                         ensure_ascii=False, indent=2))
        return

    prof = PROFILES[a.profile]
    print(f"\n  concept-load (mechanical LOWER BOUND) — profile {a.profile} ({prof['name']})")
    print(f"  L_mech = {W_S}·symLoad + {W_J}·jumps + {W_R}·backref + {W_A}·abs   "
          f"(model adds new-concept term)\n")
    print(f"  {'#':>3}  {'frame title':<36}  {'newSym':>6}  {'symL':>5}  {'jump':>4}  "
          f"{'bref':>4}  {'abs':>3}  {'L_mech':>6}  {'Lmax':>4}  flag")
    print("  " + "─" * 104)
    for r in frames:
        print(f"  {r['idx']:>3}  {r['title']:<36}  {r['new_sym']:>6}  {r['sym_load']:>5}  "
              f"{r['jumps']:>4}  {r['backref']:>4}  {r['abs']:>3}  {r['L_mech']:>6}  "
              f"{r['L_max']:>4}  {r['flag']}")
    over = [r for r in frames if r["flag"] == "OVERLOAD"]
    tight = [r for r in frames if r["flag"] == "TIGHT"]
    print("  " + "─" * 104)
    print(f"  {len(frames)} frames · OVERLOAD (lower bound already over ceiling): {len(over)} · TIGHT: {len(tight)}")
    if over:
        print("  OVERLOAD frames:", ", ".join(f"#{r['idx']}" for r in over))
    print("  NOTE: L_mech omits the new-CONCEPT term — model annotation can only RAISE L. "
          "Lower bound only.")

    if grad:
        print("\n  gradient (mechanical):")
        if grad["spikes"]:
            for s in grad["spikes"]:
                print(f"    spike  #{s[0]}→#{s[1]}  ΔL_mech=+{s[2]}  into '{s[3]}'")
        else:
            print("    no mechanical spikes ≥4.0")
        if grad["stale_intros"]:
            print("    (symbols with a >6-frame gap between uses — a recall cue may be due)")
            for s in grad["stale_intros"][:12]:
                print(f"    stale  '{s[0]}'  gap of {s[3]} frames (#{s[1]}→#{s[2]})")


if __name__ == "__main__":
    main()
