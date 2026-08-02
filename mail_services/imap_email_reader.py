"""
============================================================
FILE NAME
imap_email_reader.py

PURPOSE
Read and search emails from an IMAP mailbox.

INPUT
- fetch_unseen(): list unseen messages
- fetch_by_sender(email): messages from a sender

OUTPUT
List of message dicts:
  {"uid", "from", "to", "subject", "date", "body", "html", "raw"}

USED BY
InboxWatcher, EmailRequestOrchestrator

DEPENDENCIES
imaplib, email (stdlib), config

LAST UPDATED
2026-08-02
============================================================
"""

import imaplib
import email
from email import policy
from email.parser import BytesParser

from config import get


class IMAPEmailReader:

    def __init__(self):
        self.host = get("EMAIL_HOST", "imap.gmail.com")
        self.port = get("IMAP_PORT", 993)
        self.user = get("EMAIL_USER", "")
        self.password = get("EMAIL_PASSWORD", "")
        self.inbox = get("IMAP_INBOX", "INBOX")

    def _connect(self):
        if not self.user or not self.password:
            raise RuntimeError("IMAP credentials not configured.")

        connection = imaplib.IMAP4_SSL(self.host, self.port)
        connection.login(self.user, self.password)

        return connection

    def search(self, criteria=None, mark_seen=True):
        criteria = criteria or "UNSEEN"

        connection = self._connect()

        try:
            connection.select(self.inbox)

            _, data = connection.search(None, criteria)

            uids = data[0].split() if data and data[0] else []

            messages = []

            for uid in uids:
                _, raw = connection.fetch(uid, "(RFC822)")

                if not raw or raw[0] is None:
                    continue

                message = BytesParser(
                    policy=policy.default
                ).parsebytes(raw[0][1])

                if mark_seen:
                    connection.store(uid, "+FLAGS", "\\Seen")

                messages.append(
                    self._to_dict(uid.decode(), message)
                )

            return messages
        finally:
            connection.logout()

    def move_to_folder(self, uid, folder):
        connection = self._connect()

        try:
            if folder not in self._list_folders(connection):
                try:
                    connection.create(folder)
                except Exception:
                    pass

            connection.select(self.inbox)
            connection.copy(uid, folder)
            connection.store(uid, "+FLAGS", "\\Deleted")
            connection.expunge()
            return True
        except Exception:
            return False
        finally:
            connection.logout()

    def _list_folders(self, connection):
        try:
            _, data = connection.list()
            names = []

            for item in data or []:
                if isinstance(item, bytes):
                    parts = item.decode().split('"')
                    if parts:
                        names.append(parts[-1].strip())

            return names
        except Exception:
            return []

    def _to_dict(self, uid, message):
        body_parts = []
        html_parts = []

        for part in message.walk():
            if part.get_content_type() == "text/plain":
                try:
                    body_parts.append(part.get_content())
                except Exception:
                    body_parts.append("")
            elif part.get_content_type() == "text/html":
                try:
                    html_parts.append(part.get_content())
                except Exception:
                    html_parts.append("")

        return {
            "uid": uid,
            "from": message.get("From", ""),
            "to": message.get("To", ""),
            "subject": message.get("Subject", ""),
            "date": message.get("Date", ""),
            "body": "\n".join(p for p in body_parts if p),
            "html": "\n".join(h for h in html_parts if h),
            "raw": message.as_string()
        }
