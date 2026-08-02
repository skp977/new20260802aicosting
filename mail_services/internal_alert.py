"""
============================================================
FILE NAME
internal_alert.py

PURPOSE
Send an email alert to the internal admin address.

INPUT
subject, body

OUTPUT
True on success, False on failure

USED BY
Scheduler, EmailRequestOrchestrator

DEPENDENCIES
email_sender, config

LAST UPDATED
2026-08-02
============================================================
"""

from config import get
from mail_services.email_sender import EmailSender


class InternalAlert:

    def __init__(self):
        self.sender = EmailSender()
        self.admin_email = get("ADMIN_EMAIL", "")

    def send(self, subject, body):
        if not self.admin_email:
            return False, "ADMIN_EMAIL not configured."

        ok, message = self.sender.send(
            to=self.admin_email,
            subject=f"[PM Automation] {subject}",
            body=body
        )

        return ok, message
