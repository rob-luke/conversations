from pathlib import Path
from typing import Any, Dict, List, Optional
import pickle
from datetime import datetime, timezone
import os


class Conversation:
    """Conversations class.

    This class is the core of the **Conversations** package.
    Use this class to manage your conversation and processing.

    Examples
    --------
    >>> conversation = Conversation(recording=Path("/path/to/file.m4a"))
    >>> conversation.transcribe()
    >>> conversation.diarise()
    >>> html_report = conversation.report()
    """

    def __init__(
        self,
        recording: Path,
        num_speakers: Optional[int] = 2,
        reload: bool = True,
        speaker_mapping: Optional[Dict[str, str]] = None,
        meeting_datetime: Optional[datetime] = None,
        attendees: Optional[List[str]] = None,  # Add the new parameter
    ):
        """Initialise Conversations class.

        Parameters
        ----------
        recording : pathlib.Path
            Path to the conversation recording.
        num_speakers : int
            The number of speakers in the conversation.
        reload : bool
            If True, try to load an existing saved conversation with the default filename.
            If False, create a new Conversation instance.
        speaker_mapping : Optional[Dict[str, str]]
            A dictionary mapping speaker IDs to speaker names.

        Returns
        -------
        conversation : Conversation
            Instance of Conversation.
        """
        self._recording = recording
        self._num_speakers = num_speakers
        self._transcription: Optional[Dict[str, str]] = None
        self._diarisation: Optional[List[Dict[str, Any]]] = None
        self._speaker_mapping = speaker_mapping

        if meeting_datetime is not None:
            self._meeting_datetime = meeting_datetime
        else:
            self._meeting_datetime = self._extract_datetime_from_file(recording)

        if reload:
            default_file_path = str(_create_default_save_filename(recording))
            try:
                loaded_conversation = load_conversation(default_file_path)
                self.__dict__.update(loaded_conversation.__dict__)
            except FileNotFoundError:
                print(f"No saved conversation was found at {default_file_path}.")

            # Overwrite reloaded values if user redefines them
            if speaker_mapping is not None:
                self._speaker_mapping = speaker_mapping

            if meeting_datetime is not None:
                self._meeting_datetime = meeting_datetime

        formatted_datetime = self._meeting_datetime.strftime("%Y-%m-%d %H:%M:%S %Z")
        print(f"Loaded conversation from: {formatted_datetime}")

        self._attendees = attendees  # Store the attendees
        if self._attendees is not None:
            print("Attendees:")
            for attendee in self._attendees:
                print(f"- {attendee}")

        # Set num_speakers based on attendees if not provided
        if num_speakers is None and attendees is not None:
            self._num_speakers = len(attendees)
        else:
            self._num_speakers = num_speakers

        # Verify that num_speakers is equal to the number of attendees
        if num_speakers is not None and attendees is not None:
            if num_speakers != len(attendees):
                raise ValueError(
                    "The number of speakers must match the number of attendees."
                )

    @staticmethod
    def _extract_datetime_from_file(file_path: Path) -> datetime:
        created_timestamp = os.path.getmtime(file_path)
        return datetime.fromtimestamp(created_timestamp, timezone.utc)

    def transcribe(self, method: str = "whisper", model: str = "medium.en"):
        """Transcribe a conversation."""
        from .transcribe import whisper

        if self._transcription is not None:
            print(
                "The conversation has already been transcribed. Skipping transcription."
            )
            return

        self._transcription = whisper.process(
            audio_file=self._recording, model_name=model
        )

    def diarise(self, method: str = "simple"):
        """Diarise a conversation."""
        from .diarise import simple

        if self._diarisation is not None:
            print("The conversation has already been diarised. Skipping diarisaton.")
            return

        self._diarisation = simple.process(
            audio_file=self._recording, num_speakers=self._num_speakers
        )

    def report(self, audio_file=None):
        """Generate a report of a conversation."""
        from .report import generate

        if audio_file is None:
            audio_file = self._recording

        return generate(
            transcript=self._transcription,
            audio_file=audio_file,
            diarisation=self._diarisation,
            speaker_mapping=self._speaker_mapping,
        )

    def export_text(self):
        """Export the transcript and diarisation as text."""
        from .report import export_text

        return export_text(
            transcript=self._transcription,
            diarisation=self._diarisation,
            speaker_mapping=self._speaker_mapping,
            datetimestr=self._meeting_datetime.strftime("%Y-%m-%d %H:%M:%S %Z"),
            attendees=self._attendees,
        )

    def save(self, file_path: Optional[str] = None) -> None:
        """Save the Conversation object to disk.

        Parameters
        ----------
        file_path : Optional[str]
            The path where the Conversation object will be saved.
            If None, a default filename based on the audio file path will be used.
        """
        if file_path is None:
            file_path = str(_create_default_save_filename(self._recording))

        with open(file_path, "wb") as file:
            pickle.dump(self, file)


def load_conversation(file_path: str) -> "Conversation":
    """Load a Conversation object from disk.

    Parameters
    ----------
    file_path : str
        The path to the file containing the saved Conversation object.

    Returns
    -------
    conversation : Conversation
        The loaded Conversation object.

    Raises
    ------
    ValueError
        If the loaded object is not an instance of the Conversation class.
    """
    with open(file_path, "rb") as file:
        conversation = pickle.load(file)

    if not isinstance(conversation, Conversation):
        raise ValueError(
            "The loaded object is not an instance of the Conversation class."
        )

    return conversation


def _create_default_save_filename(audio_file_path: Path) -> Path:
    """
    Create a default filename for saving conversations.

    Parameters
    ----------
    audio_file_path : pathlib.Path
        The path to the audio file.

    Returns
    -------
    pathlib.Path
        The default filename for saving the conversation.
    """
    file_stem = audio_file_path.stem
    default_filename = file_stem + ".conv"
    conversation_file_path = audio_file_path.with_name(default_filename)
    return conversation_file_path
