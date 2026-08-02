from pathlib import Path
import sys

sys.path.append(
    str(Path(__file__).parent.parent)
)

from storage.save_manager import SaveManager
from models.travel_request import TravelRequest

manager = SaveManager()

request = TravelRequest()

print(
    manager.save_request(request)
)

print(
    manager.save_itinerary(
        "test_itinerary",
        {"day": 1}
    )
)

print(
    manager.save_costing(
        "test_costing",
        {"total": 2500}
    )
)
