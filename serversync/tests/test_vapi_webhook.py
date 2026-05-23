import pytest
from unittest.mock import patch
from uuid import uuid4


def _end_of_call_payload(appointment_id: str, outcome: str, new_time=None):
    payload = {
        "message": {
            "type": "end-of-call-report",
            "call": {
                "id": "call_abc",
                "metadata": {
                    "appointment_id": appointment_id,
                    "outcome": outcome,
                },
            },
            "analysis": {"summary": "Patient confirmed."},
        }
    }
    if new_time:
        payload["message"]["call"]["metadata"]["new_time"] = new_time
    return payload


@patch("routes.vapi.update_appointment")
@patch("routes.vapi.get_supabase")
def test_vapi_confirmed_updates_status(mock_db, mock_update, app_client):
    from models import AppointmentStatus, AppointmentUpdate
    appt_id = str(uuid4())
    resp = app_client.post("/webhook/vapi", json=_end_of_call_payload(appt_id, "confirmed"))

    assert resp.status_code == 200
    mock_update.assert_called_once_with(
        mock_db.return_value,
        appt_id,
        AppointmentUpdate(status=AppointmentStatus.confirmed),
    )


@patch("routes.vapi.update_appointment")
@patch("routes.vapi.get_supabase")
def test_vapi_cancelled_updates_status(mock_db, mock_update, app_client):
    from models import AppointmentStatus, AppointmentUpdate
    appt_id = str(uuid4())
    resp = app_client.post("/webhook/vapi", json=_end_of_call_payload(appt_id, "cancelled"))

    assert resp.status_code == 200
    mock_update.assert_called_once_with(
        mock_db.return_value,
        appt_id,
        AppointmentUpdate(status=AppointmentStatus.cancelled),
    )


def test_vapi_non_end_call_event_ignored(app_client):
    payload = {"message": {"type": "status-update", "call": {"id": "call_xyz"}}}
    resp = app_client.post("/webhook/vapi", json=payload)
    assert resp.status_code == 200
