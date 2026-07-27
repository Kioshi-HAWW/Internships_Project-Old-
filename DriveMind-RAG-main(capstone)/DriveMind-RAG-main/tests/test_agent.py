"""
test_agent.py — Integration-level tests for agent_service using mocked Gemini calls.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch


@patch("app.services.agent_service._init_model")
@patch("app.tools.search_library_tool.handle_search_library")
@pytest.mark.asyncio
async def test_answer_returns_answer_and_sources(mock_search, mock_init_model):
    """
    Simulate the agent returning a final text response on the first turn
    (no tool call needed — Gemini skips straight to answer).
    """
    # Build a fake response with text only (no function call)
    fake_part = MagicMock()
    fake_part.function_call.name = ""  # no function call
    fake_part.text = "The library says Python was created by Guido van Rossum."

    fake_candidate = MagicMock()
    fake_candidate.content.parts = [fake_part]

    fake_response = MagicMock()
    fake_response.candidates = [fake_candidate]

    fake_chat = MagicMock()
    fake_chat.send_message.return_value = fake_response

    mock_model = MagicMock()
    mock_model.start_chat.return_value = fake_chat
    mock_init_model.return_value = mock_model

    from app.services.agent_service import answer
    result = await answer("Who created Python?")

    assert "answer" in result
    assert "sources" in result
    assert "Guido" in result["answer"]
