import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from models import IntentType
from services.ai_service import parse_intent


def _mock_claude_response(json_text: str):
    mock_content = MagicMock()
    mock_content.text = json_text
    mock_resp = MagicMock()
    mock_resp.content = [mock_content]
    return mock_resp


@patch("services.ai_service.anthropic_client")
def test_parse_cancel_intent(mock_client):
    mock_client.messages.create.return_value = _mock_claude_response(
        '{"intent": "cancel", "new_time": null, "patient_phone": null}'
    )

    result = parse_intent("I want to cancel my appointment", current_date="2026-06-01")

    assert result.type == IntentType.cancel
    assert result.new_time is None


@patch("services.ai_service.anthropic_client")
def test_parse_reschedule_intent(mock_client):
    mock_client.messages.create.return_value = _mock_claude_response(
        '{"intent": "reschedule", "new_time": "2026-06-02T14:00:00+00:00", "patient_phone": null}'
    )

    result = parse_intent("Can I move to tomorrow at 2pm?", current_date="2026-06-01")

    assert result.type == IntentType.reschedule
    assert result.new_time is not None


@patch("services.ai_service.anthropic_client")
def test_parse_owner_reschedule_with_phone(mock_client):
    mock_client.messages.create.return_value = _mock_claude_response(
        '{"intent": "reschedule", "new_time": "2026-06-03T10:00:00+00:00", "patient_phone": "+919876543210"}'
    )

    result = parse_intent(
        "Please reschedule +919876543210 to Thursday at 10am",
        current_date="2026-06-01",
        is_owner=True,
    )

    assert result.type == IntentType.reschedule
    assert result.patient_phone == "+919876543210"


@patch("services.ai_service.anthropic_client")
def test_parse_unknown_returns_unknown(mock_client):
    mock_client.messages.create.return_value = _mock_claude_response(
        '{"intent": "unknown", "new_time": null, "patient_phone": null}'
    )

    result = parse_intent("What are your opening hours?", current_date="2026-06-01")

    assert result.type == IntentType.unknown
