from datetime import datetime


def _fmt(dt: datetime) -> str:
    return dt.strftime("%d %B %Y, %H:%M")


def appointment_confirmation(
    patient_name: str, appt_time: datetime, doctor_name: str, clinic_name: str
) -> str:
    return (
        f"नमस्कार {patient_name}! {clinic_name} मध्ये {doctor_name} सोबत तुमची वेळ "
        f"{_fmt(appt_time)} साठी निश्चित झाली आहे। रद्द करण्यासाठी CANCEL किंवा बदलण्यासाठी RESCHEDULE लिहा।"
    )


def appointment_reminder(
    patient_name: str, appt_time: datetime, doctor_name: str, clinic_name: str
) -> str:
    return (
        f"आठवण: {patient_name}, {clinic_name} मध्ये {doctor_name} सोबत तुमची वेळ "
        f"{_fmt(appt_time)} ला आहे।"
    )


def cancellation_confirmation(patient_name: str, appt_time: datetime) -> str:
    return f"{patient_name}, {_fmt(appt_time)} ची तुमची वेळ रद्द केली आहे।"


def reschedule_confirmation(
    patient_name: str, new_time: datetime, doctor_name: str
) -> str:
    return (
        f"{patient_name}, तुमची वेळ {_fmt(new_time)} साठी बदलली आहे। {doctor_name} भेटू!"
    )


def owner_new_booking_notification(
    patient_name: str, appt_time: datetime, doctor_name: str
) -> str:
    return f"नवीन बुकिंग: {patient_name}, {doctor_name} सोबत {_fmt(appt_time)} ला।"
