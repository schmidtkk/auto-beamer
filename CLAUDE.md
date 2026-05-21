# CvG-Diff Beamer Deck — Project Context

**Project:** CvG-Diff MICCAI 2025 XeLaTeX Beamer Deck  
**Theme:** Academic (navy + red, classic style)  
**Build:** XeLaTeX + Metropolis theme  
**Main source:** `cvgdiff-beamer.tex`  
**Config:** `config.tex` (box macros + theme palettes)  
**Build script:** `build_clean.ps1`

---

## Box Environments (from config.tex)

| Environment | Purpose | Colors |
|-------------|---------|--------|
| `bluecard{title}` | Primary info block | ThemePrimary frame + ThemeTint bg |
| `goldcall` | Alert / key takeaway | ThemeAccent frame + ThemeAccentLight bg |
| `eqbox{title}` | Equations / definitions | ThemePrimary!50 frame + ThemeSurface bg |
| `greencard{title}` | Positive result | PosGreen frame |
| `alertcard{title}` | Warning / limitation | NegRed frame |

All boxes accept optional `[...]` tcolorbox parameters before the title.

---

## Column Height Alignment Rule

### When `equal height group` Works vs. Hardcode

| Context | `equal height group` | Action |
|---------|---------------------|--------|
| Standalone frame, no shrink | ✅ Works after 2 passes | Can use group OR hardcode |
| Frame with `[shrink=N]` | ❌ Fails | **Must hardcode** |
| Inside `\budgetwideimg` / `\budgetwidecontent` | ❌ Fails (inside `\sbox`) | **Must hardcode** |

### Why `equal height group` Fails in Some Contexts

1. **`\sbox` context** (`\budgetwideimg`, `\budgetwidecontent`): tcolorbox writes height info to `.aux` at shipout time, but `\sbox` prevents shipout → no height recorded → group fails.
2. **`[shrink=N]` frames**: Beamer's shrink mechanism rescales the entire frame after typesetting, but `equal height group` heights are computed pre-shrink → mismatch.

### Hardcoding Procedure (always use this)

1. Add `equal height group=TMP` to both boxes (temporary, for measurement only)
2. Build 2 passes: `xelatex ...` × 2
3. Read height: `Select-String "TMP" build\cvgdiff-beamer.aux`
4. Replace with `height=XX.XXXXXpt,valign=top` on BOTH boxes
5. Rebuild and verify

---

## Height Hardcoding Record

| Frame | PDF Page | Context | Box A | Box B | Height Used |
|-------|----------|---------|-------|-------|-------------|
| S3 Radon/FBP | p3 | `[shrink=5]` frame | eqbox "Radon" | eqbox "FBP" | `67.42996pt` |
| S4 稀疏视图 | p4 | `\budgetwidecontent` | bluecard "动机" | bluecard "挑战" | `71.06035pt` |
| S6b 背景扩散 | p7 | `\budgetwideimg` | bluecard "核心思想" | bluecard "代表工作" | `71.40608pt` |
| S8 Cold Diffusion | p10 | Standalone, 2 rows | Row 1: eqbox+bluecard | Row 2: eqbox+bluecard | R1: `61.99364pt`, R2: `75.90117pt` |
| S14 SPDPS | p15 | `\budgetwideimg` | bluecard "Phase 1" | bluecard "Phase 2" | `54.25087pt` (measured, hardcode recommended) |
| S16b 消融解读 | p20 | Standalone frame | bluecard "18-view PSNR" | bluecard "物理解释" | `86.83221pt` |

### Active `equal height group` Entries (current build)

| Group | Frame | Boxes | Resolved Height |
|-------|-------|-------|-----------------|
| `S12top` | S12 EPCT 2/2 | eqbox "Restore Loss" ↔ bluecard "为什么有效？" | `61.43942pt` |
| `S12bot` | S12 EPCT 2/2 | eqbox "Compose Loss" ↔ bluecard "消融验证" | `62.71098pt` |
| `S13top` | S13 顺序采样 | bluecard "①语义错误" ↔ bluecard "核心观察" | `75.03171pt` |
| `S13bot` | S13 顺序采样 | bluecard "②NFE浪费" ↔ goldcall "SPDPS动机" | `70.18864pt` |
| `S14` | S14 SPDPS | bluecard "Phase 1" ↔ bluecard "Phase 2" | `54.25087pt` (inside `\sbox` — may need hardcode) |

---

## Layout Helpers

### `\budgetwideimg{caption}{bottom-block}{imagefile}`

Convenience wrapper for IMAGE_TOP layout:
- Image fills top, auto-capped by remaining height
- Caption below image
- Bottom block (cards, text) at frame bottom
- **Inside `\sbox`**: `equal height group` does NOT work → hardcode heights

### `\budgetwidecontent{top-visual}{caption}{bottom-block}`

General IMAGE_TOP helper for multi-image grids, tables, custom visuals.
- Use `\bbiAvailHt` as height cap in grids
- **Inside `\sbox`**: `equal height group` does NOT work → hardcode heights

### `\autoimg[opts]{file}`

Fill column width, cap at 76% frame height. Use inside columns.

### `\scaleeq{math}`

Scales a display equation to fit `\linewidth`. Use inside narrow columns.

---

## Custom Commands

| Command | Purpose |
|---------|---------|
| `\deltapos{+X dB}` | Green bold positive delta |
| `\deltaneg{$-$X dB}` | Red bold negative delta |
| `\cnum{①}` | CJK number in non-CJK font |
| `\thetaEMA` | `\theta^{\mathrm{EMA}}` shorthand |
| `\hlrow` | Highlight row color (ThemeLight) |

---

## File Locations

| File | Path |
|------|------|
| Main source | `cvgdiff-beamer.tex` |
| Box macros + theme | `config.tex` |
| Build script | `build_clean.ps1` |
| Assets | `slides_assets/` |
| Backup | `cvgdiff-beamer.tex.bak.20260520` |

---

## Build Command

```powershell
# From project root
xelatex -interaction=nonstopmode -output-directory=build cvgdiff-beamer.tex
```

Run **twice** when using `equal height group` (first pass writes .aux, second pass reads it).

---

## Pending Work (from HANDOFF.md)

See `HANDOFF.md` for detailed user-requested fixes and troubleshooting notes.
