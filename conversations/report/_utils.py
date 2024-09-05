import numpy as np


def _map_speaker_names(transcript: dict, speaker_mapping: dict) -> dict:
    """Map old speaker names to new speaker names in transcript.

    Parameters
    ----------
    transcript : dict
        Transcript from transcribe module.
    speaker_mapping : dict
        Mapping of old speaker names to new speaker names.

    Returns
    -------
    mapped_transcript : dict
        Transcript with updated speaker names.
    """
    mapped_segments = []

    for seg in transcript["segments"]:
        mapped_seg = seg.copy()
        if "speaker" in seg and seg["speaker"] in speaker_mapping:
            mapped_seg["speaker"] = speaker_mapping[seg["speaker"]]
        mapped_segments.append(mapped_seg)

    return {"segments": mapped_segments}


def _get_segement_speaker(segment, speaker_mapping: dict) -> str:
    """Get speaker label from segment."""
    if "speaker" in segment:
        speaker_name = segment["speaker"]
        if speaker_name in speaker_mapping:
            speaker_name = speaker_mapping[speaker_name]

        return speaker_name
    else:
        return "unknown"


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


def _group_transcript_segements_by_speaker(
    transcript, diarization, seconds_per_segment=20
):
    """Group transcript segments by speaker."""
    if "speaker" in transcript["segments"][0]:
        # Already grouped by speaker
        return transcript

    else:
        speaker_segments = []
        current_speaker = ""
        for seg in transcript["segments"]:
            start = seg["start"]
            stop = seg["end"]
            mid_time = start + ((stop - start) / 2)

            speaker = _find_current_speaker(mid_time, diarization)

            if speaker != current_speaker:
                current_speaker = speaker
                speaker_segments.append(
                    {
                        "speaker": speaker,
                        "text": seg["text"],
                        "start": start,
                        "end": stop,
                    }
                )
            else:
                if stop - speaker_segments[-1]["start"] > seconds_per_segment:
                    speaker_segments.append(
                        {
                            "speaker": speaker,
                            "text": seg["text"],
                            "start": start,
                            "end": stop,
                        }
                    )
                else:
                    speaker_segments[-1]["text"] += " " + seg["text"]
                    speaker_segments[-1]["end"] = stop

        return {"segments": speaker_segments}
