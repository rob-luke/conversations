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
        num_speakers: int = 2,
        reload: bool = True,
        speaker_mapping: Optional[Dict[str, str]] = None,
        meeting_datetime: Optional[datetime] = None,
        attendees: Optional[List[str]] = None,
        transcription: Optional[Dict[str, str]] = None,
        transcription_shortened: Optional[str] = None,
        summary: Optional[str] = None,
        summary_automated: Optional[str] = None,
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
        self._transcription = transcription
        self._diarisation: Optional[List[Dict[str, Any]]] = None
        self._speaker_mapping = speaker_mapping
        self._summary = summary
        self._summary_automated = summary_automated
        self._transcription_shortened = transcription_shortened

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

    def transcribe(
        self,
        method: str = "assembly",
        model: str = "nano",
        prompt: str | None = " - How are you? - I'm fine, thank you.",
        language: str = "en",
    ):
        """
        Transcribe a conversation using the specified method and model.

        Parameters
        ----------
        method : str, optional
            The transcription method to use, defaults to "assembly".
            Can be one of whisper or assembly.
        model : str, optional
            The model to be used for transcription, must be one of tiny, base, small, large,
            medium, tiny.en, base.en, small.en, medium.en, and openai.en, best, nano.
            Defaults to "nano".
        prompt : str, None, optional
            An optional prompt to be used for transcription, defaults to None.
        language : str, optional
            The language of the conversation, defaults to "en".

        Returns
        -------
        None

        Raises
        ------
        RuntimeError
            If the conversation has already been transcribed.
        ValueError
            If an invalid model name is provided.
        NotImplementedError
            If the method is not supported.
        """
        if self._transcription is not None:
            raise RuntimeError("The conversation has already been transcribed.")

        available_models = [
            "tiny",
            "base",
            "small",
            "large",
            "medium",
            "tiny.en",
            "base.en",
            "small.en",
            "medium.en",
            "openai.en",
            "nano",
            "best",
        ]
        if model not in available_models:
            raise ValueError(
                f"Invalid model '{model}'. Must be one of {available_models}."
            )

        if method == "whisper":
            from .transcribe import whisper

            self._transcription = whisper.process(
                audio_file=self._recording,
                model_name=model,
                prompt=prompt,
                language=language,
            )
        elif method == "assembly":
            from .transcribe import assembly

            self._transcription = assembly.process(
                audio_file=self._recording, model_name=model, language=language
            )

            # by default, we use assembly to diarise the conversation too
            self._diarisation = [
                {
                    "note": "diairisation performed by assembly and transcript contains speaker labels"
                }
            ]
        else:
            raise NotImplementedError(
                f"Transcription method '{method}' is not supported."
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

    def summarise(
        self,
        force: bool = False,
        print_summary: bool = True,
        system_prompt: Optional[str] = None,
        summary_prompt: Optional[str] = None,
        append_prompt: Optional[str] = None,
    ):
        """Generate a summary of the conversation.

        Parameters
        ----------
        force : bool
            If True, generate a new summary even if one already exists.
        print_summary : bool
            If True, print the summary to the console.
        system_prompt : str or None
            The system prompt to use when generating the summary.
        summary_prompt : str or None
            The summary prompt to use when generating the summary.
        append_prompt : str or None
            The append prompt to use when generating the summary.

        Returns
        -------
        summary : str
            The generated summary.
        """
        short_transcript = self.shortened_transcript()

        if (self._summary_automated is None) or force:
            from .ai import summarise

            self._summary_automated = summarise(
                short_transcript,
                system_prompt,
                summary_prompt,
                append_prompt,
            )

        if print_summary:
            print(self._summary_automated)

        return self._summary_automated

    def query(
        self,
        query: str,
        print_summary: bool = True,
        system_prompt: Optional[str] = None,
        append_prompt: Optional[str] = None,
    ):
        """Query the conversation.

        Parameters
        ----------
        query : str
            The query to ask the conversation.
        print_summary : bool
            If True, print the summary to the console.
        system_prompt : str or None
            The system prompt to use when generating the summary.
        append_prompt : str or None
            The append prompt to use when generating the summary.

        Returns
        -------
        summary : str
            The generated query response.
        """
        from .ai import query as query_fn

        short_transcript = self.shortened_transcript()

        answer = query_fn(short_transcript, query, system_prompt, append_prompt)
        if print_summary:
            print(answer)
        return answer

    def shortened_transcript(
        self, chunk_num_tokens: int = 7372, shorten_iterations: int = 2
    ) -> str:
        """
        Get the shortened transcript of the conversation.

        This method returns the previously shortened transcript if available.
        If not, it computes the shortened transcript first and then returns it.

        Parameters
        ----------
        chunk_num_tokens : int
            The number of tokens to use for each chunk.
            The default is 7372, which is 90% of the 8k model limit.
        shorten_iterations : int
            The number of iterations to use when shortening the transcript.

        Returns
        -------
        str
            The shortened transcript of the conversation.
        """
        if self._transcription_shortened is None:
            from .ai._shorten_transcript import _shorten_transcript

            self._transcription_shortened = _shorten_transcript(
                self.export_text(), chunk_num_tokens, shorten_iterations
            )

        return self._transcription_shortened


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
