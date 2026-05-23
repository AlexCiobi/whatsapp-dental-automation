import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
from uuid import uuid4


_BOOKING_PAYLOAD = {
    "patient_name": "Ravi Kumar",
    "patient_phone": "+919876543210",
    "appointment_time": "2026-06-01T10:00:00+00:00",
    "doctor_name": "Dr. Sharma",
    "clinic_name": "Smile Clinic",
    "owner_phone": "+919111111111",
}


@patch("routes.appointments.send_text_message", return_value=True)
@patch("routes.appointments.get_supabase")
def test_new_booking_notifies_owner(mock_db, mock_send, app_client):
    mock_db.return_value.table.return_value.insert.return_value.execute.return_value.data = [
        {**_BOOKING_PAYLOAD, "id": str(uuid4()), "status": "scheduled", "created_at": datetime.now(timezone.utc).isoformat(), "notes": None}
    ]

    resp = app_client.post("/appointments", json=_BOOKING_PAYLOAD)

    assert resp.status_code == 201
    mock_send.assert_called()
    calls = mock_send.call_args_list
    owner_calls = [c for c in calls if c[0][0] == "+919111111111"]
    assert len(owner_calls) == 1
