"""
============================================================
FILE NAME
souvenir_recommender.py

PURPOSE
Recommend souvenirs / shopping for a travel request based
on destinations.

INPUT
TravelRequest

OUTPUT
list of recommended souvenirs

USED BY
Generate Quotation UI (suggestions)

LAST UPDATED
2026-08-02
============================================================
"""


class SouvenirRecommender:

    DATABASE = {
        "kathmandu": [
            "Pashmina shawl",
            "Singing bowls",
            "Thangka paintings",
            "Beaded prayer malas"
        ],
        "pokhara": [
            "Himalayan crystal stones",
            "Handmade felt products",
            "Local honey"
        ],
        "chitwan": [
            "Tharu handicrafts",
            "Wooden masks",
            "Bamboo woven baskets"
        ],
        "lumbini": [
            "Prayer flags",
            "Buddha statues",
            "Palm-leaf manuscripts"
        ],
        "nagarkot": [
            "Local wool blankets",
            "Mountain photography prints"
        ],
        "muktinath": [
            "Muktinath prasad",
            "Shaligrams",
            "Tibetan prayer wheels"
        ],
        "mustang": [
            "Tibetan carpets",
            "Mani stone carvings",
            "Yak wool scarves"
        ],
        "bandipur": [
            "Traditional Newari pottery",
            "Juju dhau souvenirs"
        ],
        "everest": [
            "Everest T-shirts",
            "Sherpa caps",
            "Trekking certificates"
        ],
        "annapurna": [
            "Gurung woven belts",
            "Dhaka fabric items",
            "Hand-knitted wool socks"
        ]
    }

    DEFAULT = [
        "Pashmina shawl",
        "Singing bowl",
        "Prayer flag set",
        "Nepali tea packet"
    ]

    def recommend(self, request):

        destinations = getattr(request, "destinations", []) or []

        recommendations = []

        for destination in destinations:
            key = str(destination).lower()

            for souvenir in self.DATABASE.get(key, []):
                recommendations.append(souvenir)

        if not recommendations:
            recommendations = list(self.DEFAULT)

        return recommendations
