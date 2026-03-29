from conversations.transcribe import deepgram
from pathlib import Path
import pooch


audio_file = pooch.retrieve(
    url="https://project-test-data-public.s3.amazonaws.com/test_audio.m4a",
    known_hash="md5:77d8b60c54dffbb74d48c4a65cd59591",
)


def test_local_process():
    """Test deepgram processing of audio."""
    result = deepgram.process(audio_file=Path(audio_file))
    assert isinstance(result, dict)
    for seg in result["segments"]:
        assert "start" in seg
        assert "end" in seg
        assert "text" in seg
        assert "speaker" in seg
        assert seg["speaker"].startswith("Speaker_")


def test_content():
    """Test that deepgram returns expected content."""
    result = deepgram.process(audio_file=Path(audio_file))
    assert len(result["segments"]) > 0
    assert result["language"] == "en"
