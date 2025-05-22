from unittest.mock import patch
from openai import OpenAI
from conversations.ai._chatgpt import summarise, query
from conversations.config import settings


@patch.object(OpenAI, "chat")
def test_summarise_uses_settings_model(mock_chat):
    summarise("test transcript")
    mock_chat.completions.create.assert_called_once()
    # Check the model argument in the call_args
    _, kwargs = mock_chat.completions.create.call_args
    assert kwargs["model"] == settings.openai_text_model


@patch.object(OpenAI, "chat")
def test_query_uses_settings_model(mock_chat):
    query("test transcript", "test query")
    mock_chat.completions.create.assert_called_once()
    # Check the model argument in the call_args
    _, kwargs = mock_chat.completions.create.call_args
    assert kwargs["model"] == settings.openai_text_model
