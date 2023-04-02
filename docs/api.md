# Application Programming Interface

## Conversations Interface

::: conversations.Conversation
    handler: python
    options:
      show_root_heading: true
      show_source: false
      show_root_full_path: true
      heading_level: 4
      members:
        - __init__
        - transcribe
        - diarise
        - shortened_transcript
        - summarise
        - query
        - save
        - report
        - export_text

::: conversations.load_conversation
    handler: python
    options:
      show_root_heading: true
      show_source: false
      show_root_full_path: true
      heading_level: 4

## Low-Level Interface

### Transcription

::: conversations.transcribe.whisper.process
    handler: python
    options:
      show_root_heading: true
      show_source: false
      show_root_full_path: true
      heading_level: 4

### Diarisation

::: conversations.diarise.simple.process
    handler: python
    options:
      show_root_heading: true
      show_source: false
      show_root_full_path: true
      heading_level: 4

### Report

::: conversations.report.generate
    handler: python
    options:
      show_root_heading: true
      show_source: false
      show_root_full_path: true
      heading_level: 4

::: conversations.report.export_text
    handler: python
    options:
      show_root_heading: true
      show_source: false
      show_root_full_path: true
      heading_level: 4
