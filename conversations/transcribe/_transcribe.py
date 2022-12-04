from pathlib import Path
from ._whisper import transcribe as whisper_transcribe


def transcribe(
    audio_file: Path, method: str = "whisper", model: str = "base.en"
) -> dict:
    """Transcribe an audio file.


    Parameters
    ----------
    audio_file : Path
        Path to the audio file to be transcribed.
    method : str
        Transcription method. Only Whisper is currently supported.
    model : str
        Specific model to be used for the transcription method. For example, `base.en` for whisper.

    Returns
    ----------
    transcription : dict
        Transcription of the audio file.
    """

    if method == "whisper":
        return whisper_transcribe(audio_file=audio_file, model_name=model)
    else:
        raise ValueError(
            f"Unsupported method: {method}. Only whisper is currently supported."
        )
