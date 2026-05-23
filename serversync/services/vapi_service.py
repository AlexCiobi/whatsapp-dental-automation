import logging
from datetime import datetime
from typing import Optional

import httpx

from config import settings

logger = logging.getLogger(__name__)

VAPI_CALLS_URL = "https://api.vapi.ai/call/phone"

_ASSISTANT_INSTRUCTIONS = (
    "You are a dental clinic appointment reminder assistant. "
    "Call the patient to confirm their upcoming appointment. "
    "If they want to cancel or reschedule, collect the details and confirm you will update the clinic. "
    "Speak English by default, switch to Hindi or Marathi if the patient prefers. "
    "Be polite, brief, and professional."
)


def trigger_outbound_call(
    patient_phone: str,
    patient_name: str,
    appointment_id: str,
    appointment_time: datetime,
    doctor_name: str,
) -> Optional[str]:
    """Trigger an outbound reminder call via Vapi. Returns call_id or None."""
    appt_str = appointment_time.strftime("%B %d at %H:%M")
    payload = {
        "phoneNumberId": settings.vapi_phone_number_id,
        "customer": {"number": patient_phone, "name": patient_name},
        "assistant": {
            "model": {
                "provider": "anthropic",
                "model": "claude-haiku-4-5-20251001",
                "systemPrompt": _ASSISTANT_INSTRUCTIONS,
            },
            "firstMessage": (
                f"Hello, am I speaking with {patient_name}? "
                f"I'm calling from your dental clinic to remind you about your appointment "
                f"with {doctor_name} on {appt_str}. Can you confirm you'll be there?"
            ),
        },
        "metadata": {
            "appointment_id": appointment_id,
        },
    }
    headers = {
        "Authorization": f"Bearer {settings.vapi_api_key}",
        "Content-Type": "application/json",
    }
    try:
        resp = httpx.post(VAPI_CALLS_URL, json=payload, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.json().get("id")
    except httpx.HTTPStatusError as exc:
        logger.error("Vapi call failed: %s — %s", exc.response.status_code, exc.response.text)
        return None
    except Exception:
        logger.exception("trigger_outbound_call unexpected error")
        return None
