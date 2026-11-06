import logging
import math
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Deepgram pre-recorded models supported by this package. Nova-3 models take
# custom vocabulary as ``keyterm`` prompts; Nova-2 uses ``keywords`` instead.
KEYTERM_MODELS = ["nova-3", "nova-3-medical"]
KEYWORD_MODELS = ["nova-2"]
MODELS = KEYTERM_MODELS + KEYWORD_MODELS

DEFAULT_MODEL = "nova-3"

# Upload plus processing of an hour-long meeting can take a few minutes on a
# slow uplink, well beyond the HTTP client's default timeout.
DEFAULT_TIMEOUT_SECONDS = 1200

# Deepgram rejects requests whose keyterms exceed 500 tokens in total and
# recommends at most ~100 terms. Its tokenizer is not public. Measured against
# the API (Nov 2026), real names and jargon cost ~2.6 characters per token and
# synthetic names with digits ~1.7, so budget at 2 characters per token plus
# one per term, with headroom. process() also backs off if Deepgram still
# reports the limit as exceeded.
MAX_CUSTOM_TERMS = 100
MAX_KEYTERM_TOKENS = 450


def _estimate_tokens(term: str) -> int:
    """Conservatively estimate the tokens a keyterm consumes."""
    return math.ceil(len(term) / 2) + 1


def clean_custom_terms(custom_terms: Optional[List[str]]) -> List[str]:
    """Prepare custom vocabulary for Deepgram.

    Splits entries on commas, semicolons and newlines (Deepgram treats such a
    value as one literal term that never matches), strips whitespace, drops
    empty and case-insensitive duplicate terms, and trims the list to fit
    Deepgram's limits. Terms are kept in the order given, so put the most
    important first.

    Parameters
    ----------
    custom_terms : list[str], None
        Raw custom vocabulary.

    Returns
    -------
    terms : list[str]
        Cleaned terms within ``MAX_CUSTOM_TERMS`` and an estimated
        ``MAX_KEYTERM_TOKENS`` budget.
    """
    terms: List[str] = []
    seen = set()
    for raw in custom_terms or []:
        for part in re.split(r"[,;\n]", str(raw)):
            term = " ".join(part.split())
            if term and term.lower() not in seen:
                seen.add(term.lower())
                terms.append(term)

    kept: List[str] = []
    budget = MAX_KEYTERM_TOKENS
    for term in terms:
        cost = _estimate_tokens(term)
        if len(kept) >= MAX_CUSTOM_TERMS or cost > budget:
            break
        kept.append(term)
        budget -= cost

    if len(kept) < len(terms):
        logger.warning(
            "Deepgram custom terms trimmed from %d to %d to stay within limits.",
            len(terms),
            len(kept),
        )
    return kept


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
        as ``keywords`` for Nova-2, after :func:`clean_custom_terms`.

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

    terms = clean_custom_terms(custom_terms)
    if terms:
        if model in KEYTERM_MODELS:
            options["keyterm"] = terms
        else:
            options["keywords"] = terms

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


def _transcribe_with_term_backoff(
    client: Any, audio: bytes, options: Dict[str, Any]
) -> Any:
    """Call Deepgram, halving custom terms if it reports the keyterm limit.

    Parameters
    ----------
    client : deepgram.DeepgramClient
        The Deepgram client.
    audio : bytes
        The audio to transcribe.
    options : dict
        Options from :func:`build_options`.

    Returns
    -------
    response : deepgram.types.ListenV1Response
        The Deepgram response.
    """
    from deepgram.errors import BadRequestError

    options = dict(options)
    while True:
        try:
            return client.listen.v1.media.transcribe_file(
                request=audio,
                request_options={"timeout_in_seconds": DEFAULT_TIMEOUT_SECONDS},
                **options,
            )
        except BadRequestError as err:
            key = "keyterm" if "keyterm" in options else "keywords"
            terms = options.get(key) or []
            if "limit" not in str(err).lower() or not terms:
                raise
            keep = len(terms) // 2
            logger.warning(
                "Deepgram rejected %d custom terms as over its limit; retrying with %d.",
                len(terms),
                keep,
            )
            if keep:
                options[key] = terms[:keep]
            else:
                options.pop(key)


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

    response = _transcribe_with_term_backoff(client, audio, options)

    result = response.model_dump(mode="json")
    if "results" not in result:
        raise RuntimeError(
            "Deepgram did not return a transcript (received "
            f"{type(response).__name__})."
        )

    return to_whisper_format(result, language)
