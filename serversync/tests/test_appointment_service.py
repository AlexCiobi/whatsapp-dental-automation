import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from unittest.mock import MagicMock
from models import Appointment, AppointmentStatus, AppointmentUpdate
from services.appointment_service import (
    get_appointment,
    update_appointment,
    get_upcoming_appointments,
    is_owner,
)


def _make_appt_dict(**kwargs):
    base = {
        "id": str(uuid4()),
        "patient_name": "Test Patient",
        "patient_phone": "+919876543210",
        "appointment_time": datetime(2026, 6, 1, 10, 0, tzinfo=timezone.utc).isoformat(),
        "doctor_name": "Dr. Test",
        "clinic_name": "Test Clinic",
        "status": "scheduled",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "notes": None,
    }
    base.update(kwargs)
    return base


def test_get_appointment_returns_appointment(mock_supabase):
    appt_id = str(uuid4())
    mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = _make_appt_dict(id=appt_id)

    result = get_appointment(mock_supabase, appt_id)

    assert result is not None
    assert str(result.id) == appt_id


def test_get_appointment_returns_none_when_missing(mock_supabase):
    mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = None

    result = get_appointment(mock_supabase, str(uuid4()))

    assert result is None


def test_update_appointment_status(mock_supabase):
    appt_id = str(uuid4())
    updated = _make_appt_dict(id=appt_id, status="confirmed")
    mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [updated]

    result = update_appointment(mock_supabase, appt_id, AppointmentUpdate(status=AppointmentStatus.confirmed))

    assert result is not None
    assert result.status == AppointmentStatus.confirmed


def test_get_upcoming_appointments(mock_supabase):
    now = datetime.now(timezone.utc)
    future = now + timedelta(hours=23)
    row = _make_appt_dict(appointment_time=future.isoformat())
    mock_supabase.table.return_value.select.return_value.gte.return_value.lte.return_value.execute.return_value.data = [row]

    results = get_upcoming_appointments(mock_supabase, hours_ahead=24)

    assert len(results) == 1


def test_is_owner_true(mock_supabase):
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"id": str(uuid4()), "phone": "+919999999999"}]

    assert is_owner(mock_supabase, "+919999999999") is True


def test_is_owner_false(mock_supabase):
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

    assert is_owner(mock_supabase, "+911111111111") is False
