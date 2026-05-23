# Image Scale Reference Tables

## Scale Calculation

```python
# fit-to-width  scale = 398 / img_width_pt
# fit-to-height scale = bbiAvailHt / img_height_pt
# Rendered scale = min(fit-to-width, fit-to-height)
```

## Scale Thresholds

| Scale | Verdict | Action |
|-------|---------|--------|
| ≥ 0.20 | ✓ OK | Text readable |
| < 0.20, height-binding | ⚠ Too small | Crop margins, remove bottom block, or switch layout |
| < 0.20, **width-binding** | ✗ Cannot fix | **Typeset as LaTeX `tabular`** |

## Cap-Height Readability

| Cap Height | Verdict |
|------------|---------|
| ≥ 11 pt | Screen-readable |
| ≥ 7 pt | PDF-readable |
| < 7 pt | **Too small** — must re-typeset |

## Auto-Crop Workflow

```bash
# Preview scale after crop
python tools/auto_crop.py input.png --dryrun

# Execute crop
python tools/auto_crop.py input.png output.png --padding 8
```
