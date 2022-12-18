import pathlib
import dominate


test = """function play(t) {
var audio = document.getElementById('audio');
audio.currentTime = t;
audio.play();
}"""


def generate(transcript: dict, audio_file: pathlib.PosixPath | None = None):
    """Create html page from Whisper transcript."""

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
                for seg in transcript["segments"][:60]:

                    start = seg["start"]
                    stop = seg["end"]

                    dominate.tags.input_(
                        value=f"{start:.0f} - {stop:.0f} : {seg['text']}",
                        cls="pl-8",
                        type="button",
                        onclick=f"play({start})",
                    )
                    dominate.tags.p()

    return doc
