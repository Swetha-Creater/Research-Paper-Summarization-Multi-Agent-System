from gtts import gTTS
import os
from pathlib import Path

def summary_audio_agent(input: dict) -> dict:
    text = input.get("text", "")
    filename = input.get("filename", "summary_audio").replace(" ", "_")
    language = input.get("language", "en")

    if not text.strip():
        return {"status": "error", "error": "Text is empty."}

    try:
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        audio_path = output_dir / f"{filename}.mp3"
        tts = gTTS(text=text.strip(), lang=language)
        tts.save(str(audio_path))

        return {
            "audio_path": str(audio_path),
            "status": "success"
        }

    except Exception as e:
        return {"status": "error", "error": str(e)}


