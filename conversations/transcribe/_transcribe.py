from pathlib import Path
from ._whisper import transcribe as whisper_transcribe


def transcribe(audio_file: Path) -> dict:
    return whisper_transcribe(audio_file=audio_file)
