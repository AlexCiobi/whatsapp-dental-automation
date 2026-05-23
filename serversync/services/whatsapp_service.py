import logging

import httpx

from config import settings

logger = logging.getLogger(__name__)

GRAPH_API_URL = "https://graph.facebook.com/v19.0"


def send_text_message(to: str, body: str) -> bool:
    """Send a plain text WhatsApp message. Returns True on success."""
    url = f"{GRAPH_API_URL}/{settings.whatsapp_phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {settings.whatsapp_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body},
    }
    try:
        resp = httpx.post(url, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        return True
    except httpx.HTTPStatusError as exc:
        logger.error("WhatsApp send failed: %s — %s", exc.response.status_code, exc.response.text)
        return False
    except Exception:
        logger.exception("WhatsApp send_text_message unexpected error to=%s", to)
        return False
