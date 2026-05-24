# Memory Index — Beamer Deck Auto

> This file provides a **structured lookup table** for agents to quickly locate relevant context across all memory scopes.
> 
> **Rule**: Before planning or executing any task, search this index for matching keywords.

---

## Quick Lookup Table

| Keyword Pattern | Memory File | Relevant Section | Priority |
|-----------------|-------------|------------------|----------|
| `theme`, `color`, `palette`, `teal`, `academic`, `dark` | `repo/user-preferences.md` | Theme Preference | P0 |
| `box`, `block`, `infoblock`, `alertblock`, `resultblock`, `card` | `repo/user-preferences.md` | Box/Block Philosophy (CRITICAL) | P0 |
| `layout`, `column`, `twocol`, `imgtop`, `equal height` | `repo/user-preferences.md` | Layout Preference | P0 |
| `mentor deck`, `self-study`, `exercise`, `example`, `worked` | `repo/user-preferences.md` | Content Density (Mentor Deck 标准) | P0 |
| `optimal transport`, `OT`, `Villani`, `coupling`, `Monge` | `repo/user-preferences.md` | Book Decks — Villani | P0 |
| `pushforward`, `推前`, `measure`, `测度` | `repo/user-preferences.md` | Reader Cognitive Baseline | P1 |
| `chapter 1`, `ch1`, `coupling`, `变量替换` | `repo/user-preferences.md` | OT Chapter 1 内容补充阶梯 | P0 |
| `planner`, `plan`, `design`, `architecture` | `repo/user-preferences.md` | Workflow Preference | P1 |
| `compile`, `build`, `xelatex`, `error` | `repo/user-preferences.md` | (none — see CLAUDE.md Build Commands) | P2 |
| `template-lib`, `component`, `layout-*.sty` | `repo/user-preferences.md` | (none — see CLAUDE.md Three-Tier Architecture) | P2 |

---

## Memory Scopes

### `/memories/repo/` — Repository Memory
**What**: Codebase conventions, build commands, project structure, user preferences  
**When to read**: Every task  
**Key files**:
- `user-preferences.md` — **MUST READ** before any design/plan decision
- `MEMORY_INDEX.md` — This file; use for quick keyword lookup

### `/memories/session/` — Session Memory  
**What**: Task-specific context, in-progress notes, temporary working state  
**When to read**: When continuing a multi-turn task  
**Key files**: Created per-session, cleared after conversation ends

### `/memories/` — User Memory  
**What**: Persistent preferences across all workspaces and conversations  
**When to read**: For cross-project patterns, frequently used commands  
**Key files**: Global user habits, not project-specific

---

## Agent Workflow — Memory Integration

### Phase 1: Plan (MANDATORY)

```
BEFORE generating any plan:
1. Read MEMORY_INDEX.md (this file)
2. Search for keywords matching the user's request
3. Read the identified memory file(s)
4. Incorporate constraints into the plan
```

### Phase 2: Execute

```
BEFORE each edit/create operation:
1. Check if the operation violates any CRITICAL preference
2. Reference existing similar implementations in the codebase
3. Follow established naming conventions and patterns
```

### Phase 3: Review

```
AFTER completing changes:
1. Verify compliance with preference rules
2. Check for consistency with existing codebase patterns
3. Update session memory with decisions made
```

---

## Keyword Matching Rules

| Match Type | Example | Action |
|------------|---------|--------|
| Exact keyword | "teal theme" → `theme` | Read Theme Preference section |
| Partial match | "infoblock color" → `box`, `block` | Read Box/Block Philosophy |
| Context inference | "self-study slides" → `mentor deck` | Read Content Density + Mentor Deck sections |
| Multi-keyword | "OT chapter 1 exercises" → `OT` + `chapter 1` | Read both Book Decks + 补充阶梯 sections |

---

## Priority Legend

| Priority | Meaning | Action |
|----------|---------|--------|
| **P0** | Critical — must read before planning | Block and read immediately |
| **P1** | Important — should read for context | Read if task is relevant |
| **P2** | Reference — read if needed | Read on demand |

---

## Last Updated

- 2026-05-24: Created MEMORY_INDEX.md with keyword lookup table
