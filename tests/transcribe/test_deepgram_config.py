"""Offline tests for the Deepgram provider (no API calls)."""

import pytest

from conversations.transcribe.deepgram._deepgram import (
    MAX_CUSTOM_TERMS,
    MAX_KEYTERM_TOKENS,
    _estimate_tokens,
    _transcribe_with_term_backoff,
    build_options,
    clean_custom_terms,
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


def test_clean_custom_terms_splits_and_dedupes():
    """Separators split terms; blanks and case-insensitive duplicates go."""
    raw = ["Deepgram, Seagraves", "  Nova  3 ", "deepgram", "", "Flux;TLM\nSTT"]
    assert clean_custom_terms(raw) == [
        "Deepgram",
        "Seagraves",
        "Nova 3",
        "Flux",
        "TLM",
        "STT",
    ]
    assert clean_custom_terms(None) == []


def test_clean_custom_terms_caps_count_and_tokens(caplog):
    """Long vocabularies are trimmed in order to fit Deepgram's limits."""
    many = [f"term{i}" for i in range(500)]
    kept = clean_custom_terms(many)
    assert kept == many[: len(kept)]
    assert 0 < len(kept) <= MAX_CUSTOM_TERMS
    assert "trimmed" in caplog.text

    long_terms = ["x" * 300, "y" * 300, "z" * 300]
    kept_long = clean_custom_terms(long_terms)
    assert kept_long == long_terms[: len(kept_long)]
    assert sum(_estimate_tokens(t) for t in kept_long) <= MAX_KEYTERM_TOKENS
    assert len(kept_long) < len(long_terms)


def test_options_custom_terms_only_whitespace():
    """Vocabulary that cleans to nothing sends no keyterm parameter."""
    opts = build_options("nova-3", custom_terms=[" ", ","])
    assert "keyterm" not in opts


class _FakeMedia:
    """Fake ``listen.v1.media`` that rejects more than ``limit`` keyterms."""

    def __init__(self, limit, message="Keyterm limit exceeded."):
        self.limit = limit
        self.message = message
        self.calls = []

    def transcribe_file(self, request, request_options=None, **options):
        from deepgram.errors import BadRequestError

        terms = options.get("keyterm", [])
        self.calls.append(len(terms))
        if len(terms) > self.limit:
            raise BadRequestError(body={"err_msg": self.message})
        return "ok"


class _FakeClient:
    def __init__(self, media):
        self.listen = type("L", (), {"v1": type("V", (), {"media": media})()})()


def test_backoff_halves_terms_until_accepted():
    """Over-limit keyterms are halved and retried, not fatal."""
    media = _FakeMedia(limit=10)
    opts = build_options("nova-3", custom_terms=[f"t{i}" for i in range(40)])
    assert _transcribe_with_term_backoff(_FakeClient(media), b"", opts) == "ok"
    assert media.calls == [40, 20, 10]


def test_backoff_drops_terms_entirely_as_last_resort():
    """If no keyterms are accepted, transcription proceeds without them."""
    media = _FakeMedia(limit=0)
    opts = build_options("nova-3", custom_terms=["a", "b"])
    assert _transcribe_with_term_backoff(_FakeClient(media), b"", opts) == "ok"
    assert media.calls == [2, 1, 0]


def test_backoff_reraises_other_bad_requests():
    """Unrelated 400s are not swallowed."""
    from deepgram.errors import BadRequestError

    media = _FakeMedia(limit=0, message="Unsupported audio format.")
    opts = build_options("nova-3", custom_terms=["a"])
    with pytest.raises(BadRequestError):
        _transcribe_with_term_backoff(_FakeClient(media), b"", opts)
