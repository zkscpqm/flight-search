import dataclasses
from datetime import datetime

from src.flight_search.airport import Airport


@dataclasses.dataclass
class Flight:

    departs_from: Airport
    arrives_at: Airport
    airline: str
    departure_time: datetime
    arrival_time: datetime
    flight_number: str


@dataclasses.dataclass
class Trip:

    flights: list[Flight]
