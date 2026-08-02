"""
FILE NAME:
master_costing_engine.py

PURPOSE:
Calculate complete travel costing from itinerary.
"""


class MasterCostingEngine:

    HOTEL_RATES = {
        "3 Star": 50,
        "4 Star": 90,
        "5 Star": 180
    }

    VEHICLE_PER_DAY = 120
    GUIDE_PER_DAY = 35
    DEFAULT_ACTIVITY_COST = 20

    PROFIT_PERCENT = 20
    VAT_PERCENT = 13

    def calculate(self, request, itinerary):

        pax = request.pax or 1

        total_hotel = 0
        total_vehicle = 0
        total_guide = 0
        total_activity = 0

        for day in itinerary:

            hotel_category = day.get(
                "hotel_category",
                "4 Star"
            )

            hotel_rate = self.HOTEL_RATES.get(
                hotel_category,
                90
            )

            total_hotel += hotel_rate * pax

            total_vehicle += self.VEHICLE_PER_DAY

            total_guide += self.GUIDE_PER_DAY

            activity_count = len(
                day.get("activities", [])
            )

            total_activity += (
                activity_count *
                self.DEFAULT_ACTIVITY_COST *
                pax
            )

        subtotal = (
            total_hotel +
            total_vehicle +
            total_guide +
            total_activity
        )

        profit = (
            subtotal *
            self.PROFIT_PERCENT / 100
        )

        vat = (
            (subtotal + profit) *
            self.VAT_PERCENT / 100
        )

        grand_total = (
            subtotal +
            profit +
            vat
        )

        return {
            "pax": pax,
            "hotel_cost": round(total_hotel, 2),
            "vehicle_cost": round(total_vehicle, 2),
            "guide_cost": round(total_guide, 2),
            "activity_cost": round(total_activity, 2),
            "subtotal": round(subtotal, 2),
            "profit": round(profit, 2),
            "vat": round(vat, 2),
            "grand_total": round(grand_total, 2),
            "currency": request.currency
        }


if __name__ == "__main__":

    import sys
    from pathlib import Path

    ROOT = Path(__file__).resolve().parent.parent

    sys.path.insert(0, str(ROOT))

    from models.travel_request import TravelRequest
    from itinerary.itinerary_engine import ItineraryEngine

    request = TravelRequest()

    request.pax = 6
    request.currency = "USD"

    request.destinations = [
        "Kathmandu",
        "Pokhara",
        "Chitwan"
    ]

    itinerary = ItineraryEngine().generate(
        request
    )

    result = MasterCostingEngine().calculate(
        request,
        itinerary
    )

    print(result)