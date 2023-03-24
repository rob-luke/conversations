from conversations import Conversation, load_conversation
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
