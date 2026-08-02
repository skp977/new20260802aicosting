"""
============================================================
FILE NAME
test_itinerary.py

PURPOSE
Generate and print a sample itinerary through the pipeline.

RUN
.venv/Scripts/python.exe tests/test_itinerary.py

LAST UPDATED
2026-08-02
============================================================
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from models.travel_request import TravelRequest
from itinerary.itinerary_engine import ItineraryEngine
from costing.master_costing_engine import MasterCostingEngine
from storage.save_manager import SaveManager
from itinerary.activity_recommender import ActivityRecommender
from itinerary.food_recommender import FoodRecommender
from itinerary.souvenir_recommender import SouvenirRecommender
from itinerary.location_map import route_points


def build_request():

    request = TravelRequest()

    request.inquiry_id = "TEST-ITIN-001"
    request.source_type = "manual"

    request.customer_name = "Test Traveler"
    request.customer_email = "test.traveler@example.com"
    request.customer_phone = "+9779800000000"
    request.customer_country = "USA"

    request.destinations = [
        "Kathmandu",
        "Pokhara",
        "Chitwan",
        "Lumbini"
    ]

    request.cities = ["Kathmandu", "Pokhara"]

    request.pax = 6
    request.adults = 4
    request.children = 2

    request.nights = 7
    request.days = 8

    request.arrival_date = "2026-10-01"
    request.departure_date = "2026-10-08"

    request.budget = 3000
    request.currency = "USD"

    request.hotel_category = "4 Star"
    request.travel_style = "Culture & Safari"

    request.activities = [
        "Safari",
        "Boating"
    ]

    return request


def main():

    request = build_request()

    itinerary = ItineraryEngine().generate(request)

    costing = MasterCostingEngine().calculate(
        request,
        itinerary
    )

    SaveManager().save_itinerary(
        request.customer_email,
        itinerary
    )

    print("=" * 70)
    print("TEST ITINERARY")
    print(f"Customer : {request.customer_name} ({request.customer_email})")
    print(f"Pax      : {request.pax}")
    print(f"Dates    : {request.arrival_date} to {request.departure_date}")
    print(f"Budget   : {request.budget} {request.currency}")
    print("=" * 70)

    for day in itinerary:
        print()
        print(f"DAY {day['day']} - {day['title']}")
        print(f"  City        : {day['city']}")
        print(f"  Overnight   : {day['overnight']}")
        print(f"  Hotel       : {day['hotel_category']}")
        print(f"  Meals       : {', '.join(day['meals'])}")
        print(f"  Transport   : {day['transport']}")
        print(f"  Activities  : {', '.join(day['activities'])}")
        print(f"  Notes       : {day['notes']}")

    print()
    print("=" * 70)
    print("COSTING")
    print("=" * 70)

    for key, value in costing.items():
        print(f"  {key:<14}: {value}")

    print()
    print("=" * 70)
    print("SUGGESTIONS")
    print("=" * 70)

    print("\n  Activities:")
    for item in ActivityRecommender().recommend(request):
        print(f"    - {item}")

    print("\n  Food:")
    for item in FoodRecommender().recommend(request):
        print(f"    - {item}")

    print("\n  Souvenirs:")
    for item in SouvenirRecommender().recommend(request):
        print(f"    - {item}")

    print()
    print("=" * 70)
    print("MAP ROUTE")
    print("=" * 70)

    for point in route_points(request.destinations):
        print(f"  {point['name']:<12} ({point['lat']}, {point['lng']})")

    print()
    print("Itinerary saved to data/itineraries/")


if __name__ == "__main__":
    main()
