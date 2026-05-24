#!/usr/bin/env python3
"""test_themes.py — Theme compilation validator + layout stress tests

Phase 3.3: Validate all themes compile standalone.
Phase 3.4: Stress-test all layouts across all themes (5 × 8 = 40 runs).

Usage:
  python tools/test_themes.py              # Theme compilation only (5 runs)
  python tools/test_themes.py --layouts    # Full layout stress test (40 runs)
  python tools/test_themes.py --theme dark # Test single theme only
  python tools/test_themes.py --list       # List available themes + layouts
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# ── Configuration ────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent
BUILD_DIR = PROJECT_ROOT / "build"
TEMPLATE_LIB = PROJECT_ROOT / "template-lib"

THEMES = ["academic", "teal", "dark", "navygold", "minimal"]
LAYOUTS = ["text", "1img", "2img", "3img", "eq", "table", "imgtop", "twocol"]

# ANSI colours
_C = {"G": "\033[92m", "Y": "\033[93m", "R": "\033[91m",
      "B": "\033[94m", "b": "\033[1m", "0": "\033[0m"}


def cc(s, k):
    return f"{_C[k]}{s}{_C['0']}"


# ── LaTeX skeletons ──────────────────────────────────────────────────────────

def _theme_skeleton(theme: str) -> str:
    """Minimal standalone .tex that loads a theme via template-lib."""
    return (
        r"\documentclass[aspectratio=169]{beamer}"
        rf"\usepackage[{theme}]{{template-lib/template-lib}}"
        r"\begin{document}"
        rf"\begin{{frame}}{{Test {theme}}}"
        rf"Hello from {theme} theme."
        r"\end{frame}"
        r"\end{document}"
    )


def _layout_skeleton(theme: str, layout: str) -> str:
    """Standalone .tex that loads a theme + exercises one layout."""
    # Base preamble
    tex = (
        r"\documentclass[aspectratio=169]{beamer}"
        f"\n\\usepackage[{theme}]{{template-lib/template-lib}}"
        f"\n\\uselayout{{{layout}}}"
        r"\n\begin{document}"
    )

    # Layout-specific content
    if layout == "text":
        tex += (
            r"\n\begin{frame}{Text Layout}"
            r"\n  \begin{TLtext}"
            r"\n    \begin{itemize}"
            r"\n      \item First point about the method"
            r"\n      \item Second point with details"
            r"\n      \item Third takeaway"
            r"\n    \end{itemize}"
            r"\n  \end{TLtext}"
            r"\n\end{frame}"
        )
    elif layout == "1img":
        tex += (
            r"\n\begin{frame}{1-Image Layout}"
            r"\n  \TLoneimgleft[0.50]{example-image-a}{"
            r"\n    \begin{itemize}"
            r"\n      \item Left image, right text"
            r"\n      \item Side-by-side layout"
            r"\n    \end{itemize}"
            r"\n  }"
            r"\n\end{frame}"
        )
    elif layout == "2img":
        tex += (
            r"\n\begin{frame}{2-Image Layout}"
            r"\n  \TLtwoimg[0.45]{example-image-a}{Caption A}{example-image-b}{Caption B}"
            r"\n\end{frame}"
        )
    elif layout == "3img":
        tex += (
            r"\n\begin{frame}{3-Image Layout}"
            r"\n  \TLthreeimg[0.30]{example-image-a}{A}{example-image-b}{B}{example-image-c}{C}"
            r"\n\end{frame}"
        )
    elif layout == "eq":
        tex += (
            r"\n\begin{frame}{Equation Layout}"
            r"\n  \TLeqsingle{"
            r"\n    \nabla \cdot \mathbf{E} = \frac{\rho}{\varepsilon_0}"
            r"\n  }{Gauss's law in differential form.}"
            r"\n\end{frame}"
        )
    elif layout == "table":
        tex += (
            r"\n\begin{frame}{Table Layout}"
            r"\n  \TLtablefull{"
            r"\n    \begin{tabular}{lcc}"
            r"\n      \toprule"
            r"\n      Method & PSNR & SSIM \\"
            r"\n      \midrule"
            r"\n      FBP & 28.5 & 0.82 \\"
            r"\n      Ours & \textbf{35.2} & \textbf{0.91} \\"
            r"\n      \bottomrule"
            r"\n    \end{tabular}"
            r"\n  }{Quantitative comparison on AAPM dataset.}"
            r"\n\end{frame}"
        )
    elif layout == "imgtop":
        tex += (
            r"\n\begin{frame}{Image-Top Layout}"
            r"\n  \TLimgtopsingle{example-image-a}{Overview figure}{"
            r"\n    \begin{itemize}"
            r"\n      \item Key observation 1"
            r"\n      \item Key observation 2"
            r"\n    \end{itemize}"
            r"\n  }"
            r"\n\end{frame}"
        )
    elif layout == "twocol":
        tex += (
            r"\n\begin{frame}{Two-Column Layout}"
            r"\n  \TLtwocol{"
            r"\n    \textbf{Left column}"
            r"\n    \begin{itemize}"
            r"\n      \item Point A"
            r"\n      \item Point B"
            r"\n    \end{itemize}"
            r"\n  }{"
            r"\n    \textbf{Right column}"
            r"\n    \begin{itemize}"
            r"\n      \item Point C"
            r"\n      \item Point D"
            r"\n    \end{itemize}"
            r"\n  }"
            r"\n\end{frame}"
        )

    tex += r"\n\end{document}"
    return tex


# ── Compilation ──────────────────────────────────────────────────────────────

def compile_tex(tex_source: str, jobname: str, cwd: Path) -> tuple[bool, str]:
    """Compile LaTeX source inline via -jobname, return (success, stderr)."""
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    xelatex = shutil.which("xelatex")
    if xelatex is None:
        return False, "xelatex not found in PATH"

    # Escape for shell: the source is passed as a single argument
    # On Windows PowerShell/cmd we can pass it directly; subprocess handles quoting
    result = subprocess.run(
        [
            xelatex,
            "-interaction=nonstopmode",
            "-output-directory", str(BUILD_DIR),
            "-jobname", jobname,
            tex_source,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(cwd),
    )

    combined = result.stdout + result.stderr
    fatal = (
        "! Emergency stop" in combined
        or "! LaTeX Error" in combined
        or "! Undefined control sequence" in combined
    )

    pdf_path = BUILD_DIR / f"{jobname}.pdf"
    success = not fatal and pdf_path.exists() and pdf_path.stat().st_size > 1000

    # Clean up temp aux files in build/
    for ext in [".aux", ".log", ".nav", ".out", ".snm", ".toc"]:
        (BUILD_DIR / f"{jobname}{ext}").unlink(missing_ok=True)

    return success, combined if not success else ""


# ── Test runners ─────────────────────────────────────────────────────────────

def test_themes(themes: list[str]) -> dict[str, bool]:
    """Compile-test each theme standalone. Returns {theme: passed}."""
    print()
    print(cc("  Theme Compilation Tests", "b"))
    print("  " + "─" * 50)

    results = {}
    for theme in themes:
        tex = _theme_skeleton(theme)
        success, err = compile_tex(tex, f"test-theme-{theme}", PROJECT_ROOT)
        results[theme] = success

        status = cc("PASS", "G") if success else cc("FAIL", "R")
        print(f"  {theme:<12} {status}")
        if not success:
            # Print first error line
            for line in err.splitlines():
                if line.startswith("!"):
                    print(f"    {cc(line[:70], 'R')}")
                    break

    return results


def test_layouts(themes: list[str], layouts: list[str]) -> dict[tuple[str, str], bool]:
    """Stress-test: each layout × each theme. Returns {(theme,layout): passed}."""
    print()
    print(cc("  Layout Stress Tests (5 themes × 8 layouts)", "b"))
    print("  " + "─" * 50)

    results = {}
    total = len(themes) * len(layouts)
    passed = 0

    for theme in themes:
        row = []
        for layout in layouts:
            tex = _layout_skeleton(theme, layout)
            success, err = compile_tex(tex, f"test-{theme}-{layout}", PROJECT_ROOT)
            results[(theme, layout)] = success
            if success:
                passed += 1

            mark = cc("●", "G") if success else cc("●", "R")
            row.append(mark)

        print(f"  {theme:<12} " + " ".join(row))

    print()
    pct = (passed / total * 100) if total else 0
    color = "G" if passed == total else "Y" if passed >= total * 0.8 else "R"
    print(f"  {cc('Total:', 'b')} {passed}/{total}  ({cc(f'{pct:.0f}%', color)})")

    # Print failures
    failures = [(t, l) for (t, l), ok in results.items() if not ok]
    if failures:
        print()
        print(cc("  Failures:", "R"))
        for t, l in failures:
            print(f"    {cc(f'{t} × {l}', 'R')}")

    return results


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    # Reconfigure stdout for Unicode on Windows
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

    parser = argparse.ArgumentParser(
        description="Theme validator + layout stress tests for template-lib"
    )
    parser.add_argument(
        "--layouts", action="store_true",
        help="Run full layout stress test (40 compilations)"
    )
    parser.add_argument(
        "--theme", type=str, choices=THEMES,
        help="Test a single theme only"
    )
    parser.add_argument(
        "--list", action="store_true",
        help="List available themes and layouts"
    )
    args = parser.parse_args()

    if args.list:
        print("Themes:", ", ".join(THEMES))
        print("Layouts:", ", ".join(LAYOUTS))
        sys.exit(0)

    themes = [args.theme] if args.theme else THEMES

    # Check xelatex
    if shutil.which("xelatex") is None:
        print(cc("ERROR: xelatex not found in PATH", "R"))
        sys.exit(1)

    # Run tests
    theme_results = test_themes(themes)

    layout_results = {}
    if args.layouts:
        layout_results = test_layouts(themes, LAYOUTS)

    # Summary
    print()
    print(cc("  Summary", "b"))
    print("  " + "─" * 50)

    theme_pass = sum(theme_results.values())
    theme_total = len(theme_results)
    theme_pct = theme_pass / theme_total * 100 if theme_total else 0
    t_color = "G" if theme_pass == theme_total else "R"
    print(f"  Themes:    {theme_pass}/{theme_total}  ({cc(f'{theme_pct:.0f}%', t_color)})")

    if args.layouts:
        layout_pass = sum(layout_results.values())
        layout_total = len(layout_results)
        layout_pct = layout_pass / layout_total * 100 if layout_total else 0
        l_color = "G" if layout_pass == layout_total else "Y" if layout_pass >= layout_total * 0.8 else "R"
        print(f"  Layouts:   {layout_pass}/{layout_total}  ({cc(f'{layout_pct:.0f}%', l_color)})")

    # Exit code
    all_pass = all(theme_results.values())
    if args.layouts:
        all_pass = all_pass and all(layout_results.values())

    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
