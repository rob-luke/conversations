import os
from pathlib import Path
from typing import Any, Dict, List, Optional

# Deepgram pre-recorded models supported by this package. Nova-3 models take
# custom vocabulary as ``keyterm`` prompts; Nova-2 uses ``keywords`` instead.
KEYTERM_MODELS = ["nova-3", "nova-3-medical"]
KEYWORD_MODELS = ["nova-2"]
MODELS = KEYTERM_MODELS + KEYWORD_MODELS

DEFAULT_MODEL = "nova-3"

# Upload plus processing of an hour-long meeting can take a few minutes on a
# slow uplink, well beyond the HTTP client's default timeout.
DEFAULT_TIMEOUT_SECONDS = 1200


def speaker_label(speaker: Optional[int]) -> str:
    """Convert a Deepgram speaker index to the package's speaker label.

    Deepgram numbers speakers from zero. Labels follow the AssemblyAI style
    used elsewhere in the package (``Speaker_A``, ``Speaker_B``, ...) so that
    speaker mappings keyed on letters keep working. After ``Z`` the labels
    continue as ``AA``, ``AB`` and so on.

    Parameters
    ----------
    speaker : int, None
        Zero-based speaker index from Deepgram, or None if diarisation did not
        assign a speaker.

    Returns
    -------
    label : str
        The speaker label, ``Speaker_UNKNOWN`` when no speaker was assigned.
    """
    if speaker is None:
        return "Speaker_UNKNOWN"
    letters = ""
    n = int(speaker)
    while True:
        n, rem = divmod(n, 26)
        letters = chr(65 + rem) + letters
        if n == 0:
            break
        n -= 1
    return f"Speaker_{letters}"


def build_options(
    model_name: str = DEFAULT_MODEL,
    language: str = "en",
    custom_terms: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Build the Deepgram query options for a pre-recorded transcription.

    Parameters
    ----------
    model_name : str, optional
        Deepgram model, one of "nova-3", "nova-3-medical" or "nova-2".
    language : str, optional
        BCP-47 language code, by default "en". Nova-3 also accepts "multi"
        for multilingual code-switching audio.
    custom_terms : list[str], optional
        Custom vocabulary. Sent as ``keyterm`` prompts for Nova-3 models and
        as ``keywords`` for Nova-2.

    Returns
    -------
    options : dict
        Keyword arguments for ``listen.v1.media.transcribe_file``. Requests
        opt out of Deepgram's Model Improvement Program (``mip_opt_out``).

    Raises
    ------
    ValueError
        If ``model_name`` is not a supported Deepgram model.
    """
    model = model_name.lower()
    if model not in MODELS:
        raise ValueError(f"Model name must be one of {MODELS}. Received {model_name}.")

    options: Dict[str, Any] = {
        "model": model,
        "language": language,
        "smart_format": True,
        "punctuate": True,
        "diarize": True,
        "utterances": True,
        "profanity_filter": False,
        # Opt out of Deepgram's Model Improvement Program so meeting audio is
        # not retained for training. Deepgram may price opted-out requests
        # differently.
        "mip_opt_out": True,
    }

    if custom_terms:
        if model in KEYTERM_MODELS:
            options["keyterm"] = list(custom_terms)
        else:
            options["keywords"] = list(custom_terms)

    return options


def to_whisper_format(result: Dict[str, Any], language: str) -> Dict[str, Any]:
    """Add whisper-style segments to a Deepgram response.

    Parameters
    ----------
    result : dict
        The Deepgram ``/v1/listen`` response as a dictionary.
    language : str
        The requested language, used when Deepgram does not report one.

    Returns
    -------
    transcript : dict
        The Deepgram response with ``segments`` (start and end in seconds,
        text, speaker and confidence), ``text`` and ``language`` added.
    """
    results = result.get("results") or {}
    utterances = results.get("utterances") or []

    segments = [
        {
            "start": utt["start"],
            "end": utt["end"],
            "text": utt["transcript"],
            "speaker": speaker_label(utt.get("speaker")),
            "confidence": utt.get("confidence", 0.0),
        }
        for utt in utterances
    ]

    detected_language = None
    channels = results.get("channels") or []
    if channels:
        detected_language = channels[0].get("detected_language")

    result["segments"] = segments
    result["text"] = " ".join(seg["text"] for seg in segments)
    result["language"] = detected_language or language
    return result


def process(
    audio_file: Path,
    model_name: str = DEFAULT_MODEL,
    language: str = "en",
    custom_terms: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Transcribe and diarise audio using Deepgram.

    Reads the API key from the ``DEEPGRAM_API_KEY`` environment variable.

    Parameters
    ----------
    audio_file : Path
        Path to the audio file.
    model_name : str, optional
        Deepgram model, one of "nova-3" (default), "nova-3-medical" or
        "nova-2".
    language : str, optional
        BCP-47 language code, by default "en". Nova-3 also accepts "multi".
    custom_terms : list[str], optional
        Custom vocabulary to help the model with names and jargon. Sent as
        ``keyterm`` prompts for Nova-3 models and ``keywords`` for Nova-2.

    Returns
    -------
    transcript : Dict[str, Any]
        The Deepgram response plus whisper-style ``segments``, with speaker
        labels in the form ``Speaker_A``, ``Speaker_B``.

    Raises
    ------
    ValueError
        If the API key is missing or the model is not supported.
    RuntimeError
        If Deepgram does not return a transcript.
    """
    from deepgram import DeepgramClient

    options = build_options(
        model_name=model_name, language=language, custom_terms=custom_terms
    )

    api_key = os.getenv("DEEPGRAM_API_KEY")
    if not api_key:
        raise ValueError(
            "DEEPGRAM_API_KEY environment variable is not set. "
            "Please set it to your Deepgram API key."
        )

    client = DeepgramClient(api_key=api_key)

    audio = Path(audio_file).read_bytes()

    response = client.listen.v1.media.transcribe_file(
        request=audio,
        request_options={"timeout_in_seconds": DEFAULT_TIMEOUT_SECONDS},
        **options,
    )

    result = response.model_dump(mode="json")
    if "results" not in result:
        raise RuntimeError(
            "Deepgram did not return a transcript (received "
            f"{type(response).__name__})."
        )

    return to_whisper_format(result, language)
