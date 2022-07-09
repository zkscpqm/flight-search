import dataclasses
import datetime

from src.currency.money import Money
from src.flight_search.airport import Airport
from util.types import nullable


@dataclasses.dataclass
class FlightSearchQuery:
    depart_from: list[Airport]
    arrive_at: list[Airport]
    budget: Money
    departure_dates: list[datetime.datetime]
    max_journey_legs: int = 2
