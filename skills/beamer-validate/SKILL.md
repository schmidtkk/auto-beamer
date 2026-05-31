---
name: beamer-validate
description: |
  Use when running automated quantitative checks on a compiled Beamer deck.
  Triggers on: "validate", "validation", "check deck", "visual check",
  "pdf check", "slide count", "aspect ratio", "compilation health".
  Performs measurable property checks and PDF visual verification.
  Do NOT trigger on: content review (use beamer-review), layout optimization (use beamer-layout).
argument-hint: "validate [deck.tex|deck.pdf] [duration] — run automated checks"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
---

# Beamer Validate — Automated Checks

> **For content proofreading**, see [beamer-review](../beamer-review/SKILL.md).
> **For layout optimization**, see [beamer-layout](../beamer-layout/SKILL.md).
> **For build/compile errors**, see [beamer-build](../beamer-build/SKILL.md).

---

## Action: `validate [file] [duration]`

Automated quantitative validation. Checks measurable properties without reading content.

### Step 1: Compile (if .tex provided)

```bash
xelatex -interaction=nonstopmode -output-directory=build FILE.tex
```

If the file is already a `.pdf`, skip to Step 2.

### Step 2: Run All Checks

#### 2a. Slide Count vs. Duration

```bash
# Get page count
pdfinfo build/FILE.pdf 2>/dev/null | grep "Pages:"
```

| Duration | Recommended Slides |
|----------|--------------------|
| 5 min | 4–6 |
| 10 min | 7–12 |
| 15 min | 11–16 |
| 20 min | 14–20 |
| 30 min | 20–28 |
| 45 min | 28–38 |
| 60 min | 35–50 |

Flag if actual count is outside ±3 of recommended range.

#### 2b. Aspect Ratio

```bash
pdfinfo build/FILE.pdf | grep "Page size:"
```

Expected for 16:9 at 10pt: **364.19 × 272.65 pts** (ratio ≈ 1.336).
Any ratio outside 1.30–1.37 → WARNING.

#### 2c. File Size

| Size | Verdict |
|------|---------|
| < 20 MB | OK |
| 20–50 MB | INFO |
| 50–100 MB | WARNING |
| > 100 MB | CRITICAL |

#### 2d. Compilation Health (from .log)

```bash
grep -c "Overfull \\\\hbox" build/FILE.log
grep -c "Undefined control sequence" build/FILE.log
grep -c "Citation.*undefined" build/FILE.log
grep -c "multiply defined" build/FILE.log
```

| Warning Type | OK | WARNING | CRITICAL |
|-------------|-----|---------|----------|
| Overfull hbox | 0 | 1–3 | 4+ |
| Undefined control sequence | 0 | — | 1+ |
| Undefined citations | 0 | 1–2 | 3+ |
| Multiply defined labels | 0 | — | 1+ |

#### 2f. Layout Audit (mandatory — run tool)

```bash
python tools/check_layout.py deck.tex build/deck.log --advise
```

| Metric | Presentation OK | Mentor OK | Action if fail |
|--------|----------------|-----------|----------------|
| U (utilization) | [0.80, 0.95] | [0.75, 0.98] | < 0.60 → sparse, merge; > 1.00 → overflow, split |
| B (balance) | > 0.80 | > 0.70 | Rebalance columns |
| G (gravity) | < 0.15 | < 0.20 | Adjust vertical spacing |
| DGV | 0 | 0 | Fix grammar violations |

#### 2g. Sparse Slide Detection (from .tex source)

For each `\begin{frame}` block, count substantive elements (formulas `\[`, diagrams `\begin{tikzpicture}`, tables `\begin{tabular}`, theorems `\begin{theorem}`, algorithms `\begin{algorithm}`).

| Frame type | Critical threshold |
|-----------|-------------------|
| Single `\TLtakeaway` or `\TLinfoblock` with no math/diagram/table | **CRITICAL** — must merge or enrich |
| ≤ 2 short text bullets, no math | **CRITICAL** — must merge or enrich |
| Only text + citations, no substantive element | **WARNING** — consider enriching |

#### 2e. Source Code Static Checks (from .tex)

```bash
# Overlay commands (must be 0 — our Hard Rule)
grep -c "\\\\pause\|\\\\onslide\|\\\\only" FILE.tex

# Box fatigue (>2 colored boxes on one slide)
grep -n "begin{bluecard}\|begin{eqbox}\|begin{greencard}\|begin{alertcard}\|begin{goldcall}" FILE.tex

# Font size abuse
grep -c "\\\\tiny" FILE.tex

# References slide
grep -c "begin{thebibliography}\|\\\\bibliography" FILE.tex
```

| Check | Pass Condition |
|-------|---------------|
| Overlay commands (`\pause`, `\onslide`, `\only`) | 0 found |
| Slides with >3 colored boxes | 0 slides |
| `\tiny` usage | 0 found |
| References section | Present |

