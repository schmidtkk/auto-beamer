---
name: autobeamer-video
description: "Turn deck/math content into animated GIFs and narrated Chinese short videos (ManimCE + the local TTS lab / CosyVoice3 + ffmpeg)."
when_to_use: |
  Use when making a math-demonstration GIF or a narrated 教学短视频 from existing deck math
  (e.g. optimal transport). Triggers: manim, 数学动画, 教学短视频, demo gif, narrated video, 配音/旁白.
  Do NOT trigger on compiling decks (use autobeamer-build) or authoring decks (use autobeamer-create).
argument-hint: "video [topic] — scaffold a Manim scene + Chinese narration and render"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob", "Agent", "AskUserQuestion"]
---

# AutoBeamer Video — Math GIFs & narrated short videos

Animate the math from the deck library (e.g. `slides_assets/ot/sec4-displacement.tex`) into
**looping GIFs** and **narrated Chinese short videos**. Engine split:

- **Manim Community** renders the math (smooth, 3Blue1Brown-style). This is the visual.
- **The local TTS lab** (`/data/weidong/TTS`) synthesizes Chinese narration — default voice
  **CosyVoice3** (Apache-2.0, best Chinese, commercial-safe).
- **ffmpeg** muxes narration onto the timed animation.

Working templates already live in **`/data/weidong/auto-beamer/manim-demos/`** — this skill
teaches you to copy and adapt them, and documents the env + the traps. Do NOT rebuild from scratch.

## The 3-step workflow

1. **Animate (silent).** Write a Manim `Scene` mirroring the deck's math; verify visuals.
   → [references/manim-pipeline.md](references/manim-pipeline.md)
2. **Narrate (offline).** Generate Chinese narration per beat with CosyVoice3; get `durations.json`.
   → [references/narration-tts.md](references/narration-tts.md)
3. **Mux.** Render a beat-timed scene (durations from step 2) → ffmpeg muxes the audio.

```bash
# silent GIF/mp4 (step 1)
cd /data/weidong/auto-beamer/manim-demos
conda run -n manimdemo manim -qh --media_dir media ot_displacement.py OTDisplacement
conda run -n manimdemo manim -qm --format=gif --media_dir media ot_displacement.py OTDisplacement
# narrated (steps 2–3)
/home/weidongguo/miniconda3/envs/cosyvoice/bin/python gen_narration.py      # → voiceover_audio/*.wav + durations.json
conda run -n manimdemo manim -qh --media_dir media ot_displacement_voiced.py OTDisplacementVoiced
ffmpeg -y -i media/videos/.../OTDisplacementVoiced.mp4 -i voiceover_audio/sample_all.wav \
       -c:v copy -c:a aac -shortest out/ot_displacement_cosyvoice.mp4
```

## Environment prerequisites (check first)

| Need | Check | Fix |
|------|-------|-----|
| Manim env `manimdemo` | `conda run -n manimdemo manim --version` | see [manim-pipeline.md](references/manim-pipeline.md) (conda-forge cairo/pango, `setuptools<81`) |
| 中文 font for Manim | `fc-list | grep -i "source han serif sc"` | symlink `auto-beamer/.fonts/*.otf → ~/.fonts` + `fc-cache` |
| `ffmpeg` / `latex` / `dvisvgm` | `command -v ffmpeg latex dvisvgm` | system-provided (present on this host) |
| TTS (CosyVoice3) | `ls /home/weidongguo/miniconda3/envs/cosyvoice/bin/python` | run via that python directly (NOT `conda run`) |
| GPU headroom | `nvidia-smi --query-gpu=memory.free --format=csv` | pin `CUDA_VISIBLE_DEVICES` to the freer GPU |

## Make a new topic (套模板)

1. `cp manim-demos/ot_displacement.py manim-demos/<topic>.py`; edit the `plot` functions, labels,
   and takeaway to the new math. Keep `Text(font="Source Han Serif SC")` for 中文 and `MathTex`
   for formulas. Render silent first (`-s` for a fast last-frame check).
2. For narration: copy `gen_narration.py`, replace `SEGS` with the new Chinese script; run it with
   the cosyvoice python; copy `ot_displacement_voiced.py` and re-time the beats to the new
   `durations.json`; mux.
3. `bash manim-demos/make_video.sh <topic>.py <Scene>` renders mp4 + gif into `out/`.

Good next OT animations: Monge/Kantorovich geometry (splittable vs not), Wasserstein geodesic,
Ch.8 "uncrossing lowers cost."

## Reference index

| Need | Doc |
|------|-----|
| Manim env, fonts, scene pattern, render flags | [references/manim-pipeline.md](references/manim-pipeline.md) |
| Chinese narration: the TTS lab, CosyVoice3, offline-gen + mux, **voice selection table** | [references/narration-tts.md](references/narration-tts.md) |
| Alternatives: **HyperFrames** packaging, **Beamer→GIF** (no Manim) | [references/alternatives.md](references/alternatives.md) |
| **Traps**: exit-144/SIGURG, blocked `sleep`, cosyvoice env, MOSS broken, GPU | [references/gotchas.md](references/gotchas.md) |
| The deck source of truth for OT math | `../../slides_assets/ot/sec4-displacement.tex` |
| Build/compile the decks · author the decks | [autobeamer-build](../autobeamer-build/SKILL.md) · [autobeamer-create](../autobeamer-create/SKILL.md) |
