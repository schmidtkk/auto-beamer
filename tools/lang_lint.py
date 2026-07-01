#!/usr/bin/env python3
"""Language-quality linter for AutoBeamer decks.

Deterministic, LaTeX-aware enforcement of the executable subset of the
language-quality gate (流畅性·准确度·优雅性·科学性). It does NOT replace
model judgment — it catches the mechanically detectable defects so the
reviewer can spend attention on the rest. See
`skills/autobeamer-review/references/language-quality-gate.md`.

What it checks (Chinese teaching-deck register, adapted from the 说人话 taxonomy):
  - Foreign-language *prose* leakage — the one hard gate that is mechanical:
    a sentence-like run of English words (with function words) outside math
    and commands. English terms (Wasserstein, Prokhorov) and `$...$` are exempt.
  - AI-flavor fillers / empty summaries (tier 1, always flagged).
  - Proof hedges (显然/易证/不难发现/类似地…) — these double as proof-gap smells;
    CRITICAL for passive-study / problem-sheet, advisory otherwise.
  - Connector pile-ups and light-verb translation-ese (tier 2, cluster ≥2/frame).
  - Over-used intensifiers (tier 3, deck-wide density).
  - A couple of structural anti-patterns (not-X-but-Y density; mechanical chains).

"Protect first, then lint": every protected span (math, command names, verbatim,
comments, ref/cite/label/path args) is removed before any check runs, so the
deck's symbols and macros never trip a finding.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path


# --------------------------------------------------------------------------
# Frame parsing (mirrors validate_deck.py)
# --------------------------------------------------------------------------
FRAME_RE = re.compile(
    r"\\begin\{frame\}(?:\[[^\]]*\])?(?:\{([^{}]*)\})?(.*?)\\end\{frame\}",
    re.DOTALL,
)
FRAMETITLE_RE = re.compile(r"\\frametitle\{([^{}]*)\}")
INPUT_RE = re.compile(r"\\(?:input|include|subfile)\{([^{}]+)\}")


@dataclass(frozen=True)
class Frame:
    index: int
    title: str
    body: str


def flatten_inputs(source: str, base_dir: Path, depth: int = 0) -> str:
    """One/two-level expansion of \\input/\\include so split decks lint whole."""
    if depth > 4:
        return source

    def repl(match: re.Match[str]) -> str:
        name = match.group(1).strip()
        for cand in (base_dir / name, base_dir / f"{name}.tex"):
            if cand.is_file():
                return flatten_inputs(cand.read_text(encoding="utf-8", errors="replace"),
                                      cand.parent, depth + 1)
        return ""  # missing include → drop, do not lint its placeholder

    return INPUT_RE.sub(repl, source)


def parse_frames(source: str) -> list[Frame]:
    frames: list[Frame] = []
    for index, match in enumerate(FRAME_RE.finditer(source), start=1):
        title = match.group(1) or ""
        body = match.group(2)
        if not title:
            tm = FRAMETITLE_RE.search(body)
            if tm:
                title = tm.group(1)
        frames.append(Frame(index=index, title=title.strip(), body=body))
    return frames


# --------------------------------------------------------------------------
# Protected-span stripping: produce a CJK/English *prose* view of a frame.
# --------------------------------------------------------------------------
COMMENT_RE = re.compile(r"(?<!\\)%.*")
MATH_ENVS = "|".join((
    "equation", "align", "gather", "multline", "eqnarray", "array", "cases",
    "split", "alignat", "flalign", "displaymath", "math",
))
VERBATIM_ENVS = "|".join(("verbatim", "lstlisting", "minted", "Verbatim", "semiverbatim"))
MATH_ENV_RE = re.compile(rf"\\begin\{{({MATH_ENVS})\*?\}}.*?\\end\{{\1\*?\}}", re.DOTALL)
VERBATIM_ENV_RE = re.compile(rf"\\begin\{{({VERBATIM_ENVS})\}}.*?\\end\{{\1\}}", re.DOTALL)
DISPLAY_MATH_RE = re.compile(r"\\\[.*?\\\]", re.DOTALL)
INLINE_PAREN_RE = re.compile(r"\\\(.*?\\\)", re.DOTALL)
DOLLAR_MATH_RE = re.compile(r"\$\$.*?\$\$|\$[^$]*\$", re.DOTALL)
VERB_RE = re.compile(r"\\verb\*?(.).*?\1")
# Commands whose ARGUMENTS are not prose (drop command + all its braces/brackets).
OPAQUE_RE = re.compile(
    r"\\(?:label|ref|eqref|cref|Cref|autoref|pageref|hyperref|hyperlink|hypertarget|"
    r"cite|citep|citet|citeauthor|url|href|includegraphics|input|include|usepackage|"
    r"documentclass|texttt|lstinline|path|filename|color|textcolor|definecolor|"
    r"setbeamercolor|setbeamertemplate)\*?(?:\[[^\]]*\])?(?:\{[^{}]*\})*"
)
BEGIN_END_RE = re.compile(r"\\(?:begin|end)\{[^{}]*\}(?:\[[^\]]*\])?")
CONTROL_SEQ_RE = re.compile(r"\\[a-zA-Z@]+\*?(?:\[[^\]]*\])?")
CJK_RE = re.compile(r"[㐀-鿿豈-﫿]")


def prose_view(text: str) -> str:
    """Strip protected spans; keep natural-language text (incl. \\textbf{…} content)."""
    text = COMMENT_RE.sub(" ", text)
    text = VERBATIM_ENV_RE.sub(" ", text)
    text = MATH_ENV_RE.sub(" ", text)
    text = DISPLAY_MATH_RE.sub(" ", text)
    text = INLINE_PAREN_RE.sub(" ", text)
    text = DOLLAR_MATH_RE.sub(" ", text)
    text = VERB_RE.sub(" ", text)
    text = OPAQUE_RE.sub(" ", text)
    text = BEGIN_END_RE.sub(" ", text)
    # Remaining control sequences: drop the macro token + optional arg, keep brace
    # CONTENT (so \textbf{要点}/\TLtakeaway{…}/\deflab{…} contribute their prose).
    text = CONTROL_SEQ_RE.sub(" ", text)
    text = text.replace("{", " ").replace("}", " ").replace("$", " ")
    return re.sub(r"[ \t]+", " ", text)


# --------------------------------------------------------------------------
# Lexicons (说人话-derived, tuned for academic teaching Chinese)
# --------------------------------------------------------------------------
# (pattern, suggestion) — patterns are regexes.
TIER1 = [
    (r"值得注意的是", "删去；直接陈述要点"),
    (r"需要(?:注意|指出|强调|说明)的是", "删去；直接陈述要点"),
    (r"值得(?:一提|强调)的是", "删去；直接陈述要点"),
    (r"综上所述", "删去空洞收尾；若前文已清楚则无需总结"),
    (r"总(?:的来说|而言之)", "删去空洞收尾"),
    (r"一言以蔽之", "删去；直接给结论"),
    (r"归根结底", "删去；直接给结论"),
    (r"众所周知", "删去；若是前提就明确陈述（也是证明跳步信号）"),
    (r"正如我们所知", "删去；明确陈述所依赖的事实"),
    (r"我们都知道", "删去；明确陈述所依赖的事实"),
    (r"随着.{0,12}的(?:发展|不断|日益)", "删去套话开头；直接进入主题"),
    (r"在.{0,6}的今天", "删去套话开头；直接进入主题"),
    (r"起着?(?:至关重要|举足轻重)的作用", "改为具体说明它做了什么"),
    (r"扮演着?(?:重要|关键)的角色", "改为具体说明它做了什么"),
    (r"具有(?:重要|深远)(?:的)?(?:意义|价值)", "改为具体说明意义在哪"),
    (r"不(?:容忽视|言而喻)", "删去；用具体理由替代"),
    (r"赋能", "改为具体动词（支持/驱动/使……能够）"),
    (r"助力", "改为具体动词"),
    (r"一站式|全方位|保姆级", "删去自媒体式夸张修饰"),
]
# Proof hedges — gap-free-proof smells. Severity depends on mode.
PROOF_HEDGE = [
    (r"显然", "passive-study/problem-sheet 中不可用“显然”代替步骤；补出推理"),
    (r"易(?:证|知|见)", "补出该步推理，不要以“易证/易知”跳过"),
    (r"不难(?:发现|看出|证明|得到|验证)", "补出该步推理，不要以“不难……”跳过"),
    (r"可(?:以)?验证", "把“验证”过程写出来"),
    (r"类似地", "把“类似地”省去的对称部分补全或显式说明对称性"),
    (r"同理可证", "把对称论证写出，至少给出一行说明为何对称"),
    (r"读者(?:自行|可)?(?:验证|证明|补全)", "教学稿不外包给读者；补出该步"),
]
# Tier 2 — flagged only when clustered (≥2 in one frame's prose).
TIER2 = [
    (r"然而", "连接词堆叠：保留一处，其余删"),
    (r"因此", "连接词堆叠：保留一处，其余删"),
    (r"此外", "连接词堆叠：保留一处，其余删"),
    (r"从而", "连接词堆叠：保留一处，其余删"),
    (r"进而", "连接词堆叠：保留一处，其余删"),
    (r"于是", "连接词堆叠：保留一处，其余删"),
    (r"进行(?:了)?", "去掉轻动词“进行”，用实义动词（翻译腔）"),
]
# Tier 3 — flagged only on deck-wide over-use.
TIER3 = [
    (r"重要", 3),
    (r"优化", 3),
    (r"深刻", 2),
    (r"深远", 2),
    (r"极大", 2),
    (r"极其|十分|非常", 4),
]
# Structural anti-patterns (regex, label, suggestion, per-frame threshold).
NOT_X_BUT_Y = re.compile(r"不是[^，。；！？]{1,24}而是")
MECH_CHAIN = re.compile(r"首先.{0,80}?其次.{0,120}?(?:然后|接着|再次).{0,160}?最后", re.DOTALL)

# English function words: their presence marks a *sentence*, not a term list.
EN_STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being", "to", "of",
    "and", "or", "that", "this", "these", "those", "with", "for", "we", "you", "it",
    "in", "on", "as", "by", "can", "will", "which", "our", "from", "at", "if", "not",
    "but", "so", "than", "then", "into", "such", "have", "has", "had", "do", "does",
}
EN_RUN_RE = re.compile(r"[A-Za-z][A-Za-z'\-]*(?:\s+[A-Za-z][A-Za-z'\-]*){5,}")


@dataclass
class Finding:
    frame: int
    severity: str   # CRITICAL | MAJOR | MINOR
    category: str
    match: str
    suggestion: str


# --------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------
def _english_runs(prose: str) -> list[str]:
    runs = []
    for m in EN_RUN_RE.finditer(prose):
        words = m.group(0).split()
        stop = sum(1 for w in words if w.lower() in EN_STOPWORDS)
        # sentence-like = enough words AND real function words (≥2, or ≥1 for long runs)
        if (len(words) >= 6 and stop >= 2) or (len(words) >= 8 and stop >= 1):
            runs.append(" ".join(words))
    return runs


def lint_frame(frame: Frame, prose: str, mode: str | None, is_cjk: bool) -> list[Finding]:
    out: list[Finding] = []

    if is_cjk:
        for run in _english_runs(prose):
            snippet = run if len(run) <= 70 else run[:67] + "…"
            out.append(Finding(frame.index, "CRITICAL", "foreign-prose-leakage",
                               snippet, "中文稿中不得出现整句英文散文；改写为中文（术语与 $…$ 例外）"))

    for pat, sug in TIER1:
        for m in re.finditer(pat, prose):
            out.append(Finding(frame.index, "MAJOR", "ai-filler", m.group(0), sug))

    hedge_sev = "CRITICAL" if mode in ("passive-study", "problem-sheet") else "MINOR"
    for pat, sug in PROOF_HEDGE:
        for m in re.finditer(pat, prose):
            out.append(Finding(frame.index, hedge_sev, "proof-hedge", m.group(0), sug))

    for pat, sug in TIER2:
        hits = re.findall(pat, prose)
        if len(hits) >= 2:
            out.append(Finding(frame.index, "MINOR", "cluster",
                               f"{hits[0]}×{len(hits)}", sug))

    if len(NOT_X_BUT_Y.findall(prose)) >= 2:
        out.append(Finding(frame.index, "MINOR", "structural",
                           "不是…而是…", "“不是X而是Y”句式堆叠：改为直接陈述Y"))
    if MECH_CHAIN.search(prose):
        out.append(Finding(frame.index, "MINOR", "structural",
                           "首先…其次…最后", "机械罗列：改为有逻辑过渡的行文"))
    return out


def lint_deck(path: Path, mode: str | None) -> tuple[list[Finding], dict]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    raw = flatten_inputs(raw, path.parent)
    frames = parse_frames(raw)

    proses = {f.index: prose_view(f.title + " \n " + f.body) for f in frames}
    whole = " ".join(proses.values())
    cjk_chars = len(CJK_RE.findall(whole))
    en_words = len(re.findall(r"[A-Za-z]{2,}", whole))
    is_cjk = cjk_chars >= 20 and cjk_chars >= en_words

    findings: list[Finding] = []
    if not frames:
        findings.append(Finding(0, "MAJOR", "structure", "no frames", "未找到 Beamer frame"))

    for f in frames:
        findings.extend(lint_frame(f, proses[f.index], mode, is_cjk))

    # tier-3 density (deck-wide)
    n_frames = max(len(frames), 1)
    for pat, base in TIER3:
        hits = len(re.findall(pat, whole))
        if hits > base + n_frames // 4:  # scale a little with deck size
            findings.append(Finding(0, "MINOR", "density",
                                    f"{pat}×{hits}", "高频空泛词：多数处删去或替换为具体表述"))

    summary = {
        "frames": len(frames),
        "is_cjk_deck": is_cjk,
        "critical": sum(1 for f in findings if f.severity == "CRITICAL"),
        "major": sum(1 for f in findings if f.severity == "MAJOR"),
        "minor": sum(1 for f in findings if f.severity == "MINOR"),
    }
    return findings, summary


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def _fails(findings: list[Finding], strict: bool) -> list[Finding]:
    gate = {"CRITICAL", "MAJOR"} if not strict else {"CRITICAL", "MAJOR", "MINOR"}
    return [f for f in findings if f.severity in gate]


def cmd_lint(args: argparse.Namespace) -> int:
    path = Path(args.file)
    findings, summary = lint_deck(path, args.mode)
    if args.json:
        print(json.dumps({"summary": summary, "findings": [asdict(f) for f in findings]},
                         ensure_ascii=False, indent=2))
        return 1 if _fails(findings, args.strict) else 0

    failing = _fails(findings, args.strict)
    if failing or (args.strict and findings):
        print(f"FAIL language lint: {path}")
    else:
        print(f"PASS language lint: {path}")
    if not summary["is_cjk_deck"]:
        print("  (non-CJK deck: foreign-prose-leakage check skipped)")
    for f in sorted(findings, key=lambda x: (x.frame, x.severity)):
        loc = f"frame {f.frame}" if f.frame else "deck"
        print(f"- [{f.severity}] {loc} · {f.category}: «{f.match}» → {f.suggestion}")
    return 1 if (failing or (args.strict and findings)) else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    lint = sub.add_parser("lint", help="Run the language-quality gate on a deck .tex")
    lint.add_argument("file", help="Path to deck .tex (or main file that \\inputs sections)")
    lint.add_argument("--mode",
                      choices=("passive-study", "active-socratic",
                               "academic-presentation", "problem-sheet"),
                      help="Deck mode (gates proof-hedge severity)")
    lint.add_argument("--json", action="store_true", help="Emit findings as JSON")
    lint.add_argument("--strict", action="store_true",
                      help="Also fail on tier-2/tier-3 advisories")
    lint.set_defaults(func=cmd_lint)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
