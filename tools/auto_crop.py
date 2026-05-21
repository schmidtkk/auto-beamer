"""
auto_crop.py — Remove white margins from an image.

Usage:
    python auto_crop.py <input> [output] [--threshold 245] [--padding 5] [--dryrun]

If output is omitted, writes to <stem>_cropped.<ext>.
--threshold: pixels with all channels >= threshold are considered "background"
--padding:   extra pixels to keep around the detected content box
--dryrun:    print crop region only, don't write output
"""

import sys
import argparse
import numpy as np
from pathlib import Path
from PIL import Image


def find_content_bbox(arr: np.ndarray, threshold: int = 245) -> tuple[int, int, int, int]:
    """
    Return (top, bottom, left, right) of the tightest bounding box
    that contains all pixels with any channel < threshold.
    """
    if arr.ndim == 3:
        # content = any channel is dark enough
        is_bg = np.all(arr >= threshold, axis=2)
    else:
        is_bg = arr >= threshold

    is_content = ~is_bg

    row_has_content = is_content.any(axis=1)  # shape (H,)
    col_has_content = is_content.any(axis=0)  # shape (W,)

    if not row_has_content.any():
        raise ValueError("No content found — try lowering --threshold")

    top    = int(np.argmax(row_has_content))
    bottom = int(len(row_has_content) - np.argmax(row_has_content[::-1]) - 1)
    left   = int(np.argmax(col_has_content))
    right  = int(len(col_has_content) - np.argmax(col_has_content[::-1]) - 1)

    return top, bottom, left, right


def auto_crop(
    input_path: str,
    output_path: str | None = None,
    threshold: int = 245,
    padding: int = 5,
    dryrun: bool = False,
) -> tuple[Image.Image, dict]:
    img = Image.open(input_path).convert("RGB")
    orig_dpi = img.info.get("dpi", (96, 96))
    arr = np.array(img)
    H, W = arr.shape[:2]

    top, bottom, left, right = find_content_bbox(arr, threshold)

    # Apply padding, clamped to image bounds
    top    = max(0,   top    - padding)
    bottom = min(H-1, bottom + padding)
    left   = max(0,   left   - padding)
    right  = min(W-1, right  + padding)

    cropped = img.crop((left, top, right + 1, bottom + 1))
    cW, cH = cropped.size

    dpi_x = orig_dpi[0] if hasattr(orig_dpi, '__len__') else orig_dpi
    dpi_y = orig_dpi[1] if hasattr(orig_dpi, '__len__') else orig_dpi

    info = {
        "original":  (W,  H),
        "cropped":   (cW, cH),
        "box_ltrb":  (left, top, right, bottom),
        "removed":   (W - cW, H - cH),
        "dpi":       (dpi_x, dpi_y),
        "ar_before": W  / H,
        "ar_after":  cW / cH,
        "nat_pt_w":  cW / dpi_x * 72.27,
        "nat_pt_h":  cH / dpi_y * 72.27,
    }

    if not dryrun:
        if output_path is None:
            p = Path(input_path)
            output_path = str(p.parent / f"{p.stem}_cropped{p.suffix}")
        cropped.save(output_path, dpi=(dpi_x, dpi_y))
        info["output"] = output_path

    return cropped, info


def print_report(info: dict, dryrun: bool = False) -> None:
    W,  H  = info["original"]
    cW, cH = info["cropped"]
    l, t, r, b = info["box_ltrb"]
    dx, dy = info["dpi"]

    print(f"\n=== auto_crop report ===")
    print(f"  Original :  {W} × {H} px  ({W/dx*72.27:.0f} × {H/dy*72.27:.0f} pt @ {dx:.0f} dpi)")
    print(f"  Crop box :  left={l}  top={t}  right={r}  bottom={b}")
    print(f"  Removed  :  {info['removed'][0]}px left/right, {info['removed'][1]}px top/bottom")
    print(f"  Cropped  :  {cW} × {cH} px  ({info['nat_pt_w']:.0f} × {info['nat_pt_h']:.0f} pt)")
    print(f"  AR before:  {info['ar_before']:.3f}   AR after: {info['ar_after']:.3f}")

    # Ideal scale estimates (cap-height ≈ row_height × 0.65, row_height ≈ image_height / ~12)
    # Better: use OCR-derived cap ~35pt as baseline when available
    cap_pt_natural = 35.5   # OCR-measured for paper_table1_main.png
    textwidth_pt   = 398.3  # Beamer 169 \textwidth
    textheight_avail_pt = 144.0  # \textheight - 1.8cm (worst case, no bottom block)

    scale_w = textwidth_pt   / info["nat_pt_w"]
    scale_h = textheight_avail_pt / info["nat_pt_h"]
    actual_scale = min(scale_w, scale_h)

    cap_rendered = cap_pt_natural * actual_scale
    print(f"\n  --- Scale if used in S17 slide (no bottom text block) ---")
    print(f"  fit-to-width  scale : {scale_w:.1%}  (binding? {'YES' if scale_w <= scale_h else 'no'})")
    print(f"  fit-to-height scale : {scale_h:.1%}  (binding? {'YES' if scale_h <= scale_w else 'no'})")
    print(f"  Actual rendering    : {actual_scale:.1%}")
    print(f"  Cap height rendered : {cap_rendered:.1f} pt   (≥7 for PDF, ≥11 for screen)")
    if cap_rendered >= 11:
        verdict = "✓ SCREEN-READABLE"
    elif cap_rendered >= 7:
        verdict = "✓ PDF-READABLE (tight for projection)"
    else:
        verdict = "✗ TOO SMALL"
    print(f"  Verdict             : {verdict}")

    if not dryrun:
        print(f"\n  Saved to: {info['output']}")


def main():
    parser = argparse.ArgumentParser(description="Auto-crop white margins from an image.")
    parser.add_argument("input",               help="Input image path")
    parser.add_argument("output",  nargs="?",  help="Output image path (default: <stem>_cropped.<ext>)")
    parser.add_argument("--threshold", type=int, default=245,
                        help="Pixels with all channels >= threshold are background (default 245)")
    parser.add_argument("--padding",   type=int, default=5,
                        help="Extra pixels to keep around content box (default 5)")
    parser.add_argument("--dryrun",    action="store_true",
                        help="Print crop region only, don't write output file")
    args = parser.parse_args()

    _, info = auto_crop(
        args.input,
        output_path=args.output,
        threshold=args.threshold,
        padding=args.padding,
        dryrun=args.dryrun,
    )
    print_report(info, dryrun=args.dryrun)


if __name__ == "__main__":
    main()
