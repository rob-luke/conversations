from pathlib import Path
from typing import Dict, List, Optional
import os

import assemblyai as aai  # type: ignore

# Load environmental variable for API key
aai.settings.api_key = f"{os.getenv('ASSEMBLYAI_API_KEY')}"


# AssemblyAI retired the single ``speech_model`` parameter and the nano, best
# and slam-1 models. Requests now pass an ordered ``speech_models`` list and
# AssemblyAI uses the first model that supports the audio's language. Legacy
# names are kept as aliases so existing callers continue to work.
SPEECH_MODELS: Dict[str, List[str]] = {
    "universal-3-5-pro": ["universal-3-5-pro", "universal-2"],
    "universal-3-pro": ["universal-3-pro", "universal-2"],
    "universal-2": ["universal-2"],
    # Legacy aliases.
    "slam-1": ["universal-3-5-pro", "universal-2"],
    "best": ["universal-3-5-pro", "universal-2"],
    "universal": ["universal-3-5-pro", "universal-2"],
    "nano": ["universal-2"],
}

# Models whose primary entry supports ``keyterms_prompt`` for custom vocabulary.
KEYTERM_MODELS = {"universal-3-5-pro", "universal-3-pro", "slam-1", "best", "universal"}


def speech_models_for(model_name: str) -> List[str]:
    """Return the AssemblyAI ``speech_models`` list for a model name.

    Parameters
    ----------
    model_name : str
        A current AssemblyAI model name ("universal-3-5-pro", "universal-3-pro",
        "universal-2") or a legacy alias ("slam-1", "best", "universal", "nano").

    Returns
    -------
    speech_models : list[str]
        Ordered list of models to send to AssemblyAI.

    Raises
    ------
    ValueError
        If ``model_name`` is not a known model or alias.
    """
    key = model_name.lower()
    if key not in SPEECH_MODELS:
        raise ValueError(
            f"Model name must be one of {list(SPEECH_MODELS)}. Received {model_name}."
        )
    return list(SPEECH_MODELS[key])


def build_config(
    model_name: str = "nano",
    language: str = "en",
    custom_terms: Optional[List[str]] = None,
) -> aai.TranscriptionConfig:
    """Build the AssemblyAI transcription config for a model.

    Parameters
    ----------
    model_name : str, optional
        Model name or legacy alias, see :func:`speech_models_for`.
    language : str, optional
        Language to use for the transcription, by default "en".
    custom_terms : list[str], optional
        Custom terms passed as ``keyterms_prompt``. Only used with the
        Universal-3 family (and the legacy aliases that map to it).

    Returns
    -------
    config : assemblyai.TranscriptionConfig
        The transcription configuration.
    """
    speech_models = speech_models_for(model_name)

    if model_name.lower() in KEYTERM_MODELS:
        return aai.TranscriptionConfig(
            speech_models=speech_models,
            language_code=language,
            keyterms_prompt=custom_terms,
            filter_profanity=False,
            speaker_labels=True,
        )

    return aai.TranscriptionConfig(
        speech_models=speech_models,
        language_code=language,
        word_boost=["robert", "venture"],
        boost_param="default",
        filter_profanity=False,
        speaker_labels=True,
    )


def process(
    audio_file: Path,
    model_name: str = "nano",
    language: str = "en",
    custom_terms: Optional[List[str]] = None,
) -> Dict[str, str]:
    """Transcribe audio using AssemblyAI.

    Parameters
    ----------
    audio_file : Path
        Path to the audio file.
    model_name : str, optional
        Name of the AssemblyAI model to use: "universal-3-5-pro",
        "universal-3-pro" or "universal-2". The legacy names "slam-1",
        "best" and "universal" map to Universal-3.5 Pro, and "nano" maps to
        Universal-2, each with Universal-2 as the language fallback.
    language : str, optional
        Language to use for the transcription, by default "en".
    custom_terms : list[str], optional
        Custom terms to help the speech model with specific vocabulary.
        Only used with the Universal-3 family (including "slam-1").

    Returns
    -------
    transcript : Dict[str, str]
        Dictionary containing the audio transcript in whisper format.
    """
    config = build_config(
        model_name=model_name, language=language, custom_terms=custom_terms
    )

    transcriber = aai.Transcriber(config=config)

    transcript = transcriber.transcribe(str(audio_file))

    if transcript.status == aai.TranscriptStatus.error:
        raise RuntimeError(f"AssemblyAI transcription failed: {transcript.error}")

    # Convert to openai format

    result = transcript.json_response

    result["segments"] = result["utterances"]

    # For each segment, convert the start and end times to seconds from milliseconds
    # and prepend speaker to the speaker name
    for seg in result["segments"]:
        seg["start"] = seg["start"] / 1000
        seg["end"] = seg["end"] / 1000
        seg["speaker"] = f"Speaker_{seg['speaker']}"

    return result
