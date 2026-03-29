from pathlib import Path
from typing import Dict, List, Optional
import os

from deepgram import DeepgramClient, PrerecordedOptions, FileSource  # type: ignore


def process(
    audio_file: Path,
    model_name: str = "nova-3",
    language: str = "en",
    custom_terms: Optional[List[str]] = None,
) -> Dict[str, str]:
    """Transcribe audio using Deepgram.

    Parameters
    ----------
    audio_file : Path
        Path to the audio file.
    model_name : str, optional
        Name of the Deepgram model to use, by default "nova-3".
        Supported models: "nova-3", "nova-2", "nova", "enhanced", "base".
    language : str, optional
        Language to use for the transcription, by default "en".
    custom_terms : list[str], optional
        Custom terms (keywords) to help the speech model with specific vocabulary.

    Returns
    -------
    transcript : Dict[str, str]
        Dictionary containing the audio transcript in whisper format.
    """
    allowed_model_names = ["nova-3", "nova-2", "nova", "enhanced", "base"]
    if model_name.lower() not in allowed_model_names:
        raise ValueError(
            f"Model name must be one of {allowed_model_names}. Received {model_name}."
        )

    api_key = os.getenv("DEEPGRAM_API_KEY")
    if not api_key:
        raise ValueError(
            "DEEPGRAM_API_KEY environment variable is not set. "
            "Please set it to your Deepgram API key."
        )

    client = DeepgramClient(api_key)

    with open(audio_file, "rb") as f:
        buffer_data = f.read()

    payload: FileSource = {"buffer": buffer_data}

    options = PrerecordedOptions(
        model=model_name,
        language=language,
        smart_format=True,
        utterances=True,
        diarize=True,
        profanity_filter=False,
    )

    if custom_terms:
        options.keywords = custom_terms

    response = client.listen.rest.v("1").transcribe_file(payload, options)

    result = response.to_dict()

    # Convert to openai/whisper format with segments
    segments = []
    utterances = result.get("results", {}).get("utterances", [])
    for utterance in utterances:
        segments.append(
            {
                "start": utterance["start"],
                "end": utterance["end"],
                "text": utterance["transcript"],
                "speaker": f"Speaker_{utterance['speaker']}",
                "confidence": utterance.get("confidence", 0.0),
            }
        )

    result["segments"] = segments
    result["language"] = language

    return result
