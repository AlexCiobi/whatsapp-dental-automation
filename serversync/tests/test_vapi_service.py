import pytest
import respx
import httpx
from datetime import datetime, timezone
from uuid import uuid4
from services.vapi_service import trigger_outbound_call, VAPI_CALLS_URL


@respx.mock
def test_trigger_outbound_call_success(monkeypatch):
    monkeypatch.setenv("VAPI_API_KEY", "vapi_test_key")
    monkeypatch.setenv("VAPI_PHONE_NUMBER_ID", "vapi_phone_123")

    appt_id = str(uuid4())
    route = respx.post(VAPI_CALLS_URL).mock(
        return_value=httpx.Response(201, json={"id": "call_abc123"})
    )

    result = trigger_outbound_call(
        patient_phone="+919876543210",
        patient_name="Ravi Kumar",
        appointment_id=appt_id,
        appointment_time=datetime(2026, 6, 1, 10, 0, tzinfo=timezone.utc),
        doctor_name="Dr. Sharma",
    )

    assert route.called
    assert result == "call_abc123"


@respx.mock
def test_trigger_outbound_call_returns_none_on_error(monkeypatch):
    monkeypatch.setenv("VAPI_API_KEY", "vapi_test_key")
    monkeypatch.setenv("VAPI_PHONE_NUMBER_ID", "vapi_phone_123")

    respx.post(VAPI_CALLS_URL).mock(
        return_value=httpx.Response(500, json={"error": "internal"})
    )

    result = trigger_outbound_call(
        patient_phone="+919876543210",
        patient_name="Ravi Kumar",
        appointment_id=str(uuid4()),
        appointment_time=datetime(2026, 6, 1, 10, 0, tzinfo=timezone.utc),
        doctor_name="Dr. Sharma",
    )

    assert result is None
