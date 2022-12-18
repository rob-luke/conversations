# Conversations

[![PyPI - Version](https://img.shields.io/pypi/v/conversations.svg)](https://pypi.org/project/conversations)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/conversations.svg)](https://pypi.org/project/conversations)


Rich analysis of conversations.

## Installation

```console
pip install conversations
```


## Usage

```python
from conversations import report
from conversations.transcribe import whisper


audio_file = '/path/to/audio.mp4'

transcript = whisper.process(audio_file=audio_file, model_name="tiny.en")
html_report = report.generate(transcript=transcript, audio_file=audio_file)

with open('conversation.html', 'w') as f:
    f.write(html_report.render())
```



