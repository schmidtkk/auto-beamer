#!/bin/bash
# ============================================================================
# build.sh — Cross-Platform XeLaTeX Build Script
# ============================================================================
# Usage:
#   ./build.sh [deck-name]          (default: cvgdiff-beamer)
#   ./build.sh template-lib-demo
#   ./build.sh all                  (compile all .tex files)
#
# Mirrors build_clean.ps1 functionality for Linux/macOS.
# ============================================================================

set -e

# ── Defaults ──────────────────────────────────────────────────────────────────
DECK="${1:-cvgdiff-beamer}"
BUILD_DIR="build"

# ── Detect OS ─────────────────────────────────────────────────────────────────
OS="unknown"
case "$(uname -s)" in
    Linux*)     OS="linux";;
    Darwin*)    OS="macos";;
    CYGWIN*|MINGW*|MSYS*) OS="windows";;
esac

echo "=== Beamer Deck Auto Build ==="
echo "OS: $OS"
echo ""

# ── Check xelatex ─────────────────────────────────────────────────────────────
if ! command -v xelatex &> /dev/null; then
    echo "ERROR: xelatex not found in PATH."
    echo "Please install TeX Live: https://tug.org/texlive/"
    echo "For Linux, run: ./install-linux.sh"
    exit 1
fi

# ── Determine files to compile ────────────────────────────────────────────────
TEX_FILES=()

if [ "$DECK" = "all" ]; then
    for f in *.tex; do
        # Skip minimal files (like PowerShell script does)
        if [[ ! "$f" =~ ^cvgdiff-minimal ]]; then
            TEX_FILES+=("$f")
        fi
    done
    if [ ${#TEX_FILES[@]} -eq 0 ]; then
        echo "ERROR: No .tex files found in current directory."
        exit 1
    fi
else
    if [ ! -f "$DECK.tex" ]; then
        echo "ERROR: File not found: $DECK.tex"
        exit 1
    fi
    TEX_FILES=("$DECK.tex")
fi

# ── Ensure build directory exists ─────────────────────────────────────────────
mkdir -p "$BUILD_DIR"

# ── Clean function ────────────────────────────────────────────────────────────
clean_build_files() {
    local stem="$1"
    echo "=== Cleaning intermediate files for $stem ==="
    local exts=("aux" "nav" "snm" "toc" "log" "out" "fls" "fdb_latexmk" "xdv")
    for ext in "${exts[@]}"; do
        local f="$BUILD_DIR/$stem.$ext"
        if [ -f "$f" ]; then
            rm -f "$f"
            echo "  Removed: $f"
        fi
    done
}

# ── Build function ────────────────────────────────────────────────────────────
build_deck() {
    local tex_file="$1"
    local stem=$(basename "$tex_file" .tex)

    clean_build_files "$stem"

    for pass in 1 2; do
        echo ""
        echo "=== $stem : Pass $pass/2 ==="
        xelatex -output-directory="$BUILD_DIR" -interaction=nonstopmode "$tex_file" || {
            echo "WARNING: Pass $pass exited with non-zero code (may be harmless appendixnumberbeamer errors)"
        }
    done

    # Copy PDF to project root
    local pdf_src="$BUILD_DIR/$stem.pdf"
    local pdf_dst="$stem.pdf"
    if [ -f "$pdf_src" ]; then
        cp -f "$pdf_src" "$pdf_dst"
        echo "  Copied: $pdf_dst"
    fi

    # Check for Overfull \vbox
    local log_file="$BUILD_DIR/$stem.log"
    if [ -f "$log_file" ]; then
        local overflows=$(grep -c "Overfull \\\\vbox" "$log_file" || true)
        if [ "$overflows" -gt 0 ]; then
            echo "  WARNING: Overfull \\vbox detected ($overflows occurrences):"
            grep "Overfull \\\\vbox" "$log_file" | head -n 5 | sed 's/^/    /'
        else
            echo "  No Overfull \\vbox detected."
        fi
    fi

    echo ""
}

# ── Main loop ─────────────────────────────────────────────────────────────────
for tex in "${TEX_FILES[@]}"; do
    build_deck "$tex"
done

echo "=== Build complete ==="

# Final Overfull check on primary deck
if [ -f "$BUILD_DIR/cvgdiff-beamer.log" ]; then
    echo "=== Checking for Overfull \\vbox ==="
    local overfull=$(grep "Overfull \\\\vbox" "$BUILD_DIR/cvgdiff-beamer.log" || true)
    if [ -n "$overfull" ]; then
        echo "WARNING: Found Overfull \\vbox:"
        echo "$overfull" | sed 's/^/  /'
    else
        echo "  No Overfull \\vbox found."
    fi
fi

echo ""
echo "=== Done ==="
