# Transcribe audio using Whisper
from pathlib import Path
import whisper


def process(audio_file: Path, model_name: str = "base.en") -> dict:
    """Transcribe audio using Whisper.

    Parameters
    ----------
    audio_file : Path
        Path to the audio file.
    model_name : str
        Name of the whisper model to use.

    Returns
    -------
    transcript : dict
        Dictionary containing the audio transcript in whisper format.
    """
    model = whisper.load_model(model_name, device="cpu")
    audio = whisper.load_audio(str(audio_file))
    result = model.transcribe(audio)
    return result
