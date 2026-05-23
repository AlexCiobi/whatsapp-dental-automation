from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from supabase import Client

from models import Appointment, AppointmentUpdate

logger = logging.getLogger(__name__)


def get_appointment(client: Client, appointment_id: str) -> Appointment | None:
    """Fetch a single appointment by UUID string."""
    try:
        resp = (
            client.table("appointments")
            .select("*")
            .eq("id", appointment_id)
            .single()
            .execute()
        )
        return Appointment(**resp.data) if resp.data else None
    except Exception:
        logger.exception("get_appointment failed for id=%s", appointment_id)
        return None


def update_appointment(
    client: Client, appointment_id: str, update: AppointmentUpdate
) -> Appointment | None:
    """Update appointment fields. Returns updated row."""
    payload = update.model_dump(exclude_none=True)
    if "appointment_time" in payload and isinstance(payload["appointment_time"], datetime):
        payload["appointment_time"] = payload["appointment_time"].isoformat()
    try:
        resp = (
            client.table("appointments")
            .update(payload)
            .eq("id", appointment_id)
            .execute()
        )
        rows = resp.data
        return Appointment(**rows[0]) if rows else None
    except Exception:
        logger.exception("update_appointment failed for id=%s", appointment_id)
        return None


def get_appointments_by_phone(client: Client, patient_phone: str) -> list[Appointment]:
    """Return all upcoming scheduled appointments for a patient phone number."""
    try:
        now = datetime.now(timezone.utc).isoformat()
        resp = (
            client.table("appointments")
            .select("*")
            .eq("patient_phone", patient_phone)
            .gte("appointment_time", now)
            .in_("status", ["scheduled", "confirmed"])
            .execute()
        )
        return [Appointment(**row) for row in (resp.data or [])]
    except Exception:
        logger.exception("get_appointments_by_phone failed for phone=%s", patient_phone)
        return []


def get_upcoming_appointments(client: Client, hours_ahead: int) -> list[Appointment]:
    """Return appointments within the next `hours_ahead` hours."""
    now = datetime.now(timezone.utc)
    future = now + timedelta(hours=hours_ahead)
    try:
        resp = (
            client.table("appointments")
            .select("*")
            .gte("appointment_time", now.isoformat())
            .lte("appointment_time", future.isoformat())
            .execute()
        )
        return [Appointment(**row) for row in (resp.data or [])]
    except Exception:
        logger.exception("get_upcoming_appointments failed")
        return []


def is_owner(client: Client, phone: str) -> bool:
    """Return True if phone belongs to a clinic owner."""
    try:
        resp = client.table("owners").select("id").eq("phone", phone).execute()
        return bool(resp.data)
    except Exception:
        logger.exception("is_owner check failed for phone=%s", phone)
        return False
