# Description: Example of using the Conversation class to analyse a podcast
from pathlib import Path
from conversations import Conversation
import pooch

# Properties of the conversation
cloud_file = "https://project-test-data-public.s3.amazonaws.com/test_audio.m4a"
speaker_mapping = {"0": "Alice", "1": "Bob", "2": "Sam"}

# Download audio file
audio_file = pooch.retrieve(
    url=cloud_file,
    known_hash="md5:77d8b60c54dffbb74d48c4a65cd59591",
    fname="podcast.m4a"
)

# Process the conversation
conversation = Conversation(recording=Path(audio_file), num_speakers=3, speaker_mapping=speaker_mapping)
conversation.transcribe(model="openai.en")
conversation.diarise()
conversation.save()

# Generate interactive html report
html_report = conversation.report(audio_file=cloud_file)
with open('conversation.html', 'w') as f:
    f.write(html_report.render())

# Generate a text report
text_report = conversation.export_text()
with open('conversation.txt', 'w') as f:
    f.write(text_report)
