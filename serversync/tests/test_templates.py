from datetime import datetime, timezone
from templates.messages_en import (
    appointment_confirmation,
    appointment_reminder,
    cancellation_confirmation,
    reschedule_confirmation,
    owner_new_booking_notification,
)


def _appt_time():
    return datetime(2026, 6, 1, 10, 30, tzinfo=timezone.utc)


def test_confirmation_contains_patient_name():
    msg = appointment_confirmation("Ravi Kumar", _appt_time(), "Dr. Sharma", "Smile Clinic")
    assert "Ravi Kumar" in msg
    assert "Dr. Sharma" in msg


def test_reminder_contains_time():
    msg = appointment_reminder("Ravi Kumar", _appt_time(), "Dr. Sharma", "Smile Clinic")
    assert "10:30" in msg


def test_cancellation_confirmation():
    msg = cancellation_confirmation("Ravi Kumar", _appt_time())
    assert "cancelled" in msg.lower()


def test_reschedule_confirmation():
    new_time = datetime(2026, 6, 2, 14, 0, tzinfo=timezone.utc)
    msg = reschedule_confirmation("Ravi Kumar", new_time, "Dr. Sharma")
    assert "14:00" in msg


def test_owner_notification():
    msg = owner_new_booking_notification("Ravi Kumar", _appt_time(), "Dr. Sharma")
    assert "Ravi Kumar" in msg
    assert "Dr. Sharma" in msg
