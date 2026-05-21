#!/bin/bash
# ============================================================================
# install-linux.sh — Linux Environment Setup for Beamer Deck Auto
# ============================================================================
# Installs TeX Live + required packages for XeLaTeX Beamer compilation.
# Does NOT install fonts (user must install CJK fonts separately).
#
# Usage:
#   chmod +x install-linux.sh
#   ./install-linux.sh
#
# Supports: Ubuntu, Debian, and derivatives
# ============================================================================

set -e

echo "=== Beamer Deck Auto — Linux Environment Setup ==="
echo ""

# ── Detect package manager ──────────────────────────────────────────────────
if command -v apt-get &> /dev/null; then
    PKG_MANAGER="apt-get"
    echo "Detected: Debian/Ubuntu system"
elif command -v dnf &> /dev/null; then
    PKG_MANAGER="dnf"
    echo "Detected: Fedora/RHEL system"
elif command -v pacman &> /dev/null; then
    PKG_MANAGER="pacman"
    echo "Detected: Arch Linux system"
else
    echo "WARNING: Could not detect package manager."
    echo "Please install TeX Live manually: https://tug.org/texlive/"
    exit 1
fi

echo ""
echo "=== Step 1: Updating package list ==="
sudo $PKG_MANAGER update

echo ""
echo "=== Step 2: Installing TeX Live + XeLaTeX ==="

if [ "$PKG_MANAGER" = "apt-get" ]; then
    sudo apt-get install -y \
        texlive-xetex \
        texlive-latex-extra \
        texlive-fonts-recommended \
        texlive-fonts-extra \
        texlive-lang-chinese \
        texlive-science \
        texlive-pictures \
        texlive-plain-generic

    echo ""
    echo "=== Step 3: Installing auxiliary tools ==="
    sudo apt-get install -y \
        poppler-utils \
        python3 \
        python3-pip \
        fontconfig

    echo ""
    echo "=== Step 4: Installing CJK fonts (optional but recommended) ==="
    echo "Installing Noto Sans CJK..."
    sudo apt-get install -y fonts-noto-cjk || {
        echo "WARNING: Could not install fonts-noto-cjk."
        echo "You may need to install CJK fonts manually."
    }

elif [ "$PKG_MANAGER" = "dnf" ]; then
    sudo dnf install -y \
        texlive-xetex \
        texlive-metropolis \
        texlive-tcolorbox \
        texlive-adjustbox \
        texlive-pifont \
        texlive-unicode-math \
        texlive-xecjk \
        texlive-booktabs \
        texlive-multirow \
        texlive-colortbl \
        texlive-microtype \
        texlive-tabularx \
        poppler-utils \
        python3 \
        python3-pip \
        fontconfig

    echo ""
    echo "=== Step 4: Installing CJK fonts (optional but recommended) ==="
    sudo dnf install -y google-noto-sans-cjk-fonts || {
        echo "WARNING: Could not install CJK fonts."
        echo "You may need to install CJK fonts manually."
    }

elif [ "$PKG_MANAGER" = "pacman" ]; then
    sudo pacman -S --noconfirm \
        texlive-bin \
        texlive-latexextra \
        texlive-fontsextra \
        texlive-langchinese \
        texlive-science \
        texlive-pictures \
        poppler \
        python \
        python-pip \
        fontconfig

    echo ""
    echo "=== Step 4: Installing CJK fonts (optional but recommended) ==="
    sudo pacman -S --noconfirm noto-fonts-cjk || {
        echo "WARNING: Could not install CJK fonts."
        echo "You may need to install CJK fonts manually."
    }
fi

echo ""
echo "=== Step 5: Verifying installation ==="

# Check XeLaTeX
if command -v xelatex &> /dev/null; then
    echo "✓ XeLaTeX: $(xelatex --version | head -n 1)"
else
    echo "✗ XeLaTeX not found in PATH"
    exit 1
fi

# Check pdftoppm
if command -v pdftoppm &> /dev/null; then
    echo "✓ pdftoppm: $(pdftoppm -v 2>&1 | head -n 1)"
else
    echo "✗ pdftoppm not found (needed for PNG export)"
fi

# Check Python
if command -v python3 &> /dev/null; then
    echo "✓ Python: $(python3 --version)"
else
    echo "✗ Python3 not found"
fi

# Check CJK fonts
echo ""
echo "=== Step 6: Checking CJK fonts ==="
CJK_FOUND=$(fc-list :lang=zh | head -n 5)
if [ -n "$CJK_FOUND" ]; then
    echo "✓ CJK fonts detected:"
    echo "$CJK_FOUND"
else
    echo "✗ No CJK fonts found."
    echo "  Install with:"
    echo "    Ubuntu/Debian: sudo apt-get install fonts-noto-cjk"
    echo "    Fedora:        sudo dnf install google-noto-sans-cjk-fonts"
    echo "    Arch:          sudo pacman -S noto-fonts-cjk"
fi

echo ""
echo "=== Step 7: Verifying required LaTeX packages ==="

# Create a temporary test file
TMPDIR=$(mktemp -d)
cat > "$TMPDIR/test-packages.tex" << 'EOF'
\documentclass{beamer}
\usetheme{metropolis}
\usepackage{appendixnumberbeamer}
\usepackage{unicode-math}
\usepackage{fontspec}
\usepackage{xeCJK}
\usepackage{tcolorbox}
\tcbuselibrary{skins,breakable}
\usepackage{xcolor}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{array}
\usepackage{colortbl}
\usepackage{multirow}
\usepackage{adjustbox}
\usepackage{pifont}
\usepackage{tikz}
\usepackage{amsmath,amssymb}
\usetikzlibrary{positioning,calc}
\usepackage{etoolbox}
\usepackage{microtype}
\usepackage{tabularx}
\begin{document}
\begin{frame}{Test}
Test
\end{frame}
\end{document}
EOF

cd "$TMPDIR"
xelatex -interaction=nonstopmode -output-directory="$TMPDIR" test-packages.tex > /dev/null 2>&1 && \
    echo "✓ All required LaTeX packages available" || \
    echo "✗ Some packages missing — check output above"

# Cleanup
rm -rf "$TMPDIR"

echo ""
echo "=== Installation Complete ==="
echo ""
echo "Next steps:"
echo "  1. If CJK fonts are missing, install them (see Step 6)."
echo "  2. Run: ./build.sh <deck-name>  (or build_clean.ps1 on Windows)"
echo "  3. For custom fonts, set in your .tex file before \\input{config.tex}:"
echo "       \\def\\CJKFontPath{/path/to/fonts/}"
echo "       \\def\\CJKFontName{FontName.ttf}"
echo "       \\def\\CJKFontBold{FontNameBold.ttf}"
echo ""
