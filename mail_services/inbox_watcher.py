"""
============================================================
FILE NAME
inbox_watcher.py

PURPOSE
Watch the inbox for new emails and process each one through
the email orchestrator. Skips senders already handled and
optionally moves processed messages to a subfolder.

INPUT
None (polls IMAP)

OUTPUT
List of processed results

USED BY
Scheduler

DEPENDENCIES
imap_email_reader, email_request_orchestrator, config

LAST UPDATED
2026-08-02
============================================================
"""

import re
from pathlib import Path

from config import get
from mail_services.imap_email_reader import IMAPEmailReader
from orchestrators.email_request_orchestrator import EmailRequestOrchestrator


class InboxWatcher:

    def __init__(self, processed_log=None):
        self.reader = IMAPEmailReader()
        self.orchestrator = EmailRequestOrchestrator()

        if processed_log is None:
            processed_log = (
                Path(__file__).resolve().parent.parent /
                "data" / "logs" / "processed_uids.txt"
            )

        self.processed_log = Path(processed_log)
        self.processed_log.parent.mkdir(parents=True, exist_ok=True)

        self.mark_processed = get("AUTOMATION_MARK_PROCESSED", False)

    def poll(self):
        try:
            messages = self.reader.search(
                criteria="UNSEEN",
                mark_seen=True
            )
        except Exception as exc:
            return [], str(exc)

        results = []

        seen = self._load_processed()

        for message in messages:
            uid = message.get("uid")

            if uid in seen:
                continue

            try:
                result = self.orchestrator.process(message)

                self._mark_processed(uid)

                if self.mark_processed:
                    self.reader.move_to_folder(
                        uid,
                        get("IMAP_FOLDER_PROCESSED", "INBOX/Processed")
                    )

                results.append({
                    "uid": uid,
                    "from": message.get("from"),
                    "subject": message.get("subject"),
                    "ok": True,
                    "details": result
                })
            except Exception as exc:
                results.append({
                    "uid": uid,
                    "from": message.get("from"),
                    "subject": message.get("subject"),
                    "ok": False,
                    "error": str(exc)
                })

        return results, None

    def _load_processed(self):
        if not self.processed_log.is_file():
            return set()

        return set(
            line.strip()
            for line in self.processed_log.read_text(
                encoding="utf-8"
            ).splitlines()
            if line.strip()
        )

    def _mark_processed(self, uid):
        with open(self.processed_log, "a", encoding="utf-8") as handle:
            handle.write(f"{uid}\n")
