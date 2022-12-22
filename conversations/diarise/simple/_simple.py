from pathlib import Path
from simple_diarizer import diarizer


def process(audio_file: Path, num_speakers: int = 2) -> list[dict]:
    """Diarise audio using simple_diarizer.

    Parameters
    ----------
    audio_file : Path
        Path to the audio file.
    num_speakers : int
        The number of speakers in the conversation.

    Returns
    -------
    segments : list[dict]
        List containing the segments as dictionaries.
    """
    diar = diarizer.Diarizer(
        embed_model="xvec",  # 'xvec' and 'ecapa' supported
        cluster_method="sc",  # 'ahc' and 'sc' supported
    )

    segments = diar.diarize(audio_file, num_speakers=num_speakers)

    return segments
