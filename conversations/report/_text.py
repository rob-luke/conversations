from typing import Any, Dict, List, Optional
from ._utils import (
    _map_speaker_names,
    _get_segement_speaker,
    _group_transcript_segements_by_speaker,
)


def export_text(
    transcript: dict,
    diarisation: Optional[List[Dict[str, Any]]] = None,
    speaker_mapping: Optional[dict] = None,
    datetimestr: Optional[str] = None,
    attendees: Optional[List[str]] = None,
):
    """Create text file from conversation.

    Exports the transcript as a text document while grouping segments by speaker (if diarisation is provided) and
    mapping speaker names (if speaker_mapping is provided).

    Parameters
    ----------
    transcript : Dict[str, Any]
        The transcript data structured as a dictionary with a key "segments" containing a list of dicts.
        Each dict has a "text" key with the corresponding transcript segment text and optionally a "speaker" key.
    diarisation : Optional[List[Dict[str, Any]]], default=None
        A list of diarisation data dictionaries. Each dictionary should have the keys "start", "end", and "speaker".
    speaker_mapping : Optional[Dict[str, str]], default=None
        A dictionary that maps speaker identifiers to speaker names. The key is the speaker identifier and the value
        is the speaker name.
    datetimestr : Optional[str], default=None
        A string representing the date and time of the meeting.
    attendees : Optional[List[str]], default=None
        A list of attendees in the meeting.

    Returns
    -------
    str
        The transcript exported as a text document.

    Examples
    --------
    >>> transcript = {"segments": [{"text": "Hello, world!", "speaker": "speaker_1"}]}
    >>> diarisation = None
    >>> speaker_mapping = {"speaker_1": "John"}
    >>> export_text(transcript, diarisation, speaker_mapping)
    'John: Hello, world!'
    """
    if diarisation is not None:
        transcript = _group_transcript_segements_by_speaker(transcript, diarisation)

    if speaker_mapping is not None:
        transcript = _map_speaker_names(transcript, speaker_mapping)
    else:
        speaker_mapping = {}

    doc = ""

    previous_speaker = None

    if datetimestr is not None:
        doc += "Meeting Transcript from " + datetimestr
    if attendees is not None:
        doc += " with " + ", ".join(attendees)
    print("\n\n")

    for seg in transcript["segments"]:
        speaker = _get_segement_speaker(seg, speaker_mapping)

        if diarisation is not None:
            if speaker != previous_speaker:
                doc += f"\n\n{speaker}:"
                previous_speaker = speaker

        doc += f" {seg['text']}"

    return doc
