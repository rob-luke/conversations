from conversations.diarise import simple
from pathlib import Path
import pooch


audio_file = pooch.retrieve(
    url="https://project-test-data-public.s3.amazonaws.com/test_audio.m4a",
    known_hash="md5:77d8b60c54dffbb74d48c4a65cd59591",
)


def test_process():
    """Test whisper processing of audio."""
    segments = simple.process(audio_file=Path(audio_file))
    assert isinstance(segments, list)
    for seg in segments:
        assert "start" in seg
        assert "end" in seg
        assert "label" in seg
