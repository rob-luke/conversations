import dominate
from pathlib import Path
from typing import Any, Dict, List, Optional
from ._utils import (
    _map_speaker_names,
    _get_segement_speaker,
    _group_transcript_segements_by_speaker,
)


test = """function play(t) {
var audio = document.getElementById('audio');
audio.currentTime = t;
audio.play();
}"""


def generate(
    transcript: dict,
    diarisation: Optional[List[Dict[str, Any]]] = None,
    audio_file: Optional[Path] = None,
    speaker_mapping: Optional[dict] = None,
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
    speaker_mapping : dict
        Mapping of old speaker names to new speaker names.
        For example, {"0": "Alice", "1": "Bob"}.

    Returns
    -------
    report : dominate.document
        Conversation report as a dominate document.
    """
    if diarisation is not None:
        transcript = _group_transcript_segements_by_speaker(transcript, diarisation)

    if speaker_mapping is not None:
        transcript = _map_speaker_names(transcript, speaker_mapping)
    else:
        speaker_mapping = {}

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
                previous_speaker = None
                for seg in transcript["segments"]:
                    start = seg["start"]
                    stop = seg["end"]
                    speaker = _get_segement_speaker(seg, speaker_mapping)

                    with dominate.tags.p(cls="mr-2 m-1 flex"):
                        if diarisation is not None:
                            if speaker != previous_speaker:
                                dominate.tags.input_(
                                    value=f"{speaker}",
                                    cls="border m-1 bg-blue-50 mb-2 mt-4 p-1 pl-2 pr-2",
                                    type="button",
                                    onclick=f"play({start})",
                                )
                                previous_speaker = speaker

                        dominate.tags.p(
                            f"{seg['text']}",
                            cls="ml-8 mr-8 m-1",
                            onclick=f"play({start})",
                        )

    return doc
