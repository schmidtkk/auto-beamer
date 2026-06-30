#!/usr/bin/env python3
"""Static validation gates for AutoBeamer decks."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


BANNED_OVERLAYS = (r"\pause", r"\onslide", r"\only", r"\uncover")
BOX_COMMAND = re.compile(r"\\TL(?:infoblock|alertblock|resultblock|warnblock|takeaway)\b")
FRAME_RE = re.compile(
    r"\\begin\{frame\}(?:\[[^\]]*\])?(?:\{([^{}]*)\})?(.*?)\\end\{frame\}",
    re.DOTALL,
)
FRAMETITLE_RE = re.compile(r"\\frametitle\{([^{}]*)\}")


@dataclass(frozen=True)
class Frame:
    index: int
    title: str
    body: str
    start: int
    end: int


def clean_text(text: str) -> str:
    text = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?", " ", text)
    text = re.sub(r"[{}$]", " ", text)
    return re.sub(r"\s+", " ", text).strip().lower()


def parse_frames(source: str) -> list[Frame]:
    frames: list[Frame] = []
    for index, match in enumerate(FRAME_RE.finditer(source), start=1):
        body = match.group(2)
        title = match.group(1) or ""
        if not title:
            title_match = FRAMETITLE_RE.search(body)
            if title_match:
                title = title_match.group(1)
        frames.append(Frame(index=index, title=title.strip(), body=body, start=match.start(), end=match.end()))
    return frames


def has_reference(frame: Frame) -> bool:
    text = clean_text(frame.title + " " + frame.body)
    return (
        "reference" in text
        or "bibliography" in text
        or r"\begin{thebibliography}" in frame.body
        or r"\bibliography" in frame.body
    )


def is_thank_you(frame: Frame) -> bool:
    text = clean_text(frame.title + " " + frame.body)
    return "thank you" in text or text == "thanks" or "questions" in text and "thank" in text


def is_backup(frame: Frame) -> bool:
    text = clean_text(frame.title + " " + frame.body)
    return "backup" in text or "appendix" in text


def contains_any(frames: list[Frame], terms: tuple[str, ...]) -> bool:
    text = "\n".join(clean_text(frame.title + " " + frame.body) for frame in frames)
    return any(term in text for term in terms)


def validate_static(path: Path, mode: str | None) -> list[str]:
    source = path.read_text(encoding="utf-8")
    frames = parse_frames(source)
    violations: list[str] = []

    if not frames:
        violations.append("No Beamer frames found.")

    for command in BANNED_OVERLAYS:
        if command in source:
            violations.append(f"Illegal overlay command found: {command}")

    if r"\tiny" in source:
        violations.append(r"Illegal font size command found: \tiny")

    for frame in frames:
        box_count = len(BOX_COMMAND.findall(frame.body))
        if box_count > 3:
            violations.append(
                f"Frame {frame.index} has {box_count} colored boxes; maximum is 3."
            )

    reference_indices = [i for i, frame in enumerate(frames) if has_reference(frame)]
    thank_indices = [i for i, frame in enumerate(frames) if is_thank_you(frame)]

    if mode == "academic-presentation" or thank_indices:
        if not reference_indices:
            violations.append("References slide missing before Thank You.")
        if not thank_indices:
            violations.append("Thank You slide missing after References.")
        if reference_indices and thank_indices:
            first_thank = thank_indices[0]
            if first_thank == 0 or reference_indices[-1] != first_thank - 1:
                violations.append(
                    "References slide must be second-to-last before Thank You."
                )

    backup_indices = [i for i, frame in enumerate(frames) if is_backup(frame)]
    if backup_indices:
        appendix_pos = source.find(r"\appendix")
        first_backup_start = frames[backup_indices[0]].start
        if appendix_pos == -1 or appendix_pos > first_backup_start:
            violations.append(r"\appendix must appear before backup slides.")

    if mode == "passive-study":
        if not contains_any(frames, ("glossary", "notation")):
            violations.append("passive-study requires a glossary or notation section.")
        if not contains_any(frames, ("exercise", "exercises")):
            violations.append("passive-study requires exercise frames.")
        if not reference_indices and not contains_any(frames, ("bibliography", "bibliographical")):
            violations.append("passive-study requires references or bibliographical notes.")
    elif mode == "active-socratic":
        if not contains_any(frames, ("question", "?")):
            violations.append("active-socratic requires question frames.")
        if not contains_any(frames, ("attempt", "try", "derive")):
            violations.append("active-socratic requires learner-work attempt gates.")
        if not contains_any(frames, ("hint", "solution", "reflection")):
            violations.append("active-socratic requires hints, solutions, or reflection frames.")
    elif mode == "academic-presentation":
        if not backup_indices:
            violations.append("academic-presentation requires backup slides after Thank You.")
    elif mode == "problem-sheet":
        # Accept either literal keywords or the comp-exercise macros (raw source).
        has_problems = (r"\TLprobtitle" in source
                        or contains_any(frames, ("exercise", "exercises", "problem", "习题")))
        has_hints = (r"\TLhint" in source or contains_any(frames, ("hint", "提示")))
        has_solutions = (r"\TLsoltitle" in source
                         or contains_any(frames, ("solution", "solutions", "解答")))
        if not has_problems:
            violations.append("problem-sheet requires problem/exercise frames.")
        if not has_hints:
            violations.append("problem-sheet requires weak-to-strong hints.")
        if r"\appendix" not in source:
            violations.append(r"problem-sheet requires an \appendix answer key.")
        if not has_solutions:
            violations.append("problem-sheet requires worked-solution frames in the answer key.")
        # Worked solutions must live after \appendix, not interleaved with the problems.
        appendix_pos = source.find(r"\appendix")
        sol_pos = source.find(r"\TLsoltitle")
        if sol_pos == -1:
            sol_only = [f for f in frames if contains_any([f], ("solution", "解答"))]
            sol_pos = sol_only[0].start if sol_only else -1
        if appendix_pos != -1 and sol_pos != -1 and sol_pos < appendix_pos:
            violations.append(r"Worked solutions must appear after \appendix (struggle-first).")

    return violations


def cmd_static(args: argparse.Namespace) -> int:
    path = Path(args.file)
    violations = validate_static(path, args.mode)
    if violations:
        print(f"FAIL static validation: {path}")
        for violation in violations:
            print(f"- {violation}")
        return 1
    print(f"PASS static validation: {path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    static = subparsers.add_parser("static", help="Run source-level validation gates")
    static.add_argument("file", help="Path to deck .tex file")
    static.add_argument(
        "--mode",
        choices=("passive-study", "active-socratic", "academic-presentation", "problem-sheet"),
        help="Deck mode for mode-specific section gates",
    )
    static.set_defaults(func=cmd_static)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
