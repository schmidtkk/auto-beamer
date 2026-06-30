"""
一次性用 CosyVoice3（Apache-2.0，中文最佳、可商用）合成位移插值短视频的中文旁白。
零样本克隆 CosyVoice/asset/zero_shot_prompt.wav 的女声。
运行：
  conda run -n cosyvoice python gen_narration.py
输出：manim-demos/voiceover_audio/seg_{0..4}.wav + durations.json
"""
import sys, json
from pathlib import Path

ROOT = Path("/data/weidong/TTS/CosyVoice")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "third_party" / "Matcha-TTS"))

import torch
import torchaudio
from cosyvoice.cli.cosyvoice import AutoModel

MODEL_DIR = str(ROOT / "pretrained_models" / "Fun-CosyVoice3-0.5B")
REF_WAV = str(ROOT / "asset" / "zero_shot_prompt.wav")
SYS = "You are a helpful assistant.<|endofprompt|>"
REF_TEXT = SYS + "希望你以后能够做的比我还好呦。"

OUT = Path("/data/weidong/auto-beamer/manim-demos/voiceover_audio")
OUT.mkdir(parents=True, exist_ok=True)

SEGS = [
    "在最优传输里，我们常问：两个概率分布之间，如何构造一条合理的演化路径？",
    "最直接的想法是线性插值——把起点和终点两个分布，按时间比例加权平均。",
    "但请看上面一行：线性插值在中间会分裂成两个峰。质量仿佛凭空消失又出现，而不是真正地移动。",
    "下面一行是位移插值：每一份质量沿着最优路径匀速平移。中间分布始终保持单峰，只是整体移动并形变。",
    "这正是 Wasserstein 空间中的测地线——最优传输给出的，最自然的分布演化方式。",
]

print("loading CosyVoice3 ...", flush=True)
cv = AutoModel(model_dir=MODEL_DIR)
sr = int(cv.sample_rate)
print("sample_rate", sr, flush=True)

durs = []
wavs = []
for i, text in enumerate(SEGS):
    chunks = [o["tts_speech"] for o in cv.inference_zero_shot(text, REF_TEXT, REF_WAV, stream=False)]
    wav = torch.cat(chunks, dim=1)  # [1, samples]
    torchaudio.save(str(OUT / f"seg_{i}.wav"), wav, sr)
    d = wav.shape[1] / sr
    durs.append(round(d, 3))
    wavs.append(wav)
    print(f"seg {i}: {d:.2f}s", flush=True)

# 拼一个带 0.4s 间隔的整段样本，方便一次性试听
gap = torch.zeros(1, int(0.4 * sr))
combined = torch.cat([t for w in wavs for t in (w, gap)], dim=1)
torchaudio.save(str(OUT / "sample_all.wav"), combined, sr)

json.dump({"sr": sr, "durations": durs, "segs": SEGS}, open(OUT / "durations.json", "w"), ensure_ascii=False, indent=2)
print("TOTAL", round(sum(durs), 2), "s")
print("GEN_DONE")
