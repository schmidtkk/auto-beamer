# AutoBeamer Skill Framework Evidence Inventory

Date: 2026-06-04

Scope: evidence gathered for an adversarial review of the current AutoBeamer
skill framework, with emphasis on three learning modes: passive study, active
Socratic study, and academic presentation.

## External Best-Practice Evidence

### Local skill-creator guidance

- Skills should provide specialized workflows, tool integrations, domain
  expertise, and bundled resources (`skill-creator/SKILL.md:14-24`).
- The skill body should stay concise because the context window is shared
  (`skill-creator/SKILL.md:28-34`).
- Fragile operations should use low-freedom scripts, while variable tasks should
  use higher-freedom guidance (`skill-creator/SKILL.md:36-46`).
- `agents/openai.yaml` is recommended for UI-facing metadata and default prompts
  (`skill-creator/SKILL.md:56-90`).
- References, scripts, and assets are the intended progressive-disclosure
  mechanism (`skill-creator/SKILL.md:92-121`).
- When a skill supports multiple variants, variant-specific details should move
  into separate reference files (`skill-creator/SKILL.md:135-147`).

### shanraisshan/claude-code-best-practice

- Skill frontmatter supports trigger fields such as `description`,
  `when_to_use`, `paths`, `context: fork`, and `agent`
  (`best-practice/claude-skills.md:17-36`).
- The repo highlights `run` and `verify` skills as project-specific correctness
  gates, not just tests (`best-practice/claude-skills.md:50-52`).
- The README emphasizes that skill descriptions are trigger surfaces, not
  summaries, and that skills should focus on what changes model behavior
  (`README.md:270-281`).
- The README recommends progressive disclosure via folders such as
  `references/`, `scripts/`, and examples (`README.md:274-281`).
- Memory guidance argues for context optimization via root instructions and
  lazily loaded component-specific instructions (`best-practice/claude-memory.md:89-113`).
- The orchestration example separates command, agent, and skill responsibilities
  (`orchestration-workflow.md:12-29`).

### affaan-m/ECC

- ECC frames itself as a harness-native system spanning skills, memory,
  verification, security, and cross-harness workflows (`README.md:37-43`).
- ECC foregrounds token optimization, memory persistence, verification loops,
  parallelization, and subagent orchestration (`README.md:110-118`).
- ECC's Codex guidance expects each skill to include `SKILL.md` plus
  `agents/openai.yaml` metadata (`.codex/AGENTS.md:14-19`).
- ECC preserves user config in managed merges and warns on drift instead of
  overwriting blindly (`.codex/AGENTS.md:51-61`).
- ECC treats networked tools as read-only by default and requires explicit
  approval for external state changes (`.codex/AGENTS.md:63-67`).
- ECC's Codex plugin manifest exposes skills through one shared source of truth
  and rich interface metadata (`.codex-plugin/plugin.json:169-204`).

## Local Framework Evidence

### Packaging and discovery

- AutoBeamer has Codex and Claude plugin manifests, both pointing to
  `./skills/` (`.codex-plugin/plugin.json:23`, `.claude-plugin/plugin.json:23`).
- Plugin default prompts mention generic research-paper deck creation and layout
  help only (`.codex-plugin/plugin.json:35-38`,
  `.claude-plugin/plugin.json:34-37`).
- No `agents/openai.yaml` files exist under `skills/`, even though both
  skill-creator guidance and ECC recommend them.
- The six skill files are:
  `autobeamer-build`, `autobeamer-create`, `autobeamer-layout`,
  `autobeamer-review`, `autobeamer-tikz`, and `autobeamer-validate`.

### Current mode taxonomy

- `autobeamer-create` asks for only two deck modes: Presentation or Mentor
  (`skills/autobeamer-create/SKILL.md:56-59`).
- `CLAUDE.md` also defines only Presentation Deck vs Mentor Deck
  (`CLAUDE.md:233-253`).
- `AGENTS.md` requires an explicit deck mode, but the choices remain
  Presentation vs Mentor (`AGENTS.md:152`).
- Searches for passive study, active Socratic study, and academic presentation
  do not reveal a first-class mode taxonomy in the current skill framework.
