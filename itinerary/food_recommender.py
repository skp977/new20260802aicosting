"""
============================================================
FILE NAME
food_recommender.py

PURPOSE
Recommend foods / restaurants for a travel request based
on destinations.

INPUT
TravelRequest

OUTPUT
list of recommended food experiences

USED BY
Generate Quotation UI (suggestions)

LAST UPDATED
2026-08-02
============================================================
"""


class FoodRecommender:

    DATABASE = {
        "kathmandu": [
            "Momos (steamed dumplings)",
            "Newari khaja set (samay baji)",
            "Dal bhat tarkari",
            "Sel roti (rice bread)"
        ],
        "pokhara": [
            "Fresh fish curry from Phewa lake",
            "Laphing (thakali style)",
            "Dal bhat at a lakeside restaurant"
        ],
        "chitwan": [
            "Tharu village feast",
            "Grilled river fish",
            "Local organic vegetables"
        ],
        "lumbini": [
            "Vegetarian thali",
            "Buddhist monastery kitchen meal"
        ],
        "nagarkot": [
            "Sunrise breakfast with mountain view",
            "Traditional Sherpa dishes"
        ],
        "muktinath": [
            "Local Tibetan butter tea",
            "Thakali dal bhat"
        ],
        "mustang": [
            "Tibetan yak cheese",
            "Buckwheat noodles (thukpa)"
        ],
        "bandipur": [
            "Newari buffet in old town",
            "Local juju dhau (king curd)"
        ],
        "everest": [
            "Sherpa stew (shyakpa)",
            "Tibetan bread with honey"
        ],
        "annapurna": [
            "Thakali khana set",
            "Gurung cuisine in Ghandruk"
        ]
    }

    DEFAULT = [
        "Dal bhat tarkari",
        "Momos",
        "Fresh local fruit",
        "Nepali milk tea"
    ]

    def recommend(self, request):

        destinations = getattr(request, "destinations", []) or []

        recommendations = []

        for destination in destinations:
            key = str(destination).lower()

            for food in self.DATABASE.get(key, []):
                recommendations.append(food)

        if not recommendations:
            recommendations = list(self.DEFAULT)

        return recommendations
