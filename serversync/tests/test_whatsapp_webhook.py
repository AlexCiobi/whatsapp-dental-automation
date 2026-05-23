import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
from uuid import uuid4


_PATIENT_MSG_PAYLOAD = {
    "object": "whatsapp_business_account",
    "entry": [{
        "id": "entry_1",
        "changes": [{
            "value": {
                "messaging_product": "whatsapp",
                "metadata": {"display_phone_number": "1234567890", "phone_number_id": "123"},
                "messages": [{
                    "from": "+919876543210",
                    "id": "wamid.ABC123",
                    "timestamp": "1748000000",
                    "text": {"body": "I want to cancel"},
                    "type": "text",
                }],
            }
        }],
    }],
}


def test_webhook_verification(app_client, monkeypatch):
    monkeypatch.setenv("WHATSAPP_VERIFY_TOKEN", "verify_me")
    resp = app_client.get(
        "/webhook/whatsapp",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "verify_me",
            "hub.challenge": "challenge_abc",
        },
    )
    assert resp.status_code == 200
    assert resp.text == "challenge_abc"


def test_webhook_verification_fails_bad_token(app_client, monkeypatch):
    monkeypatch.setenv("WHATSAPP_VERIFY_TOKEN", "verify_me")
    resp = app_client.get(
        "/webhook/whatsapp",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "wrong_token",
            "hub.challenge": "challenge_abc",
        },
    )
    assert resp.status_code == 403


@patch("routes.whatsapp.is_owner", return_value=False)
@patch("routes.whatsapp.parse_intent")
@patch("routes.whatsapp.get_appointments_by_phone")
@patch("routes.whatsapp.send_text_message", return_value=True)
@patch("routes.whatsapp.get_supabase")
def test_patient_cancel_message(
    mock_db, mock_send, mock_get_appts, mock_parse, mock_is_owner, app_client
):
    from models import ParsedIntent, IntentType, Appointment, AppointmentStatus
    appt = Appointment(
        id=uuid4(),
        patient_name="Ravi Kumar",
        patient_phone="+919876543210",
        appointment_time=datetime(2026, 6, 1, 10, 0, tzinfo=timezone.utc),
        doctor_name="Dr. Sharma",
        clinic_name="Smile Clinic",
        status=AppointmentStatus.scheduled,
        created_at=datetime.now(timezone.utc),
    )
    mock_get_appts.return_value = [appt]
    mock_parse.return_value = ParsedIntent(type=IntentType.cancel)

    resp = app_client.post("/webhook/whatsapp", json=_PATIENT_MSG_PAYLOAD)

    assert resp.status_code == 200
    mock_send.assert_called_once()


def test_webhook_post_no_messages_returns_ok(app_client):
    payload = {"object": "whatsapp_business_account", "entry": []}
    resp = app_client.post("/webhook/whatsapp", json=payload)
    assert resp.status_code == 200
