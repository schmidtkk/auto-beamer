# Gotchas (this host) — read before you fight the same trap

## Shell / process

- **`exit 144` = SIGURG (signal 16).** Long-lived **background processes get killed** by this shell
  wrapper shortly after launch — both `nohup … &` and the Bash tool's `run_in_background` mode died
  this way (a TTS *server* never stayed up reliably). **Fix:** prefer a **one-shot script that loads,
  works, and exits** (e.g. `gen_narration.py`) over a persistent server.
- **Bare foreground `sleep` is blocked** (also surfaces as exit 144). Never write `sleep 8` directly.
  **Fix:** wait via `timeout 300 bash -c 'until <COND>; do sleep 6; done'` (sleep inside the
  `bash -c` is allowed). This is how to poll for "model loaded" / "file produced".
- Keep launch commands short; avoid `pkill … ; sleep … ; nohup …` chains — they tend to 144.

## TTS

- **The `cosyvoice` env is NOT a registered conda env** (a bare dir under `miniconda3/envs/`).
  `conda run -n cosyvoice` → "not a conda environment". **Run its python directly:**
  `/home/weidongguo/miniconda3/envs/cosyvoice/bin/python`. (This is why `conda env list` doesn't show it.)
- **MOSS-TTS is broken in `tts_eval`** — `module 'transformers.processing_utils' has no attribute
  'MODALITY_TO_BASE_CLASS_MAPPING'` (transformers version mismatch vs the MOSS custom model). Use
  CosyVoice3 instead unless you set up a matching transformers env.
- **F5-TTS `zh_female`** default reference sounds bad — don't ship it. CosyVoice3 is the production voice.
- **CosyVoice3 instruct format = `"<instruction><|endofprompt|><text-to-speak>"` in ONE string**
  (see `CosyVoice/examples/.../*cosyvoice3*`: `"用四川话说<|endofprompt|>扁担长…"`). The part before
  `<|endofprompt|>` conditions the model and is **not spoken**; only the text after it is voiced.
  CosyVoice3 *asserts* the token is present in `text` or `prompt_text` (else the LLM thread throws →
  empty mel → `upsample_linear1d … input (W: 0)` crash).
- **Do NOT use `inference_instruct2` for narration** — on Fun-CosyVoice3-0.5B the instruction text
  **leaks into the spoken audio** (you hear "用亲切的语气…" read aloud). For tone/voice, clone a
  REFERENCE CLIP instead (this is `tts_server.py`'s documented path):
  - have a transcript → `inference_zero_shot(text, SYS+transcript, ref_wav, speed=)`
    (`SYS="You are a helpful assistant.<|endofprompt|>"`); per-language ref_text cues zh vs en.
  - no transcript (just a voice clip you like) → `inference_cross_lingual(SYS+text, ref_wav, speed=)`
    — clones timbre, speaks zh OR en, no leak. This is how we got a "mature broadcaster" lady voice:
    clone a curated 4 s / 16 kHz mono clip (e.g. `/data/weidong/TTS/asr_input/front_0_4s_*.wav`).
- **Per-segment pace** = the `speed=` kwarg (1.0 normal, <1 slower). For bilingual study videos,
  English at `speed=1.0` is plenty (don't drag it); add a ~0.5 s silence after each English line for
  shadowing instead of slowing the speech.
- **Voice bake-off reality (this host):** only **CosyVoice3** weights are cached (modelscope). Qwen3-TTS
  (`qwen3tts` env, speakers serena/vivian) would need a download; MOSS-TTS (`moss-tts` env) is
  broadcast-grade but ZH-centric (English support unverified). Cold model load is **slow (minutes)**
  under shared-disk contention — run the generator in the background and poll its log.

## GPU

- Both RTX 6000 Ada (48 GB) are often **partly occupied by other work**. Before loading a model,
  `nvidia-smi --query-gpu=memory.free --format=csv` and **pin `CUDA_VISIBLE_DEVICES`** to the freer
  GPU (GPU0 was frequently near-full; GPU1 had headroom). MOSS needs ~16 GB; CosyVoice3 ~5 GB.

## Manim

- **`No module named 'pkg_resources'`** on `manim --version` → install `setuptools<81` in `manimdemo`.
- **Cairo/Pango missing system-wide** (no root) → install them from **conda-forge** inside the env.
- **Chinese shows as tofu** → the font isn't visible to **fontconfig**; symlink the `.otf`s into
  `~/.fonts` + `fc-cache`, then `Text(font="Source Han Serif SC")`. Keep Chinese OUT of `MathTex`.
- Always `manim -s` (last frame only) first to verify fonts/layout before a full multi-minute render.

## Misc

- The narrated video's length = sum of segment audio durations (CosyVoice3 ≈ normal pace, ~46 s for
  5 lines; F5 was ~67 s because it speaks slowly). Time the `_voiced` scene's beats to
  `durations.json` so audio and video stay aligned.
