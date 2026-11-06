"""Live tests for the Deepgram provider. Skipped without DEEPGRAM_API_KEY."""

import os
from pathlib import Path

import dominate
import pooch
import pytest

from conversations import Conversation
from conversations.transcribe import deepgram

pytestmark = pytest.mark.skipif(
    not os.getenv("DEEPGRAM_API_KEY"), reason="DEEPGRAM_API_KEY not set"
)

audio_file = Path(
    pooch.retrieve(
        url="https://project-test-data-public.s3.amazonaws.com/test_audio.m4a",
        known_hash="md5:77d8b60c54dffbb74d48c4a65cd59591",
    )
)


@pytest.fixture(scope="module")
def nova3_result():
    """Transcribe the test audio once with Nova-3."""
    return deepgram.process(audio_file=audio_file)


def test_segments(nova3_result):
    """Segments carry timing, text and letter speaker labels."""
    segments = nova3_result["segments"]
    assert len(segments) > 0
    for seg in segments:
        assert 0 <= seg["start"] <= seg["end"]
        assert seg["text"]
        assert seg["speaker"] in ["Speaker_A", "Speaker_B", "Speaker_C"]
    assert nova3_result["metadata"]["models"]


def test_content(nova3_result):
    """The transcript matches the known audio content.

    Smart formatting renders spoken numbers as digits ("$210,000,000"), so
    check for words that formatting leaves alone.
    """
    assert "private equity" in nova3_result["text"].lower()
    assert nova3_result["language"] == "en"


def test_keyterms_nova3():
    """Nova-3 accepts keyterm prompts."""
    result = deepgram.process(audio_file=audio_file, custom_terms=["RJR Nabisco"])
    assert "nabisco" in result["text"].lower()


def test_nova2_keywords():
    """Nova-2 accepts keywords."""
    result = deepgram.process(
        audio_file=audio_file, model_name="nova-2", custom_terms=["million"]
    )
    assert len(result["segments"]) > 0


def test_conversation_report_and_text():
    """A Deepgram transcript drives the existing report and text export."""
    conv = Conversation(recording=audio_file)
    conv.transcribe(method="deepgram")
    assert conv._transcription["segments"][0]["speaker"].startswith("Speaker_")
    conv.diarise()  # Skipped: Deepgram already diarised
    assert isinstance(conv.report(), dominate.document)
    text = conv.export_text()
    assert "private equity" in text.lower()


def test_keyterms_at_limit():
    """The most vocabulary the cleaner allows is accepted by Deepgram."""
    names = [f"Kowalczyk{i} Nakamura{i} Oyelaran{i}" for i in range(200)]
    result = deepgram.process(audio_file=audio_file, custom_terms=names)
    assert len(result["segments"]) > 0
