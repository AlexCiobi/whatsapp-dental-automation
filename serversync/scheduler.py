import logging

from apscheduler.schedulers.background import BackgroundScheduler

from database import get_supabase
from services.appointment_service import get_upcoming_appointments
from services.whatsapp_service import send_text_message
from services.vapi_service import trigger_outbound_call
from templates import messages_en as msg

logger = logging.getLogger(__name__)

_scheduler = BackgroundScheduler()


def send_reminders(hours_ahead: int) -> None:
    """Fetch appointments in the next `hours_ahead` hours and WhatsApp each patient."""
    client = get_supabase()
    appointments = get_upcoming_appointments(client, hours_ahead=hours_ahead)
    for appt in appointments:
        text = msg.appointment_reminder(
            appt.patient_name, appt.appointment_time, appt.doctor_name, appt.clinic_name
        )
        ok = send_text_message(appt.patient_phone, text)
        logger.info("Reminder sent to %s: %s", appt.patient_phone, ok)


def trigger_confirmation_calls() -> None:
    """Trigger outbound Vapi calls for appointments ~24h away."""
    client = get_supabase()
    appointments = get_upcoming_appointments(client, hours_ahead=25)
    for appt in appointments:
        call_id = trigger_outbound_call(
            patient_phone=appt.patient_phone,
            patient_name=appt.patient_name,
            appointment_id=str(appt.id),
            appointment_time=appt.appointment_time,
            doctor_name=appt.doctor_name,
        )
        logger.info("Outbound call triggered for appt %s — call_id=%s", appt.id, call_id)


def start_scheduler() -> None:
    """Start APScheduler with reminder and call jobs."""
    if _scheduler.running:
        logger.warning("Scheduler already running, skipping start")
        return
    _scheduler.add_job(send_reminders, "interval", hours=1, kwargs={"hours_ahead": 24}, id="reminder_24h")
    _scheduler.add_job(send_reminders, "interval", hours=1, kwargs={"hours_ahead": 2}, id="reminder_2h")
    _scheduler.add_job(trigger_confirmation_calls, "interval", hours=1, id="outbound_calls")
    _scheduler.start()
    logger.info("Scheduler started")


def shutdown_scheduler() -> None:
    """Stop APScheduler gracefully."""
    if _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
