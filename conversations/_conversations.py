from pathlib import Path
from typing import Any, Dict, List, Optional
import pickle


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
        num_speakers: int = 2,
        reload: bool = False,
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

        Returns
        -------
        conversation : Conversation
            Instance of Conversation.
        """
        self._recording = recording
        self._num_speakers = num_speakers
        self._transcription: Optional[Dict[str, str]] = None
        self._diarisation: Optional[List[Dict[str, Any]]] = None

        if reload:
            default_file_path = str(_create_default_save_filename(recording))
            try:
                loaded_conversation = load_conversation(default_file_path)
                self.__dict__.update(loaded_conversation.__dict__)
            except FileNotFoundError:
                print(f"No saved conversation was found at {default_file_path}.")

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

    def report(self, audio_file=None, speaker_mapping=None):
        """Generate a report of a conversation."""
        from .report import generate

        if audio_file is None:
            audio_file = self._recording

        return generate(
            transcript=self._transcription,
            audio_file=audio_file,
            diarisation=self._diarisation,
            speaker_mapping=speaker_mapping,
        )

    def export_text(self, speaker_mapping=None):
        """Generate a report of a conversation."""
        from .report import export_text

        return export_text(
            transcript=self._transcription,
            diarisation=self._diarisation,
            speaker_mapping=speaker_mapping,
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
