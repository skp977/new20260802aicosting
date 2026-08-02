"""
FILE NAME:
itinerary_engine.py

PURPOSE:
Generate structured Nepal travel itineraries from TravelRequest.
"""

from datetime import datetime


class ItineraryEngine:

    def generate(self, request):

        itinerary = []

        destinations = request.destinations

        if not destinations:
            destinations = ["Kathmandu"]

        day_number = 1

        for destination in destinations:

            itinerary.append(
                self.build_arrival_day(
                    day_number,
                    destination
                )
            )

            day_number += 1

        return itinerary

    def build_arrival_day(
        self,
        day,
        city
    ):

        sightseeing = self.get_city_sightseeing(city)

        return {
            "day": day,
            "title": f"Explore {city}",
            "city": city,
            "overnight": city,
            "hotel_category": "4 Star",
            "meals": [
                "Breakfast",
                "Lunch",
                "Dinner"
            ],
            "transport": "Private Vehicle",
            "activities": sightseeing,
            "notes": f"Arrival and sightseeing in {city}"
        }

    def get_city_sightseeing(
        self,
        city
    ):

        database = {

            "kathmandu": [
                "Pashupatinath Temple",
                "Boudhanath Stupa",
                "Swayambhunath",
                "Kathmandu Durbar Square"
            ],

            "pokhara": [
                "Phewa Lake",
                "Davis Falls",
                "Gupteshwor Cave",
                "Sarangkot Sunrise"
            ],

            "chitwan": [
                "Jungle Safari",
                "Canoe Ride",
                "Elephant Breeding Center",
                "Tharu Cultural Show"
            ]
        }

        return database.get(
            city.lower(),
            [
                "City Tour",
                "Local Experience"
            ]
        )


if __name__ == "__main__":

    import sys
    from pathlib import Path

    ROOT = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(ROOT))

    from models.travel_request import TravelRequest

    req = TravelRequest()

    req.destinations = [
        "Kathmandu",
        "Pokhara",
        "Chitwan"
    ]

    engine = ItineraryEngine()

    result = engine.generate(req)

    for day in result:
        print(day)