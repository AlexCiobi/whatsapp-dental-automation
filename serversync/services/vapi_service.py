import logging
from datetime import datetime
from typing import Optional

import httpx

from config import settings

logger = logging.getLogger(__name__)

VAPI_CALLS_URL = "https://api.vapi.ai/call/phone"

_ASSISTANT_INSTRUCTIONS = """You are Sofia, a warm and professional dental clinic assistant making an outbound reminder call.

Your goal: confirm the patient's upcoming appointment in a natural, human way.

Rules:
- Start by greeting the patient by name and confirming it's them
- Mention the appointment details clearly (doctor name and date/time)
- Ask if they can confirm, need to cancel, or want to reschedule
- If they want to reschedule, ask for their preferred date and time and tell them the clinic will confirm
- If they confirm, thank them warmly and wish them a good day
- Keep it brief and conversational — this is a phone call, not an essay
- Speak English by default. If the patient replies in Hindi, switch fully to Hindi. If they reply in Marathi, switch fully to Marathi.
- Never sound robotic or scripted
- If there is silence or confusion, gently repeat the key info
"""


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
            "transcriber": {
                "provider": "deepgram",
                "model": "nova-2",
                "language": "multi",
            },
            "model": {
                "provider": "anthropic",
                "model": "claude-haiku-4-5-20251001",
                "messages": [
                    {"role": "system", "content": _ASSISTANT_INSTRUCTIONS}
                ],
            },
            "voice": {
                "provider": "playht",
                "voiceId": "jennifer",
            },
            "firstMessage": (
                f"Hello! Am I speaking with {patient_name}? "
                f"This is Sofia calling from Demo Dental Clinic. "
                f"I'm reaching out about your appointment with {doctor_name} on {appt_str}. "
                f"Are you still able to make it?"
            ),
            "endCallMessage": "Perfect, thank you! Have a wonderful day. Goodbye!",
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
