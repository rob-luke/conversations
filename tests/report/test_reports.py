from conversations import report
from conversations.transcribe import assembly
from conversations.diarise import simple
from pathlib import Path
from typing import Dict
import pooch
import dominate


audio_file = pooch.retrieve(
    url="https://project-test-data-public.s3.amazonaws.com/test_audio.m4a",
    known_hash="md5:77d8b60c54dffbb74d48c4a65cd59591",
)

transcript = assembly.process(audio_file=audio_file)
# diarisation = simple.process(audio_file=audio_file, num_speakers=3)
diarisation = [
    {
        "note": "diairisation performed by assembly and transcript contains speaker labels"
    }
]


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


def test_report_with_mapping():
    """Test report generation."""
    html_report = report.generate(
        transcript=transcript,
        audio_file=audio_file,
        speaker_mapping={"A": "Alice", "B": "Bob", "C": "Sam"},
    )
    assert isinstance(html_report, dominate.document)

    with open("tests/output/test_w_audio.html", "w") as f:
        f.write(html_report.render())


def test_text_export():
    """Test report generation."""
    text_report = report.export_text(
        transcript=transcript,
        speaker_mapping={"A": "Alice", "B": "Bob", "C": "Sam"},
        diarisation=diarisation,
    )
    assert isinstance(text_report, str)

    with open("conversation.txt", "w") as f:
        f.write(text_report)
