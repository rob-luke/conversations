# Conversations

[![PyPI - Version](https://img.shields.io/pypi/v/conversations.svg)](https://pypi.org/project/conversations)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/conversations.svg)](https://pypi.org/project/conversations)
[![Tests](https://github.com/rob-luke/conversations/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/rob-luke/conversations/actions/workflows/test.yml)

Introducing "Conversations" - a Python package designed to
explore the true potential of conversational analysis.
With its ability to transcribe, diarise, and generate visually appealing HTML reports,
"Conversation" empowers you to delve deeper into the intricacies of human communication.
Recognizing that conversations are brimming with meaning
conveyed not just through language,
but also through key acoustic features like loudness, intonation, and speech rate,
this package brings forth an indispensable tool for understanding and
interpreting the wealth of information embedded in everyday exchanges.
`Conversations` enables you to analyse and comprehend
the complex world of human interaction.

## Documentation

Comprehensive documentation, including overview, API, and examples,
can be found [here](https://rob-luke.github.io/conversations/).

## Installation

```console
pip install conversations
```

## Usage

```python
from pathlib import Path
from conversations import Conversation

# Information about the conversation
audio_file = Path('/path/to/audio.mp4')
speaker_mapping={"0": "Alice", "1": "Bob", "2": "Sam"}

# Load the conversation
conversation = Conversation(recording=audio_file, speaker_mapping=speaker_mapping)

# Process the conversation
conversation.transcribe()
conversation.diarise()
conversation.save()

# Generate an interactive HTML version of the conversation
html_report = conversation.report()
with open('conversation.html', 'w') as f:
    f.write(html_report.render())

# Generate a text file of the conversation
text_report = conversation.export_text()
with open('conversation.txt', 'w') as f:
    f.write(text_report)

# Generate a text file summarising the conversation
summary = conversation.summarise()
with open('conversation-summary.txt', 'w') as f:
    f.write(summary)

# Query the conversation
answer = conversation.query("What was the value of operating cash flow we were discussing?")


print(f"The answer to your query is: {answer}")    
print(summary)


# The answer to your query is: The value of operating cash 
# flow being discussed was $210 million in the last 12 months.


# Summary:
# In the meeting, Alice, Sam and Bob discuss the financial state of
# businesses, the challenges of companies going private, and the
# evolution of private equity firms' return expectations. They
# also touch on the industry's early risk-taking nature. Bob
# mentions historical deals as examples of the early risk-taking
# nature of private equity firms.
# 
# Key Points:
# 1. Challenges of companies going private
#    Alice: "Challenges of companies going private, especially in
#    terms of cutting expenses and finding new ways to pay
#    employees who were previously compensated with stocks."
# 2. Private equity firms' return expectations
#    Sam: "What are private equity firms' return expectations
#    when purchasing a company?"
# 3. Evolution of the private equity industry
#    Bob: "The industry has evolved over time, with early private
#    equity firms taking on riskier ventures,
#    similar to venture capitalists."
# ...
# 
# Action Items:
# None discussed in the meeting.
# 
# 20 Keywords (most to least relevant):
# 1. Financial state
# 2. Business
# 3. Operating cash flow
# ...
# 
# 10 Concepts/Themes (most to least relevant):
# 1. Financial challenges
# 2. Going private
# 3. Private equity
# ...
# 
# Most unexpected aspect of the conversation:
# The most unexpected aspect of the conversation was the mention of
# historical deals like RJR Nabisco and TWA Airlines as examples
# of the early risk-taking nature of private equity firms.
# 
# Concepts/Topics explained in the transcript:
# 1. Private equity firms' return expectations:
#    Bob explains that the industry has evolved over time,
#    with early private equity firms taking on riskier ventures,
#    similar to venture capitalists. No inaccuracies were identified.
# 
# Tone of the conversation:
# Overall tone: Informative and analytical
# Alice's tone: Concerned and analytical
# Bob's tone: Informative and explanatory
# Sam's tone: Inquisitive

```
