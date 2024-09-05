from conversations.transcribe import assembly
from pathlib import Path
from typing import Dict
import pooch


audio_file = pooch.retrieve(
    url="https://project-test-data-public.s3.amazonaws.com/test_audio.m4a",
    known_hash="md5:77d8b60c54dffbb74d48c4a65cd59591",
)


def test_local_process():
    """Test whisper processing of audio."""
    result = assembly.process(audio_file=Path(audio_file))
    assert isinstance(result, dict)
    # print json dump of result
    for seg in result["segments"]:
        assert "start" in seg
        assert "end" in seg
        assert "text" in seg
        assert seg["speaker"] in ["speaker_A", "speaker_B", "speaker_C"]


def test_content():
    """Test that local and cloud processing return the same results."""
    cloud_result = assembly.process(audio_file=Path(audio_file))
    assert "million" in cloud_result["segments"][0]["text"]
