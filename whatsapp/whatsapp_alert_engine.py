"""
============================================================
FILE NAME
whatsapp_alert_engine.py

PURPOSE
Send WhatsApp alerts to the internal number when new
inquiries are processed.

INPUT
subject / text

OUTPUT
True on success, False on failure

USED BY
Scheduler, EmailRequestOrchestrator

DEPENDENCIES
whatsapp_sender, config

LAST UPDATED
2026-08-02
============================================================
"""

from config import get
from whatsapp.whatsapp_sender import WhatsAppSender


class WhatsAppAlertEngine:

    def __init__(self):
        self.sender = WhatsAppSender()
        self.phone = get("WHATSAPP_PHONE", "")

    def send(self, text):
        if not self.phone:
            return False, "WHATSAPP_PHONE not configured."

        ok, message = self.sender.send(
            self.phone,
            f"[PM Automation]\n{text}"
        )

        return ok, message
