from pathlib import Path
from simple_diarizer import diarizer


def process(audio_file: Path, num_speakers: int = 2) -> list[dict]:

    diar = diarizer.Diarizer(
                      embed_model='xvec', # 'xvec' and 'ecapa' supported
                      cluster_method='sc' # 'ahc' and 'sc' supported
                   )

    segments = diar.diarize(audio_file, num_speakers=num_speakers)

    return segments

