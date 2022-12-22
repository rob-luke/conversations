import pathlib
import numpy as np
import dominate
from pathlib import Path

from scipy.sparse import dia


test = """function play(t) {
var audio = document.getElementById('audio');
audio.currentTime = t;
audio.play();
}"""


def generate(
    transcript: dict,
    diarisation: dict | None = None,
    audio_file: Path | None = None,
):
    """Create html page from conversation.

    Parameters
    ----------
    transcript : dict
        Transcript from transcribe module.
    diarisation : dict
        Speaker diarisation from from diarisation module.
    audio_file : PosixPath | None
        Path to audio file. If provided, audio will be embedded in the
        report and timestamps will link to audio times.

    Returns
    -------
    report : dominate.document
        Conversation report as a dominate document.
    """
    doc = dominate.document(title="Conversation")

    with doc.head:
        dominate.tags.script(src="https://cdn.tailwindcss.com")

    with doc:
        with dominate.tags.div(cls="ml-12 mr-12 mt-6"):

            if audio_file is not None:
                with dominate.tags.audio(
                    id="audio", controls="controls", cls="w-full border"
                ):
                    dominate.tags.source(src=str(audio_file), type="audio/wav")

                dominate.tags.script(test)

            with dominate.tags.div(id="conversation", cls="pt-2"):

                current_speaker = None
                for seg in transcript["segments"]:

                    start = seg["start"]
                    stop = seg["end"]
                    mid_time = start + ((stop - start) / 2)

                    if diarisation is not None:
                        speaker = _find_current_speaker(mid_time, diarisation)

                        if speaker != current_speaker:
                            current_speaker = speaker
                            dominate.tags.p(
                                f"Speaker: {speaker}",
                                cls="border ml-2 m-1 w-32 bg-blue-50 mb-2 mt-4 p-1 pl-2",
                            )

                    with dominate.tags.p(cls="ml-8 mr-2 m-1 border"):

                        dominate.tags.input_(
                            value=f"{_seconds_to_formatted(start)} - {_seconds_to_formatted(stop)} : {seg['text']}",
                            cls="m-1",
                            type="button",
                            onclick=f"play({start})",
                        )

    return doc


def _seconds_to_formatted(seconds):
    """Format seconds for use in report."""
    res = np.divmod(seconds, 60)
    min = res[0]
    sec = round(res[1])
    return f"{int(min):02}:{int(sec):02}"


def _find_current_speaker(timeval, diarisation) -> str:
    """Find the speaker label associated with a time."""
    for seg_idx in range(len(diarisation) - 1):
        seg = diarisation[seg_idx]
        next_seg = diarisation[seg_idx + 1]
        if (seg["start"] < timeval) & (next_seg["start"] > timeval):
            return str(seg["label"])
    return str(diarisation[-1]["label"])
