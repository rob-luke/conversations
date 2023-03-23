from pathlib import Path


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

    def __init__(self, recording: Path, num_speakers: int = 2):
        """Initialise Conversations class.
        Parameters
        ----------
        recording : pathlib.Path
            Path to the conversation recording.
        num_speakers : int
            The number of speakers in the conversation.
        Returns
        -------
        conversation : Conversation
            Instance of Conversation.
        """
        self._recording = recording
        self._num_speakers = num_speakers

    def transcribe(self, method: str = "whisper", model: str = "medium.en"):
        """Transcribe a conversation."""
        from .transcribe import whisper

        self._transcription = whisper.process(
            audio_file=self._recording, model_name=model
        )

    def diarise(self, method: str = "simple"):
        """Diarise a conversation."""
        from .diarise import simple

        self._diarisation = simple.process(
            audio_file=self._recording, num_speakers=self._num_speakers
        )

    def report(self):
        """Generate a report of a conversation."""
        from .report import generate

        return generate(
            transcript=self._transcription,
            audio_file=self._recording,
            diarisation=self._diarisation,
        )
