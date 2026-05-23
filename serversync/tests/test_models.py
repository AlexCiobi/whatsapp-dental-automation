from datetime import datetime, timezone
from uuid import uuid4
from models import Appointment, AppointmentStatus, ParsedIntent, IntentType


def test_appointment_model():
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
    assert appt.status == AppointmentStatus.scheduled


def test_parsed_intent_reschedule():
    intent = ParsedIntent(
        type=IntentType.reschedule,
        new_time=datetime(2026, 6, 2, 14, 0, tzinfo=timezone.utc),
        patient_phone=None,
    )
    assert intent.type == IntentType.reschedule
    assert intent.new_time is not None


def test_parsed_intent_cancel():
    intent = ParsedIntent(type=IntentType.cancel, new_time=None, patient_phone=None)
    assert intent.type == IntentType.cancel
