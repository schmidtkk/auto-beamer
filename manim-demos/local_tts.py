"""
manim-voiceover SpeechService that calls the LOCAL OpenAI-compatible TTS adapter
already running in /data/weidong/TTS (tts_exploration/tts_server.py).

Start the server first, e.g.:
  conda activate cosyvoice && cd /data/weidong/TTS/CosyVoice && \
  LOCAL_TTS_MODEL=cosyvoice3 LOCAL_TTS_VOICE=zh_female \
  python ../tts_exploration/tts_server.py        # serves POST localhost:8880/v1/audio/speech

Then in a scene:
  from local_tts import LocalOpenAITTS
  self.set_speech_service(LocalOpenAITTS(model="cosyvoice3", voice="zh_female"))
"""
import os
import requests
from manim_voiceover.services.base import SpeechService

try:
    from manim_voiceover.helper import get_audio_basename
except Exception:  # pragma: no cover - fallback if helper name differs across versions
    import hashlib, json
    def get_audio_basename(input_data) -> str:
        return hashlib.sha256(json.dumps(input_data, sort_keys=True).encode()).hexdigest()[:32]


class LocalOpenAITTS(SpeechService):
    """Routes manim-voiceover narration to the local OpenAI-compatible TTS server."""

    def __init__(
        self,
        base_url: str = None,
        model: str = None,
        voice: str = None,
        instructions: str = "Speak in Chinese. 清晰、稳重、适合教学讲解的语气，语速适中。",
        timeout: int = 600,
        **kwargs,
    ):
        self.base_url = (base_url or os.environ.get("LOCAL_TTS_URL", "http://localhost:8880")).rstrip("/")
        self.model = model or os.environ.get("LOCAL_TTS_MODEL", "cosyvoice3")
        self.voice = voice or os.environ.get("LOCAL_TTS_VOICE", "zh_female")
        self.instructions = instructions
        self.timeout = timeout
        super().__init__(**kwargs)

    def generate_from_text(self, text: str, cache_dir: str = None, path: str = None) -> dict:
        if cache_dir is None:
            cache_dir = self.cache_dir

        input_data = {
            "input_text": text,
            "service": "local_openai_tts",
            "config": {"model": self.model, "voice": self.voice, "base_url": self.base_url},
        }
        cached = self.get_cached_result(input_data, cache_dir)
        if cached is not None:
            return cached

        audio_path = path if path is not None else (get_audio_basename(input_data) + ".mp3")

        resp = requests.post(
            f"{self.base_url}/v1/audio/speech",
            json={
                "model": self.model,
                "voice": self.voice,
                "input": text,
                "instructions": self.instructions,
                "response_format": "mp3",
            },
            timeout=self.timeout,
        )
        resp.raise_for_status()
        with open(os.path.join(cache_dir, audio_path), "wb") as f:
            f.write(resp.content)

        return {"input_text": text, "input_data": input_data, "original_audio": audio_path}
