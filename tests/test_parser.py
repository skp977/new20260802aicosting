import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from models.travel_request import TravelRequest

req = TravelRequest()

print("=" * 60)
print(req)
print("=" * 60)
