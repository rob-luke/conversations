from unittest.mock import patch, MagicMock
from conversations.ai._chatgpt import summarise, query, _get_client
from conversations.config import settings
import conversations.ai._chatgpt as chatgpt_module


def test_summarise_uses_settings_model():
    """Test that summarise uses the model from settings."""
    mock_client = MagicMock()
    with patch.object(chatgpt_module, "_get_client", return_value=mock_client):
        summarise("test transcript")
        mock_client.chat.completions.create.assert_called_once()
        _, kwargs = mock_client.chat.completions.create.call_args
        assert kwargs["model"] == settings.openai_text_model


def test_query_uses_settings_model():
    """Test that query uses the model from settings."""
    mock_client = MagicMock()
    with patch.object(chatgpt_module, "_get_client", return_value=mock_client):
        query("test transcript", "test query")
        mock_client.chat.completions.create.assert_called_once()
        _, kwargs = mock_client.chat.completions.create.call_args
        assert kwargs["model"] == settings.openai_text_model
