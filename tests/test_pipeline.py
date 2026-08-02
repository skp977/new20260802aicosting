
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))

from parsers.travel_request_extractor import TravelRequestExtractor
from itinerary.itinerary_engine import ItineraryEngine
from costing.master_costing_engine import MasterCostingEngine

text="""
We are 4 pax.
Kathmandu Pokhara Chitwan.
Budget 3000 USD.
john@test.com
"""

request=TravelRequestExtractor().extract(text)

itinerary=ItineraryEngine().generate(request)

costing=MasterCostingEngine().calculate(
    request,
    itinerary
)

print()
print("REQUEST")
print(request)

print()
print("ITINERARY")
print(itinerary)

print()
print("COSTING")
print(costing)