### Step 3: Generate Report

```
# Validation Report: [Filename]

| Check | Result | Status |
|-------|--------|--------|
| Slide count | N slides / Xmin duration | OK / WARNING |
| Aspect ratio | 16:9 (ratio) | OK / WARNING |
| File size | X.X MB | OK / WARNING / CRITICAL |
| Overfull hbox | N warnings | OK / WARNING / CRITICAL |
| Undefined references | N | OK / CRITICAL |
| Overlay commands | N found | OK / VIOLATION |
| Box fatigue violations | N slides | OK / WARNING |
| Font abuse (\tiny) | N found | OK / VIOLATION |
| References slide | Present / Missing | OK / WARNING |
| **Layout audit (U/B/G/DGV)** | U=X, B=X, G=X, DGV=X | OK / WARNING / CRITICAL |
| **Sparse slides** | N frames < 0.60 utilization | OK / CRITICAL |

Overall: PASS / PASS WITH WARNINGS / FAIL
```

### Verdict Criteria

| Verdict | Condition |
|---------|-----------|
| **PASS** | Zero CRITICAL, zero VIOLATION |
| **PASS WITH WARNINGS** | Warnings present but no CRITICAL or VIOLATION |
| **FAIL** | Any CRITICAL or VIOLATION |

---

## Action: `visual-check [file]` (MANDATORY)

PDF-based visual verification. **This step is NOT optional.** Beamer suppresses overfull warnings inside blocks — only visual inspection catches block-interior overflow and sparse slides.

**When to run:** After every compile, before declaring validation PASS.

### Step 1: Convert PDF to Images

```powershell
# Windows (pdftoppm from poppler)
pdftoppm -jpeg -r 200 build\FILE.pdf _slides_png\slide
```

```bash
# Linux/macOS
pdftoppm -jpeg -r 200 build/FILE.pdf _slides_png/slide
```

Fallback if `pdftoppm` unavailable: read the PDF page-by-page using the workspace viewer.

### Step 2: Per-Slide Inspection Checklist

For each generated slide image, verify:

- [ ] No text overflow at any edge
- [ ] No content overflowing inside colored boxes
- [ ] All text legible at presentation distance
- [ ] Tables and equations fit within slide width
- [ ] TikZ labels not overlapping
- [ ] Consistent font sizes across similar slide types
- [ ] Adequate contrast between text and background
- [ ] No visual clutter
- [ ] Images properly scaled (not pixelated, not oversized)
- [ ] Footer/header not overlapping content
- [ ] **No sparse slides** — each frame must have ≥1 substantive element and ≥30% vertical fill

**Sparse-slide detection heuristic:**
- If a frame contains only 1 block (e.g., `\TLtakeaway`, `\TLinfoblock`) and no math/diagram/table/theorem → flag as CRITICAL
- If a frame has large empty vertical space (>50% of slide height unused) → flag as WARNING
- For Mentor mode: also check that bibliographical notes, glossary, and exercise sections are present

### Step 3: Report Per Issue

```
### Slide N: [slide title]
- **Issue:** [description]
- **Severity:** Critical / Major / Minor
- **Fix:** [specific recommendation]
```

### Step 4: Summary

| Severity | Count | Example Slides |
|----------|-------|----------------|
| Critical | N | Slide X, Y |
| Major | N | Slide X, Y |
| Minor | N | Slide X, Y |

---

## Action: `check [file]`

Run both `validate` and `visual-check` in sequence for a complete health report.

1. Run all quantitative checks (Step 2a–2g)
2. Run `python tools/check_layout.py deck.tex build/deck.log --advise`
3. Convert PDF to images
4. Inspect each slide visually (mandatory — block overflow is invisible in logs)
5. Produce combined report

**Do NOT skip visual-check.** Overfull warnings inside Beamer blocks are suppressed by the engine; only visual inspection catches them.

---

## Integration with Our Tools

| Tool | When Used |
|------|-----------|
| `check_layout.py` | During `audit` action in beamer-review |
| `layout_optimizer.py` | During layout optimization in beamer-layout |
| `build_clean.ps1` / `build.sh` | Compilation step |
| `pdftoppm` (poppler) | PDF-to-image conversion for visual-check |

---

## Cross-References

| Need | Skill |
|------|-------|
| Content proofreading / pedagogy | [beamer-review](../beamer-review/SKILL.md) |
| Create new deck from scratch | [beamer-create](../beamer-create/SKILL.md) |
| Layout optimization, DGV grammar | [beamer-layout](../beamer-layout/SKILL.md) |
| Build errors, compilation | [beamer-build](../beamer-build/SKILL.md) |
| TikZ diagram quality | [beamer-tikz](../beamer-tikz/SKILL.md) |
