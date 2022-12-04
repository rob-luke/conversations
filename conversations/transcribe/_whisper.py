# Transcribe audio using Whisper
from pathlib import Path
import whisper


def transcribe(audio_file: Path, model_name: str = "base.en") -> dict:
    """Transcribe audio using Whisper."""

    model = whisper.load_model(model_name, device="cpu")
    audio = whisper.load_audio(str(audio_file))
    result = model.transcribe(audio)
    return result
