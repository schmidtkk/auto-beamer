# Narration — the local TTS lab, CosyVoice3, offline-gen + mux

Chinese voiceover comes from the existing lab at **`/data/weidong/TTS`** (don't rebuild it).
It exposes an **OpenAI-compatible** server (`tts_exploration/tts_server.py`,
`POST localhost:8880/v1/audio/speech`); full docs in `tts_exploration/TTS_API.md` and
`FINAL_REPORT.md`.

## Default voice: **CosyVoice3** (best Chinese, commercial-safe)

`Fun-CosyVoice3-0.5B` — **Apache-2.0**, #1 in the lab's own "Production (commercial)" / "中文最佳
质量" ranking, female, **zero-shot voice cloning** (clones `CosyVoice/asset/zero_shot_prompt.wav`).
Ready on disk (weights cached, repo + `third_party/Matcha-TTS` present).

**Run it via the env's python directly** — the `cosyvoice` env is NOT a registered conda env, so
`conda run -n cosyvoice` fails with "not a conda environment":
```bash
/home/weidongguo/miniconda3/envs/cosyvoice/bin/python <script>.py
```

## Robust path: offline one-shot generation + ffmpeg mux (RECOMMENDED)

The persistent TTS server gets **SIGURG-killed (exit 144)** in this shell (see gotchas), so prefer a
**one-shot generator that exits** over a long-running server:

1. `manim-demos/gen_narration.py` — loads CosyVoice3, synthesizes each narration line
   (`inference_zero_shot`), writes `voiceover_audio/seg_{i}.wav` + `sample_all.wav` (segments joined
   with 0.4 s gaps) + `durations.json`. Edit its `SEGS` list for a new script. Run:
   ```bash
   cd /data/weidong/TTS/CosyVoice
   CUDA_VISIBLE_DEVICES=1 /home/weidongguo/miniconda3/envs/cosyvoice/bin/python \
     /data/weidong/auto-beamer/manim-demos/gen_narration.py
   ```
2. `manim-demos/ot_displacement_voiced.py` — a `Scene` whose beats are timed to `durations.json`
   (each segment's animation lasts its audio length, +0.4 s gaps), so the silent render's timeline
   matches `sample_all.wav` beat-for-beat. Copy & re-time `pad(d[i], used)` for new content.
3. Mux:
   ```bash
   ffmpeg -y -i <silent.mp4> -i voiceover_audio/sample_all.wav -c:v copy -c:a aac -shortest out/<name>.mp4
   ```
   Verify `video dur ≈ audio dur`.

## Live path (when the server stays up): manim-voiceover

`manim-demos/local_tts.py` is a manim-voiceover `SpeechService` that POSTs to `localhost:8880`
(env-configurable `LOCAL_TTS_URL/MODEL/VOICE`). A `VoiceoverScene` then auto-fits animation to
narration: `with self.voiceover(text="…") as tr: self.play(..., run_time=tr.duration)`
(see `ot_displacement_narrated.py`). Start the server first, e.g.:
```bash
conda activate cosyvoice && cd /data/weidong/TTS/CosyVoice
LOCAL_TTS_MODEL=cosyvoice3 LOCAL_TTS_VOICE=default python ../tts_exploration/tts_server.py
```
Use only if the server survives; otherwise use the offline path above.

## TTS model / voice selection (from the lab's benchmark)

| Model | ID / env | License | 中文 quality | Voice | VRAM | Notes |
|-------|----------|---------|-------------|-------|------|-------|
| **CosyVoice3** | `cosyvoice` (bin/python) | **Apache-2.0 ✅** | best | clone `zero_shot_prompt.wav` (female) | ~5 GB | **default**; fast (RTF 0.4–0.6); instruct mode for tone |
| Qwen3-TTS 1.7B | `qwen3tts` | Apache-2.0 ✅ | excellent (WER 0.77%) | `vivian` 清晰女声 | ~5 GB | slower (RTF ~3); weights cached |
| Chatterbox MTL | `tts_eval` | MIT ✅ | good | `zh` | ~3 GB | multilingual; ready, but fixed speaker |
| MOSS-TTS v1.5 | `tts_eval` | — | broadcast | `broadcast_calm`/`authoritative` | ~16 GB | **BROKEN in tts_eval** (transformers mismatch); needs its own env |
| F5-TTS | `tts_eval` | MIT code / CC-BY-NC weights | weak/odd default ref | `zh_female` | ~2 GB | avoid for production voice |
| Kokoro | `tts_eval` | Apache-2.0 ✅ | ok | English-named voices only | ~0.5 GB | tiny/fast; not ideal for ZH |

**For a "mature / 成熟 / broadcast" lady voice with CosyVoice3:** either (a) clone a *mature*
reference clip (e.g. from `/data/weidong/TTS/front_0_4s_cleaned_versions.zip`) instead of the
default gentle `zero_shot_prompt.wav`, or (b) use `inference_instruct2(text, "用一位成熟、稳重、
专业的女性播音员的声音", ref_wav)`. The default `zero_shot_prompt.wav` reads gentle/young.

The adapter's `instructions` field is parsed only for `Speak in <Language>` (language detection);
MOSS's per-voice instruction comes from its preset map, not the request.

## Bilingual review video — the dual-model recipe (battle-tested)

For a **Chinese-explanation + English-example** review video, one model rarely does both well:
cloning a short clip drifts in timbre/pace, CosyVoice/MOSS English is accented/weak, Qwen3 is a
download. The robust answer is **split by language** (two different voices is natural for a host +
example-reader). Reference implementation: `auto-beamer/english-review/` (`beats.py` is the source
of truth; `gen_zh_moss.py`, `gen_en_chatterbox.py`, `stitch.py`).

- **Chinese → MOSS-TTS v1.5** (`moss-tts` env — NOT `tts_eval`, where it's broken; 8B, ~16 GB).
  Maturity comes from the **instruction**, not a clip: `build_user_message(text, reference=[clean_ref],
  instruction="用一位成熟、稳重…女性新闻主播…", language="Chinese")`, then `model.generate(...,
  audio_temperature=1.3, audio_top_p=0.8, audio_top_k=25, audio_repetition_penalty=1.1)`. Low temp =
  stable broadcast. MOSS English is weak → don't use it for the English lines.
- **English → Chatterbox MTL** (`tts_eval` env, `ChatterboxMultilingualTTS`, `generate(text,
  language_id="en", cfg_weight=…, exaggeration=…)`). Good native timbre. Two must-do fixes:
  - **Breathless long sentences** → split at clause punctuation (`, ; : . —`), synth each clause
    separately, join with **~0.35 s breath gaps**. Global `atempo` alone does NOT add breaths.
  - **Too fast** → `cfg_weight≈0.3` slows pacing a little; for real control use ffmpeg
    **`atempo=0.86`** (pitch-preserving). EQ for "clear & resonant" (清晰洪亮): highpass 85 +
    body 250 Hz + presence 3.5 kHz + air 9 kHz + light `acompressor`.
- **Balance the two voices**: RMS-match English to Chinese (or both to a target), then a single
  `loudnorm=I=-15` on the concatenated track. Both models are 24 kHz here (no resample).

### TTS PROTOCOL — never feed an engine mixed-language text (a real bug we hit)
A Chinese segment that embedded English terms (`…：through the lens of，意思是…`), sent to MOSS as
`language=Chinese`, made MOSS **read the English as Chinese → garbled "strange" audio**. Rule:
**every unit handed to an engine is single-language and speakable.** Author mixed text as a
*sequence* of `zh`/`en` units (an embedded English term becomes its own `en` unit → Chatterbox).
Gate it with a validator (`english-review/check_narration.py` + `TTS-PROTOCOL.md`): single script
per unit, no markup / `<|…|>` tokens, no punctuation-only units (use `("pause", s)` for a break).
Also normalize loudness **per segment** — MOSS's per-utterance level swung **3.3×**, which read as
"front-to-back inconsistency" until each part was RMS-matched.

### Decouple control from content + verify the OUTPUT (the only real fix for prompt leak)
A role/tone instruction is a *soft* in-prompt directive (MOSS templates it as `- Instruction: …`
right next to `- Text: …`; CosyVoice `instruct2` is similar) so the model can **speak it**. You
cannot prevent this from the input side alone. Two-part fix, both implemented in `english-review/`:
1. **Decouple** — keep role/intonation/speed in a STYLE profile referenced by an "intonation
   footnote", never in the spoken text (format + schema: `ORAL-SCRIPT-PROTOCOL.md` + `oral_script.py`).
   Synthesize **short lead-ins with no instruction at all** (no leak vector).
2. **Verify the audio (G3)** — ASR every clip (`tts_verify.py`, whisper-medium) and reject+regenerate
   any whose transcript contains control vocabulary (主播/播报/咬字/新闻… , `user_inst`, `<|`) or
   diverges from the intended text. Loop until clean. This caught real leaks ("…女性新闻主播的声音
   播报，语速平稳，咬字清晰") that shipped silently before. Note: whisper-zh emits *traditional* chars
   and is weak on 2-s clips → do the leak check (high-precision) on zh; do the similarity/garble
   check on en; convert trad→simp or skip zh-similarity to avoid false positives.

### MOSS runaway guard (short inputs)
MOSS-TTS hallucinates/loops on **very short inputs** (a 3-char lead-in "核心是" generated **115 s**).
Cap `max_new_tokens` by text length (`len*8+160`) and **re-roll at lower `audio_temperature`** if
the clip is implausibly long (> ~0.45 s/char). Same for Chatterbox: lowering temp / raising
`repetition_penalty` to fight tail-echo can instead cause *runaway* — keep its defaults and fix
tails structurally (clean clause stops + trailing trim/fade) instead.

### Per-model speaking-rate control (the "how do I slow it down" answer)
- **CosyVoice3**: native `speed=` kwarg on every `inference_*` (1.0 normal, `<1` slower).
- **Chatterbox**: no speed arg — use `cfg_weight` (lower = slower) and/or ffmpeg `atempo`.
- **MOSS**: `tokens=` target length (1 s ≈ 12.5 tokens) + inline `[pause 0.3s]` markers.
- **Universal**: ffmpeg `atempo=0.85` (0.5–2.0, chain for more) — pitch-preserving, any model.
