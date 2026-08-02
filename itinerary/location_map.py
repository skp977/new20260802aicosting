"""
============================================================
FILE NAME
location_map.py

PURPOSE
Provide latitude/longitude for Nepal destinations so the
itinerary can be plotted on a free OpenStreetMap (Leaflet).

INPUT
List of destination names

OUTPUT
List of {"name", "lat", "lng"} points in itinerary order

USED BY
main.py (Generate Quotation map)

LAST UPDATED
2026-08-02
============================================================
"""

LOCATIONS = {
    "kathmandu": {"lat": 27.7172, "lng": 85.3240},
    "pokhara": {"lat": 28.2096, "lng": 83.9856},
    "chitwan": {"lat": 27.5291, "lng": 84.3542},
    "lumbini": {"lat": 27.4833, "lng": 83.2767},
    "nagarkot": {"lat": 27.7153, "lng": 85.5206},
    "muktinath": {"lat": 28.8167, "lng": 83.8667},
    "janakpur": {"lat": 26.7288, "lng": 85.9250},
    "mustang": {"lat": 28.8000, "lng": 83.7000},
    "everest": {"lat": 27.9881, "lng": 86.9250},
    "annapurna": {"lat": 28.5225, "lng": 83.9211},
    "bandipur": {"lat": 27.9350, "lng": 84.4133},
    "ghandruk": {"lat": 28.3893, "lng": 83.6433},
    "dhulikhel": {"lat": 27.6224, "lng": 85.5479},
    "trisuli": {"lat": 27.9240, "lng": 85.1486},
    "manang": {"lat": 28.6706, "lng": 84.0222},
    "bhaktapur": {"lat": 27.6710, "lng": 85.4298},
    "patan": {"lat": 27.6710, "lng": 85.3240},
    "gorkha": {"lat": 27.9896, "lng": 84.6290},
    "solukhumbu": {"lat": 27.7000, "lng": 86.7000}
}

DEFAULT_POINT = {"lat": 28.3949, "lng": 84.1240}


def route_points(destinations):
    points = []

    for destination in destinations or []:
        key = str(destination).strip().lower()

        point = LOCATIONS.get(key, DEFAULT_POINT)

        points.append({
            "name": str(destination),
            "lat": point["lat"],
            "lng": point["lng"]
        })

    return points
