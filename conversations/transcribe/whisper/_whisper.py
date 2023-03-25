from pathlib import Path
from typing import Dict

import openai
import whisper


def process(audio_file: Path, model_name: str = "base.en") -> Dict[str, str]:
    """Transcribe audio using Whisper.

    Parameters
    ----------
    audio_file : Path
        Path to the audio file.
    model_name : str, optional
        Name of the whisper model to use. To use the cloud service
        provided by OpenAI, use "openai.en", by default "base.en".

    Returns
    -------
    transcript : Dict[str, str]
        Dictionary containing the audio transcript in whisper format.
    """
    if model_name == "openai.en":
        result = _cloud_whisper(audio_file)
    else:
        result = _local_whisper(audio_file, model_name=model_name)
    return result


def _cloud_whisper(audio_file: Path) -> Dict[str, str]:
    """Transcribe audio using OpenAI's Whisper API.

    Parameters
    ----------
    audio_file : Path
        Path to the audio file.

    Returns
    -------
    transcript : Dict[str, str]
        Dictionary containing the audio transcript in whisper format.
    """
    with audio_file.open("rb") as audio:
        result = openai.Audio.transcribe(
            "whisper-1", audio, response_format="verbose_json"
        )
    return result


def _local_whisper(
    audio_file: Path,
    model_name: str = "base.en",
    device: str = "cpu",
) -> Dict[str, str]:
    """Transcribe audio using a local Whisper model.

    Parameters
    ----------
    audio_file : Path
        Path to the audio file.
    model_name : str, optional
        Name of the whisper model to use, available models are "base.en"
        and "large.en", by default "base.en".
    device : str, optional
        The device on which to run the model, either "cpu" or "gpu", by default "cpu".

    Returns
    -------
    transcript : Dict[str, str]
        Dictionary containing the audio transcript in whisper format.
    """
    model = whisper.load_model(model_name, device=device)
    audio = whisper.load_audio(str(audio_file))
    result = model.transcribe(audio)
    return result
