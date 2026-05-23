from datetime import datetime


def _fmt(dt: datetime) -> str:
    return dt.strftime("%d %B %Y, %H:%M")


def appointment_confirmation(
    patient_name: str, appt_time: datetime, doctor_name: str, clinic_name: str
) -> str:
    return (
        f"नमस्ते {patient_name}! {clinic_name} में {doctor_name} के साथ आपकी अपॉइंटमेंट "
        f"{_fmt(appt_time)} के लिए पक्की हो गई है। रद्द करने के लिए CANCEL या बदलने के लिए RESCHEDULE लिखें।"
    )


def appointment_reminder(
    patient_name: str, appt_time: datetime, doctor_name: str, clinic_name: str
) -> str:
    return (
        f"याद दिलाना: {patient_name} जी, {clinic_name} में {doctor_name} के साथ आपकी अपॉइंटमेंट "
        f"{_fmt(appt_time)} को है।"
    )


def cancellation_confirmation(patient_name: str, appt_time: datetime) -> str:
    return (
        f"{patient_name} जी, {_fmt(appt_time)} की आपकी अपॉइंटमेंट रद्द कर दी गई है।"
    )


def reschedule_confirmation(
    patient_name: str, new_time: datetime, doctor_name: str
) -> str:
    return (
        f"{patient_name} जी, आपकी अपॉइंटमेंट {_fmt(new_time)} के लिए बदल दी गई है। "
        f"{doctor_name} से मिलेंगे!"
    )


def owner_new_booking_notification(
    patient_name: str, appt_time: datetime, doctor_name: str
) -> str:
    return f"नई बुकिंग: {patient_name}, {doctor_name} के साथ {_fmt(appt_time)} को।"
