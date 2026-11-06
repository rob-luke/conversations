"""Offline tests for AssemblyAI model selection (no API calls)."""

import pytest

from conversations.transcribe.assembly._assembly import (
    build_config,
    speech_models_for,
)


@pytest.mark.parametrize(
    "name, expected",
    [
        ("universal-3-5-pro", ["universal-3-5-pro", "universal-2"]),
        ("universal-3-pro", ["universal-3-pro", "universal-2"]),
        ("universal-2", ["universal-2"]),
        ("slam-1", ["universal-3-5-pro", "universal-2"]),
        ("best", ["universal-3-5-pro", "universal-2"]),
        ("universal", ["universal-3-5-pro", "universal-2"]),
        ("nano", ["universal-2"]),
        ("NANO", ["universal-2"]),
    ],
)
def test_speech_models_for(name, expected):
    """Model names and legacy aliases map to current AssemblyAI models."""
    assert speech_models_for(name) == expected


def test_speech_models_for_rejects_unknown():
    """Unknown model names raise a ValueError."""
    with pytest.raises(ValueError):
        speech_models_for("whisper-large")


def test_config_uses_speech_models_list():
    """Config sends speech_models and never the retired speech_model field."""
    raw = build_config("slam-1", custom_terms=["Deepgram"]).raw
    assert raw.speech_models == ["universal-3-5-pro", "universal-2"]
    assert getattr(raw, "speech_model", None) is None
    assert raw.keyterms_prompt == ["Deepgram"]
    assert raw.speaker_labels is True


def test_config_universal_2_uses_word_boost():
    """Universal-2 keeps the word boost configuration."""
    raw = build_config("nano").raw
    assert raw.speech_models == ["universal-2"]
    assert raw.word_boost == ["robert", "venture"]
    assert raw.keyterms_prompt is None
