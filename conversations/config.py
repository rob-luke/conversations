"""Configuration settings for the conversations package."""

from pydantic_settings import BaseSettings


class OpenAISettings(BaseSettings):
    """Settings for OpenAI API, primarily the text model."""

    open_ai_text_model: str = "gpt-4.1-mini"


settings = OpenAISettings()
