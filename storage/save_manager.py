"""
============================================================
FILE NAME
save_manager.py

PURPOSE
Persist travel records (requests / itineraries / costings)
as JSON under data/ for the dashboard and exporters.

INPUT
TravelRequest / dict / list

OUTPUT
Saved JSON file under data/requests, data/itineraries,
data/costings

USED BY
EmailRequestOrchestrator, ManualRequestOrchestrator

DEPENDENCIES
json, pathlib, datetime, dataclasses

LAST UPDATED
2026-08-02
============================================================
"""

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path


class SaveManager:

    def __init__(self, root=None):

        if root is None:
            root = Path(__file__).resolve().parent.parent

        self.requests_dir = Path(root) / "data" / "requests"
        self.itineraries_dir = Path(root) / "data" / "itineraries"
        self.costings_dir = Path(root) / "data" / "costings"

        for directory in (
            self.requests_dir,
            self.itineraries_dir,
            self.costings_dir
        ):
            directory.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _serialize(obj):

        if is_dataclass(obj):
            return asdict(obj)

        if isinstance(obj, dict):
            return {
                key: SaveManager._serialize(value)
                for key, value in obj.items()
            }

        if isinstance(obj, (list, tuple)):
            return [SaveManager._serialize(item) for item in obj]

        return obj

    @staticmethod
    def _safe_key(value):

        safe = (
            str(value or "record")
            .replace(" ", "_")
            .replace("/", "_")
            .replace("\\", "_")
            .replace(":", "_")
            .replace("@", "_")
        )

        return safe or "record"

    @staticmethod
    def _timestamp():
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def _stamp(self, data):

        payload = self._serialize(data)

        if isinstance(payload, dict):
            payload = dict(payload)
            payload.setdefault("saved_at", datetime.now().isoformat())

        return payload

    def _write(self, directory, filename, data):

        path = directory / filename

        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        return str(path)

    def save_request(self, request):

        data = self._stamp(request)

        key = self._safe_key(
            data.get("customer_email")
            or data.get("customer_phone")
        )

        filename = f"request_{key}_{self._timestamp()}.json"

        return self._write(self.requests_dir, filename, data)

    def save_itinerary(self, customer_email, itinerary):

        data = self._stamp(itinerary)
        key = self._safe_key(customer_email)

        filename = f"itinerary_{key}_{self._timestamp()}.json"

        return self._write(self.itineraries_dir, filename, data)

    def save_costing(self, customer_email, costing):

        data = self._stamp(costing)
        key = self._safe_key(customer_email)

        filename = f"costing_{key}_{self._timestamp()}.json"

        return self._write(self.costings_dir, filename, data)
