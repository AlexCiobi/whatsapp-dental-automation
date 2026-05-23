from datetime import datetime


def _fmt(dt: datetime) -> str:
    return dt.strftime("%B %d, %Y at %H:%M")


def appointment_confirmation(
    patient_name: str, appt_time: datetime, doctor_name: str, clinic_name: str
) -> str:
    return (
        f"Hello {patient_name}! Your appointment at {clinic_name} with {doctor_name} "
        f"is confirmed for {_fmt(appt_time)}. Reply CANCEL to cancel or RESCHEDULE to change."
    )


def appointment_reminder(
    patient_name: str, appt_time: datetime, doctor_name: str, clinic_name: str
) -> str:
    return (
        f"Reminder: Hi {patient_name}, your appointment at {clinic_name} with {doctor_name} "
        f"is on {_fmt(appt_time)}. Reply CANCEL or RESCHEDULE if needed."
    )


def cancellation_confirmation(patient_name: str, appt_time: datetime) -> str:
    return (
        f"Hi {patient_name}, your appointment on {_fmt(appt_time)} has been cancelled. "
        f"Please contact us to rebook."
    )


def reschedule_confirmation(
    patient_name: str, new_time: datetime, doctor_name: str
) -> str:
    return (
        f"Hi {patient_name}, your appointment has been rescheduled to {_fmt(new_time)} "
        f"with {doctor_name}. See you then!"
    )


def owner_new_booking_notification(
    patient_name: str, appt_time: datetime, doctor_name: str
) -> str:
    return (
        f"New booking: {patient_name} with {doctor_name} at {_fmt(appt_time)}."
    )
