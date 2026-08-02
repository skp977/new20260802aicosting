"""
============================================================
FILE NAME
whatsapp_sender.py

PURPOSE
Send WhatsApp messages through the local Waha HTTP API
(free, open source, self-hosted via docker).

INPUT
phone (with country code), text

OUTPUT
True on success, False on failure

USED BY
WhatsAppAlertEngine

DEPENDENCIES
requests, config

LAST UPDATED
2026-08-02
============================================================
"""

import requests

from config import get


class WhatsAppSender:

    def __init__(self):
        self.api_url = get("WAHA_API_URL", "http://127.0.0.1:3000").rstrip("/")
        self.session = get("WAHA_SESSION", "default")
        self.api_key = get("WAHA_API_KEY", "")

    def send(self, phone, text):
        if not phone or not text:
            return False, "Phone or text missing."

        url = (
            f"{self.api_url}/api/sendText"
        )

        payload = {
            "session": self.session,
            "chatId": self._chat_id(phone),
            "text": text
        }

        headers = {}
        if self.api_key:
            headers["X-Api-Key"] = self.api_key

        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=15
            )

            if response.status_code in (200, 201):
                return True, "sent"
            return False, response.text[:200]
        except requests.RequestException as exc:
            return False, f"Waha unreachable: {exc}"

    def _chat_id(self, phone):
        digits = "".join(ch for ch in str(phone) if ch.isdigit())
        return f"{digits}@c.us"
