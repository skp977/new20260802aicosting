"""
============================================================
FILE NAME
lead_manager.py

PURPOSE
Track customer leads as JSON records (simple CRM).

INPUT
TravelRequest / dict

OUTPUT
Saved lead file under data/leads/

USED BY
EmailRequestOrchestrator, ManualRequestOrchestrator (optional)

DEPENDENCIES
json, pathlib, datetime

LAST UPDATED
2026-08-02
============================================================
"""

import json
from datetime import datetime
from pathlib import Path


class LeadManager:

    def __init__(self, root=None):

        if root is None:
            root = Path(__file__).resolve().parent.parent

        self.leads_dir = Path(root) / "data" / "leads"
        self.leads_dir.mkdir(parents=True, exist_ok=True)

    def add(self, request, status="new"):

        if hasattr(request, "__dataclass_fields__"):
            data = {
                field: getattr(request, field)
                for field in request.__dataclass_fields__
            }
        elif isinstance(request, dict):
            data = dict(request)
        else:
            data = {"data": str(request)}

        data["status"] = status
        data["created_at"] = datetime.now().isoformat()

        key = (
            data.get("customer_email")
            or data.get("customer_phone")
            or "lead"
        )

        safe_key = (
            str(key)
            .replace(" ", "_")
            .replace("/", "_")
            .replace("\\", "_")
            .replace(":", "_")
            or "lead"
        )

        filename = (
            f"lead_{safe_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        filepath = self.leads_dir / filename

        filepath.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        return str(filepath)

    def list(self):
        leads = []

        for path in sorted(
            self.leads_dir.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        ):
            leads.append({
                "file": path.name,
                "saved": datetime.fromtimestamp(
                    path.stat().st_mtime
                ).strftime("%Y-%m-%d %H:%M")
            })

        return leads
