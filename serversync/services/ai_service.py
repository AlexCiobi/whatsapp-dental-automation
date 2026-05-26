import json
import logging
from collections import defaultdict, deque
from typing import List, Dict

import anthropic

from config import settings
from models import IntentType, ParsedIntent

logger = logging.getLogger(__name__)

anthropic_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

# In-memory conversation history: phone -> deque of {role, content}
_conversation_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10))

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

_CHAT_SYSTEM_PROMPT = """You are a smart, friendly dental clinic assistant communicating via WhatsApp.
You work for Demo Dental Clinic. Your name is Sofia.

Personality:
- Natural and conversational — like texting with a helpful human, not a robot
- Warm but professional
- Concise — WhatsApp messages should be short, 1-3 sentences max
- Never repeat the same greeting twice in a conversation
- Actually respond to what the patient said — don't give generic replies
- If they want to book, ask for their preferred date/time and what treatment they need
- If they confirm/cancel/reschedule, acknowledge it clearly
- Never say "How can I help you today?" if you already know what they want

You can help with: booking, confirming, cancelling, rescheduling appointments, general clinic questions.
If asked about specific clinic details you don't know (exact address, prices), say you'll check and ask them to call.
"""


_CHAT_SYSTEM_PROMPT = """You are Sofia, a friendly and professional assistant for a dental clinic called Demo Dental Clinic.
You communicate via WhatsApp. Be warm, concise, and helpful. Use natural language — not robotic.
Keep replies short (2-4 sentences max). Use emojis sparingly but naturally.

You can help patients with:
- Booking, confirming, cancelling, or rescheduling appointments
- General questions about the clinic (hours, services, location)
- Anything else clinic-related

If someone wants to book an appointment, ask for their preferred date and time.
If you don't know something specific (like exact clinic hours), say you'll check and ask them to call the clinic.
Never make up clinic details you don't know. Always end with an offer to help further."""


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


def generate_chat_response(phone: str, message: str, context: str = "") -> str:
    """Generate a conversational reply as Sofia, with full conversation history."""
    history = _conversation_history[phone]

    # Build system with context injection if provided
    system = _CHAT_SYSTEM_PROMPT
    if context:
        system += f"\n\nContext about this patient: {context}"

    # Add the new user message to history
    history.append({"role": "user", "content": message})

    try:
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            system=system,
            messages=list(history),
        )
        reply = response.content[0].text.strip()
        # Save assistant reply to history
        history.append({"role": "assistant", "content": reply})
        return reply
    except Exception:
        logger.exception("generate_chat_response failed")
        return "Hey! Thanks for reaching out. How can I help you?"
