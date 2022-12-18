from conversations.transcribe import whisper
from pathlib import Path
from typing import Dict
import pooch


audio_file = pooch.retrieve(
    url="https://www2.cs.uic.edu/~i101/SoundFiles/preamble10.wav",
    known_hash="md5:fd76bc5fd34ffd93837490c3b946a99d",
)


def test_process():
    """Test whisper processing of audio."""
    result = whisper.process(audio_file=audio_file)
    assert isinstance(result, Dict)
    for seg in result["segments"]:
        assert "start" in seg
        assert "end" in seg
        assert "text" in seg
