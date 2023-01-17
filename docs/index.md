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
from pathlib import Path
from conversations import Conversation

audio_file = Path('/path/to/audio.mp4')

conversation = Conversation(recording=audio_file)

conversation.transcribe()
conversation.diarise()
html_report = conversation.report()

with open('conversation.html', 'w') as f:
    f.write(html_report.render())
```



