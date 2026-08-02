"""
============================================================
FILE NAME
email_auto_responder.py

PURPOSE
Automatically reply to a customer with their quotation.

INPUT
customer_email, request, itinerary, costing

OUTPUT
(ok, message)

USED BY
EmailRequestOrchestrator

DEPENDENCIES
email_sender

LAST UPDATED
2026-08-02
============================================================
"""

from mail_services.email_sender import EmailSender


class EmailAutoResponder:

    def __init__(self):
        self.sender = EmailSender()

    def send_quote(self, customer_email, request, itinerary, costing):
        if not customer_email:
            return False, "Customer email missing."

        subject = (
            f"Your Nepal Tour Quotation - "
            f"{costing['grand_total']} {costing['currency']}"
        )

        body = self._build_body(request, itinerary, costing)

        ok, message = self.sender.send(
            to=customer_email,
            subject=subject,
            body=body
        )

        return ok, message

    def _build_body(self, request, itinerary, costing):
        lines = [
            "Dear " + (request.customer_name or "Traveler") + ",",
            "",
            "Thank you for your inquiry. Here is your quotation:",
            "",
            f"Customer    : {request.customer_name or '-'}",
            f"Pax         : {request.pax}",
            f"Destinations: {', '.join(request.destinations)}",
            f"Budget      : {request.budget} {request.currency}",
            "",
            "ITINERARY",
            "========="
        ]

        for day in itinerary:
            lines.append("")
            lines.append(f"Day {day['day']} - {day['title']}")
            lines.append(f"  City: {day['city']} | Hotel: {day['hotel_category']}")
            lines.append(f"  Activities: {', '.join(day['activities'])}")

        lines.extend([
            "",
            "COSTING",
            "=======",
            f"  Subtotal    : {costing['subtotal']} {costing['currency']}",
            f"  Profit (20%): {costing['profit']} {costing['currency']}",
            f"  VAT (13%)   : {costing['vat']} {costing['currency']}",
            f"  GRAND TOTAL : {costing['grand_total']} {costing['currency']}",
            "",
            "We look forward to serving you.",
            "",
            "Best regards,",
            "Nepal International Travel Services (NITS)"
        ])

        return "\n".join(lines)
