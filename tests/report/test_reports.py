from conversations import report
from conversations.transcribe import whisper
from pathlib import Path
from typing import Dict
import pooch
import dominate


audio_file = pooch.retrieve(
    url="https://www2.cs.uic.edu/~i101/SoundFiles/preamble10.wav",
    known_hash="md5:fd76bc5fd34ffd93837490c3b946a99d",
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
