from conversations import Conversation, load_conversation
from conversations._conversations import _create_default_save_filename
from pathlib import Path
import pooch
import dominate
import os
import tempfile
import pytest
import pickle


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
