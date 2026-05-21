# Template Library Catalog

## Three-Tier Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  TIER 1: THEMES (Color + Typography)                        │
│  ├─ academic    (Navy + Brick Red)                          │
│  ├─ teal        (Teal + Amber)                              │
│  ├─ dark        (Dark Mode, Catppuccin-like)                │
│  └─ navygold    (Navy + Gold)                               │
├─────────────────────────────────────────────────────────────┤
│  TIER 2: LAYOUTS (Page Structure)                           │
│  ├─ text        (Pure text flow)                            │
│  ├─ 1img        (Single image: left/right/top/bottom)       │
│  ├─ 2img        (Two images: side-by-side, labeled)         │
│  ├─ 3img        (Three images: grid, asymmetric)            │
│  ├─ eq          (Equation-focused: single, compare, deriv)  │
│  ├─ table       (Table: full-width, side-text)              │
│  ├─ imgtop      (Image-top with auto-height bottom content) │
│  └─ twocol      (Two-column text: equal, divider, pro/con)  │
├─────────────────────────────────────────────────────────────┤
│  TIER 3: COMPONENTS (Reusable Blocks)                       │
│  ├─ Title slides    (standard, centered, section)           │
│  ├─ Content blocks  (info, alert, result, warning)          │
│  ├─ Figure helpers  (auto-img, subfig, caption)             │
│  └─ Text utilities  (takeaway, term highlight, checkmarks)  │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Start

```latex
\documentclass[aspectratio=169,10pt]{beamer}
\usepackage[academic]{template-lib}
\uselayout{1img}
\uselayout{eq}

\TLsetfoot{Author · Conference 2025}

\begin{document}
\TLtitlestandard[
  paper_fancy_title.jpg
]{Title}{Subtitle}{Author}{Institute}{Date}

\begin{frame}{Single Image Layout}
  \TLoneimgleft{image.png}{
    \begin{itemize}
      \item Point 1
      \item Point 2
    \end{itemize}
  }
\end{frame}
\end{document}
```

---

## Theme Reference

| Theme | Primary | Accent | Best For |
|-------|---------|--------|----------|
| `academic` | Navy #1a3a6b | Brick #b8321a | General academic |
| `teal` | Teal #00796b | Amber #e65100 | Medical/biotech |
| `dark` | Soft Blue #8aadf4 | Gold #eed49f | Low-light venues |
| `navygold` | Navy #1a3a6b | Gold #c9a23a | Prestigious/ivy |

---

## Layout Reference

| Layout | Command | Use Case |
|--------|---------|----------|
| **text** | `\begin{TLtext}...\end{TLtext}` | Bullet points, discussion |
| **1img** | `\TLoneimgleft{img}{text}` | Figure explanation |
| **2img** | `\TLtwoimg{img1}{cap1}{img2}{cap2}` | Comparison |
| **3img** | `\TLthreeimg{...}` | Progression/grid |
| **eq** | `\TLeqsingle{eq}{note}` | Math derivation |
| **table** | `\TLtablefull{table}{cap}` | Data presentation |
| **imgtop** | `\TLimgtop{img}{cap}{bottom}` | Visual + analysis |
| **twocol** | `\TLtwocol{left}{right}` | Parallel content |

---

## Component Reference

### Title Components
| Command | Description |
|---------|-------------|
| `\TLtitlestandard[img]{title}{sub}{author}{inst}{date}` | Left text, right image |
| `\TLtitlecenter{title}{sub}{author}{date}` | Centered, no image |
| `\TLsection{Title}` | Section divider |

### Block Components
| Command | Description |
|---------|-------------|
| `\TLinfoblock{Title}{Content}` | Primary info box |
| `\TLalertblock[Title]{Content}` | Accent highlight box |
| `\TLresultblock{Title}{Content}` | Green result box |
| `\TLwarnblock{Title}{Content}` | Red warning box |
| `\TLtakeaway{Text}` | Key takeaway banner |
| `\TLterm{word}` | Inline highlighted term |

### Figure Components
| Command | Description |
|---------|-------------|
| `\TLautoimg[opts]{file}` | Auto-scale image |
| `\TLimgcap[opts]{file}{caption}` | Image + caption |
| `\TLsubfig[frac]{img1}{img2}{cap}` | Side-by-side |
| `\TLthead` | Styled table header |
| `\TLthl` | Table row highlight |

---

## File Structure

```
template-lib/
├── template-lib.sty      # Master entry point
├── themes/
│   ├── theme-academic.sty
│   ├── theme-teal.sty
│   ├── theme-dark.sty
│   └── theme-navygold.sty
├── layouts/
│   ├── layout-text.sty
│   ├── layout-1img.sty
│   ├── layout-2img.sty
│   ├── layout-3img.sty
│   ├── layout-eq.sty
│   ├── layout-table.sty
│   ├── layout-imgtop.sty
│   └── layout-twocol.sty
├── components/
│   ├── comp-title.sty
│   ├── comp-block.sty
│   └── comp-fig.sty
└── docs/
    └── CATALOG.md
```
