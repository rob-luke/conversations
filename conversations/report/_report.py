import pathlib
import numpy as np
import dominate


test = """function play(t) {
var audio = document.getElementById('audio');
audio.currentTime = t;
audio.play();
}"""


def generate(transcript: dict, audio_file: pathlib.PosixPath | None = None):
    """Create html page from Whisper transcript.

    Parameters
    ----------
    transcript : dict
        Transcript from transcribe module.
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
        with dominate.tags.div():

            if audio_file is not None:
                with dominate.tags.audio(
                    id="audio", controls="controls", cls="w-full border"
                ):
                    dominate.tags.source(src=str(audio_file), type="audio/wav")

                dominate.tags.script(test)

            with dominate.tags.div(id="conversation", cls="pt-4"):
                for seg in transcript["segments"]:

                    start = seg["start"]
                    stop = seg["end"]

                    with dominate.tags.p(cls="ml-8 mr-8 m-1 border"):

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
