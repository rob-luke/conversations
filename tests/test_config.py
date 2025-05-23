from conversations.config import settings


def test_load_settings():
    assert settings.openai_text_model == "gpt-4.1-mini"


def test_openai_speech_model_default_value():
    assert settings.openai_speech_model == "whisper-1"


def test_openai_token_settings_default_values():
    """Test that the token settings have the correct default values."""
    assert settings.max_prompt_tokens == 900000
