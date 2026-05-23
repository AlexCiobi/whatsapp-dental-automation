import logging
from datetime import datetime

from fastapi import APIRouter, Request

from database import get_supabase
from models import AppointmentStatus, AppointmentUpdate
from services.appointment_service import update_appointment

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/webhook/vapi")
async def vapi_webhook(request: Request):
    body = await request.json()
    message = body.get("message", {})

    if message.get("type") != "end-of-call-report":
        return {"status": "ignored"}

    call_meta = message.get("call", {}).get("metadata", {})
    appointment_id = call_meta.get("appointment_id")
    outcome = call_meta.get("outcome")

    if not appointment_id or not outcome:
        logger.warning("Vapi webhook missing appointment_id or outcome: %s", call_meta)
        return {"status": "missing_fields"}

    client = get_supabase()

    status_map = {
        "confirmed": AppointmentStatus.confirmed,
        "cancelled": AppointmentStatus.cancelled,
        "rescheduled": AppointmentStatus.rescheduled,
    }

    new_status = status_map.get(outcome)
    if not new_status:
        logger.info("Vapi outcome=%s — no status update needed", outcome)
        return {"status": "ok"}

    update = AppointmentUpdate(status=new_status)

    new_time_str = call_meta.get("new_time")
    if outcome == "rescheduled" and new_time_str:
        try:
            update.appointment_time = datetime.fromisoformat(new_time_str)
        except ValueError:
            logger.warning("Could not parse new_time=%s", new_time_str)

    update_appointment(client, appointment_id, update)
    logger.info("Vapi webhook: appointment %s → %s", appointment_id, new_status)
    return {"status": "ok"}
