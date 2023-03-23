from conversations.transcribe import whisper
from pathlib import Path
from typing import Dict
import pooch


audio_file = pooch.retrieve(
    url="https://project-test-data-public.s3.amazonaws.com/test_audio.m4a",
    known_hash="md5:77d8b60c54dffbb74d48c4a65cd59591",
)


def test_local_process():
    """Test whisper processing of audio."""
    result = whisper.process(audio_file=Path(audio_file))
    assert isinstance(result, Dict)
    for seg in result["segments"]:
        assert "start" in seg
        assert "end" in seg
        assert "text" in seg


def test_cloud_process():
    """Test whisper processing of audio via api."""
    result = whisper.process(audio_file=Path(audio_file), model_name="openai.en")
    assert isinstance(result, Dict)
    for seg in result["segments"]:
        assert "start" in seg
        assert "end" in seg
        assert "text" in seg


def test_match_local_and_cloud_process():
    """Test that local and cloud processing return the same results."""
    local_result = whisper.process(audio_file=Path(audio_file))
    cloud_result = whisper.process(audio_file=Path(audio_file), model_name="openai.en")
    assert "million" in local_result["segments"][0]["text"]
    assert "million" in cloud_result["segments"][0]["text"]
