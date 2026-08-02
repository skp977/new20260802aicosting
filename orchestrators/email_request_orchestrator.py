"""
============================================================
FILE NAME
email_request_orchestrator.py

PURPOSE
Email -> extract -> itinerary -> costing -> save -> notify.
Turns an inbound customer email into a quotation workflow.

INPUT
Email message dict:
  {"from", "to", "subject", "body", "uid"}

OUTPUT
Dict with request / itinerary / costing / notification status

USED BY
InboxWatcher, Scheduler

DEPENDENCIES
extractor, itinerary engine, costing engine, storage,
email_auto_responder, internal_alert, whatsapp_alert_engine

LAST UPDATED
2026-08-02
============================================================
"""

import re

from parsers.travel_request_extractor import TravelRequestExtractor
from itinerary.ai_itinerary_generator import SmartItineraryGenerator
from costing.master_costing_engine import MasterCostingEngine
from storage.save_manager import SaveManager
from crm.lead_manager import LeadManager
from mail_services.email_auto_responder import EmailAutoResponder
from mail_services.internal_alert import InternalAlert
from whatsapp.whatsapp_alert_engine import WhatsAppAlertEngine


class EmailRequestOrchestrator:

    def __init__(self):
        self.extractor = TravelRequestExtractor()
        self.itinerary_engine = SmartItineraryGenerator()
        self.costing_engine = MasterCostingEngine()
        self.storage = SaveManager()
        self.leads = LeadManager()
        self.responder = EmailAutoResponder()
        self.alert = InternalAlert()
        self.whatsapp = WhatsAppAlertEngine()

    def process(self, message):
        text = self._build_text(message)

        request = self.extractor.extract(text)

        request.source_type = "email"
        request.source_file = message.get("uid", "")

        if not request.customer_email:
            request.customer_email = self._extract_email(message.get("from", ""))

        itinerary = self.itinerary_engine.generate(request)

        costing = self.costing_engine.calculate(request, itinerary)

        self.storage.save_request(request)
        self.storage.save_itinerary(request.customer_email or "email", itinerary)
        self.storage.save_costing(request.customer_email or "email", costing)

        lead_path = self.leads.add(request, status="quoted")

        reply_ok, reply_msg = self.responder.send_quote(
            customer_email=request.customer_email,
            request=request,
            itinerary=itinerary,
            costing=costing
        )

        alert_ok, alert_msg = self.alert.send(
            subject=f"New inquiry processed - {request.customer_name or request.customer_email}",
            body=self._alert_text(request, costing)
        )

        whatsapp_ok, whatsapp_msg = self.whatsapp.send(
            self._whatsapp_text(request, costing)
        )

        price_estimate = getattr(
            self.itinerary_engine, "last_price_estimate", None
        )

        return {
            "request": request,
            "itinerary": itinerary,
            "costing": costing,
            "price_estimate": price_estimate,
            "lead_file": lead_path,
            "notifications": {
                "customer_reply": {"ok": reply_ok, "message": reply_msg},
                "internal_alert": {"ok": alert_ok, "message": alert_msg},
                "whatsapp_alert": {"ok": whatsapp_ok, "message": whatsapp_msg}
            }
        }

    def _build_text(self, message):
        lines = [
            message.get("subject", ""),
            "",
            message.get("body", "")
        ]

        return "\n".join(lines).strip()

    def _extract_email(self, sender):
        match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", sender)

        if match:
            return match.group()

        return sender

    def _alert_text(self, request, costing):
        return (
            f"Customer: {request.customer_name or '-'}\n"
            f"Email: {request.customer_email or '-'}\n"
            f"Phone: {request.customer_phone or '-'}\n"
            f"Pax: {request.pax}\n"
            f"Destinations: {', '.join(request.destinations)}\n"
            f"Grand Total: {costing['grand_total']} {costing['currency']}\n"
        )

    def _whatsapp_text(self, request, costing):
        return (
            f"New inquiry from {request.customer_name or request.customer_email}\n"
            f"{request.pax} pax - {', '.join(request.destinations)}\n"
            f"Grand Total: {costing['grand_total']} {costing['currency']}"
        )
