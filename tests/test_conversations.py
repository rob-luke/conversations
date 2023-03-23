from conversations import Conversation
from pathlib import Path
import pooch
import dominate


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
    conv.diarise()
    html_report = conv.report()
    assert isinstance(html_report, dominate.document)
