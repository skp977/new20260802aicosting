"""
============================================================
FILE NAME
scheduler.py

PURPOSE
Background automation loop. Periodically polls the inbox and
processes new inquiries, records activity, and sleeps until
the next cycle.

INPUT
Config via .env (AUTOMATION_ENABLED, AUTOMATION_POLL_SECONDS)

OUTPUT
Activity log written to data/logs/automation.log

USED BY
main.py (background thread)

DEPENDENCIES
inbox_watcher, config

LAST UPDATED
2026-08-02
============================================================
"""

import logging
import threading
import time
from datetime import datetime
from pathlib import Path

from config import get
from mail_services.inbox_watcher import InboxWatcher

logger = logging.getLogger("automation")


class AutomationScheduler:

    def __init__(self, interval=None):
        self.interval = interval or get("AUTOMATION_POLL_SECONDS", 60)
        self.watcher = InboxWatcher()
        self.enabled = get("AUTOMATION_ENABLED", True)
        self.running = False
        self.thread = None

        log_dir = Path(__file__).resolve().parent.parent / "data" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        handler = logging.FileHandler(
            log_dir / "automation.log",
            encoding="utf-8"
        )
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    def start(self):
        if self.running or not self.enabled:
            return

        self.running = True
        self.thread = threading.Thread(
            target=self._run,
            name="automation-scheduler",
            daemon=True
        )
        self.thread.start()

        logger.info("Scheduler started (poll every %ss)", self.interval)

    def stop(self):
        self.running = False

    def _run(self):
        while self.running:
            try:
                self._cycle()
            except Exception as exc:
                logger.error("Cycle failed: %s", exc)

            for _ in range(self.interval):
                if not self.running:
                    break
                time.sleep(1)

    def _cycle(self):
        logger.info("Polling inbox...")

        results, error = self.watcher.poll()

        if error:
            logger.warning("Inbox poll error: %s", error)
            return

        logger.info("Found %s new message(s)", len(results))

        for result in results:
            if result["ok"]:
                details = result.get("details", {})
                notifications = details.get("notifications", {})
                logger.info(
                    "Processed %s from %s | reply=%s alert=%s whatsapp=%s",
                    result.get("subject", ""),
                    result.get("from", ""),
                    notifications.get("customer_reply", {}).get("ok"),
                    notifications.get("internal_alert", {}).get("ok"),
                    notifications.get("whatsapp_alert", {}).get("ok")
                )
            else:
                logger.error(
                    "Failed to process %s: %s",
                    result.get("uid"),
                    result.get("error")
                )


scheduler = AutomationScheduler()
