from conversations import report
from conversations.transcribe import whisper
from pathlib import Path
from typing import Dict
import pooch
import dominate


audio_file = pooch.retrieve(
    url="https://project-test-data-public.s3.amazonaws.com/test_audio.m4a",
    known_hash="md5:77d8b60c54dffbb74d48c4a65cd59591",
)

transcript = whisper.process(audio_file=audio_file)


def test_report_without_audiofile():
    """Test report generation."""
    html_report = report.generate(transcript=transcript)
    assert isinstance(html_report, dominate.document)

    with open("tests/output/test_wo_audio.html", "w") as f:
        f.write(html_report.render())


def test_report_with_audiofile():
    """Test report generation."""
    html_report = report.generate(transcript=transcript, audio_file=audio_file)
    assert isinstance(html_report, dominate.document)

    with open("tests/output/test_w_audio.html", "w") as f:
        f.write(html_report.render())
