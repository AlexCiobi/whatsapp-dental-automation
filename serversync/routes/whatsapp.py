import logging
import os
from datetime import datetime, timezone

from fastapi import APIRouter, Query, Response, Request, BackgroundTasks
from fastapi.responses import PlainTextResponse

from config import settings
from database import get_supabase
from models import AppointmentUpdate, AppointmentStatus, IntentType
from services.appointment_service import (
    get_appointments_by_phone,
    update_appointment,
    is_owner,
)
from services.whatsapp_service import send_text_message
from services.ai_service import parse_intent, generate_chat_response
from templates import messages_en as msg

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/webhook/whatsapp")
def verify_webhook(
    hub_mode: str = Query(alias="hub.mode", default=""),
    hub_verify_token: str = Query(alias="hub.verify_token", default=""),
    hub_challenge: str = Query(alias="hub.challenge", default=""),
):
    expected = os.environ.get("WHATSAPP_VERIFY_TOKEN", settings.whatsapp_verify_token)
    if hub_mode == "subscribe" and hub_verify_token == expected:
        return PlainTextResponse(hub_challenge)
    return Response(status_code=403)


@router.post("/webhook/whatsapp")
async def receive_message(request: Request, background_tasks: BackgroundTasks):
    try:
        body = await request.json()
    except Exception:
        return {"status": "ok"}
    entries = body.get("entry", [])
    for entry in entries:
        for change in entry.get("changes", []):
            messages = change.get("value", {}).get("messages", [])
            for message in messages:
                if message.get("type") != "text":
                    continue
                background_tasks.add_task(
                    _handle_text_message,
                    from_number=message["from"],
                    body=message["text"]["body"],
                )
    return {"status": "ok"}


def _normalize_phone(phone: str) -> str:
    """Ensure phone number has leading + (WhatsApp omits it)."""
    if phone and not phone.startswith("+"):
        return "+" + phone
    return phone


def _handle_text_message(from_number: str, body: str) -> None:
    client = get_supabase()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    from_number = _normalize_phone(from_number)

    if is_owner(client, from_number):
        _handle_owner_message(client, from_number, body, today)
    else:
        _handle_patient_message(client, from_number, body, today)


def _handle_patient_message(client, from_number: str, body: str, today: str) -> None:
    intent = parse_intent(body, current_date=today, is_owner=False)
    appointments = get_appointments_by_phone(client, from_number)

    if not appointments:
        reply = generate_chat_response(from_number, body, context="This patient has no upcoming appointments on record.")
        send_text_message(from_number, reply)
        return

    appt = appointments[0]

    if intent.type == IntentType.cancel:
        update_appointment(client, str(appt.id), AppointmentUpdate(status=AppointmentStatus.cancelled))
        reply = msg.cancellation_confirmation(appt.patient_name, appt.appointment_time)
        send_text_message(from_number, reply)

    elif intent.type == IntentType.reschedule and intent.new_time:
        update_appointment(
            client,
            str(appt.id),
            AppointmentUpdate(status=AppointmentStatus.rescheduled, appointment_time=intent.new_time),
        )
        reply = msg.reschedule_confirmation(appt.patient_name, intent.new_time, appt.doctor_name)
        send_text_message(from_number, reply)

    else:
        context = (
            f"Patient name: {appt.patient_name}. "
            f"They have an appointment with {appt.doctor_name} on "
            f"{appt.appointment_time.strftime('%B %d at %H:%M')}. "
            "If this is the first message, greet them by name and mention the appointment. "
            "Ask if they want to confirm, cancel, or reschedule."
        )
        reply = generate_chat_response(from_number, body, context=context)
        send_text_message(from_number, reply)


def _handle_owner_message(client, from_number: str, body: str, today: str) -> None:
    intent = parse_intent(body, current_date=today, is_owner=True)

    if intent.patient_phone and intent.type == IntentType.reschedule and intent.new_time:
        appointments = get_appointments_by_phone(client, intent.patient_phone)
        if not appointments:
            send_text_message(from_number, f"No upcoming appointment found for {intent.patient_phone}.")
            return
        appt = appointments[0]
        update_appointment(
            client,
            str(appt.id),
            AppointmentUpdate(status=AppointmentStatus.rescheduled, appointment_time=intent.new_time),
        )
        patient_reply = msg.reschedule_confirmation(appt.patient_name, intent.new_time, appt.doctor_name)
        send_text_message(intent.patient_phone, patient_reply)
        send_text_message(from_number, f"Done. {appt.patient_name} rescheduled and notified.")

    elif intent.patient_phone and intent.type == IntentType.cancel:
        appointments = get_appointments_by_phone(client, intent.patient_phone)
        if not appointments:
            send_text_message(from_number, f"No upcoming appointment found for {intent.patient_phone}.")
            return
        appt = appointments[0]
        update_appointment(client, str(appt.id), AppointmentUpdate(status=AppointmentStatus.cancelled))
        send_text_message(intent.patient_phone, msg.cancellation_confirmation(appt.patient_name, appt.appointment_time))
        send_text_message(from_number, f"Done. {appt.patient_name}'s appointment cancelled.")

    else:
        reply = generate_chat_response(from_number, body, context="You are responding to the clinic owner or staff member.")
        send_text_message(from_number, reply)