- Review and validation skills still evaluate Presentation/Mentor, not all
  three requested modes (`skills/autobeamer-layout/SKILL.md:189-201`,
  `skills/autobeamer-validate/SKILL.md:94-99`).

### Creation and review behavior

- `autobeamer-create` is a monolithic 584-line skill that mixes mode selection,
  mathematical pedagogy, textbook handling, table rules, figure rules,
  validation, and scoring.
- `autobeamer-review` provides proofread, audit, pedagogy, excellence, and
  devils-advocate actions, but no mode-specific review path for passive,
  active Socratic, or academic presentation modes
  (`skills/autobeamer-review/SKILL.md:21-30`).
- The excellence review says to run three perspectives, but then collapses them
  into one agent reviewing all three (`skills/autobeamer-review/SKILL.md:238-248`).

### Constraint drift

- `AGENTS.md` caps colored boxes at three per slide for all Beamer work
  (`AGENTS.md:129`).
- `autobeamer-create` allows Mentor mode to use up to five blocks per slide
  (`skills/autobeamer-create/SKILL.md:73`, `:337-343`).
- `autobeamer-layout` also allows Mentor mode up to five blocks
  (`skills/autobeamer-layout/SKILL.md:196-201`).
- `CLAUDE.md` says new decks should use `template-lib` commands while legacy
  decks retain old `config.tex` commands (`CLAUDE.md:152-167`).
- `autobeamer-layout`, `autobeamer-review`, and `autobeamer-validate` still
  prescribe legacy macros such as `goldcall`, `bluecard`, and `eqbox`
  (`skills/autobeamer-layout/SKILL.md:121-126`,
  `skills/autobeamer-review/SKILL.md:141-143`,
  `skills/autobeamer-validate/SKILL.md:118`).

### Validation and verification risks

- `autobeamer-validate` compiles `.tex` input once, while build guidance says
  manual compilation should run twice for layout/cross-reference stability
  (`skills/autobeamer-validate/SKILL.md:25-31`,
  `skills/autobeamer-build/SKILL.md:57-60`).
- `autobeamer-validate` labels `364.19 x 272.65 pts` as 16:9 despite the ratio
  being about 1.336 (`skills/autobeamer-validate/SKILL.md:54-61`).
- The overlay grep checks `pause`, `onslide`, and `only`, but omits `uncover`
  even though `AGENTS.md` bans all four (`skills/autobeamer-validate/SKILL.md:113-116`,
  `AGENTS.md:128`).
- Visual checking is marked mandatory and correctly acknowledges that block
  overflow can be invisible in logs (`skills/autobeamer-validate/SKILL.md:166-236`).

### Image and figure sourcing

- `paper_parser.py` is already designed to extract text, images, and structural
  metadata from a PDF paper (`tools/paper_parser.py:3-17`).
- The parser extracts embedded images, skips likely icons/logos by minimum size,
  writes PNGs, and records page, dimensions, aspect ratio, and xref
  (`tools/paper_parser.py:265-322`).
- The full parse command includes image extraction and records source PDF,
  sections, extracted images, full text, and page texts
  (`tools/paper_parser.py:359-405`).
- `autobeamer-create` still recommends checking external sources such as POT,
  Wikimedia Commons, arXiv paper figures, and standard textbook illustrations
  for pure math visuals (`skills/autobeamer-create/SKILL.md:159-166`).
- Current skills do not define a precedence rule such as:
  source-document figures first, rendered page crops second, custom TikZ third,
  external images only with explicit citation and necessity.

## Evidence-Based Review Targets

1. Mode routing: current two-mode taxonomy is not aligned with the requested
   passive, active Socratic, and academic presentation modes.
2. Review parity: review and validation do not currently apply the requested
   learning modes.
3. Progressive disclosure: mode policy should move out of the monolithic create
   skill into mode-specific references.
4. Deterministic verification: validation needs stronger static checks and
   accurate aspect-ratio logic.
5. Figure fidelity: creation should prefer extracted source-document images
   before external web/CDN image sourcing.
6. Packaging: plugin metadata should expose the three modes and include
   per-skill UI metadata where the harness supports it.
