"""
============================================================
FILE NAME
email_parser.py

PURPOSE
Parse .eml files or raw email strings into readable text.

INPUT
File path (.eml) or raw email string

OUTPUT
{"text": ..., "source": ..., "type": "email"}

DEPENDENCIES
email (stdlib), pathlib

LAST UPDATED
2026-08-02
============================================================
"""

import email
from email import policy
from email.parser import BytesParser
from pathlib import Path


class EmailParser:

    def parse(self, source):

        source = str(source)

        if Path(source).is_file():
            return self._parse_file(Path(source))

        return self._parse_string(source)

    def _parse_file(self, path):
        try:
            with open(path, "rb") as handle:
                message = BytesParser(policy=policy.default).parse(handle)

            return self._build_result(path.name, message)
        except Exception:
            return {
                "text": path.read_text(encoding="utf-8", errors="ignore"),
                "source": str(path),
                "type": "email"
            }

    def _parse_string(self, source):
        try:
            message = email.message_from_string(source)
            return self._build_result("inline", message)
        except Exception:
            return {
                "text": source,
                "source": "inline",
                "type": "email"
            }

    def _build_result(self, name, message):
        lines = []

        subject = message.get("Subject")
        sender = message.get("From")
        recipient = message.get("To")

        if sender:
            lines.append(f"From: {sender}")
        if recipient:
            lines.append(f"To: {recipient}")
        if subject:
            lines.append(f"Subject: {subject}")

        if subject or sender or recipient:
            lines.append("")

        body = self._extract_body(message)
        lines.append(body)

        return {
            "text": "\n".join(lines),
            "source": str(name),
            "type": "email"
        }

    def _extract_body(self, message):
        parts = []

        for part in message.walk():
            content_type = part.get_content_type()
            disposition = part.get("Content-Disposition") or ""

            if content_type == "text/plain":
                payload = part.get_content()
                parts.append(payload)
            elif content_type == "text/html":
                try:
                    from bs4 import BeautifulSoup
                    payload = part.get_content()
                    soup = BeautifulSoup(payload, "html.parser")
                    parts.append(soup.get_text("\n", strip=True))
                except Exception:
                    pass

        return "\n".join(p for p in parts if p)
