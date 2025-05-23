"""Configuration settings for the conversations package."""

from pydantic_settings import BaseSettings


class OpenAISettings(BaseSettings):
    """Settings for OpenAI API, primarily the text model."""

    openai_speech_model: str = "whisper-1"
    openai_text_model: str = "gpt-4.1-mini"
    max_prompt_tokens: int = 900000
    """Max tokens for AI processing chunks and final transcript target."""


settings = OpenAISettings()
