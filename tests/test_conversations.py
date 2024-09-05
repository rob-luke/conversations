from conversations import Conversation, load_conversation
from conversations._conversations import _create_default_save_filename
from pathlib import Path
import pooch
import dominate
import os
import tempfile
import pytest
import pickle
from datetime import datetime, timezone, timedelta


audio_file = Path(
    pooch.retrieve(
        url="https://project-test-data-public.s3.amazonaws.com/test_audio.m4a",
        known_hash="md5:77d8b60c54dffbb74d48c4a65cd59591",
    )
)


def test_conv_type():
    conv = Conversation(recording=audio_file)
    assert isinstance(conv, Conversation)


def test_conv_report():
    conv = Conversation(recording=audio_file)
    conv.transcribe()
    html_report = conv.report()
    assert isinstance(html_report, dominate.document)


def test_save_and_load():
    # Create a temporary directory to store the conversation file
    with tempfile.TemporaryDirectory() as temp_dir:
        conversation_file = Path(temp_dir) / "conversation.pkl"

        # Create a Conversation object, transcribe, and diarise
        conversation = Conversation(recording=Path(audio_file))
        conversation.transcribe()
        conversation.diarise()

        # Save the Conversation object to disk
        conversation.save(conversation_file)

        # Load the Conversation object from disk
        loaded_conversation = load_conversation(conversation_file)

        # Check if the loaded Conversation object has the same attributes as the original
        assert loaded_conversation._recording == conversation._recording
        assert loaded_conversation._num_speakers == conversation._num_speakers
        assert loaded_conversation._transcription == conversation._transcription
        assert loaded_conversation._diarisation == conversation._diarisation

        # Remove the temporary file
        os.remove(conversation_file)


def test_invalid_conversation():
    # Create a temporary directory to store the invalid conversation file
    with tempfile.TemporaryDirectory() as temp_dir:
        invalid_conversation_file = Path(temp_dir) / "invalid_conversation.pkl"

        # Save a non-Conversation object to disk
        with open(invalid_conversation_file, "wb") as file:
            pickle.dump("not a conversation object", file)

        # Try to load the invalid object and check if a ValueError is raised
        with pytest.raises(
            ValueError,
            match="The loaded object is not an instance of the Conversation class.",
        ):
            load_conversation(invalid_conversation_file)

        # Remove the temporary file
        os.remove(invalid_conversation_file)


@pytest.mark.parametrize(
    "audio_file_path, expected_conversation_file_path",
    [
        ("my-audio-file.mp3", "my-audio-file.conv"),
        ("my-audio-file.ext", "my-audio-file.conv"),
        ("my-audio-file.m4a", "my-audio-file.conv"),
        ("my-audio-file.wav", "my-audio-file.conv"),
        ("my-audio-file.mov", "my-audio-file.conv"),
        ("my-audio-file.mkv", "my-audio-file.conv"),
        ("my audio file.mp3", "my audio file.conv"),
        ("my_audio_file.mp3", "my_audio_file.conv"),
        ("./my-audio-file.mp3", "./my-audio-file.conv"),
        ("../../my-audio-file.mp3", "../../my-audio-file.conv"),
        ("/path/to/my/file/my-audio-file.mp3", "/path/to/my/file/my-audio-file.conv"),
        ("/path/to/my file/my-audio-file.mp3", "/path/to/my file/my-audio-file.conv"),
    ],
)
def test_create_default_filename(audio_file_path, expected_conversation_file_path):
    assert _create_default_save_filename(Path(audio_file_path)) == Path(
        expected_conversation_file_path
    )


def test_save_and_reload_conversation(tmp_path: Path):
    # Create a dummy recording file
    recording_path = audio_file
    recording_path.touch()

    # Create a new conversation
    conversation = Conversation(recording=recording_path)

    # Save the conversation with the default filename
    conversation.save()

    # Check if the saved conversation file exists
    saved_conversation_path = _create_default_save_filename(recording_path)
    assert saved_conversation_path.is_file()

    # Load the existing saved conversation with the default filename
    loaded_conversation = Conversation(recording=recording_path, reload=True)

    # Check if the loaded conversation has the same recording path as the original conversation
    assert loaded_conversation._recording == conversation._recording
    assert loaded_conversation._num_speakers == conversation._num_speakers


def test_meeting_datetime():
    # Test with the provided meeting_datetime parameter
    meeting_datetime = datetime(2022, 1, 1, 12, 0, 0, 0, tzinfo=timezone.utc)
    conv_with_datetime = Conversation(
        recording=audio_file, meeting_datetime=meeting_datetime, reload=False
    )
    assert abs(conv_with_datetime._meeting_datetime - meeting_datetime) < timedelta(
        seconds=1
    )

    # Test without the meeting_datetime parameter (get from file metadata)
    conv_without_datetime = Conversation(recording=audio_file, reload=False)
    file_metadata_datetime = conv_without_datetime._extract_datetime_from_file(
        audio_file
    )
    assert abs(
        conv_without_datetime._meeting_datetime - file_metadata_datetime
    ) < timedelta(seconds=1)


def test_attendees():
    attendees = ["Alice", "Bob", "Charlie"]
    conv_with_attendees = Conversation(
        recording=audio_file, attendees=attendees, reload=False, num_speakers=None
    )
    assert conv_with_attendees._attendees == attendees
    assert conv_with_attendees._num_speakers == len(attendees)


def test_num_speakers_and_attendees_mismatch():
    attendees = ["Alice", "Bob", "Charlie"]
    num_speakers = 2
    with pytest.raises(
        ValueError, match="The number of speakers must match the number of attendees."
    ):
        Conversation(
            recording=audio_file,
            num_speakers=num_speakers,
            attendees=attendees,
            reload=False,
        )


def test_num_speakers_and_attendees():
    attendees = ["Alice", "Bob", "Charlie"]
    num_speakers = len(attendees)
    conv_with_speakers_attendees = Conversation(
        recording=audio_file,
        num_speakers=num_speakers,
        attendees=attendees,
        reload=False,
    )
    assert conv_with_speakers_attendees._attendees == attendees
    assert conv_with_speakers_attendees._num_speakers == num_speakers


@pytest.fixture
def conversation():
    return Conversation(recording=audio_file, reload=True)


def test_summarise_new_summary(conversation):
    conversation.transcribe()
    summary = conversation.summarise(force=True, print_summary=False)
    assert isinstance(summary, str)
    assert len(summary) > 0


def test_summarise_existing_summary(conversation):
    conversation.transcribe()
    conversation._summary_automated = "Test summary"
    summary = conversation.summarise(force=False, print_summary=False)
    assert summary == "Test summary"


def test_summarise_force_new_summary(conversation):
    conversation.transcribe()
    conversation._summary_automated = "Test summary"
    summary = conversation.summarise(force=True, print_summary=False)
    assert summary != "Test summary"
    assert isinstance(summary, str)
    assert len(summary) > 0
