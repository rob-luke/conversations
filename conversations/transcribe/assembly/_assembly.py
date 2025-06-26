from pathlib import Path
from typing import Dict, List, Optional
import os

import assemblyai as aai  # type: ignore

# Load environmental variable for API key
aai.settings.api_key = f"{os.getenv('ASSEMBLYAI_API_KEY')}"


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
        Name of the assembly model to use. To use the cloud service
        provided by Assembly, use "nano", "slam-1", "universal", or "best".
    language : str, optional
        Language to use for the transcription, by default "en".
    custom_terms : list[str], optional
        Custom terms to help the speech model with specific vocabulary.
        Only used when ``model_name`` is ``"slam-1"``.

    Returns
    -------
    transcript : Dict[str, str]
        Dictionary containing the audio transcript in whisper format.
    """
    allowed_model_names = ["nano", "best", "slam-1", "universal"]
    if model_name.lower() not in allowed_model_names:
        raise ValueError(
            f"Model name must be one of {allowed_model_names}. Received {model_name}."
        )

    if model_name == "nano":
        speech_model = aai.SpeechModel.nano
    if model_name == "best":
        speech_model = aai.SpeechModel.best
    if model_name == "slam-1":
        speech_model = aai.SpeechModel.slam_1
    if model_name == "universal":
        speech_model = aai.SpeechModel.universal

    if model_name == "slam-1":
        config = aai.TranscriptionConfig(
            speech_model=speech_model,
            language_code=language,
            keyterms_prompt=custom_terms,
            filter_profanity=False,
            speaker_labels=True,
        )

    else:
        config = aai.TranscriptionConfig(
            speech_model=speech_model,
            language_code=language,
            word_boost=["robert", "venture"],
            boost_param="default",
            filter_profanity=False,
            speaker_labels=True,
        )

    transcriber = aai.Transcriber(config=config)

    transcript = transcriber.transcribe(str(audio_file))

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
