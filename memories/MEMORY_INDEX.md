# Memory Index — Beamer Deck Auto

> **Rule**: Before planning or executing any task, search this index for matching keywords.

---

## Quick Lookup Table

| Keyword Pattern | Memory File | Priority |
|-----------------|-------------|----------|
| `theme`, `color`, `palette`, `teal`, `academic`, `dark` | `repo/user-preferences.md` | P0 |
| `CJK`, `Chinese`, `中文`, `font`, `serif`, `Source Han`, `font-config` | `repo/cjk-font-setup.md` + `repo/user-preferences.md` | P0 |
| `math font`, `KpMath`, `unicode-math`, `setmathfont` | `repo/user-preferences.md` (Math Font section) | P1 |
| `box`, `block`, `infoblock`, `alertblock`, `card` | `repo/user-preferences.md` | P0 |
| `layout`, `column`, `twocol`, `imgtop`, `equal height` | `repo/user-preferences.md` | P0 |
| `mentor deck`, `self-study`, `exercise`, `example`, `worked` | `repo/user-preferences.md` | P0 |
| `optimal transport`, `OT`, `Villani`, `coupling`, `Monge` | `repo/user-preferences.md` + workspace `beamer-ot-deck-patterns` | P0 |
| `pushforward`, `推前`, `measure`, `测度` | `repo/user-preferences.md` | P1 |
| `split`, `overflow`, `overfull`, `shrink` | `repo/feedback-split-not-shrink.md` | P0 |
| `underbrace`, `brace`, `black rectangle`, `fontspec` | autobeamer-tikz skill (TikZ quality standards) | P1 |
| `compile`, `build`, `xelatex`, `error` | See CLAUDE.md Build Commands | P2 |
| `template-lib`, `component`, `layout-*.sty` | See CLAUDE.md Three-Tier Architecture | P2 |

---

## Memory Scopes

### `/memories/repo/` — Repository Memory
**What**: Codebase conventions, build commands, user preferences, feedback  
**When**: Every task  
**Key files**:
- `user-preferences.md` — MUST READ before any design/plan decision
- `cjk-font-setup.md` — Chinese font setup, auto-detection chain, math pairing
- `feedback-split-not-shrink.md` — Split vs shrink preference (CRITICAL)
- `MEMORY_INDEX.md` — This file

### Workspace project memory
**What**: Project-specific patterns (OT decks, Villani chapters)  
**Where**: `.claude/projects/.../memory/`  
**Key file**: `beamer-ot-deck-patterns.md` — OT deck structure, LaTeX pitfalls

---

## Priority Legend

| Priority | Action |
|----------|--------|
| **P0** | Block and read immediately |
| **P1** | Read if task is relevant |
| **P2** | Read on demand |

---

## Last Updated

- 2026-06-05: Added CJK font setup (Source Han Serif SC + KpMath), updated build/create skills, added `cjk-font-setup.md` memory
- 2026-06-04: Restored skill memory into the repo; fixed skill-name drift (autobeamer-*), removed a dangling memory-file row from the lookup table
- 2026-05-31: Added `feedback-split-not-shrink.md`, compacted index, added workspace memory reference
- 2026-05-24: Created MEMORY_INDEX.md
