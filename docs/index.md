# Conversations

[![PyPI - Version](https://img.shields.io/pypi/v/conversations.svg)](https://pypi.org/project/conversations)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/conversations.svg)](https://pypi.org/project/conversations)
[![Tests](https://github.com/rob-luke/conversations/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/rob-luke/conversations/actions/workflows/test.yml)

Introducing "Conversations" - a Python package designed to explore the true potential of conversational analysis.
With its ability to transcribe, diarise, and generate visually appealing HTML reports, "Conversation" empowers you to delve deeper into the intricacies of human communication.
Recognizing that conversations are brimming with meaning conveyed not just through language, but also through key acoustic features like loudness, intonation, and speech rate,
this package brings forth an indispensable tool for understanding and interpreting the wealth of information embedded in everyday exchanges.
`Conversations` enables you to analyze and comprehend the complex world of human interaction.


## Documentation

Comprehensive documentation including overview, api, and examples can be found [here](rob-luke.github.io/conversations/).


## Installation

```console
pip install conversations
```

## Usage

```python
from pathlib import Path
from conversations import Conversation

audio_file = Path('/path/to/audio.mp4')
speaker_mapping={"0": "Alice", "1": "Bob", "2": "Sam"}

conversation = Conversation(recording=audio_file)

conversation.transcribe()
conversation.diarise()
html_report = conversation.report(speaker_mapping=speaker_mapping)

with open('conversation.html', 'w') as f:
    f.write(html_report.render())
```
