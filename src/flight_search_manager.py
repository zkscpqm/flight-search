from src.currency.exchange import ExchangeRateMap
from src.flight_search.session import AmadeusSession
from src.geo.world_map import WorldMap
from util.logging.logger import Logger


class FlightSearchManager:

    def __init__(self, logger: Logger, world_map: WorldMap, fx_api: ExchangeRateMap, flight_search: AmadeusSession):
        ...
