from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class AppointmentStatus(str, Enum):
    scheduled = "scheduled"
    confirmed = "confirmed"
    rescheduled = "rescheduled"
    cancelled = "cancelled"


class Appointment(BaseModel):
    id: UUID
    patient_name: str
    patient_phone: str
    appointment_time: datetime
    doctor_name: str
    clinic_name: str
    status: AppointmentStatus
    created_at: datetime
    notes: Optional[str] = None


class AppointmentUpdate(BaseModel):
    appointment_time: Optional[datetime] = None
    status: Optional[AppointmentStatus] = None
    notes: Optional[str] = None


class IntentType(str, Enum):
    confirm = "confirm"
    cancel = "cancel"
    reschedule = "reschedule"
    unknown = "unknown"


class ParsedIntent(BaseModel):
    type: IntentType
    new_time: Optional[datetime] = None
    patient_phone: Optional[str] = None


class WhatsAppTextMessage(BaseModel):
    from_number: str
    message_id: str
    body: str
    timestamp: str


class VapiCallEndPayload(BaseModel):
    call_id: str
    appointment_id: str
    outcome: str
    new_time: Optional[datetime] = None
