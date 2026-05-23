import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from database import get_supabase
from services.whatsapp_service import send_text_message
from templates import messages_en as msg

logger = logging.getLogger(__name__)

router = APIRouter()


class NewAppointmentRequest(BaseModel):
    patient_name: str
    patient_phone: str
    appointment_time: datetime
    doctor_name: str
    clinic_name: str
    owner_phone: str
    notes: Optional[str] = None


@router.post("/appointments", status_code=201)
def create_appointment(payload: NewAppointmentRequest):
    """Create appointment in Supabase and notify patient + owner."""
    client = get_supabase()
    row = {
        "patient_name": payload.patient_name,
        "patient_phone": payload.patient_phone,
        "appointment_time": payload.appointment_time.isoformat(),
        "doctor_name": payload.doctor_name,
        "clinic_name": payload.clinic_name,
        "status": "scheduled",
        "notes": payload.notes,
    }
    resp = client.table("appointments").insert(row).execute()
    created = resp.data[0] if resp.data else row

    # Notify patient
    patient_msg = msg.appointment_confirmation(
        payload.patient_name, payload.appointment_time, payload.doctor_name, payload.clinic_name
    )
    send_text_message(payload.patient_phone, patient_msg)

    # Notify owner
    owner_msg = msg.owner_new_booking_notification(
        payload.patient_name, payload.appointment_time, payload.doctor_name
    )
    send_text_message(payload.owner_phone, owner_msg)

    return {"status": "created", "appointment_id": created.get("id")}
