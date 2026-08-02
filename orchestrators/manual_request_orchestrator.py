"""
FILE NAME: manual_request_orchestrator.py

PURPOSE:
Manual inquiry -> request -> itinerary -> costing -> save

INPUT:
Raw text

OUTPUT:
TravelRequest
Itinerary
Costing

USED BY:
main.py

LAST UPDATED:
2026-06-04
"""

from parsers.travel_request_extractor import TravelRequestExtractor
from itinerary.ai_itinerary_generator import SmartItineraryGenerator
from costing.master_costing_engine import MasterCostingEngine
from storage.save_manager import SaveManager


class ManualRequestOrchestrator:

    def __init__(self):

        self.extractor = TravelRequestExtractor()
        self.itinerary_engine = SmartItineraryGenerator()
        self.costing_engine = MasterCostingEngine()
        self.storage = SaveManager()

    def process(self, raw_text):

        request = self.extractor.extract(raw_text)

        itinerary = self.itinerary_engine.generate(request)

        price_estimate = getattr(
            self.itinerary_engine, "last_price_estimate", None
        )

        costing = self.costing_engine.calculate(request, itinerary)

        self.storage.save_request(request)

        self.storage.save_itinerary(
            request.customer_email or "manual",
            itinerary
        )

        self.storage.save_costing(
            request.customer_email or "manual",
            costing
        )

        return {
            "request": request,
            "itinerary": itinerary,
            "costing": costing,
            "price_estimate": price_estimate
        }

