from conversations.diarise import simple
from pathlib import Path
import pooch


audio_file = pooch.retrieve(
    url="https://www2.cs.uic.edu/~i101/SoundFiles/preamble10.wav",
    known_hash="md5:fd76bc5fd34ffd93837490c3b946a99d",
)


def test_process():
    """Test whisper processing of audio."""
    segments = simple.process(audio_file=Path(audio_file))
    assert isinstance(segments, list)
    for seg in segments:
        assert "start" in seg
        assert "end" in seg
        assert "label" in seg
