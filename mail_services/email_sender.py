"""
============================================================
FILE NAME
email_sender.py

PURPOSE
Send emails via SMTP.

INPUT
recipient, subject, body (plain text / HTML optional)

OUTPUT
True on success, False on failure

USED BY
EmailAutoResponder, InternalAlert

DEPENDENCIES
smtplib, email, config

LAST UPDATED
2026-08-02
============================================================
"""

import smtplib
import ssl
from email.message import EmailMessage

from config import get


class EmailSender:

    def __init__(self):
        self.host = get("SMTP_HOST", "smtp.gmail.com")
        self.port = get("SMTP_PORT", 587)
        self.user = get("SMTP_USER", "")
        self.password = get("SMTP_PASSWORD", "")

    def send(self, to, subject, body, html=None):
        if not self.user or not self.password:
            return False, "SMTP credentials not configured."

        if not to:
            return False, "No recipient provided."

        try:
            message = EmailMessage()

            message["From"] = self.user
            message["To"] = to
            message["Subject"] = subject

            message.set_content(body)

            if html:
                message.add_alternative(html, subtype="html")

            context = ssl.create_default_context()

            with smtplib.SMTP(self.host, self.port, timeout=30) as server:
                server.starttls(context=context)
                server.login(self.user, self.password)
                server.send_message(message)

            return True, "sent"
        except Exception as exc:
            return False, str(exc)
