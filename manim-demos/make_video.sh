#!/usr/bin/env bash
# 一键渲染一个 Manim 场景为 mp4 + gif，并拷贝到 out/。
# 用法:  bash make_video.sh <file.py> <SceneName> [quality:-ql|-qm|-qh]
#   带旁白:  在场景名后传 --narrated（需先启动 localhost:8880 的 TTS 服务器）
set -euo pipefail
cd "$(dirname "$0")"

FILE="${1:?usage: make_video.sh <file.py> <SceneName> [-ql|-qm|-qh]}"
SCENE="${2:?scene name required}"
Q="${3:--qm}"

source /home/weidongguo/miniconda3/etc/profile.d/conda.sh
RUN="conda run -n manimdemo manim ${Q} --media_dir media"

echo "▶ rendering mp4: ${FILE}::${SCENE} (${Q})"
$RUN "${FILE}" "${SCENE}"
echo "▶ rendering gif"
$RUN --format=gif "${FILE}" "${SCENE}"

mkdir -p out
mp4=$(find media -iname "${SCENE}.mp4" -printf '%T@ %p\n' | sort -nr | head -1 | cut -d' ' -f2-)
gif=$(find media -iname "${SCENE}*.gif" -printf '%T@ %p\n' | sort -nr | head -1 | cut -d' ' -f2-)
[ -n "${mp4:-}" ] && cp "$mp4" "out/${SCENE}.mp4" && echo "✓ out/${SCENE}.mp4"
[ -n "${gif:-}" ] && cp "$gif" "out/${SCENE}.gif" && echo "✓ out/${SCENE}.gif"

if ffprobe -v error -show_streams "out/${SCENE}.mp4" 2>/dev/null | grep -q codec_type=audio; then
  echo "✓ has narration audio track"
fi
