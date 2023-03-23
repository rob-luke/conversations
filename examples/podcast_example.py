from pathlib import Path
from conversations import Conversation
import pooch


cloud_file = "https://project-test-data-public.s3.amazonaws.com/test_audio.m4a"

audio_file = pooch.retrieve(
    url=cloud_file,
    known_hash="md5:77d8b60c54dffbb74d48c4a65cd59591",
)

conversation = Conversation(recording=Path(audio_file), num_speakers=3)

conversation.transcribe(model="openai.en")
conversation.diarise()
html_report = conversation.report(audio_file=cloud_file)


with open('conversation.html', 'w') as f:
    f.write(html_report.render())
