# manim-demos — 数学演示 GIF / 教学短视频流水线

把 `auto-beamer` 里的数学内容（如最优传输）做成 **平滑数学动画 GIF** 和 **带中文旁白的教学短视频**。
引擎：**Manim Community v0.20** + 本地 **TTS 服务器**（`/data/weidong/TTS`，OpenAI 兼容 API）。

## 环境（已搭好，一次性）

- Conda 环境 **`manimdemo`**：`python 3.11` + `pycairo` / `manimpango` / `ffmpeg`（来自 conda-forge，
  无需 root）+ `pip install manim manim-voiceover requests setuptools<81`。
- 中文字体：`auto-beamer/.fonts/SourceHanSerifSC-*.otf` 已通过 `~/.fonts` 软链 + `fc-cache` 注册，
  Manim 里直接 `Text("中文", font="Source Han Serif SC")`。
- 渲染依赖（系统已有）：`ffmpeg`、`xelatex`、`dvisvgm`（MathTex 用）。
- 重建环境：
  ```bash
  conda create -y -n manimdemo -c conda-forge python=3.11 pycairo manimpango ffmpeg pkg-config
  conda run -n manimdemo pip install manim manim-voiceover requests "setuptools<81"
  ```

## 文件

| 文件 | 作用 |
|------|------|
| `ot_displacement.py` | **静音**动画场景 `OTDisplacement`（位移 vs 线性插值；镜像 `slides_assets/ot/sec4-displacement.tex` 的高斯例子） |
| `local_tts.py` | manim-voiceover 的 `SpeechService`，把旁白转发到本地 `localhost:8880/v1/audio/speech` |
| `ot_displacement_narrated.py` | **带旁白**场景 `OTDisplacementNarrated`（VoiceoverScene，动画时长自动对齐旁白） |
| `out/` | 成品：`ot_displacement.gif`、`ot_displacement_silent.mp4`、`ot_displacement_narrated.mp4` |
| `make_video.sh` | 一键封装：渲染 mp4 + gif（+可选旁白） |

## 渲染

```bash
# 静音 mp4 / gif（数学演示）
conda run -n manimdemo manim -qh --media_dir media ot_displacement.py OTDisplacement
conda run -n manimdemo manim -qm --format=gif --media_dir media ot_displacement.py OTDisplacement

# 带中文旁白的教学短视频：先启动 TTS 服务器（见下），再渲染
conda run -n manimdemo manim -qh --media_dir media ot_displacement_narrated.py OTDisplacementNarrated
```
画质：`-ql`(480p) / `-qm`(720p) / `-qh`(1080p) / `-qk`(4K)。

## 中文旁白 TTS 服务器

复用 `/data/weidong/TTS` 的统一适配器（OpenAI 兼容）。当前没有 `cosyvoice` conda 环境；可用
**F5-TTS（`tts_eval` 环境，约 2GB 显存，中文 `zh_female`）**：
```bash
conda activate tts_eval
cd /data/weidong/TTS
LOCAL_TTS_MODEL=f5tts LOCAL_TTS_VOICE=zh_female LOCAL_TTS_PORT=8880 \
  python /data/weidong/TTS/tts_exploration/tts_server.py
# 验证： curl -s localhost:8880/health
```
其他可选模型见 `/data/weidong/TTS/tts_exploration/TTS_API.md`（mosstts=广播级教学嗓 `broadcast_authoritative`，
约 16GB 显存；chatterbox / qwen3tts / kokoro 等）。`local_tts.py` 通过环境变量
`LOCAL_TTS_URL/LOCAL_TTS_MODEL/LOCAL_TTS_VOICE` 选择，默认 `f5tts/zh_female`。

> 注意：F5-TTS 语速偏慢（教学场景反而清晰），故旁白版时长（~67s）比静音版（~18s）长。
> 想更快/更广播化，换 `mosstts`（需 GPU1 富余显存）。

## 做一个新主题（套模板）

1. 复制 `ot_displacement.py` → `mytopic.py`，改数学（plot 函数）、标签、要点。
2. 想加旁白：复制 `ot_displacement_narrated.py`，把动画 beat 包进
   `with self.voiceover(text="……") as tr: self.play(..., run_time=tr.duration)`，旁白会自动对齐。
3. `bash make_video.sh mytopic.py MyScene` 出片。

适合下一步做的最优传输动画：Monge/Kantorovich 几何（耦合矩阵/不可分裂 vs 可分裂）、
Wasserstein 测地线、第 8 章"轨迹不相交（解开降低成本）"。

## 进阶（可选）
- 平滑动画 + 精排版的"竖版/横版短视频包装"可叠加已安装的 **HeyGen HyperFrames** 插件
  （HTML/GSAP→MP4 + TTS + 字幕），把 Manim 片段嵌进去做片头/字幕/转场。
