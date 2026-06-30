---
description: Create a self-study problem sheet (Beamer PDF) — guided problems + weak→strong hints + gap-free answer key
argument-hint: <topic or source path> [dark] [theme=<name>]
allowed-tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob", "Agent", "AskUserQuestion", "Skill"]
---

Invoke the **autobeamer-problem-sheet** skill to build an intensive-math self-study
**problem sheet** as a XeLaTeX Beamer PDF for:

$ARGUMENTS

Follow `skills/autobeamer-problem-sheet/SKILL.md` and `references/problem-sheet-guide.md`:

1. **Intake** — confirm topic, source material, target reader, problem count, difficulty mix
   (ask only if unstated). Theme defaults to `[slatecoral]` (light) or `[rosepine]` if "dark"
   is requested; honor `theme=<name>` if given.
2. **Plan the logical chain** before any TeX (final insight → prereqs → 3–6 Parts →
   per-Part question → misconceptions).
3. **Draft** problems with `\TLprobtitle`/`\TLsubq`/`TLhints`/`\TLconcept`; figures
   source-first.
4. **Answer key** in `\appendix` — gap-free worked solutions (`\TLsoltitle`…`\TLqed`), P0.
5. **Build** (`./build.sh`), **validate** (`python3 tools/validate_deck.py static <deck>.tex
   --mode problem-sheet`), and gate the answer key with **naive-reader P2**.

Default output shape: problems + hints in the body, full solutions deferred to the answer
key ("struggle first, then check").
