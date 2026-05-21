#!/usr/bin/env python3
"""Privacy scanner: check PNGs, PDFs, and text files for personal information."""

import subprocess
import os
import sys

KEYWORDS = ['郭', '炜', '栋', '报告人', 'CvG', 'MICCAI', '郭炜栋', 'gwd200']


def check_pdf_text(pdf_path):
    """Extract text from PDF and check for keywords."""
    try:
        result = subprocess.run(
            ['pdftotext', '-layout', pdf_path, '-'],
            capture_output=True, text=True, encoding='utf-8', errors='replace'
        )
        return result.stdout
    except Exception as e:
        return f"[ERROR: {e}]"


def check_tex_source(tex_path):
    """Check .tex source for keywords."""
    try:
        with open(tex_path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except Exception as e:
        return f"[ERROR: {e}]"


def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    theme_lib = os.path.join(base, 'theme-library')

    print("=" * 60)
    print("PRIVACY ROI SCAN — theme-library/")
    print("=" * 60)

    # Check PDFs
    print("\n## PDF Files (text extraction)")
    print("-" * 40)
    pdfs = sorted([f for f in os.listdir(theme_lib) if f.endswith('.pdf')])
    for pdf in pdfs:
        path = os.path.join(theme_lib, pdf)
        text = check_pdf_text(path)
        found_kw = [(kw, line.strip()) for kw in KEYWORDS for line in text.split('\n') if kw in line]
        if found_kw:
            print(f"\n  *** {pdf} — PERSONAL INFO FOUND ***")
            for kw, line in found_kw:
                print(f"    [{kw}] → {line}")
        else:
            preview = text[:150].replace('\n', ' | ')
            print(f"  {pdf}: Clean — preview: {preview[:100]}...")

    # Check .tex sources in theme-library
    print("\n## TeX Source Files")
    print("-" * 40)
    texs = sorted([f for f in os.listdir(theme_lib) if f.endswith('.tex')])
    for tex in texs:
        path = os.path.join(theme_lib, tex)
        content = check_tex_source(path)
        found_kw = [(kw, line.strip()) for kw in KEYWORDS
                     for i, line in enumerate(content.split('\n'), 1) if kw in line]
        if found_kw:
            print(f"\n  *** {tex} — PERSONAL INFO FOUND ***")
            for kw, line in found_kw:
                print(f"    [{kw}] → {line}")
        else:
            print(f"  {tex}: Clean")

    # Check PNG metadata
    print("\n## PNG Files (filename + size)")
    print("-" * 40)
    pngs = sorted([f for f in os.listdir(theme_lib) if f.endswith('.png')])
    for png in pngs:
        path = os.path.join(theme_lib, png)
        size_kb = os.path.getsize(path) / 1024
        print(f"  {png}: {size_kb:.1f} KB")

    # Also check personal-deck (even if gitignored)
    pd_dir = os.path.join(base, 'personal-deck')
    if os.path.isdir(pd_dir):
        print("\n## personal-deck/ (may be gitignored)")
        print("-" * 40)
        for f in sorted(os.listdir(pd_dir)):
            if f.endswith('.tex'):
                path = os.path.join(pd_dir, f)
                content = check_tex_source(path)
                found_kw = [(kw, i, line.strip()) for kw in KEYWORDS
                             for i, line in enumerate(content.split('\n'), 1) if kw in line]
                if found_kw:
                    print(f"\n  *** {f} — PERSONAL INFO FOUND ***")
                    for kw, lineno, line in found_kw:
                        print(f"    L{lineno} [{kw}] → {line}")
                else:
                    print(f"  {f}: Clean")

    # Check git history for personal info
    print("\n## Git History Check")
    print("-" * 40)
    result = subprocess.run(
        ['git', 'log', '--all', '--oneline', '-S', '郭炜栋'],
        capture_output=True, text=True, encoding='utf-8', errors='replace',
        cwd=base
    )
    if result.stdout.strip():
        print("  *** Commits containing '郭炜栋':")
        for line in result.stdout.strip().split('\n'):
            print(f"    {line}")
    else:
        print("  No commits found with '郭炜栋'")

    print("\n" + "=" * 60)
    print("SCAN COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    main()
