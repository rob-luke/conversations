"""Offline tests for the Deepgram provider (no API calls)."""

import pytest

from conversations.transcribe.deepgram._deepgram import (
    build_options,
    speaker_label,
    to_whisper_format,
)


@pytest.mark.parametrize(
    "index, expected",
    [
        (0, "Speaker_A"),
        (1, "Speaker_B"),
        (25, "Speaker_Z"),
        (26, "Speaker_AA"),
        (27, "Speaker_AB"),
        (None, "Speaker_UNKNOWN"),
    ],
)
def test_speaker_label(index, expected):
    """Deepgram speaker indices map to AssemblyAI-style letter labels."""
    assert speaker_label(index) == expected


def test_options_defaults():
    """Defaults request diarised, formatted utterances from Nova-3."""
    opts = build_options()
    assert opts["model"] == "nova-3"
    assert opts["language"] == "en"
    assert opts["diarize"] is True
    assert opts["utterances"] is True
    assert opts["smart_format"] is True
    assert opts["mip_opt_out"] is True
    assert "keyterm" not in opts
    assert "keywords" not in opts


def test_options_nova3_custom_terms_use_keyterm():
    """Nova-3 models take custom vocabulary as keyterm prompts."""
    opts = build_options("nova-3", custom_terms=["Deepgram", "Seagraves"])
    assert opts["keyterm"] == ["Deepgram", "Seagraves"]
    assert "keywords" not in opts


def test_options_nova2_custom_terms_use_keywords():
    """Nova-2 takes custom vocabulary as keywords."""
    opts = build_options("nova-2", custom_terms=["Deepgram"])
    assert opts["keywords"] == ["Deepgram"]
    assert "keyterm" not in opts


def test_options_rejects_unknown_model():
    """Unknown models raise a ValueError before any API call."""
    with pytest.raises(ValueError):
        build_options("slam-1")


def test_to_whisper_format():
    """Utterances become whisper-style segments with letter speaker labels."""
    response = {
        "metadata": {"request_id": "abc"},
        "results": {
            "channels": [{"alternatives": [{"transcript": "hi there"}]}],
            "utterances": [
                {
                    "start": 0.5,
                    "end": 1.25,
                    "transcript": "Hi.",
                    "speaker": 0,
                    "confidence": 0.9,
                },
                {"start": 1.5, "end": 2.0, "transcript": "There.", "speaker": 1},
            ],
        },
    }
    result = to_whisper_format(response, "en")
    assert result["segments"] == [
        {
            "start": 0.5,
            "end": 1.25,
            "text": "Hi.",
            "speaker": "Speaker_A",
            "confidence": 0.9,
        },
        {
            "start": 1.5,
            "end": 2.0,
            "text": "There.",
            "speaker": "Speaker_B",
            "confidence": 0.0,
        },
    ]
    assert result["text"] == "Hi. There."
    assert result["language"] == "en"
    assert result["metadata"]["request_id"] == "abc"


def test_to_whisper_format_detected_language_and_empty():
    """Detected language wins, and silence yields no segments."""
    response = {
        "results": {
            "channels": [{"detected_language": "de", "alternatives": []}],
            "utterances": None,
        }
    }
    result = to_whisper_format(response, "multi")
    assert result["segments"] == []
    assert result["text"] == ""
    assert result["language"] == "de"


def test_missing_api_key(monkeypatch, tmp_path):
    """A missing API key raises a clear error."""
    from conversations.transcribe import deepgram

    monkeypatch.delenv("DEEPGRAM_API_KEY", raising=False)
    audio = tmp_path / "a.wav"
    audio.write_bytes(b"")
    with pytest.raises(ValueError, match="DEEPGRAM_API_KEY"):
        deepgram.process(audio_file=audio)
