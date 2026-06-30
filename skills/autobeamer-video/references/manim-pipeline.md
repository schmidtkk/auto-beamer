# Manim pipeline — env, fonts, scene pattern, rendering

The visual layer. ManimCE renders math animations to mp4/gif. Keep it isolated from
`auto-beamer/.venv` (uv, minimal) and from the conda TTS envs.

## Environment (`manimdemo` conda env — one-time)

Cairo/Pango are **missing system-wide** here and need root to apt-install. Get them from
**conda-forge instead** (no root):

```bash
conda create -y -n manimdemo -c conda-forge python=3.11 pycairo manimpango ffmpeg pkg-config
conda run -n manimdemo pip install manim manim-voiceover requests "setuptools<81"
conda run -n manimdemo manim --version          # → Manim Community v0.20.x
```

- **`setuptools<81` is required.** Newer setuptools dropped `pkg_resources`; Manim (and deps)
  import it, so a bare install fails with `No module named 'pkg_resources'`. Pin `<81`.
- `ffmpeg`, `latex`/`xelatex`, `dvisvgm` are present on the host (MathTex needs latex+dvisvgm).
- The "SoX … double-check your path variables" banner on import is harmless noise.

## Chinese fonts (Pango / fontconfig)

`Text(...)` renders via Pango, which finds fonts through **fontconfig** — the `.fonts/` files are
not auto-registered. Register them once (symlink, no 175 MB copy):

```bash
mkdir -p ~/.fonts
ln -sf /data/weidong/auto-beamer/.fonts/SourceHanSerifSC-*.otf ~/.fonts/
fc-cache -f ~/.fonts
fc-list | grep -i "source han serif sc"          # must print the family
```

Then in scenes: `Text("最优传输", font="Source Han Serif SC")` for 中文; `MathTex(r"\mu_t")` for
formulas (pure LaTeX — keep Chinese OUT of MathTex). Greek + sub/superscripts inside `Text`
(μ₀, σₜ²) render fine with Source Han.

## Scene pattern (copy `manim-demos/ot_displacement.py`)

The proven recipe for "a quantity morphing over time":

- A `ValueTracker` `t` drives the animation; `always_redraw(lambda: axes.plot(lambda x: f(x, t.get_value()), ...))`
  redraws curves each frame.
- Two stacked `Axes` panels (teal `#00796b` / orange `#e65100` to match the deck palette), each
  with `get_area(...)` fill + ghost end-state curves for reference.
- Drive the story with `self.play(t.animate.set_value(1.0), run_time=..., rate_func=smooth)`.
- `ot_displacement.py` mirrors `slides_assets/ot/sec4-displacement.tex` exactly: linear interp
  `(1−t)μ₀+t·μ₁` (goes bimodal) vs displacement `μ_t=N(m_t,σ_t²)` with `m_t=(1−t)m₀+t·m₁`,
  `σ_t=(1−t)σ₀+t·σ₁` (single bump translating). Keep new topics consistent with their deck math.

## Rendering

```bash
cd /data/weidong/auto-beamer/manim-demos
conda run -n manimdemo manim -s  --media_dir media file.py Scene   # FAST: last frame → PNG (font/layout check)
conda run -n manimdemo manim -qm --media_dir media file.py Scene   # 720p mp4
conda run -n manimdemo manim -qh --media_dir media file.py Scene   # 1080p mp4
conda run -n manimdemo manim -qm --format=gif --media_dir media file.py Scene   # looping GIF
```

Output lands in `media/videos/<file>/<res>/Scene.mp4` (and `media/images/.../Scene_*.png` for `-s`).
Always do `-s` first to catch tofu/overflow cheaply before a full render. `make_video.sh` wraps
mp4+gif and copies to `out/`.
