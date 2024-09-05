from pathlib import Path
from typing import Dict
import os

import assemblyai as aai  # type: ignore

# Load environmental variable for API key
aai.settings.api_key = f"{os.getenv('ASSEMBLYAI_API_KEY')}"


def process(
    audio_file: Path,
    model_name: str = "nano",
    language: str = "en",
) -> Dict[str, str]:
    """Transcribe audio using Whisper.

    Parameters
    ----------
    audio_file : Path
        Path to the audio file.
    model_name : str, optionalππ
        Name of the assembly model to use. To use the cloud service
        provided by Assembly, use "nano" or "best".
    language : str, optional
        Language to use for the transcription, by default "en".

    Returns
    -------
    transcript : Dict[str, str]
        Dictionary containing the audio transcript in whisper format.
    """
    allowed_model_names = ["nano", "best"]
    if model_name.lower() not in allowed_model_names:
        raise ValueError(
            f"Model name must be one of {allowed_model_names}. Received {model_name}."
        )

    if model_name == "nano":
        speech_model = aai.SpeechModel.nano
    elif model_name == "best":
        speech_model = aai.SpeechModel.best

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
    for seg in result["segments"]:
        seg["start"] = seg["start"] / 1000
        seg["end"] = seg["end"] / 1000

    return result
