# Alternative pipelines

Manim + local TTS (the main path) is best for *smooth, rigorous* math animation. Two alternatives
fit other needs.

## A) HyperFrames — narrated-short *packaging* (not a math renderer)

**HyperFrames** (HeyGen, Apache-2.0, "author HTML/CSS/GSAP → deterministic MP4 via headless Chrome
+ FFmpeg", with built-in **TTS voiceover + Whisper auto-captions**) is **already installed** as a
Codex plugin: `~/.codex/.tmp/plugins/plugins/hyperframes/` (skills: `hyperframes`, `hyperframes-cli`,
`gsap`, `website-to-hyperframes`). Needs Node ≥ 22 + ffmpeg (both present).

- It renders **motion graphics, not math** — use it to *wrap* Manim clips into a polished short:
  title cards, kinetic captions, transitions, intro/outro, vertical/horizontal formats.
- Driven by `npx hyperframes init | preview | tts | transcribe | render`. Author the composition in
  HTML+GSAP, embed the Manim mp4, add narration/captions.
- Chinese-adapted forks exist (`liangdabiao/hyperframes-fix`, `bbylw/hyperframes-cn`).
- **When to use:** you want a shareable, designed *teaching short* (片头/字幕/转场) on top of the
  math animation — not when you just need the raw math GIF/clip.

## B) Beamer overlay → PNG → GIF (no Manim, reuses existing decks)

For **discrete, step-by-step reveals** (formula lines appearing, a `\foreach` TikZ curve drawn
segment by segment) you don't need Manim at all — reuse the decks:

```bash
# add \only<1-3>/\onslide/\foreach steps to a deck (a SEPARATE animation variant —
# the OT deck itself bans overlays), compile, then:
pdftoppm -png -r 200 build/deck.pdf frames/f
convert -delay 60 -loop 0 frames/f-*.png out.gif                    # ImageMagick
ffmpeg -framerate 2 -pattern_type glob -i 'frames/f-*.png' -pix_fmt yuv420p out.mp4
```

- Zero install (ffmpeg/ImageMagick/pdftoppm/`animate.sty` all present); Chinese is automatic via
  `template-lib/font-config.sty`.
- **Quality:** discrete frames, not smooth tweening — fine for "reveal" teaching GIFs, not for
  continuous morphs (use Manim for those).
- Add narration the same way as the main path: generate audio offline, `ffmpeg` mux.
