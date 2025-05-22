from conversations.config import settings


def test_load_settings():
    assert settings.openai_text_model == "gpt-4.1-mini"
