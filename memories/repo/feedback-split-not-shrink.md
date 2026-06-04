---
name: feedback-split-not-shrink
description: "For dense Beamer frames, prefer splitting into multiple frames over shrinking fonts or compressing content."
metadata:
  type: feedback
---

**Rule:** If a frame overflows by more than ~15pt, split it. If it overflows by less, compress spacing first. Never shrink body text below `\small` for main content.

**Why:** User said "i don't care if you use 100 or 200 pages" — readability and comfort come before page count. Shrinking fonts on proof-heavy slides makes equations illegible.

**How to apply:**
- For frames with 3+ equations + text: split into "setup" and "analysis" or "derivation" and "conclusion" frames.
- For frames with TikZ + dense text: move TikZ to its own "illustration" frame, or move text to an "explanation" frame.
- When splitting, preserve narrative flow by naming frames sequentially (e.g. Slide 8a and 8b).

**Related:** [[beamer-ot-deck-patterns]] (project memory in workspace)
