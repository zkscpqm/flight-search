import dataclasses
import datetime

from src.currency.money import Money
from src.skylib.airport import Airport
from util.types import nullable


@dataclasses.dataclass
class FlightSearchQuery:
    depart_from: list[Airport]
    arrive_at: list[Airport]
    budget: Money
    departure_dates: list[datetime.datetime] = datetime.datetime.now()
    return_dates: nullable(list[datetime.datetime]) = None
