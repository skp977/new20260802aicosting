"""
============================================================
FILE NAME
activity_recommender.py

PURPOSE
Recommend activities for a travel request based on
destinations and already-requested activities.

INPUT
TravelRequest

OUTPUT
list of recommended activities

USED BY
Generate Quotation UI (suggestions)

LAST UPDATED
2026-08-02
============================================================
"""


class ActivityRecommender:

    DATABASE = {
        "kathmandu": [
            "Kathmandu Durbar Square heritage walk",
            "Boudhanath Stupa evening kora",
            "Swayambhunath sunrise visit",
            "Patan Museum guided tour",
            "Thamel cultural evening"
        ],
        "pokhara": [
            "Sarangkot sunrise trek",
            "Phewa Lake boating",
            "World Peace Pagoda visit",
            "Paragliding tandem flight",
            "Davis Falls & Gupteshwor Cave"
        ],
        "chitwan": [
            "Jungle safari (jeep)",
            "Canoe ride on Rapti river",
            "Elephant breeding center",
            "Tharu cultural dance show",
            "Bird watching tour"
        ],
        "lumbini": [
            "Maya Devi Temple visit",
            "Bodhi tree meditation",
            "Monastery circuit tour",
            "Lumbini museum"
        ],
        "nagarkot": [
            "Himalayan sunrise viewpoint",
            "Nagarkot nature walk"
        ],
        "muktinath": [
            "Muktinath Temple darshan",
            "Muktinath hot springs"
        ],
        "mustang": [
            "Upper Mustang jeep expedition",
            "Kagbeni village walk"
        ],
        "bandipur": [
            "Bandipur old town walk",
            "Siddha cave exploration"
        ],
        "everest": [
            "Everest scenic flight",
            "Lukla short trek"
        ],
        "annapurna": [
            "Annapurna base camp trek",
            "Ghorepani Poon Hill sunrise"
        ]
    }

    DEFAULT = [
        "City heritage walking tour",
        "Local market experience",
        "Cultural show evening",
        "Scenic viewpoint visit"
    ]

    def recommend(self, request):

        destinations = getattr(request, "destinations", []) or []
        requested = set(getattr(request, "activities", []) or [])

        recommendations = []

        for destination in destinations:
            key = str(destination).lower()

            for activity in self.DATABASE.get(key, []):
                if activity not in requested:
                    recommendations.append(activity)

        if not recommendations:
            recommendations = list(self.DEFAULT)

        return recommendations
