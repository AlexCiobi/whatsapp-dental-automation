import pytest
from unittest.mock import patch, MagicMock, call
from datetime import datetime, timezone
from uuid import uuid4
from models import Appointment, AppointmentStatus
from scheduler import send_reminders, trigger_confirmation_calls


def _make_appt(**kwargs):
    base = dict(
        id=uuid4(),
        patient_name="Ravi Kumar",
        patient_phone="+919876543210",
        appointment_time=datetime(2026, 6, 1, 10, 0, tzinfo=timezone.utc),
        doctor_name="Dr. Sharma",
        clinic_name="Smile Clinic",
        status=AppointmentStatus.scheduled,
        created_at=datetime.now(timezone.utc),
    )
    base.update(kwargs)
    return Appointment(**base)


@patch("scheduler.send_text_message", return_value=True)
@patch("scheduler.get_upcoming_appointments")
@patch("scheduler.get_supabase")
def test_send_reminders_sends_to_each_patient(mock_db, mock_get_appts, mock_send):
    appt1 = _make_appt(patient_phone="+919876543210")
    appt2 = _make_appt(patient_phone="+919999999999")
    mock_get_appts.return_value = [appt1, appt2]

    send_reminders(hours_ahead=24)

    assert mock_send.call_count == 2


@patch("scheduler.send_text_message", return_value=True)
@patch("scheduler.get_upcoming_appointments", return_value=[])
@patch("scheduler.get_supabase")
def test_send_reminders_no_appointments(mock_db, mock_get_appts, mock_send):
    send_reminders(hours_ahead=24)
    mock_send.assert_not_called()


@patch("scheduler.trigger_outbound_call", return_value="call_id_123")
@patch("scheduler.get_upcoming_appointments")
@patch("scheduler.get_supabase")
def test_trigger_confirmation_calls(mock_db, mock_get_appts, mock_call):
    appt = _make_appt()
    mock_get_appts.return_value = [appt]

    trigger_confirmation_calls()

    mock_call.assert_called_once_with(
        patient_phone=appt.patient_phone,
        patient_name=appt.patient_name,
        appointment_id=str(appt.id),
        appointment_time=appt.appointment_time,
        doctor_name=appt.doctor_name,
    )
