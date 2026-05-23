import json
import logging

import anthropic

from config import settings
from models import IntentType, ParsedIntent

logger = logging.getLogger(__name__)

anthropic_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

_SYSTEM_PROMPT = """You are an intent parser for a dental clinic WhatsApp assistant.
Extract the patient's or clinic owner's intent from their message and return ONLY a JSON object.

JSON schema:
{
  "intent": "confirm" | "cancel" | "reschedule" | "unknown",
  "new_time": "<ISO 8601 datetime with timezone>" | null,
  "patient_phone": "<phone with country code>" | null
}

Rules:
- "new_time" is required when intent is "reschedule". Use the provided current_date as reference for relative phrases like "tomorrow" or "next Tuesday".
- "patient_phone" is only set when an owner message explicitly mentions a patient phone number.
- Return raw JSON only — no markdown, no explanation.
"""


def parse_intent(
    message: str,
    current_date: str,
    is_owner: bool = False,
) -> ParsedIntent:
    """Parse a WhatsApp message and return a structured intent."""
    role_hint = "This message is from a CLINIC OWNER managing a patient." if is_owner else "This message is from a PATIENT."
    user_prompt = f"current_date: {current_date}\n{role_hint}\nMessage: {message}"
    try:
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=256,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        raw = response.content[0].text.strip()
        data = json.loads(raw)
        return ParsedIntent(
            type=IntentType(data.get("intent", "unknown")),
            new_time=data.get("new_time"),
            patient_phone=data.get("patient_phone"),
        )
    except Exception:
        logger.exception("parse_intent failed for message=%r", message)
        return ParsedIntent(type=IntentType.unknown)
