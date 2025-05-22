from pydantic_settings import BaseSettings

class OpenAISettings(BaseSettings):
    open_ai_text_model: str = "gpt-4.1-mini"

settings = OpenAISettings()
