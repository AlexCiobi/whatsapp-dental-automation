import pytest
import respx
import httpx
from services.whatsapp_service import send_text_message, GRAPH_API_URL


@respx.mock
def test_send_text_message_success(monkeypatch):
    monkeypatch.setenv("WHATSAPP_TOKEN", "test_token")
    monkeypatch.setenv("WHATSAPP_PHONE_NUMBER_ID", "123")

    route = respx.post(f"{GRAPH_API_URL}/123/messages").mock(
        return_value=httpx.Response(200, json={"messages": [{"id": "wamid.123"}]})
    )

    result = send_text_message("+919876543210", "Hello test")

    assert route.called
    assert result is True


@respx.mock
def test_send_text_message_handles_api_error(monkeypatch):
    monkeypatch.setenv("WHATSAPP_TOKEN", "test_token")
    monkeypatch.setenv("WHATSAPP_PHONE_NUMBER_ID", "123")

    respx.post(f"{GRAPH_API_URL}/123/messages").mock(
        return_value=httpx.Response(400, json={"error": {"message": "bad request"}})
    )

    result = send_text_message("+919876543210", "Hello")

    assert result is False
